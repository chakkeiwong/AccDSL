# Version 2.5 bounded insurance review

8 October 2026. Author preparation only. Final 129-page PDF SHA256:
`3f1d45e0ce13ae7e2eac557e4d1cb81585edf9490b6dec7fb05920c595174a0a`.
The final render manifest binds that PDF before and after rendering.

Read baseline pages 86–91 and final pages 1, 5–6, 59–61, 85–93 and 124–129
at normal resolution. This covers the whole insurance chapter in order,
its transitions, the cross-standard insertion and adjacent pages, relevant
contents and the bibliography. It is not a full 129-page manuscript reread.

| Ledger | Finding and disposition |
| --- | --- |
| Reader comprehension | Pages 90–91 distinguish coverage, premium/service and claim-settlement intervals, then show why the two-year claim is 55. The group balance and liability-error consequence are reconstructible from the slice. Human/independent comprehension remains pending |
| Mathematical integrity | Exact rational PV, current RA, half-year revenue, three journals and net assets reconcile. The source target is discounted fulfilment cash flows under authored inputs. No existing display or prior insurance example was removed; earlier methods were preserved, not all re-derived in this unit |
| Source fidelity | Sixteen Chinese anchors support the selected claims. The dated AASB comparator, translated interpretations, local calculation and missing adoption evidence are distinguished. On the first rendered pass the return to reinsurance/transition could leave bare paragraph references ambiguous; the final text explicitly names AASB 17 in both places |
| Typography and rendering | Final LuaLaTeX log has no warnings or overfull/underfull boxes. Equations, journal text, headings and new bibliography entry are legible on the inspected pages. The AASB bibliography entry continues from page 124 to 125 without lost text; no substantive repair is needed for that ordinary page continuation |

## Reader questions answered from the repaired slice

1. **What does PAA simplify?** The stated eligibility conditions permit a
   simpler remaining-coverage measurement. They do not remove fulfilment-cash-
   flow measurement of incurred claims. Page 90 introduces the unpaid-claim
   example immediately after the existing LRC/LIC distinction.
2. **Which one-year interval governs each choice?** Article 50 uses coverage
   of each contract; Article 54 uses each service portion relative to the
   related premium due date; Article 56 uses incurrence to expected settlement.
   All three are stated before the example.
3. **Why 55 rather than 65.5 or 50?** The assumed expected payment of 60.5 in
   two years discounts to 50 at 10%; the separately authored current RA is 5.
   It is not discounted twice. Ignoring time value gives 65.5 and ignoring RA
   gives 50. The manuscript states the former error and its profit consequence;
   the calculation record also checks the latter.
4. **Which result is this?** An isolated group's balances at the instant the
   claim is incurred, halfway through coverage. No intervening claim finance
   accrual, complete insurer balance sheet or realised settlement is implied.
5. **What remains needed for real use?** Insurance grouping, real cash-flow
   evidence, appropriate market rates, actuarial RA and entity applicability.
   The text states that Article 120 alone does not settle adoption and that the
   retained AASB compilation has a specified period of application.

These are author answers, not an independent reader experiment. The local
transition passes the author interruption check: the concrete unpaid claim
creates the need for discounting before arithmetic appears, and the preceding
pages have already defined LRC, LIC and RA. General insurance readiness still
requires the retained VFA/guarantee, transition, acquisition/reinsurance and
actuarial evidence.

## Preservation and surface diagnostics

Changes are confined to the version label, Chapter 9's authority cross-reference,
the insurance section's addition and two explicit AASB attributions, and one
bibliography entry. `manuscript-delta.diff` and `candidate-checks.json` compare
the actual sources with the protected Version 2.4. All 37 displays and all 62
prior bibliography entries remain; 63 entries result after the addition.

The surface audit was run on the actual included insurance source, not only
the manuscript entry point. Its long-sentence and unlabelled-display candidates
refer to existing compact examples and the unnumbered PV/chain-ladder displays;
the surrounding explanations identify their quantities and the displays need
no cross-reference. They remain intentionally unnumbered. There are no repeated-
word, space-before-punctuation or placeholder findings. The section-only audit
does not establish cross-document citation resolution; the separate final main
build and candidate checks address that. Mechanical findings are diagnostics,
not readability scores.

First-build outputs are retained under `first-build/`; its former render paths
are relocated beneath that directory. Its hash and page review are historical,
not the final render binding. No source gaps were hidden by a clean build.

Independent reader: pending. Human/domain acceptance: pending. Full proposal:
`not_ready`. Missing acceptance does not stop feasible internal continuation.
