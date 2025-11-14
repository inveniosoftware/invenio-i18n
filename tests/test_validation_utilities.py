# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test cases for the validation workflow."""

import os
import tempfile
from pathlib import Path

import polib
import pytest
from click.testing import CliRunner

from invenio_i18n.cli import i18n
from invenio_i18n.translation_utilities.validate import validate_po


def test_validation_workflow_example():
    """Test the complete validation workflow with real example."""
    runner = CliRunner()

    result = runner.invoke(i18n, ["validate-translations", "-p", "invenio-i18n"])
    output_dir = Path.cwd() / "i18n-collected"
    report_path = output_dir / "validation-report.json"

    if report_path.exists():
        import json

        with open(report_path) as f:
            report = json.load(f)

        fuzzy_count = report.get("summary", {}).get("fuzzyTranslations", 0)

        if fuzzy_count > 0:
            update_result = runner.invoke(
                i18n,
                [
                    "update-translation",
                    "-p",
                    "invenio-i18n",
                    "-l",
                    "de",
                    "--msgid",
                    "New upload",
                    "--msgstr",
                    "Neuer Eintrag",
                ],
            )

            assert update_result.exit_code == 0
            assert (
                "Updated translation for 'New upload' in invenio-i18n/de"
                in update_result.output
            )

            result2 = runner.invoke(
                i18n, ["validate-translations", "-p", "invenio-i18n"]
            )

            with open(report_path) as f:
                report2 = json.load(f)

            fuzzy_count2 = report2.get("summary", {}).get("fuzzyTranslations", 0)

            assert fuzzy_count2 <= fuzzy_count

    else:
        pytest.skip("Validation report not created - invenio-i18n may not be available")


def test_create_global_pot_workflow(app):
    """Test the create-global-pot command workflow."""
    runner = CliRunner()

    with app.app_context():
        result = runner.invoke(i18n, ["create-global-pot", "-p", "invenio-i18n"])

        if "Package invenio-i18n not found" in result.output:
            pytest.skip("invenio-i18n not available in test environment")

        assert result.exit_code == 0
        assert "Collected translations for 1 packages" in result.output

        output_dir = Path.cwd() / "i18n-collected"
        assert output_dir.exists()

        translations_file = output_dir / "translations.json"
        assert translations_file.exists()

        package_file = output_dir / "invenio_i18n" / "translations.json"
        if package_file.exists():
            # If it exists, verify it has content
            import json

            with open(package_file) as f:
                data = json.load(f)
                assert isinstance(data, dict)


def test_validate_detects_fuzzy_when_short_word_changes():
    """Test fuzzy detection for short word changes (German example).

    Scenario: "Save" changed to "Save changes"
    Old translation "Speichern" is marked fuzzy.
    """
    po_file = polib.POFile()
    normal_entry = polib.POEntry(msgid="Upload", msgstr="Hochladen")
    po_file.append(normal_entry)
    fuzzy_entry = polib.POEntry(
        msgid="Save changes",
        msgstr="Speichern",  # Old translation for "Save", not "Save changes"
        flags=["fuzzy"],
    )
    po_file.append(fuzzy_entry)

    report = validate_po(po_file, "test-package", "de", Path("/tmp/test.po"))

    assert report["counts"]["fuzzyTranslations"] == 1
    assert report["counts"]["untranslated"] == 0
    assert "Save changes" in report["issues"]["fuzzyTranslations"]
    assert "Upload" not in report["issues"]["fuzzyTranslations"]


def test_fuzzy_translation_multiple_entries():
    """Test multiple fuzzy entries in German translations."""
    po_file = polib.POFile()

    fuzzy1 = polib.POEntry(
        msgid="New upload",
        msgstr="Neuer Upload",  # Might be wrong after source changed
        flags=["fuzzy"],
    )
    fuzzy2 = polib.POEntry(
        msgid="Delete file",
        msgstr="Löschen",  # Old translation, source changed
        flags=["fuzzy"],
    )
    normal = polib.POEntry(msgid="Cancel", msgstr="Abbrechen")

    po_file.append(fuzzy1)
    po_file.append(fuzzy2)
    po_file.append(normal)

    report = validate_po(po_file, "test-package", "de", Path("/tmp/test.po"))

    assert report["counts"]["fuzzyTranslations"] == 2
    assert report["counts"]["untranslated"] == 0
    assert "New upload" in report["issues"]["fuzzyTranslations"]
    assert "Delete file" in report["issues"]["fuzzyTranslations"]
    assert "Cancel" not in report["issues"]["fuzzyTranslations"]


