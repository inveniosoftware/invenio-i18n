# SPDX-FileCopyrightText: 2023 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Proxies for accessing the currently instantiated i18n extension."""

from flask import current_app
from werkzeug.local import LocalProxy

current_i18n = LocalProxy(lambda: current_app.extensions["invenio-i18n"])
"""Proxy for the instantiated i18n extension."""
