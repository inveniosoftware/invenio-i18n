# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Basic tests."""

from os.path import dirname, join

import pytest
from babel.support import NullTranslations, Translations
from flask_babel import Babel, force_locale, get_locale

from invenio_i18n.babel import MultidirDomain


def test_init():
    """Test initialization."""
    d = MultidirDomain(paths=[".", ".."], entry_point_group="invenio_i18n.translations")
    assert d
    assert d.has_paths()

    d = MultidirDomain()
    assert not d.has_paths()


def test_merge_translations(app):
    """Test initialization."""
    Babel(app)

    d = MultidirDomain(
        paths=[join(dirname(__file__), "translations")],
        entry_point_group="invenio_i18n.translations",
    )

    with app.test_request_context():
        with force_locale("en"):
            t = d.get_translations()
            assert isinstance(t, Translations)
            # Only in tests/translations
            assert t.gettext("Test string") == "Test string from test"
            # Only in invenio_i18n/translations
            assert t.gettext("Block translate %s") % "a" == "Block translate a"
            # In both - tests/translations overwrites invenio_i18n/translations
            assert t.gettext("Translate") == "From test catalog"


def test_add_nonexisting_path():
    """Test add non-existing path."""
    d = MultidirDomain()
    pytest.raises(RuntimeError, d.add_path, "invalidpath")


def test_get_translations():
    """Test get translations."""
    d = MultidirDomain()
    assert isinstance(d.get_translations(), NullTranslations)


def test_get_translations_existing_and_missing_mo(app):
    """Test get translations for language with existing/missing *.mo files."""
    app.config["I18N_LANGUAGES"] = [("de", "German")]
    Babel(app)

    d = MultidirDomain(entry_point_group="invenio_i18n.translations")

    with app.test_request_context():
        with force_locale("en"):
            assert isinstance(d.get_translations(), Translations)
        with force_locale("de"):
            assert isinstance(d.get_translations(), NullTranslations)


def test_force_locale_no_app_ctx():
    """Test get translations when there is no application ctx."""
    # force_locale is allowed to work outside of application context,
    # but the language is not used
    with force_locale("en"):
        assert True


def test_force_locale(app):
    """Test get translations for language with existing/missing *.mo files."""
    Babel(app)
    with app.test_request_context():
        with force_locale("en"):
            assert str(get_locale()) == "en"
        with force_locale("da"):
            assert str(get_locale()) == "da"
