# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Webpack bundles for Invenio-I18N."""

from flask_webpackext import WebpackBundle

i18n = WebpackBundle(
    __name__,
    'assets',
    entry={
        'i18n_app': './js/invenio_i18n/app.js'
    },
    dependencies={
        'angular': '~1.4.9',
        'angular-gettext': '~2.3.8',
    })
