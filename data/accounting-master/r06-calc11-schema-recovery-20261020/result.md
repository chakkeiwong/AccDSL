# Calculations 1.1 publication schema recovery

20 October 2026. P15/P16/P17/P19; MC01–07, MC24–26, MC28–35.

The exact AppendixA publication URL now returns the complete 1,343-byte XML
schema with HTTP200, no redirect and no change of host or scheme. The earlier
trusted timeout remains preserved in the predecessor. This is a successful
bounded retry of a transient acquisition failure, not evidence about when a
particular filing system retrieved the schema.

The appendix copy was explicitly labelled non-normative. Exact UTF-8 bytes
differ. The complete namespace-aware element/attribute/text profile agrees:
both define target namespace
https://xbrl.org/2023/calculation-1.1, unqualified attributes and qualified
elements, with one annotation/appinfo containing one link:arcroleType for
https://xbrl.org/2023/arcrole/summation-item, id summation-item,
cyclesAllowed undirected, the checked definition, and the QName-valued
link:calculationArc usedOn. Inter-element formatting whitespace differs.
Copyright notices agree after whitespace normalization. The check is scoped
to this finite document profile; it does not assert general XML Schema,
DTS-discovery or processor equivalence.

The recovered file has six XML elements and no XSD imports, includes or
redefines. Two metamorphic controls preserve the checked profile under a
prefix alias and inter-element whitespace. Eight single-field alterations
change the compared record; four unbound-prefix, external-declaration or
truncated inputs are rejected. All 36 counted checks pass, with three source
anchors, 13 bindings and one successful HTTP200 acquisition.

AppendixA explains that DTS discovery uses the publication URL; installation
and local substitution are separate behavior. That source identity duty is
now materially better evidenced. Installed version correspondence, a report's
actual DTS discovery, adoption of Calculations1.1 and rounding policy remain
unexamined. The pre-existing 5.4 cross-reference mismatch and contextual
duplicate-fact reading are unchanged; retrieving the schema cannot correct
the prose or validate its interpretation. No old-arc result is replaced.

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Close this source-copy recovery unit | Exact publication URL, complete bytes and namespace-aware profile retained | Response identity, structure and altered controls pass | Processor-specific DTS use | Preserve publication and appendix roles separately | Full schema validity or installed correspondence |
| Keep Calculation 1.1 report use unselected | No report/DTS execution or adoption evidence | No source-integrity veto; adoption evidence remains absent | Filing-system policy and actual taxonomy selection | Inspect actual retained schemaRef/reachable DTS only in a separately scoped unit | Replacement of XBRL2.1 results or a selected rounding mode |
| Preserve the duplicate-rule qualification | 5.4 cross-reference mismatch remains independently open | No new authority resolves it | OIM dimension definition versus numeric duplicate consistency | Continue the targeted interpretation queue without redoing schema acquisition | An authoritative erratum or conformance ruling |

Engineering evidence is exact response preservation and a finite XML profile
comparison. No numerical experiment or stochastic ranking was conducted.
Counts and successful downloads are not promotion metrics for accounting
semantics. The manuscript's scope qualification remains supported; no rebuild
is warranted. The six-ledger supplement closes no mission row.

Post-run challenge: the profile intentionally ignores inter-element formatting
whitespace and XML comments while comparing the checked namespace-expanded
declarations and leaf text. An unmodelled XML processing rule or installed
override could affect runtime use. The result establishes a source comparison,
not full parser equivalence. No input, harness, target or research direction
was invalidated; no global continuation veto fired.

Proposal 3.44 remains 396 pages and not_ready. All 53 obligations, six
interactions and 46 operations remain; zero whole rows close. HEAD/index,
empty staging and 36 tracked dirty paths are preserved. No installation,
runtime, empirical run, commit, outreach, publication or fee occurred. After
completion, verify.py without flags is the safe read-only replay.
