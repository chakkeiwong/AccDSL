# R06 native identity and notices: inspected source result

18 October 2026. P17/P19; MC23–25/27/30–35. Static source inspection only.
The comparator is the 16 October dependency frontier and the unchanged selected
Arelle/pdfplumber records and eleven documentary exchanges. pypdfium2 5.9.0
remains a lower-bound metadata witness, not a selected runtime version.

The exact PyPI source archive has SHA256
`db1274bd27844db6fda17ef1dbcd0026c47d357437058d838e98060c0da9e92e`
and 272,455 bytes. Twelve selected regular UTF-8 members are retained and
hash-bound. No package code was imported or executed. Source spans below are
relative to `sources/extracted/`; the machine findings bind their exact bytes.

## Findings and consequences

1. **The witness supplies a declared PDFium pin, not a binary identity.**
   `autorelease/record.json:1–5` names tag 5.9.0, PDFium 7869 and null
   `post_pdfium`. `setupsrc/base.py:346–352` resolves `pinned` by choosing
   `post_pdfium` or `pdfium`; `setupsrc/emplace.py:107–113` uses that pin when
   the prebuilt target has no version or requests `pinned`. A `latest` request
   takes a different route. These sources establish the normal prebuilt
   selection rule for this archive. They do not identify a downloaded binary,
   the full Chromium version, a wheel's payload or the library on this machine.

2. **Build mode and flags belong in the future lock.**
   `setupsrc/base.py:819–850` parses platform, optional subtarget, version and
   V8/XFA flags. `setupsrc/emplace.py:53–115` distinguishes system search or
   generated bindings, native/toolchained source builds, fallback and prebuilt
   targets. Fallback first searches for system PDFium, then may source-build;
   it is not an unconditional use of build 7869. `base.py:36–44` also declares
   separate tested sourcebuild constants 7841 and 7191. Their presence is not
   evidence that either builder executed or that a published wheel uses them.
   `pyproject.toml:24–42` configures sourcebuild modes for the wheel pipeline;
   actual wheel contents still require their own artifact inspection.

3. **Download provenance verification is conditional.**
   `setupsrc/update.py:31–52` constructs the release artifact from build,
   platform map and optional V8 prefix. `update.py:118–146` automatically
   requests attestation verification only for version at least 7557 with
   sufficiently recent `gh`; explicitly disabled verification returns after
   a warning. `update.py:158–173` downloads, verifies, then extracts. This is
   the inspected behavior, not an observed failure or successful verification.
   A future lock must retain the exact URL/bytes/digest and actual attestation
   outcome instead of inferring verification from package version or local
   tool availability. `emplace.py:19–40` compares cached build and flags;
   that check alone does not attest cached binary bytes.

4. **Version metadata is useful but insufficient.**
   `setupsrc/update.py:73–112` checks the archive VERSION build against the
   requested build and writes origin/flags. `base.py:362–376` records full
   version fields, origin, flags, optional hash and commit count; the latter
   two default to null and zero. These fields do not substitute for an exact
   binary digest, bindings digest and their verified correspondence. No full
   native version is guessed from build 7869 in this inquiry.

5. **System discovery has explicit unresolved and unsafe cases.**
   `setupsrc/system_pdfium.py:47–70` tries filename and pkg-config version
   information, otherwise returning NaN placeholders. Lines 113–163 try an
   explicit `PDFIUM_BINARY`, ctypes discovery and LibreOffice; known headers
   or versions select bindings, while neither leads to reference bindings
   with an ABI-unsafe warning. The LibreOffice branch warns that some APIs
   may be missing. Those are upstream warnings and static alternatives, not
   measurements of this environment. A future admitted system path needs
   resolved library identity, package provenance, headers and bindings; unknown
   versions cannot silently become a compatible-library result.

