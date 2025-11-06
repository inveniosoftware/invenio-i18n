# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and it
# under the terms of the MIT License; see LICENSE file for more details.
"""Collect PO translations and convert to JSON."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import polib
from polib import POFile

from .convert import po_to_i18next_json
from .discovery import find_package_path, find_po_files, package_name_to_module_name
from .io import write_json_file


@dataclass
class Message:
    """A single translation message."""

    msgid: str
    text: str


@dataclass
class TranslationBundle:
    """A bundle of translation messages for a specific locale."""

    locale: str
    messages: list[Message] = field(default_factory=list)


@dataclass
class PackageTranslation:
    """Translations for a package, organized by locale."""

    package_name: str
    translation_bundles: list[TranslationBundle] = field(default_factory=list)

    def add(self, locale: str, po_file: POFile) -> None:
        """Add translations from a PO file for a locale."""
        bundle = self.get_translation_bundle(locale)
        if bundle is None:
            bundle = TranslationBundle(locale=locale)
            self.translation_bundles.append(bundle)

        translations = po_to_i18next_json(po_file, self.package_name)
        for msgid, msgstr in translations.items():
            bundle.messages.append(Message(msgid=msgid, text=msgstr))

    def get_translation_bundle(self, locale: str) -> Optional[TranslationBundle]:
        """Get translation bundle for a locale, or None if not found."""
        for bundle in self.translation_bundles:
            if bundle.locale == locale:
                return bundle
        return None


def build_global_translation_bundle(
    locale: str,
    package_translations: list[PackageTranslation],
) -> dict[str, dict[str, str]]:
    """Build a global translation bundle for a locale from multiple packages.

    Combines translations from all packages for a specific locale into a single
    dictionary structure suitable for JSON output.

    :param locale: Locale code (e.g., 'de', 'en')
    :param package_translations: List of package translations to combine
    :return: Dictionary with package names as keys and their translations as values
    """
    result: dict[str, dict[str, str]] = {}

    for package_translation in package_translations:
        bundle = package_translation.get_translation_bundle(locale)
        if bundle:
            translations: dict[str, str] = {
                msg.msgid: msg.text for msg in bundle.messages
            }
            if translations:
                result[package_translation.package_name] = translations

    return result


def get_package_translations(
    package_name: str, locales: Optional[list[str]] = None
) -> PackageTranslation:
    """Get all translations from one package.

    :param package_name: Name of the package like 'invenio-app-rdm'
    :param locales: Optional list of locales to filter. If None, all locales are included.
    :return: PackageTranslation with translations organized by locale
    """
    package_root = find_package_path(package_name)
    normalized_name = package_name_to_module_name(package_name)
    package_translation = PackageTranslation(package_name=normalized_name)

    if not package_root:
        return package_translation

    for locale, po_path in find_po_files(package_root, package_name):
        if locales is not None and locale not in locales:
            continue
        po_file = polib.pofile(str(po_path))
        package_translation.add(locale, po_file)

    return package_translation


def collect_translations(
    packages: list[str], locales: Optional[list[str]] = None
) -> list[PackageTranslation]:
    """Collect translations from packages.

    :param packages: List of package names like ['invenio-app-rdm', 'invenio-rdm-records']
    :param locales: Optional list of locales to filter. If None, all locales are included.
    :return: List of PackageTranslation objects
    """
    package_translations: list[PackageTranslation] = []

    for package_name in packages:
        package_translation = get_package_translations(package_name, locales)
        if package_translation.translation_bundles:
            package_translations.append(package_translation)

    return package_translations


def write_translations_to_json(
    collected_data: list[PackageTranslation],
    output_file: Path,
    locales: list[str],
    write_package_wise_too: bool = False,
) -> None:
    """Write collected translations to JSON files.

    :param collected_data: Output from collect_translations()
    :param output_file: Path to output file (for single locale) or directory
    :param locales: List of locales to write
    :param write_package_wise_too: If True, also write per-package JSON files
    """
    for locale in locales:
        bundle_dict = build_global_translation_bundle(locale, collected_data)
        if bundle_dict:
            locale_file = (
                output_file.parent / f"{locale}.json"
                if output_file.is_file()
                else output_file / f"{locale}.json"
            )
            write_json_file(locale_file, bundle_dict)

    if write_package_wise_too:
        output_dir = output_file.parent if output_file.is_file() else output_file
        for package_translation in collected_data:
            translations_by_locale: dict[str, dict[str, str]] = {}
            for bundle in package_translation.translation_bundles:
                translations_by_locale[bundle.locale] = {
                    msg.msgid: msg.text for msg in bundle.messages
                }
            if translations_by_locale:
                package_output = (
                    output_dir / package_translation.package_name / "translations.json"
                )
                package_output.parent.mkdir(parents=True, exist_ok=True)
                write_json_file(package_output, translations_by_locale)
