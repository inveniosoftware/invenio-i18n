# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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

"""Default locale and timezone selectors for Flask-BabelEx.

See full documentation of corresponding methods in Flask-BabelEx:
https://pythonhosted.org/Flask-BabelEx/
"""

from flask import current_app, request


def get_locale():
    """Get locale based on Accept-Language HTTP headers.

    Will only accept languages defined in ``I18N_LANGUAGES``.
    """
    return request.accept_languages.best_match(
        [str(l) for l in current_app.extensions['invenio-i18n'].get_locales()])


def get_timezone():
    """Get default timezone (i.e. ``BABEL_DEFAULT_TIMEZONE``)."""
    return current_app.extensions['babel'].default_timezone
