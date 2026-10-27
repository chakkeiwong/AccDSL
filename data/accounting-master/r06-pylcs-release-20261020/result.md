# pylcs0.1.1 source release versus inspected Git files

20 October2026. R06/R04; P15/P17/P19; MC23/24/26/29/30/31/33–35.

The published source archive is now identified and retained. Its three selected
source files agree with the previously inspected Git files after converting
CRLF to LF. Their raw bytes are different. This narrows the release/source
gap while leaving compiled and installed identities unverified.

The single acquisition followed the exact retained PyPI metadata URL and
returned HTTP200 with no redirect. The11,274-byte archive matches SHA256
632c69235d77cda0ba524d82796878801d2f46131fc59e730c98767fc4ce1307.
The retained metadata dates the upload to24October2023 and marks it unyanked;
no fresh latest-version or yanked-status query was made. Bounded decompression
produced71,680 bytes containing20 members,15 regular files and five directories.
Paths and member types passed the declared guard; no link or special file was
admitted. No archive path was extracted through extractall.

| Complete file | Release bytes | Pinned Git bytes | CRLF pairs removed | Raw equality | After CRLF-to-LF |
|---|---:|---:|---:|---|---|
| src/main.cpp | 12,231 | 11,873 | 358 | Different | Equal |
| pylcs/__init__.py | 2,628 | 2,567 | 61 | Different | Equal |
| setup.py | 3,338 | 3,232 | 106 | Different | Equal |

The Git comparator remains5eee78a655fbe34ef24c8240304646f7cd07543b, with the
predecessor's exact source/tree bindings. The transformation removes only CR
immediately before LF. There are no lone CR bytes and no other differences in
these three complete files. This is a specified textual equivalence, not an
assertion that the source archive equals a whole repository or any binary.
The previously read LCS and binding spans can therefore be located in this
source release with that explicit line-ending qualification. The earlier
native reading scope remains unchanged; other native functions are not newly
certified by a whole-file comparison.

The release's pyproject.toml declares setuptools.build_meta with
setuptools>=42 and pybind11>=2.2. setup.py also declares pybind11>=2.2, as
does egg-info/requires.txt. PKG-INFO identifies version0.1.1 but contains no
Requires-Dist field; this does not erase the separately present dependency
declarations. Both PKG-INFO copies are byte-identical. The source manifest
lists13 paths, all present; the two additional regular files are generated
PKG-INFO and setup.cfg. The inventory has no bundled pybind11 headers or
native binary.

Complete setup.py reading shows environmental build choices: it obtains
pybind11 include paths from the installed build dependency, prefers C++14
when the compiler probe accepts it, falls back to C++11, conditionally enables
hidden visibility and uses platform/compiler-specific options. The small
setup.cfg supplies egg-info tags, not resolved dependency versions. None of
these sources identifies the actual backend, headers, compiler, ABI or flags
used to build a released wheel. Neither prior pybind11 snapshot is promoted
to the actual pylcs build version.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain exact source-release identity | Metadata digest,size and actual response agree | Archive/path/budget checks pass | Snapshot status may change later | Preserve raw source archive and receipts | Current installation or wheel provenance |
| Narrow three-file source correspondence | Complete equality after the declared CRLF conversion | Raw identity claim rejected explicitly | Uncompared members and native environment | Carry forward only the scoped source account | Whole-repository or compiler equivalence |
| Keep native build identity open | Build metadata contains ranges and conditional options | Missing build attestation vetoes that claim | Resolved pybind11,compiler,backend and ABI | Keep runtime held; inspect the independent version-bounded dispatcher question | Installed correctness,performance or downstream financial validity |

One source acquisition,14 excerpt anchors and26 source bindings support the
record. No upstream code, tests, compiler, build backend or package import
executed. Local read-only checks confirm the archive, comparisons and exact
text views. There is no stochastic comparison or empirical ranking. Six
additive ledgers and an R08 supplement retain all53 obligations,six
interactions and46 operations with zero whole-row closures;3.44 remains
396 pages/not_ready and the manuscript is unchanged.

Post-run red team: identical source can produce different native behavior
through build dependencies and platform choices. Actual wheel build evidence
and a separately authorised installed-runtime check would be needed to bridge
that gap. This result establishes the source account only, so it does not
invalidate the method or fire a global continuation veto. Safe future replay
is verify.py without flags; completed stages remain immutable.
