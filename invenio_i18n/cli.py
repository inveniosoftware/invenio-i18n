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

from json import dump
from pathlib import Path
from typing import Optional

import polib
import rich_click as click
from flask import current_app
from flask.cli import with_appcontext
from rich_click import STRING
from rich_click import Path as ClickPath
from rich_click import group, option, secho

from .translation_utilities.collect import (
    collect_translations,
    write_translations_to_json,
)
from .translation_utilities.convert import po_to_i18next_json
from .translation_utilities.discovery import (
    find_all_packages_with_translations,
    find_bundle_path,
    find_bundle_po_file,
    find_js_po_files,
    find_package_path,
    find_po_files,
)
from .translation_utilities.validate import (
    validate_translations,
    write_validation_report,
)
from .utils import (
    collect_js_package_translations,
    convert_to_list,
    distribute_js_translations_from_directory,
    ensure_parent_directory,
    fetch_translations_from_transifex,
    has_translation_key,
    map_to_i18next_style,
    merge_bundle_js_layers,
    merge_instance_js_layers,
    update_po_file,
    write_js_translation_outputs,
)

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.USE_MARKDOWN = False


@group()
@with_appcontext
def i18n():
    """i18n commands."""


@i18n.group("js-translation")
def js_translation():
    """Javascript translation commands."""
    pass


@i18n.command("build-translations")
@option(
    "--packages",
    "-p",
    multiple=True,
    callback=convert_to_list,
    help="Packages to include. Can be specified multiple times.",
)
@option(
    "--all-packages",
    is_flag=True,
    help="Collect from all invenio_* packages",
)
@option("--all-locales", is_flag=True, help="Use all languages")
@option(
    "--locale",
    "-l",
    "locales",
    multiple=True,
    callback=convert_to_list,
    help="Languages to include",
)
@option("--prefix", type=STRING, default="invenio_")
@option(
    "--path-to-global-pot",
    "output_file",
    required=True,
    type=ClickPath(dir_okay=False, file_okay=True, writable=True, path_type=Path),
    callback=ensure_parent_directory,
    help="Output file path for the JSON translations file.",
)
@option(
    "--write-package-wise-too",
    is_flag=True,
    default=False,
    help="Also write per-package JSON files alongside the global file.",
)
def build_translations(
    packages: Optional[list[str]],
    locales: Optional[list[str]],
    prefix: str,
    output_file: Path,
    *,
    all_packages: bool,
    all_locales: bool,
    write_package_wise_too: bool,
):
    """Collect Python translations and write JSON files for testing.

    Collects Python PO translations from packages and converts them to JSON
    format (for testing/validation). Does not process JavaScript sources.

    Examples:
        invenio i18n build-translations -p invenio-app-rdm -p invenio-rdm-records -l de -l en
        invenio i18n build-translations --all-packages -l de
    """
    if all_packages and packages:
        secho(
            "Error: Provide --packages or --all-packages, they are mutual exclusive",
            fg="red",
        )
        return

    if all_locales and locales:
        secho(
            "Error: Provide --locales or --all-locales, they are mutual exclusive",
            fg="red",
        )
        return

    if all_packages:
        packages = [
            name for name, _ in find_all_packages_with_translations(prefix=prefix)
        ]

    if all_locales:
        secho("Error: --all-locales not implemented yet, use --locale", fg="red")
        return

    if not locales:
        secho("Error: Provide --locale to specify languages", fg="red")
        return

    try:
        package_translations = collect_translations(packages, locales)
        write_translations_to_json(
            package_translations, output_file, locales, write_package_wise_too
        )
        secho(f"Collected translations for {len(packages)} package(s).", fg="green")
    except (OSError, IOError, FileNotFoundError, PermissionError, ValueError) as error:
        secho(f"Error: {error}")


