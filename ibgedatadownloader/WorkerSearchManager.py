"""/***************************************************************************
        begin                : 2021-11-17
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Vinicius Etchebeur Medeiros Dória
        email                : vinicius_etchebeur@hotmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from __future__ import annotations

import contextlib
import http
import http.client
import socket
import time
import unicodedata
import urllib.error
import urllib.request
from difflib import SequenceMatcher
from typing import TYPE_CHECKING

from qgis.core import Qgis, QgsProject, QgsTask
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QIcon

from ibgedatadownloader.__about__ import DIR_PLUGIN_ROOT

from .MyHTMLParser import MyHTMLParser

if TYPE_CHECKING:
    from qgis.gui import QgisInterface


class WorkerSearchManager(QgsTask):
    """Searches for a word in an FTP URL in the background.

    This class inherits from QgsTask to perform a network-intensive search
    without blocking the QGIS user interface. It recursively navigates through
    directories on an FTP server, looking for matches to a search term.

    :param iface: The QGIS interface.
    :type iface: qgis.gui.QgisInterface
    :param desc: A description for the task.
    :type desc: str
    :param rootFtp: The root FTP URL to start the search from.
    :type rootFtp: str
    :param txtSearch: The text to search for.
    :type txtSearch: str
    :param matchContains: If True, performs a "contains" search.
    :type matchContains: bool
    :param matchScore: The minimum similarity score for a match (0-100).
    :type matchScore: float
    """

    # Signals emitted
    text_progress = pyqtSignal(str)  #: Signal to update progress text.
    process_result = pyqtSignal(list)  #: Signal to emit the final result.
    bar_max = pyqtSignal(float)  #: Signal to set the progress bar's maximum value.

    def __init__(
        self,
        iface: QgisInterface,
        desc: str,
        root_ftp: str,
        txt_search: str,
        match_contains: bool,
        match_score: float,
    ) -> None:
        """Initialize the WorkerSearchManager."""
        # Mother class constructor QgsTask (subclass)
        super().__init__(desc, flags=QgsTask.CanCancel)

        # Saving references
        self.iface: QgisInterface = iface
        self.project: QgsProject = QgsProject.instance()
        self.msg_bar = self.iface.messageBar()
        self.html_parser: MyHTMLParser = MyHTMLParser()
        self.root_ftp: str = root_ftp if root_ftp.endswith("/") else f"{root_ftp}/"
        self.txt_search: str = txt_search
        self.match_contains: bool = match_contains
        self.match_score: float = match_score
        self.plugin_icon: QIcon = QIcon(str(DIR_PLUGIN_ROOT / "icon.png"))
        self.exception: list[Exception | str] = []

        # Avoid headers and maxlines limit error
        http.client._MAXHEADERS = 999999999999999999
        http.client._MAXLINE = 999999999999999999

    def standardize_text(self, text: str) -> str:
        """Standardize text for comparison.

        Normalizes text by removing accents, converting to lowercase,
        and replacing spaces with underscores.

        :param text: The text to standardize.
        :type text: str
        :returns: The standardized text.
        :rtype: str
        """
        t = unicodedata.normalize("NFD", text)
        t = t.encode("ascii", "ignore")
        t = t.decode("utf-8")
        t = t.replace(" ", "_")
        return t.lower()

    def finished(self, result: bool) -> None:
        """Handle the task's completion.

        This method is called from the main thread when the task finishes.
        It displays a message to the user based on the task's outcome.

        :param result: True if the task completed successfully, False otherwise.
        :type result: bool
        """
        if result is False:
            self.msg_bar.pushMessage(
                self.tr("Error"),
                self.tr("Oops, something went wrong! Please, contact the developer by e-mail."),
                Qgis.Critical,
                duration=0,
            )
        elif self.exception != []:
            self.msg_bar.pushMessage(
                self.tr("Warning"),
                self.tr("Process partially completed."),
                Qgis.Warning,
                duration=0,
            )
        else:
            self.msg_bar.pushMessage(
                self.tr("Success"),
                self.tr("Process completed."),
                Qgis.Success,
                duration=0,
            )

    def run(self) -> bool:
        """Execute the background search task.

        This is the main method that runs in a separate thread. It performs
        the recursive search on the FTP server.

        :returns: True if the search completes, False if it's canceled.
        :rtype: bool
        """
        self.bar_max.emit(0)

        match_url: list[list[str]] = []

        self.html_parser.resetParent()
        self.html_parser.resetChildren()
        self.html_parser.resetChild()
        # Set timeout for requests
        socket.setdefaulttimeout(15)
        try:
            with urllib.request.urlopen(self.root_ftp) as response:
                self.html_parser.feed(response.read().decode("utf-8", errors="ignore"))
        except TimeoutError as e:
            self.exception.append(e)
            self.process_result.emit(
                [
                    self.tr("The search fails due to a server timeout."),
                    Qgis.Critical,
                    self.exception,
                    match_url,
                    "search",
                ],
            )
            return True
        # Set timeout for requests to default
        socket.setdefaulttimeout(None)
        children = self.html_parser.getChildren()

        fails = 0
        if children:
            search_urls: list[list[str]] = []
            for child in children:
                # Skip child pointing to the domain
                if child[0] == "https://www.ibge.gov.br/":
                    continue
                search_urls.append([self.root_ftp + child[0], child[1]])
                if self.match_contains:
                    if self.txt_search.lower() in child[0].lower():
                        match_url.append([self.root_ftp + child[0], child[1]])
                        self.text_progress.emit(
                            self.tr(f"{len(match_url)} Product(s) found.\nThe search may take several minutes..."),
                        )
                elif (
                    SequenceMatcher(
                        None,
                        self.standardize_text(self.txt_search),
                        self.standardize_text(child[0]),
                    ).ratio()
                    * 100
                    >= self.match_score
                ):
                    match_url.append([self.root_ftp + child[0], child[1]])
                    self.text_progress.emit(
                        self.tr(f"{len(match_url)} Product(s) found.\nThe search may take several minutes..."),
                    )
            loop = 0
            while True:
                for search_url in search_urls:
                    # Check if task was canceled by the user
                    if self.isCanceled():
                        # self.exception.append(self.tr('Process canceled by user.'))
                        self.process_result.emit(
                            [
                                self.tr("The process was canceled by the user."),
                                Qgis.Warning,
                                self.exception,
                                match_url,
                                "search",
                            ],
                        )
                        return False
                    loop += 1
                    # Avoid files
                    if not search_url[0].endswith("/"):
                        search_urls.remove(search_url)
                        continue
                    self.html_parser.resetParent()
                    self.html_parser.resetChildren()
                    self.html_parser.resetChild()
                    try:
                        # print('feed1', sUrl[0])
                        # Set timeout for requests
                        socket.setdefaulttimeout(15)
                        with urllib.request.urlopen(search_url[0]) as response:
                            self.html_parser.feed(response.read().decode("utf-8", errors="ignore"))
                        # Set timeout for requests to default
                        socket.setdefaulttimeout(None)
                    except (TimeoutError, urllib.error.HTTPError, NotImplementedError):
                        # print(e.code, e.reason, e.headers)
                        # print('tentando novamente em 5 segundos...')
                        # Set timeout for requests to default
                        socket.setdefaulttimeout(None)
                        time.sleep(5)
                        try:
                            # print('feed2', sUrl[0])
                            # Set timeout for requests
                            socket.setdefaulttimeout(15)
                            with urllib.request.urlopen(search_url[0]) as response:
                                self.html_parser.feed(response.read().decode("utf-8", errors="ignore"))
                            # Set timeout for requests to default
                            socket.setdefaulttimeout(None)
                            # print('feed2 ok', sUrl[0])
                        except (TimeoutError, urllib.error.HTTPError, NotImplementedError) as e:
                            # Set timeout for requests to default
                            socket.setdefaulttimeout(None)
                            # print(e.code, e.reason, e.headers)
                            if isinstance(e, urllib.error.HTTPError):
                                self.exception.append(e.reason)
                            elif isinstance(e, socket.timeout):
                                self.exception.append(self.tr("Timeout error."))
                            elif isinstance(e, NotImplementedError):
                                self.exception.append(self.tr("Not implemented error."))
                            search_urls.remove(search_url)
                            fails += 1
                            continue
                    children = self.html_parser.getChildren()
                    if children:
                        for child in children:
                            if child[0] == "https://www.ibge.gov.br/":
                                continue
                            search_urls.append([search_url[0] + child[0], child[1]])
                            if self.match_contains:
                                if self.txt_search.lower() in child[0].lower():
                                    match_url.append([search_url[0] + child[0], child[1]])
                                    self.text_progress.emit(
                                        self.tr("{} Product(s) found.\nThe search may take several minutes...").format(
                                            len(match_url),
                                        ),
                                    )
                            elif (
                                SequenceMatcher(
                                    None,
                                    self.standardize_text(self.txt_search),
                                    self.standardize_text(child[0]),
                                ).ratio()
                                * 100
                                >= self.match_score
                            ):
                                match_url.append([search_url[0] + child[0], child[1]])
                                self.text_progress.emit(
                                    self.tr("{} Product(s) found.\nThe search may take several minutes...").format(
                                        len(match_url),
                                    ),
                                )
                    with contextlib.suppress(ValueError):
                        search_urls.remove(search_url)
                # print('end while for', len(searchUrls))
                if len(search_urls) == 0:
                    break

        self.process_result.emit(
            [
                self.tr(f"Search completed with {len(match_url)} product(s) found and {fails} fails."),
                Qgis.Success,
                self.exception,
                match_url,
                "search",
            ],
        )
        return True
