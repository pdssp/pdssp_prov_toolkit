# Operations Environment

## General

PDSSP Prov Toolkit is a plain importable Python library, not a running service: it exposes no
HTTP server, no CLI, and no daemon of any kind. There is nothing to bind an address/port to and
nothing to keep alive. This page describes what an environment *using* it needs, not an
environment to "run" it in — there is no such thing.

## Software Configuration

The following must be present in whatever environment imports this package:

| Component | Version / Notes |
|---|---|
| Python | 3.12 or later |
| `prov` | 3.1.0 or later — this package's only runtime dependency |

Recommended installation, via [`uv`](https://docs.astral.sh/uv/):

```bash
uv add pdssp-prov-toolkit
```

## Hardware Configuration

Not applicable. This package allocates no persistent memory, opens no sockets, and writes no
files of its own — its resource footprint is whatever a few pure-Python function calls cost,
indistinguishable from the rest of the consuming process. There is no separate hardware sizing
question to answer beyond that of the service embedding it.

## Operational Constraints

- No constraint of its own. The only thing a caller must respect is each function's own
  parameter contract (see the [Reference Manual](reference_manual.md)) — e.g.
  `render_prov_html`'s `subtitle_html`/`footer_extra_html` must already be safe HTML when passed
  in, since this function does not escape them itself.
