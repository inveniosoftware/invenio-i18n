# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Basic tests."""

from __future__ import absolute_import, print_function

import pytest
from babel.support import NullTranslations

from invenio_i18n.babel import MultidirDomain


def test_init():
    """Test initialization."""
    d = MultidirDomain(
        paths=['.', '..'], entrypoint='invenio_i18n.translations')
    assert d
    assert d.has_paths()

    d = MultidirDomain()
    assert not d.has_paths()


def test_add_nonexisting_path():
    """Test add non-existing path."""
    d = MultidirDomain()
    pytest.raises(RuntimeError, d.add_path, 'invalidpath')


def test_get_translations():
    """Test get translations."""
    d = MultidirDomain()
    assert isinstance(d.get_translations(), NullTranslations)
