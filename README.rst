..
    This file is part of Invenio.
    Copyright (C) 2015-2018 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

==============
 Invenio-I18N
==============

.. image:: https://img.shields.io/github/license/inveniosoftware/invenio-i18n.svg
        :target: https://github.com/inveniosoftware/invenio-i18n/blob/master/LICENSE

.. image:: https://github.com/inveniosoftware/invenio-i18n/workflows/CI/badge.svg
        :target: https://github.com/inveniosoftware/invenio-i18n/actions

.. image:: https://img.shields.io/coveralls/inveniosoftware/invenio-i18n.svg
        :target: https://coveralls.io/r/inveniosoftware/invenio-i18n

.. image:: https://img.shields.io/pypi/v/invenio-i18n.svg
        :target: https://pypi.org/pypi/invenio-i18n

**Invenio-I18N** provides the internationalization layer for InvenioRDM and other Invenio/Flask applications. It integrates the Babel/Flask-Babel stack, merges translation catalogs from multiple sources, exposes safe language-switch routes, and includes CLI tools to fetch from Transifex and distribute i18next-ready JSON for front-end use.

Features
--------
- Load and merge message catalogs from various locations.
- Robust user-locale detection.
- Secure views/endpoints for changing the active locale.
- Jinja2 macros and filters for i18n in templates.
- Fetch from Transifex, read PO files, and convert to/from ``i18next`` JSON for the browser.
- Further documentation: https://invenio-i18n.readthedocs.io/

What it provides
----------------
- **Unified catalogs across locations.** Merge translations from your app, entry-point packages, optional bundles, and extra paths. The multi-directory domain (via ``I18N_TRANSLATIONS_PATHS``) keeps translations modular per feature while rendering as a single catalog.
- **Sensible locale selection.** Language is chosen in this order: **session → user preference → ``Accept-Language`` → default**.
- **Language-switch views.** A small blueprint persists the choice in the session and redirects back safely.
- **Jinja2 helpers.** Macros (e.g., a language selector) and filters such as ``language_name`` plus timezone utilities.
- **Lazy strings.** ``lazy_gettext()`` returns ``LazyString`` objects that resolve at render time—ideal for constants and form labels.
- **Front-end compatibility.** Convert PO catalogs to **i18next-style JSON** or consume i18next JSON directly. Bundled Webpack entries ship minimal JS helpers for the selector; wire JSON into i18next with React, Angular, or plain JS.

How it fits together (high level)
---------------------------------
- **Babel / Flask-Babel** supply gettext, pluralization, and locale-aware formatting.
- **Merged “multidir” domain** overlays catalogs from multiple directories; later sources override earlier ones so apps can override package defaults.
- **Jinja** renders templates/macros for the language selector and localized UI.
- **i18n blueprint** handles ``/lang`` (or your configured path) to set the session language and redirect back.

CLI commands
------------
- **Fetch from Transifex → unified JSON**

  .. code-block:: bash

      invenio i18n fetch-from-transifex \
        -t <TRANSIFEX_TOKEN> -l "en,tr,de" -o js_translations/

  Pulls PO resources from Transifex, maps plurals, and writes **per-language unified i18next JSON**.

- **Distribute JSON back to packages**

  .. code-block:: bash

      invenio i18n distribute-js-translations -i js_translations/

  Splits each unified language file into **per-package** ``translations.json`` under the correct asset paths.

Key configuration (``config.py``)
---------------------------------
- ``I18N_LANGUAGES`` — available languages, e.g. ``[("en","English"),("tr","Türkçe")]``.
- ``I18N_SET_LANGUAGE_URL`` — base URL for the language-switch routes (e.g., ``"/lang"``).
- ``I18N_DEFAULT_REDIRECT_ENDPOINT`` — fallback endpoint after switching.
- ``I18N_SESSION_KEY`` — session key storing the chosen language (default: ``"language"``).
- ``I18N_USER_LANG_ATTR`` — user model attribute for a saved preference (e.g., ``"preferred_language"``).
- ``I18N_TRANSLATIONS_PATHS`` — extra filesystem paths to include in the merged domain.
- ``I18N_JS_DISTR_EXCEPTIONAL_PACKAGE_MAP`` — webpack-entry → package name fixes.
- ``I18N_TRANSIFEX_JS_RESOURCES_MAP`` — maps Transifex resources to packages for JS translations.

Typical locale selection order: **session → user profile → ``Accept-Language`` → ``BABEL_DEFAULT_LOCALE``**.

Minimal setup
-------------

.. code-block:: python

    from flask import Flask
    from invenio_i18n import InvenioI18N
    from invenio_i18n.views import create_blueprint_from_app

    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="dev",
        BABEL_DEFAULT_LOCALE="en",
        BABEL_DEFAULT_TIMEZONE="UTC",
        I18N_LANGUAGES=[("en", "English"), ("tr", "Türkçe")],
        I18N_SET_LANGUAGE_URL="/lang",            # enables the routes
        I18N_USER_LANG_ATTR="preferred_language", # if your User has it
    )

    InvenioI18N(app)                                    # init extension
    app.register_blueprint(create_blueprint_from_app(app))  # language routes

Installation
------------

Available on PyPI:

.. code-block:: bash

    pip install invenio-i18n
