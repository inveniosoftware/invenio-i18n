..
    This file is part of Invenio.
    Copyright (C) 2015-2018 CERN.
    Copyright (C) 2024-2025 Graz University of Technology.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

Version v3.4.2 (released 2025-07-22)

- fix(actions): babel compile step missing

Version v3.4.1 (released 2025-07-22)

- fix(babel): migration gone wrong

Version v3.4.0 (released 2025-07-17)

- i18n: pulled translations
- fix(action): commit msg needs whitespace after colon

Version v3.3.0 (released 2025-07-14)

- chores: replaced importlib_xyz with importlib

Version 3.2.0 (released 2025-07-01)

- fix: pkg_resources DeprecationWarning

Version 3.1.0 (released 2025-05-20)

- cli: add command to fetch translation from tansifex
- cli: add command to distribute react translation to packages
- fix: setuptools require underscores instead of dashes

Version 3.0.0 (released 2024-12-02)

- setup: update dependencies

Version 2.2.0 (released 2024-11-28)

- setup: upper pin packages
- fix: tests by pin pytz
- fix: my-site not overriding packages
- ext: add bundle entrypoint
- github: update reusable workflows

Version 2.1.2 (released 2024-08-05)

- fix BABEL_DEFAULT_LOCALE overridability

Version 2.1.1 (released 2023-11-10)

- semantic-ui: Update dependency restriction to be compatible with react-searchkit

Version 2.1.0 (released 2023-07-12)

- add method to check if locale is available

Version 2.0.0 (released 2023-02-27)

- Remove deprecated flask-babelex
- Expose LazyString, gettext from flask_babel to invenio
- Fix get_locale in cli (without request context)
- Replace set_locale with flask_babel.set_locale
- Use Multidomain translation in flask_babel context

Version 1.3.3 (released 2022-11-18)

- Adds translations
- Updates invenio dependencies
- refactors CI tests

Version 1.3.2 (released 2022-03-30)

- Adds support for Flask v2.1

Version 1.3.1 (released 2021-10-06)

- Fixes issue with language selector button not disabling the currently
  selected field.

Version 1.3.0 (released 2020-12-07)

- Integrates Semantic-UI templates and assets.
- Removes webassets-based bundles.
- Adds InvenioI18N extransion to the API level applications.

Version 1.2.0 (released 2020-03-06)

- Bumps Flask-BabelEx support latest Flask/Werkzeug.
- Replaces Flask dependency with ``invenio-base``.

Version 1.1.1 (released 2018-12-12)

- Fix an incorrect JS import.

Version 1.1.0 (released 2018-11-06)

- Introduce webpack support.

Version 1.0.0 (released 2018-03-23)

- Initial public release.
