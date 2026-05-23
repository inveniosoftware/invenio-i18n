# SPDX-FileCopyrightText: 2025 Graz University of Technology.
# SPDX-License-Identifier: MIT
"""IO helpers for i18n service."""

from __future__ import annotations

import json
from pathlib import Path


def write_json_file(path: Path, data: dict) -> None:
    """Save data to a JSON file.

    Create parent directory if it doesn't exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