@i18n.command("validate-translations")
@option(
    "--packages",
    "-p",
    multiple=True,
    callback=convert_to_list,
    help="Packages to validate. Can be specified multiple times.",
)
@option(
    "--all-packages",
    "--global",
    is_flag=True,
    help="Validate all invenio_* packages",
)
@option(
    "--languages",
    "-l",
    "locales",
    multiple=True,
    callback=convert_to_list,
    help="Languages to validate (e.g., 'de', 'sv'). Can be specified multiple times. If not provided, validates all languages.",
)
@option(
    "--output-directory",
    "-o",
    type=ClickPath(
        exists=False, file_okay=False, dir_okay=True, writable=True, path_type=Path
    ),
    default=None,
    help="Directory for validation report. Default: ./i18n-collected",
)
def cmd_validate_translations(
    packages: Optional[list[str]],
    all_packages: bool,
    locales: Optional[list[str]],
    output_directory: Optional[Path],
):
    """Validate translation quality.

    Checks PO files for missing, fuzzy, and obsolete translations.
    Generates a validation report in the output directory (default: ./i18n-collected/validation-report.json).

    Examples:
        invenio i18n validate-translations -p invenio-app-rdm -p invenio-rdm-records
        invenio i18n validate-translations --all-packages
        invenio i18n validate-translations --all-packages -l de -l sv
        invenio i18n validate-translations --all-packages -o ./my-reports
    """
    if all_packages:
        if packages:
            secho("Warning: --all-packages ignores --packages", fg="yellow")
        packages = [
            name for name, _ in find_all_packages_with_translations(prefix="invenio_")
        ]
    elif not packages:
        secho("Error: Provide --packages or --all-packages")
        return

    output_dir = output_directory or Path.cwd() / "i18n-collected"
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = validate_translations(packages, locales)
    write_validation_report(summary, output_dir)
    report_path = output_dir / "validation-report.json"
    secho(f"Validation report written: {report_path}", fg="green")

    secho(
        f"Summary: packages={summary.total_packages}, "
        f"locales={summary.total_locales}, "
        f"issues={summary.total_issues}",
    )


@i18n.command("update-translation")
@option("--package", "-p", help="Package name like 'invenio-app-rdm'")
@option("--bundle", "-b", help="Bundle name like 'invenio-translations-de'")
@option("--locale", "-l", required=True, help="Language code like 'de' or 'fr'")
@option(
    "--msgid",
    required=True,
    help="Original English text (or prefix if --prefix is used)",
)
@option("--msgstr", required=True, help="New translation")
@option("--prefix", is_flag=True, help="Match msgid by prefix instead of exact match")
def update_translation(package, bundle, locale, msgid, msgstr, prefix):
    """Update translation in PO file(s)."""
    if not package and not bundle:
        secho("Error: Provide --package or --bundle", fg="red")
        return
    if package and bundle:
        secho("Error: Cannot specify both --package and --bundle", fg="red")
        return

    if package:
        package_root = find_package_path(package)
        if not package_root:
            secho(f"Package {package} not found", fg="red")
            return
        po_path = next(
            (
                path
                for loc, path in find_po_files(package_root, package)
                if loc == locale
            ),
            None,
        )
        if not po_path:
            secho(f"No PO file for {package} in {locale}", fg="red")
            return
        updated, created_new, count, error = update_po_file(
            po_path, msgid, msgstr, prefix
        )
        if error:
            secho(f"Error: {error}")
            return
        if updated:
            target_name = f"{package}/{locale}"
            if prefix:
                secho(
                    f"Updated {count} translation(s) matching '{msgid}' in {target_name}",
                    fg="green",
                )
            elif created_new:
                secho(f"Created '{msgid}' in {target_name}", fg="green")
            else:
                secho(f"Updated '{msgid}' in {target_name}", fg="green")

    elif bundle:
        bundle_root = find_bundle_path(bundle)
        if not bundle_root:
            secho(f"Bundle {bundle} not found")
            return
        po_path = find_bundle_po_file(bundle_root, locale)
        if not po_path:
            secho(f"No PO file for {bundle} in {locale}")
            return

        instance_po_path = (
            Path(current_app.root_path)
            / "translations"
            / locale
            / "LC_MESSAGES"
            / "messages.po"
        )
        if instance_po_path.exists():
            try:
                instance_po_file = polib.pofile(str(instance_po_path))
                entry = (
                    next(
                        (e for e in instance_po_file if e.msgid.startswith(msgid)), None
                    )
                    if prefix
                    else instance_po_file.find(msgid)
                )
                if entry:
                    secho(
                        f"Warning: Instance translation '{entry.msgstr}' will override bundle",
                    )
            except (OSError, IOError, FileNotFoundError, ValueError) as e:
                secho(f"  Warning: Could not check instance PO file: {e}")

        updated, created_new, count, error = update_po_file(
            po_path, msgid, msgstr, prefix
        )
        if error:
            secho(f"Error: {error}")
            return
        if updated:
            target_name = f"{bundle}/{locale}"
            if prefix:
                secho(
                    f"Updated {count} translation(s) matching '{msgid}' in {target_name}",
                    fg="green",
                )
            elif created_new:
                secho(f"Created '{msgid}' in {target_name}", fg="green")
            else:
                secho(f"Updated '{msgid}' in {target_name}", fg="green")


