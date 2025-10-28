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


def test_create_global_pot_workflow():
    """Test the create-global-pot command workflow."""
    runner = CliRunner()

    result = runner.invoke(i18n, ["create-global-pot", "-p", "invenio-i18n"])

    if "Package invenio-i18n not found" in result.output:
        pytest.skip("invenio-i18n not available in test environment")

    assert result.exit_code == 0
    assert "Collected translations for 1 packages" in result.output

    output_dir = Path.cwd() / "i18n-collected"
    assert output_dir.exists()

    translations_file = output_dir / "translations.json"
    assert translations_file.exists()

    # Check if package-specific file exists (may not exist if package has no translations)
    package_file = output_dir / "invenio_i18n" / "translations.json"
    if package_file.exists():
        # If it exists, verify it has content
        import json

        with open(package_file) as f:
            data = json.load(f)
            assert isinstance(data, dict)
