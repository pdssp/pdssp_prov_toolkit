# PDSSP Prov Toolkit - Shared W3C PROV-DM vocabulary, document helpers, and Graphviz/HTML rendering for FAIR-transformation provenance across PDSSP services.
# Copyright (C) 2026 - CNES (Jean-Christophe Malapert for PDSSP)
# This file is part of PDSSP Prov Toolkit <https://gitlab.cnes.fr/pdssp/pdssp_prov_toolkit>
# SPDX-License-Identifier: Apache-2.0

"""
HTML graph visualisation for a ``GET /prov``-style endpoint.
===============================================================
When a browser navigates to a provenance endpoint, a graph is the most
legible representation of a PROV-DM document -- that is the whole point of
the diagrams in the W3C PROV Primer -- so :func:`render_prov_html` renders
one instead of raw PROV-JSON.

The Graphviz DOT source produced by :func:`~.dot.prov_to_dot` is rendered
into an SVG **client-side**, in the browser, via Viz.js (Graphviz compiled
to WebAssembly/asm.js, loaded from a CDN, pinned by version and by
Subresource Integrity hash so the CDN cannot silently swap in different
script content). No native ``graphviz`` binary runs on the server.

The SVG is shown at its native size inside a scrollable container, rather
than shrunk with CSS to fit the viewport width: a PROV graph with several
same-rank nodes is often wider or taller than one screen, and forcing it
to fit would shrink its text past legibility. Scrolling (or the browser's
own zoom) is the tradeoff that keeps the labels readable.

The page also links to the raw PROV-JSON / PROV-N / PROV-XML / PROV-JSON-LD
serialisations, which are plain, standard PROV-DM documents that can be
pasted or uploaded into ProvStore (https://openprovenance.org/store/) or
any other PROV-DM-compliant tool -- this page does not call out to
ProvStore itself, so nothing about a deployment using it is sent anywhere
without the operator choosing to do so.

Deliberately generic about *what* is being shown: :func:`render_prov_html`
takes an already-built *subtitle_html* fragment and *query_suffix* rather
than any scope-specific parameter name (a STAC ``collection_id``/``item_id``
pair, a gazetteer ``planet``, or anything a future consumer's own resource
model might add) -- building that scope-specific text/query-string is each
caller's own job (see the parameters' own docstrings for the escaping
contract).

**Security note**: the DOT source is embedded via a hidden, HTML-escaped
``<pre>`` element read back through ``.textContent`` in a *static* inline
script (see :func:`render_prov_html`), rather than interpolated directly
into a ``<script>`` block -- this sidesteps both HTML/JS string-escaping
pitfalls and the ``</script>`` early-termination issue, regardless of what
free-text labels end up in the DOT source.
"""

from __future__ import annotations

from html import escape

#: Pinned Viz.js release -- keep in lock-step with :data:`_VIZ_JS_SRI`/
#: :data:`_VIZ_FULL_RENDER_JS_SRI` below: bumping the version without
#: recomputing these hashes makes the browser refuse to run either script
#: at all (a safe, loud failure -- the graph just won't render -- rather
#: than a silent security regression).
_VIZ_JS_BASE = "https://cdn.jsdelivr.net/npm/viz.js@2.1.2"
_VIZ_JS_SRI = "sha384-f4dIboC5mwQKuVsNplQrKp19L8ttwIgw0LJNV0PsuIJYHTjIljdJ9cZdTqIVtk8y"
_VIZ_FULL_RENDER_JS_SRI = "sha384-oyiaz0P9mLALNbgQC9EQ48wxHRWGopFpDEMBoCc9Rir7gWL7GrgKzr4+X9mVM77b"


