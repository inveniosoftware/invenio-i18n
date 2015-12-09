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

"""Views for Invenio-I18N."""

from __future__ import absolute_import, print_function

from flask import Blueprint, abort, current_app, redirect, request, session, \
    url_for
from six.moves.urllib.parse import urljoin, urlparse

blueprint = Blueprint(
    'invenio_i18n',
    __name__,
    template_folder='templates',
)


def is_local_url(target):
    """Determine if URL is safe to redirect to."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def get_redirect_target():
    """Get URL to redirect to and ensure that it is local."""
    for target in request.values.get('next'), request.referrer:
        if target and is_local_url(target):
            return target


@blueprint.route('/', methods=['POST'])
@blueprint.route('/<lang_code>/', methods=['GET'])
def set_lang(lang_code=None):
    """Set language in session and redirect."""
    # Check if language is available.
    lang_code = lang_code or request.values.get('lang_code')
    languages = dict(current_app.extensions['invenio-i18n'].get_languages())
    if lang_code is None or lang_code not in languages:
        abort(404 if request.method == 'GET' else 400)

    # Set language in session.
    session[current_app.config['I18N_SESSION_KEY']] = lang_code.lower()

    # Redirect user back.
    target = get_redirect_target()
    if not target:
        endpoint = current_app.config['I18N_DEFAULT_REDIRECT_ENDPOINT']
        target = url_for(endpoint) if endpoint else '/'

    return redirect(target)
