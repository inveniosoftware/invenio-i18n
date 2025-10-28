# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""IO helpers for i18n service."""

from __future__ import annotations

import json
from pathlib import Path


def write_json_file(path: Path, data: dict) -> None:
    """Save data to a JSON file.

    :param path: Where to save the file
    :param data: Dictionary to save as JSON
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
