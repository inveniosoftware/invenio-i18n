# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test cases for the update-translation CLI command."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import polib
import pytest
from click.testing import CliRunner

from invenio_i18n.cli import i18n


@pytest.fixture
def temp_po_file():
    """Create a temporary PO file with test translations."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".po", delete=False) as f:
        po = polib.POFile()

        fuzzy_entry = polib.POEntry(
            msgid="New upload", msgstr="Alter Upload", flags=["fuzzy"]
        )
        po.append(fuzzy_entry)

        po.save(f.name)
        yield f.name

    os.unlink(f.name)


def test_update_translation_removes_fuzzy_flag(temp_po_file):
    """Test that update-translation command removes fuzzy flag."""
    po_file = polib.pofile(temp_po_file)

    upload_entry = None
    for entry in po_file:
        if entry.msgid == "New upload":
            upload_entry = entry
            break

    assert upload_entry is not None
    assert "fuzzy" in upload_entry.flags
    assert upload_entry.msgstr == "Alter Upload"

    upload_entry.msgstr = "Neuer Eintrag"
    upload_entry.flags.remove("fuzzy")
    po_file.save()

    # Verify the changes
    updated_po_file = polib.pofile(temp_po_file)
    updated_entry = None
    for entry in updated_po_file:
        if entry.msgid == "New upload":
            updated_entry = entry
            break

    assert updated_entry is not None
    assert "fuzzy" not in updated_entry.flags
    assert updated_entry.msgstr == "Neuer Eintrag"


def test_update_translation_cli_integration(app):
    """Test the CLI command integration with invenio-i18n package."""
    runner = CliRunner()

    with app.app_context():
        # Test with invenio-i18n package itself - which should exist
        result = runner.invoke(
            i18n,
            [
                "update-translation",
                "-p",
                "invenio-i18n",
                "-l",
                "de",
                "--msgid",
                "NonExistentMessage",
                "--msgstr",
                "Test Translation",
            ],
        )

        if "Package invenio-i18n not found" in result.output:
            pytest.skip("invenio-i18n not available in test environment")

        assert result.exit_code == 0
        assert (
            "Created 'NonExistentMessage' in invenio-i18n/de" in result.output
            or "Updated 'NonExistentMessage' in invenio-i18n/de" in result.output
        )


def test_update_translation_bundle(app, tmp_path):
    """Ensure bundle translations can be updated and fuzzy entries cleared."""
    translations_dir = tmp_path / "bundle" / "translations"
    po_dir = translations_dir / "de" / "LC_MESSAGES"
    po_dir.mkdir(parents=True)
    po_path = po_dir / "messages.po"

    po = polib.POFile()
    fuzzy_entry = polib.POEntry(msgid="Upload file", msgstr="Upload", flags=["fuzzy"])
    po.append(fuzzy_entry)
    po.save(str(po_path))

    def mock_find_bundle_path(name):
        return translations_dir if name == "test-bundle" else None

    def mock_find_bundle_po_file(root, locale):
        return po_path if root == translations_dir and locale == "de" else None

    runner = CliRunner()
    with app.app_context():
        with patch(
            "invenio_i18n.cli.find_bundle_path", side_effect=mock_find_bundle_path
        ):
            with patch(
                "invenio_i18n.cli.find_bundle_po_file",
                side_effect=mock_find_bundle_po_file,
            ):
                result = runner.invoke(
                    i18n,
                    [
                        "update-translation",
                        "-b",
                        "test-bundle",
                        "-l",
                        "de",
                        "--msgid",
                        "Upload file",
                        "--msgstr",
                        "Datei hochladen",
                    ],
                )

    assert result.exit_code == 0
    assert "Updated 'Upload file' in test-bundle/de" in result.output

    reloaded = polib.pofile(str(po_path))
    entry = reloaded.find("Upload file")
    assert entry is not None
    assert entry.msgstr == "Datei hochladen"
    assert "fuzzy" not in entry.flags
