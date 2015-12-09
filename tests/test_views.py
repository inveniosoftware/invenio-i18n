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

"""Basic tests."""

from __future__ import absolute_import, print_function

from flask import session, url_for
from flask_babelex import get_locale

from invenio_i18n import InvenioI18N


def test_lang_view(app):
    """Test extension initalization."""
    app.config.update(
        I18N_LANGUAGES=[('da', 'Danish'), ],
        I18N_SESSION_KEY='my_session_key',
        SECRET_KEY='CHANGEME',
    )
    InvenioI18N(app)

    @app.route("/")
    def index():
        return get_locale().language

    with app.test_request_context():
        da_lang_url = url_for('invenio_i18n.set_lang', lang_code='da')
        en_lang_url = url_for('invenio_i18n.set_lang', lang_code='en')
        es_lang_url = url_for('invenio_i18n.set_lang', lang_code='es')

    with app.test_client() as client:
        # Set language to danish
        res = client.get(da_lang_url)
        assert res.status_code == 302
        assert res.location == 'http://localhost/'
        assert session[app.config['I18N_SESSION_KEY']] == 'da'

        res = client.get("/")
        assert res.get_data(as_text=True) == 'da'

        # Set language to english
        res = client.get(en_lang_url)
        assert res.status_code == 302
        assert res.location == 'http://localhost/'
        assert session[app.config['I18N_SESSION_KEY']] == 'en'

        res = client.get("/")
        assert res.get_data(as_text=True) == 'en'

        # Try to set invalid language.
        res = client.get(es_lang_url)
        assert res.status_code == 404


def test_lang_view_redirect(app):
    """Test extension initalization."""
    app.config.update(
        I18N_LANGUAGES=[('da', 'Danish'), ],
        SECRET_KEY='CHANGEME',
    )
    InvenioI18N(app)

    @app.route("/page/")
    def page():
        return get_locale().language

    with app.test_request_context():
        da_lang_url = url_for('invenio_i18n.set_lang', lang_code='da')
        next_url = url_for('page')

    with app.test_client() as client:
        # Request body
        res = client.get(da_lang_url, data={'next': next_url})
        assert res.status_code == 302
        assert res.location == 'http://localhost/page/'
        assert session[app.config['I18N_SESSION_KEY']] == 'da'

        # Query string
        res = client.get(da_lang_url + "?next={0}".format(next_url))
        assert res.location == 'http://localhost/page/'

        # Referrer header
        res = client.get(da_lang_url, headers={'Referer': next_url})
        assert res.location == 'http://localhost/page/'

        # Unsafe redirects
        res = client.get(da_lang_url + "?next=http://example.org")
        assert res.location == 'http://localhost/'
        res = client.get(
            da_lang_url, headers={'Referer': 'http://example.org'})
        assert res.location == 'http://localhost/'
