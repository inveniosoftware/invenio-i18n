..
    This file is part of Invenio.
    Copyright (C) 2015, 2016 CERN.

    Invenio is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    Invenio is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Invenio; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.


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
