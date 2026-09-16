# PDSSP Prov Toolkit - Shared W3C PROV-DM vocabulary, document helpers, and Graphviz/HTML rendering for FAIR-transformation provenance across PDSSP services.
# Copyright (C) 2026 - CNES (Jean-Christophe Malapert for PDSSP)
# This file is part of PDSSP Prov Toolkit <https://gitlab.cnes.fr/pdssp/pdssp_prov_toolkit>
# SPDX-License-Identifier: Apache-2.0

"""
PROV-DM / FOAF vocabulary.
============================
Plain string constants for the attribute keys, record-type values and
qualified-relation attribute names used throughout this toolkit's own
``document``/``dot`` modules, and by every service building a
:class:`~prov.model.ProvDocument` with them.

This is the union of the vocabulary independently grown by two PDSSP
services (``ode_stac_proxy`` and ``geocoding-api``) before this package
existed -- extracted here specifically because both had already drifted
from each other (one had gained ``PLAN``/``COLLECTION``/``IDENTIFIER``, the
other ``LICENSE``/``CRS``/``INFORMED``/``INFORMANT``) without either
noticing the other's additions. Nothing here is specific to either
service's own domain: a consumer is free to only ever use the subset it
needs.
"""

from __future__ import annotations


class ProvAttr:
    """PROV-DM (and FOAF) attribute keys used on records built by this
    toolkit (or by any caller building its own).
    """

    TYPE = "prov:type"
    LABEL = "prov:label"
    LOCATION = "prov:location"
    #: Custom attributes below (not part of PROV-DM's core vocabulary) all
    #: deliberately skip the ``prov:`` prefix -- that namespace is reserved
    #: for the fixed set of terms PROV-XML's schema actually knows, and a
    #: validator (ProvToolbox/ProvStore) rejects an unrecognized ``prov:*``
    #: element/attribute outright rather than treating it as an extension
    #: point. They use the ``pdssp:`` prefix instead (bound by
    #: :func:`~.document.new_document` to the same URI as the document's own
    #: default namespace) rather than being left bare: ``prov``'s own
    #: PROV-JSON-LD serializer never compacts an unprefixed term against
    #: ``@vocab``, so a bare extension attribute round-trips as a raw
    #: expanded IRI (e.g. ``"https://example.org/prov#license"``) -- which
    #: at least one real PROV-JSON-LD consumer (a Jackson-based
    #: ``Namespace.stringToQualifiedName()``) then fails to parse back,
    #: since it only recognises terms with an explicit prefix mapping in
    #: ``@context``, not ones relying on ``@vocab`` alone.
    VERSION = "pdssp:version"
    #: The identifier (e.g. a STAC item/collection id) an entity represents.
    IDENTIFIER = "pdssp:identifier"
    #: Machine-readable schema URL alongside a human-readable LOCATION.
    SCHEMA = "pdssp:schema"
    #: The license terms an entity is distributed/available under.
    LICENSE = "pdssp:license"
    #: The coordinate reference system an entity's geometry uses.
    CRS = "pdssp:crs"
    FOAF_NAME = "foaf:name"
    FOAF_HOMEPAGE = "foaf:homepage"


class ProvType:
    """PROV-DM record-type values used as a record's :data:`ProvAttr.TYPE`."""

    COLLECTION = "prov:Collection"
    ENTITY = "prov:Entity"
    ACTIVITY = "prov:Activity"
    PLAN = "prov:Plan"
    PERSON = "prov:Person"
    ORGANIZATION = "prov:Organization"
    SOFTWARE_AGENT = "prov:SoftwareAgent"


class ProvQualifier:
    """Lowercase ``formal_attributes`` keys naming the endpoints of
    ``prov``'s qualified n-ary relations (``ProvGeneration``, ``ProvUsage``,
    ``ProvDerivation``, ``ProvAssociation``, ``ProvAttribution``,
    ``ProvDelegation``, ``ProvMembership``, ``ProvCommunication``) --
    distinct from :class:`ProvAttr` (descriptive attributes on a record)
    and :class:`ProvType`'s capitalized record-type values.

    Consumed by :func:`~.dot.prov_to_dot` to draw each relation as a graph
    edge; a caller building relations via ``prov``'s own
    ``doc.wasGeneratedBy()``/``doc.used()``/... helpers never needs these
    directly (``prov`` sets the qualifiers internally) -- they matter only
    to code that reads a relation's ``formal_attributes`` back out, as
    :mod:`.dot` does.
    """

    ENTITY = "prov:entity"
    ACTIVITY = "prov:activity"
    AGENT = "prov:agent"
    PLAN = "prov:plan"
    GENERATED_ENTITY = "prov:generatedEntity"
    USED_ENTITY = "prov:usedEntity"
    DELEGATE = "prov:delegate"
    RESPONSIBLE = "prov:responsible"
    COLLECTION = "prov:collection"
    INFORMED = "prov:informed"
    INFORMANT = "prov:informant"
