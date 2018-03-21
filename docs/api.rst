..
    This file is part of Invenio.
    Copyright (C) 2015-2018 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

API Docs
========

Extension
---------

.. automodule:: invenio_i18n.ext
   :members:

Translation Domain
------------------

.. automodule:: invenio_i18n.babel
   :members:

Jinja2 filters
--------------
.. automodule:: invenio_i18n.jinja2
   :members:

Locale/timezone selectors
-------------------------
.. automodule:: invenio_i18n.selectors
   :members:

Views
-----
.. automodule:: invenio_i18n.views
   :members:

Date/time formatting
--------------------
For formatting date and time using the current locale settings, you may use the methods provided by `Flask-BabelEx <http://pythonhosted.org/Flask-BabelEx/#formatting-dates>`_.

These methods are also available as Jinja filters:

* `format_datetime <http://pythonhosted.org/Flask-BabelEx/#flask.ext.babelex.format_datetime>`_ as ``datetimeformat``
* `format_date <http://pythonhosted.org/Flask-BabelEx/#flask.ext.babelex.format_date>`_ as ``dateformat``
* `format_time <http://pythonhosted.org/Flask-BabelEx/#flask.ext.babelex.format_time>`_ as ``timeformat``
* `format_timedelta <http://pythonhosted.org/Flask-BabelEx/#flask.ext.babelex.format_timedelta>`_ as ``timedeltaformat``.
