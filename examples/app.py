# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016, 2017 CERN.
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


"""Minimal Flask application example for development.

Run the development server:

.. code-block:: console

   $ pip install -e .[all]
   $ cd examples
   $ ./app-setup.sh

Run example development server:

.. code-block:: console

    $ FLASK_APP=app.py flask run --debugger -p 5000

The example application will render "Hello World" and display language
selectors for english, danish and spanish that allow you to change the text to
the given language.

To be able to uninstall the example app:

.. code-block:: console

    $ ./app-teardown.sh
"""

from __future__ import absolute_import, print_function

from flask import Flask, render_template

from invenio_i18n import InvenioI18N

# Create Flask application
app = Flask(__name__)
app.config.update(
    SECRET_KEY='CHANGE_ME',
    I18N_LANGUAGES=[('da', 'Danish'), ('en', 'English'), ('es', 'Spanish')],
)
InvenioI18N(app)


@app.route('/')
def index():
    return render_template('invenio_i18n/page.html')
