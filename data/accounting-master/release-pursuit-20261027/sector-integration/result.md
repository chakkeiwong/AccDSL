# Dated insurance and bank interfaces integrated in 5.55

The protected 5.55 candidate integrates the checked premium-allocation calendar,
eight-event sequence and company-book/interim-report interface, plus the bank
profile compatibility and reproduction boundaries. It preserves the separate
Australian accounting and US prudential profiles. The existing US dated book
already supplies the balances for its capital query; no invented cross-basis
connection was added. The candidate remains **not_ready**.

Plan: docs/plans/accounting-sector-interface-integration-20261027.md.
Requirements: MC05/13/16/19/20/21/22/24/25/28/32/33/34/35.
Protected predecessor: manuscript-financing-v554r2p2-20261027.
Successor: docs/design/proposal/manuscript-sector-v555-20261027/.

## Verification and reproduction

All 437 source/build checks pass. Every predecessor package file remains
unchanged in place. Three prose additions and two explicitly documented
transition repairs preserve all original equations and citations. Both covers
identify 5.55; simulation chapter sources are unchanged. The main volume has
836 pages and the simulation volume 264 total / 243 body pages.

The first verification correctly rejected a 40.90385pt overfull paragraph.
Its record remains verification.json; a sentence split fixes the overflow in
build-03. Verification-02.json and rendered-pages-02.json bind the passing
PDFs and 15 inspected pages. Author-review.md separates comprehension,
mathematics/accounting, source fidelity and typography. This bounded review
does not advance the ordered whole-manuscript frontier beyond page 162.

The 447-file package contains six companions. The two added archives reproduce
from a fresh package copy with exact parsed-JSON equality for all declared
complete results: insurance cases, controls and verification; bank v1, bank v2,
US assessment, exact-time cases and checks. The insurance evidence retains
seven cases, 21 controls and 732 checks, plus 70 prior identity/prefix checks.
The bank evidence retains 1,659 original exchanges, 20,339 checks, 63 exact-time
cases, 42 retries and 12 additional controls. Shared financial implementation
and historical Git/index exclusions remain explicit.

Both documents were rebuilt in the separate package copy. Every normalized
page text matches, with no undefined/multiply defined references or overfull
boxes. All copied non-PDF package inputs and predecessor files preserve their
hashes. PDF file hashes differ after reproduction because generated file
metadata is not the comparison target; the report binds both identities.
Commands, paths, environments, exit codes and elapsed times are retained in
build-01, build-02, build-03 and relocation-01. No dependency was installed.

## Decision

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Select 5.55 as the next internal specification candidate | Complete declared copied outputs agree; both document texts reproduce; original source/evidence remains | Overflow repaired; no remaining source/build, replay or copied-input failure | Actual accounting applicability, independent readers and broader implementation remain unevaluated | Guard four stable links and live controls; continue ordered reading at 163 | Broad MC closure, whole-document acceptance, compliance, empirical accuracy or production readiness |

The strongest alternative explanation is shared implementation or retained
premises producing mutually consistent but inapplicable results. Independent
expectations and exact complete comparisons check the declared finite examples;
they do not resolve actual source admission or validate every accounting rule.
A mismatched output, omitted premise or independently identified manuscript
defect would overturn the corresponding local acceptance. This is deterministic
engineering/editorial evidence, not a stochastic ranking.

See remaining-work.md for C0–C7. All original broad obligations remain open,
S1–S5 partial, S6 held and E3 deferred. The timed pursuit continues through
15:19:56 UTC with no publication, outreach, fees or new installation.