def test_validate_detects_fuzzy_when_phrase_expands():
    """Test fuzzy detection for longer phrases (German example).

    Scenario: "Welcome" changed to "Welcome to Invenio"
    """
    po_file = polib.POFile()

    fuzzy_entry = polib.POEntry(
        msgid="Welcome to Invenio",
        msgstr="Willkommen",  # Old translation for just "Welcome"
        flags=["fuzzy"],
    )
    po_file.append(fuzzy_entry)

    report = validate_po(po_file, "test-package", "de", Path("/tmp/test.po"))

    assert report["counts"]["fuzzyTranslations"] == 1
    assert "Welcome to Invenio" in report["issues"]["fuzzyTranslations"]


def test_fuzzy_mixed_with_untranslated():
    """Test fuzzy entries mixed with untranslated entries."""
    po_file = polib.POFile()

    fuzzy = polib.POEntry(msgid="Edit record", msgstr="Bearbeiten", flags=["fuzzy"])
    untranslated = polib.POEntry(msgid="Delete record", msgstr="")
    normal = polib.POEntry(msgid="View", msgstr="Anzeigen")

    po_file.append(fuzzy)
    po_file.append(untranslated)
    po_file.append(normal)

    report = validate_po(po_file, "test-package", "de", Path("/tmp/test.po"))

    assert report["counts"]["fuzzyTranslations"] == 1
    assert report["counts"]["untranslated"] == 1
    assert "Edit record" in report["issues"]["fuzzyTranslations"]
    assert "Delete record" in report["issues"]["untranslated"]
    assert "View" not in report["issues"]["fuzzyTranslations"]
    assert "View" not in report["issues"]["untranslated"]


def test_validate_detects_fuzzy_minor_text_change():
    """Test fuzzy detection when source text changes slightly.

    Scenario: "OK" changed to "OK!" or similar small change.
    """
    po_file = polib.POFile()

    fuzzy_entry = polib.POEntry(
        msgid="OK!", msgstr="OK", flags=["fuzzy"]  # Old translation
    )
    po_file.append(fuzzy_entry)

    report = validate_po(po_file, "test-package", "de", Path("/tmp/test.po"))

    assert report["counts"]["fuzzyTranslations"] == 1
    assert "OK!" in report["issues"]["fuzzyTranslations"]


def test_validate_no_issues_when_no_fuzzy_flags():
    """Test that clean translations without fuzzy flags are not reported."""
    po_file = polib.POFile()

    entry1 = polib.POEntry(msgid="Save", msgstr="Speichern")
    entry2 = polib.POEntry(msgid="Cancel", msgstr="Abbrechen")
    entry3 = polib.POEntry(msgid="Delete", msgstr="Löschen")

    po_file.append(entry1)
    po_file.append(entry2)
    po_file.append(entry3)

    report = validate_po(po_file, "test-package", "de", Path("/tmp/test.po"))

    assert report["counts"]["fuzzyTranslations"] == 0
    assert report["counts"]["untranslated"] == 0
    assert len(report["issues"]["fuzzyTranslations"]) == 0


def test_fuzzy_german_common_words():
    """Test fuzzy detection with common German UI words."""
    po_file = polib.POFile()

    fuzzy_words = [
        ("Save", "Speichern", "Save changes", "Speichern"),
        ("Close", "Schließen", "Close window", "Schließen"),
        ("Open", "Öffnen", "Open file", "Öffnen"),
    ]

    for old_msgid, translation, new_msgid, old_translation in fuzzy_words:
        fuzzy_entry = polib.POEntry(
            msgid=new_msgid,
            msgstr=old_translation,  # Old translation for old_msgid
            flags=["fuzzy"],
        )
        po_file.append(fuzzy_entry)

    report = validate_po(po_file, "test-package", "de", Path("/tmp/test.po"))

    assert report["counts"]["fuzzyTranslations"] == 3
    assert "Save changes" in report["issues"]["fuzzyTranslations"]
    assert "Close window" in report["issues"]["fuzzyTranslations"]
    assert "Open file" in report["issues"]["fuzzyTranslations"]
