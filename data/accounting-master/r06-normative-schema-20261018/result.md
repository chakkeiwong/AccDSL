# R06 — historical normative instance-schema correspondence

Completed 19 October 2026 (Hong Kong); started 18 October. The dated directory
and plan retain their start date. P15/P17/P19; MC01–06/23–25/27/30–35.

The retained non-normative XBRL instance schema corresponds exactly to the
instance schema extracted from the named normative 2 July 2008 RTF after three
explicit adjustments: retained CRLF becomes LF; each text's leading XML notice
comment is removed; and one final LF is appended to the extraction, which ends
at the closing schema tag. The resulting 22,141-character texts are identical.
There is no remaining token, attribute, annotation or ordering difference under
those adjustments. Raw byte identity is false and was not required.

The official index led to the release history and its exact dated HTML. That
HTML explicitly calls itself non-normative and names the normative RTF. The
RTF was acquired and used as comparator. Five distinct URLs and one initial
sandbox DNS failure/retry are preserved in six acquisition receipts. No newer
edition or standalone schema download substitutes for the normative source.

The entire instance-schema slice was decoded from RTF bytes 6,161,896 through
6,217,247 exclusive. Its inspected control vocabulary consists of formatting
and paragraph controls; no deleted-text, Unicode or escape rule was silently
invented. An independently extracted HTML appendix gives the same ordered
355-element structure, namespace bindings, attributes and whitespace-normalized
text. The HTML HTTP charset label disagrees with its file meta declaration;
the bytes were decoded as declared Windows-1252 without replacement characters.

All thirteen deliberate changes were rejected: nine schema/namespace/order/
annotation mutations and four unsupported RTF controls. These are finite
comparison fixtures, not evidence that a general RTF parser or XSD validator
has been implemented. Exact correspondence additionally checks the texts
without relying on structural whitespace normalization.

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Admit the narrow historical source correspondence | Exact dated normative source acquired; text equality under three named adjustments; 355 ordered elements agree | Wrong-edition/substitution/namespace/order/mutation screens pass | Full specification constraints beyond this selected source question are not audited | Preserve the source-copy result and continue the built-in lexical/value-space inquiry | Valid filing, validated facts, installed parser equivalence, accounting meaning or rights clearance |
| Preserve all prior portable Values and runtime hold | No existing declaration/translation artifact changed | No installation, upstream execution or empirical action admitted | Built-in type semantics, other normative schemas, taxonomy constraints and installed behavior | Audit a finite source-only W3C type-boundary unit for the seven already identified unitless facts | Whole taxonomy equivalence or validation |
| Continue proposal preparation | Protected 3.44 and frozen 53/6/46 assessment remain authoritative | No continuation veto identified | Independent technical/domain/human acceptance remains pending | Refresh four controls and add separate R08 evidence; continue ready source work | Whole-row closure or readiness promotion |

Engineering ledger: deterministic source receipts, extraction, equality and
mutation checks. Numerical/sampler ledger: not applicable; no experiment.
Scientific interpretation: the copy-status qualification is resolved only for
this exact retained instance schema and this exact historical Appendix A.
No stochastic ranking applies. The protected manuscript stays 3.44, 396 pages,
not_ready. Earlier notes saying Appendix A correspondence is unchecked remain
historical; the new additive evidence supersedes that narrow current status.

Post-run red-team: a matching copy does not make every fact valid, validate the
referenced linkbase/XLink schemas, establish a legal permission, or implement
the surrounding normative prose. The exact-text result limits dependence on
the custom extraction's whitespace handling; independent HTML agreement is
corroboration, not authority. A wrong RTF edition or a missed revision control
would overturn the source conclusion. The retained source bytes, raw offsets,
strict control inventory and complete text comparison permit that challenge.

Safe replay: CPU-hidden tfgpu Python running verify.py without flags. Never
repeat prepare, check, extraction, source recording or completion recording.

Next: audit the XML Schema 1.0 source references for gYear, string/token and
normalizedString, including facet and whitespace semantics of the seven retained
unitless declaration chains. Preserve unknown Values and the runtime hold.
