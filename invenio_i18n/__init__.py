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
>>> app.config['I18N_LANGUAGES'] = [('da', _('Danish'))]
>>> from invenio_i18n import InvenioI18N
>>> i18n = InvenioI18N(app)

You can now use the Flask-BabelEx localization features:

>>> from flask_babelex import format_number
>>> with app.test_request_context(headers=[('Accept-Language', 'en')]):
...     format_number(10.1) == '10.1'
True
>>> with app.test_request_context(headers=[('Accept-Language', 'da')]):
...     format_number(10.1) == '10,1'
True

as well as internationalization features:

>>> from flask_babelex import gettext
>>> with app.test_request_context(headers=[('Accept-Language', 'en')]):
...     gettext('Translate') == 'Translate'
True
>>> with app.test_request_context(headers=[('Accept-Language', 'da')]):
...     gettext('Translate') != u'Translate'
True


Configuration
-------------

================================ =============================================
`I18N_TRASNLATION_PATHS`         List of paths to load message catalogs from.
                                 Defaults to ``[]``.
`I18N_LANGUAGES`                 List of tuples of available languages (you
                                 should not include ``BABEL_DEFAULT_LOCALE``
                                 in this list). Defaults to:
                                 ``[]``.
`I18N_SESSION_KEY`               Key to retrieve from Flask session object
                                 the variable which is containing the language
                                 for the current session.
`I18N_USER_LANG_ATTR`            Key to retrieve from the User object the
                                 variable which is containing the prefered
                                 language of the user.
`I18N_SET_LANGUAGE_URL`          URL prefix for set language view. Set to
                                 ``None`` to prevent view from being installed.
                                 Default: ``/lang``.
`I18N_DEFAULT_REDIRECT_ENDPOINT` Default endpoint to redirect to if no next
                                 parameter is provided to set language view.
                                 Default: ``/``.
================================ =============================================

In addition, Flask-BabelEx sets system-wide defaults using the following
configuration variables:

=========================== =============================================
`BABEL_DEFAULT_LOCALE`      The default locale to use if no locale
                            selector is registered.  This defaults
                            to ``'en'``.
`BABEL_DEFAULT_TIMEZONE`    The timezone to use for user facing dates.
                            This defaults to ``'UTC'`` which also is the
                            timezone your application must use internally.
=========================== =============================================

Marking strings for translation
-------------------------------
Following is a short overview on how to mark strings in Python code and
templates for translation so that they can be automatically extracted:

Python
~~~~~~
You specify translations in Python by importing ``gettext`` or ``lazy_gettext``
from Flask-BabelEx:

>>> from flask_babelex import gettext as _
>>> _("Test") == 'Test'
True

For further details and examples see:

 * https://pythonhosted.org/Flask-BabelEx/#using-translations
 * http://babel.pocoo.org/docs/messages/#working-with-message-catalogs


Templates
~~~~~~~~~
In templates you can use either the underscore function:

>>> from flask import render_template_string
>>> with app.app_context():
...     render_template_string("{{_('Test')}}") == 'Test'
True

or the ``{% trans %}`` tag:

>>> with app.app_context():
...     r = render_template_string("{% trans %}Long translation{% endtrans %}")
...     r == "Long translation"
True

For further details and examples see:

* http://jinja.pocoo.org/docs/dev/templates/#i18n
"""

from __future__ import absolute_import, print_function

from .ext import InvenioI18N
from .version import __version__

__all__ = ('__version__', 'InvenioI18N')
