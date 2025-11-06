# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Translation collection and validation utilities.

This module helps you work with translation files (.po files) from Invenio packages.
You can collect translations, convert them to JSON, and check for problems.

Collection - translation utilities
----------
Get translations from packages and convert them to JSON:

>>> from invenio_i18n.translation_utilities import collect_translations
>>> data = collect_translations(['invenio-app-rdm'])
>>> 'translations_by_package' in data
True

Use :func:`write_translations_to_json` to save the results to files.

Validation
----------
Check translation files for problems:

>>> from invenio_i18n.translation_utilities import validate_translations
>>> report = validate_translations(['invenio-app-rdm'])
>>> 'summary' in report
True

The report shows:
- **Untranslated**: Missing translations (empty ``msgstr``)
- **Fuzzy**: Translations marked with ``#, fuzzy`` that need review
- **Obsolete**: Old translations no longer used

Discovery
---------
Find where packages are installed and locate their translation files:

>>> from invenio_i18n.translation_utilities import find_package_path, find_po_files
>>> package_root = find_package_path('invenio-app-rdm')
>>> if package_root:
...     for locale, po_path in find_po_files(package_root, 'invenio-app-rdm'):
...         print(f"{locale}: {po_path}")

CLI Commands
------------
You can also use these from the command line:

.. code-block:: console

   $ invenio i18n create-global-pot -p invenio-app-rdm
   $ invenio i18n validate-translations -p invenio-app-rdm
   $ invenio i18n update-translation -p invenio-app-rdm -l de --msgid "Save" --msgstr "Speichern"
"""

from __future__ import annotations

from .collect import (
    collect_translations,
    get_package_translations,
    get_package_validation_reports,
    validate_translations,
    write_translations_to_json,
    write_validation_report,
)
from .convert import po_to_i18next_json
from .discovery import (
    find_package_path,
    find_po_files,
    normalize_package_to_module_name,
)
from .io import write_json_file
from .validate import validate_po

__all__ = [
    "collect_translations",
    "find_package_path",
    "find_po_files",
    "get_package_translations",
    "get_package_validation_reports",
    "normalize_package_to_module_name",
    "po_to_i18next_json",
    "validate_po",
    "validate_translations",
    "write_json_file",
    "write_translations_to_json",
    "write_validation_report",
]
