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

import http
import http.client
import socket
import time
import unicodedata
import urllib
from difflib import SequenceMatcher

from qgis.core import Qgis, QgsProject, QgsTask
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QIcon

from ibgedatadownloader.__about__ import DIR_PLUGIN_ROOT

from .MyHTMLParser import MyHTMLParser


class WorkerSearchManager(QgsTask):
    """Searches in a FTP's url for a word in background"""

    # Signals emitted
    textProgress = pyqtSignal(str)  # text for progress dialog
    processResult = pyqtSignal(list)  # process result
    barMax = pyqtSignal(float)  # max number of progress bar

    def __init__(self, iface, desc, rootFtp, txtSearch, matchContains, matchScore):
        """Constructor."""
        # Mother class constructor QgsTask (subclass)
        super().__init__(desc, flags=QgsTask.CanCancel)

        # Saving references
        self.iface = iface
        self.project = QgsProject.instance()
        self.msgBar = self.iface.messageBar()
        self.htmlParser = MyHTMLParser()
        self.rootFtp = rootFtp if rootFtp.endswith("/") else f"{rootFtp}/"
        self.txtSearch = txtSearch
        self.matchContains = matchContains
        self.matchScore = matchScore
        self.pluginIcon = QIcon(str(DIR_PLUGIN_ROOT / "icon.png"))
        self.exception = []

        # Avoid headers and maxlines limit error
        http.client._MAXHEADERS = 999999999999999999
        http.client._MAXLINE = 999999999999999999

    def standardizeText(self, text):
        """Standardizes texts to check equality."""
        text = unicodedata.normalize("NFD", text)
        text = text.encode("ascii", "ignore")
        text = text.decode("utf-8")
        text = text.replace(" ", "_")
        return text.lower()

    def finished(self, result):
        """This function is called automatically when the task is completed and is
        called from the main thread so it is safe to interact with the GUI etc here
        """
        if result is False:
            self.msgBar.pushMessage(
                self.tr("Error"),
                self.tr("Oops, something went wrong! Please, contact the developer by e-mail."),
                Qgis.Critical,
                duration=0,
            )
        elif self.exception != []:
            self.msgBar.pushMessage(
                self.tr("Warning"),
                self.tr("Process partially completed."),
                Qgis.Warning,
                duration=0,
            )
        else:
            self.msgBar.pushMessage(
                self.tr("Success"),
                self.tr("Process completed."),
                Qgis.Success,
                duration=0,
            )

    def run(self):
        """Principal method that is automatically called when the task runs."""
        self.barMax.emit(0)

        matchUrl = []

        self.htmlParser.resetParent()
        self.htmlParser.resetChildren()
        self.htmlParser.resetChild()
        # Set timeout for requests
        socket.setdefaulttimeout(15)
        try:
            response = urllib.request.urlopen(self.rootFtp)
            self.htmlParser.feed(response.read().decode("utf-8", errors="ignore"))
        except TimeoutError as e:
            self.exception.append(e)
            self.processResult.emit(
                [
                    self.tr("The search fails due to a server timeout."),
                    Qgis.Critical,
                    self.exception,
                    matchUrl,
                    "search",
                ],
            )
            return True
        # Set timeout for requests to default
        socket.setdefaulttimeout(None)
        children = self.htmlParser.getChildren()

        fails = 0
        if children:
            searchUrls = []
            for child in children:
                # Skip child pointing to the domain
                if child[0] == "https://www.ibge.gov.br/":
                    continue
                searchUrls.append([self.rootFtp + child[0], child[1]])
                if self.matchContains:
                    if self.txtSearch.lower() in child[0].lower():
                        matchUrl.append([self.rootFtp + child[0], child[1]])
                        self.textProgress.emit(
                            self.tr(f"{len(matchUrl)} Product(s) found.\nThe search may take several minutes..."),
                        )
                elif (
                    SequenceMatcher(
                        None,
                        self.standardizeText(self.txtSearch),
                        self.standardizeText(child[0]),
                    ).ratio()
                    * 100
                    >= self.matchScore
                ):
                    matchUrl.append([self.rootFtp + child[0], child[1]])
                    self.textProgress.emit(
                        self.tr(f"{len(matchUrl)} Product(s) found.\nThe search may take several minutes..."),
                    )
            loop = 0
            while True:
                for sUrl in searchUrls:
                    # Check if task was canceled by the user
                    if self.isCanceled():
                        # self.exception.append(self.tr('Process canceled by user.'))
                        self.processResult.emit(
                            [
                                self.tr("The process was canceled by the user."),
                                Qgis.Warning,
                                self.exception,
                                matchUrl,
                                "search",
                            ],
                        )
                        return False
                    loop += 1
                    # Avoid files
                    if not sUrl[0].endswith("/"):
                        searchUrls.remove(sUrl)
                        continue
                    self.htmlParser.resetParent()
                    self.htmlParser.resetChildren()
                    self.htmlParser.resetChild()
                    try:
                        # print('feed1', sUrl[0])
                        # Set timeout for requests
                        socket.setdefaulttimeout(15)
                        response = urllib.request.urlopen(sUrl[0])
                        self.htmlParser.feed(response.read().decode("utf-8", errors="ignore"))
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
                            response = urllib.request.urlopen(sUrl[0])
                            self.htmlParser.feed(response.read().decode("utf-8", errors="ignore"))
                            # Set timeout for requests to default
                            socket.setdefaulttimeout(None)
                            # print('feed2 ok', sUrl[0])
                        except (TimeoutError, urllib.error.HTTPError, NotImplementedError) as e:
                            # Set timeout for requests to default
                            socket.setdefaulttimeout(None)
                            # print(e.code, e.reason, e.headers)
                            if e == urllib.error.HTTPError:
                                self.exception.append(e.reason)
                            elif e == socket.timeout:
                                self.exception.append(self.tr("Timeout error."))
                            elif e == NotImplementedError:
                                self.exception.append(self.tr("Not implemented error."))
                            searchUrls.remove(sUrl)
                            fails += 1
                            continue
                    children = self.htmlParser.getChildren()
                    if children:
                        for child in children:
                            if child[0] == "https://www.ibge.gov.br/":
                                continue
                            searchUrls.append([sUrl[0] + child[0], child[1]])
                            if self.matchContains:
                                if self.txtSearch.lower() in child[0].lower():
                                    matchUrl.append([sUrl[0] + child[0], child[1]])
                                    self.textProgress.emit(
                                        self.tr("{} Product(s) found.\nThe search may take several minutes...").format(
                                            len(matchUrl),
                                        ),
                                    )
                            elif (
                                SequenceMatcher(
                                    None,
                                    self.standardizeText(self.txtSearch),
                                    self.standardizeText(child[0]),
                                ).ratio()
                                * 100
                                >= self.matchScore
                            ):
                                matchUrl.append([sUrl[0] + child[0], child[1]])
                                self.textProgress.emit(
                                    self.tr("{} Product(s) found.\nThe search may take several minutes...").format(
                                        len(matchUrl),
                                    ),
                                )
                    try:
                        searchUrls.remove(sUrl)
                    except ValueError:
                        pass
                # print('end while for', len(searchUrls))
                if len(searchUrls) == 0:
                    break

        self.processResult.emit(
            [
                self.tr(f"Search completed with {len(matchUrl)} product(s) found and {fails} fails."),
                Qgis.Success,
                self.exception,
                matchUrl,
                "search",
            ],
        )
        return True
