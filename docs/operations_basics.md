# Operations Basics

Not applicable in the usual sense: PDSSP Prov Toolkit has no operator role, no daily/scheduled
operations, and nothing to start, stop, or monitor — it is a library called by a consuming
service's own code, not a thing deployed and run on its own.

The closest equivalent "operational task" is a development one:

| # | Task | Role | Frequency |
|---|---|---|---|
| 1 | Bump the dependency in a consuming service (`uv add pdssp-prov-toolkit@<version>`) | Developer | Per release the consumer wants to pick up |
| 2 | Run this package's own test suite (`make tests`) before releasing a new version | Maintainer | Per change |

For how to actually *use* the library once it's installed, see the [Tutorial](tutorial.md).
