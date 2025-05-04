# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2025 TUBITAK ULAKBIM.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CLI for Invenio internationalization module"""
import subprocess
from json import JSONDecodeError, dump, load
from pathlib import Path

import polib
from click import Path as ClickPath
from click import group, option, secho
from flask import current_app
from flask.cli import with_appcontext
from importlib_metadata import entry_points
from jinja2 import BaseLoader, Environment

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
    """Map source translation file paths to their languages."""
    for source_file in input_directory.iterdir():
        if not source_file.is_file() or source_file.suffix != ".json":
            msg = f"source file: {source_file} is not meant to be distributed."
            secho(msg, fg="red")
            continue

        language = source_file.stem

        with source_file.open("r") as source_file:
            try:
                obj = load(source_file)
            except JSONDecodeError as error:
                msg = f"source file: {source_file} couldn't be loaded because of error: {str(error)}"
                secho(msg, fg="yellow")
            else:
                yield language, obj


def calculate_target_packages(
    exceptional_package_names,
    entrypoint_group,
    language,
):
    """Calculate target packages."""
    package_translations_base_paths = {}

    for entry_point in entry_points(group=entrypoint_group):
        package_path = entry_point.load().path

        if not package_path:
            msg = f"Package {package_path} doesn't have webpack entrypoint. Skipping..."
            secho(msg, fg="yellow")
            continue

        package_name = exceptional_package_names.get(
            package_path.name, package_path.name
        )
        target_translations_path = (
            package_path / "translations" / package_name / "messages" / language
        )

        if not target_translations_path.exists():
            msg = f"Translations directory for {package_name} in language {language} not found. Creating..."
            secho(msg, fg="yellow")
            target_translations_path.mkdir(parents=True)

        package_translations_base_paths[package_name] = (
            target_translations_path / "translations.json"
        )

    return package_translations_base_paths


def create_transifex_configuration(temporary_cache, js_resources):
    """Create transifex fetch configuration.

    This configuration is build dynamically because the targeted packages are
    customizable over the configuration variable.
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


def map_to_invenio_style(pofile):
    """Map to invenio style.

    For plurals we need a special treatment.
    """
    obj = {}
    for entry in pofile:
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
@with_appcontext
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
    """Distribute JS/React translation files"""

    exceptional_package_names = current_app.config[
        "I18N_JS_DISTR_EXCEPTIONAL_PACKAGE_MAP"
    ]

    # Read unified source translation files and distribute translations to relevant packages
    for language, unified_translations in source_translation_files(input_directory):
        target_packages = calculate_target_packages(
            exceptional_package_names, entrypoint_group, language
        )

        for package_name, translations in unified_translations.items():
            target_file = target_packages[package_name]

            with target_file.open("w") as file_pointer:
                dump(translations, file_pointer, indent=2, ensure_ascii=False)

            msg = f"{package_name} translations for language {language} have been written."
            secho(msg, fg="green")


@i18n.command()
@option("--token", "-t", required=True, help="API token for your Transifex account.")
@option(
    "--languages",
    "-l",
    required=True,
    help="Languages you want to download translations for (one or multiple comma separated values, e.g. 'de,en,fr').",
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
    """Compile message catalog."""
    js_resources = current_app.config["I18N_TRANSIFEX_JS_RESOURCES_MAP"]

    temporary_cache = output_directory / "tmp"

    fetch_translations_from_transifex(token, temporary_cache, languages, js_resources)

    collected_translations = {}

    for language in languages.split(","):
        collected_translations[language] = {}

        for package in js_resources.values():
            po_path = f"{temporary_cache}/{package}/{language}/messages.po"
            pofile = polib.pofile(po_path)

            collected_translations[language][package] = map_to_invenio_style(pofile)

        output_file = (Path(f"{output_directory}/{language}.json"),)
        with output_file.open("w", encoding="utf-8") as fp:
            dump(collected_translations[language], fp, indent=4, ensure_ascii=False)
