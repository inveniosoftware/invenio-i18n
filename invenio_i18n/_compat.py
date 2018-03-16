# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Compatibility module for Python 2 and 3.

The code is inspired by ``six`` library and cheat sheet from
`http://python-future.org/compatible_idioms.html`_
"""

import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:  # pragma: no cover
    text_type = str

    from urllib.parse import urljoin, urlparse
else:
    text_type = unicode

    from urlparse import urljoin, urlparse