@js_translation.command("build")
@option(
    "--packages",
    "-p",
    multiple=True,
    callback=convert_to_list,
    help="Packages to build. Can be specified multiple times.",
)
@option(
    "--all-packages",
    "--global",
    is_flag=True,
    help="Build JavaScript translations for all invenio_* packages",
)
@option(
    "--output-directory",
    "-o",
    type=ClickPath(
        exists=False, file_okay=False, dir_okay=True, writable=True, path_type=Path
    ),
    default=Path.cwd() / "js-translations",
    help="Directory for temporary JSON files. Default: ./js-translations",
)
def build_js_translations(
    packages: Optional[list[str]],
    all_packages: bool,
    output_directory: Path,
):
    """Build JavaScript translations: convert PO to JSON, merge, and distribute.

    Collects JavaScript PO files from packages, converts to JSON, merges with
    bundles and instance overrides, then distributes to package asset directories.

    Priority order: instance > bundle > package:

    Important: Do NOT edit generated JSON files directly - they will be overwritten.

    Examples:
        invenio i18n js-translation build -p invenio-app-rdm
        invenio i18n js-translation build --all-packages
    """
    if all_packages:
        if packages:
            secho("Warning: --all-packages ignores --packages", fg="yellow")
        packages = [
            name
            for name, package_root in find_all_packages_with_translations(
                prefix="invenio_"
            )
            if any(find_js_po_files(package_root, name))
        ]
    elif not packages:
        secho("Error: Provide --packages or --all-packages")
        return

    if not packages:
        secho("No packages found with JavaScript translations")
        return

    existing_files = list(output_directory.glob("*.json"))
    if existing_files:
        secho(
            f"Warning: Output directory '{output_directory}' already contains {len(existing_files)} JSON file(s)."
        )
        secho(
            "  These files will be OVERWRITTEN. If you have custom edits, copy them to a new directory first."
        )
        secho(
            "  Workflow: 1) Generate → 2) Copy to new directory → 3) Edit → 4) js-translation distribute -i <new-dir>"
        )

    secho(
        f"Collecting JavaScript translations from {len(packages)} package(s)...",
        fg="blue",
    )
    translations_by_language, translation_sources = collect_js_package_translations(
        packages, echo=secho
    )

    secho("Merging translation bundle translations...", fg="blue")
    merge_bundle_js_layers(translations_by_language, translation_sources, echo=secho)

    secho("Merging instance-level translations...", fg="blue")
    merge_instance_js_layers(
        Path(current_app.root_path),
        translations_by_language,
        translation_sources,
        echo=secho,
    )

    if not translations_by_language:
        secho("No JavaScript translations found", fg="yellow")
        return

    secho(f"Total locales collected: {len(translations_by_language)}", fg="green")

    write_js_translation_outputs(
        translations_by_language, translation_sources, output_directory, echo=secho
    )

    secho("Distributing translations to package assets...", fg="blue")
    try:
        results = distribute_js_translations_from_directory(output_directory)
        for package_name, language, target_file, skipped in results:
            if skipped:
                secho(
                    f"Package {package_name} doesn't have webpack entrypoint. Skipping..."
                )
            else:
                secho(
                    f"{package_name} translations for language {language} have been written."
                )
    except (OSError, IOError, FileNotFoundError, PermissionError) as e:
        secho(f"Error during distribution: {e}")
        return

    secho("JavaScript translation build complete!", fg="green", bold=True)


