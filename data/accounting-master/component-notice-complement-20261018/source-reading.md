# R06 — Retained notice complement: source findings

18 October 2026. P17/P19, R06/R08; MC23–25/27/30–35.

All 23 complementary notice texts have now been inspected. Together with the
protected five-text inquiry, this accounts for all 28 notice files in the exact
retained pypdfium2 5.9.0 source archive. It does not establish which components,
files or versions any eventual binary contains. The archive remains a
documentary lower-bound witness; its normal PDFium7869 prebuilt rule is not a
selected or installed binary.

Paths and line numbers below refer to `sources/`. Raw bytes, complete reading
coverage and selected clause anchors are bound in `source-manifest.json`.
The earlier 21 complete inspections were resumed from their recorded work;
ICU's 512 lines and the GCC notice's 696 lines were then read in bounded,
numbered chunks. Four repeated Apache bodies use the fully inspected abseil
reference plus exact equal blocks and inspection of every differing target
line, recorded in `apache-comparison.json`. The hashes check preservation;
they do not substitute for those author observations.

## General and multi-part texts

**Abseil — `abseil.txt:1–203`.** The Apache 2.0 definitions at 8–65 delimit
the licensed Work, Derivative Works, contributions and distribution forms.
The copyright grant is at 67–72. The contributor patent grant at 74–88 is
limited to necessarily infringed claims of the contribution alone or its
combination with the submitted Work; the specified patent litigation ends
that grant. Redistribution at 90–129 requires a licence copy, prominent
modification notices, retention of pertinent source notices and reproduction
of attribution from an included NOTICE file, using one of the stated locations.
The NOTICE condition is conditional, and its contents do not modify the licence.
Additional notices or different terms for modifications cannot displace the
applicable requirements for the Work. Contributions, trademark limits,
warranty/liability and assumed additional liability are at 131–175. The
appendix at 177–202 is application guidance, not an actual copyright identity.
Actual covered files, contributor/NOTICE information and modifications remain
needed before preparing a distribution record.

**PDFium — `pdfium.txt:1–230`.** Its BSD-style prefix at 1–27 requires source
retention and binary reproduction of the copyright, conditions and disclaimer;
Google/contributor names cannot endorse derived products without permission.
The following Apache body at 29–230 equals abseil lines 1–202 byte for byte.
Preserve both parts. This file alone does not assign every covered source file
to a particular regime, identify the actual PDFium revision or close third-party
terms. `pdfium-binaries.txt:1–9` separately supplies MIT-style retention for
copies/substantial portions and points to third-party `licenses/` at line 9.
It cannot waive those referenced terms or identify an actual binary payload.

**LLVM libc — `all_except_musl/llvm-libc.txt:1–278`.** The Apache body through
206 was compared against abseil, including every difference. The LLVM
exceptions at 208–222 distinguish two cases. Compilation-embedded object
portions may omit sections 4(a), 4(b) and 4(d) only under the stated condition.
The separate GPLv2 conflict waiver depends on the specified court finding and
is limited to the combined software. Neither is a blanket exception for library
redistribution. Lines 224–234 preserve third-party/file-specific notices and
reproduce the possibility of separately licensed material. The legacy NCSA
section at 237–278 has source and binary retention and non-endorsement terms.
The actual revision, files, current/legacy applicability and incorporated
third-party notices remain unestablished; the sections are not silently treated
as cumulative conditions on every file.

**Android libunwind — `android/libunwind.txt:1–311`.** The complete text was
read directly. Its Apache body, LLVM exceptions and third-party qualification
occupy 1–234. The legacy section at 239–245 explicitly offers an NCSA-or-MIT
choice and says contributions are available under both. The NCSA text is at
249–289; MIT is at 293–311. Both refer to `CREDITS.TXT` for contributor identity.
The exact revision/files, applicable regime and credits are missing. Preserve
the licence choice instead of requiring both alternatives without a source basis.

**CPU features — `android/cpu_features.txt:1–230`.** The Apache body at 1–203
was compared against abseil, with its URL differences inspected. The separate
`ndk_compat` section at 204–230 uses Android's two-condition BSD-style text:
source retention, binary reproduction and disclaimer. It has no separate
non-endorsement clause. Future records must distinguish that subdirectory and
its actual included files from the enclosing Apache-covered material.

**Highway — `v8_xfa/highway.txt:1–201`.** The entire Apache 2.0 text is covered
by exact comparison with the read abseil body plus inspection of its HTTP URL
and boundary differences. Its conditions have the same scope distinctions
described above. Actual inclusion, covered files, changes and any NOTICE remain
build-dependent. The directory name does not prove that XFA or V8 is enabled.

## ICU and its incorporated components

