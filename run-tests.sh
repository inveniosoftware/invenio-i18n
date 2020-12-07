# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

python -m setup compile_catalog
python -m babel.messages.frontend compile -d tests/translations/
python -m check_manifest --ignore ".*-requirements.txt"
python -m sphinx.cmd.build -qnNW docs docs/_build/html
python -m sphinx.cmd.build -qnNW -b doctest docs docs/_build/doctest
python -m pytest
tests_exit_code=$?
exit "$tests_exit_code"
