# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Configuration for the Invenio internationalization module.

In addition to the configuration variables listed below, Flask-BabelEx also
sets system-wide defaults. For further details see:

 * https://pythonhosted.org/Flask-BabelEx/#configuration
"""

I18N_TRANSLATIONS_PATHS = []
"""List of paths to load message catalogs from."""

I18N_LANGUAGES = []
"""List of tuples of available languages.

Example configuration with english and danish with english as default language:

.. code-block:: python

    from flask_babelex import lazy_gettext as _
    BABEL_DEFAULT_LOCALE = 'en'
    I18N_LANGUAGES = (('da', _('Danish')),)

.. note:: You should not include ``BABEL_DEFAULT_LOCALE`` in this list.
"""

I18N_SET_LANGUAGE_URL = "/lang"
"""URL prefix for set language view.

Set to ``None`` to prevent view from being installed.
"""

I18N_DEFAULT_REDIRECT_ENDPOINT = None
"""Endpoint to redirect if no next parameter is provided."""

I18N_SESSION_KEY = "language"
"""Key to retrieve language identifier from the current session object."""

I18N_USER_LANG_ATTR = "prefered_language"
"""Attribute name which contains language identifier on the User object.

It is used only when the login manager is installed and a user is
authenticated. Set to ``None`` to prevent selector from being used.
"""
