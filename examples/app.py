# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Minimal Flask application example for development.

SPHINX-START

A simple example application demonstrating Invenio-I18N language rendering.

First, install and set up the example application:

.. code-block:: console

   $ pip install -e .[all]
   $ cd examples
   $ ./app-setup.sh

Now start the example application server:

.. code-block:: console

    $ FLASK_APP=app.py flask run --debugger -p 5000

The example application will render "Hello World" and display the language
selectors for English, Danish and Spanish. It will allow you to change the
text to the given language.

You can uninstall the example application as follows:

.. code-block:: console

    $ ./app-teardown.sh

SPHINX-END
"""

from __future__ import absolute_import, print_function

from flask import Flask, render_template
from flask_babelex import lazy_gettext as _

from invenio_i18n import InvenioI18N
from invenio_i18n.views import create_blueprint_from_app

# Create Flask application
app = Flask(__name__)
app.config.update(
    SECRET_KEY="CHANGE_ME",
    BABEL_DEFAULT_LOCALE="en",
    I18N_LANGUAGES=[("da", _("Danish")), ("es", _("Spanish"))],
)
InvenioI18N(app)
app.register_blueprint(create_blueprint_from_app(app))


@app.route("/")
def index():
    return render_template("invenio_i18n/page.html")
