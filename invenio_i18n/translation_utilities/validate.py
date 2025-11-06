# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Validation helpers for i18n service."""

from __future__ import annotations

from pathlib import Path

import polib

from .discovery import normalize_package_to_module_name


def validate_po(
    po_file: polib.POFile, package_name: str, locale: str, po_path: Path
) -> dict[str, str | dict[str, list[str]] | dict[str, int]]:
    """Check one translation file for problems.

    :param po_file: The translation file to check
    :param package_name: Name of the package
    :param locale: Language code like 'de' or 'fr'
    :param po_path: Path to the file being checked
    :return: Report with all issues found (untranslated, fuzzy, obsolete)
    """
    # Track untranslated entries, fuzzy flags, and obsolete entries
    untranslated: list[str] = []
    fuzzy: list[str] = []
    obsolete: list[str] = []

    for entry in po_file:
        if entry.obsolete:
            obsolete.append(entry.msgid)
        elif "fuzzy" in entry.flags:
            fuzzy.append(entry.msgid)
        elif not entry.msgstr and not entry.msgstr_plural:
            untranslated.append(entry.msgid)

    issues = {
        "untranslated": untranslated,
        "fuzzyTranslations": fuzzy,
        "obsoleteTranslations": obsolete,
    }
    return {
        "package": normalize_package_to_module_name(package_name),
        "locale": locale,
        "file": str(po_path),
        "issues": issues,
        "counts": {
            "untranslated": len(untranslated),
            "fuzzyTranslations": len(fuzzy),
            "obsoleteTranslations": len(obsolete),
        },
    }
