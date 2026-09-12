# Welcome to the PDSSP Prov Toolkit Documentation

**PDSSP Prov Toolkit** is a small, dependency-light Python library providing the
[W3C PROV-DM](https://www.w3.org/TR/prov-dm/) vocabulary, document-building helpers, and
Graphviz/HTML rendering shared by every PDSSP service that publishes a machine-readable
provenance document for its FAIR-transformed data.

It is not an application: it has no CLI, no server, and no configuration of its own — just a
handful of functions and constants that a consuming service (a live STAC proxy, a batch
GeoPackage-compilation pipeline, or anything similar) imports and builds its own `GET /prov`
endpoint on top of.

- New here? Start with [Purpose](purpose.md) and the [Tutorial](tutorial.md).
- Looking for a specific function or constant? See the [Reference Manual](reference_manual.md).
- Wondering why this exists instead of using `prov`'s own `prov[dot]` extra, or why the
  document-assembly logic isn't in here too? See [Introduction](introduction.md).
