# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2025 TUBITAK ULAKBIM.
# Copyright (C) 2025 University of Münster.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CLI for Invenio internationalization module."""
import subprocess
import traceback
from json import JSONDecodeError, dump, load
from pathlib import Path

import polib
from click import Path as ClickPath
from click import group, option, secho
from flask import current_app
from flask.cli import with_appcontext
from invenio_base.utils import entry_points
from jinja2 import BaseLoader, Environment

from .translation_utilities import (
    collect_translations,
)
from .translation_utilities import (
    validate_translations as validate_translations_from_packages,
)
from .translation_utilities import (
    write_translations_to_json,
    write_validation_report,
)
from .translation_utilities.discovery import (
    find_package_path,
    find_po_files,
    normalize_package_to_module_name,
)

TRANSIFEX_CONFIG_TEMPLATE = """
[main]
host = https://www.transifex.com

[o:inveniosoftware:p:invenio:r:{{- resource }}]
file_filter = {{- temporary_cache }}/{{- package }}/<lang>/messages.po
source_file = {{- package }}/assets/semantic-ui/translations/{{- package }}/translations.pot
source_lang = en
type = PO
"""


def source_translation_files(input_directory):
    """Map source translation file contents to their languages."""
    for source_file in input_directory.iterdir():
        if not source_file.is_file() or source_file.suffix != ".json":
            msg = f"source file: {source_file} is not meant to be distributed."
            secho(msg, fg="yellow")
            continue

        language = source_file.stem

        with source_file.open("r") as source_file:
            try:
                obj = load(source_file)
            except JSONDecodeError as error:
                tb = traceback.format_exc()
                msg = f"ERROR: source file: {source_file.name} couldn't be loaded because of error: {str(error)}\n{tb}"
                secho(msg, fg="red")
            else:
                yield language, obj


def calculate_target_packages(
    exceptional_package_names,
    entrypoint_group,
    language,
):
    """Calculate target package translation paths.

    Maps each package to its target translation file path by inspecting entrypoint and handling exceptional package names.
    """
    package_translations_paths = {}

    for entry_point in entry_points(group=entrypoint_group):
        package_name = entry_point.name
        package_path = Path(entry_point.load().path)

        # Some webpack entry points use names that differ from their package names.
        # Map these exceptional webpack entry‑point names to their correct package names.
        package_name = exceptional_package_names.get(package_name, package_name)

        target_translations_path = (
            package_path / "translations" / package_name / "messages" / language
        )

        package_translations_paths[package_name] = (
            target_translations_path / "translations.json"
        )

    return package_translations_paths


def create_transifex_configuration(temporary_cache, js_resources):
    """Create a transifex fetch configuration.

    This configuration is built dynamically because the targeted packages are
    customizable over the configuration variable I18N_TRANSIFEX_JS_RESOURCES_MAP.
    """
    environment = Environment(loader=BaseLoader())
    config_template = environment.from_string(TRANSIFEX_CONFIG_TEMPLATE)

    with Path(temporary_cache / "collected_config").open("w") as fp:
        for resource, package in js_resources.items():
            config = config_template.render(
                temporary_cache=temporary_cache,
                resource=resource,
                package=package,
            )
            fp.write(config)
            fp.write("\n\n")


def fetch_translations_from_transifex(token, temporary_cache, languages, js_resources):
    """Fetch translations from transifex."""
    temporary_cache.mkdir(parents=True, exist_ok=True)

    create_transifex_configuration(temporary_cache, js_resources)

    transifex_pull_cmd = [
        "tx",
        f"--token={token}",
        f"--config={temporary_cache}/collected_config",
        "pull",
        f"--languages={languages}",
        "--force",
    ]
    subprocess.run(transifex_pull_cmd)


def map_to_i18next_style(po_file):
    """Map translations from po to i18next style.

    Plurals need a special format.
    """
    obj = {}
    for entry in po_file:
        obj[entry.msgid] = entry.msgstr
        if entry.msgstr_plural:
            obj[entry.msgid] = entry.msgstr_plural[0]
            obj[entry.msgid + "_plural"] = entry.msgstr_plural[1]
    return obj


@group(chain=True)
@with_appcontext
def i18n():
    """i18n commands."""


