# PDSSP Prov Toolkit

[![image](https://img.shields.io/badge/Maintained%3F-yes-green.svg)]()

![image]()

Shared W3C PROV-DM vocabulary, document helpers, and Graphviz/HTML rendering for FAIR-transformation provenance across PDSSP services.

## Why this exists

Two PDSSP services (`ode_stac_proxy`, a live STAC proxy, and
`geocoding-api`, an offline GeoPackage/OpenSearch pipeline) each expose a
`GET /prov` endpoint describing how their own FAIR-transformed data is
produced, as a W3C PROV-DM document. Both were built independently, before
this package existed — and by the time it was extracted, each had grown
its own, already-drifted copy of the same vocabulary and rendering code:

- `geocoding-api` had added Subresource Integrity hashes pinning its
  Viz.js CDN scripts (a real security hardening) and `wasInformedBy`/
  `license`/`crs` support — none of which had made it back into
  `ode_stac_proxy`.
- `ode_stac_proxy` had added `hadMember`/`hadPlan` support — which had
  never made it into `geocoding-api`.

Neither service noticed the other's fixes, because there was nothing to
notice — it was two copies, not one dependency. This package is that one
dependency: the union of both, so a fix or an addition made once benefits
every PDSSP service producing FAIR-transformation provenance, present or
future.

**What deliberately did *not* move here**: each service's own
document-assembly logic — *which* activities and entities its own
pipeline has, and how they connect — stays in that service. A STAC proxy
harvesting one live upstream and a batch pipeline harvesting several
static sources into per-body GeoPackages don't share a pipeline shape, so
forcing one here would fit neither well. What both actually needed
identically is the vocabulary they build records with and the code that
turns the finished document into a graph — that's the whole scope of this
package.

## Relationship to `prov`'s own `prov.dot`

This package depends on [`prov`](https://prov.readthedocs.io/), and `prov`
already ships its own optional Graphviz export
(`prov.dot.prov_to_dot`, via the `prov[dot]` extra) — doing, on paper, the
same job as `pdssp_prov_toolkit.dot`. They even use the *same* node
colours (`#FFFC87`/`#9FB1FC`/`#FED37F`), because both independently follow
the same W3C PROV Primer / ProvToolbox convention. So why not just use it?

| | `prov[dot]` | `pdssp_prov_toolkit.dot` |
|---|---|---|
| Extra dependency | `pydot` + `pyparsing` | none (plain string templating) |
| Long label/URL wrapping | no — a long value renders as one unbroken line | yes — this is *why* this module exists: an unwrapped long location once made a real graph too wide to read |
| Relation vocabulary | every PROV-DM relation, n-ary relations, nested bundles, attribute-annotation nodes | exactly the relations PDSSP's own document builders emit (Generation, Usage, Derivation, Association + `hadPlan`, Attribution, Delegation, Membership, Communication) — nothing else, because nothing else is ever produced |
| Output | a `pydot.Dot` object | a plain DOT string, ready for client-side rendering |
| HTML/Viz.js page | not provided | `pdssp_prov_toolkit.html.render_prov_html` — a full standalone page, SRI-pinned Viz.js, no server-side `graphviz` binary needed |

In short: `prov[dot]` is the right choice for a general-purpose PROV-DM
visualiser. This package is narrower on purpose — it only ever has to
render what PDSSP's own toolkit-built documents contain — and adds the
one thing that mattered enough in practice to justify not just calling
`prov[dot]` directly: readable graphs when a label or URL is long.

## Usage

```python
from pdssp_prov_toolkit import (
    ProvAttr,
    ProvType,
    new_document,
    prov_to_dot,
    render_prov_html,
    resolve_agent,
    slug,
)

doc = new_document("https://example.org/api")
source = doc.entity(
    "source-data",
    {ProvAttr.TYPE: ProvType.COLLECTION, ProvAttr.LABEL: "Upstream source"},
)
mapping = doc.activity(
    "mapping", other_attributes={ProvAttr.TYPE: ProvType.ACTIVITY, ProvAttr.LABEL: "Mapping"}
)
doc.used(mapping, source)

# A Graphviz DOT string, ready to render client-side (see render_prov_html)
# or with any Graphviz-compatible tool.
dot = prov_to_dot(doc)

# A full standalone HTML page rendering that graph via Viz.js.
page = render_prov_html(dot=dot, base="https://example.org/api", subtitle_html="Whole catalog.")
```

See each module's own docstring (`pdssp_prov_toolkit.vocab`,
`.document`, `.dot`, `.html`) for the full API.

## Installing UV

To manage the dependencies of PDSSP Prov Toolkit, we use
[UV](<https://docs.astral.sh/uv/>). If you don\'t have UV
installed, follow these steps:

1.  **Install UV**:

    > ``` shell
    > $ curl -LsSf https://astral.sh/uv/install.sh | sh
    > ```

2.  **Verify the installation**:

    > ``` console
    > $ uv --version
    > ```

Please note that this project has been tested with UV version 0.9.15.

## From sources

``` console
$ git clone https://gitlab.cnes.fr/pdssp/pdssp_prov_toolkit.git
$ cd pdssp_prov_toolkit
$ uv sync
```

## Development

``` console
$ git clone https://gitlab.cnes.fr/pdssp/pdssp_prov_toolkit.git
$ cd pdssp_prov_toolkit
$ make prepare-dev
$ source .venv/bin/activate
$ make install-dev
```

To get more information about the preconfigured tasks:

``` console
$ make help
```

## Run tests

``` console
$ make tests
```

## Documentation

The documentation is automatically deployed on
<https://pdssp.io.cnes.fr/>pdssp_prov_toolkit based on main branch

## Author

👤 **Jean-Christophe Malapert**

## 🤝 Contributing

Contributions, issues and feature requests are welcome!
Feel free to check [issues page](https://gitlab.cnes.fr/pdssp/pdssp_prov_toolkit/issues).
You can also take a look at the [contributing guide](https://gitlab.cnes.fr/pdssp/pdssp_prov_toolkit/blob/main/CONTRIBUTING.rst)

## 📝 License

This project is [Apache V2.0](https://gitlab.cnes.fr/pdssp/pdssp_prov_toolkit/blob/main/LICENSE) licensed.
