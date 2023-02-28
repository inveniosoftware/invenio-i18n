# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


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