6. **The bindings have an independent provenance boundary.**
   `base.py:46–52` can select reference bindings through configuration or tool
   availability. `base.py:678–695` says reference reuse bypasses binding
   parameters and warns when its recorded pin differs from the requested
   version. `base.py:754–795` separately caches parameters, fetches headers and
   generates bindings. `pyproject.toml:4–12` declares setuptools, packaging,
   wheel exclusions and a ctypesgen Git revision
   `062a4ed4f3d6e205b8638fc1f22fa7ae50ad896d`. The three ordinary build-tool
   versions remain unselected. A future source-build record must preserve
   headers, binding bytes, generator identity, compiler/build configuration
   and the reference/generated choice. This is not transitive closure.

7. **Top-level Python metadata omits bundled component obligations.**
   `setup.py:65–72,84–108,134–152` separates helper/raw distributions and
   shared wrapper/documentation terms from mode-dependent BUILD_LICENSES.
   A normal combined distribution's empty initial `install_requires` does not
   establish the absence of native components. The helpers-only branch adds
   a raw-package dependency. Source-only/system paths and bundled native paths
   have different package-data and notice handling. `setup.py:21–49` assigns
   platform wheel tags; the Python ABI tag `none` does not mean native-library
   independence.

8. **The archive's notice inventory is not a reviewed component bill.**
   `README.md:920–944` distinguishes wrapper code, documentation, PDFium and
   dependency terms, requires binary-distribution notices and says the exact
   situation depends on the build, including possible libgcc linkage.
   `BUILD_LICENSES/pdfium.txt:1–27` contains PDFium's notice-retention,
   binary-reproduction and non-endorsement conditions. The file has additional
   text beyond that inspected prefix. `BUILD_LICENSES/pdfium-binaries.txt:1–9`
   retains its notice/permission and directs readers to third-party terms.
   `update.py:83–96` copies component notices for newer binary layouts and an
   aggregate notice for older ones. The source archive inventories 28
   BUILD_LICENSES members; only the two stated spans were inspected here.
   Neither 28 filenames nor the wrapper's permissive terms establishes all
   components, licences or distribution obligations for an eventual build.

## Remaining lock fields

| Layer | Fields still required before an admitted environment |
|---|---|
| Python distribution | Selected version, exact wheel/sdist digest and source, platform/interpreter tag, selected extras and complete resolved dependency graph |
| Native library | Mode/subtarget, full PDFium version and source revision, origin, flags, platform/architecture/libc, exact binary and any dependent runtime identities/digests |
| Generated or reference bindings | Binding/header digests and versions, ctypesgen revision and complete build tools, configuration and verified library correspondence |
| Provenance and repeatability | Actual download/build/cache path, recorded attestation and digest results, deterministic replay inputs or explicit unknowns |
| Component terms | Build-specific component bill, retained exact notices/terms and applicable obligations, including linked runtimes and documentation where distributed |
| Behavior | Separately authorised compatibility, field-loss/fallback and downstream adapter evidence; a static lock cannot supply these results |

No fields above are silently populated from this machine. Sourcebuild internals,
all component terms and the contents of actual wheels/binaries are not fully
reviewed. They remain preparation tasks for a specific proposed environment.

## Decision and manuscript disposition

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Deliver this bounded static supplement | Each finding has inspected source spans and actionable remaining fields | Archive, excerpts and protected-input checks must pass | Actual platform/build and complete component bill are unselected | Bind the note and refresh R06; continue independent manuscript reading | Runtime compatibility, legal clearance or dependency closure |
| Keep manuscript 3.44 unchanged | Its unresolved dependency/native/terms description remains accurate | No confirmed manuscript contradiction found | Full future environment and actual distribution | Use this supplement when a concrete lock is proposed | New source selection, implementation or full requirement closure |

Post-review red team: a future wheel could use a different PDFium source build
from the source archive's normal prebuilt pin. The decisive overturning evidence
would be inspection of that exact wheel/build and its component records. The
weakest boundary here is the deliberately uninspected native payload and wider
component terms; the note does not fill it by extrapolation. No stochastic
comparison applies. Independent technical/domain/human acceptance stays pending.
