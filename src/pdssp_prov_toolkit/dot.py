# PDSSP Prov Toolkit - Shared W3C PROV-DM vocabulary, document helpers, and Graphviz/HTML rendering for FAIR-transformation provenance across PDSSP services.
# Copyright (C) 2026 - CNES (Jean-Christophe Malapert for PDSSP)
# This file is part of PDSSP Prov Toolkit <https://gitlab.cnes.fr/pdssp/pdssp_prov_toolkit>
# SPDX-License-Identifier: Apache-2.0

"""
DOT (Graphviz) rendering for PROV-DM documents.
=================================================
Converts a :class:`prov.model.ProvDocument` into Graphviz DOT source, using
the standard PROV-DM node shapes/colours (yellow ellipses for entities,
blue rounded boxes for activities, orange houses for agents), matching the
W3C PROV Primer and ProvStore/ProvToolbox conventions.

Produces plain DOT *text* only -- no native ``graphviz`` binary or extra
Python dependency beyond ``prov`` itself (deliberately not built on
``prov``'s own optional ``prov[dot]``/``pydot`` extra, which needs a real
dependency and does not word-wrap long labels/URLs -- see this module's
own history for why that matters: an unwrapped long label/location made an
early graph too wide to read). Rendering the DOT source itself happens
client-side, in the browser, via Viz.js (see :mod:`.html`).

Covers exactly the record/relation shapes the two services this toolkit
was extracted from actually produce -- every :class:`~prov.model.ProvRecord`
subtype ``prov`` itself defines that isn't listed in :data:`_RELATION_SPECS`
is simply not drawn as an edge (nodes for entities/activities/agents are
always drawn regardless). Add to :data:`_RELATION_SPECS` (and, for a new
attribute, to :func:`_label_lines`) rather than working around a gap here.
"""

from __future__ import annotations

import textwrap

from prov.model import (
    ProvActivity,
    ProvAgent,
    ProvAssociation,
    ProvAttribution,
    ProvCommunication,
    ProvDelegation,
    ProvDerivation,
    ProvDocument,
    ProvEntity,
    ProvGeneration,
    ProvMembership,
    ProvRecord,
    ProvUsage,
)

from .vocab import ProvAttr, ProvQualifier


class ProvDotConfig:
    ENTITY_STYLE = 'shape=ellipse, style=filled, fillcolor="#FFFC87", color="#808080"'
    ACTIVITY_STYLE = 'shape=box, style="filled,rounded", fillcolor="#9FB1FC", color="#0000FF"'
    AGENT_STYLE = 'shape=house, style=filled, fillcolor="#FED37F", color="#D2691E"'

    #: Relation record type -> (source attribute, target attribute, edge label,
    #: edge line style), per the PROV-DM diagram conventions. Attribute names
    #: are :class:`~.vocab.ProvQualifier` keys.
    RELATION_SPECS: dict[type, tuple[str, str, str, str]] = {
        ProvGeneration: (ProvQualifier.ENTITY, ProvQualifier.ACTIVITY, "wasGeneratedBy", "solid"),
        ProvUsage: (ProvQualifier.ACTIVITY, ProvQualifier.ENTITY, "used", "dashed"),
        ProvDerivation: (
            ProvQualifier.GENERATED_ENTITY,
            ProvQualifier.USED_ENTITY,
            "wasDerivedFrom",
            "solid",
        ),
        ProvAssociation: (
            ProvQualifier.ACTIVITY,
            ProvQualifier.AGENT,
            "wasAssociatedWith",
            "dotted",
        ),
        ProvAttribution: (ProvQualifier.ENTITY, ProvQualifier.AGENT, "wasAttributedTo", "dotted"),
        ProvDelegation: (
            ProvQualifier.DELEGATE,
            ProvQualifier.RESPONSIBLE,
            "actedOnBehalfOf",
            "dotted",
        ),
        ProvMembership: (ProvQualifier.COLLECTION, ProvQualifier.ENTITY, "hadMember", "solid"),
        ProvCommunication: (
            ProvQualifier.INFORMED,
            ProvQualifier.INFORMANT,
            "wasInformedBy",
            "dashed",
        ),
    }

    #: Target line length for node-label wrapping (short values stay on one
    #: line; long URLs/descriptions get broken up).
    WRAP_WIDTH = 50


def prov_to_dot(doc: ProvDocument) -> str:
    """Render *doc* as Graphviz DOT source.

    Parameters
    ----------
    doc:
        The PROV-DM document to render.

    Returns
    -------
    str
        A ``digraph`` DOT source string, ready to be rendered by any
        Graphviz-compatible tool (the ``dot`` CLI, or client-side via
        Viz.js).
    """
    lines = [
        "digraph provenance {",
        "  rankdir=LR;",
        "  nodesep=0.4;",
        "  ranksep=0.6;",
        '  node [fontname="Helvetica,Arial,sans-serif", fontsize=11];',
        '  edge [fontname="Helvetica,Arial,sans-serif", fontsize=9];',
    ]

    for record in doc.get_records():
        if isinstance(record, (ProvEntity, ProvActivity, ProvAgent)):
            lines.append(_node_line(record))

    for record in doc.get_records():
        spec = ProvDotConfig.RELATION_SPECS.get(type(record))
        if spec is not None:
            lines.append(_edge_line(record, *spec))
        if isinstance(record, ProvAssociation):
            plan_edge = _plan_edge_line(record)
            if plan_edge is not None:
                lines.append(plan_edge)

    lines.append("}")
    return "\n".join(lines)


