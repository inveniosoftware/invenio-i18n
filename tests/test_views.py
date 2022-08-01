# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Basic tests."""

from __future__ import absolute_import, print_function

from flask import session, url_for
from flask_babelex import get_locale

from invenio_i18n import InvenioI18N
from invenio_i18n.views import create_blueprint_from_app


def test_lang_view(app):
    """Test extension initalization."""
    app.config.update(
        I18N_LANGUAGES=[
            ("da", "Danish"),
        ],
        I18N_SESSION_KEY="my_session_key",
        SECRET_KEY="CHANGEME",
    )
    InvenioI18N(app)
    app.register_blueprint(create_blueprint_from_app(app))

    @app.route("/")
    def index():
        return get_locale().language

    with app.test_request_context():
        da_lang_url = url_for("invenio_i18n.set_lang", lang_code="da")
        en_lang_url = url_for("invenio_i18n.set_lang", lang_code="en")
        es_lang_url = url_for("invenio_i18n.set_lang", lang_code="es")

    with app.test_client() as client:
        # Set language to danish
        res = client.get(da_lang_url)
        assert res.status_code == 302
        assert res.location == "/"
        assert session[app.config["I18N_SESSION_KEY"]] == "da"

        res = client.get("/")
        assert res.get_data(as_text=True) == "da"

        # Set language to english
        res = client.get(en_lang_url)
        assert res.status_code == 302
        assert res.location == "/"
        assert session[app.config["I18N_SESSION_KEY"]] == "en"

        res = client.get("/")
        assert res.get_data(as_text=True) == "en"

        # Try to set invalid language.
        res = client.get(es_lang_url)
        assert res.status_code == 404


def test_lang_view_redirect(app):
    """Test extension initalization."""
    app.config.update(
        I18N_LANGUAGES=[
            ("da", "Danish"),
        ],
        SECRET_KEY="CHANGEME",
    )
    InvenioI18N(app)
    app.register_blueprint(create_blueprint_from_app(app))

    @app.route("/page/")
    def page():
        return get_locale().language

    with app.test_request_context():
        da_lang_url = url_for("invenio_i18n.set_lang", lang_code="da")
        next_url = url_for("page")

    with app.test_client() as client:
        # Request body
        res = client.post(da_lang_url, data={"next": next_url})
        assert res.status_code == 302
        assert res.location == "/page/"
        assert session[app.config["I18N_SESSION_KEY"]] == "da"

        # Query string
        res = client.get(da_lang_url + "?next={0}".format(next_url))
        assert res.location == "/page/"

        # Referrer header
        res = client.get(da_lang_url, headers={"Referer": next_url})
        assert res.location == "/page/"

        # Unsafe redirects
        res = client.get(da_lang_url + "?next=http://example.org")
        assert res.location == "/"
        res = client.get(da_lang_url, headers={"Referer": "http://example.org"})
        assert res.location == "/"
