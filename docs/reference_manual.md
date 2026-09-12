# Reference Manual

## Introduction

Complete API reference for PDSSP Prov Toolkit, generated from the source docstrings. There is
no command-line interface — this is a library, imported by a consuming service.

## Public API

Everything below is importable directly from the top-level package
(`from pdssp_prov_toolkit import ...`) as well as from its own module.

### `vocab` — PROV-DM / FOAF vocabulary

::: pdssp_prov_toolkit.vocab

### `document` — Generic PROV-DM document helpers

::: pdssp_prov_toolkit.document

### `dot` — Graphviz (DOT) rendering

::: pdssp_prov_toolkit.dot

### `html` — HTML graph visualisation

::: pdssp_prov_toolkit.html

## Errors

None of the functions above raise an exception type specific to this package. `resolve_agent`
and the `dot`/`html` functions never raise on their own; a caller can still hit ordinary `prov`
exceptions (e.g. `prov.model.ProvExceptionInvalidQualifiedName` from a malformed identifier
passed to `new_document`/`doc.entity`/...) or plain Python errors (e.g. a missing dict key)
from misuse — see each function's own docstring for its exact parameter contract.
