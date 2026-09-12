# PDSSP Prov Toolkit - Shared W3C PROV-DM vocabulary, document helpers, and Graphviz/HTML rendering for FAIR-transformation provenance across PDSSP services.
# Copyright (C) 2026 - CNES (Jean-Christophe Malapert for PDSSP)
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for ``pdssp_prov_toolkit.html``.
"""

from __future__ import annotations

from pdssp_prov_toolkit.html import render_prov_html

BASE_URL = "https://example.org/api"


class TestRenderProvHtml:
    def test_returns_a_full_html_document(self):
        page = render_prov_html(dot="digraph provenance {}", base=BASE_URL, subtitle_html="Whole catalog.")
        assert page.startswith("<!doctype html>")
        assert page.rstrip().endswith("</html>")

    def test_base_is_escaped_in_title(self):
        page = render_prov_html(
            dot="digraph provenance {}",
            base="https://example.org/<script>",
            subtitle_html="x",
        )
        assert "<script>" not in page.split("<title>")[1].split("</title>")[0]

    def test_dot_source_is_escaped_and_embedded_as_hidden_pre(self):
        dot = 'digraph provenance { "a" [label="<script>alert(1)</script>"]; }'
        page = render_prov_html(dot=dot, base=BASE_URL, subtitle_html="x")
        assert '<pre id="dot-source" hidden>' in page
        assert "<script>alert(1)</script>" not in page
        assert "&lt;script&gt;" in page

    def test_subtitle_html_passed_through_unescaped(self):
        # subtitle_html is a caller-built, already-safe fragment -- this
        # function must not escape it a second time.
        page = render_prov_html(
            dot="digraph provenance {}",
            base=BASE_URL,
            subtitle_html='scoped to collection <code>ctx</code>',
        )
        assert "scoped to collection <code>ctx</code>" in page

    def test_query_suffix_appended_to_format_links(self):
        page = render_prov_html(
            dot="digraph provenance {}",
            base=BASE_URL,
            subtitle_html="x",
            query_suffix="&collection_id=ctx",
        )
        assert '?format=json&collection_id=ctx' in page
        assert '?format=provn&collection_id=ctx' in page
        assert '?format=xml&collection_id=ctx' in page

    def test_no_query_suffix_by_default(self):
        page = render_prov_html(dot="digraph provenance {}", base=BASE_URL, subtitle_html="x")
        assert '?format=json"' in page

    def test_footer_extra_html_appended(self):
        page = render_prov_html(
            dot="digraph provenance {}",
            base=BASE_URL,
            subtitle_html="x",
            footer_extra_html=' See also <a href="/#licenses">licenses</a>.',
        )
        assert 'See also <a href="/#licenses">licenses</a>.' in page

    def test_viz_js_is_pinned_with_integrity_hash(self):
        page = render_prov_html(dot="digraph provenance {}", base=BASE_URL, subtitle_html="x")
        assert "viz.js@2.1.2/viz.js" in page
        assert 'integrity="sha384-' in page
        assert 'crossorigin="anonymous"' in page

    def test_legend_lists_the_three_prov_dm_shapes(self):
        page = render_prov_html(dot="digraph provenance {}", base=BASE_URL, subtitle_html="x")
        assert "Entity" in page
        assert "Activity" in page
        assert "Agent" in page
