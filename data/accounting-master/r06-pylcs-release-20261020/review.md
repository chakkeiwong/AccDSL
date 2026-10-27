# Source-release review

The comparator is the retained exact Git snapshot and metadata-defined source
release, not latest against latest. The archive digest is checked before any
member content is used. Bounded decompression and an explicit member inventory
avoid both arbitrary path extraction and interpreting package code as commands.

Raw-file inequality is preserved. Only CRLF-to-LF produces complete equality;
byte-count differences exactly equal the removed CRLF counts. This qualification
is present in the result and live controls. No broader whitespace or Unicode
normalization conceals source changes. The source archive remains available
unchanged and selected text views preserve its exact bytes.

Build requirements are ranges, not resolved identities. The source recipe's
compiler probes and conditional options make source-to-binary transfer an
unproved step even with three matching files. PKG-INFO's missing Requires-Dist
field does not mean no dependencies: setup.py,pyproject.toml and egg metadata
provide separate declarations. Neither an upload date nor the unyanked flag
certifies a build, licence or downstream scientific result.

The complete archive inventory does not establish technical inspection of
every algorithm or legal clearance. The prior native read scope is retained;
this unit reads packaging/build metadata and compares complete file contents.
No new LCS arithmetic, implementation tests or performance run is needed to
answer a file-identity question. The local checks target the claimed equality
and provenance, not promotion by check count.

All protected state and unrelated dirty paths remain intact. The source/build
boundary leaves exact binary identity open without rejecting the research
direction. Independent technical/domain/human acceptance remains pending.
