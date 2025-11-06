# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and it
# under the terms of the MIT License; see LICENSE file for more details.
"""Conversion helpers for i18n service."""

from __future__ import annotations

from polib import POFile

from .discovery import package_name_to_module_name


def po_to_i18next_json(po_file: POFile, package_name: str) -> dict[str, str]:
    """Convert PO file to JSON format.

    Returns only namespaced keys to avoid duplicates and clearly separate
    translations by package source.

    :param po_file: The translation file to convert
    :param package_name: Name of the package
    :return: Dictionary with namespaced translations like {"package_name:Overview": "Overview"}
    """
    result: dict[str, str] = {}
    normalized_package = package_name_to_module_name(package_name)

    for entry in po_file:
        if entry.obsolete:
            continue

        base_key = entry.msgid
        if not base_key:
            continue

        if entry.msgstr_plural:
            singular_value = (entry.msgstr_plural.get(0) or base_key).strip()
            plural_value = (entry.msgstr_plural.get(1) or base_key).strip()

            # Only add namespaced keys to avoid duplicates
            result[f"{normalized_package}:{base_key}"] = singular_value
            result[f"{normalized_package}:{base_key}_plural"] = plural_value
        else:
            value = (entry.msgstr or base_key).strip()
            # Only add namespaced keys to avoid duplicates
            result[f"{normalized_package}:{base_key}"] = value

    return result
