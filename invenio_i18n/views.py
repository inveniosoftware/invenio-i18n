# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2016 TIND.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Views for Invenio-I18N."""

from __future__ import absolute_import, print_function

from flask import Blueprint, abort, current_app, redirect, request, session, url_for

from ._compat import urljoin, urlparse


def is_local_url(target):
    """Determine if URL is safe to redirect to."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def get_redirect_target():
    """Get URL to redirect to and ensure that it is local."""
    for target in request.values.get("next"), request.referrer:
        if target and is_local_url(target):
            return target


def set_lang(lang_code=None):
    """Set language in session and redirect."""
    # Check if language is available.
    lang_code = lang_code or request.values.get("lang_code")
    languages = dict(current_app.extensions["invenio-i18n"].get_languages())
    if lang_code is None or lang_code not in languages:
        abort(404 if request.method == "GET" else 400)

    # Set language in session.
    session[current_app.config["I18N_SESSION_KEY"]] = lang_code.lower()

    # Redirect user back.
    target = get_redirect_target()
    if not target:
        endpoint = current_app.config["I18N_DEFAULT_REDIRECT_ENDPOINT"]
        target = url_for(endpoint) if endpoint else "/"

    return redirect(target)


def create_blueprint(register_default_routes=True, url_prefix=None):
    """Create Invenio-I18N blueprint."""
    blueprint = Blueprint(
        "invenio_i18n",
        __name__,
        url_prefix=url_prefix,
        template_folder="templates",
        static_folder="static",
    )

    if register_default_routes:
        blueprint.add_url_rule("/", view_func=set_lang, methods=["POST"])
        blueprint.add_url_rule(
            "/<lang_code>", view_func=set_lang, methods=["GET", "POST"]
        )

    return blueprint


def create_blueprint_from_app(app):
    """Create Invenio-I18N blueprint from a Flask application.

    :params app: A Flask application.
    :returns: Configured blueprint.
    """
    # Register default routes if URL is set.
    register_default_routes = (
        app.config["I18N_SET_LANGUAGE_URL"] and app.config["I18N_LANGUAGES"]
    )
    return create_blueprint(
        register_default_routes=register_default_routes,
        url_prefix=app.config["I18N_SET_LANGUAGE_URL"],
    )
