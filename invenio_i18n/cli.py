# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio internationalization module."""

import click
from invenio_app.factory import create_ui


@click.group()
def i18n(ctx):
    """I18N group."""


# TODO

# think of how to hook those two commands into invenio-cli without destroying
# the performance boosts of the uv+rspack+pnpm changes. i am thinking of adding
# a flag and caching mechanism

# maybe move the content below into separate files, but keep the cli
# functionality, because this should be usable without invenio-cli too, but
# invenio-cli should not necessarily rely on cli commands. it should be possible
# to use a function or class in invenio-cli (performance)


@i18n.command()
@click.option("--language")
def collect(language):
    """Collect."""
    app = create_ui()
    bundles = app.extensions["invenio-assets"].project.bundles

    for bundle in bundles:
        # needs slint/invenio-assets@rspack
        bundle.app = app

        print(f"collect theme: {bundle.aliases}")

        # TODO:

        # collect all messages.json from `translations/*` paths and combine
        # theme into one messages.json according to the language parameter. the
        # message strings have to be namespaced with the package name

        # add new entry_point_group like invenio_i18n.translation_bundle to have
        # a entry point to hook in the javascript translation of the translation
        # bundle. the translations have to be namespaced by the package name

        # think of how to incorporate the messages.json file from my-site

        # combine all three options into one big messages.json file. the latest
        # overrides the previous and so on

        # write that messages.json file somewhere

        # ATTENTION:
        # keep an eye to the react-invenio-* packages


@i18n.command()
@click.option("--language")
def spread(language):
    """Spread."""

    # TODO

    # use the big messages.json file collected in collect to spread over the
    # messages.json files in the different packages installed in the virtual
    # environment using the namespaced message-ids to know into which package
    # which message-id should be copyied.
