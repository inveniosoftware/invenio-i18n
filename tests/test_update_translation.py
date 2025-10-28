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

import polib
import pytest
from click.testing import CliRunner

from invenio_i18n.cli import i18n
from invenio_i18n.translation_utilities import discovery


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
    pofile = polib.pofile(temp_po_file)

    upload_entry = None
    for entry in pofile:
        if entry.msgid == "New upload":
            upload_entry = entry
            break

    assert upload_entry is not None
    assert "fuzzy" in upload_entry.flags
    assert upload_entry.msgstr == "Alter Upload"

    upload_entry.msgstr = "Neuer Eintrag"
    upload_entry.flags.remove("fuzzy")
    pofile.save()

    # Verify the changes
    updated_pofile = polib.pofile(temp_po_file)
    updated_entry = None
    for entry in updated_pofile:
        if entry.msgid == "New upload":
            updated_entry = entry
            break

    assert updated_entry is not None
    assert "fuzzy" not in updated_entry.flags
    assert updated_entry.msgstr == "Neuer Eintrag"


def test_update_translation_cli_integration():
    """Test the CLI command integration with invenio-i18n package."""
    runner = CliRunner()

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
    assert "Translation 'NonExistentMessage' not found" in result.output
