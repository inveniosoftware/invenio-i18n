# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Translation collection, conversion, validation, and distribution utilities.

Utilities for working with translation files (.po files) from Invenio packages.
Supports both Python and JavaScript translations: collection, conversion, validation,
and distribution.

COLLECTION  --------
Collect translations from packages and convert to JSON:

.. code-block:: python

    from invenio_i18n.translation_utilities import collect_translations
    data = collect_translations(['invenio-app-rdm'], locales=['de', 'en'])
    # Returns a list of PackageTranslation objects

Use :func:`write_translations_to_json` to save the results to files.

CONVERSION  ------
Convert PO files to i18next JSON format for JavaScript:

.. code-block:: python

    from invenio_i18n.translation_utilities import po_to_i18next_json
    from polib import pofile
    from pathlib import Path

    po_file_path = Path("translations/de/LC_MESSAGES/messages.po")
    po_file = pofile(str(po_file_path))
    json_data = po_to_i18next_json(po_file, "invenio-i18n")

VALIDATION  ------
Check translation files for problems:

.. code-block:: python

    from invenio_i18n.translation_utilities import validate_translations
    report = validate_translations(['invenio-app-rdm'])
    # Returns a ValidationSummary object with validation results

The validation report identifies:
- **Untranslated**: missing translations (empty ``msgstr``)
- **Fuzzy**: translations marked with ``#, fuzzy`` that need review
- **Obsolete**: old translations no longer used

DISCOVERY  ------
Find where packages are installed and locate their translation files:

.. code-block:: python

    from invenio_i18n.translation_utilities import find_package_path, find_po_files
    package_root = find_package_path('invenio-app-rdm')
    if package_root:
        for locale, po_path in find_po_files(package_root, 'invenio-app-rdm'):
            print(f"{locale}: {po_path}")

Find JavaScript-specific PO files:

.. code-block:: python

    from invenio_i18n.translation_utilities import find_js_po_files
    if package_root:
        for locale, po_path in find_js_po_files(package_root, 'invenio-app-rdm'):
            print(f"JS {locale}: {po_path}")

Find translation bundles:

.. code-block:: python

    from invenio_i18n.translation_utilities import find_bundle_path, find_bundle_po_file
    bundle_root = find_bundle_path('invenio-translations-de')
    if bundle_root:
        po_path = find_bundle_po_file(bundle_root, 'de')
        if po_path:
            print(f"Bundle PO file: {po_path}")

CLI COMMANDS  ------

JavaScript Translation Commands:
    - ``js-translation build``: build JavaScript translations (collect, convert, merge, distribute)
    - ``js-translation distribute``: distribute custom JSON translations to packages
    - ``js-translation update``: update a single JavaScript translation in PO file

Python/General Translation Commands:
    - ``build-translations``: collect Python PO translations and write JSON files
    - ``validate-translations``: validate translation for missing, fuzzy, obsolete
    - ``update-translation``: update a Python translation in package or bundle PO file

"""

from __future__ import annotations

from .collect import (
    collect_translations,
    get_package_translations,
    write_translations_to_json,
)
from .convert import po_to_i18next_json
from .discovery import (
    find_bundle_path,
    find_bundle_po_file,
    find_js_po_files,
    find_package_path,
    find_po_files,
    package_name_to_module_name,
)
from .io import write_json_file
from .validate import (
    get_package_validation_report,
    validate_po,
    validate_translations,
    write_validation_report,
)

__all__ = [
    "collect_translations",
    "find_bundle_path",
    "find_bundle_po_file",
    "find_js_po_files",
    "find_package_path",
    "find_po_files",
    "get_package_translations",
    "get_package_validation_report",
    "package_name_to_module_name",
    "po_to_i18next_json",
    "validate_po",
    "validate_translations",
    "write_json_file",
    "write_translations_to_json",
    "write_validation_report",
]
