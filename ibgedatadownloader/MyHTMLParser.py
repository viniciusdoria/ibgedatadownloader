"""
/***************************************************************************
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

import re
from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    """Personalizes HTML parser to extract directory listings from IBGE FTP servers."""

    def __init__(self):
        """Initialize the HTML parser.

        Sets up attributes to track parent/child relationships in HTML structure,
        specifically for parsing FTP directory listings.
        """

        # Mother class constructor HTMLParser (subclass)
        super().__init__()

        # Attribute that receive parent tree
        self.parent = None
        # Attribute that receive children tree
        self.children = []
        # Attribute that receives child information
        self.child = []
        # Attribute that receives tag <tr> in and out information
        self.trElement = False

    def handle_starttag(self, tag, attrs):
        """Handle HTML start tags.

        Extracts parent and child URLs from anchor tags.

        :param tag: The name of the tag being processed
        :param attrs: List of (name, value) pairs containing the tag's attributes
        """

        if tag == "tr":
            self.trElement = True
            # print(tag, self.trElement)

        if tag == "a":
            for attr in attrs:
                if attr[1]:
                    if attr[1].startswith("/"):
                        # Set parent
                        self.parent = attr[1]
                    if not any(attr[1].startswith(item) for item in ("?", "/")):
                        # Set child name
                        self.child = [attr[1]]
                        # print('adicionou handle_starttag')
            # print(tag, self.child)

    def handle_endtag(self, tag):
        """Handle HTML end tags.

        Closes table rows and appends completed child entries to the children list.

        :param tag: The name of the tag being closed
        """

        if tag == "tr":
            self.trElement = False
            # If child is valid, append to children
            if self.child != []:
                self.children.append(self.child)
            # Reset child
            self.resetChild()
            # print(tag, self.trElement)

    def handle_data(self, data):
        """Handle text data within HTML tags.

        Extracts metadata (dates and file sizes) from the HTML content using regex patterns.

        :param data: The text content to process
        """

        # Remove white spaces at start / end of the string
        data = data.lstrip().rstrip()
        # Set child last modified date
        match = re.match(r"(\d+-\d+-\d+ \d+:\d+)", data)
        if match and self.child != []:
            self.child.append(data)
            # print(self.child)
        # Set child file size using regular expression
        match = re.match(r"(\d+[A-Za-z])", data)  # N...X
        matchType = 1
        if not match:
            match = re.match(r"(\d+\.?\d+[A-Za-z])", data)  # N.N...X
        if not match:
            match = re.match(r"(^\d+$)", data)  # N...
            matchType = 2
        if match and self.child != []:
            # Adds a space between value and unit and a B as sufix
            if matchType == 1:
                self.child.append(f"{data[:-1]} {data[-1]}B")
            elif matchType == 2:
                self.child.append(f"{data} B")
            # print(self.child)

    def error(self, message):
        """Handle parsing errors from HTMLParser.

        Logs error details and continues parsing to handle malformed HTML gracefully.

        :param message: Error message from the parser
        """
        # Print error details for debugging
        print(f"HTMLParser error: {message}")
        print(f"Raw data around error: {self.rawdata[:500]}")
        # Silently ignore the error to continue parsing

    def getChildren(self):
        """Return the list of child entries parsed from HTML.

        :return: List of child entries, or None if no children were found
        """

        return self.children if self.children else None

    def getParent(self):
        """Return the parent URL extracted from HTML.

        :return: The parent URL string, or None if not set
        """

        return self.parent

    def resetChild(self):
        """Reset the child attribute to an empty list.

        Called after a child entry is complete and added to children list.
        """

        self.child = []

    def resetChildren(self):
        """Reset the children list to empty.

        Clears all previously parsed child entries.
        """

        self.children = []

    def resetParent(self):
        """Reset the parent attribute to None.

        Clears the current parent URL.
        """

        self.parent = None
