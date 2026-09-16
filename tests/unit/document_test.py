# PDSSP Prov Toolkit - Shared W3C PROV-DM vocabulary, document helpers, and Graphviz/HTML rendering for FAIR-transformation provenance across PDSSP services.
# Copyright (C) 2026 - CNES (Jean-Christophe Malapert for PDSSP)
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for ``pdssp_prov_toolkit.document``.
"""

from __future__ import annotations

from prov.model import ProvDocument

from pdssp_prov_toolkit.document import FOAF_NS, new_document, resolve_agent, slug
from pdssp_prov_toolkit.vocab import ProvAttr, ProvType

BASE_URL = "https://example.org/api"


class TestNewDocument:
    def test_returns_a_prov_document(self):
        doc = new_document(BASE_URL)
        assert isinstance(doc, ProvDocument)

    def test_default_namespace_is_derived_from_base(self):
        doc = new_document(BASE_URL)
        entity = doc.entity("foo")
        assert entity.identifier.uri == f"{BASE_URL}/prov#foo"

    def test_foaf_namespace_is_registered(self):
        doc = new_document(BASE_URL)
        namespaces = {ns.prefix: ns.uri for ns in doc.get_registered_namespaces()}
        assert namespaces["foaf"] == FOAF_NS

    def test_custom_foaf_namespace_is_honoured(self):
        doc = new_document(BASE_URL, foaf_ns="https://example.org/foaf#")
        namespaces = {ns.prefix: ns.uri for ns in doc.get_registered_namespaces()}
        assert namespaces["foaf"] == "https://example.org/foaf#"

    def test_pdssp_namespace_is_registered_for_extension_attributes(self):
        # Same URI as the default namespace, but under an explicit prefix --
        # see ProvAttr's docstring: this is what lets its "pdssp:"-prefixed
        # extension attributes (license, crs, ...) round-trip through
        # PROV-JSON-LD instead of serializing as a raw expanded IRI.
        doc = new_document(BASE_URL)
        namespaces = {ns.prefix: ns.uri for ns in doc.get_registered_namespaces()}
        assert namespaces["pdssp"] == f"{BASE_URL}/prov#"

    def test_extension_attribute_compacts_in_jsonld_instead_of_expanding(self):
        doc = new_document(BASE_URL)
        doc.entity("item-1", {ProvAttr.LICENSE: "CC-BY-4.0"})
        serialized = doc.serialize(format="jsonld")
        assert '"pdssp:license"' in serialized
        assert f'"{BASE_URL}/prov#license"' not in serialized


class TestSlug:
    def test_lowercases_and_hyphenates(self):
        assert slug("NASA PDS Geosciences Node") == "nasa-pds-geosciences-node"

    def test_strips_leading_trailing_separators(self):
        assert slug("  Jean-Christophe Malapert  ") == "jean-christophe-malapert"

    def test_collapses_runs_of_non_alnum(self):
        assert slug("A///B   C") == "a-b-c"

    def test_empty_input_falls_back_to_agent(self):
        assert slug("") == "agent"
        assert slug("---") == "agent"


class TestResolveAgent:
    def test_creates_a_new_agent_when_absent(self):
        doc = new_document(BASE_URL)
        agents: dict = {}
        agent = resolve_agent(doc, agents, "Jean-Christophe Malapert", ProvType.PERSON)
        assert agents["Jean-Christophe Malapert"] is agent
        assert agent.get_attribute(ProvAttr.TYPE) == {ProvType.PERSON}
        assert agent.get_attribute(ProvAttr.LABEL) == {"Jean-Christophe Malapert"}
        assert agent.get_attribute(ProvAttr.FOAF_NAME) == {"Jean-Christophe Malapert"}

    def test_reuses_an_existing_agent_by_name(self):
        doc = new_document(BASE_URL)
        agents: dict = {}
        first = resolve_agent(doc, agents, "CNES", ProvType.ORGANIZATION)
        second = resolve_agent(doc, agents, "CNES", ProvType.PERSON)
        # Second call's prov_type is ignored -- the cached record wins, so
        # the same real-world party never gets a duplicate/conflicting record.
        assert first is second
        assert second.get_attribute(ProvAttr.TYPE) == {ProvType.ORGANIZATION}

    def test_slugifies_the_new_agent_identifier(self):
        doc = new_document(BASE_URL)
        agent = resolve_agent(doc, {}, "NASA PDS Geosciences Node", ProvType.ORGANIZATION)
        assert agent.identifier.localpart == "nasa-pds-geosciences-node"