def render_prov_html(
    *,
    dot: str,
    base: str,
    subtitle_html: str,
    query_suffix: str = "",
    footer_extra_html: str = "",
) -> str:
    """Return the full HTML page visualising a PROV-DM document as a graph.

    Parameters
    ----------
    dot:
        Graphviz DOT source produced by :func:`~.dot.prov_to_dot`.
    base:
        Public base URL of the service, shown (HTML-escaped by this
        function) in the page title.
    subtitle_html:
        The page's subtitle, e.g. ``"How this service's STAC catalog is
        produced, scoped to collection <code>foo</code>."`` -- an
        already-safe HTML fragment built by the caller (any dynamic part,
        such as an id, must already be ``html.escape()``-d by the caller
        before it's wrapped in ``<code>...</code>``; this function does
        **not** escape it again, exactly like the caller's existing
        practice before this was extracted).
    query_suffix:
        An already-escaped, already-``&``-prefixed query-string suffix
        (e.g. ``"&collection_id=foo&item_id=bar"`` or ``"&planet=mars"``)
        appended to every format-switch link so re-fetching PROV-JSON/-N/-XML/
        JSON-LD preserves the same scope shown here. Empty string (default)
        for an unscoped, whole-catalog document.
    footer_extra_html:
        Extra HTML appended to the footer paragraph (e.g. a link to a
        human-readable licenses/citation page) -- already-safe HTML,
        same escaping contract as *subtitle_html*. Empty by default.

    Returns
    -------
    str
        A complete, standalone HTML document.
    """
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Provenance (PROV-DM) — {escape(base)}</title>
<script src="{_VIZ_JS_BASE}/viz.js" integrity="{_VIZ_JS_SRI}" crossorigin="anonymous"></script>
<script src="{_VIZ_JS_BASE}/full.render.js" integrity="{_VIZ_FULL_RENDER_JS_SRI}" crossorigin="anonymous"></script>
<style>
  :root {{ color-scheme: light dark; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    margin: 0; padding: 1.5rem 2rem; color: #1a1a1a; background: #fff;
  }}
  h1 {{ font-size: 1.15rem; margin: 0 0 0.25rem; }}
  p.sub {{ color: #666; margin: 0 0 1.25rem; font-size: 0.9rem; }}
  #graph {{ overflow: auto; max-height: 80vh; border: 1px solid #ddd; border-radius: 6px; padding: 0.5rem; background: #fafafa; }}
  #graph svg {{ display: block; }}
  .legend {{ display: flex; gap: 1.5rem; margin: 0 0 1rem; font-size: 0.85rem; flex-wrap: wrap; }}
  .swatch {{ display: inline-block; width: 0.9rem; height: 0.9rem; border-radius: 3px; margin-right: 0.35rem; vertical-align: -1px; }}
  .formats {{ margin-top: 1.25rem; font-size: 0.9rem; }}
  .formats a {{ margin-right: 1rem; }}
  footer {{ margin-top: 1.5rem; font-size: 0.8rem; color: #888; }}
  footer a {{ color: inherit; }}
  #error {{ color: #b00020; white-space: pre-wrap; font-family: ui-monospace, monospace; margin: 0; }}
</style>
</head>
<body>
<h1>W3C PROV-DM provenance</h1>
<p class="sub">{subtitle_html}</p>

<div class="legend">
  <span><span class="swatch" style="background:#FFFC87;border:1px solid #808080"></span>Entity</span>
  <span><span class="swatch" style="background:#9FB1FC;border:1px solid #0000FF"></span>Activity</span>
  <span><span class="swatch" style="background:#FED37F;border:1px solid #D2691E"></span>Agent</span>
  <span style="color:#888">Rendered at full size — scroll to see the whole graph.</span>
</div>

<div id="graph"><p id="error" hidden></p></div>

<pre id="dot-source" hidden>{escape(dot)}</pre>

<div class="formats">
  Machine-readable: <a href="?format=json{query_suffix}">PROV-JSON</a><a href="?format=provn{query_suffix}">PROV-N</a><a href="?format=xml{query_suffix}">PROV-XML</a><a href="?format=jsonld{query_suffix}">PROV-JSON-LD</a>
</div>

<footer>
  Rendered with the colour convention used throughout the PROV community (W3C PROV Primer,
  ProvStore, ProvToolbox). The PROV-JSON / PROV-N / PROV-XML / PROV-JSON-LD above are plain
  PROV-DM documents that can be pasted or uploaded into
  <a href="https://openprovenance.org/store/" target="_blank" rel="noopener noreferrer">ProvStore</a>
  or any other PROV-DM-compliant tool.{footer_extra_html}
</footer>

<script>
  var dotSource = document.getElementById('dot-source').textContent;
  new Viz().renderSVGElement(dotSource)
    .then(function (el) {{ document.getElementById('graph').appendChild(el); }})
    .catch(function (err) {{
      var e = document.getElementById('error');
      e.hidden = false;
      e.textContent = 'Graph rendering failed: ' + err;
    }});
</script>
</body>
</html>
"""
