# Calculations1.1 source contract

20 October 2026. Five official documents are retained: the release history,
the corrected2024 Calculations1.1 recommendation, its linked2021 OIM and
xBRL-XML recommendations, and the calculations area index. Seven acquisition
attempts preserve a sandbox DNS failure, its successful trusted retry, and a
trusted normative-schema connection timeout. The other five attempts succeed.
No absence claim follows from the timeout. AppendixA's schema copy is explicitly
non-normative and is not substituted for the publication copy.

The release page lists Recommendation2023-02-22 with corrections to2024-02-14.
The area index lists Calculations2.0 under development. Those are observations
of these retained pages, not an adoption claim about the2024 filing.

The inspected1.1 rules differ materially from the frozen XBRL2.1 result:

- Old and new arcroles define separate networks. Applying1.1 to old arcs is
  optional, and the old results must remain available and distinguishable.
- xBRL-XML compatibility is a prerequisite. Non-tuple compatibility errors
  become a warning and stop1.1 processing; tuples have a narrower exception.
- One rounding mode applies to the whole report. Nearest-mode intervals are
  closed, permitting either tie direction. Truncation uses sign-dependent
  half-open intervals, with both endpoints open for zero.
- Consistent duplicates contribute their interval intersection; inconsistent
  pairs and excess digits stop further checking of the affected binding.
  All-nil points are ignored, while mixed nil/non-nil duplicates are inconsistent.
- Calculated and reported total intervals must overlap. Taxonomy errors,
  calculation inconsistencies and nonfatal warnings remain separate categories.

Section5.4 contains a checked cross-reference mismatch. It links its
consistent-duplicate definition to OIM's dimension-only duplicate-facts
definition, which contains no numeric interval rule. The surrounding text,
its stated nearest-mode equivalence and section5.5's example point to OIM6.2
numeric consistency. The local examples use that explicit contextual reading,
including the same-precision/equal-value rule; this is not an authoritative
erratum or a conformance certificate.

All37 exact examples and122 counted assertions pass. The evidence includes
19 source excerpts,31 input bindings and preserved acquisition receipts.
Discriminators cover closed versus open boundary intersections, positive/
negative/zero truncation, same-precision disagreement, nontransitive duplicate
consistency, all-nil versus mixed-nil sets, excess digits, negative-weight
endpoint reversal and interval addition. The synthetic summed terms represent
distinct contributing concepts. No actual filing is assessed under1.1 here.

The source review identifies16 prerequisites or unresolved duties in
prerequisites.json. Several structural prerequisites have bounded earlier
evidence, but OIM dimension mapping, footnotes, discoverable role references,
the normative schema copy and the5.4 wording issue retain separate dispositions.
Rounding mode and filing-system policy remain unselected.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain source contract and exact examples | Primary technical text and discriminating outcomes | No failed authored arithmetic check |5.4 literal cross-reference differs from its context | Audit actual xBRL-XML compatibility and OIM mapping | Report-level1.1 acceptance or authoritative source correction |
| Keep normative schema-copy gap open | Exact publication route attempted and preserved | Trusted connection timeout | Actual publication bytes not retained | Use a distinct bounded source-recovery attempt only when needed | Global schema unavailability or appendix-copy identity |
| Preserve old calculation result | Frozen old-arc network and110/164 outcomes unchanged | No preservation failure | An optional new contract has not been adopted | Keep old/new evidence separate | Replacement of old results or default policy |

Engineering evidence consists of preserved sources and exact examples.
Numerical interval rules are specification interpretations; they do not prove
an issuer measurement process or financial-history constraint. No stochastic
ranking is involved. No manuscript contradiction requiring a rebuild is found.
Candidate3.44/396/not_ready and53 obligations/six interactions/46 operations
remain unchanged; zero whole rows close.

Post-run red team: a literal reading of the defective link would make the
numeric definition incomplete. A source-author clarification could alter the
contextual interpretation and would require a successor result. Likewise OIM
grouping could differ from the earlier XML duplicate classes; no actual report
interval calculation is run before checking that mapping.
