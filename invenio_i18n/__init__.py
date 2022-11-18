# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

r"""Invenio internationalization module.

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
>>> from invenio_i18n.views import create_blueprint_from_app
>>> i18n = InvenioI18N(app)
>>> app.register_blueprint(create_blueprint_from_app(app))

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

Angular
~~~~~~~
There is also simple integration for Angular application using Angular-Gettext
library. First, you need to mark HTML tags which contain translatable string
or expression.

.. code-block:: html

   <a href="/" translate>Hello {{name}}</a>

For further details see:

* https://angular-gettext.rocketeer.be/
* https://github.com/neillc/angular-gettext-babel

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

Working with Message Catalogs
-----------------------------
Babel package contains really good documentation which you should read
first:

* http://babel.pocoo.org/en/latest/messages.html

Angular-Gettext
~~~~~~~~~~~~~~~
This part focuses on how to configure Babel extraction for Angular application
in custom ``babel-js.ini`` file:

.. code-block:: text

  [angular_gettext: **/static/templates/**/**.html]

To make message extraction and catalog extraction easier you can add following
aliases to ``setup.cfg`` (replace ``${PACKAGE_PATH}`` with package path):

.. code-block:: text

  [aliases]
  extract_messages_js = extract_messages -F babel-js.ini -o \
      ${PACKAGE_PATH}/translations/messages-js.pot
  init_catalog_js = init_catalog -D messages-js --input-file \
      ${PACKAGE_PATH}/translations/messages-js.pot
  update_catalog_js = update_catalog -D messages-js --input-file \
      ${PACKAGE_PATH}/translations/messages-js.pot

Integration with Transifex service
----------------------------------
There is a Python package that provides CLI. You can start by installing
*Transifex* package and check if the ``tx`` command is available:

.. code-block:: console

   $ pip install transifex-client
   $ tx --version
   0.12.2

The integration is configured in ``.tx/config`` file (replace
``${PACKAGE_PATH}`` and ``${PACKAGE_NAME}``).

.. code-block:: text

   [main]
   host = https://www.transifex.com

   [invenio.${PACKAGE_NAME}-messages]
   file_filter = ${PACKAGE_PATH}/translations/<lang>/LC_MESSAGES/messages.po
   source_file = ${PACKAGE_PATH}/translations/messages.pot
   source_lang = en
   type = PO

   [invenio.${PACKAGE_NAME}-messages-js]
   file_filter = ${PACKAGE_PATH}/translations/<lang>/LC_MESSAGES/messages-js.po
   source_file = ${PACKAGE_PATH}/translations/messages-js.pot
   source_lang = en
   type = PO

1. Create message catalog
~~~~~~~~~~~~~~~~~~~~~~~~~
Start by extracting localizable messages from a collection of source files.

.. code-block:: console

   $ python setup.py extract_messages
   $ python setup.py init_catalog -l <lang>

If you have localizable Angular messages run commands with ``_js`` suffix too.

.. code-block:: console

   $ python setup.py extract_messages_js
   $ python setup.py init_catalog_js -l <lang>

2. Transifex project
~~~~~~~~~~~~~~~~~~~~
Ensure project has been created on Transifex under the ``inveniosoftware``
organisation.


3. First push
~~~~~~~~~~~~~
Push source (``.pot``) and translations (``.po``) to Transifex.

.. code-block:: console

   $ tx push -s -t

.. note::

   From now on do not edit ``.po`` files localy, but only on Transifex.

4. Fetch changes
~~~~~~~~~~~~~~~~
Pull translations for a single/all language(s) from Transifex.

.. code-block:: console

   $ tx pull -l <lang>
   $ tx pull -a

Check fetched tranlations, commit changes
``git commit -a -s -m 'i18n: updates from Transifex'`` and create
pull-request.

5. Update message catalog
~~~~~~~~~~~~~~~~~~~~~~~~~
When new localizable messages are introduced or changes, the message
catalog needs to be extracted again. Then you need to push the source
files to Transifex service which will take care about updating catalogs.
At the end pull translations for all languages from Transifex and commit
the changes.

.. code-block:: console

   $ python setup.py extract_messages
   $ python setup.py extract_messages_js
   $ tx push -s
   $ tx pull -a
"""

from __future__ import absolute_import, print_function

# Monkey patch Werkzeug 2.1
# Flask-Login uses the safe_str_cmp method which has been removed in Werkzeug
# 2.1. Flask-Login v0.6.0 (yet to be released at the time of writing) fixes the
# issue. Once we depend on Flask-Login v0.6.0 as the minimal version in
# Flask-Security-Invenio/Invenio-Accounts we can remove this patch again.
try:
    # Werkzeug <2.1
    from werkzeug import security

    security.safe_str_cmp
except AttributeError:
    # Werkzeug >=2.1
    import hmac

    from werkzeug import security

    security.safe_str_cmp = hmac.compare_digest

from .ext import InvenioI18N

__version__ = "1.3.3"

__all__ = ("__version__", "InvenioI18N")
