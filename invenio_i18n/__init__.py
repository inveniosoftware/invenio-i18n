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

"""Invenio internationalization module.

This module provide features for loading and merging message catalogs. It is
built on top of `Flask-BabelEx <https://pythonhosted.org/Flask-BabelEx/>`_ and
most external modules should just depend on Flask-BabelEx instead of
Invenio-I18N. Only applications in need of loading and merging many message
catalogs should integrate this module.

Quick start
-----------
First initialize the extension (Flask-BabelEx is also automatically initialized
by the extension):

>>> from flask import Flask
>>> from flask_babelex import lazy_gettext as _
>>> app = Flask('myapp')
>>> app.config['I18N_LANGUAGES'] = [('cs', _('Czech')), ('da', _('Danish'))]
>>> from invenio_i18n import InvenioI18N
>>> i18n = InvenioI18N(app)

You can now use the Flask-BabelEx localization features:

>>> from flask_babelex import format_number
>>> with app.test_request_context(headers=[('Accept-Language', 'en')]):
...     format_number(10.1) == '10.1'
True
>>> with app.test_request_context(headers=[('Accept-Language', 'cs')]):
...     format_number(10.1) == '10,1'
True

as well as internationalization features:

>>> from flask_babelex import gettext
>>> with app.test_request_context(headers=[('Accept-Language', 'en')]):
...     gettext('Language:') == 'Language:'
True
>>> with app.test_request_context(headers=[('Accept-Language', 'cs')]):
...     gettext('Language:') == 'Jazyk:'
True

Marking strings for translation
-------------------------------
Following is a short overview on how to mark strings in Python code and
templates for translation so that they can be automatically extracted:

Python
~~~~~~
You specify translations in Python by importing ``gettext`` or ``lazy_gettext``
from Flask-BabelEx:

>>> from flask_babelex import gettext as _
>>> _('Test') == 'Test'
True

For further details and examples see:

 * https://pythonhosted.org/Flask-BabelEx/#using-translations
 * http://babel.pocoo.org/en/latest/messages.html#working-with-message-catalogs

Jinja2
~~~~~~
In templates you can use either the underscore function:

>>> from flask import render_template_string
>>> with app.app_context():
...     render_template_string("{{_('Test')}}") == 'Test'
True

or the ``{% trans %}`` tag:

>>> with app.app_context():
...     r = render_template_string('{% trans %}Long translation{% endtrans %}')
...     r == 'Long translation'
True

For further details and examples see:

* http://jinja.pocoo.org/docs/dev/templates/#i18n

Templates
---------
This section only gives a very quick introduction into custom context variables
and filters.

Context
~~~~~~~
The ``current_i18n`` global variable is available within Jinja2 templates
to give access to an instance of :class:`~invenio_i18n.ext.InvenioI18N`
attached to current application context.

>>> with app.test_request_context(headers=[('Accept-Language', 'en')]):
...     r = render_template_string('{{ current_i18n.language }}')
...     r == 'en'
True
>>> with app.test_request_context(headers=[('Accept-Language', 'en')]):
...     r = render_template_string('{{ current_i18n.timezone }}')
...     r == 'UTC'
True
>>> with app.test_request_context(headers=[('Accept-Language', 'da')]):
...     r = render_template_string('{{ current_i18n.locale }}')
...     r == 'da'
True

Filters
~~~~~~~
There are several useful filters automatically added to the Jinja2 template
context:

* ``tousertimezone`` converts a datetime object to the user's timezone
  (see :func:`~invenio_i18n.jinja2.filter_to_user_timezone`).
* ``toutc`` converts a datetime object to UTC and drop tzinfo
  (see :func:`~invenio_i18n.jinja2.filter_to_utc`).
* ``language_name`` converts language code into display name in current locale
  (see :func:`~invenio_i18n.jinja2.filter_language_name`).
* ``language_name_local`` converts language code into display name in local
  locale (see :func:`~invenio_i18n.jinja2.filter_language_name_local`).

Macros
~~~~~~
Invenio-I18N also provides three templates macros that you can use to render a
language selector in templates with:

* ``language_selector`` - Renders a list of links and uses GET requests to
  change the locale.
* ``language_selector_form`` - Same as above, but uses POST requests to change
  the locale.
* ``language_selector_dropdown`` - Renders a dropdown with languages and uses
  a POST request to change the locale.

You use the macros by importing one of them from
``invenio_i18n/macros/language_selector.html``, for instance:

>>> with app.test_request_context():
...     r = render_template_string(
...         '{% from "invenio_i18n/macros/language_selector.html"'
...         '   import language_selector %}'
...         '{{ language_selector() }}'
...     )
"""

from __future__ import absolute_import, print_function

from .ext import InvenioI18N
from .version import __version__

__all__ = ('__version__', 'InvenioI18N')