**Unicode V3 — `icu.txt:1–39`.** The notice covers data/software and associated
documentation. Lines 13–22 allow the copyright and permission notice either
with all copies or in associated documentation. Lines 24–39 disclaim warranty
and liability and restrict promotional use of copyright-holder names without
written authorization. The older ICU 1.8.1–57.1 notice at 51–84 instead says
the notices appear in all copies **and** supporting documentation. These are
different stated scopes and conditions; actual version/file evidence must
determine applicability. Lines 43–47 expressly introduce third-party terms.

**Chinese/Japanese dictionary — `icu.txt:88–290`.** The Google BSD-style text
at 90–125 requires source/binary retention and non-endorsement. Lines 128–139
describe the combined word lists. The Libtabe material at 141–214 preserves
separate TaBE/Pai-Hsiang and Academia Sinica notices, source/binary retention,
named-party non-endorsement and disclaimers, plus the Chih-Hao Tsai attribution.
IPADIC at 217–290 requires its copyright and following paragraphs in original
or modified copies. Its ICOT-derived terms require the NO WARRANTY provisions
to accompany the distribution substantially as stated, and condition distribution
on the laws/regulations having jurisdiction. The experimental/no-warranty,
risk and downstream-supplier provisions are retained, not reduced to a generic
BSD label. The source says ICOT conditions apply to the current dictionary.

**Other dictionaries and data — `icu.txt:294–430`.** Lao's notice at 294–332
identifies the November 2020 derivation, Unicode/IBM attribution and the copied
Brian Wilson/Robert Campbell source/binary retention/disclaimer; it has no
non-endorsement clause. Burmese at 336–374 additionally preserves the Myanmar
Karen Word Lists/contributor non-endorsement term. The time-zone section at
378–399 quotes BCP175 section 7's public-domain status, contribution waiver,
and court-order qualification. That statement is about that database/code,
not all ICU material or all possible third-party rights. Double-conversion at
403–430 has source/binary retention, Google/contributor non-endorsement and
disclaimer. Included dictionaries, data vintages and source identities remain
actual-build questions.

**ICU4C build files — `icu.txt:434–512`.** `aclocal.m4`/`pkg.m4` is GPLv2-or-later
at 434–465, with a special exception when distributed as part of a program
containing an Autoconf-generated configuration script. The notice says ICU4C's
`configure` fulfils that condition for ICU4C. `config.guess` at 469–495 is
GPLv3-or-later with a similarly conditioned exception, expressly an additional
permission under GPLv3 section 7. Do not infer that any different repackaging
fulfils these conditions. `install-sh` at 499–512 requires copyright in copies,
copyright/permission in supporting documentation and prior permission for the
specified MIT advertising/publicity use; it disclaims suitability/warranty.
The ICU notice does not include GPLv2's full terms. The separately retained
GCC notice supplies GPLv3 text, but does not choose a regime for these files.
If their unexcepted GPLv2 terms become relevant, obtain and inspect that text.
The full actual file/source package is still needed to establish inclusion,
licence notices, modification history and any other incorporated terms.

## GCC runtime library exception and GPLv3

**`cibw_musl/libgcc_and_libstdc++.txt:1–696`.** All text was read, including
the GPL terms after the exception. Exception 3.1 applies only to a file bearing
the holder's notice that GPLv3 and this exception govern it (10–20). Definitions
at 22–57 distinguish an Independent Module, GCC, GPL-compatible Software,
Target Code and an Eligible Compilation Process. Compiler intermediate
representations are excluded from Target Code; non-GPL-compatible optimisation
of GCC intermediate representations is the stated ineligible example.
Lines 59–72 permit the specified combination of Runtime Library and Independent
Modules under chosen consistent terms only when all Target Code came from
Eligible Compilation Processes. They explicitly deny a general presumption
that third-party software is unaffected by GCC copyleft. The filename and musl
directory alone establish none of those prerequisites. Separate runtime-library
source/binary redistribution and modifications still need their own analysis;
the exception does not simply relabel the libraries MIT or BSD.

The full GPLv3 terms are at 76–696: definitions and Corresponding Source/System
Library distinctions at 148–227; private activity/basic permissions at 229–252;
anti-circumvention provisions at 254–268; verbatim and modified source notices,
licensing and interactive-interface provisions at 270–318. Sections 6 and 7
(320–480) specify object-code Corresponding Source alternatives, the conditions
of offers/network/peer transmission, the User Product/Installation Information
case and its limits, and additional terms/permissions. The System Library
exception is defined, not assumed from a library's name. Sections 8–10
(482–544) include termination/cure, acceptance on modification/propagation,
downstream licensing, entity transactions and no further restrictions.
Section 11 (546–613) supplies the limited contributor patent grant and
conditional downstream/patent-arrangement provisions. Sections 12–14 (615–662)
address conflicting obligations, an AGPLv3 combination and choice of revised
versions. The AGPL paragraph references requirements not reproduced here;
it does not license an uninspected combination. Sections 15–17 (664–694)
state warranty/liability exclusions and their interpretation under local law.
The preamble is context; the terms and actual file-specific additional
permissions determine any future proposal. The exact runtime versions/files,
holder notices, compilation provenance, modifications, distribution form,
corresponding sources and any conditional installation information are missing.

