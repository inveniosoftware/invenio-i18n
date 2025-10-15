# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and it
# under the terms of the MIT License; see LICENSE file for more details.
"""Collect PO translations, convert to JSON, and validate."""

from __future__ import annotations

from pathlib import Path

import polib

from .convert import po_to_i18next_json
from .discovery import (
    find_package_path,
    iter_po_files,
    normalize_package_to_module_name,
)
from .io import write_json_file
from .validate import validate_po


def scan_package_for_translations(package_name: str) -> dict[str, dict[str, str]]:
    """Get all translations from one package.

    :param package_name: Name of the package like 'invenio-app-rdm'
    :return: Translations organized by language like {"de": {...}, "fr": {...}}
    """

    package_root = find_package_path(package_name)
    translations_by_locale = {}

    if not package_root:
        return translations_by_locale

    for locale, po_path in iter_po_files(package_root, package_name):
        pofile = polib.pofile(str(po_path))
        translations_by_locale[locale] = po_to_i18next_json(pofile, package_name)

    return translations_by_locale


def scan_package_for_validation(package_name: str) -> list[dict]:
    """Check one package for translation problems.

    :param package_name: Name of the package to check like 'invenio-app-rdm'
    :return: List of reports showing what needs to be fixed
    """

    package_root = find_package_path(package_name)
    validation_reports = []

    if not package_root:
        return validation_reports

    for locale, po_path in iter_po_files(package_root, package_name):
        pofile = polib.pofile(str(po_path))
        validation_reports.append(validate_po(pofile, package_name, locale, po_path))

    return validation_reports


def collect_translations_to_json(
    packages: list[str],
    output_dir: Path,
) -> dict:
    """Collect translations from packages and save as JSON files.

    :param packages: List of package names like ['invenio-app-rdm', 'invenio-rdm-records']
    :param output_dir: Where to save the translation files
    :return: Summary with number of packages and languages processed
    """

    results: dict[str, dict[str, dict[str, str]]] = {}

    for package_name in packages:
        translations_by_locale = scan_package_for_translations(package_name)

        # Write per-package JSON under translations/<package>/translations.json
        if translations_by_locale:
            normalized_name = normalize_package_to_module_name(package_name)
            package_output = output_dir / normalized_name / "translations.json"
            write_json_file(package_output, translations_by_locale)

            # Store for merged output
            for locale, translations in translations_by_locale.items():
                if locale not in results:
                    results[locale] = {}
                results[locale][normalized_name] = translations

    # Write merged per-locale JSON (locale -> package -> keys)
    merged = results
    write_json_file(output_dir / "translations.json", merged)

    return {
        "packagesProcessed": len(packages),
        "locales": sorted(list(merged.keys())),
    }


def validate_translations_from_packages(
    packages: list[str],
    output_dir: Path,
) -> dict:
    """Check translations for problems and save a report.

    :param packages: List of package names to check like ['invenio-app-rdm']
    :param output_dir: Where to save the validation report
    :return: Summary of all issues found
    """

    all_validation_reports = []

    for package_name in packages:
        validation_reports = scan_package_for_validation(package_name)
        all_validation_reports.extend(validation_reports)

    summary = _summarize_validation_reports(all_validation_reports, packages)

    report_path = output_dir / "validation-report.json"
    write_json_file(report_path, summary)

    return summary


def _summarize_validation_reports(reports: list[dict], packages: list[str]) -> dict:
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
