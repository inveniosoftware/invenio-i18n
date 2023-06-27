# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio internationalization module."""

import json
import os.path

from babel import Locale, UnknownLocaleError
from flask import current_app
from flask_babel import Babel, LazyString
from flask_babel import get_locale as get_current_locale
from flask_babel import get_timezone as get_current_timezone
from werkzeug.local import LocalProxy

from . import config
from .babel import MultidirDomain
from .jinja2 import (
    filter_language_name,
    filter_language_name_local,
    filter_to_user_timezone,
    filter_to_utc,
)
from .selectors import get_locale, get_timezone

current_i18n = LocalProxy(lambda: current_app.extensions["invenio-i18n"])
text_type = str


def get_lazystring_encoder(app):
    """Return a JSONEncoder for handling lazy strings from Babel.

    Installed on Flask application by default by :class:`InvenioI18N`.
    """

    class JSONEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, LazyString):
                return text_type(o)
            return super(JSONEncoder, self).default(o)

    return JSONEncoder


class InvenioI18N(object):
    """Invenio I18N extension."""

    def __init__(
        self,
        app=None,
        date_formats=None,
        localeselector=None,
        timezoneselector=None,
        entry_point_group="invenio_i18n.translations",
    ):
        """Initialize extension.

        :param app: Flask application.
        :param data_formats: Override default date/time formatting.
        :param localeselector: Callback function used for locale selection.
            (Default: :func:`invenio_i18n.selectors.get_locale()`)
        :param timezoneselector: Callback function used for timezone selection.
            (Default: ``BABEL_DEFAULT_TIMEZONE``)
        :param entry_point_group: Entrypoint used to load translations from.
            Set to ``None`` to not load translations from entry points.
        """
        self.domain = MultidirDomain()
        self.babel = Babel(
            date_formats=date_formats,
            configure_jinja=True,
            default_domain=self.domain,
        )
        self.entry_point_group = entry_point_group
        self._locales_cache = None
        self._languages_cache = None

        if app:
            self.init_app(app, localeselector, timezoneselector)

    def init_app(self, app, localeselector=None, timezoneselector=None):
        """Flask application initialization.

        The initialization will:

         * Set default values for the configuration variables.
         * Load translations from paths specified in
           ``I18N_TRANSLATIONS_PATHS``.
         * Load translations from ``app.root_path>/translations`` if it exists.
         * Load translations from a specified entry point.
         * Add ``toutc`` and ``tousertimezone`` template filters.
         * Install a custom JSON encoder on app.
        """
        self.init_config(app)
        self.init_multidir_domain(app)

        # Initialize Flask-Babel
        self.babel.init_app(
            app,
            default_translation_directories=";".join(
                self.domain._translation_directories
            ),
            locale_selector=localeselector or get_locale,
            timezone_selector=timezoneselector or get_timezone,
        )

        app.config["BABEL_DEFAULT_LOCALE"] = "en"

        # Register Jinja2 template filters for date formatting (Flask-Babel
        # already installs other filters).
        app.add_template_filter(filter_to_utc, name="toutc")
        app.add_template_filter(filter_to_user_timezone, name="tousertimezone")
        app.add_template_filter(filter_language_name, name="language_name")
        app.add_template_filter(filter_language_name_local, name="language_name_local")
        app.add_template_global(current_i18n, name="current_i18n")

        # Lazy string aware JSON encoder.
        app.json_provider_class = get_lazystring_encoder(app)

        app.extensions["invenio-i18n"] = self

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("I18N_"):
                app.config.setdefault(k, getattr(config, k))

    def init_multidir_domain(self, app):
        """Initialize MultidirDomain."""
        # 1. Paths listed in I18N_TRANSLATIONS_PATHS
        for p in app.config.get("I18N_TRANSLATIONS_PATHS", []):
            self.domain.add_path(p)

        # 2. <app.root_path>/translations
        app_translations = os.path.join(app.root_path, "translations")
        if os.path.exists(app_translations):
            self.domain.add_path(app_translations)

        # 3. Entrypoints
        if self.entry_point_group:
            self.domain.add_entrypoint(self.entry_point_group)

    def iter_languages(self):
        """Iterate over list of languages."""
        default_lang = self.babel.default_locale.language
        default_title = self.babel.default_locale.get_display_name(default_lang)

        yield (default_lang, default_title)

        for lang, title in current_app.config.get("I18N_LANGUAGES", []):
            yield lang, title

    def get_languages(self):
        """Get list of languages."""
        if self._languages_cache is None:
            self._languages_cache = list(self.iter_languages())
        return self._languages_cache

    def get_locales(self):
        """Get a list of supported locales.

        Computes the list using ``I18N_LANGUAGES`` configuration variable.
        """
        if self._locales_cache is None:
            langs = [self.babel.default_locale]
            for lang, dummy_title in current_app.config.get("I18N_LANGUAGES", []):
                langs.append(Locale.parse(lang))
            self._locales_cache = langs

        return self._locales_cache

    def is_locale_available(self, locale):
        """Check if provided locale is available.

        First parse a locale and then check if it is configured as available.
        Could be that locale data is available (Locale will not raise) but it
        is not configured as available in the app.
        """
        try:
            return Locale.parse(locale) in self.get_locales()
        except (UnknownLocaleError, TypeError):
            return False

    @property
    def locale(self):
        """Get current locale."""
        return get_current_locale()

    @property
    def language(self):
        """Get current language code."""
        return get_current_locale().language

    @property
    def timezone(self):
        """Get current timezone."""
        return get_current_timezone()
