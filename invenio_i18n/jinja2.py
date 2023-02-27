# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Babel datetime localization template filters for Jinja.

See full documentation of corresponding methods in Flask-Babel

 * https://python-babel.github.io/flask-babel/
"""

from babel import Locale
from flask_babel import get_locale, to_user_timezone, to_utc


def filter_to_user_timezone(dt):
    """Convert a datetime object to the user's timezone.

    Installed on application as ``tousertimezone``.
    """
    return to_user_timezone(dt)


def filter_to_utc(dt):
    """Convert a datetime object to UTC and drop tzinfo.

    Installed on application as ``toutc``.
    """
    return to_utc(dt)


def filter_language_name(lang_code):
    """Convert language code into display name in current locale.

    Installed on application as ``language_name``.
    """
    return Locale.parse(lang_code).get_display_name(get_locale().language)


def filter_language_name_local(lang_code):
    """Convert language code into display name in local locale.

    Installed on application as ``language_name_local``.
    """
    return Locale.parse(lang_code).display_name
