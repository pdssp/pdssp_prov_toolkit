# PDSSP Prov Toolkit - Shared W3C PROV-DM vocabulary, document helpers, and Graphviz/HTML rendering for FAIR-transformation provenance across PDSSP services.
# Copyright (C) 2026 - CNES (Jean-Christophe Malapert for PDSSP)
# This file is part of PDSSP Prov Toolkit <https://gitlab.cnes.fr/pdssp/pdssp_prov_toolkit>
# SPDX-License-Identifier: Apache-2.0

"""
Generic PROV-DM document helpers.
====================================
Small, domain-agnostic building blocks every service assembling its own
:class:`~prov.model.ProvDocument` needs regardless of its own pipeline
shape (a live-mapping STAC proxy, an offline GeoPackage-compilation
pipeline, ...): a namespaced empty document, a safe local identifier from
a free-text name, and de-duplicated agent lookup.

Deliberately excludes anything that assumes a particular pipeline shape
(e.g. "one software agent acting on behalf of another", "a source entity
attributed to a producer/licensor") -- those patterns are common across
today's two PDSSP consumers of this package, but each has grown its own,
differently-shaped set of activities/entities around them, so forcing a
single higher-level "build me a document" helper here would either fit
neither well or silently constrain a future consumer's own pipeline shape.
Each service keeps that assembly logic in its own codebase, built out of
these primitives plus :mod:`.vocab`.
"""

from __future__ import annotations

import re
from typing import Any

from prov.model import ProvDocument

from .vocab import ProvAttr

#: Default FOAF namespace URI, bound to the ``foaf`` prefix by
#: :func:`new_document`.
FOAF_NS = "https://xmlns.com/foaf/0.1/"


def new_document(base: str, foaf_ns: str = FOAF_NS) -> ProvDocument:
    """Return an empty :class:`ProvDocument` namespaced for *base*.

    Parameters
    ----------
    base:
        Public base URL of the service (no trailing slash), used as the
        default namespace so record identifiers resolve to real URIs.
    foaf_ns:
        Namespace URI bound to the ``foaf`` prefix.
    """
    doc = ProvDocument()
    doc.set_default_namespace(f"{base}/prov#")
    doc.add_namespace("foaf", foaf_ns)
    return doc


def slug(name: str) -> str:
    """Turn a free-text name into a safe PROV local identifier, e.g.
    ``"NASA PDS Geosciences Node"`` -> ``"nasa-pds-geosciences-node"``.

    A PROV-N/PROV-XML identifier's local part is a QName-like token that
    cannot contain arbitrary characters (spaces, ``/``, ...) -- this is the
    one place in the toolkit that turns a human-facing name into something
    safe to use as one.
    """
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "agent"


def resolve_agent(doc: ProvDocument, agents: dict[str, Any], name: str, prov_type: str) -> Any:
    """Return the existing agent named *name* in *agents*, or add (and
    cache into *agents*) a new one of *prov_type* -- so the same real-world
    party never gets a duplicate record across different callers or calls.

    Parameters
    ----------
    doc:
        The document to add a new agent to, if needed.
    agents:
        Mutable ``name -> ProvAgent`` cache, shared across every caller
        resolving agents for *doc* (typically built up alongside whatever
        per-pipeline agents a service adds itself).
    name:
        The agent's human-facing name (also used as its ``prov:label`` and
        ``foaf:name`` when a new record is created).
    prov_type:
        One of :class:`~.vocab.ProvType`'s agent-shaped values (``PERSON``,
        ``ORGANIZATION``, ``SOFTWARE_AGENT``) for a newly created record;
        ignored when *name* already resolves to an existing agent.
    """
    agent = agents.get(name)
    if agent is None:
        agent = doc.agent(
            slug(name),
            {ProvAttr.TYPE: prov_type, ProvAttr.LABEL: name, ProvAttr.FOAF_NAME: name},
        )
        agents[name] = agent
    return agent
