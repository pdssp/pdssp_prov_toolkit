# PDSSP Prov Toolkit - Shared W3C PROV-DM vocabulary, document helpers, and Graphviz/HTML rendering for FAIR-transformation provenance across PDSSP services.
# Copyright (C) 2026 - CNES (Jean-Christophe Malapert for PDSSP)
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for ``pdssp_prov_toolkit.vocab``.

Mostly a change-detector: these are plain string constants read by
:mod:`pdssp_prov_toolkit.dot`, so an accidental rename here would silently
break rendering rather than raise -- pinning the exact values catches that.
"""

from __future__ import annotations

from pdssp_prov_toolkit.vocab import ProvAttr, ProvQualifier, ProvType


class TestProvAttr:
    def test_core_prov_keys_are_namespaced(self):
        assert ProvAttr.TYPE == "prov:type"
        assert ProvAttr.LABEL == "prov:label"
        assert ProvAttr.LOCATION == "prov:location"

    def test_extension_keys_use_the_pdssp_prefix_not_prov(self):
        # See the class docstring: a "prov:" prefix on a non-core-vocabulary
        # attribute breaks PROV-XML validation, and leaving it bare breaks
        # PROV-JSON-LD round-tripping -- "pdssp:" is the fix for both.
        for key in (
            ProvAttr.VERSION,
            ProvAttr.IDENTIFIER,
            ProvAttr.SCHEMA,
            ProvAttr.LICENSE,
            ProvAttr.CRS,
        ):
            assert not key.startswith("prov:")
            assert key.startswith("pdssp:")

    def test_foaf_keys_are_namespaced(self):
        assert ProvAttr.FOAF_NAME == "foaf:name"
        assert ProvAttr.FOAF_HOMEPAGE == "foaf:homepage"


class TestProvType:
    def test_values_are_capitalized_prov_terms(self):
        assert ProvType.ENTITY == "prov:Entity"
        assert ProvType.ACTIVITY == "prov:Activity"
        assert ProvType.PLAN == "prov:Plan"
        assert ProvType.COLLECTION == "prov:Collection"
        assert ProvType.PERSON == "prov:Person"
        assert ProvType.ORGANIZATION == "prov:Organization"
        assert ProvType.SOFTWARE_AGENT == "prov:SoftwareAgent"


class TestProvQualifier:
    def test_values_are_lowercase_prov_terms(self):
        for name, value in vars(ProvQualifier).items():
            if name.startswith("__"):
                continue
            assert value.startswith("prov:")
            assert value[len("prov:")].islower()

    def test_covers_every_relation_this_toolkit_draws(self):
        # One assertion per relation kind pdssp_prov_toolkit.dot actually
        # draws an edge for (see ProvDotConfig.RELATION_SPECS) -- a missing
        # qualifier here would silently drop that relation's edge.
        for name in (
            "ENTITY",
            "ACTIVITY",
            "AGENT",
            "PLAN",
            "GENERATED_ENTITY",
            "USED_ENTITY",
            "DELEGATE",
            "RESPONSIBLE",
            "COLLECTION",
            "INFORMED",
            "INFORMANT",
        ):
            assert hasattr(ProvQualifier, name)
