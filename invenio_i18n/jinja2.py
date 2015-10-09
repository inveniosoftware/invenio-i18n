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

"""Babel datetime localization template filters for Jinja.

See full documentation of corresponding methods in Flask-BabelEx:
https://pythonhosted.org/Flask-BabelEx/
"""

from __future__ import absolute_import, print_function

from flask_babelex import to_user_timezone, to_utc


def filter_to_user_timezone(dt):
    """Convert a datetime object to the user's timezone."""
    return to_user_timezone(dt)


def filter_to_utc(dt):
    """Convert a datetime object to UTC and drop tzinfo."""
    return to_utc(dt)
