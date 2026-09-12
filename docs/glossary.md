# Terms, Definitions and Abbreviated Terms

| Term | Definition |
|---|---|
| PROV-DM | [W3C PROV Data Model](https://www.w3.org/TR/prov-dm/) — the abstract model this package's vocabulary and document helpers implement: entities, activities, agents, and the relations between them. |
| PROV-JSON / PROV-N / PROV-XML | The three standard machine-readable serialisations of a PROV-DM document, produced by `prov.model.ProvDocument.serialize(format=...)` — not by this package, which only builds the document and renders it as a graph. |
| FAIR | Findable, Accessible, Interoperable, Reusable — the data principles a PDSSP service's own `GET /prov` endpoint (built with this package) exists to support, by making a dataset's provenance itself machine-readable. |
| Entity | A PROV-DM record representing a piece of data (`ProvType.ENTITY`/`COLLECTION`) — something that was generated, used, or derived. |
| Activity | A PROV-DM record representing something that happened over time (`ProvType.ACTIVITY`) and produced or consumed entities. |
| Agent | A PROV-DM record representing who or what bears responsibility (`ProvType.PERSON`/`ORGANIZATION`/`SOFTWARE_AGENT`). |
| Qualifier | The lowercase `formal_attributes` key naming one endpoint of a qualified PROV-DM relation (e.g. `prov:entity`, `prov:activity`) — see `ProvQualifier`; distinct from a record's own descriptive attributes (`ProvAttr`). |
| DOT | The [Graphviz](https://graphviz.org/doc/info/lang.html) graph-description language — the text format `prov_to_dot` produces. |
| Viz.js | A WebAssembly/asm.js build of Graphviz, run entirely client-side in the browser by the page `render_prov_html` returns — no server-side `graphviz` binary needed. |
| SRI | Subresource Integrity — the `integrity="sha384-..."` HTML attribute pinning a CDN script to an exact, verified content hash, used by `render_prov_html` for the Viz.js scripts it loads. |
| STAC | SpatioTemporal Asset Catalog — the data model `ode_stac_proxy` (this package's first consumer) serves; irrelevant to this package itself, which has no STAC-specific concept. |
| CNES | Centre National d'Études Spatiales. |
| PDSSP | Planetary Data System Service Platform. |
