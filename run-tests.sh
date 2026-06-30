# SPDX-FileCopyrightText: 2015-2018 CERN.
# SPDX-FileCopyrightText: 2022 Graz University of Technology.
# SPDX-FileCopyrightText: 2026 TU Wien.
# SPDX-License-Identifier: MIT

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

pybabel compile -d invenio_i18n/translations --use-fuzzy --output-file /dev/null
python -m babel.messages.frontend compile -d tests/translations/
python -m sphinx.cmd.build -qnNW docs docs/_build/html
python -m pytest
