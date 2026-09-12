# PDSSP Prov Toolkit - Shared W3C PROV-DM vocabulary, document helpers, and Graphviz/HTML rendering for FAIR-transformation provenance across PDSSP services.
# Copyright (C) 2026 - CNES (Jean-Christophe Malapert for PDSSP)
# This file is part of PDSSP Prov Toolkit <https://gitlab.cnes.fr/pdssp/pdssp_prov_toolkit>
# SPDX-License-Identifier: Apache-2.0

"""Shared W3C PROV-DM vocabulary, document helpers, and Graphviz/HTML
rendering for FAIR-transformation provenance across PDSSP services.

A library, not an application -- it configures no logging of its own
(that is each consuming service's own decision to make) and has no CLI.
"""

from ._version import (
    __author__,
    __author_email__,
    __copyright__,
    __description__,
    __license__,
    __name_soft__,
    __title__,
    __url__,
    __version__,
)
from .document import FOAF_NS, new_document, resolve_agent, slug
from .dot import prov_to_dot
from .html import render_prov_html
from .vocab import ProvAttr, ProvQualifier, ProvType

__all__ = [
    "FOAF_NS",
    "ProvAttr",
    "ProvQualifier",
    "ProvType",
    "__author__",
    "__author_email__",
    "__copyright__",
    "__description__",
    "__license__",
    "__name_soft__",
    "__title__",
    "__url__",
    "__version__",
    "new_document",
    "prov_to_dot",
    "render_prov_html",
    "resolve_agent",
    "slug",
]
