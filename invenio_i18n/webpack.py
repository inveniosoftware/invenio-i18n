# SPDX-FileCopyrightText: 2018 CERN.
# SPDX-License-Identifier: MIT

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
                "semantic-ui-less": "^2.4.1",
                "semantic-ui-css": "^2.4.1",
                "font-awesome": "~4.4.0",
                "jquery": "~3.2.1",
            },
        ),
    },
)
