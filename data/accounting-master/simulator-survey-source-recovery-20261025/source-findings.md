# Source-recovery decisions

25 October 2026. The inspected bytes support the conclusions below. An access
failure blocks only the named source claim. It does not stop independent DSL
and simulator design work. No new accounting or empirical default is adopted.

## ACTUS

The official organization listing, userguides tree
`60234c1ea538115386421aec94ede4bcae0a94d4`, resources tree
`e8d8fc4df9a5d07bcb84646ef13ddb3c640215bb`, and service blobs are retained.
Four decoded Git blobs are checked against their Git SHA1 identities. The
installation page suggests a Python package; that does not identify the Java
core required by the inspected service. The resources tree supplies README
and logos. The already inspected service tree
`7293157a7f272925dbce68b5a037d2e23c585c9e` contains no matched core/submodule.
Its Dockerfile copies a local core, its README describes core 1.0.1, and its
Gradle file requests 1.1.0 through MavenCentral/MavenLocal. These facts do not
establish a single matched source release. The official developers page asks
for registration before reference-implementation access. None was attempted.
Earlier ordering, day-count and maturity mismatches remain open.

## Gentry (1974/1979) and Francis/Rowell (1978)

The 1974 Archive metadata and scan inventory match 52 included leaves to the
52-page retained PDF. Four excluded leaves are labeled Delete or Color Card.
Their images were not inspected; the metadata cannot conclusively locate or
exclude an appendix. Exact 1979 Crossref/OpenAlex metadata supplies no open
technical PDF. A publisher request returned an invalid-view response and the
corrected FULL request returned rate limiting. Neither is article evidence.

For Francis/Rowell, DOI 10.2307/3664904, the JSTOR HTTP 200 body is a JavaScript
challenge, not a paper. Exact-title metadata supplies no recovered PDF. The
unverified author-host route returned 403 HTML, retained with an HTML suffix.
Gentry/Hoque's 1990 discussion of the 1978 model is secondary characterization.
The 1978 technical model remains uninspected.

## Recovered distinct comparator

The university-contributed Archive scan of Gentry and Hoque (1990), working
paper 90-1694, was recovered from
https://archive.org/download/simultaneousequa1694gent/simultaneousequa1694gent.pdf.
It is 2,079,346 bytes, 46 pages, and matches the metadata SHA1
`0431938fc2c646d286ec1f5f73dc34f865b174af`. The initial transfer timed out
after 81,708 bytes; a resumed transfer completed the file and its digest was
checked. Illinois repository access returned 403. The working paper is retained
and technically inspected; see technical-reading.md for page-level findings.
No exact-author code was recovered. Blank built-in web results cannot establish
absence of code or sources.

## Access and reproducibility limits

JSON responses preserve their source URLs where available; the access register
records known routes and distinguishes successful content, metadata-only,
challenge/error and incomplete command provenance. Some earlier retrieval
commands are not saved verbatim. Their flags, durations and HTTP headers must
not be invented. Retained bytes, exact source identifiers and hashes support
this audit; the manifest labels that retrieval-log limitation explicitly.

No paid access, outreach, registration, dependency installation, external-code
execution, forecasting, publication or source-access circumvention occurred.
