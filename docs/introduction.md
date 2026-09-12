# Introduction

::: pdssp_prov_toolkit

## Purpose

This manual serves as a comprehensive resource for:

- Installation and Setup: Guiding you through the installation process.
- Features and Functionality: Explaining the core features and how to use them.
- Best Practices: Offering recommendations on where to draw the line between what belongs in
  this package and what belongs in a consuming service.
- Troubleshooting: Providing solutions to common issues.

## Context

Two PDSSP services expose a `GET /prov` endpoint describing, as a W3C PROV-DM document, how
their own FAIR-transformed data is produced:

- `ode_stac_proxy` — a live STAC API proxying the NASA PDS Orbital Data Explorer REST API.
- `geocoding-api` — an offline pipeline compiling planetary nomenclature/mission-site data
  into per-body GeoPackages and OpenSearch indices.

Both were built independently, before this package existed. By the time this package was
extracted, each had grown its own, already-drifted copy of the same PROV-DM vocabulary and the
same Graphviz/HTML rendering code:

- `geocoding-api` had added Subresource Integrity hashes pinning its Viz.js CDN scripts (a real
  security hardening) and `wasInformedBy`/`license`/`crs` support — none of which had made it
  back into `ode_stac_proxy`.
- `ode_stac_proxy` had added `hadMember`/`hadPlan` support — which had never made it into
  `geocoding-api`.

Neither service noticed the other's fixes, because there was nothing to notice: it was two
independent copies, not one shared dependency. This package is that one dependency — the union
of both, so a fix or an addition made once benefits every PDSSP service producing
FAIR-transformation provenance, present or future.

### What deliberately stayed out of this package

Each service's own document-*assembly* logic — which activities and entities its own pipeline
has, and how they connect — stays in that service. A live STAC proxy harvesting one upstream API
and a batch pipeline harvesting several static sources into per-body GeoPackages don't share a
pipeline shape, so a single "build me a document" helper here would fit neither well. What both
actually needed identically is the vocabulary they build records with, and the code that turns
the finished document into a graph — that is the whole scope of this package. See
[External View](external_view.md) for exactly where that boundary sits.

### Relationship to `prov`'s own `prov.dot`

This package depends on [`prov`](https://prov.readthedocs.io/), which already ships its own
optional Graphviz export (`prov.dot.prov_to_dot`, via the `prov[dot]` extra). Both use the same
node colours, because both independently follow the W3C PROV Primer / ProvToolbox convention —
but `prov[dot]` needs an extra dependency (`pydot`/`pyparsing`), doesn't word-wrap long
labels/URLs (the actual reason `pdssp_prov_toolkit.dot` exists — an unwrapped long value once
made a real graph too wide to read), and supports every PROV-DM relation/n-ary relation/bundle
rather than the curated subset PDSSP's own document builders ever produce. `prov[dot]` is the
better choice for a general-purpose PROV-DM visualiser; this package is narrower on purpose.
