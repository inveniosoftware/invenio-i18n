# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Validation helpers for i18n service."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Optional

from polib import POFile, pofile

from .discovery import find_package_path, find_po_files, package_name_to_module_name
from .io import write_json_file


@dataclass
class Issues:
    """Translation issues found in a PO file."""

    untranslated: list[str] = field(default_factory=list)
    fuzzy: list[str] = field(default_factory=list)
    obsolete: list[str] = field(default_factory=list)


@dataclass
class Counts:
    """Counts of translation issues."""

    untranslated: int = 0
    fuzzyTranslations: int = 0
    obsoleteTranslations: int = 0

    @classmethod
    def from_issues(cls, issues: Issues) -> Counts:
        """Create Counts from Issues object."""
        return cls(
            untranslated=len(issues.untranslated),
            fuzzyTranslations=len(issues.fuzzy),
            obsoleteTranslations=len(issues.obsolete),
        )

    @property
    def total(self) -> int:
        """Calculate total number of issues."""
        return self.untranslated + self.fuzzyTranslations + self.obsoleteTranslations


@dataclass
class ValidationReport:
    """Validation report for a single PO file."""

    package: str
    locale: str
    filename: Path
    issues: Issues
    counts: Counts


@dataclass
class PackageValidation:
    """Validation results for a package."""

    package_name: str
    reports: list[ValidationReport] = field(default_factory=list)


@dataclass
class ProblematicLanguage:
    """Information about a language with issues in a package."""

    locale: str
    counts: Counts


@dataclass
class PackageBreakdown:
    """Breakdown of issues by package."""

    locales: int = 0
    total_issues: int = 0
    untranslated_strings: int = 0
    fuzzy_translations: int = 0
    problematic_languages: list[ProblematicLanguage] = field(default_factory=list)


@dataclass
class LanguageBreakdown:
    """Breakdown of issues by language."""

    packages: int = 0
    total_issues: int = 0
    untranslated_strings: int = 0
    fuzzy_translations: int = 0
    is_complete: bool = True


@dataclass
class ValidationSummary:
    """Summary of validation results across all packages."""

    total_packages: int = 0
    total_locales: int = 0
    total_issues: int = 0
    untranslated_strings: int = 0
    fuzzy_translations: int = 0
    package_breakdown: dict[str, PackageBreakdown] = field(default_factory=dict)
    language_breakdown: dict[str, LanguageBreakdown] = field(default_factory=dict)
    reports: list[ValidationReport] = field(default_factory=list)


def validate_po(
    po_file: POFile, package_name: str, locale: str, po_path: Path
) -> ValidationReport:
    """Check one translation file for problems.

    :param po_file: The translation file to check
    :param package_name: Name of the package
    :param locale: Language code like 'de' or 'fr'
    :param po_path: Path to the file being checked
    :return: ValidationReport with all issues found
    """
    issues = Issues()

    for entry in po_file:
        if entry.obsolete:
            issues.obsolete.append(entry.msgid)
        elif "fuzzy" in entry.flags:
            issues.fuzzy.append(entry.msgid)
        elif not entry.msgstr and not entry.msgstr_plural:
            issues.untranslated.append(entry.msgid)

    counts = Counts.from_issues(issues)

    return ValidationReport(
        package=package_name_to_module_name(package_name),
        locale=locale,
        filename=po_path,
        issues=issues,
        counts=counts,
    )


def get_package_validation_report(
    package_name: str, locales: Optional[list[str]] = None
) -> PackageValidation:
    """Get validation reports for one package.

    :param package_name: Name of the package to check like 'invenio-app-rdm'
    :param locales: Optional list of locales to filter. If None, all locales are included.
    :return: PackageValidation with reports for specified locales
    """
    package_root = find_package_path(package_name)
    package_validation = PackageValidation(package_name=package_name)

    if not package_root:
        return package_validation

    for locale, po_path in find_po_files(package_root, package_name):
        if locales is not None and locale not in locales:
            continue
        po_file = pofile(str(po_path))
        package_validation.reports.append(
            validate_po(po_file, package_name, locale, po_path)
        )

    return package_validation


def validate_translations(
    packages: list[str], locales: Optional[list[str]] = None
) -> ValidationSummary:
    """Validate translations from packages.

    :param packages: List of package names to check like ['invenio-app-rdm']
    :param locales: Optional list of locales to filter. If None, all locales are included.
    :return: ValidationSummary with all issues found
    """
    package_validations = [
        get_package_validation_report(package, locales) for package in packages
    ]

    return calculate_validation_summary(package_validations, packages)


