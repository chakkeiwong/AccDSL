# Calculations 1.1: design intent supports equality; source qualifications remain

22 October 2026. Three public official documents were acquired and inspected:
the Calculations 1.1 product index, its complete 2022 Requirements document and
the requirements release history. The index places the dated conformance suite
under “Additional Resources (members-only)”. No suite request, authentication
attempt, download or test reading occurred. This is a publisher-stated access
boundary, not an observed HTTP denial or a finding that every legitimate copy
is inaccessible.

The public requirements provide new support for the existing contextual
equality interpretation. Section 1 identifies common period, dimensions and
other contextual information. Section 2.3 calls for the same built-in and
taxonomy-defined dimensions and units, with type-aware comparison of equivalent
QNames. Section 4.1 explicitly excludes new cross-period or other
cross-dimensional calculations from 1.1. These statements support preserving
common contextual dimensions when moving from XML syntax to OIM semantics.

That design intent does not insert the missing converse into the retained
Recommendation's section 5.1 definition. The prior 528 equality joins, 801
contributor-subset joins and 1,001 total-subset joins remain separate exact
conditional results. No comparison was rerun, policy selected or authoritative
erratum obtained. The strongest competing reading is the literal directed
definition; the new requirements explain why the contextual equality reading
is plausible without resolving its normative status.

The edition distinction is consequential for duplicates. Requirements section
3.3 says to use the most precise consistent fact. The corrected Recommendation
section 5.5 requires the intersection of every duplicate interval. Its example
has 5000 at decimals -3, interval [4500,5500], and 5500 at decimals -2,
interval [5450,5550]. The intersection is [5450,5500], which is smaller than
the finer interval. A supplied exact total of 5525 falls in the finer interval
and outside the intersection. Thus a finest-only implementation would compute
the wrong interval relative to the final rule, even though it follows the
earlier broad requirement. The 5525 total is a local mathematical illustration,
not a source test or an actual report fact. This does not resolve the separate
section 5.4 OIM duplicate-reference mismatch.

The requirements' rounding example is internally reconstructible. Actual
amounts 12,141,123 and 45,441,321 sum to 57,582,444. Their reported millions,
12.1 and 45.4, sum to 57.5 while the reported total is 57.6. Closed nearest
intervals give a component-sum interval [57.4,57.6] and reported-total interval
[57.55,57.65], whose overlap is [57.55,57.6]. This checks the source's intended
distinction between displayed sums and possible underlying amounts; it does
not establish an issuer's rounding policy.

The source date discrepancy is also retained. Both official indexes display
22 May 2022, while the linked URL and the actual document title say 25 May
2022. The release history identifies that item as supporting the Candidate
Recommendation. Appendix B lists the initial draft on 9 November 2021. The
original bytes remain unmodified; no exact publication-history inference is
made from these differences.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain new alignment-intent support | Complete requirements sections 1, 2.3 and 4.1 explain same-context scope | No source identity or arithmetic failure | Recommendation's missing converse remains unrepaired | Keep equality labelled as a contextual interpretation | Authoritative clarification, default or filing-error conclusion |
| Preserve final duplicate intersection rule | Exact final-source example differs from most-precise-only interval | Earlier requirement cannot replace the later rule | Section 5.4 link/definition ambiguity remains | Retain OIM qualification and original observations | A general duplicate policy is settled by broad requirements |
| Record suite access boundary | Explicit members-only heading and dated link inspected | Suite-specific conclusion blocked; independent work remains ready | Suite contents and expected results unread | Inspect the separate public Calculations 2.0 requirements lead for broader calculation scope | Suite coverage, processor conformance or global source absence |
| Preserve proposal status | Frozen 3.48 candidate and completed review protected | No continuation veto | Independent/domain/human evidence remains pending | Continue bounded internal preparation | Whole-row closure or readiness |

The main alternative explanation is that the earlier requirements describe
intent more loosely than the final specification. The duplicate comparison
demonstrates exactly that risk. Only an authoritative clarification or an
explicit, applicable source resolution could settle the normative wording.
The weakest evidence is the unread suite and the absence of installed
correspondence. These results do not invalidate the earlier conditional
arithmetic, manuscript or research direction.

`source-ledger.json` retains three acquisitions and 18 passage anchors; the
six research ledgers distinguish documentary support, local interpretation,
exact derivation and unresolved leads. `exact-examples.json` preserves the
source arithmetic and the authored discriminator. `run-manifest.json` records
commands, source identities, CPU-only environment and timing. Version 3.48,
401 pages and not_ready remain; all 53 obligations, six interactions and
46 operations survive with zero whole-row closures. No runtime, installation,
empirical run, commit, outreach, publication or fee occurred.
