#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtCore


class Logger(QtCore.QObject):
    """A message aggregator for the friture classes.

    Parameters
    ----------
    verbose : bool, optional
        Whether the _logger should print to console in addition to writing to the log.

    Attributes
    ----------
    count : int
        Number of messages passed to the _logger.
    log : str
        A string containing every message passed to this instance of the _logger.

    Signals
    -------
    log_changed :
        Signal emitted whenever the log is updated.

    """

    log_changed = QtCore.pyqtSignal()  # Signal

    def __init__(self, verbose=False):
        super(Logger, self).__init__()
        self.count = 0
        self.log = ""
        self.verbose = verbose

    def push(self, text):
        """Adds a new message to the log.

        Parameters
        ----------
        text : str
            The message to be added to the log.

        """

        self.count += 1

        if self.count == 1:  # It's our first message!
            self.log += "[1] %s" % text
        else:
            self.log += "\n[%d] %s" % (self.count, text)
        self.log_changed.emit()

        if self.verbose:  # Also print to the console, if the user wants.
            print(text)

    def get_log(self):
        """Returns the entire log history."""
        return self.log


class PrintLogger(object):
    """A default _logger that prints to the console"""

    @staticmethod
    def push(text):
        """Prints a message to the console.

        Parameters
        ----------
        text : str
            The message to print to the console.

        """
        print(text)

    @staticmethod
    def get_log():
        """Placeholder method returning an empty string for consistency with application _logger"""
        return ""
