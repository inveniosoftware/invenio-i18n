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

"""Invenio internationalization module."""

from __future__ import absolute_import, print_function

import os.path

from flask import current_app
from flask_babelex import Babel
from six import text_type

from .babel import MultidirDomain
from .jinja2 import filter_to_user_timezone, filter_to_utc
from .selectors import get_locale, get_timezone


def get_lazystring_encoder(app):
    """Custom JSONEncoder that handles lazy strings from Babel."""
    from speaklater import _LazyString

    class JSONEncoder(app.json_encoder):

        def default(self, o):
            if isinstance(o, _LazyString):
                return text_type(o)
            return super(JSONEncoder, self).default(o)

    return JSONEncoder


class InvenioI18N(object):
    """Invenio I18N module."""

    def __init__(self, app=None, date_formats=None, localeselector=None,
                 timezoneselector=None,
                 entrypoint='invenio_i18n.translations'):
        """Initialize extension."""
        self.babel = Babel(
            date_formats=date_formats,
            configure_jinja=True,
            default_domain=MultidirDomain())

        self.localeselector = localeselector
        self.timezoneselector = timezoneselector
        self.entrypoint = entrypoint
        self._locales_cache = None

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        # Initialize Flask-BabelEx
        app.config.setdefault("I18N_LANGUAGES", [])

        # TODO: allow to plug custom localeselector and timezoneselector
        self.babel.init_app(app)
        self.babel.localeselector(self.localeselector or get_locale)
        self.babel.timezoneselector(self.timezoneselector or get_timezone)

        # Add paths to search for message catalogs
        domain = self.babel._default_domain
        # 1. Paths listed in I18N_TRANSLATIONS_PATHS
        for p in app.config.get("I18N_TRANSLATIONS_PATHS", []):
            domain.add_path(p)
        # 2. <app.root_path>/translations
        app_translations = os.path.join(app.root_path, 'translations')
        if os.path.exists(app_translations):
            domain.add_path(app_translations)
        # 3. Entrypoints
        if self.entrypoint:
            domain.add_entrypoint(self.entrypoint)

        # Register Jinja2 template filters for date formatting (Flask-Babel
        # already installs other filters).
        app.add_template_filter(filter_to_utc, name="toutc")
        app.add_template_filter(filter_to_user_timezone, name="tousertimezone")

        # Lazy string aware JSON encoder.
        app.json_encoder = get_lazystring_encoder(app)

        app.extensions['invenio-i18n'] = self

    def get_locales(self):
        """Get a list of supported locales."""
        if self._locales_cache is None:
            langs = [self.babel.default_locale]
            for l in current_app.config.get('I18N_LANGUAGES', []):
                langs.append(self.babel.load_locale(l))
            self._locales_cache = langs
        return self._locales_cache
