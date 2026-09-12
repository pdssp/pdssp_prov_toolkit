# Operations Manual

## General

Not applicable: PDSSP Prov Toolkit is a library, not a deployed service. There is no set-up,
launch configuration, session, or termination sequence of its own to document — importing it has
no side effects (it configures no logging, opens no connections, reads no configuration files),
and there is nothing left running afterwards to stop.

For installing and building on top of the library, see:

- [Tutorial](tutorial.md) — a worked example building, rendering, and serving a PROV-DM document.
- [Reference Manual](reference_manual.md) — the full function/constant reference.
- [Operations Environment](operations_environment.md) — what a consuming environment needs.

## Error Conditions

This package raises nothing of its own — see [Reference Manual § Errors](reference_manual.md#errors)
for the ordinary `prov`/Python exceptions a misuse can still surface, and each function's own
docstring for its exact contract.

## Troubleshooting

Nothing package-specific has come up yet. If `render_prov_html`'s graph fails to render in the
browser, check first whether the pinned Viz.js CDN URL
(`https://cdn.jsdelivr.net/npm/viz.js@2.1.2`) is reachable from the client and whether its
Subresource Integrity hash still matches — a version bump of that pin (in `html.py`) must update
both the URL and the two `integrity="sha384-..."` hashes together, or the browser will refuse to
run the (now mismatched) script.