def _node_line(
    record: ProvRecord,
    entity_style: str = ProvDotConfig.ENTITY_STYLE,
    activity_style: str = ProvDotConfig.ACTIVITY_STYLE,
    agent_style: str = ProvDotConfig.AGENT_STYLE,
) -> str:
    """Return the DOT statement declaring one entity/activity/agent node."""
    if isinstance(record, ProvEntity):
        style = entity_style
    elif isinstance(record, ProvActivity):
        style = activity_style
    else:
        style = agent_style
    # Joined with a literal "\n" (backslash-n), which Graphviz renders as a
    # line break inside a label -- not an actual newline character, which
    # `_escape` would otherwise be free to mangle along with the rest.
    label = "\\n".join(_escape(line) for line in _label_lines(record))
    return f'  "{record.identifier.localpart}" [label="{label}", {style}];'


def _edge_line(record: ProvRecord, from_attr: str, to_attr: str, label: str, style: str) -> str:
    """Return the DOT statement for one relation record, per *spec*."""
    attrs = {str(key): value for key, value in record.formal_attributes}
    src = _local(attrs.get(from_attr))
    dst = _local(attrs.get(to_attr))
    return f'  "{src}" -> "{dst}" [label="{label}", style={style}];'


def _plan_edge_line(record: ProvRecord) -> str | None:
    """Return the extra ``hadPlan`` edge for an association naming a plan.

    Not covered by :data:`ProvDotConfig.RELATION_SPECS` (which only draws
    the activity/agent edge) -- drawn only when a plan is actually present
    (a ``wasAssociatedWith`` with no ``plan=`` produces no edge here).
    """
    attrs = {str(key): value for key, value in record.formal_attributes}
    activity = attrs.get(ProvQualifier.ACTIVITY)
    plan = attrs.get(ProvQualifier.PLAN)
    if activity is None or plan is None:
        return None
    return f'  "{_local(activity)}" -> "{_local(plan)}" [label="hadPlan", style=dotted];'


def _local(qname) -> str:
    """Return the local part of a :class:`~prov.identifier.QualifiedName`, or ``"?"``."""
    return qname.localpart if qname is not None else "?"


def _label_lines(record: ProvRecord) -> list[str]:
    """Return the lines to display inside *record*'s node: the word-wrapped
    primary label (``prov:label``, falling back to the identifier), then
    ``version``, ``identifier``, ``license`` and ``crs`` when present, and
    a hard-wrapped ``prov:location`` when present -- each shown only for a
    record that actually carries it, so a consumer that never sets e.g.
    ``crs`` never sees an empty line.
    """
    lines = _wrap_text(_primary_label(record))
    version = _first_attribute(record, ProvAttr.VERSION)
    if version is not None:
        lines.append(f"v{version}")
    identifier = _first_attribute(record, ProvAttr.IDENTIFIER)
    if identifier is not None:
        lines.append(f"id: {identifier}")
    license_ = _first_attribute(record, ProvAttr.LICENSE)
    if license_ is not None:
        lines.append(f"license: {license_}")
    crs = _first_attribute(record, ProvAttr.CRS)
    if crs is not None:
        lines.append(f"crs: {crs}")
    location = _first_attribute(record, ProvAttr.LOCATION)
    if location is not None:
        lines.extend(_wrap_url(str(location)))
    return lines


def _wrap_text(text: str, wrap_width: int = ProvDotConfig.WRAP_WIDTH) -> list[str]:
    """Word-wrap free-form prose (e.g. a ``prov:label``) at *wrap_width*."""
    return textwrap.wrap(text, width=wrap_width, break_on_hyphens=False) or [text]


def _wrap_url(text: str, wrap_width: int = ProvDotConfig.WRAP_WIDTH) -> list[str]:
    """Hard-wrap a URL into chunks of at most *wrap_width* chars, preferring
    to break at ``&``/``/`` near the target width over a hard mid-word cut.
    """
    lines = []
    remaining = text
    while len(remaining) > wrap_width:
        cut = wrap_width
        for sep in ("&", "/"):
            idx = remaining.rfind(sep, 0, wrap_width + 15)
            if idx > wrap_width // 2:
                cut = idx + 1
                break
        lines.append(remaining[:cut])
        remaining = remaining[cut:]
    lines.append(remaining)
    return lines


def _primary_label(record: ProvRecord) -> str:
    """Return ``record``'s ``prov:label``, or its identifier if it has none."""
    values = record.get_attribute(ProvAttr.LABEL)
    if values:
        return str(next(iter(values)))
    return record.identifier.localpart


def _first_attribute(record: ProvRecord, name: str) -> str | None:
    """Return one value of the *name* attribute on *record*, or ``None``."""
    values = record.get_attribute(name)
    return str(next(iter(values))) if values else None


def _escape(text: str) -> str:
    """Escape backslashes and double quotes so *text* is safe inside a DOT string literal."""
    return text.replace("\\", "\\\\").replace('"', '\\"')
