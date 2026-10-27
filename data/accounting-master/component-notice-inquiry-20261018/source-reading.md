# R06 component-notice text findings

18 October 2026. P17/P19, R06/R08; MC23–25/27/30–35.
Five complete source-archive texts were inspected, representing four component
families. Their exact bytes and the cited line spans are bound in
`source-manifest.json`. Paths below are relative to this directory's `sources/`.
This is internal documentary preparation, not a legal opinion or a finding
about the components present in any selected wheel, native binary or system.

The comparator is the preserved native-boundary inquiry. Its source archive
has SHA256 db1274bd27844db6fda17ef1dbcd0026c47d357437058d838e98060c0da9e92e.
pypdfium2 5.9.0 is still a lower-bound witness, and PDFium 7869 is still its
normal prebuilt selection rule, not a chosen runtime identity. The prior 28
filenames remain an inventory. This supplement adds full text inspection of
five of those files; it does not backdate that inspection or complete the other 23.

## Source wording and conditional consequences

**FreeType.** `freetype.txt:19–22,65–82` limits this licence to files without
their own explicit licence; compiling and linking fall within its definition
of use. The explicit uncertainty/contact instruction at 81–82 is retained as
an unresolved applicability condition, not authority to contact anyone.
`101–125` grants rights subject to conditions: source redistribution retains
FTL.TXT unaltered, preserves original copyright notices and identifies file
changes in accompanying documentation; binary redistribution provides the
stated FreeType Team acknowledgment/disclaimer in distribution documentation.
`130–145` restricts promotional use of the parties' names without permission.
The suggested credit at 46–56 is encouraged wording, with the year taken from
the actual version; the web URL at 119–120 is explicitly optional. The future
build record therefore needs actual FreeType version/files, chosen applicable
terms, modifications and separate source/binary notice destinations. This
archive does not establish those facts or exclude other file-specific terms.
The complete 169-line inspection used a lossless Latin-1 view for the copyright
glyph; the raw bytes were never transcoded or replaced.

**libjpeg-turbo scope and two texts.** `libjpeg_turbo.md:4–22` assigns IJG terms
to the libjpeg API, describes SIMD zlib terms as subsumed in that context, and
assigns Modified BSD terms to TurboJPEG/build-system code. It explicitly says
both IJG and Modified BSD apply in the overall TurboJPEG library. This is the
retained source's description; it cannot identify which APIs or files an
uninspected PDFium build incorporates. `28–30` labels the following roll-up an
explanation rather than a licence. Its binary/static-link explanation at 58–75
calls for the IJG credit and, when TurboJPEG is used, the Modified BSD text.
The actual Modified BSD conditions and disclaimer are at 97–122: source notice
retention, binary notice/conditions/disclaimer reproduction and a conditional
non-endorsement restriction. Read those clauses separately from the roll-up's
broader advertising paraphrase at 77–82.

The paired `libjpeg_turbo.ijg` starts by saying it was modified for reference
and points back to the Markdown file (`1–5`). Its legal terms at 128–161
require the README and unaltered copyright/no-warranty notice when source is
distributed, documented changes, the specified IJG credit for executable-only
distribution, and the stated responsibility/name-use conditions. The Markdown
roll-up at 32–56 additionally describes per-file modification marking. Preserve
that explanation and the underlying clauses as distinct sources; do not turn
the roll-up into a replacement licence. Future preparation needs actual API/
file inclusion, modifications, distribution form, the corresponding complete
upstream notices and an identified destination for each applicable credit.
The paired archive notices supply a bounded text comparison, not proof of the
actual component version or a complete upstream source/legal package.

**libpng.** `libpng.txt:4–36` supplies PNG Reference Library License version 2.
It prohibits origin misrepresentation, requires altered source to be marked,
and retains its copyright notice in source or altered-source distributions.
Product-documentation acknowledgment is appreciated but explicitly optional;
it must not be recorded as a new mandatory credit. The same file separately
contains historical version 1 text (`39–134`), including its stated 0.5–1.6.35
scope and later source restrictions. Lines67–69 warn of other licences for
some contrib/configure-generated files. Consequently a future record must
identify the actual libpng version, files and modifications before selecting
applicable terms, and inspect any included exceptions. Reading both versions
does not establish that both govern every eventual binary. No binary notice
condition absent from these inspected clauses is invented.

**zlib.** `zlib.txt:1–4` labels the retained header 1.3.1, dated 22 January 2024;
this is notice metadata, not an observed linked-library version. Lines6–20
state the warranty exclusion, permission and three restrictions: no origin
misrepresentation, marked altered source, and unchanged notice in source
distributions. Documentation acknowledgment is appreciated but not required.
Future preparation records actual version/source changes and the source-notice
destination, while retaining any separate enclosing-distribution requirements.
The RFC references at 26–28 describe formats; they were not used as licensing
support and no external text was retrieved for this bounded inquiry.

## Required future build-specific records

| Family | Applicability facts still missing | Conditional action preserved from the inspected text |
|---|---|---|
| FreeType | Exact files/version, file-specific terms, selected licence, modifications and distribution form | Preserve source licence/notices and change documentation; provide the stated binary acknowledgment; distinguish optional suggested wording/URL |
| JPEG | libjpeg versus TurboJPEG/build-system/SIMD inclusion, actual versions/files, modifications and linking/distribution form | Preserve applicable IJG README/credit and BSD notice/conditions/disclaimer; retain both texts when their conditions apply |
| PNG | Actual version, included contrib/generated files, modifications and source distribution | Select the supported version-specific terms, preserve source notices and mark alterations; keep optional credit optional |
| zlib | Actual version/files, modifications and source distribution | Preserve source notice and mark alterations; keep optional credit optional |

These are fields for internal preparation. No installation, distribution,
permission request, contact or professional engagement is authorised by them.
Wrapper terms, PDFium's other bundled components, build-conditional runtimes,
transitive Python dependencies and portable field translation remain separate
open work. An enclosing distribution can require retention beyond one component's
minimal clauses; optional credit in one text cannot waive another applicable
notice. The exact full build/component bill is still absent.

## Decision and limitations

| Decision | Primary criterion status | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Deliver the five-text supplement | Complete selected texts read; statements mapped to exact spans and applicability conditions | Raw archive/member/anchor/protected-input bindings must pass | Which files/versions/terms a future build actually includes | Use these conditional records with the eventual concrete build proposal | Complete terms review, dependency closure or rights clearance |
| Keep manuscript 3.44 unchanged | Its open dependency/component-terms description remains accurate | No confirmed contradiction found | The remaining23 notice texts and actual native payload are unreviewed in full here | Continue R07 ordered review and independent ready preparation | Requirement closure or independent/domain/human acceptance |

No stochastic comparison applies. The strongest alternative explanation is
that the future build includes different versions, omits one of these
components or incorporates differently licensed files. Its exact source/build
bill and corresponding terms would determine applicability. The weakest
evidence boundary is the intentionally unselected actual binary and component
graph. Static source text and successful integrity checks cannot fill it.
The UTF-8-only extraction assumption failed at the cheap check and was repaired
before interpretation; `extraction-attempt-01.json` preserves that event.

No new confirmed manuscript defect, global continuation veto or whole-row
closure follows. The exact candidate remains not_ready and all independent
technical/domain/human acceptance remains pending.
