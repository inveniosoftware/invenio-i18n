# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default locale and timezone selectors for Flask-BabelEx.

See `Flask-BabelEx documentation <https://pythonhosted.org/Flask-BabelEx/>`_
for corresponding methods.
"""

from flask import current_app, request, session

try:
    from flask_login import current_user
except ImportError:  # pragma nocover
    current_user = None


def get_locale():
    """Get locale.

    Searches for locale in the following the order:

    - User has specified a concrete language in the query string.
    - Current session has a language set.
    - User has a language set in the profile.
    - Headers of the HTTP request.
    - Default language from ``BABEL_DEFAULT_LOCALE``.

    Will only accept languages defined in ``I18N_LANGUAGES``.
    """
    locales = []
    if "invenio-i18n" in current_app.extensions:
        locales = [x[0] for x in current_app.extensions["invenio-i18n"].get_languages()]

    # In the case of the user specifies a language for the resource.
    if "ln" in request.args:
        language = request.args.get("ln")
        if language in locales:
            return language

    # In the case of the user has set a language for the current session.
    language_session_key = current_app.config["I18N_SESSION_KEY"]
    if language_session_key in session:
        language = session[language_session_key]
        if language in locales:
            return language

    # In the case of the registered user has a prefered language.
    language_user_key = current_app.config["I18N_USER_LANG_ATTR"]
    if (
        language_user_key is not None
        and hasattr(current_app, "login_manager")
        and current_user is not None
        and current_user.is_authenticated
    ):
        language = getattr(current_user, language_user_key, None)
        if language is not None and language in locales:
            return language

    # Using the headers that the navigator has sent.
    headers_best_match = request.accept_languages.best_match(locales)
    if headers_best_match is not None:
        return headers_best_match

    # If there is no way to know the language, return BABEL_DEFAULT_LOCALE
    return current_app.config["BABEL_DEFAULT_LOCALE"]


def get_timezone():
    """Get default timezone (i.e. ``BABEL_DEFAULT_TIMEZONE``)."""
    return current_app.extensions["babel"].default_timezone