@i18n.command()
@option(
    "-i",
    "--input-directory",
    required=True,
    type=ClickPath(
        exists=True, file_okay=False, dir_okay=True, writable=False, path_type=Path
    ),
    help="Input directory containing translations in JSON format.",
)
@option(
    "--entrypoint-group",
    default="invenio_assets.webpack",
    help="Entrypoint group used to get package assets paths. Default: \"invenio_assets.webpack\" You don't need to set this option under normal circumstances.'",
)
def distribute_js_translations(input_directory: Path, entrypoint_group: str):
    """
    Distribute package‑specific JavaScript translations.

    Usage
    -----
    .. code-block:: console
       $ invenio i18n distribute-js-translations -i js_translations/

    The command expects an input directory that contains one unified JSON file per
    language, named after the locale code—e.g., de.json, tr.json, de_AT.json, etc.

    The ``invenio i18n fetch-from-transifex`` command can be used to retrieve translations from Transifex and unify them.

    The command uses invenio_assets.webpack entrypoint group to determine package asset paths. In order for the command to work properly, add the following config to the ``invenio.cfg``:

    .. code-block:: python
       I18N_JS_DISTR_EXCEPTIONAL_PACKAGE_MAP = {
         "jobs": "invenio_jobs",
         "invenio_previewer_theme": "invenio_previewer",
         "invenio_app_rdm_theme": "invenio_app_rdm",
       }


    Distribution of translation
    ---------------------------
    This CLI command processes unified per‑language JSON files in a given input path.  The command extracts translations that belong to the target package, discovers asset root paths of packages through the ``invenio_assets.webpack``
    entry‑point group and writes it to the package’s  translation folder in react-i18next format here.

    For example, for locale ``tr`` the extracted fragment for
    ``invenio_communities`` is written to:

    ``<site‑packages>/invenio-communities/assets/semantic-ui/translations/invenio_communities/messages/tr/translations.json``

    Missing directories and files will be created automatically if not exist.
    """
    exceptional_package_names = current_app.config[
        "I18N_JS_DISTR_EXCEPTIONAL_PACKAGE_MAP"
    ]

    # Read unified source translation files and distribute translations to relevant packages
    for language, unified_translations in source_translation_files(input_directory):
        target_packages = calculate_target_packages(
            exceptional_package_names, entrypoint_group, language
        )

        for package_name, translations in unified_translations.items():
            if package_name not in target_packages:
                msg = f"Package {package_name} doesn't have webpack entrypoint. Skipping..."
                secho(msg, fg="yellow")
                continue

            target_file = target_packages[package_name]

            if not target_file.parent.exists():
                msg = f"Translations directory for {package_name} in language {language} not found. Creating..."
                secho(msg, fg="yellow")
                target_file.parent.mkdir(parents=True)

            with target_file.open("w") as file_pointer:
                dump(translations, file_pointer, indent=2, ensure_ascii=False)

            msg = f"{package_name} translations for language {language} have been written."
            secho(msg, fg="green")


def _convert_to_list(ctx, param, value):
    """Convert Click's tuple from multiple=True to a list."""
    if value is None:
        return []
    return list(value)


@i18n.command()
@option(
    "--packages",
    "-p",
    multiple=True,
    required=True,
    callback=_convert_to_list,
    help="Packages to include. Can be specified multiple times.",
)
def create_global_pot(packages: list[str]):
    """Collect translations and write JSON files for testing.

    Collects PO translations from packages and converts them to JSON format.
    Output files are written to the i18n-collected/ directory.

    Examples:
        invenio i18n create-global-pot -p invenio-app-rdm -p invenio-rdm-records
        invenio i18n create-global-pot -p invenio-communities -p invenio-requests
    """
    # Collect translations to JSON
    output_dir = Path.cwd() / "i18n-collected"
    output_dir.mkdir(exist_ok=True)
    collected_data = collect_translations(packages)
    write_translations_to_json(collected_data, output_dir)
    secho(
        f"Collected translations for {collected_data['packagesProcessed']} packages into {output_dir}",
        fg="green",
    )
    secho(f"Wrote merged JSON: {output_dir / 'translations.json'}", fg="blue")
    secho(
        "Per‑package JSON under: i18n-collected/<package>/translations.json",
        fg="blue",
    )


@i18n.command()
@option(
    "--packages",
    "-p",
    multiple=True,
    required=True,
    callback=_convert_to_list,
    help="Packages to validate. Can be specified multiple times.",
)
def validate_translations(packages: list[str]):
    """Validate translation quality.

    Checks PO files for missing, fuzzy, and obsolete translations.
    Generates a validation report in i18n-collected/validation-report.json.

    Examples:
        invenio i18n validate-translations -p invenio-app-rdm -p invenio-rdm-records
        invenio i18n validate-translations -p invenio-communities -p invenio-requests
    """
    output_dir = Path.cwd() / "i18n-collected"
    output_dir.mkdir(exist_ok=True)

    try:
        summary = validate_translations_from_packages(packages)
        write_validation_report(summary, output_dir)
        report_path = output_dir / "validation-report.json"
        secho(f"Validation report written: {report_path}", fg="green")

        summary_data = summary.get("summary", {})
        secho(
            f"Summary: packages={summary_data.get('totalPackages', 0)}, "
            f"locales={summary_data.get('totalLocales', 0)}, "
            f"issues={summary_data.get('totalIssues', 0)}",
            fg="blue",
        )
    except Exception as e:
        secho(f"Error during validation: {e}", fg="red")


