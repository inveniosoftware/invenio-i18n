# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2016 TIND.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Bundles for Invenio-I18N."""

from __future__ import absolute_import, print_function

from invenio_assets import NpmBundle, RequireJSFilter

js = NpmBundle(
    'js/invenio_i18n/angularLangSelector.js',
    filters=RequireJSFilter(),
    output='gen/i18n.%(version)s.js',
    npm={
        'angular': '~1.4.9',
        'angular-gettext': '~2.3.8',
    }
)
