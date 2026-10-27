# Exact bytes differ; the comparison must retain that finding

The downloaded11,274-byte archive matches the retained PyPI SHA256. Its
bounded expansion is71,680 bytes with20 members. The three raw source-file
comparisons fail exact equality. A complete diff shows why: the release uses
CRLF while the pinned Git copies use LF. Replacing only CRLF with LF produces
equal bytes for all three files. No source spelling or other whitespace
change is hidden by that transformation.

Keep raw-byte inequality as the primary result. Report a separate declared
line-ending comparison; never relabel it as exact archive/Git identity or
universal compiler equivalence. This repair answers the original source
question more precisely without changing the protected comparator. No
additional acquisition, build or runtime test is needed.

The release contains a105-byte pyproject.toml declaring setuptools>=42 and
pybind11>=2.2 with setuptools.build_meta. Inspect this and the other small
packaging metadata; they may establish the build recipe but cannot identify
resolved headers,backend,compiler or a distributed binary. The complete
archive inventory is distinct from the source-manifest list, which may omit
generated package metadata. Record those differences explicitly.
