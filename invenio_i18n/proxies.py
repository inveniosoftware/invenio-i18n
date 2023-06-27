# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Proxies for accessing the currently instantiated i18n extension."""

from flask import current_app
from werkzeug.local import LocalProxy

current_i18n = LocalProxy(lambda: current_app.extensions["invenio-i18n"])
"""Proxy for the instantiated i18n extension."""
