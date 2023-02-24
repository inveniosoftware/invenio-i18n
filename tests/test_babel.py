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
    assert len(d._translation_directories) > 0

    d = MultidirDomain()
    assert len(d._translation_directories) == 0


def test_add_nonexisting_path():
    """Test add non-existing path."""
    d = MultidirDomain()
    pytest.raises(RuntimeError, d.add_path, "invalidpath")


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
