# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Selector tests."""

from __future__ import absolute_import, print_function

from flask import session
from flask_login import LoginManager, login_user

from invenio_i18n import InvenioI18N
from invenio_i18n.selectors import get_locale


class FakeUser(object):
    """Fake class simulation a user."""

    def __init__(self, prefered_language):
        """Initialize fake user."""
        self.is_active = True
        self.is_authenticated = True
        self.prefered_language = prefered_language

    def get_id(self):
        """Return a default ID. This is only a fake object."""
        return 1


def test_get_locale_querystring(app):
    """Test getting locales from the querystring."""
    app.config["I18N_LANGUAGES"] = [
        ("da", "Danish"),
        ("en", "English"),
        ("es", "Spanish"),
    ]
    InvenioI18N(app)

    with app.test_request_context("/?ln=da"):
        assert "da" == get_locale()

    with app.test_request_context("/?ln=en"):
        assert "en" == get_locale()

    with app.test_request_context("/?ln=es"):
        assert "es" == get_locale()


def test_get_locale_session(app):
    """Test getting locales from the current session."""
    app.config["I18N_LANGUAGES"] = [
        ("da", "Danish"),
        ("en", "English"),
        ("es", "Spanish"),
    ]
    app.secret_key = "secret key"
    InvenioI18N(app)

    with app.test_request_context():
        session["language"] = "da"
        assert "da" == get_locale()

    with app.test_request_context():
        session["language"] = "en"
        assert "en" == get_locale()

    with app.test_request_context():
        session["language"] = "es"
        assert "es" == get_locale()


def test_get_locale_user_settings(app):
    """Test getting locales from the user settings."""
    app.config["I18N_LANGUAGES"] = [
        ("da", "Danish"),
        ("en", "English"),
        ("es", "Spanish"),
    ]
    app.secret_key = "secret key"
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    InvenioI18N(app)

    with app.test_request_context():
        login_user(FakeUser("da"))
        assert "da" == get_locale()

    with app.test_request_context():
        login_user(FakeUser("en"))
        assert "en" == get_locale()

    with app.test_request_context():
        login_user(FakeUser("es"))
        assert "es" == get_locale()


def test_get_locale_headers(app):
    """Test getting locale from the headers of the request."""
    app.config["I18N_LANGUAGES"] = [
        ("da", "Danish"),
        ("en", "English"),
        ("es", "Spanish"),
    ]
    InvenioI18N(app)

    with app.test_request_context(headers=[("Accept-Language", "da")]):
        assert "da" == get_locale()

    with app.test_request_context(headers=[("Accept-Language", "en")]):
        assert "en" == get_locale()

    with app.test_request_context(headers=[("Accept-Language", "es")]):
        assert "es" == get_locale()


def test_get_locale_default(app):
    """Test getting locale by default."""
    app.config["I18N_LANGUAGES"] = [
        ("da", "Danish"),
        ("en", "English"),
        ("es", "Spanish"),
    ]
    InvenioI18N(app)

    with app.test_request_context():
        assert "en" == get_locale()


def test_get_locale_anonymous_user(app):
    """Test anonymous user locale selection by default."""
    app.secret_key = "secret key"
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.user_loader(lambda id_: {})
    InvenioI18N(app)

    with app.test_request_context():
        assert "en" == get_locale()
