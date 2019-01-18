# -*- coding: utf-8 -*-
"""
    oy.exceptions
    ~~~~~~~~~~

    The core exception classes for oy

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from werkzeug.exceptions import HTTPException


class OyException(Exception):
    """The base exception class for Oy."""

    def __init__(self, help_message=None):
        self.help_message = help_message


class OyHTTPException(OyException, HTTPException):
    """An HTTP exception"""


class OyConfigurationError(OyException):
    """Miss configuration of oy"""


class SettingDoesNotExist(OyException):
    """Raised when accessing a setting that does
    not exist in the database nor the current_app settings
    """