@js_translation.command("distribute")
@option(
    "-i",
    "--input-directory",
    required=True,
    type=ClickPath(
        exists=True, file_okay=False, dir_okay=True, writable=False, path_type=Path
    ),
    help="Input directory for translations in JSON format.",
)
def distribute_js_translations(input_directory: Path):
    """Distribute JavaScript translations from JSON files to installed packages.

    Reads JSON files one per locale, e.g., de.json, en.json from input directory
    and distributes them to package asset directories via webpack entrypoints.

    Input format: Each JSON file contains {package_name: {key: value}}.
    Example: {"invenio_app_rdm": {"Save": "Speichern"}}

    Examples:
        invenio i18n js-translation distribute -i ./js-translations
        invenio i18n js-translation distribute -i ./my-custom-translations
    """
    try:
        results = distribute_js_translations_from_directory(input_directory)
        for package_name, language, target_file, skipped in results:
            if skipped:
                secho(
                    f"Package {package_name} doesn't have webpack entrypoint. Skipping..."
                )
            else:
                secho(
                    f"{package_name} translations for language {language} have been written."
                )
    except (OSError, IOError, FileNotFoundError, PermissionError) as e:
        secho(f"Error during distribution: {e}")
        raise


@js_translation.command("update")
@option("--package", "-p", required=True, help="Package name like 'invenio-app-rdm'")
@option("--locale", "-l", required=True, help="Language code like 'de' or 'fr'")
@option(
    "--msgid",
    required=True,
    help="Original English text (or prefix if --prefix is used)",
)
@option("--msgstr", required=True, help="New translation")
@option("--prefix", is_flag=True, help="Match msgid by prefix instead of exact match")
def update_js_translation(package, locale, msgid, msgstr, prefix):
    """Update JavaScript translation in messages.po file and convert to translations.json.

    Updates a translation in a package's JavaScript PO file and automatically
    converts it to JSON format for webpack.

    Usage:
        # Update a German translation for invenio-app-rdm
        invenio i18n js-translation update -p invenio-app-rdm -l de --msgid "Save" --msgstr "Speichern"

        # Update multiple translations matching a prefix
        invenio i18n js-translation update -p invenio-app-rdm -l de --msgid "Upload" --msgstr "Hochladen" --prefix
    """
    package_root = find_package_path(package)
    if not package_root:
        secho(f"Package {package} not found")
        return

    po_path = next(
        (
            path
            for loc, path in find_js_po_files(package_root, package)
            if loc == locale
        ),
        None,
    )
    if not po_path:
        secho(f"No JavaScript PO file for {package} in {locale}")
        secho(
            "Hint: JavaScript PO files are typically in assets/semantic-ui/translations/<package>/messages/<locale>/messages.po",
        )
        return

    updated, created_new, count, error = update_po_file(po_path, msgid, msgstr, prefix)
    if error:
        secho(f"Error: {error}")
        return
    if not updated:
        return
    target_name = f"{package}/{locale} (JS)"
    if prefix:
        secho(
            f"Updated {count} translation(s) matching '{msgid}' in {target_name}",
            fg="green",
        )
    elif created_new:
        secho(f"Created '{msgid}' in {target_name}", fg="green")
    else:
        secho(f"Updated '{msgid}' in {target_name}", fg="green")
    try:
        po_file = polib.pofile(str(po_path))
        json_data = po_to_i18next_json(po_file, package)

        json_path = po_path.parent / "translations.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)

        with json_path.open("w", encoding="utf-8") as fp:
            dump(json_data, fp, indent=2, ensure_ascii=False)

        secho(f"Converted to JSON: {json_path}")
    except (OSError, IOError, FileNotFoundError, PermissionError, ValueError) as e:
        secho(f"Warning: Failed to convert to JSON: {e}")


@i18n.command("fetch-from-transifex")
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

    try:
        stdout = fetch_translations_from_transifex(
            token, temporary_cache, languages, js_resources
        )
        if stdout:
            secho(stdout, nl=False)
    except RuntimeError as e:
        secho(f"Error fetching from Transifex: {e}")
        return

    collected_translations = {}

    for language in languages.split(","):
        collected_translations[language] = {}

        for package in js_resources.values():
            po_path = Path(temporary_cache) / package / language / "messages.po"
            if not po_path.exists():
                secho(f"Warning: PO file not found: {po_path}")
                continue
            try:
                po_file = polib.pofile(str(po_path))
                collected_translations[language][package] = map_to_i18next_style(
                    po_file
                )
            except (OSError, IOError, FileNotFoundError, ValueError) as e:
                secho(f"Error reading PO file {po_path}: {e}")
                continue

        output_file = Path(f"{output_directory}/{language}.json")
        with output_file.open("w", encoding="utf-8") as fp:
            dump(collected_translations[language], fp, indent=4, ensure_ascii=False)
