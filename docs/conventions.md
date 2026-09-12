# Conventions

## Docstring Style

Every public function/class uses NumPy-style docstrings (`Parameters`/`Returns` sections), the
same convention `ode_stac_proxy` (this package's first consumer) already uses — `mkdocstrings`
renders them into the [Reference Manual](reference_manual.md) directly from source.

## Naming

| Convention | Meaning | Example |
|---|---|---|
| `PascalCase` class holding only constants | A namespaced vocabulary (never instantiated) | `ProvAttr`, `ProvType`, `ProvQualifier` |
| `snake_case` function | A plain, stateless transformation | `new_document`, `slug`, `prov_to_dot` |
| `UPPER_SNAKE_CASE` module-level constant | A single shared value, not a vocabulary | `FOAF_NS` |

## Typographic Conventions

| Convention | Meaning | Example |
|---|---|---|
| `Monospace` | Function, constant, file path, or code | `prov_to_dot` |
| *Italic* | Placeholder to be replaced by the caller | `<base>` |

## Admonitions

> **Note** — Notes provide supplementary information that is useful but not critical.

> **Warning** — Warnings describe a contract a caller must honour (e.g. `render_prov_html`'s
> escaping contract) to avoid a real defect, not just a stylistic preference.
