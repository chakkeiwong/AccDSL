# Skeptical authoring audit and evidence contract

Question: does the finite authored sequence preserve the exact program and runtime
outcomes of the checked typed data baseline? Comparator: DeclaredCompanyProgram/1,
including two charts, two periods and an unknown-finding stopped prefix. The
frontend reuses its semantics; no superiority claim follows from round-trip tests.
Primary pass: full parsed/rendered and compiled engine-program equality, exact
complete/stopped result equality, and checked source spans/import identities.
Veto: unchecked import, invented amount/default/type, silently ignored declaration,
source ambiguity, changed unknown/refusal or future-state hash. Missing fields
must fail at their defined parse/compile/runtime boundary. Counts/time explain only.

| Choice | Provenance/status | Justification | Failure/early check |
|---|---|---|---|
| Four hashed imports | Existing annual import precedent; scoped hypothesis | Reuse explicit checked definitions | Alter/delete/swap each import; compile must fail |
| Line declarations and strict quoted values | Existing lexers; reviewed default | Bounded predictable parsing | Duplicate keys, CRLF, Unicode and token tests |
| Type from registry/memory | Required fixed-schema program contract | One authoritative type declaration | Wrong typed input/reset rejected before projection |
| Author commands, import large definitions | Staged plan | Avoid pretending JSON is a new method language | Manifest states imported vs authored scope |
| 64 commands/inherited byte limit | Existing engine convenience bounds | Preserve bounded work | Exact boundary test; no scale inference |

Premortem: a parse/render pair could share omissions. Compare against the original
engine record and mutate each field. The inherited lexer allows structured JSON,
so this grammar must explicitly reject arrays/objects as scalar input tokens.
Unknown findings must survive unchanged, including prose reasons. Static type
resolution must not inspect hypothetical future balances. Audit passes for this
specified bounded command language; complete company-method authoring remains open.
Store tests, comparison, grammar examples, dependency hashes and result/manifest.
