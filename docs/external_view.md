# External View of the Software

This section describes the files this package consists of and what a consuming service actually
depends on — there is no server, no persistent process, and no data of its own to describe.

## Software Files

| File / Module | Type | Description |
|---|---|---|
| `pdssp_prov_toolkit/vocab.py` | Python module | `ProvAttr`, `ProvType`, `ProvQualifier` — PROV-DM/FOAF constants. No dependencies of its own. |
| `pdssp_prov_toolkit/document.py` | Python module | `new_document`, `slug`, `resolve_agent`. Depends on `vocab` and `prov`. |
| `pdssp_prov_toolkit/dot.py` | Python module | `prov_to_dot`. Depends on `vocab` and `prov`. |
| `pdssp_prov_toolkit/html.py` | Python module | `render_prov_html`. Depends on nothing else in this package (only the standard library's `html.escape`). |
| `pdssp_prov_toolkit/__init__.py` | Python module | Re-exports the public API of the four modules above, plus package metadata (`__version__`, ...). |

```
vocab  <───────────┐
  ▲                 │
  │                 │
document          dot          html
```

`document` and `dot` both depend on `vocab`; `html` depends on nothing internal. Nothing in this
package imports `document`/`dot`/`html` from one another — a consumer that only needs the
vocabulary, or only the HTML rendering, pays for exactly that and nothing else.

## External Dependencies

| Dependency | Purpose |
|---|---|
| [`prov`](https://pypi.org/project/prov/) `>=3.1.0` | The W3C PROV-DM data model itself (`ProvDocument` and friends) — this package's only runtime dependency. |

At runtime, `pdssp_prov_toolkit.html.render_prov_html` also references a CDN-hosted script
(`https://cdn.jsdelivr.net/npm/viz.js@2.1.2`, pinned by version and Subresource Integrity hash)
from the HTML page it returns — that script is loaded by the *browser* viewing the page, not by
the Python process producing it; nothing this package does itself reaches the network.

## Security and Privacy Considerations

- This package performs no I/O of its own: no file access, no network calls, no environment
  variable reads. Every function is a pure transformation of its arguments.
- `render_prov_html` HTML-escapes the DOT source and the base URL it is given; it does **not**
  escape `subtitle_html`/`footer_extra_html` a second time — see the
  [Tutorial](tutorial.md)'s escaping contract for what a caller must do before passing them in.
- The CDN script URLs baked into `render_prov_html`'s output are pinned to an exact version and
  checked via Subresource Integrity (`integrity="sha384-..."`), so a compromised or altered CDN
  response is rejected by the browser rather than silently executed.

## Emergency Continuity

Not applicable: this package has no running process of its own to recover. A consuming service
experiencing an error while using it (e.g. a malformed identifier raising a `prov` exception)
handles that exactly as it would any other library call failing — see that service's own
operational documentation.
