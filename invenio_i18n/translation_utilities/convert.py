# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and it
# under the terms of the MIT License; see LICENSE file for more details.
"""Conversion helpers for i18n service."""

from __future__ import annotations

import polib

from .discovery import normalize_package_to_module_name


def po_to_i18next_json(po_file: polib.POFile, package_name: str) -> dict[str, str]:
    """Convert PO file to JSON format.

    :param po_file: The translation file to convert
    :param package_name: Name of the package
    :return: Dictionary with translations like {"Hello": "Hallo"}
    """
    result: dict[str, str] = {}
    normalized_package = normalize_package_to_module_name(package_name)

    for entry in po_file:
        if entry.obsolete:
            continue

        base_key = entry.msgid
        if not base_key:
            continue

        if entry.msgstr_plural:
            # Singular (0) and plural (1)
            singular_value = (entry.msgstr_plural.get(0) or base_key).strip()
            plural_value = (entry.msgstr_plural.get(1) or base_key).strip()

            result[base_key] = singular_value
            result[f"{base_key}_plural"] = plural_value

            result[f"{normalized_package}:{base_key}"] = singular_value
            result[f"{normalized_package}:{base_key}_plural"] = plural_value
        else:
            value = (entry.msgstr or base_key).strip()
            result[base_key] = value
            result[f"{normalized_package}:{base_key}"] = value

    return result