@i18n.command()
@option("--package", "-p", required=True, help="Package name like 'invenio-app-rdm'")
@option("--locale", "-l", required=True, help="Language code like 'de' or 'fr'")
@option("--msgid", required=True, help="Original English text")
@option("--msgstr", required=True, help="New translation")
def update_translation(package, locale, msgid, msgstr):
    r"""Update a translation and remove fuzzy flag.

    Usage: finds the PO file for the specified package and locale, updates the
    translation entry, and removes the fuzzy flag if present.

    Example:
        invenio i18n update-translation -p invenio-app-rdm -l de \\
            --msgid "Upload file" --msgstr "Datei hochladen"
    """
    package_root = find_package_path(package)
    if not package_root:
        secho(f"Package {package} not found", fg="red")
        return

    po_path = None
    for loc, path in find_po_files(package_root, package):
        if loc == locale:
            po_path = path
            break

    if not po_path:
        secho(f"No PO file found for {package} in locale {locale}", fg="red")
        return

    try:
        po_file = polib.pofile(str(po_path))
        updated = False

        for entry in po_file:
            if entry.msgid == msgid:
                entry.msgstr = msgstr
                if "fuzzy" in entry.flags:
                    entry.flags.remove("fuzzy")
                updated = True
                break

        if updated:
            po_file.save()
            secho(
                f"Updated translation for '{msgid}' in {package}/translations/{locale}",
                fg="green",
            )
        else:
            secho(
                f"Translation '{msgid}' not found in {package}/translations/{locale}",
                fg="yellow",
            )

    except Exception as e:
        secho(f"Error updating translation: {e}", fg="red")


@i18n.command()
@option("--token", "-t", required=True, help="API token for your Transifex account.")
@option(
    "--languages",
    "-l",
    required=True,
    help="Languages you want to download translations for. One or multiple comma separated values, e.g. 'de,en,fr'.",
)
@option(
    "--output-directory",
    "-o",
    required=True,
    type=ClickPath(
        exists=True, file_okay=False, dir_okay=True, writable=True, path_type=Path
    ),
    help="Directory to which collected translations in JSON format should be written.",
)
def fetch_from_transifex(token, languages, output_directory):
    """Retrieve package translations from Transifex and unify them to a single file using i18next format.

    Usage
    -----
    .. code-block:: console
       $ invenio i18n fetch-from-transifex -t <your transifex API token> -l 'de,en,fr' -o js_translations/

    The command expects an API token associated with a Transifex account to be able to pull translations.
    Such a token can be generated in the user settings on the Transifex website.

    The output directory will be used to store downloaded translations per package as well as the unified translation file.

    To supply the packages for which translations should be pulled, add the following config to your instance's ``invenio.cfg``:

    .. code-block:: python
        I18N_TRANSIFEX_JS_RESOURCES_MAP = {
            "invenio-administration-messages-ui": "invenio_administration",
            "invenio-app-rdm-messages-ui": "invenio_app_rdm",
            "invenio-communities-messages-ui": "invenio_communities",
            "invenio-rdm-records-messages-ui": "invenio_rdm_records",
            "invenio-requests-messages-ui": "invenio_requests",
            "invenio-search-ui-messages-js": "invenio_search_ui"
        }

    Fetching and unifying of translations
    ---------------------------
    This CLI command pulls translations in PO format from Transifex for all packages specified in the config.
    It will then unify all translations to a single JSON file in a format that can be used with the i18next library.
    The unified file will contain keys for package names on the top level and a nested dict with translation keys and values for each package, e.g.:

    .. code-block:: json
        {
            "invenio_administration": {
                "Error": "Fehler",
                "Save": "Speichern",
                ...
            },
            "invenio_app_rdm": {
                "Basic information": "Allgemeine Informationen",
                "New": "Neu",
                ...
            },
            ...
        }
    """
    js_resources = current_app.config["I18N_TRANSIFEX_JS_RESOURCES_MAP"]

    temporary_cache = output_directory / "tmp"

    fetch_translations_from_transifex(token, temporary_cache, languages, js_resources)

    collected_translations = {}

    for language in languages.split(","):
        collected_translations[language] = {}

        for package in js_resources.values():
            po_path = f"{temporary_cache}/{package}/{language}/messages.po"
            po_file = polib.pofile(po_path)

            collected_translations[language][package] = map_to_i18next_style(po_file)

        output_file = Path(f"{output_directory}/{language}.json")
        with output_file.open("w", encoding="utf-8") as fp:
            dump(collected_translations[language], fp, indent=4, ensure_ascii=False)
