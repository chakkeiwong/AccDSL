# Financing amounts and cash prefixes are specified explicitly

27 October 2026. Protected candidate 5.54-R2 repairs section 14.13's unsupported
finite-action claim. Three inventory-sale offers do not make continuously
varying borrowing amounts finite. The chapter now derives the feasible amount
domain, distinguishes a minimum-funding witness from a liquidity optimum, and
shows how a different same-day settlement order changes admissibility.

For sale fraction z, bridge principal a, term face b, issue indicator u and
receipt R, cash after the old debt is a+15z−31; cash after bridge repayment is
15z+R+qb−32−2u. Together with issue domains and offer eligibility, nonnegative
cash is equivalent to a lying between 31−15z and 30 and the latter cash being
nonnegative. The proof depends on receipt-before-issue settlement, fixed
positive supplied price and the chapter's stated fee/calendar assumptions.
The manager's notice deadline and information restrictions remain separate.

Two exact examples explain why the domain matters. With full sale, timely
collection and no term issue, bridge principal 16 gives minimum cash zero;
principal 17 gives minimum cash one with the same cost and final cash. A
negative-net-proceeds term issue of face 10/9 at price 0.9 is feasible after
the receipt but causes a one-unit shortfall before it, despite equal final
cash. That second diagnostic excludes the inventory covenant and is not
recommended finance. Later term debt remains outside the day-6 cash horizon.

The original arithmetic run passed 4,586 checks over 1,428 selected rational
cases and 24 regimes. These check event arithmetic and boundary examples;
the continuous result follows from the derivation, not those counts. The
portable standard-library companion was copied with the package and run with
isolated Python from /tmp. All full traces match the retained reference and
both explicit expected counterexamples match. No original one-shot writer
was rerun. The reviewed plan later acquired integration and rendered-review
sections; its original run-manifest hash remains the pre-run plan identity.

The final document passes 428 source/build checks. All original displays and
citations are retained, with three derived displays added. The package has
414 files, including this example's three companion files. The main volume
has 835 pages, SHA256
0a78bcd582784e4119de330438a8517916efc6ef781e3db244ad4d644a82f3fd.
The simulation volume has 264 total / 243 body pages, SHA256
51b093b702d848d092294588bd4765de665e0c68e60aa1483dd74b3fe25789c2.
Both volumes rebuild from the separate package with every normalized page's
text equal and no original-worktree build inputs. PDF byte identities differ
between builds, so semantic reproduction and original identities are recorded
separately. No clean-install claim is made for the existing TeX environment.

The complete revised chapter, both covers and affected standalone pages received
bounded author review, with 17 final page bindings. Two wording defects found
in attempt 01 were repaired; its files and checks are preserved. The ordered
whole-manuscript read remains bound to 5.52-R2 and separate from this regression.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept the local amount-domain repair | Derived necessary/sufficient constraints and distinguishing examples agree with event arithmetic | No failed identity, lost citation or hidden cash prefix | Actual offer amounts, prices, ordering and notice rules | Use the stated continuous branch or an explicitly finite contract menu | General financing optimum or real issuer feasibility |
| Include the portable example | All traces and independent expected counterexamples reproduce outside the worktree | No undeclared worktree data read by this standard-library script | Broader engine and source-acquisition dependencies | Continue the separately active executable-evidence closure | Whole AccDSL runtime reproduction |
| Select a provisional document successor | Source preservation, local rendering, package verification and both relocated builds pass | No local promotion veto | Whole-document, source-population and independent acceptance | Continue ordered reading and C1–C7 residual work | Release readiness or broad MC completion |

Evidence: checks.json, traces.json, run-manifest.json,
candidate-verification-02.json, author-review.md, rendered-review.json,
package-record.json, companion-reproduction.json and relocation-01/result.json.
Actual build commands, environments and wall times are recorded per volume
under build-01, build-02 and relocation-01. Integration provenance is recorded
separately in integration-manifest.json and advancement.json.

The strongest alternative explanation for successful checks is shared mistaken
offer assumptions. The examples therefore expose those assumptions and give
a direct counterexample when settlement order changes. The weakest evidence
is their transfer to actual contracts and broader simulations. An amount-based
interest charge, endogenous issue price or different action timing would reopen
the domain calculation. The existing all-company, sector, source and independent
acceptance requirements remain open; the release stays not_ready.
