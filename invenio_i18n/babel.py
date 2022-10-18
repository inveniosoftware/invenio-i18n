# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Flask-Babel domain for merging translations from many directories."""

import os
from contextlib import contextmanager

from babel import Locale
from flask_babel import Domain, _get_current_context
from pkg_resources import iter_entry_points, resource_filename, resource_isdir


# TODO:
# think of replacing it with force_locale from flask_babel
@contextmanager
def set_locale(ln):
    """Set Babel localization in request context.

    :param ln: Language identifier.
    """
    ctx = _get_current_context()
    if ctx is None:
        raise RuntimeError("Working outside of request context.")

    new_locale = Locale.parse(ln)
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
        super().__init__(domain=domain)
        self._translation_directories = []

        if entry_point_group:
            self.add_entrypoint(entry_point_group)

        for p in paths or []:
            self.add_path(p)

    def has_paths(self):
        """Determine if any paths have been specified."""
        return bool(self._translation_directories)

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
            raise RuntimeError(f"Path does not exists: {path}")
        self._translation_directories.append(path)
