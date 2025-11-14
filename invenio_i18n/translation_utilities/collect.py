# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and it
# under the terms of the MIT License; see LICENSE file for more details.
"""Collect PO translations, convert to JSON, and validate."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import polib

from .convert import po_to_i18next_json
from .discovery import (
    find_package_path,
    find_po_files,
    normalize_package_to_module_name,
)
from .io import write_json_file
from .validate import validate_po


def get_package_translations(package_name: str) -> dict[str, dict[str, str]]:
    """Get all translations from one package.

    :param package_name: Name of the package like 'invenio-app-rdm'
    :return: Translations organized by language like {"de": {...}, "fr": {...}}
    """
    package_root = find_package_path(package_name)
    translations_by_locale: dict[str, dict[str, str]] = {}

    if not package_root:
        return translations_by_locale

    for locale, po_path in find_po_files(package_root, package_name):
        po_file = polib.pofile(str(po_path))
        translations_by_locale[locale] = po_to_i18next_json(po_file, package_name)

    return translations_by_locale


def get_package_validation_reports(
    package_name: str,
) -> list[dict[str, str | dict[str, list[str]] | dict[str, int]]]:
    """Get validation reports for one package.

    :param package_name: Name of the package to check like 'invenio-app-rdm'
    :return: List of reports showing what needs to be fixed
    """
    package_root = find_package_path(package_name)
    validation_reports: list[dict[str, str | dict[str, list[str]] | dict[str, int]]] = (
        []
    )

    if not package_root:
        return validation_reports

    for locale, po_path in find_po_files(package_root, package_name):
        po_file = polib.pofile(str(po_path))
        validation_reports.append(validate_po(po_file, package_name, locale, po_path))

    return validation_reports


def collect_translations(
    packages: list[str],
) -> dict[
    str,
    dict[str, dict[str, dict[str, str]]]
    | dict[str, dict[str, dict[str, str]]]
    | int
    | list[str],
]:
    """Collect translations from packages.

    :param packages: List of package names like ['invenio-app-rdm', 'invenio-rdm-records']
    :return: Dictionary with collected translations and summary info
    """
    collected_translations: defaultdict[str, dict[str, dict[str, str]]] = defaultdict(
        dict
    )
    translations_by_package: dict[str, dict[str, dict[str, str]]] = {}

    for package_name in packages:
        translations_by_locale = get_package_translations(package_name)

        if translations_by_locale:
            normalized_name = normalize_package_to_module_name(package_name)
            translations_by_package[normalized_name] = translations_by_locale

            # Store for merged output
            for locale, translations in translations_by_locale.items():
                collected_translations[locale][normalized_name] = translations

    return {
        "translations_by_package": translations_by_package,
        "collected_translations": dict(collected_translations),
        "packagesProcessed": len(packages),
        "locales": sorted(list(collected_translations.keys())),
    }


def write_translations_to_json(
    collected_data: dict,
    output_dir: Path,
) -> None:
    """Write collected translations to JSON files.

    :param collected_data: Output from collect_translations()
    :param output_dir: Where to save the translation files
    """
    translations_by_package = collected_data["translations_by_package"]
    collected_translations = collected_data["collected_translations"]

    for normalized_name, translations_by_locale in translations_by_package.items():
        package_output = output_dir / normalized_name / "translations.json"
        write_json_file(package_output, translations_by_locale)

    write_json_file(output_dir / "translations.json", collected_translations)


def write_validation_report(
    validation_summary: dict,
    output_dir: Path,
) -> None:
    """Write validation report to JSON file.

    :param validation_summary: Output from validate_translations()
    :param output_dir: Where to save the validation report
    """
    report_path = output_dir / "validation-report.json"
    write_json_file(report_path, validation_summary)


def validate_translations(
    packages: list[str],
) -> dict[
    str,
    dict[str, int]
    | dict[str, dict[str, int | list[dict[str, dict[str, int]]]]]
    | dict[str, dict[str, int | bool]]
    | list[dict[str, str | dict[str, list[str]] | dict[str, int]]],
]:
    """Validate translations from packages.

    :param packages: List of package names to check like ['invenio-app-rdm']
    :return: Summary of all issues found
    """
    all_validation_reports: list[
        dict[str, str | dict[str, list[str]] | dict[str, int]]
    ] = []

    for package_name in packages:
        validation_reports = get_package_validation_reports(package_name)
        all_validation_reports.extend(validation_reports)

    summary = _calculate_validation_report(all_validation_reports, packages)

    return summary


def _calculate_validation_report(
    reports: list[dict[str, str | dict[str, list[str]] | dict[str, int]]],
    packages: list[str],
) -> dict[
    str,
    dict[str, int]
    | dict[str, dict[str, int | list[dict[str, dict[str, int]]]]]
    | dict[str, dict[str, int | bool]]
    | list[dict[str, str | dict[str, list[str]] | dict[str, int]]],
]:
    """Create a summary of all validation issues.

    :param reports: Individual reports from each package
    :param packages: Names of packages that were checked
    :return: Combined summary with totals and details
    """
    package_breakdown: dict[str, dict] = {}
    language_breakdown: dict[str, dict] = {}

    for report in reports:
        pkg = report["package"]
        locale = report["locale"]
        counts = report["counts"]

        if pkg not in package_breakdown:
            package_breakdown[pkg] = {
                "locales": 0,
                "totalIssues": 0,
                "untranslatedStrings": 0,
                "fuzzyTranslations": 0,
                "problematicLanguages": [],
            }
        package_breakdown[pkg]["locales"] += 1
        package_breakdown[pkg]["totalIssues"] += sum(counts.values())
        package_breakdown[pkg]["untranslatedStrings"] += counts["untranslated"]
        package_breakdown[pkg]["fuzzyTranslations"] += counts["fuzzyTranslations"]
        if sum(counts.values()) > 0:
            package_breakdown[pkg]["problematicLanguages"].append(
                {"locale": locale, "issues": counts}
            )

        if locale not in language_breakdown:
            language_breakdown[locale] = {
                "packages": 0,
                "totalIssues": 0,
                "untranslatedStrings": 0,
                "fuzzyTranslations": 0,
                "isComplete": True,
            }
        language_breakdown[locale]["packages"] += 1
        language_breakdown[locale]["totalIssues"] += sum(counts.values())
        language_breakdown[locale]["untranslatedStrings"] += counts["untranslated"]
        language_breakdown[locale]["fuzzyTranslations"] += counts["fuzzyTranslations"]
        if sum(counts.values()) > 0:
            language_breakdown[locale]["isComplete"] = False

    all_locales = {report["locale"] for report in reports}

    summary_data = {
        "totalPackages": len(packages),
        "totalLocales": len(all_locales),
        "totalIssues": sum(sum(r["counts"].values()) for r in reports),
        "untranslatedStrings": sum(r["counts"]["untranslated"] for r in reports),
        "fuzzyTranslations": sum(r["counts"]["fuzzyTranslations"] for r in reports),
    }

    return {
        "summary": summary_data,
        "packageBreakdown": package_breakdown,
        "languageBreakdown": language_breakdown,
        "reports": reports,
    }
