# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Merge helpers for i18n service."""

from __future__ import annotations

from .discovery import normalize_package_to_module_name
from .types import PackageScanResult


def merge_by_locale(
    results: list[PackageScanResult],
) -> dict[str, dict[str, dict[str, str]]]:
    """Combine translations from all packages by language.

    :param results: Translation data from each package
    :return: Organized by language like {"de": {"package1": {...}}}
    """

    merged: dict[str, dict[str, dict[str, str]]] = {}
    for res in results:
        normalized_package = normalize_package_to_module_name(res.package_name)
        for locale, mapping in res.translations_by_locale.items():
            if locale not in merged:
                merged[locale] = {}
            merged[locale][normalized_package] = mapping
    return merged
