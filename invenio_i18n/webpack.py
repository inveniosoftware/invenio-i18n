# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Webpack bundles for Invenio-I18N."""

from invenio_assets.webpack import WebpackThemeBundle

i18n = WebpackThemeBundle(
    __name__,
    "assets",
    default="bootstrap3",
    themes={
        "bootstrap3": dict(
            entry={
                "i18n_app": "./js/invenio_i18n/app.js",
            },
            dependencies={
                "angular": "~1.4.9",
                "angular-gettext": "~2.3.8",
            },
        ),
        "semantic-ui": dict(
            entry={
                "i18n_app": "./js/invenio_i18n/app.js",
            },
            dependencies={
                "semantic-ui-less": "~2.4.1",
                "semantic-ui-css": "~2.4.1",
                "font-awesome": "~4.4.0",
                "jquery": "~3.2.1",
            },
        ),
    },
)
