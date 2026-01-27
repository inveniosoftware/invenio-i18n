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

"""I18N utils."""

from json import JSONDecodeError, dump, load
from pathlib import Path
from subprocess import run
from typing import Callable, Dict, List, Optional, Tuple

import polib
from flask import current_app
from invenio_base.utils import entry_points
from jinja2 import BaseLoader, Environment
from polib import POEntry, pofile

from .translation_utilities.convert import po_to_i18next_json
from .translation_utilities.discovery import (
    find_all_bundles,
    find_js_po_files,
    find_package_path,
    package_name_to_module_name,
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

Echo = Optional[Callable[[str], None]]

LocaleMessages = Dict[str, str]  # msgid -> msgstr
PackageTranslations = Dict[str, LocaleMessages]  # package -> messages
TranslationsByLang = Dict[str, PackageTranslations]  # lang -> package -> messages
SourceList = List[str]
PackageSources = Dict[str, Dict[str, SourceList]]  # package -> msgid -> sources
TranslationSources = Dict[str, PackageSources]  # lang -> package -> sources


def _echo(message: str, echo: Echo, **kwargs) -> None:
    """Call the provided echo callback if it exists."""
    if echo:
        echo(message, **kwargs)


def convert_to_list(_, __, value):
    """Turn Click's multiple=True tuple into a plain list."""
    if value is None:
        return []
    return list(value)


def ensure_parent_directory(_, __, value):
    """Make sure the parent directory exists for a Click Path option."""
    if value:
        value.parent.mkdir(parents=True, exist_ok=True)
    return value


def source_translation_files(input_directory):
    """Yield language, translations for each JSON file in a directory."""
    for source_file in input_directory.iterdir():
        if not source_file.is_file() or source_file.suffix != ".json":
            continue

        language = source_file.stem

        with source_file.open("r") as file_handle:
            try:
                obj = load(file_handle)
            except JSONDecodeError:
                # Skip invalid JSON files - command can handle logging if needed
                continue
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
    """Fetch translations from transifex.

    :raises RuntimeError: If Transifex pull fails
    """
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
    result = run(transifex_pull_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Transifex pull failed with return code {result.returncode}: {result.stderr}"
        )


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


def distribute_js_translations_from_directory(
    input_directory: Path, entrypoint_group: str = "invenio_assets.webpack"
):
    """Distribute JavaScript translations from JSON files to installed packages.

    This is a helper function which reads unified JSON files per language e.g., de.json, en.json,
    from a translation bundle directory and distributes them to package asset directories.

    :param input_directory: containing JSON files - translation bundle
    :param entrypoint_group: Entrypoint group for discovering package paths
    :return: List of tuples (package_name, language, target_file, skipped) for each distribution
    :raises RuntimeError: If distribution fails
    """
    exceptional_package_names = current_app.config.get(
        "I18N_JS_DISTR_EXCEPTIONAL_PACKAGE_MAP", {}
    )

    results = []
    for language, unified_translations in source_translation_files(input_directory):
        target_packages = calculate_target_packages(
            exceptional_package_names, entrypoint_group, language
        )

        for package_name, translations in unified_translations.items():
            # Skip metadata keys (they start with _)
            if package_name.startswith("_"):
                continue
            if package_name not in target_packages:
                results.append((package_name, language, None, True))
                continue

            target_file = target_packages[package_name]
            target_file.parent.mkdir(parents=True, exist_ok=True)

            with target_file.open("w", encoding="utf-8") as file_pointer:
                dump(translations, file_pointer, indent=2, ensure_ascii=False)

            results.append((package_name, language, target_file, False))

    return results


def collect_js_package_translations(
    packages: list[str],
    *,
    echo: Echo = None,
) -> tuple[TranslationsByLang, TranslationSources]:
    """Read JS PO files per package and return translations with sources."""
    translations_by_language: TranslationsByLang = {}
    translation_sources: TranslationSources = {}

    for package_name in packages:
        package_root = find_package_path(package_name)
        if not package_root:
            _echo(f"  Skipping: package {package_name} not found", echo, fg="yellow")
            continue

        for locale, po_path in find_js_po_files(package_root, package_name):
            _add_package_locale_translations(
                package_name,
                locale,
                po_path,
                translations_by_language,
                translation_sources,
                echo,
            )

    return translations_by_language, translation_sources


def _add_package_locale_translations(
    package_name: str,
    locale: str,
    po_path: Path,
    translations_by_language: TranslationsByLang,
    translation_sources: TranslationSources,
    echo: Echo,
) -> None:
    """Load one package/locale PO file and record translations + sources."""
    translations_by_language.setdefault(locale, {})
    translation_sources.setdefault(locale, {})

    try:
        po_file = polib.pofile(str(po_path))
        module_name = package_name_to_module_name(package_name)
        package_translations = po_to_i18next_json(po_file, package_name)

        if module_name not in translation_sources[locale]:
            translation_sources[locale][module_name] = {}

        is_first_processing = module_name not in translations_by_language[locale]
        translations_by_language[locale][module_name] = package_translations

        if is_first_processing:
            for key in package_translations.keys():
                translation_sources[locale][module_name].setdefault(key, [])
                translation_sources[locale][module_name][key].append("package")

        _echo(f"  Collected {locale} from {package_name}", echo, fg="cyan")
    except (OSError, IOError, FileNotFoundError, ValueError) as err:
        _echo(f"  Error reading {po_path}: {err}", echo, fg="red")


def merge_js_translations(
    target: PackageTranslations,
    source: PackageTranslations,
    sources_metadata: Optional[PackageSources] = None,
    source_type: str = "unknown",
) -> None:
    """Merge source into target; source wins. Track sources if provided."""
    for package_name, package_translations in source.items():
        if package_name not in target:
            target[package_name] = {}

        if sources_metadata is not None:
            if package_name not in sources_metadata:
                sources_metadata[package_name] = {}
            for key, value in package_translations.items():
                if key not in sources_metadata[package_name]:
                    sources_metadata[package_name][key] = []

                if source_type not in sources_metadata[package_name][key]:
                    sources_metadata[package_name][key].append(source_type)

                if key in target[package_name] and target[package_name][key] == value:
                    continue
                target[package_name][key] = value
        else:
            target[package_name].update(package_translations)


def collect_bundle_js_translations(*, echo: Echo = None) -> TranslationsByLang:
    """Load bundle JSON translations per locale from translation bundles."""
    translations_by_language: TranslationsByLang = {}

    for bundle_name, bundle_root in find_all_bundles():
        for json_file in bundle_root.glob("*.json"):
            locale = json_file.stem
            bundle_translations = _load_locale_json(
                json_file, echo, f"bundle {locale} from {bundle_name}"
            )
            if not isinstance(bundle_translations, dict):
                continue
            translations_by_language.setdefault(locale, {})
            merge_js_translations(translations_by_language[locale], bundle_translations)

    return translations_by_language


def collect_instance_js_translations(
    app_root_path: Path,
    *,
    echo: Echo = None,
) -> TranslationsByLang:
    """Load instance-level JS translations from app.root_path/translations."""
    translations_by_language: TranslationsByLang = {}
    instance_translations_dir = app_root_path / "translations"

    if not instance_translations_dir.exists():
        return translations_by_language

    for json_file in instance_translations_dir.glob("*.json"):
        locale = json_file.stem
        translations = _load_locale_json(
            json_file, echo, f"instance-level {locale} from {json_file}"
        )
        if isinstance(translations, dict):
            translations_by_language[locale] = translations

    return translations_by_language


def merge_bundle_js_layers(
    translations_by_language: TranslationsByLang,
    translation_sources: TranslationSources,
    *,
    echo: Echo = None,
) -> None:
    """Merge bundle translations into collected package translations."""
    bundle_translations = collect_bundle_js_translations(echo=echo)
    if bundle_translations:
        _echo(
            f"  Found {len(bundle_translations)} locale(s) in bundles", echo, fg="cyan"
        )
    for locale, bundle_data in bundle_translations.items():
        translations_by_language.setdefault(locale, {})
        translation_sources.setdefault(locale, {})
        merge_js_translations(
            translations_by_language[locale],
            bundle_data,
            translation_sources[locale],
            "bundle",
        )
        if bundle_data:
            _echo(f"  Merged bundle translations for {locale}", echo, fg="cyan")


def merge_instance_js_layers(
    app_root_path: Path,
    translations_by_language: TranslationsByLang,
    translation_sources: TranslationSources,
    *,
    echo: Echo = None,
) -> None:
    """Merge instance translations into collected package translations."""
    instance_translations = collect_instance_js_translations(app_root_path, echo=echo)
    if instance_translations:
        _echo(
            f"  Found {len(instance_translations)} locale(s) in instance",
            echo,
            fg="cyan",
        )
    for locale, instance_data in instance_translations.items():
        translations_by_language.setdefault(locale, {})
        translation_sources.setdefault(locale, {})
        merge_js_translations(
            translations_by_language[locale],
            instance_data,
            translation_sources[locale],
            "instance",
        )
        if instance_data:
            _echo(f"  Merged instance translations for {locale}", echo, fg="cyan")


def write_js_translation_outputs(
    translations_by_language: TranslationsByLang,
    translation_sources: TranslationSources,
    output_directory: Path,
    *,
    echo: Echo = None,
) -> list[Path]:
    """Write merged JS translations (and metadata) to the output directory."""
    output_directory.mkdir(parents=True, exist_ok=True)
    written_files: list[Path] = []

    for locale, translations in translations_by_language.items():
        json_path = output_directory / f"{locale}.json"
        output_data = _add_metadata_block(
            locale, translations, translation_sources, echo=echo
        )

        with json_path.open("w", encoding="utf-8") as fp:
            dump(output_data, fp, indent=2, ensure_ascii=False)
        written_files.append(json_path)
        _echo(f"Wrote {json_path}", echo, fg="green")

    return written_files


def _load_locale_json(json_file: Path, echo: Echo, context: str) -> Optional[dict]:
    """Read a locale JSON file; warn and skip on errors."""
    try:
        with json_file.open("r", encoding="utf-8") as fp:
            data = load(fp)
            if isinstance(data, dict):
                return data
    except (
        JSONDecodeError,
        OSError,
        IOError,
        FileNotFoundError,
        PermissionError,
    ) as err:
        _echo(f"  Warning: Could not read {context}: {err}", echo, fg="yellow")
    return None


def _add_metadata_block(
    locale: str,
    translations: PackageTranslations,
    translation_sources: TranslationSources,
    *,
    echo: Echo,
) -> dict[str, dict[str, str]]:
    """Attach translation source metadata for a locale, if present."""
    output_data = translations.copy()

    if locale in translation_sources and translation_sources[locale]:
        output_data["_translation_sources"] = {
            "_description": (
                "Translation source tracking metadata. "
                "Structure: {package_name: {translation_key: [source_types]}}. "
                "Source types: 'package' = from package PO files, "
                "'bundle' = from translation bundle JSON, "
                "'instance' = from instance-level JSON overrides. "
                "Keys with multiple sources indicate overrides/conflicts."
            ),
            **translation_sources[locale],
        }
        total_keys = sum(len(keys) for keys in translation_sources[locale].values())
        _echo(
            f"  Added metadata for {len(translation_sources[locale])} package(s), {total_keys} translation key(s)",
            echo,
            fg="cyan",
        )

    return output_data


def has_translation_key(po_path: Path, msgid: str, match_prefix: bool) -> bool:
    """Check if PO file contains the translation key."""
    try:
        po_file = pofile(str(po_path))
        if match_prefix:
            return any(entry.msgid.startswith(msgid) for entry in po_file)
        return po_file.find(msgid) is not None
    except (OSError, IOError, FileNotFoundError, ValueError):
        return False


def update_po_file(
    po_path: Path,
    msgid: str,
    msgstr: str,
    match_prefix: bool = False,
) -> Tuple[bool, bool, int, Optional[str]]:
    """Update PO file with translation.

    :param po_path: Path to PO file
    :param msgid: Message ID to update
    :param msgstr: New translation string
    :param match_prefix: If True, match msgid by prefix
    :return: Tuple of updated, created_new, count, error_message
        - updated: whether any update was made
        - created_new: whether a new entry was created
        - count: number of entries updated
        - error_message: error message if operation failed, None otherwise
    """
    try:
        po_file = pofile(str(po_path))
    except (OSError, IOError, FileNotFoundError, ValueError) as e:
        return False, False, 0, f"Error opening {po_path}: {e}"

    updated = False
    created_new = False
    count = 0

    def remove_fuzzy_flag(entry):
        if isinstance(entry.flags, list):
            if "fuzzy" in entry.flags:
                entry.flags.remove("fuzzy")
        else:
            entry.flags.discard("fuzzy")

    for entry in po_file:
        if (match_prefix and entry.msgid.startswith(msgid)) or entry.msgid == msgid:
            entry.msgstr = msgstr
            remove_fuzzy_flag(entry)
            updated = True
            count += 1
            if not match_prefix:
                break

    if not updated or match_prefix:
        for entry in list(po_file.obsolete_entries()):
            if (match_prefix and entry.msgid.startswith(msgid)) or entry.msgid == msgid:
                entry.msgstr = msgstr
                remove_fuzzy_flag(entry)
                entry.obsolete = False
                po_file.append(entry)
                updated = True
                count += 1
                if not match_prefix:
                    break

    if not updated and not match_prefix:
        po_file.append(POEntry(msgid=msgid, msgstr=msgstr))
        updated = True
        created_new = True

    if not updated:
        return False, False, 0, None

    try:
        po_file.save()
    except (OSError, IOError, PermissionError) as e:
        return False, False, 0, f"Error saving {po_path}: {e}"

    is_js_po = (
        "assets" in str(po_path)
        or "messages.po" in str(po_path)
        and "LC_MESSAGES" not in str(po_path)
    )
    compile_error = None
    if not is_js_po:
        translations_dir = po_path.parent.parent.parent
        result = run(
            ["pybabel", "compile", "-d", str(translations_dir)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            compile_error = f"Warning: Failed to compile: {result.stderr}"

    return updated, created_new, count, compile_error
