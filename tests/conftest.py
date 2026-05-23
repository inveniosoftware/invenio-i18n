# SPDX-FileCopyrightText: 2015-2018 CERN.
# SPDX-FileCopyrightText: 2023 Graz University of Technology.
# SPDX-License-Identifier: MIT


"""Pytest configuration."""

import pytest
from flask import Flask, g


@pytest.fixture
def app():
    """Application fixture."""

    def delete_locale_from_cache(exception):
        """Unset locale from `flask.g` when the request is tearing down."""
        if "_flask_babel" in g:
            g._flask_babel.babel_locale = None

    app = Flask("testapp")
    app.teardown_request(delete_locale_from_cache)
    return app