## Other complete notices: individual dispositions

| Exact file and inspected lines | Stated terms and boundary | Facts still needed for a future build |
|---|---|---|
| `agg23.txt:1–14` | AGG2.3 permits copying/use/modification/sale/distribution if copyright appears in all copies; warranty exclusion at 2–8 | Actual version/files and retention destination; contact metadata grants no outreach authority |
| `fast_float.txt:1–27` | MIT-style copyright/permission retention in copies or substantial portions, with disclaimer, 3–27 | Covered files/version and notice destination |
| `lcms.txt:1–27` | Copyright/permission retention and disclaimer, 4–22; line 26 labels version 2.15 only as notice metadata | Actual included version/files and notice destination |
| `libopenjpeg.txt:1–32` | Lines 2–5 disclaim a third-party/contributor/patent-right grant; two-condition source/binary retention and disclaimer at 12–31 | Exact files/version, third-party rights and source/binary notice destination; no patent clearance inference |
| `libtiff.txt:1–21` | Copyright/permission in software and related documentation; advertising/publicity name-use condition, 1–10; disclaimer, 11–21 | Actual files, documentation, modifications and notice destination |
| `android/catapult.txt:1–27` | BSD-style source/binary retention, Catapult/contributor non-endorsement and disclaimer, 1–26 | Actual Android inclusion, files and notice destination |
| `pdfium-binaries_musl/musl.txt:1–193` | Whole-text MIT-style terms/author list, 1–109; third-party/per-file sections, 111–161; limited header/crt attribution exception, 171–186; clarification, 188–193 | Exact musl files/version, applicable per-file notices and whether the listed-path exception actually applies |
| `v8_xfa/bigint.txt:1–71` | Technical context, 1–64; author's original-work copyright waiver/public-domain and warranty statement, 67–69 | Actual code identity and third-party additions; no universal jurisdictional clearance inference |
| `v8_xfa/fdlibm.txt:1–6` | Sun copyright and freely use/copy/modify/distribute permission require the notice to be preserved, 4–6 | Actual files/version and complete notice destination |
| `v8_xfa/fp16.txt:1–12` | MIT-style retention/disclaimer, 3–11 | Actual included files/version and notices |
| `v8_xfa/inspector_protocol.txt:1–27` | Source/binary retention, Google/contributor non-endorsement and disclaimer | Actual enabled components, files and notices |
| `v8_xfa/simdutf.txt:1–18` | MIT-style retention and disclaimer | Actual included files/version and notices |
| `v8_xfa/strongtalk.txt:1–29` | Source/binary retention, Sun/contributor non-endorsement and disclaimer | Actual included files/version and notices |
| `v8_xfa/v8.txt:1–26` | Source/binary retention, Google/contributor non-endorsement and disclaimer | Actual V8 flags/version/files and notices |

Musl's statement of compatibility does not reproduce the per-file notices for
TRE, math, ARM/AArch64, DES, Blowfish and smoothsort. The port paragraphs specify
standard MIT terms, already reproduced in the general notice; their exact file
and authorship mapping remains unverified. Its listed
header/crt exception cannot be extended to the whole library. Obtain the
applicable source-file notices before applying it. The LLVM third-party/legacy
qualifications and libunwind credits similarly remain source dependencies.
The AGPL paragraph is conditional; no AGPL component has been identified here.

## Decision and red-team record

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | What is not concluded |
|---|---|---|---|---|---|
| Deliver this complement as documentary preparation | All 23 complete texts inspected; terms and exceptions have exact anchors and conditional dispositions | Require exact archive/member, comparison, anchor and protected-input checks | Actual covered files, modifications and future distribution | Preserve all 28 readings; use the missing-source list to prepare a concrete future dependency proposal | Actual component bill, transitive closure, compatibility or rights clearance |
| Preserve manuscript 3.44 and frozen R08 judgments | No contradiction with its open dependency/terms claims was found | No confirmed manuscript defect | Independent technical/domain/human acceptance | Bind the supplement and continue ready internal source/method work | Whole-requirement closure or product readiness |

No stochastic comparison applies. The strongest alternative explanation is
that an eventual build uses different versions, flags or files and therefore
different terms. Exact source and binary identities could overturn the
applicability of any row above. The weakest boundary remains that absent
actual-build evidence. Reading all 28 archive notices closes this inventory's
author-reading task only; missing incorporated sources and build-specific
actions remain open. No global continuation veto fired.
