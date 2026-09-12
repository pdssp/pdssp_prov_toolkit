# PDSSP Prov Toolkit - Shared W3C PROV-DM vocabulary, document helpers, and Graphviz/HTML rendering for FAIR-transformation provenance across PDSSP services.
# Copyright (C) 2026 - CNES (Jean-Christophe Malapert for PDSSP)
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for ``pdssp_prov_toolkit.dot``.

Builds small, self-contained :class:`~prov.model.ProvDocument` fixtures by
hand (no dependency on any consuming service's own document-building
code) and asserts on the rendered DOT source.
"""

from __future__ import annotations

from pdssp_prov_toolkit.document import new_document
from pdssp_prov_toolkit.dot import prov_to_dot
from pdssp_prov_toolkit.vocab import ProvAttr, ProvType

BASE_URL = "https://example.org/api"


def _pipeline_document() -> tuple:
    """One entity, one activity, one agent, wired by every relation kind
    :mod:`pdssp_prov_toolkit.dot` knows how to draw except Membership/
    Communication/hadPlan (covered by their own dedicated fixtures below).

    Returns
    -------
    tuple
        ``(doc, source, mapping, agent)``.
    """
    doc = new_document(BASE_URL)
    source = doc.entity(
        "source-data",
        {ProvAttr.TYPE: ProvType.COLLECTION, ProvAttr.LABEL: "Upstream source"},
    )
    catalog = doc.entity("catalog", {ProvAttr.TYPE: ProvType.COLLECTION, ProvAttr.LABEL: "Catalog"})
    mapping = doc.activity(
        "mapping", other_attributes={ProvAttr.TYPE: ProvType.ACTIVITY, ProvAttr.LABEL: "Mapping"}
    )
    agent = doc.agent(
        "agent", {ProvAttr.TYPE: ProvType.SOFTWARE_AGENT, ProvAttr.LABEL: "Agent"}
    )
    doc.used(mapping, source)
    doc.wasGeneratedBy(catalog, mapping)
    doc.wasDerivedFrom(catalog, source)
    doc.wasAssociatedWith(mapping, agent)
    doc.wasAttributedTo(source, agent)
    return doc, source, catalog, mapping, agent


class TestPrimaryShape:
    def test_is_a_digraph(self):
        doc, *_ = _pipeline_document()
        dot = prov_to_dot(doc)
        assert dot.startswith("digraph provenance {")
        assert dot.rstrip().endswith("}")

    def test_entities_styled_yellow_ellipse(self):
        doc, *_ = _pipeline_document()
        dot = prov_to_dot(doc)
        assert '"source-data" [label=' in dot
        assert "shape=ellipse" in dot
        assert "#FFFC87" in dot

    def test_activities_styled_blue_box(self):
        doc, *_ = _pipeline_document()
        dot = prov_to_dot(doc)
        assert '"mapping" [label=' in dot
        assert "shape=box" in dot
        assert "#9FB1FC" in dot

    def test_agents_styled_orange_house(self):
        doc, *_ = _pipeline_document()
        dot = prov_to_dot(doc)
        assert '"agent" [label=' in dot
        assert "shape=house" in dot
        assert "#FED37F" in dot


class TestRelationEdges:
    def test_generation_usage_derivation(self):
        doc, *_ = _pipeline_document()
        dot = prov_to_dot(doc)
        assert '"mapping" -> "source-data" [label="used"' in dot
        assert '"catalog" -> "mapping" [label="wasGeneratedBy"' in dot
        assert '"catalog" -> "source-data" [label="wasDerivedFrom"' in dot

    def test_association_and_attribution(self):
        doc, *_ = _pipeline_document()
        dot = prov_to_dot(doc)
        assert '"mapping" -> "agent" [label="wasAssociatedWith"' in dot
        assert '"source-data" -> "agent" [label="wasAttributedTo"' in dot

    def test_delegation(self):
        doc = new_document(BASE_URL)
        delegate = doc.agent("delegate", {ProvAttr.TYPE: ProvType.SOFTWARE_AGENT})
        responsible = doc.agent("responsible", {ProvAttr.TYPE: ProvType.ORGANIZATION})
        doc.actedOnBehalfOf(delegate, responsible)
        dot = prov_to_dot(doc)
        assert '"delegate" -> "responsible" [label="actedOnBehalfOf"' in dot

    def test_membership(self):
        doc = new_document(BASE_URL)
        catalog = doc.entity("catalog", {ProvAttr.TYPE: ProvType.COLLECTION})
        item = doc.entity("item", {ProvAttr.TYPE: ProvType.ENTITY})
        doc.hadMember(catalog, item)
        dot = prov_to_dot(doc)
        assert '"catalog" -> "item" [label="hadMember"' in dot

    def test_communication(self):
        doc = new_document(BASE_URL)
        informant = doc.activity("harvest", other_attributes={ProvAttr.TYPE: ProvType.ACTIVITY})
        informed = doc.activity("compile", other_attributes={ProvAttr.TYPE: ProvType.ACTIVITY})
        doc.wasInformedBy(informed, informant)
        dot = prov_to_dot(doc)
        assert '"compile" -> "harvest" [label="wasInformedBy"' in dot

    def test_had_plan_edge_only_when_association_names_one(self):
        doc = new_document(BASE_URL)
        mapping = doc.activity("mapping", other_attributes={ProvAttr.TYPE: ProvType.ACTIVITY})
        agent = doc.agent("agent", {ProvAttr.TYPE: ProvType.SOFTWARE_AGENT})
        plan = doc.entity("data-model-spec", {ProvAttr.TYPE: ProvType.PLAN})
        doc.wasAssociatedWith(mapping, agent, plan=plan)
        dot = prov_to_dot(doc)
        assert '"mapping" -> "data-model-spec" [label="hadPlan"' in dot

    def test_no_had_plan_edge_when_association_has_no_plan(self):
        doc, *_ = _pipeline_document()
        dot = prov_to_dot(doc)
        assert "hadPlan" not in dot


class TestLabelLines:
    def test_falls_back_to_identifier_when_no_label(self):
        doc = new_document(BASE_URL)
        doc.entity("unlabelled", {ProvAttr.TYPE: ProvType.ENTITY})
        dot = prov_to_dot(doc)
        assert '"unlabelled" [label="unlabelled"' in dot

    def test_version_shown_as_extra_line(self):
        doc = new_document(BASE_URL)
        doc.agent(
            "agent",
            {ProvAttr.TYPE: ProvType.SOFTWARE_AGENT, ProvAttr.LABEL: "Agent", ProvAttr.VERSION: "1.2.3"},
        )
        dot = prov_to_dot(doc)
        assert 'label="Agent\\nv1.2.3"' in dot

    def test_identifier_license_crs_shown_as_extra_lines(self):
        doc = new_document(BASE_URL)
        doc.entity(
            "item-1",
            {
                ProvAttr.TYPE: ProvType.ENTITY,
                ProvAttr.LABEL: "Item 1",
                ProvAttr.IDENTIFIER: "item-1",
                ProvAttr.LICENSE: "CC BY 4.0",
                ProvAttr.CRS: "IAU:2015:49900",
            },
        )
        dot = prov_to_dot(doc)
        assert 'label="Item 1\\nid: item-1\\nlicense: CC BY 4.0\\ncrs: IAU:2015:49900"' in dot

    def test_long_label_is_word_wrapped(self):
        doc = new_document(BASE_URL)
        long_label = "A very long human-readable label meant to exceed the wrap width by a fair bit"
        doc.entity("e", {ProvAttr.TYPE: ProvType.ENTITY, ProvAttr.LABEL: long_label})
        dot = prov_to_dot(doc)
        assert "\\n" in dot
        assert long_label not in dot  # split across at least two lines

    def test_long_location_is_hard_wrapped_preferring_separators(self):
        doc = new_document(BASE_URL)
        long_url = "https://example.org/a/very/long/path/that/exceeds/the/wrap/width/for/sure"
        doc.entity(
            "e", {ProvAttr.TYPE: ProvType.ENTITY, ProvAttr.LABEL: "E", ProvAttr.LOCATION: long_url}
        )
        dot = prov_to_dot(doc)
        assert "\\n" in dot
        # Each wrapped chunk still ends right after a "/" (its own preferred
        # break point), not mid-path -- reassembling the label's lines
        # around the "\n" join must reproduce the original URL exactly.
        label_line = next(line for line in dot.splitlines() if '"e" [label=' in line)
        rejoined = label_line.split('label="', 1)[1].split('", ', 1)[0].replace("\\n", "")
        assert rejoined.endswith(long_url)


class TestEscaping:
    def test_quotes_and_backslashes_are_escaped_in_labels(self):
        doc = new_document(BASE_URL)
        doc.entity("e", {ProvAttr.TYPE: ProvType.ENTITY, ProvAttr.LABEL: 'Say "hi"\\bye'})
        dot = prov_to_dot(doc)
        assert '\\"hi\\"' in dot
        assert "\\\\bye" in dot
