# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2025 TUBITAK ULAKBIM.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CLI for Invenio internationalization module"""
import json
import subprocess
from importlib.metadata import entry_points
from pathlib import Path

import click
import polib
from flask import current_app
from flask.cli import with_appcontext
from jinja2 import BaseLoader, Environment


@click.group(chain=True)
@with_appcontext
def i18n():
    """i18n commands."""


@i18n.command()
@with_appcontext
@click.option(
    "-i",
    "--input-directory",
    required=True,
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=False, path_type=Path
    ),
    help="Input directory containing translations in JSON format.",
)
@click.option(
    "--entrypoint-group",
    default="invenio_assets.webpack",
    help="Entrypoint group used to get package assets paths. Default: \"invenio_assets.webpack\" You don't need to set this option under normal circumstances.'",
)
def distribute_js_translations(input_directory: Path, entrypoint_group: str):
    """Distribute JS/React translation files"""

    exceptional_package_name_mapper = current_app.config[
        "I18N_JS_DISTR_EXCEPTIONAL_PACKAGE_MAP"
    ]
    bundle_entrypoints = [ep for ep in entry_points(group=entrypoint_group)]

    # Map package names to their translation file base paths for packages with a webpack entrypoint.
    package_translations_base_paths = {
        exceptional_package_name_mapper.get(
            bundle_entrypoint.name, bundle_entrypoint.name
        ): Path(bundle_entrypoint.load().path)
           / "translations"
        for bundle_entrypoint in bundle_entrypoints
        if bundle_entrypoint.load().path
    }

    # Map source translation file paths to their languages
    source_translation_files = {
        path.stem: path
        for path in input_directory.iterdir()
        if path.is_file() and path.suffix == ".json"
    }

    # Read unified source translation files and distribute translations to relevant packages
    for language, source_file_path in source_translation_files.items():
        with source_file_path.open("r") as source_file:
            unified_translations = json.load(source_file)

        for package_name, translations in unified_translations.items():
            base_path = package_translations_base_paths.get(
                package_name,
            )
            if not base_path:
                click.secho(
                    f"Package {package_name} doesn't have webpack entrypoint. Skipping...",
                    fg="yellow",
                    italic=True,
                )
                continue

            target_translations_path = base_path / package_name / "messages" / language

            if not target_translations_path.exists():
                click.secho(
                    f"Translations directory for {package_name} in language {language} not found. Creating...",
                    fg="yellow",
                )
                target_translations_path.mkdir(parents=True)

            with (target_translations_path / "translations.json").open(
                    "w"
            ) as target_file:
                json.dump(translations, target_file, indent=2, ensure_ascii=False)

            click.secho(
                f"{package_name} translations for language {language} have been written.",
                fg="green",
            )


@i18n.command()
@click.option(
    "--token", "-t", required=True, help="API token for your Transifex account."
)
@click.option(
    "--languages",
    "-l",
    required=True,
    help="Languages you want to download translations for (one or multiple comma separated values).",
)
@click.option(
    "--output-directory",
    "-o",
    required=True,
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, path_type=Path
    ),
    help="Directory to which collected translations in JSON format should be written.",
)
def download_transifex(token, languages, output_directory):
    """Compile message catalog."""
    js_resources = current_app.config["I18N_TRANSIFEX_JS_RESOURCES_MAP"]

    downloads_path = output_directory / "download_transifex"
    downloads_path.mkdir(parents=True, exist_ok=True)

    with open(downloads_path / "collected_config", "w") as f:
        # TODO Transifex downloads to path in config, change config if a different file location for *.po files is needed
        config_template = Environment(loader=BaseLoader()).from_string("""
[main]
host = https://www.transifex.com

[o:inveniosoftware:p:invenio:r:{{- resource }}]
file_filter = {{- downloads_path }}/{{- module }}/<lang>/messages.po
source_file = {{- module }}/assets/semantic-ui/translations/{{- module }}/translations.pot
source_lang = en
type = PO
        """)

        for resource, module in js_resources.items():
            f.write(
                config_template.render(
                    downloads_path=downloads_path, resource=resource, module=module
                )
            )
            f.write("\n\n")

    transifex_pull_cmd = [
        "tx",
        f"--token={token}",
        f"--config={downloads_path}/collected_config",
        "pull",
        f"--languages={languages}",
        "--force",
    ]
    subprocess.run(transifex_pull_cmd)

    collected_translations = {}

    languages_array = languages.split(",")
    for language in languages_array:
        collected_translations[language] = {}

        for resource, module in js_resources.items():
            po_path = f"{downloads_path}/{module}/{language}/messages.po"

            pofile = polib.pofile(po_path)
            collected_translations[language][module] = {}

            for entry in pofile:
                collected_translations[language][module][entry.msgid] = entry.msgstr
                if entry.msgstr_plural:
                    collected_translations[language][module][entry.msgid] = (
                        entry.msgstr_plural[0]
                    )
                    collected_translations[language][module][
                        entry.msgid + "_plural"
                        ] = entry.msgstr_plural[1]

        with open(
                f"{output_directory}/{language}.json",
                "w",
                encoding="utf-8",
        ) as f:
            json.dump(collected_translations[language], f, indent=4, ensure_ascii=False)
