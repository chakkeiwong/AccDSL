# R06 — three companion schema copies

19 October 2026. P15/P17/P19; MC01–06/23–25/27/30–35.

All three retained companion schemas have the same ordered XML elements,
attribute values, effective namespace bindings and normalized annotation text
as their exact historical normative Appendix A extracts. They are not identical
after only the three adjustments used for the earlier instance-schema result:
additional indentation, tabs and blank lines differ. Every textual difference
is retained in the three diff files and has been inspected.

| Schema | Ordered elements | Equal nonblank content lines after ASCII indentation trimming | Additional retained tabs |
| --- | --- | --- | --- |
| Linkbase | 216 | 435 | 0 |
| XLink | 50 | 89 | 46 |
| XL | 117 | 218 | 4 |

After CRLF conversion and removal of each first prolog notice comment, removing
ASCII-space/tab-only blank lines and trimming ASCII spaces/tabs at line edges
gives identical ordered nonblank lines. Internal line content is not changed.
These are documented presentation adjustments, not byte equality or a general
semantic-equivalence proof. Attribute values and annotation words are preserved.

The complete three RTF XML slices contain 66,948 bytes and the same inspected
formatting-control vocabulary as the earlier extraction. No decoder extension
was required. Unique bookmark-starts identify normative headings; literal
filename matching alone was rejected because filenames also occur in contents,
cross-references and errata. Twelve altered namespace, target namespace,
declaration and annotation fixtures fail the comparison. All seven input source
bindings are checked. No new network acquisition or upstream execution occurred.

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Admit the three bounded structural source correspondences | 383 ordered elements agree; all nonblank line content agrees under declared presentation rules | Twelve mutations rejected; exact text differences retained, not suppressed | Surrounding normative prose and processor/schema composition behavior untested | Preserve these results alongside the previous instance-schema result | Exact bytes or equality under the earlier three-adjustment rule |
| Keep validation and runtime open | No installed parser, schema validation or financial mapping executed | Missing installed evidence continues to veto admission | Effective builds, configuration, full taxonomy/instance validity and rights | Continue ready proposal work; require a separately authorised runtime protocol before installation | Taxonomy validity, financial meaning, rights clearance or completed R06 |
| Refresh the execution frontier | Four core source-copy questions now have bounded evidence | No continuation veto fired | Remaining scientific method gaps need their own discriminating work | Re-audit the general nonadditive EPS residual from its completed discriminator | General accounting selection or whole-row closure |

Engineering ledger: deterministic source-copy checks. Numerical/sampler ledger:
not applicable. Scientific interpretation: qualified source correspondence only.
No stochastic ranking, default change or manuscript change follows. Version 3.44
remains 396 pages, not_ready; 53 obligations, six interactions and 46 operations
are preserved with zero whole-row closures.

Post-run red-team: structure equality alone can hide different annotation
whitespace or omitted comments. The independent exact nonblank-line comparison
and retained diffs make these losses explicit. The three retained schemas cite
the same historical correction date, but that does not establish correspondence
for any other taxonomy or edition. A missed control, wrong bookmark or altered
attribute must invalidate the affected comparison and trigger re-extraction.

Safe replay: verify.py without flags. Never repeat completed one-time stages.
