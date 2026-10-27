# R06 — Full retained fact-concept declaration coverage

18 October 2026. P16/P17/R06/R08; MC01–06/23–25/27/28/30–35.

Question: does every retained fact occurrence join a unique global declaration,
and can its explicitly declared type be traced through the retained definitions
to an XML Schema built-in reference? Compare these source-supported declarations
with the frozen full-file translator's lexical candidate categories. The
comparator is native-full-portable-20261018/native-packet.json and its proposed
portable output. The seven-token inquiry is complete and is preservation
evidence, not work to repeat.

Skeptical audit passes for a source-only coverage inquiry. A global flat
prefix dictionary could resolve the wrong QName when prefixes are rebound;
therefore resolve each attribute using its element's in-scope namespaces.
Repeated facts are occurrences, not duplicate declarations to discard. Inspect
only global declarations in retained schema roots; local declarations cannot
satisfy a global QName join. Preserve missing, ambiguous, unsupported and cyclic
paths explicitly instead of guessing or filling them from an installed package.
QName resolution and derivation traversal are not XSD/XBRL validation.

Primary criterion: account for all 1,127 original fact IDs, retaining their
tokens/context/unit/nil fields and exact declaration/type-chain anchors or an
explicit unresolved reason; preserve the frozen Values and source hashes.
Any claimed resolved join must be unique and every traversed edge source-bound.
Promotion vetoes: namespace error, dropped/reordered occurrence, guessed
declaration, erased restriction, unsupported built-in semantic inference,
validated-value credit or frozen evidence change. An unresolved source join
blocks that join's resolution claim and triggers further source preparation;
it is not a global continuation veto. A corrupted protected source is a
continuation veto. Counts/type/category cross-tabs are explanatory only.

Defaults and assumptions:

| Choice | Provenance and reason | Failure mode and earliest check | Status |
| --- | --- | --- | --- |
| Retained 27-resource map | Prior offline source graph; exact bytes already bound | Not a complete validator schema set; inventory actual schema roots and source hashes first | Documentary baseline |
| Expanded names and scoped prefixes | XML namespace attributes in the retained files | Prefix rebinding or local/global confusion; preserve per-element namespace scope and check global indexes | Required source interpretation |
| Explicit type derivation | Retained element/type declarations | Anonymous types, union/list, cycles or multiple bases; retain as unresolved if unsupported | Bounded traversal hypothesis |
| XML Schema namespace as terminal | Names in source base attributes | A terminal name is mistaken for lexical/value-space validation; label it a terminal reference only | Convenience stopping rule with explicit non-claim |
| Prior lexical candidate tags | Frozen translator output | Numeric-looking token mistaken for a validated number; cross-tab only and never mutate Values | Comparator, not type authority |
| Authoring Python | Standard-library CPU parsing/hashing only | Author environment mistaken for selected production target; keep twelve runtime duties/nulls unchanged | Tooling only |

Pre-mortem: the command could succeed while joining local elements, collapsing
repeated facts or treating a type name as validation. Global-only indexes,
full occurrence preservation, exact excerpts and explicit limits distinguish
those failures. No target/build/default selection is authorised by this unit.

Use only retained local XML, previous JSON evidence and standard-library code.
No network, Arelle import, resolver, installation, GPU or empirical execution.
Planned artifacts: data/accounting-master/native-concept-type-coverage-20261018/
with coverage.json, checks.json, run-manifest.json, result.md and record-once/
read-only replay. Exact command will be recorded in the manifest. Preserve the
seven-token evidence and all protected 3.44/R08 files, add an R08 supplement,
refresh controls, then select the next ready source/specification task.
