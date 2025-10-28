# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Translation collection and validation utilities."""

from __future__ import annotations

from .collect import (
    collect_translations_to_json,
    scan_package_for_translations,
    scan_package_for_validation,
    validate_translations_from_packages,
)
from .convert import po_to_i18next_json
from .discovery import (
    find_package_path,
    iter_po_files,
    normalize_package_to_module_name,
)
from .io import write_json_file
from .validate import validate_po

__all__ = [
    "collect_translations_to_json",
    "find_package_path",
    "iter_po_files",
    "normalize_package_to_module_name",
    "po_to_i18next_json",
    "scan_package_for_translations",
    "scan_package_for_validation",
    "validate_po",
    "validate_translations_from_packages",
    "write_json_file",
]
