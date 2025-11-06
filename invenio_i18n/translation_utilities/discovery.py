# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and it
# under the terms of the MIT License; see LICENSE file for more details.
"""Discovery helpers for i18n service."""

from __future__ import annotations

from collections.abc import Iterable
from importlib.metadata import distributions
from importlib.resources import files
from importlib.util import find_spec
from pathlib import Path
from typing import Optional

from invenio_base.utils import entry_points


def package_name_to_module_name(package_name: str) -> str:
    """Convert package name to module name (replace - with _).

    Converts package names like 'invenio-app-rdm' to module names like 'invenio_app_rdm'.

    :param package_name: Package name like 'invenio-app-rdm'
    :return: Module name like 'invenio_app_rdm'
    """
    return package_name.replace("-", "_")


def find_package_path(package_name: str) -> Optional[Path]:
    """Find where a package is installed on your computer.

    :param package_name: Name of the package to find
    :return: Path to the package folder, or None if not found
    """
    module_name = package_name_to_module_name(package_name)
    spec = find_spec(module_name)
    if not spec or not spec.submodule_search_locations:
        return None
    return Path(list(spec.submodule_search_locations)[0])


def _get_translation_roots(package_root: Path, package_name: str) -> list[Path]:
    """Get standard translation root paths for a package.

    :param package_root: Folder where the package is located
    :param package_name: Name of the package
    :return: List of potential translation root paths
    """
    return [
        package_root / "translations",
        package_root / package_name_to_module_name(package_name) / "translations",
    ]


def _find_po_files_in_roots(
    translation_roots: list[Path], po_file_path: Path
) -> Iterable[tuple[str, Path]]:
    """Find PO files in translation root directories.

    :param translation_roots: List of base paths to search
    :param po_file_path: Relative path to PO file from locale directory
        (e.g., Path("LC_MESSAGES/messages.po"))
    :return: Pairs of (language, file_path)
    """
    for base in translation_roots:
        if not base.exists():
            continue
        for locale_dir in sorted(base.iterdir()):
            if not locale_dir.is_dir():
                continue
            po_path = locale_dir / po_file_path
            if po_path.exists():
                yield locale_dir.name, po_path


def find_po_files(package_root: Path, package_name: str) -> Iterable[tuple[str, Path]]:
    """Find all translation files in a package.

    :param package_root: Folder where the package is located
    :param package_name: Name of the package
    :return: Pairs of (language, file_path) like ('de', '/path/to/messages.po')
    """
    translation_roots = _get_translation_roots(package_root, package_name)
    yield from _find_po_files_in_roots(
        translation_roots, Path("LC_MESSAGES") / "messages.po"
    )


def find_bundle_path(bundle_name: str) -> Optional[Path]:
    """Find translation bundle via entrypoint.

    :param bundle_name: Bundle name (e.g., 'invenio-translations-de')
    :return: Path to bundle's translations/ directory, or None if not found
    """
    for ep in entry_points(group="invenio_i18n.translations_bundle"):
        if ep.name == bundle_name:
            translations_dir = files(ep.module) / "translations"
            if translations_dir.is_dir():
                return Path(str(translations_dir))
    return None


def find_bundle_po_file(bundle_root: Path, locale: str) -> Optional[Path]:
    """Find PO file for a specific locale in a translation bundle.

    :param bundle_root: Path to bundle's translations/ directory
    :param locale: Language code like 'de' or 'fr'
    :return: Path to PO file, or None if not found
    """
    po_path = bundle_root / locale / "LC_MESSAGES" / "messages.po"
    if po_path.exists():
        return po_path
    return None


def find_all_bundles() -> Iterable[tuple[str, Path]]:
    """Find all translation bundles via entrypoints.

    :return: Pairs of (bundle_name, bundle_root_path)
    """
    for ep in entry_points(group="invenio_i18n.translations_bundle"):
        translations_dir = files(ep.module) / "translations"
        if translations_dir.is_dir():
            yield ep.name, Path(str(translations_dir))


def find_js_po_files(
    package_root: Path, package_name: str
) -> Iterable[tuple[str, Path]]:
    """Find all JavaScript translation files (messages-js.po) in a package.

    :param package_root: Folder where the package is located
    :param package_name: Name of the package
    :return: Pairs of (language, file_path) like ('de', '/path/to/messages-js.po')
    """
    module_name = package_name_to_module_name(package_name)

    translation_roots = _get_translation_roots(package_root, package_name)
    yield from _find_po_files_in_roots(
        translation_roots, Path("LC_MESSAGES") / "messages-js.po"
    )

    # assets locations: assets/ or theme/assets/semantic-ui/translations/<package>/messages/<locale>/messages.po
    js_assets_paths = [
        package_root
        / "assets"
        / "semantic-ui"
        / "translations"
        / module_name
        / "messages",
        package_root
        / "theme"
        / "assets"
        / "semantic-ui"
        / "translations"
        / module_name
        / "messages",
    ]
    yield from _find_po_files_in_roots(js_assets_paths, Path("messages.po"))


def find_all_packages_with_translations(
    prefix: Optional[str] = None,
) -> Iterable[tuple[str, Path]]:
    """Find all packages that have translation files.

    :param prefix: Optional prefix to filter packages (e.g., "invenio_").
    :return: Pairs of (package_name, package_root_path)
    """
    seen = set()

    for ep in entry_points(group="invenio_i18n.translations"):
        try:
            package_name = ep.name
            module_name = package_name_to_module_name(package_name)

            if prefix and not module_name.startswith(prefix):
                continue
            if package_name in seen:
                continue

            package_root = find_package_path(package_name)
            if package_root:
                for _loc, _path in find_po_files(package_root, package_name):
                    seen.add(package_name)
                    yield package_name, package_root
                    break
        except Exception:
            continue

    if prefix:
        for dist in distributions():
            try:
                package_name = dist.metadata["Name"]
                module_name = package_name_to_module_name(package_name)

                if not module_name.startswith(prefix) or package_name in seen:
                    continue

                package_root = find_package_path(package_name)
                if package_root:
                    for _loc, _path in find_po_files(package_root, package_name):
                        seen.add(package_name)
                        yield package_name, package_root
                        break
            except (KeyError, Exception):
                continue
