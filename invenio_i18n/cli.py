# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2025 TUBITAK ULAKBIM.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CLI for Invenio internationalization module"""
import click
import json
from importlib.metadata import entry_points
from pathlib import Path

from flask.cli import with_appcontext
from flask import current_app


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
    """Distribute JS/React localizations"""

    # TODO: should we keep naming "translation" or change to "localization"?

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
            # TODO: maybe we should add confirmation or info message for missing languages before create their directories?
            # TODO: set parents=False if base_path / domain / "messages" part is mandatory. Custom 3rd party packages might not have this, idk.
            target_translations_path.mkdir(parents=True, exist_ok=True)

            with (target_translations_path / "translations.json").open(
                "w"
            ) as target_file:
                json.dump(translations, target_file, indent=2, ensure_ascii=False)

            click.secho(
                f"{package_name} localizations for language {language} have been written.",
                fg="green",
            )