def calculate_validation_summary(
    package_validations: list[PackageValidation], packages: list[str]
) -> ValidationSummary:
    """Create a summary of all validation issues.

    :param package_validations: Individual package validations
    :param packages: Names of packages that were checked
    :return: Combined summary with totals and details
    """
    all_reports: list[ValidationReport] = []
    for pv in package_validations:
        all_reports.extend(pv.reports)

    package_breakdown: dict[str, PackageBreakdown] = {}
    language_breakdown: dict[str, LanguageBreakdown] = {}

    for report in all_reports:
        pkg = report.package
        locale = report.locale
        counts = report.counts

        if pkg not in package_breakdown:
            package_breakdown[pkg] = PackageBreakdown()
        package_breakdown[pkg].locales += 1
        total_issues = counts.total
        package_breakdown[pkg].total_issues += total_issues
        package_breakdown[pkg].untranslated_strings += counts.untranslated
        package_breakdown[pkg].fuzzy_translations += counts.fuzzyTranslations
        if total_issues > 0:
            package_breakdown[pkg].problematic_languages.append(
                ProblematicLanguage(
                    locale=locale,
                    counts=replace(counts),
                )
            )

        if locale not in language_breakdown:
            language_breakdown[locale] = LanguageBreakdown()
        language_breakdown[locale].packages += 1
        language_breakdown[locale].total_issues += total_issues
        language_breakdown[locale].untranslated_strings += counts.untranslated
        language_breakdown[locale].fuzzy_translations += counts.fuzzyTranslations
        if total_issues > 0:
            language_breakdown[locale].is_complete = False

    all_locales = {report.locale for report in all_reports}

    # Calculate totals from all reports
    total_issues = sum(r.counts.total for r in all_reports)
    untranslated_strings = sum(r.counts.untranslated for r in all_reports)
    fuzzy_translations = sum(r.counts.fuzzyTranslations for r in all_reports)

    return ValidationSummary(
        total_packages=len(packages),
        total_locales=len(all_locales),
        total_issues=total_issues,
        untranslated_strings=untranslated_strings,
        fuzzy_translations=fuzzy_translations,
        package_breakdown=package_breakdown,
        language_breakdown=language_breakdown,
        reports=all_reports,
    )


def _problematic_language_to_dict(lang: ProblematicLanguage) -> dict:
    """Convert ProblematicLanguage to dictionary for JSON."""
    return {
        "locale": lang.locale,
        "issues": {
            "untranslated": lang.counts.untranslated,
            "fuzzyTranslations": lang.counts.fuzzyTranslations,
            "obsoleteTranslations": lang.counts.obsoleteTranslations,
        },
    }


def _package_breakdown_to_dict(breakdown: PackageBreakdown) -> dict:
    """Convert PackageBreakdown to dictionary for JSON."""
    return {
        "locales": breakdown.locales,
        "totalIssues": breakdown.total_issues,
        "untranslatedStrings": breakdown.untranslated_strings,
        "fuzzyTranslations": breakdown.fuzzy_translations,
        "problematicLanguages": [
            _problematic_language_to_dict(lang)
            for lang in breakdown.problematic_languages
        ],
    }


def _language_breakdown_to_dict(breakdown: LanguageBreakdown) -> dict:
    """Convert LanguageBreakdown to dictionary for JSON."""
    return {
        "packages": breakdown.packages,
        "totalIssues": breakdown.total_issues,
        "untranslatedStrings": breakdown.untranslated_strings,
        "fuzzyTranslations": breakdown.fuzzy_translations,
        "isComplete": breakdown.is_complete,
    }


def _validation_report_to_dict(report: ValidationReport) -> dict:
    """Convert ValidationReport to dictionary for JSON."""
    return {
        "package": report.package,
        "locale": report.locale,
        "file": str(report.filename),
        "issues": {
            "untranslated": report.issues.untranslated,
            "fuzzyTranslations": report.issues.fuzzy,
            "obsoleteTranslations": report.issues.obsolete,
        },
        "counts": {
            "untranslated": report.counts.untranslated,
            "fuzzyTranslations": report.counts.fuzzyTranslations,
            "obsoleteTranslations": report.counts.obsoleteTranslations,
        },
    }


def write_validation_report(
    validation_summary: ValidationSummary, output_dir: Path
) -> None:
    """Write validation report to JSON file.

    :param validation_summary: Output from validate_translations()
    :param output_dir: Where to save the validation report
    """
    report_dict = {
        "summary": {
            "totalPackages": validation_summary.total_packages,
            "totalLocales": validation_summary.total_locales,
            "totalIssues": validation_summary.total_issues,
            "untranslatedStrings": validation_summary.untranslated_strings,
            "fuzzyTranslations": validation_summary.fuzzy_translations,
        },
        "packageBreakdown": {
            pkg: _package_breakdown_to_dict(breakdown)
            for pkg, breakdown in validation_summary.package_breakdown.items()
        },
        "languageBreakdown": {
            locale: _language_breakdown_to_dict(breakdown)
            for locale, breakdown in validation_summary.language_breakdown.items()
        },
        "reports": [_validation_report_to_dict(r) for r in validation_summary.reports],
    }

    report_path = output_dir / "validation-report.json"
    write_json_file(report_path, report_dict)
