# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Flask-BabelEx domain for merging translations from many directories."""

from __future__ import absolute_import, print_function

import os
from contextlib import contextmanager

from babel.support import NullTranslations, Translations
from flask import _request_ctx_stack, current_app
from flask_babelex import Domain, get_locale
from pkg_resources import iter_entry_points, resource_filename, resource_isdir


@contextmanager
def set_locale(ln):
    """Set Babel localization in request context.

    :param ln: Language identifier.
    """
    ctx = _request_ctx_stack.top
    if ctx is None:
        raise RuntimeError("Working outside of request context.")
    new_locale = current_app.extensions["babel"].load_locale(ln)
    old_locale = getattr(ctx, "babel_locale", None)
    setattr(ctx, "babel_locale", new_locale)
    yield
    setattr(ctx, "babel_locale", old_locale)


class MultidirDomain(Domain):
    """Domain supporting merging translations from many catalogs.

    The domain contains an internal list of paths that it loads translations
    from. The translations are merged in order of the list of paths, hence
    the last path in the list will overwrite strings set by previous paths.

    Entry points are added to the list of paths before the ``paths``.
    """

    def __init__(self, paths=None, entry_point_group=None, domain="messages"):
        """Initialize domain.

        :param paths: List of paths with translations.
        :param entry_point_group: Name of entry point group.
        :param domain: Name of message catalog domain.
            (Default: ``'messages'``)
        """
        self.paths = []
        if entry_point_group:
            self.add_entrypoint(entry_point_group)
        for p in paths or []:
            self.add_path(p)
        super(MultidirDomain, self).__init__(domain=domain)

    def has_paths(self):
        """Determine if any paths have been specified."""
        return bool(self.paths)

    def add_entrypoint(self, entry_point_group):
        """Load translations from an entry point."""
        for ep in iter_entry_points(group=entry_point_group):
            if not resource_isdir(ep.module_name, "translations"):
                continue
            dirname = resource_filename(ep.module_name, "translations")
            self.add_path(dirname)

    def add_path(self, path):
        """Load translations from an existing path."""
        if not os.path.exists(path):
            raise RuntimeError("Path does not exists: %s." % path)
        self.paths.append(path)

    def _get_translation_for_locale(self, locale):
        """Get translation for a specific locale."""
        translations = None

        for dirname in self.paths:
            # Load a single catalog.
            catalog = Translations.load(dirname, [locale], domain=self.domain)
            if translations is None:
                if isinstance(catalog, Translations):
                    translations = catalog
                continue

            try:
                # Merge catalog into global catalog
                translations.merge(catalog)
            except AttributeError:
                # Translations is probably NullTranslations
                if isinstance(catalog, NullTranslations):
                    current_app.logger.debug(
                        "Compiled translations seems to be missing"
                        " in {0}.".format(dirname)
                    )
                    continue
                raise

        return translations or NullTranslations()

    def get_translations(self):
        """Return the correct gettext translations for a request.

        This will never fail and return a dummy translation object if used
        outside of the request or if a translation cannot be found.
        """
        ctx = _request_ctx_stack.top
        if ctx is None:
            return NullTranslations()

        locale = get_locale()

        cache = self.get_translations_cache(ctx)

        translations = cache.get(str(locale))

        if translations is None:
            translations = self._get_translation_for_locale(locale)
            cache[str(locale)] = translations

        return translations
