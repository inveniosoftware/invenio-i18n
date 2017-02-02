# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016, 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Configuration for the Invenio internationalization module.

In addition to the configuration variables listed below, Flask-BabelEx also
sets system-wide defaults. For further details see:

 * https://pythonhosted.org/Flask-BabelEx/#configuration
"""

I18N_TRANSLATIONS_PATHS = []
"""List of paths to load message catalogs from."""

I18N_LANGUAGES = []
"""List of tuples of available languages.

.. note:: You should not include ``BABEL_DEFAULT_LOCALE`` in this list.
"""

I18N_SET_LANGUAGE_URL = '/lang'
"""URL prefix for set language view.

Set to ``None`` to prevent view from being installed.
"""

I18N_DEFAULT_REDIRECT_ENDPOINT = None
"""Endpoint to redirect if no next parameter is provided."""

I18N_SESSION_KEY = 'language'
"""Key to retrieve language identifier from the current session object."""

I18N_USER_LANG_ATTR = 'prefered_language'
"""Attribute name which contains language identifier on the User object.

It is used only when the login manager is installed and a user is
authenticated. Set to ``None`` to prevent selector from being used.
"""
