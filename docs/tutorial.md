# Tutorial

## Introduction

This tutorial walks through building a small W3C PROV-DM document with PDSSP Prov Toolkit,
rendering it as a Graphviz graph and as a standalone HTML page, and wiring that into a FastAPI
`GET /prov` endpoint the way `ode_stac_proxy` and `geocoding-api` actually do it. No prior
knowledge of PROV-DM is required, though the
[W3C PROV Primer](https://www.w3.org/TR/prov-primer/) is a good companion read.

---

## Getting Started

### Step 1 — Install

```bash
git clone https://gitlab.cnes.fr/pdssp/pdssp_prov_toolkit
cd pdssp_prov_toolkit && uv sync --no-dev
```

Or, as a dependency of your own project:

```bash
uv add pdssp-prov-toolkit
```

### Step 2 — Build a document

Every document starts from [`new_document`](reference_manual.md), which returns an empty,
correctly namespaced `prov.model.ProvDocument`:

```python
from pdssp_prov_toolkit import ProvAttr, ProvType, new_document

doc = new_document("https://example.org/api")

source = doc.entity(
    "source-data",
    {
        ProvAttr.TYPE: ProvType.COLLECTION,
        ProvAttr.LABEL: "Upstream dataset",
        ProvAttr.LOCATION: "https://example.org/source-archive",
    },
)
mapping = doc.activity(
    "mapping",
    other_attributes={
        ProvAttr.TYPE: ProvType.ACTIVITY,
        ProvAttr.LABEL: "Map the upstream archive onto the service's own data model",
    },
)
catalog = doc.entity(
    "catalog", {ProvAttr.TYPE: ProvType.COLLECTION, ProvAttr.LABEL: "Published catalog"}
)

doc.used(mapping, source)
doc.wasGeneratedBy(catalog, mapping)
doc.wasDerivedFrom(catalog, source)
```

Everything after `new_document` is plain `prov` API (`doc.entity`/`doc.activity`/`doc.agent`,
`doc.used`/`doc.wasGeneratedBy`/...) — `pdssp_prov_toolkit` only supplies the attribute keys
(`ProvAttr`) and type values (`ProvType`) so every PDSSP service spells them the same way.

### Step 3 — Render as a graph

```python
from pdssp_prov_toolkit import prov_to_dot

dot = prov_to_dot(doc)
print(dot)
```

```
digraph provenance {
  rankdir=LR;
  ...
  "source-data" [label="Upstream dataset\nhttps://example.org/source-archive", shape=ellipse, ...];
  "mapping" [label="Map the upstream archive onto the service's own data model", shape=box, ...];
  "catalog" [label="Published catalog", shape=ellipse, ...];
  "mapping" -> "source-data" [label="used", style=dashed];
  "catalog" -> "mapping" [label="wasGeneratedBy", style=solid];
  "catalog" -> "source-data" [label="wasDerivedFrom", style=solid];
}
```

(Abbreviated — the real output also includes the ``node``/``edge`` default-style lines and
every attribute Graphviz needs; see Step 5 below for what the graph looks like once an agent
is added.)

This is plain Graphviz DOT text — render it with the `dot` CLI, any Graphviz binding, or (as the
next step shows) client-side in a browser via Viz.js.

### Step 4 — Render as a standalone HTML page

```python
from pdssp_prov_toolkit import render_prov_html

page = render_prov_html(
    dot=dot,
    base="https://example.org/api",
    subtitle_html="How this service's catalog is produced, for the whole service.",
)
```

`page` is a complete, self-contained HTML document: it loads Viz.js from a pinned, Subresource
Integrity-checked CDN URL, embeds the DOT source safely, and renders it into an SVG in the
browser — no native `graphviz` binary, no server-side rendering step.

> **Escaping contract** — `subtitle_html` (and the optional `footer_extra_html`) are inserted
> **as-is**, not HTML-escaped by `render_prov_html`: build them with `html.escape()` on any
> dynamic part yourself, exactly as the Step 6 example below does. `dot` and `base`, by
> contrast, *are* escaped internally — pass them through unescaped.

### Step 5 — Attribute agents without duplicating them

[`resolve_agent`](reference_manual.md) returns an existing agent by name, or creates (and
remembers) a new one — useful when several entities might cite the same real-world organisation
or person. Continuing to build on the same `doc` from the previous steps:

```python
from pdssp_prov_toolkit import ProvType, resolve_agent

agents: dict = {}
producer = resolve_agent(doc, agents, "NASA Planetary Data System", ProvType.ORGANIZATION)
doc.wasAttributedTo(source, producer)

# Later, for a different entity citing the same organisation:
same_producer = resolve_agent(doc, agents, "NASA Planetary Data System", ProvType.ORGANIZATION)
assert same_producer is producer
```

Re-rendering with `prov_to_dot(doc)` now also draws the agent (an orange house, per the PROV-DM
colour convention) and its `wasAttributedTo` edge from `source-data`.

[`slug`](reference_manual.md) (used internally by `resolve_agent`) is also available directly,
for any other PROV-N/PROV-XML identifier a service builds from a free-text name:

```python
from pdssp_prov_toolkit import slug

slug("NASA PDS Geosciences Node")  # -> "nasa-pds-geosciences-node"
```

---

## Step 6 — Wire it into a FastAPI endpoint

This is how a consuming service actually uses this package end to end — content negotiation
between the machine-readable PROV-JSON/-N/-XML serialisations (produced by `prov` itself,
via `doc.serialize(format=...)`) and the human-facing graph view:

```python
from html import escape

from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import HTMLResponse
from pdssp_prov_toolkit import prov_to_dot, render_prov_html

router = APIRouter()

_MEDIA_TYPES = {"json": "application/json", "xml": "application/xml"}


@router.get("/prov")
async def get_prov(request: Request, format: str | None = Query(None), scope_id: str | None = None):
    base = str(request.base_url).rstrip("/")
    doc = build_my_own_prov_document(base, scope_id)  # your own service's assembly logic

    wants_html = format == "html" or (format is None and "text/html" in request.headers.get("accept", ""))
    if wants_html:
        scope_html = f"scoped to <code>{escape(scope_id)}</code>" if scope_id else "for the whole service"
        query_suffix = f"&scope_id={escape(scope_id)}" if scope_id else ""
        html = render_prov_html(
            dot=prov_to_dot(doc),
            base=base,
            subtitle_html=f"How this service's catalog is produced, {scope_html}.",
            query_suffix=query_suffix,
        )
        return HTMLResponse(content=html)

    resolved_format = format or "json"
    return Response(
        content=doc.serialize(format=resolved_format),
        media_type=_MEDIA_TYPES[resolved_format],
    )
```

`build_my_own_prov_document` is exactly the part this package deliberately leaves to each
service — see [Introduction](introduction.md#what-deliberately-stayed-out-of-this-package) for
why. For a real, complete example of this pattern (collection/item scoping, 404 handling,
`?format=` validation), see `ode_stac_proxy.ogc_api.prov`'s `make_prov_router` in the
`ode_stac_proxy` repository.
