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
from importlib.util import find_spec
from pathlib import Path


def normalize_package_to_module_name(package_name: str) -> str:
    """Convert package name to module name (replace - with _).

    :param package_name: Package name like 'invenio-app-rdm'
    :return: Module name like 'invenio_app_rdm'
    """
    return package_name.replace("-", "_")


def find_package_path(package_name: str) -> Path | None:
    """Find where a package is installed on your computer.

    :param package_name: Name of the package to find
    :return: Path to the package folder, or None if not found
    """
    module_name = normalize_package_to_module_name(package_name)
    spec = find_spec(module_name)
    if not spec or not spec.submodule_search_locations:
        return None
    return Path(list(spec.submodule_search_locations)[0])


def find_po_files(package_root: Path, package_name: str) -> Iterable[tuple[str, Path]]:
    """Find all translation files in a package.

    :param package_root: Folder where the package is located
    :param package_name: Name of the package
    :return: Pairs of (language, file_path) like ('de', '/path/to/messages.po')
    """
    # Candidate roots: package-level "translations" or module-nested "<module>/translations"
    candidates: list[Path] = [
        package_root / "translations",
        package_root / normalize_package_to_module_name(package_name) / "translations",
    ]

    for base in candidates:
        if not base.exists():
            continue
        # Each subdirectory is a locale (e.g., de, fr, zh_CN)
        for locale_dir in sorted(base.iterdir()):
            if not locale_dir.is_dir():
                continue
            po_path = locale_dir / "LC_MESSAGES" / "messages.po"
            if po_path.exists():
                yield locale_dir.name, po_path
