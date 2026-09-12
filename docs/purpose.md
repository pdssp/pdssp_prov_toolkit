# Purpose of the Software

PDSSP Prov Toolkit provides the shared, FAIR-oriented W3C PROV-DM building blocks every PDSSP
service publishing a machine-readable provenance document needs: a PROV-DM/FOAF vocabulary,
a handful of domain-agnostic document helpers, and a Graphviz DOT + client-side HTML rendering
pipeline. It is a library, imported by a service's own `GET /prov`-style endpoint — never run on
its own.

## Intended Uses

- Building a [W3C PROV-DM](https://www.w3.org/TR/prov-dm/) document describing a FAIR-data
  transformation pipeline (harvest, mapping, compilation, ingestion, ...), with consistent
  attribute/type/qualifier naming across every PDSSP service that does this.
- Rendering that document as a Graphviz graph, and as a standalone interactive HTML page, without
  running a native `graphviz` binary or shipping a heavyweight plotting dependency.
- Serving a browser-friendly graph view alongside the raw PROV-JSON / PROV-N / PROV-XML
  serialisations (produced by `prov` itself, this package's own dependency) at the same endpoint.

## Key Capabilities

- **`vocab`** — `ProvAttr`, `ProvType`, `ProvQualifier`: plain string constants for every
  attribute key, record-type value, and qualified-relation attribute name used by the rest of
  this package (and by a consuming service's own document-assembly code).
- **`document`** — `new_document`, `slug`, `resolve_agent`: a namespaced empty
  `prov.model.ProvDocument`, a safe PROV local identifier from a free-text name, and
  de-duplicated agent lookup so the same real-world party is never recorded twice.
- **`dot`** — `prov_to_dot`: a `ProvDocument` to Graphviz DOT source, with the standard PROV-DM
  node shapes/colours and word-wrapped long labels/URLs.
- **`html`** — `render_prov_html`: a full standalone HTML page rendering that DOT source
  client-side via Viz.js (Subresource-Integrity-pinned), with no server-side `graphviz` binary.

## Benefits

- **One vocabulary, not N drifting copies.** A fix or an addition (a new relation kind, a new
  attribute) is made once and reaches every consuming service on its next dependency bump.
- **Zero opinion on a consumer's own pipeline shape.** Nothing here assumes "one plugin harvests
  a source" or "one batch job compiles a GeoPackage" — each service keeps that logic, built out
  of these primitives.
- **Minimal footprint.** A single runtime dependency (`prov`); no native binary, no heavyweight
  plotting library, no logging configuration imposed on the importing process.
