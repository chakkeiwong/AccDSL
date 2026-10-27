Read-only substantive review of the P16 governing proposal. Codex remains executor. Do not edit, launch agents, run commands, access network or change state. The background master is stopped. Product runtime implementation is disabled.

The user wants execution here, with one meaningful integrated review, not more controller work. Judge the actual specification and its interactions. Check inconsistent identities/replay/commit claims, status loss, unknown-to-false coercion, scope/admission, hidden defaults, invalid financial or probability arithmetic, omitted reference bindings, unsupported claims and whether a P16 architecture can govern later detailed methods. Distinguish a material P16 architecture defect from explicitly retained P17 method/source obligations and P18/P19 manuscript/readiness work. Do not demand already deferred product runtime or professional review. Missing real E05 conflict and a complete real package remain genuine proposal blockers, not completed evidence.

Return substantive findings with file/section, counterexample, smallest repair and whether they block P16 acceptance. Avoid procedural review chains or file-count criteria. State inspected scope and uninspected limitations. End with VERDICT: AGREE or VERDICT: REVISE.

Executed checks: python3 platform-contract-calculation-v1.py returned 169/169 exact finite checks; accounting-complete-exchanges-diagnostic-v1.py returned 2580/2580 checks including 27 new exchanges, 17 retained controls and V01–V16; unchanged check_accounting_proposal.py --phase P16 --check returned 797/797 structural checks before final canonicalization wording refinement; 932 protected originals unchanged. Those counts are document/structural evidence, not execution of a new compiler, solver or store. Current plan: docs/plans/accounting-p16-direct-execution-20261006.md. Current result and progress: data/accounting-master/deliverables/P16/. Reports: data/accounting-master/direct-p16-20261006/.

Review focus: new four architecture contracts, complete accounting exchanges and matched company calculation.

FILE: docs/design/proposal/architecture/language-ir-contract-v1.md
SHA256: e2cdc3c82d34786364ad4180b0b26581bd8b70eeb6179e4ef6e0e150208bdb1f
1: # Portable financial records and authoring, proposed version 1
2: 
3: The portable representation is the meaning exchanged between extraction,
4: reconstruction, accounting and reporting. Text notation and typed constructors
5: are two ways of proposing those records. Neither authoring path can create an
6: accepted source reading, an accounting permission or a probability merely by
7: constructing a value. This contract addresses MC02–MC14 and MC23–MC27, especially
8: G2/G3/G12/G15/G18. `platform-contract-examples-v1.json` supplies specified examples;
9: the companion calculation checks finite consequences, not a compiler.
10: 
11: ## L1. Representation and version boundary
12: 
13: A `Record` has exactly `kind`, `schema`, `key`, `revision`, `body`, and
14: `dependencies`. `kind` and `schema` name a registered, versioned record
15: definition; `key` is its stable, schema-scoped logical name; `revision` is a
16: nonnegative JSON integer (never Boolean). `body` conforms to that exact schema.
17: `dependencies` is a set of typed `Ref` values. A `Ref` has exactly `kind`,
18: `schema`, `digest`; its target digest covers the entire target record. Links
19: inside a body are also typed Refs and must occur in dependencies. Additional
20: dependencies are permitted only with a declared role in the body's schema.
21: The dependency graph of a submitted closure must be finite and acyclic. A new
22: receipt refers to its request and prior state; the prior state never refers
23: forward to that receipt. Stable business keys may refer to one another as names
24: without creating content-reference cycles.
25: 
26: Each schema declares required, optional and nullable fields separately, and
27: rejects unknown fields. Omission and null are not synonyms. Unknown scientific
28: or accounting content uses `Unknown {reason, obligation_refs}`; an absent required
29: field is an invalid record. A record with unknown content can be retained but
30: cannot satisfy an operation that requires that content. A `Candidate<T>` is
31: distinct from `Admitted<T, view_ref, decision_ref>`. Admission requires checking
32: the referenced decision in the requested immutable view, including ancestors;
33: possession of the wrapper alone is insufficient.
34: 
35: Quantities use reduced exact `Rational {n,d}` with signed base-ten numerator
36: text and positive denominator text: no leading plus or zeroes, `gcd(|n|,d)=1`,
37: zero `0/1`. Decimal source tokens are converted by their base-ten value, never
38: through binary floating point. Integer metadata and integer counts remain JSON
39: integers. This separates the old Core 0 phrase “all numeric values are rational”
40: from record revisions, ordinals and bounded counts. Approximate results instead
41: use `Approximation {decimal_text, method_ref, error_description, environment_ref}`;
42: they cannot be substituted into an exact operation without an explicit
43: approximation policy and its provenance.
44: 
45: New record digests use `SHA256(UTF8("accdsl.portable.v1/" + schema) || 0x00 ||
46: canonical(record))`. Canonical JSON is UTF-8, sorted ASCII object keys, no
47: insignificant whitespace and no floats, NaN, infinity, duplicate keys or invalid
48: Unicode scalar values. Strings retain their decoded code points; JSON escapes
49: and literal Unicode for the same code point are equivalent. Composed and
50: decomposed Unicode are distinct unless a named transformation explicitly maps
51: them. Identifiers are ASCII; financial labels and quoted source text may be
52: Unicode. This deliberately replaces implicit global NFC normalization in the
53: exploratory Core 0 proposal: source spelling must not be silently changed.
54: Raw source identity always hashes original bytes, outside this record encoding.
55: 
56: Array order is meaningful except for schema-declared sets. In this version,
57: `dependencies`, module declarations by key, context dimensions by axis key, and
58: the explicit IR `all_of`/`any_of` operand sets are canonical sets; reject duplicate
59: keys or members before sorting by canonical UTF-8 bytes. All other arrays,
60: including event schedules, journal lines, source spans and diagnostic priority
61: sequences, retain order. Rational reduction and set sorting occur during typed
62: construction; a purported canonical wire record violating them is rejected.
63: There is no general algebraic simplification, alias folding or equivalence proof
64: in hashing. Hash equality supports byte identity under the chosen encoding, not
65: economic equivalence or source truth.
66: 
67: For byte-level interoperability the serializer emits literal valid non-ASCII
68: Unicode scalars in UTF-8. Escape only quotation mark, reverse solidus and control
69: characters U+0000–U+001F: use `\b`, `\t`, `\n`, `\f`, `\r` for their five named
70: controls and lowercase `\u00xx` for the remainder. Do not escape solidus. Integers
71: use minimal base-ten text, with no leading plus, zeroes or negative zero. Input
72: escapes are decoded before canonical output. Object keys are ASCII and ordered
73: by unsigned ASCII bytes. These rules, set normalization and rational reduction
74: fix one byte string for every valid typed record; arbitrary JSON writer defaults
75: are not part of the definition.
76: 
77: Existing `accdsl.replay.v1/*`, uncertainty fixture and Core 0 digests retain
78: their original encodings. `LegacyImport {format, original_bytes_ref,
79: original_id, decoder_ref, portable_ref, comparison_ref}` connects them to a new
80: record. A migration must prove the stated field/value correspondence and retain
81: both IDs. A two-decimal acquisition fixture is not a general two-decimal money
82: rule. No historical digest or receipt is rewritten to fit this proposal.
83: 
84: ## L2. Financial types and context
85: 
86: The primitive types are Bool, Int, Rational, Text, Date, Timestamp, Ref<T> and
87: explicit tagged Unknown. Containers are Option<T>, homogeneous List<T>,
88: schema-declared Set<T>, records and tagged unions. Bool is not Int. Dates use
89: valid Gregorian days; timestamps require an offset and retain the original
90: precision. Timestamp comparison uses the time contract's interval interpretation.
91: 
92: The financial types include `Money<currency>`, `Quantity<unit>`,
93: `Rate<convention>`, `YearFraction<calendar, convention>`, `InstantValue<T>` and
94: `Flow<T, [start,end)>`. Every contextual value carries a Context Ref identifying
95: legal entity, book, perimeter version, basis, currency/unit, economic instant
96: or reporting interval, calendar and a set of dimensions. Source locators,
97: reported display scale and reading provenance are retained alongside the value;
98: they do not silently change its arithmetic magnitude.
99: 
100: Addition, subtraction and comparison require equal financial types and
101: compatible contexts. A source scale is applied once during reading, while its
102: original value and spelling remain available. Entity, perimeter, basis,
103: currency, time or dimension changes require a named transformation with input
104: and output contexts, method, assumptions and evidence. `sumOver` removes an
105: axis only under a pinned disjoint/exhaustive partition. `convert` requires a
106: dated rate, purpose and measurement method. No label similarity converts IFRS
107: into US GAAP; the standards method must supply a transformation or report that
108: the comparison is unresolved.
109: 
110: An opening and closing stock cannot be added as flows. Deriving an interim
111: flow by annual-minus-prior-interim requires compatible interval endpoints,
112: perimeter, basis and revision view. Precision does not create an error tolerance:
113: nearest-rounding intervals require source support or an explicit admitted
114: rounding assumption. A displayed 100 at unit scale may conditionally denote
115: `[199/2,201/2)` only under the declared tie convention; unknown convention
116: remains unknown, and different tie rules have different endpoint inclusion.
117: 
118: ## L3. Expression and model records
119: 
120: An Expression has `key`, `type`, nullable `context_ref` and one discriminated
121: operator payload. Literal carries one typed value; ref names one declaration;
122: negate/not take one operand; add/subtract/multiply/divide/comparisons take two;
123: `all_of`/`any_of` take nonempty operand sets; field takes a record and field key;
124: call carries a pinned operation Ref and ordered arguments. Each operator's
125: payload excludes the other payloads. Boolean expressions remain formulas when
126: their shared symbols are unknown; Unknown values are never coerced to false.
127: 
128: Multiplication by a dimensionless scalar preserves a financial type. A rate is
129: not dimensionless: simple interest requires principal, annual rate and an
130: explicit year fraction. Division requires a nonzero denominator; inability to
131: establish nonzero is an unresolved precondition, while an established zero
132: gives undefined mathematics. Backend admission classifies the expanded formula,
133: not the spelling of a function call. Symbolic products are not rational-linear
134: merely because the surrounding function has an accounting name.
135: 
136: A Module contains declaration sets for contexts, sources, readings,
137: interpretations, assumptions, symbols/domains, constraints, choices,
138: contracts/events, measurements, rules, scenarios and reports, plus a package
139: lock. Every symbol has one uncertainty category, type, domain and admission
140: dependencies. Reusing its key means the same unknown in every linked expression.
141: Global constraints apply to every alternative; a choice-local constraint stays
142: inside that named choice. Alternatives are joined under the history contract's
143: specified union/intersection, not silently intersected or independently selected
144: account by account. No declaration automatically creates a probability measure.
145: 
146: An OperationSignature declares input/output types, context relationships,
147: preconditions, postconditions, failure codes, effects, capability and method/
148: authority dependencies. Effects are one of pure calculation, candidate
149: construction, source acquisition, review proposal or requested transaction.
150: An accounting rule proposes an assessment/journal/delta; it cannot commit.
151: Opaque callbacks or arbitrary host-language execution are not portable IR.
152: Extension packages must declare record schemas and signatures, export hashes
153: and the unsupported-operation response; unknown required semantics cannot be
154: ignored. Names are qualified by package and version; no mutable “latest”.
155: 
156: The portable initial exact fragment permits rational affine constraints over
157: real unknowns plus explicitly finite discrete choices and bounded integers.
158: Negative rates are permitted when the operation's economic domain permits them;
159: the P03 nonnegative-rate restriction is not inherited globally. Unsupported
160: nonlinear, unbounded discrete, distribution or calendar methods return the
161: requested operation and missing capability. Partial linearization is a new
162: assumption-labelled model, never an exact solution of the original formula.
163: 
164: ## L4. Compilation and matched authoring
165: 
166: `CompileRequest` supplies source kind (text or typed construction), source bytes
167: or typed Module, schema/profile refs, full package lock, evidence/time view and
168: requested capability target. Compilation performs, in order: strict decode and
169: source spans; name/import resolution; dependency/cycle checks; static types and
170: context checks; admission-layer checks; expanded-operation capability analysis;
171: canonical record production. Each stage returns all independently decidable
172: diagnostics in stage/path/code order. Dependent checks are `not_evaluated` with
173: their blocking diagnostic; they are not additional guessed type errors.
174: 
175: `CompileResult` returns candidate IR, source map, unresolved input obligations,
176: capability analysis and a validation receipt bound to every input. Invalid
177: structure/types produce no executable IR. A well-typed module can have unresolved
178: financial inputs: return a retained candidate and `execution_admitted=false` for
179: affected targets. Compilation does not call a solver, choose a history, post a
180: journal or turn source acceptance into method eligibility.
181: 
182: The bounded text notation retains Core 0 lexical/precedence rules and its
183: registered declarations. Unsupported syntax is diagnosed; textual support is
184: advertised per declaration/signature. Typed constructors produce the same
185: abstract declarations; arbitrary Python objects or lambdas are not accepted.
186: Both frontends pass through the same typed IR admission rules. Text positions
187: are Unicode code-point half-open ranges in retained source bytes after a named
188: decode; typed positions are constructor paths. Source maps are outside model
189: semantic identity, but their own content hashes bind the exact authored source.
190: Formatting and comments may change a source-map ID without changing the model.
191: 
192: LX01 specifies matched text and typed declarations for debt 100, shared unknown
193: floating share x in [0,1] and interest `100*((1-x)*1/20+x*7/100)`. Both propose
194: the same financial expression and its explicitly conditional stress assumption.
195: Its expanded interest is `5+2x`; endpoints are 5 and 7 and x=1/2 gives 6.
196: The shared domain is continuous, not two equally probable cases. LX02 changes
197: 7/100 to 9/100, so the upper endpoint becomes 9: frontend agreement alone would
198: miss a shared wrong constant, hence the independent arithmetic. LX03–LX08 reject
199: currency/context mixing, absent admission, symbolic nonlinearity at an exact
200: linear backend, duplicate keys and unknown imports. These are proposed expected
201: exchanges; the document calculation is not evidence of a completed compiler.
202: 
203: ## L5. Alternatives and consequences
204: 
205: The old small text compiler and typed library are useful feasibility evidence,
206: but neither settles the portable representation. JSON records are proposed
207: because they are inspectable and already match retained evidence; a binary
208: encoding is permissible as a lossless transport with a specified decoder.
209: Embedding executable Python is rejected as the governing representation because
210: it leaves side effects, evaluation order and unknown handling outside a shared
211: contract. XBRL remains an evidence interchange, ledgers carry concrete postings,
212: and inference languages implement selected methods; none by itself preserves
213: all the required evidence, joint histories and accounting admission layers.
214: No authoring, performance or maintenance superiority has been measured.


FILE: docs/design/proposal/architecture/persistence-contract-v1.md
SHA256: 64930493a2a4683cbb09816f979166b18d27401685fd37772f2aebe35fe1c584
1: # Persistence, correction and recovery, proposed version 1
2: 
3: A completed accounting transition is one committed fact about a particular
4: book and branch. A lost network response must not post it again; a correction
5: must not rewrite what an earlier information view contained. This contract
6: addresses MC04–MC06, MC18, MC25, MC27 and MC33–MC35, especially G17/G18. It
7: specifies observable storage behavior. The examples are transaction traces,
8: not an implemented database or a durability experiment.
9: 
10: ## P1. Ownership and retained objects
11: 
12: One transactional store owns immutable portable records, dependency edges,
13: review snapshots, branch heads, committed journals/state deltas, operation
14: receipts and continuation checkpoints. Original source bytes live in immutable
15: content-addressed storage. A metadata transaction may reference a blob only
16: after its exact bytes are durably available and verified. A crash between blob
17: creation and metadata commit can leave an unreferenced blob; it cannot leave an
18: accepted source reference to absent bytes. Existing originals are retained.
19: Exports, caches, Parquet tables and rendered reports are derivatives of a named
20: store snapshot, not additional writable truth. An export failure does not undo
21: a committed transaction or justify posting again.
22: 
23: Each branch has a stable `branch_key`, an immutable branch definition Ref and a
24: mutable head `(state_ref, generation)`. The branch definition names its family,
25: evidence/model/scenario versions and projection namespace. A separately
26: commissioned hypothetical run uses a new projection namespace/branch key;
27: reopening the same run uses its original key. A branch revision, renamed run or
28: retry cannot evade an event conflict inside that namespace. Aggregating branches
29: requires the declared family/view semantics and never counts projections as
30: multiple realized transactions.
31: 
32: The initial local implementation is proposed to have one logical transaction
33: writer. Multiple clients may submit requests, but the store serializes commits.
34: Other implementations must provide the same atomic comparisons and isolation;
35: “single writer” is not permission to omit stale-state checks. SQLite is an
36: implementation candidate based on P07's bounded probe. Distributed consensus,
37: specific filesystem durability and physical media failure guarantees require
38: their own implementation and evidence; no document calculation establishes them.
39: 
40: ## P2. Event commit and replay
41: 
42: The stable accounting lookup key remains the tuple `(entity_id, book_id,
43: branch_key, business_event_id)` from accounting-replay-contract-v1. Event version,
44: payload and expected opening state belong to the complete request fingerprint,
45: not the lookup key. The generic Core 0 run/event key is historical exploratory
46: evidence and does not override this rule. Legacy fixture digests are retained
47: through the import mapping in L1, never silently compared with portable digests.
48: 
49: For one requested event the store performs:
50: 
51: 1. Validate the request's decoding, field shapes, exact reference closure,
52:    internal bindings and admissible historical context. Corrupt or inconsistent
53:    input fails before any receipt lookup. Validate independent fields in the
54:    declared stage order; do not derive fresh accounting assumptions here.
55: 2. Read the committed receipt index under the stable key. An equal fingerprint
56:    returns the original immutable receipt with `additional_commit=false`.
57:    A different fingerprint yields `EVENT_ID_CONFLICT`, including when its event
58:    version differs. Replaying a valid historical request is not reassessment
59:    against today's source or method version.
60: 3. For an absent key, compare both expected opening state and expected head
61:    generation. A mismatch returns `STALE_OPENING_STATE`. Assess treatment and
62:    construct the candidate journal, economic delta and closing state outside
63:    mutation. Arithmetic/balance alone cannot authorize a treatment.
64: 4. In one transaction, recheck absent key and the same head comparison, validate
65:    the candidate dependencies, then insert the journal, delta, closing state,
66:    dependency edges and immutable committed receipt, and advance the head.
67:    Commit all or none. A competing identical commit returns the original
68:    receipt; a different fingerprint conflicts; a competing different event
69:    advancing the head makes this request stale. No speculative candidate is
70:    published as committed while the comparison is unresolved.
71: 
72: The observation returned with replay may identify today's branch head, but the
73: receipt's original opening/closing states, assessment and journal never change.
74: The four accounting domains in the existing fixtures—state, journal registry,
75: delta registry and committed receipt index—remain identical on rejection/replay.
76: Candidate scratch data and diagnostics are not members of those domains.
77: Rejected requests may append a separately typed audit record after validation;
78: it cannot appear in the committed event index or count as an economic transition.
79: If an operation promises an audit receipt and its audit write fails, report that
80: failure explicitly while retaining the established unchanged-domain outcome.
81: 
82: ## P3. Crash ambiguity, resume and exports
83: 
84: A response has `commit_observation` equal to `committed`, `not_committed` or
85: `unknown`. A crash before the atomic commit leaves the old head and no new
86: receipt. A crash after commit but before acknowledgement leaves the complete
87: new head and receipt. The client's timeout alone cannot distinguish those cases;
88: return `unknown` with the original key/fingerprint and query/retry that identity.
89: Do not retry under a fresh event ID. Once storage recovers, receipt lookup
90: resolves the ambiguity. Missing/corrupt committed dependencies are an integrity
91: failure, not a reason to reconstruct an apparently similar receipt.
92: 
93: A search checkpoint atomically records the semantic manifest, partition identity,
94: completed/explored cells, preserved unresolved formulas/regions, frontier order,
95: budget used and resulting objects. A cell is not complete before its evidence
96: and frontier transition commit together. Resume requires the original semantic
97: manifest and partition/traversal identity. An increased explicitly supplied
98: budget is a new scheduling request linked to the old checkpoint, not a new
99: financial model. Changed source, context, method, scenario, family or ordering
100: requires a new applicable manifest and a stated reuse relation; it cannot reuse
101: an old suffix by position. Cancellation preserves the last committed frontier.
102: 
103: Immutable export manifests name every record/blob, format/decoder, digest,
104: root query/view and required reference closure. Stage an export in a temporary
105: location, verify its closure, then publish its manifest atomically. An incomplete
106: export is explicitly incomplete and cannot be loaded as a closed bundle. Import
107: verifies all referenced bytes before committing metadata; an unavailable
108: optional attachment remains a located coverage obligation. Missing required
109: closure rejects dependent use, even if the manifest itself hashes correctly.
110: 
111: ## P4. Review, correction and invalidation
112: 
113: Source and review requests have their own idempotency namespace
114: `(operation_kind, workspace_key, request_id)` and fingerprints. A repeated exact
115: request returns its immutable receipt; changed payload conflicts. A new review
116: uses an expected prior view and generation. It records reviewer, rationale,
117: accepted layer, referenced evidence and operation (propose, accept,
118: accept-alternative, reject or supersede). Legal state transitions follow the
119: evidence contract. Self-supersession and mismatched replacement scope reject
120: before mutation. Only review admission records can advance a reading's layer.
121: 
122: A new immutable view records its parent, changed decisions and dependency
123: selection revisions. It never mutates the old view. Invalidation follows the
124: reverse dependency graph transitively, including dependencies on candidate-set
125: membership, not only on the previously chosen members. Therefore adding a newly
126: eligible filing can stale a selection that formerly had one member. Newly
127: created descendants must check all ancestors against their requested view;
128: they cannot escape invalidation by being created after the invalidation scan.
129: Unrelated dependency closures remain usable. `explain` always uses the output's
130: frozen view; a current-view query explicitly reports stale dependencies.
131: 
132: A correction to an economic event is a new business event linked to its
133: predecessor and a specified correction method (reversal/replacement or a dated
134: adjustment, as applicable). It does not overwrite the original receipt and a
135: version bump alone does not post it. Corrected historical disclosure creates a
136: new evidence/model projection; it does not retroactively change what an investor
137: or the system knew. P17 supplies the accounting treatment of each correction;
138: missing treatment authority remains unresolved rather than a generic reversal.
139: 
140: ## P5. Migration and reproducibility
141: 
142: Migration input is `(old_schema, new_schema, migration_method_ref, source_snapshot,
143: expected_head, declared_semantic_relation)`. Output retains original bytes/IDs,
144: new bytes/IDs, a complete mapping and the comparison evidence. A
145: representation-only migration must preserve decoded typed quantities, contexts,
146: uncertainty categories, references, admission states, event identities and exact
147: reference-query outcomes. Invertibility over the retained source domain or an
148: explicit lossless retained original is required. Changed model meaning, rounding,
149: calendar, probability or operation order is a new model/version, not a successful
150: representation-only migration. Failed mapping or comparison leaves all prior
151: heads and objects usable; migration never silently fills missing metadata.
152: 
153: Replay locks the model, view, package/calculator versions, scenario, requested
154: outputs, numeric/calendar policies, algorithm/capability manifest and relevant
155: environment. Exact rational operations require exact equality. Approximate
156: operations require predeclared method-specific error comparisons and retain both
157: values; a generic float tolerance cannot establish financial equivalence.
158: Random-stream identity names seed, coupling group, economic owner, date,
159: shock-kind and draw index, with pinned generator and transforms. Branch traversal
160: position is absent. The retained SHA-based reference primitive remains only an
161: identity illustration; no production generator or calibration is selected here.
162: 
163: PX01–PX08 in the shared examples specify lost acknowledgement, exact replay,
164: changed payload, two writers at one head, correction invalidation, branch
165: isolation, incomplete export and migration outcomes. Their finite traces make
166: the expected behavior reviewable. The future implementation must additionally
167: pass crash/reopen/fault-injection tests on the selected storage/environment.
168: 
169: ## P6. Alternatives and tradeoffs
170: 
171: Mutable documents with periodic checkpoints cannot establish the atomic
172: receipt/state relation above without an additional transaction protocol.
173: An event log with deterministic projections is viable if its commit marker,
174: projection visibility and replay checkpoints obey the same contract. The
175: proposed transactional metadata store plus immutable blobs separates large
176: source bytes from small atomic changes and fits existing local probes. Its
177: single-writer throughput and crash guarantees are unmeasured. Analytics engines
178: and storage libraries remain replaceable behind these observable semantics.


FILE: docs/design/proposal/architecture/interfaces-contract-v1.md
SHA256: a7235c3485e8942a6a0e4251ae893d3f531a7ea601ad62f506a57936975ca491
1: # Operations across the financial model, proposed version 1
2: 
3: The interfaces connect an acquired disclosure to a proposed reading, an admitted
4: financial model, alternative histories and conditional statements. Each operation
5: names the version it consumes and the authority it needs. In particular, an
6: extraction service cannot accept its own interpretation, a valuation service
7: cannot authorize accounting, and a report cannot commit journals. This contract
8: addresses MC01–MC27 and MC33–MC35, with the software obligations of MC29–MC32.
9: It specifies exchanges; it does not provide runtime endpoints.
10: 
11: ## I1. Common request and response
12: 
13: `OperationRequest` is a portable L1 record with schema
14: `accdsl.operation.request.v1`. Its body has exactly:
15: 
16: | Field | Required type and meaning |
17: | --- | --- |
18: | `operation` | Qualified operation name from I2; no implicit version selection |
19: | `request_id` | ASCII identifier, stable across retries of the same request |
20: | `workspace_key` | ASCII identifier for the store namespace |
21: | `profile_ref`, `signature_ref` | Exact profile and operation-signature Refs |
22: | `view_ref` | Immutable evidence/review/time view Ref; never a mutable `current` alias |
23: | `arguments` | Closed tagged record for the named signature, with fields in I2 |
24: | `execution` | `{mode, budget, environment_ref}`; mode is `specification_example` or `runtime`; budget explicitly states operation count and elapsed-time limits or a reason each is inapplicable |
25: | `expected_head` | Null for a read, or `{owner_key, state_ref, generation}` for a requested mutation |
26: 
27: All fields are present. Null is allowed only where stated. A caller asking for
28: the current view first resolves it and receives its revision; mutation compares
29: that revision again. Arguments contain typed Refs and typed values, never
30: arbitrary host-language objects. Required closure is the transitive closure of
31: request dependencies plus schema/package definitions in its lock. A missing
32: optional source attachment remains a named coverage obligation; a missing
33: required rule, record, admission or decoder rejects affected use. Schema version,
34: argument type or unsupported operation is diagnosed before calculation. A
35: request fingerprint covers the exact portable request; accounting's historical
36: fingerprint is retained by an explicit legacy adapter, not recomputed as this one.
37: 
38: `OperationResult` has exactly `request_ref`, `operation`, `input_view_ref`,
39: `disposition`, `statuses`, `payload`, `diagnostics`, `coverage`, `unresolved`,
40: `continuation_ref`, `commit_observation`, `receipt_ref`, and `evidence_mode`.
41: References are typed. The last two references may be null. `payload` is a tagged
42: union selected by the signature; rejected input has null payload. `diagnostics`
43: and `unresolved` are ordered lists (possibly empty). `coverage` contains the
44: requested domain Ref and completed/unresolved/unsupported/infeasible/cancelled
45: region Refs, with their partition/overlap relation. Reads may use one singleton
46: request region; they cannot invent an economic-family denominator. `statuses`
47: and disposition obey F1. `evidence_mode` repeats specification/runtime, so an
48: expected `complete` in a document never asserts runtime execution.
49: 
50: `commit_observation` describes the mutation requested by this operation:
51: `committed`, `not_committed`, or `unknown`. A read returns `not_committed` even
52: when it inspects an earlier committed receipt. Accounting's replay payload may
53: say the original event is committed while the outer result says this invocation
54: made no new commit. The payload must carry `additional_commit=false`; this is
55: not a contradiction. A successful review or checkpoint mutation has its own
56: receipt and is never described as an accounting posting.
57: 
58: Transport status and financial status are independent. An HTTP error or client
59: timeout is not evidence of noncommit. A local Python, CLI or service binding
60: must preserve the same argument values, input versions and result union. There
61: is no required network deployment, server framework or user interface in P16.
62: 
63: ## I2. Operation signatures and ownership
64: 
65: In this table each listed input is required unless explicitly marked optional.
66: Lists are explicit even when empty. Domain records retain the detailed fields
67: in their named contracts; the table does not replace them with untyped prose.
68: 
69: | Versioned operation | Arguments → payload | Effect and controlling contract |
70: | --- | --- | --- |
71: | `source.prepare@1` | package manifest, source snapshot, adapter/config lock, prior review, traversal budget and optional continuation → ExtractionPreparation | Acquires/preserves sources and constructs candidates under extraction-v1; no semantic admission |
72: | `review.propose@1` | target Ref, layer, decision kind, evidence Refs, actor, rationale, replacement Ref or null → ReviewProposal | Candidate construction; accepts no layer |
73: | `review.commit@1` | ReviewProposal, expected review view/revision → immutable ReviewDecision and new view | Review transaction under evidence E4/persistence P4; admissible action/layer required |
74: | `time.select@1` | package/view, investor/system/exploratory mode, cutoffs, revision and unknown-time policy → selected assertions, conflicts and temporal obligations | Pure selection under time T1–T6; no invented ingestion or publication time |
75: | `model.compile@1` | CompileRequest from L4 → candidate Module, source map, diagnostics and target admission/capability report | Candidate construction; no solver or posting |
76: | `history.construct@1` | admitted Module, opening, scope, template registry, query/horizon, resource budget → HistoryFamily, partition, witnesses and unresolved formulas | H1–H7; witnesses are examples within the family, not its definition |
77: | `history.refine@1` | frozen family, additional admitted constraint or refinement, dependency view, budget → child family and inclusion relation | Candidate construction; record whether correction replaces constraints instead of intersecting them |
78: | `history.query@1` | family, typed joint observable, bound/feasibility request, capability manifest → symbolic/partial/exact answer, coverage and endpoint attainability | Pure; unsupported expressions remain explicit |
79: | `uncertainty.evaluate@1` | exact native uncertainty request, law/attachment/admission and operation-specific event or observation block → native UncertaintyResult and candidate derived bundle | Native admission/attachment/chaining rules; never selects its result automatically |
80: | `uncertainty.admit@1` | candidate bundle, target time/evidence/purpose, actor, rationale, requested assumption scope, expected selection revision → admitted attachment and decision | Admission transaction; author-stipulated measures keep that label |
81: | `uncertainty.select@1` | admitted attachment/receipt, rationale and expected selection revision → new selected-view revision | Selection transaction; no probability recomputation |
82: | `scenario.project@1` | family, exogenous scenario, policy/method lock, horizon/calendar, explicit information policy, resource budget → conditional event/journal/state proposals by history and scenario | Candidate construction; budgets preserve unresolved regions; no historical-book commit |
83: | `accounting.assess@1` | native assessment request, event, opening, context/time, authority/method, evidence/assumptions and admissions → TreatmentAssessment | Pure accounting assessment; inherited `assess_only` profile cannot post |
84: | `accounting.propose@1` | eligible assessment, exact request/opening, posting/rounding method → JournalProposal and independent EconomicDelta | Candidate construction; revalidate bindings; unsupported method gives no journal |
85: | `accounting.commit@1` | validated commit request, eligible assessment, proposal/delta and expected branch head/generation → StateTransitionReceipt | Single atomic transaction in P2; separate signature from assess-only |
86: | `report.build@1` | frozen branch/family result, statement-map version, interval/view, typed requested statements and presentation policy → joint statement family, reconciliation and coverage | Pure; derive from retained state/journals, no balancing plug or hidden branch selection |
87: | `record.explain@1` | output Ref, its frozen view, requested lineage depth → source/method/assumption/decision paths and unresolved dependencies | Pure; depth truncation is explicit; cannot substitute today's view |
88: | `work.resume@1` | checkpoint Ref, original semantic manifest, scheduling budget → operation-specific resumed result | Resume the original operation; checkpoint ownership/atomicity in P3; no model change hidden as resume |
89: | `store.export@1` | snapshot/root Refs, format/decoder, destination → closed manifest or explicit incomplete export | Derivative publication under P3; no domain mutation |
90: | `store.import@1` | closed manifest, exact blobs/records, decoder and target namespace → import receipt and original-to-local mappings | Verify before metadata transaction; import alone grants no financial admission |
91: | `store.migrate@1` | migration request from P5 → preserved originals, new representation, comparison/mapping and receipt | Transaction only after required semantic comparisons; no changed-model-as-format claim |
92: 
93: Compilation and history queries may be pure with respect to committed accounting
94: state while producing immutable candidates in a scratch or candidate store.
95: Persisting those candidates requires the named owner and receipt. The effect
96: classification is not a promise that no bytes are written anywhere.
97: 
98: ## I3. Scenario information and joint statements
99: 
100: The initial `ExogenousScenario` specifies dated values or formulas for named
101: drivers, their domains, units, admissibility assumptions and dependencies. An
102: `InformationView` exposed to a policy or measurement operation contains only
103: admitted historical information up to its decision instant and permitted
104: simulated past. Future simulated values are withheld, even when the scheduler
105: already knows the full imposed path. Deterministic stress does not by itself
106: authorize perfect-foresight decisions; a separate assumption must do that.
107: Observational conditioning uses the uncertainty interface. A causal intervention
108: requires a specified causal model/replacement operation and is unsupported by
109: the initial exogenous profile.
110: 
111: The result remains indexed by history, admissible treatment and scenario. Every
112: statement amount refers to that common index, opening and event sequence.
113: Cash flow, profit, balance sheet and equity movement are reconciled jointly.
114: Reporting may return separate conditional answers or a pushforward of an
115: admitted law. It cannot create one statement from independent minima/maxima
116: that occur in incompatible histories. Aggregating an axis requires a pinned
117: disjoint/exhaustive partition or returns an unallocated residual with a reason.
118: An unsupported tax/lease/FX method makes dependent lines unresolved; unaffected
119: amounts remain available with their dependence stated.
120: 
121: ## I4. Extension boundary and adapters
122: 
123: An `ExtensionPackage` declares `{package_key, version, record_schemas,
124: operation_signatures, supported_contexts, state_requirements, authority_refs,
125: method_refs, capability_requirements, migration_refs, example_refs}` and pins
126: every member. Empty authority lists mean no accounting-authority claim, not
127: universal eligibility. Callers verify the method's dated entity/instrument/basis
128: scope and uncertainty admission separately from schema loading.
129: 
130: Corporate records retain receivable/payable terms, inventory lots and cost
131: method, assets and depreciation memory, tax bases, leases, debt/equity rights
132: and contingencies. Groups retain legal entity, control evidence, dated perimeter,
133: ownership/NCI, functional/presentation currencies and elimination links. Banks
134: add cash-flow terms, effective rate, credit-risk stage, default/cure history,
135: collateral/guarantees and prudential-rule context; prudential capital is not
136: accounting equity. Insurers add coverage units, cohort/group eligibility,
137: fulfilment cash-flow assumptions, discount/risk adjustment, CSM/loss component,
138: reinsurance and service history. These are structural obligations; P17 must
139: specify their method fields, transitions, authority and matched cases before an
140: operation using them becomes supported.
141: 
142: An extraction adapter returns located candidates; a contract scheduler returns
143: dated contractual events; a valuation adapter returns a quantity with method,
144: currency/date and numerical evidence; an accounting method returns an assessment
145: and proposed entries; a ledger adapter exchanges concrete entries/receipts.
146: None inherits another's authority. Each adapter manifest identifies upstream
147: version/license, supported subset, input/output schema mapping, calendar/unit/
148: rounding transformations, preserved lineage, information loss and unavailable-
149: backend behavior. Lost economically relevant fields veto that exchange. Retaining
150: raw upstream output permits inspection but does not repair lost meaning.
151: P17 owns pinned official-interface/license inspection and executable adapter
152: feasibility; existing exploratory tool presence is not completed integration.
153: 
154: ## I5. Precedence and versioning
155: 
156: The active P16 architecture index pins its contracts. Domain-specific validation
157: and accounting/uncertainty vocabulary take precedence within their versioned
158: native interfaces. Platform v1 adds explicit wrappers and cross-contract rules;
159: it does not rewrite saved native receipts. `architecture-integration-v1.md`
160: records status mapping and the precise historical rules that are superseded.
161: A later amendment prevails only for the fields and profile it expressly names;
162: date alone or a file named “latest” grants no precedence.
163: 
164: Two conflicts are resolved explicitly. The stable accounting event key is P2's
165: entity/book/branch/business-event key, not an event-version or transient-run key.
166: For native assessment validation, the established parse → recognizable
167: dependencies → shape → source versions → bindings sequence prevails over a
168: generic platform ordering. A wrapper may reject its own malformed envelope
169: first; it cannot expose a receipt before native validation. New portable-only
170: operations use F2's order. This preserves historical outcomes without letting
171: the old generic Core 0 contracts silently select defaults for new domains.
172: 
173: IX01–IX06 in the shared example file cover a connected company, changed stress,
174: an unresolved operating input, later-information rejection, overlapping report
175: classes and a sector call without an eligible method. Together with the native
176: complete accounting exchanges they make the contracts' interaction inspectable.
177: They specify results; the document calculation verifies only finite arithmetic
178: and reference consistency. Compatible implementations still require actual
179: frontend, backend, storage and recovery conformance evidence.


FILE: docs/design/proposal/architecture/failure-contract-v1.md
SHA256: 1de4e0151e5c6c8311aa7d4695134c7ee419501384a79ff227c66ad8bb79cdf6
1: # Results, incomplete work and failures, proposed version 1
2: 
3: A missing source, an insolvent company and a crashed solver are different
4: outcomes. Combining them into “failed” would either lose admissible histories or
5: publish results with stronger meaning than the evidence permits. This contract
6: addresses MC08–MC14, MC18, MC25 and MC33–MC35 and integrates the existing
7: uncertainty and accounting status rules.
8: 
9: ## F1. Independent result dimensions
10: 
11: Every public operation returns an `OperationResult` bound to its request and
12: input snapshot. It contains a disposition, status envelope, typed payload,
13: diagnostics, unresolved obligations, domain coverage, nullable continuation and
14: commit observation. Disposition is one of `completed`, `partial`, `rejected`,
15: `unsupported`, `cancelled`, `internal_failure`, `commit_unknown` or `replayed`.
16: It is not an accounting conclusion. Successful completion within a declared
17: scope does not imply that scope describes every real history or disclosure.
18: 
19: The existing uncertainty envelope remains normative: structural validity,
20: mathematical status, computation status, empirical justification, capability
21: status, accounting validity and human acceptance have separate fields. An adapter preserves
22: the exact domain-native vocabulary in the payload; it does not invent a Boolean
23: “passed” from them. In particular, a pre-evaluation rejection uses
24: `structural_validity=invalid`, `mathematical_status=unresolved` and
25: `computation_status=not_computed`, as the rejection-status supplement requires.
26: Mathematical status cannot be `not_computed`. Empirical/capability/accounting/
27: human fields are copied from the governing operation evidence in their native
28: vocabulary, never assumed accepted.
29: 
30: For new platform envelopes, structural validity is `valid` or `invalid`;
31: mathematical status is `defined`, `undefined`, `unresolved`, `infeasible` or
32: `not_applicable`; computation status is `complete`, `partial`, `not_computed`,
33: `cancelled` or `failed`. Domain-native subreceipts keep their own named schema
34: and vocabulary. The platform does not rewrite historical receipts to these
35: labels: its explicit versioned adapter maps their stated meaning. New platform
36: envelopes additionally retain `empirical_justification`, `capability_status`,
37: `accounting_validity`, `forecast_validity`, `product_readiness` and
38: `human_acceptance`. The first three copy a supported native value or use
39: `not_established`, `specified_only_no_runtime`, `not_assessed` respectively;
40: the last three are `not_assessed`, `not_implemented`, `pending` in these examples.
41: No map turns `specified_exact` into a claim of runtime execution: evidence mode
42: remains `specification_example`. The explicit mappings and unsupported cases
43: are in architecture-integration-v1.md.
44: 
45: Mathematical `infeasible` requires established emptiness of the declared model;
46: solver silence gives `unresolved`. Conditioning on a zero-probability event
47: under the specified finite law is `undefined`, even if computing its zero
48: normalizer completed successfully. A feasible symbolic family may have a
49: partial search. An economically defined default event is an outcome of a
50: successfully evaluated scenario when its default method is supported; it is not
51: a solver failure. A positive balance check establishes none of the accounting,
52: forecast, product or human acceptance fields.
53: 
54: ## F2. Diagnostic and rejection order
55: 
56: `Diagnostic` has code, stage, record Ref or submitted-byte Ref, source locator,
57: field path, affected query/branch IDs, dependency path, observed value/category,
58: expected rule, retry advice and blocking diagnostic IDs. No fabricated numeric
59: substitute appears in place of an unavailable observation. Diagnostic prose
60: explains a typed code but cannot supply missing economic facts.
61: 
62: For new portable-only operations the stages are decode; field shape; reference integrity; cross-record
63: binding/context/time admission; capability/admission; requested calculation;
64: transaction comparison; publication. An operation may refine these stages,
65: but cannot reverse a required domain ordering. Existing native accounting uses
66: parse → recognizable dependencies → shape → source versions → bindings, as
67: specified in the field-validation supplement. For accounting, all specified
68: source field/binding checks precede receipt lookup; lookup precedes new-event
69: freshness and treatment calculation. Retried historical requests use their
70: pinned historical context, not today's review view. Domain profiles identify
71: which preconditions are checked before lookup and which only for a new event.
72: 
73: Return all independently decidable diagnostics within the earliest failed stage,
74: sorted by schema-defined stage rank, canonical field path and code. Later stages
75: are explicitly not evaluated. A malformed parent/controller suppresses its
76: dependent child predicates; it does not suppress independent sibling findings.
77: This incorporates the guarded C03/C05/C07/C09/C10 reason rules without turning
78: an unknown route into false or promoting contextual prose into evidence.
79: Invalid requests return no candidate result that could be used as admitted
80: output. Retained submitted bytes and separate audit receipts remain available.
81: 
82: ## F3. Preserve the requested domain
83: 
84: Every aggregate identifies the full requested family/view/scenario domain and
85: partitions its work into completed, unresolved, unsupported, infeasible and
86: cancelled regions. Regions are predicates with identities and coverage relations,
87: not just counts. Overlap is explicitly represented or removed under a proven
88: partition; unexplored formulas remain available. A partial result states which
89: queries depend on unresolved regions and which are unaffected. “No completed
90: regions” is not an empty family.
91: 
92: With an admitted joint law, retain assigned mass for all regions, including
93: unsupported or failed evaluations. Do not renormalize successful regions.
94: Example FX01 assigns mass 3/5 to a path returning cash 120 and 2/5 to a path
95: whose calculation is unavailable. The returned known cash mass is 3/5 and
96: unresolved mass 2/5; neither mean 120 nor a complete cash distribution is
97: authorized. If the unresolved path has independently established cash bounds
98: [80,110], the unconditional mean is bounded by [104,116]; without those bounds
99: even that interval is unsupported. Computing a conditional mean given successful
100: evaluation is a different estimand and requires an explicitly requested,
101: meaningful conditioning event; computational success is not economic evidence.
102: 
103: Without an admitted law, return joint feasible regions or per-history conditional
104: results, never weights derived from witness/branch counts. Interval endpoints
105: from partial exploration are explored-only. An exact bound must identify the
106: full formula, proof/certificate or checked exact method, endpoint attainability
107: and numerical policy. A supremum of 1 for x<1 is not an attained maximum.
108: Approximate bounds retain method, error description and missing coverage.
109: 
110: ## F4. Retry, cancellation and integrity
111: 
112: Retry advice distinguishes `same_request_after_service_recovery`,
113: `inspect_commit_then_retry_same_identity`, `new_request_after_input_repair`,
114: `new_model_or_capability_required` and `no_automatic_retry`. A model-input repair
115: gets a new fingerprint; it cannot reuse an existing business-event key to hide
116: a conflict. Availability failures preserve input and work checkpoints; an
117: unknown commit must first be reconciled under its original identity.
118: 
119: Caller cancellation stops new work at the next interruptible boundary and
120: returns the last committed checkpoint. Already committed events are not rolled
121: back by a cancelled response. Cancellation during a storage call may yield
122: unknown commit observation until recovery. A callback that cannot be interrupted
123: requires an external resource limit and a recoverable process boundary; a
124: cooperative progress report is not proof that a commit did or did not occur.
125: 
126: A mismatched required digest, invalid dependency cycle, corrupted committed
127: record or inconsistent checkpoint is an integrity veto on affected use. Preserve
128: the invalid bytes and report the mismatch. Do not resume, fabricate replacement
129: evidence or relabel the error as financial infeasibility. An unrelated corrupt
130: source does not block a query whose complete dependency closure excludes it.
131: 
132: FX02–FX07 specify zero conditioning mass, unsupported nonlinear bounds, economic
133: default, a timed-out worker, malformed source fields and unknown commit. They
134: make both allowed and forbidden conclusions explicit. The checks are finite
135: examples of the proposed semantics; accounting authority, empirical forecast
136: quality and production recovery remain separate evidence obligations.
137: 
138: ## F5. Alternatives
139: 
140: A single success flag is simpler to transmit but conflates mathematical meaning,
141: computation, admission and acceptance. Throwing an exception for every partial
142: branch loses useful unaffected results and encourages selection bias. The
143: proposed typed result plus diagnostics preserves partial work while making
144: invalid or unsupported calculations unusable as complete results. Exceptions
145: may still signal implementation faults internally, but the public boundary
146: must retain the submitted identity, commit uncertainty and last durable work.


FILE: docs/design/proposal/architecture/initial-profile-v1.md
SHA256: 7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb
1: # Proposed first implementation profile
2: 
3: The first implementation should connect a company's disclosures, alternative
4: histories, economic events and complete statements. A financing-only example
5: would leave the working-capital, operating-asset, tax and reporting interfaces
6: untested. The proposed domain is therefore a bounded corporate company; the
7: initial authoring interface is typed constructors into the portable IR, with a
8: matched, bounded textual notation. These are separate choices. This proposal
9: addresses MC01–MC35 without asserting that every requested method is now supplied.
10: 
11: ## Scope and the alternatives compared
12: 
13: P15 compared four candidates. Corporate/shared-IR and typed-library-first can
14: have exactly the same domain and differ only in authoring. Instrument-first
15: would make financing lifecycle work earlier, but cannot meet the whole-company
16: goal until the operating-company continuation is added. Broad sector-first
17: would require bank, insurance, group and cross-standard methods at entry, with
18: more currently unresolved authority. The chosen order exposes interactions in
19: one connected company while specifying extension requirements now. It does not
20: establish that this order is cheapest, fastest or easiest to use.
21: 
22: The profile is `CorporateJointHistory/1`. It includes one legal entity and book
23: per branch, a declared domestic functional currency, annual/interim evidence,
24: multiple source vintages and reviewed alternatives. Context and schema design
25: retain multiple-entity/perimeter/currency fields so an unsupported operation
26: is explicit. “One book” is an execution scope, not a global uniqueness rule for
27: companies or future groups. A company with subsidiaries, leases or contingencies
28: cannot be admitted as a closed single-company model merely by omitting them.
29: 
30: Evidence preparation must account for the declared statement and note inventory,
31: incorporated references and unresolved source units. Readings, interpretations,+assumptions and treatment eligibility are separate layers. Investor-information,
32: system-as-of and exploratory archival questions use the time contract's distinct
33: admission rules. Exact financial quantities, source precision and conditional
34: rounding assumptions remain distinct. Source limitations accompany each dependent
35: query; there is no global “complete” flag inferred from pages parsed.
36: 
37: The initial economic methods must connect sales/delivery/collection, purchases/
38: inventory/cost of sales/payables, payroll, tangible-asset additions/depreciation,
39: simple debt/equity/dividends and a declared simple tax model. They produce profit,
40: balance sheet, cash flows and changes in equity from the same event histories.
41: The simple tax model is an authored teaching assumption; actual tax requires
42: P17's jurisdictional method. Northstar supplies a closed synthetic example,
43: not proof that these methods cover Apple or a representative real issuer.
44: 
45: The initial reconstruction method is the history contract's admitted-template,
46: rational affine family with finite choices and bounded integers. It preserves
47: unidentified debt mix, unknown payment timing and other query-relevant state.
48: The declared half-year event slots do not recover invoices or prove daily
49: liquidity. Querying a finer horizon requires refinement or an unresolved answer.
50: Exact bounds require whole-domain reasoning and endpoint attainability; search
51: witnesses and explored extrema are not promoted to complete families or bounds.
52: 
53: Scenario execution initially supports imposed exogenous paths with explicit
54: behavior and information restrictions. Joint finite rational probability is an
55: optional extension under the admitted-measure contract. Unweighted alternatives
56: remain valid initial results. Continuous inference, causal interventions,
57: calibration and empirically validated forecasts require P17 methods and later
58: execution evidence. An imposed interest-rate stress does not reweight historical
59: contract alternatives or become a probability forecast.
60: 
61: Typed constructors must express all included records without embedding opaque
62: Python functions. The bounded text frontend initially covers the matched debt
63: and constraint fragment; unsupported declarations produce located diagnostics.
64: Textual whole-company authoring is a later frontend obligation, with the same
65: domain semantics and validation. Deferring that parser does not defer the
66: whole-company typed model, the DSL design or the portable representation.
67: 
68: ## Acceptance examples and limits
69: 
70: The primary integrated example is the protected Northstar disclosure fixture
71: and chapter, interpreted through the new contracts. Its opening and half-year
72: events support independently calculable statements and a continuous debt family.
73: For the 2025 stress, let x be the floating fraction. The common joint result is:
74: 
75: | Quantity | Conditional value in currency units |
76: | --- | --- |
77: | Debt interest | 5 + 2x |
78: | Profit before tax | 82 − 2x |
79: | Tax at the stipulated 20% rate | 16.4 − 0.4x |
80: | Profit | 65.6 − 1.6x |
81: | Operating cash flow | 48.6 − 1.6x |
82: | Closing cash | 95.2 − 1.6x |
83: | Closing equity | 148.2 − 1.6x |
84: | Closing assets | 288.2 − 1.6x |
85: 
86: Here 0 ≤ x ≤ 1, payables plus debt are 140, receivables 55, inventory 40 and
87: net plant 98. Every row uses the same x. The endpoints are not equiprobable
88: scenarios, and the output is not a rectangular box of independently selectable
89: amounts. Changing the floating rate to 9% changes the interest slope to 4 and
90: the cash/profit/equity slopes to −3.2; independent arithmetic must detect that
91: change even if both frontends share an erroneous constant.
92: 
93: Acceptance of the specification requires exact expected exchanges for the
94: following connected cases, with preserved sources and explicit assumptions:
95: 
96: 1. Annual/interim source inventory, missing incorporated reference, alternative
97:    narrative translation, rounding unknowns and separately admitted constraints.
98: 2. Joint working-capital reconstruction and unidentified fixed/floating debt
99:    mix, with known aggregate movements and unknown intraperiod timing.
100: 3. Conditional 2025 events, eligible treatments, balanced proposals, reconciled
101:    complete statements and debt-mix dependence, plus a changed-rate control.
102: 4. Original versus corrected interim information views without later-information
103:    leakage; no automatic source-derived accounting permission.
104: 5. Partial or unsupported region preservation, unavailable methods, exact versus
105:    approximate capabilities and unweighted versus admitted-measure queries.
106: 6. Valid replay, changed-payload conflict, concurrent stale-head rejection,
107:    unknown commit recovery, review correction/invalidation and failed migration.
108: 
109: The shared platform examples exercise these connections alongside retained
110: evidence/time/history/uncertainty/accounting examples. A bounded real filing
111: case must retain its full declared inventory and all unformalized disclosures;
112: Apple's partial source preparation cannot satisfy that case by itself. E05's
113: real source-backed conflict and P17's dated accounting methods remain proposal
114: work. A document calculation satisfies only the finite arithmetic part of this
115: list. Runtime acceptance additionally needs implemented source/typed lowering,
116: solver/simulator, transaction fault tests and adapter checks. Human understanding
117: and accounting/forecast validity have separate evidence.
118: 
119: ## Dependencies and retained later work
120: 
121: Implementation should proceed in dependency order, after the proposal has been
122: completed and the user has authorized implementation:
123: 
124: 1. Versioned record definitions, exact values/context, source byte retention,
125:    dependency closure and pinned package/schema loading.
126: 2. Review and time selection, provenance/invalidation, immutable views and the
127:    initial transaction store's receipt/replay behavior.
128: 3. Typed constructors and validation; the matched debt text fragment and source
129:    maps; independent expected IR and adverse input cases.
130: 4. Admitted history templates, joint affine constraints, finite-choice search,
131:    partial checkpoints, typed capability failures and query-dependent refinement.
132: 5. The connected corporate economic and accounting methods with their actual
133:    authority, event scheduling and information boundaries; statement mapping.
134: 6. The integrated company case, source corrections, replay/recovery and bounded
135:    real-filing coverage; then optional justified measure operations and adapters.
136: 
137: P17 must complete actual source-grounded methods for corporate operations,
138: bonds/equity, groups/FX, IFRS/US GAAP/ASBE, banks and insurers. The extension
139: records in I4 make dependencies visible; they do not count as method completion.
140: Examples must include a changed group perimeter, intercompany elimination and
141: FX translation, credit loss and credit-risk memory, and insurance service/
142: measurement memory. Imported official rules and software interfaces require
143: located inspected sources and explicit limits. General nonlinear inference,
144: calibrated forecasting, multiwriter throughput and distributed durability are
145: later implementation/evaluation obligations, not inferred from prototype tests.
146: 
147: P18 integrates the completed methods and contracts into the governing LaTeX
148: manuscript and inspects its actual rendering. P19 assesses the full proposal
149: against MC01–MC35 and G1–G18. The current architecture may be judged specified
150: within its scope while those later proposal blockers remain open. Neither that
151: judgment nor a successful PDF build authorizes product implementation.


FILE: docs/design/proposal/architecture/architecture-integration-v1.md
SHA256: 29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1
1: # Integration of the nine proposed contracts
2: 
3: The active contract list in P16 architecture.json is the document index. This
4: supplement resolves interactions among those contracts without altering earlier
5: evidence or treating saved fixture outcomes as executed product behavior. It
6: addresses MC02–MC14, MC18–MC27 and MC33–MC35. The baseline is the five existing
7: P16 contracts and their accepted amendments; Core 0/P03/P07 are investigated
8: prototypes, not automatic defaults.
9: 
10: ## Meaning carried between contracts
11: 
12: | Boundary | Meaning that must survive | Rejection or unresolved consequence |
13: | --- | --- | --- |
14: | Evidence → time | Original bytes, source occurrence, review layer, economic/reporting/publication/ingestion clocks | Missing clocks cannot support stronger historical-knowledge claims |
15: | Evidence/time → history | Scoped admitted interpretation/assumption, joint symbols, conflicts and exclusions | Faithful reading alone cannot become an admitted accounting constraint |
16: | History → uncertainty | Full family/view, partition, dependence and query-relevant economic memory | No weights from witness counts; missing law gives a symbolic/unweighted result |
17: | Scenario/history → accounting | Branch opening, exact event identity, date/context, permitted information and eligible method | Unresolved or unsupported treatment produces no posting |
18: | Accounting → persistence | Validated request, source/method versions, proposal/delta and expected head | Exact replay before freshness; all-or-none transition; unknown commit reconciled under original identity |
19: | Calculation → report | Common history/scenario index, native statuses, unresolved regions/mass and unit/time semantics | No successful-subset renormalization or independent selection of line extrema |
20: | Correction → all descendants | Immutable old view, replacement scope, candidate-set membership and transitive dependency | Current reuse invalidated even for descendants created after the correction |
21: | Any contract → IR/interface | Versioned type, lineage and admission requirements | Unknown schema or required semantics cannot be ignored or coerced |
22: 
23: ## Explicit amendments and precedence
24: 
25: L1's portable encoding applies only to new portable records. Existing native
26: record digests, original files, source byte hashes and receipts stay unchanged.
27: Integer metadata remains integer; financial quantities use exact rationals.
28: There is no global NFC normalization. A named legacy import retains both IDs
29: and checked decoded correspondence. Source-map identity is separate from model
30: identity, so formatting changes do not alter a model's financial meaning.
31: 
32: P2 resolves the early accounting contract's ambiguous “event/version” language:
33: the stable lookup key excludes version and payload. A correction uses a new
34: business-event identity with an explicit treatment/lineage; merely changing a
35: version under an existing key conflicts. Branch identity includes an explicit
36: projection namespace, distinguishing separately requested hypotheticals from
37: retries of the same projection. No double counting of hypothetical projections
38: is permitted when reporting realized transactions.
39: 
40: Native accounting retains its established validation order and assess-only
41: boundary. New portable wrappers validate their own envelopes and then delegate
42: to that native order. Dependency recognition is guarded by reference shape;
43: malformed refs are not followed. A shape error cannot be masked by finding an
44: old receipt. Output defects are distinguished from ineligible economic events:
45: reject publication as ASSESSMENT_OUTPUT_INVALID while retaining the validated
46: request and diagnostic candidate. All four committed accounting domains remain
47: unchanged for assess-only, rejection and replay.
48: 
49: Uncertainty fixture v2 rejection receipts supersede only their explicitly named
50: v1 predecessors. Their valid requests, joint laws, calculation payloads and
51: unchanged successes remain evidence. Derived law/view bundles require separate
52: admission and selection; a numerical posterior does not admit itself. No
53: platform wrapper changes an existing domain's status values in place.
54: 
55: ## Status mapping at the new platform boundary
56: 
57: The native uncertainty schema has seven distinct statuses. The new platform
58: schema preserves the full native result and applies these mappings only with
59: the operation's tagged disposition and payload. Unknown combinations return
60: `STATUS_MAPPING_UNSUPPORTED`; they are not guessed.
61: 
62: | Native meaning | Platform interpretation |
63: | --- | --- |
64: | REQUEST_INVALID with invalid/unresolved/not_computed | rejected; invalid/unresolved/not_computed; no usable payload |
65: | satisfied + specified_exact, with a valid finite calculation payload | completed; valid/defined/complete; evidence_mode=specification_example |
66: | undefined, with established zero normalizer | completed; valid/undefined/complete; no posterior |
67: | specified_partial with retained unresolved regions | partial; valid/unresolved/partial, even when some local values are defined |
68: | symbolic without a requested executable evaluator | partial with retained formulas; valid/unresolved/not_computed |
69: | UNSUPPORTED operation/capability | unsupported; valid/unresolved/not_computed; retain input family |
70: | failed mathematics, such as an invalid proposed law | rejected; mathematical_status=unresolved at platform level with the exact native `failed` finding retained; never `infeasible` without proof of an empty family |
71: 
72: For the last row a platform diagnostic names the failed mathematical predicate
73: and preserves the native result; the requested probability result remains
74: unresolved. `structural_validity` is copied from the native request validation,
75: not inferred from the law's failure. A proof of infeasibility is a different
76: tagged result and maps to `infeasible`. Numeric/service failure has computation
77: `failed` and math `unresolved`, not mathematical infeasibility. These rules
78: prevent the platform's deliberately smaller vocabulary from changing a claim.
79: 
80: Native accounting `assessed` with `eligible` means the requested assessment was
81: specified, not that a journal was committed. Outer disposition is completed,
82: commit observation not_committed; its native accounting-validity field remains
83: not_assessed for the synthetic examples. `unresolved`/`outside_scope`/`ineligible`
84: remain explicit assessment results, with no JournalProposal. Input rejection
85: maps as above. A replay payload carries the original committed receipt and
86: additional_commit=false; outer disposition replayed, commit observation
87: not_committed. A lost acknowledgement of a requested write maps to commit_unknown
88: with unknown observation until the original identity is reconciled.
89: 
90: Empirical justification and capability values are preserved. Forecast validity,
91: product readiness and human acceptance cannot be inferred from any mapping.
92: All platform examples are specification examples; their finite arithmetic is
93: checked separately, and product_implemented remains false.
94: 
95: ## Continuous company family and insufficient summaries
96: 
97: The protected Northstar example has one shared unidentified floating fraction
98: x∈[0,1]. Historical interest of 5 does not identify it when both loan types
99: charged 5%. The 2025 scenario changes floating interest, profit, tax, cash and
100: equity together. I3's statement payload must therefore retain their common x,
101: not just independent endpoint lists. The source package's closed synthetic
102: scope, teaching tax model, assumed intraperiod ordering and aggregate event
103: resolution all travel with the result.
104: 
105: Grouping two instruments with the same currency, rate/reset schedule, maturity,
106: seniority, collateral/guarantee rights and relevant accounting memory may preserve
107: a specified linear interest query by adding principals. Grouping fixed and
108: floating instruments only by their historical interest loses the stress exposure
109: and fails that query. Even the safe grouping must be reconsidered for a new
110: default, prepayment or instrument-specific tax question. This is a query-scoped
111: sufficiency rule, not a general compiler proof of economic equivalence.
112: 
113: The real source-backed conflict requested in E05 is still missing: seven inspected
114: candidates did not establish one. The fourteen synthetic conflict cases specify
115: behavior but cannot supply that source evidence. P17 must complete the exact
116: authority/method and real-source obligations. The initial-profile choice and
117: interface decisions are proposed answers now, with actual evidence and owning
118: phase in P16's decision records. Open source/method decisions remain proposal
119: blockers through P19; they are not closed by writing this integration document.


FILE: docs/design/proposal/architecture/accounting-complete-exchanges-v1.md
SHA256: c85637bb5ee53feaa64a0de0d68056bc1c37f0e106354e67c1d726da3fc4fa49
1: # Accounting exchange and context reconciliation
2: 
3: The field controls for C09/C10 distinguish missing, malformed, unknown and
4: not-applicable values. This supplement carries those controls through complete
5: requests, dependency closure, assessments and publication. It also supplies the
6: remaining source/context predicates and an independently derived disposition for
7: V01–V16. It addresses MC08, MC13, MC25, MC27, MC34 and MC35, with G4/G18.
8: No accounting engine or product endpoint is implemented.
9: 
10: ## Comparator, evidence and audit
11: 
12: The comparators are the seventeen corrected integration-v2 exchanges, the
13: accepted C03/C05/C07 supplements, the saved 260 C09/C10 field controls and
14: the sixteen V-series input/output mutations. Source claims and method flags
15: remain synthetic assumptions. The check must derive findings from supplied
16: fields, verify newly pinned source packets and all transitive record references,
17: then compare authored expected results. Matching a copied outcome alone would
18: not test the defect. Earlier evidence remains unchanged.
19: 
20: The skeptical audit passes for this finite specification task. Reject stale
21: pins, unintended changed facts, incorrect reference closure, disagreement between
22: price and route requirement, guessed Boolean controllers, premature receipt
23: lookup or publication of defective output. Fixable failures trigger correction
24: of this draft. Source-authority gaps remain P17 work; no deterministic check
25: promotes stipulated facts into inspected entity facts. No backend, solver,
26: timing or statistical comparison is attempted.
27: 
28: ## Binding and semantic predicates
29: 
30: Use the native sequence parse, recognizable dependencies, shape, source_versions,
31: bindings, lookup, freshness, assessment, output validation. A shape-valid but
32: internally inconsistent source packet is a binding failure, not a legitimate
33: economic alternative. Unknown economic content must use the named unknown
34: representation. The existing 299-path field matrix governs types/presence; the
35: later reason and C03/C05/C07/C09/C10 amendments prevail for their exact fields.
36: 
37: | Conditions | Required consistency and remaining meaning |
38: | --- | --- |
39: | C01 | Annual start equals request context; `within_retained_window` equals `2023-01-01 <= annual_start < 2026-07-01` for the pinned Compilation 5. False consistently represented is outside_scope; a contradictory flag is SOURCE_CONTEXT_MISMATCH. The edition, reporting basis and actual entity applicability still need source-supported assessment. |
40: | C02 | Holder/instrument/exception facts remain independently admitted. A synthetic scope-exceptions string is a stated assumption, never executable proof that exceptions are absent. Unsupported feature gives outside_scope; missing required real-world assessment gives unresolved. |
41: | C03/C04 | Preserve the accepted C03 date/party rules. Recognition date equals the event's economic date; trade/settlement and valuation dates must be valid dates. Conditional policy eligibility does not override nonparticipation. No universal equality of contractual and recognition dates is imposed. Regular-way/policy eligibility is a distinct admitted method judgment. |
42: | C05 | Category agrees with the event category. Classification rationale and designation/OCI choices remain the accepted explicit conditional rules; descriptive cash-flow prose is not a completed SPPI analysis. |
43: | C06/C07 | Exact decimal price/fair value/fee equal the event values; valuation date equals the event's date for this immediate-acquisition profile. A different valuation date needs a named bridging method/new profile. C07 incrementality and purpose obey the saved predicates; contextual reason text never changes them. |
44: | C08 | Source entity/book/branch labels match the declared synthetic aliases; aliases match request identity and pinned context/branch. Currency/unit/scale equal context. Cash settlement and no separate FX/tax/other-asset treatment are profile assumptions, not universal accounting rules. |
45: | C09 | With valid exact source amounts, required is exactly `price != fair_value`. Under equal price the retained profile has two null, not-applicable routes and branch not_applicable. Under unequal price either true route gives branch a, both false give b, and all other valid pairs give unknown. Both route values and both reasons survive even when one true route suffices. A stored branch inconsistent with those values is SOURCE_CONTEXT_MISMATCH. |
46: | C10 | Method availability comes from the pinned method/profile, not a supplied true flag or reason. This retained profile has neither unequal-price posting method. A true availability flag contradicts its pinned capability and fails METHOD_CAPABILITY_MISMATCH. A different supported package requires a new method/profile Ref and full reassessment. C10 contextual reason remains nullable; unknown C09 does not itself require C10 text. |
47: 
48: The single KnownBool `observable_valuation` in the request's evidence record is
49: only the derived qualifying OR of C09. Under required=false it is unknown/not
50: required; with a true route it is known true; with two false routes known false;
51: otherwise unknown. The source's two route values are never reconstructed from
52: this lossy projection. A contradictory convenience field fails
53: SOURCE_CONTEXT_MISMATCH. Assessment preconditions retain their coarse historical
54: projection, while findings and valuation_routes retain the precise results.
55: 
56: These rules distinguish a malformed controller from an internally inconsistent
57: but typed packet, and both from a legitimate unresolved treatment. C01/C02/C04/
58: C05 actual authority, economic facts and permitted methods remain admissibility
59: requirements. A real input cannot acquire `synthetic_only` admission by copying
60: an example label. The interfaces require an explicit mapping and reviewed
61: applicability decision in its own scope.
62: 
63: ## Complete exchanges and output discipline
64: 
65: The companion fixture imports the exact native record registries. Every changed
66: source packet is stored separately with its comparator and change explanation;
67: the changed eligibility source/ConditionRefs, request, submission, assessment and
68: response are rehashed. Each exchange resolves the complete record closure.
69: File hashes are file references, never mistaken for record digests. Imported
70: records retain their original digest domains.
71: 
72: Valid contextual-reason changes preserve all economic facts, treatment findings,
73: method flags and evidence statuses of their comparator. Invalid shape/context
74: changes return no validated request, assessment, diagnostic journal/delta,
75: receipt or observed-state publication reference. Lookup, freshness and assessment
76: are false. Every exchange has additional_commit=false and identical before/after
77: values for identity index, committed journals, selected state and committed
78: receipts. Valid assess-only exchanges can look up and assess without posting.
79: 
80: The sixteen retained V cases are active adverse examples, not completed runtime
81: tests. V01–V04 and V08/V09 fail shape; V05–V07 fail bindings; V10 fails dependency
82: kind. V11–V16 retain a validated request but reject a defective produced
83: assessment/response as ASSESSMENT_OUTPUT_INVALID. Derive these outcomes from the
84: candidate operation/profile/version/aliases/conditions/bindings and published
85: assessment content. Output checking requires one ordered finding per C01–C10,
86: summary consistency, correct route projection and diagnostic-example scope,
87: posting_permitted=false for assess-only, and no additional commit. The rejection
88: does not imply that the company's acquisition is ineligible.
89: 
90: The finite diagnostic establishes these specified distinctions and preservation
91: properties. It does not implement arbitrary request validation, prove the truth
92: of the underlying source statements, establish standards compliance or accept
93: P16. Integrated independent review must assess its scope with the other eight
94: contracts and the initial profile.


FILE: docs/design/proposal/architecture/accounting-replay-contract-v1.md
SHA256: 0575dbe1d050c7fe1fc894e344ff22fcfc52f81e4c0450b87af1218d369910f2
1: # Accounting replay and event identity — proposed supplement v1
2: 
3: This supplement repairs the replay semantics in accounting-contract-v1.md,
4: sections 2–4. It supersedes AC04 and AC05 as reproducible retry/staleness
5: examples, and clarifies invariant 5: event version belongs to the fingerprint,
6: not the stable lookup key. AC01–AC03 and all predecessor files remain historical
7: source-scoped evidence. This slice addresses MC13, MC25 and MC34 with MC08
8: branch preservation and G4/G18 interactions. It specifies behavior, not software.
9: 
10: ## Question, evidence and stopping rule
11: 
12: Can the same recorded acquisition be retried after later transactions without
13: posting twice, while changed requests conflict and genuinely new stale requests
14: are rejected? Compare identity lookup before freshness with freshness before
15: identity lookup, using the identical request and committed state. The primary
16: criterion is the derived response and absence/presence of a further domain
17: transition in each specified case, including branch isolation. Wrong source
18: hashes, inconsistent dependencies or non-reconciling arithmetic invalidate the
19: fixture calculation. Journal balance is an explanatory arithmetic check, not
20: proof of eligibility. No statistical ranking, runtime durability, accounting
21: validity or complete IR selection follows. Preserve the result in
22: accounting-replay-verification-v1.json and stop after this bounded slice.
23: 
24: Skeptical audit: these are matched deterministic cases, not a comparison of
25: prototype test counts. Failure of the whole P16 checker is expected while four
26: contracts and the initial profile are unfinished. It does not invalidate a
27: correctly scoped retry example. Conversely, passing these examples cannot
28: complete the accounting contract. Remaining input/receipt, eligibility, atomic
29: failure and architectural-alternative obligations require a subsequent task.
30: 
31: ## Identity and record encoding
32: 
33: The stable event key is the tuple (entity_id, book_id, branch_id,
34: business_event_id). Book identifiers are scoped by entity; branch identifiers
35: are scoped by book. Branch IDs reference explicit branch records and their
36: common family. The same event label in a different branch is a distinct posting
37: identity; it neither inherits a receipt nor grants economic admissibility.
38: A version change under the same key conflicts. An intentional correction needs
39: a new business-event ID linked to the superseded event and a separately
40: specified correction method; a version bump alone never authorizes a second
41: posting. Correction workflows are outside this slice.
42: 
43: The request fingerprint covers the complete request record: stable key, event
44: version and payload, expected opening-state digest, context, time/cutoff,
45: branch record, and authority/method/evidence/assumption record digests. Mutable
46: transport metadata (arrival time, tracing token) is outside this request. Every
47: transitive record is immutable and checked against its digest. Thus equal
48: fingerprints mean equal retained request bytes under this encoding, assuming
49: SHA256 collision resistance; they do not assert economic equivalence.
50: 
51: For these finite fixtures only, serialize JSON with sorted keys, compact
52: separators, ensure_ascii=True and allow_nan=False, encoded as ASCII. Objects
53: have unique string keys; arrays preserve order; numeric amounts are decimal
54: strings with exactly two fractional digits; versions are nonnegative integers.
55: Floats, NaN, duplicate keys and non-ASCII text are excluded from this fixture
56: profile. UTF-8 interoperability, arbitrary dimensions, migrations and a general
57: language encoding remain open. The digest is SHA256 of the ASCII domain,
58: a NUL byte and serialized bytes. Domains are accdsl.replay.v1/key,
59: accdsl.replay.v1/request and accdsl.replay.v1/<record kind>. A receipt references
60: request, assessment, journal, delta and opening/closing records without a cycle.
61: The registry stores kind, full content and digest, not symbolic digest labels.
62: 
63: These are proposed convenience choices. SHA256 follows existing immutable
64: source references; exact two-decimal amounts follow the synthetic A01 example;
65: branch IDs and monotonically numbered states expose isolation and stale inputs.
66: Their failure modes are omitted request fields, accidental aliases, precision
67: loss and mistaken cross-branch reuse. The bounded calculation checks all
68: request dependencies, changes payload and branch separately, uses Decimal and
69: checks distinct opening/closing digests. These checks do not promote the
70: choices to a general persistence or IR default.
71: 
72: ## Order, receipts and concurrency obligations
73: 
74: 1. Check structure, resolve all pinned records and validate internal context:
75:    entity/book/branch, currency/unit/basis, event time and source cutoff. An
76:    exact retry uses its retained historical context, not today's method or
77:    cutoff. Missing/corrupt dependencies are an invalid request, not a replay.
78: 2. Under that branch/book identity, look up the stable key in committed receipts.
79:    If found, compare the complete request fingerprint. An equal fingerprint
80:    returns the original immutable receipt; a different fingerprint returns
81:    EVENT_ID_CONFLICT before any freshness check. Neither creates a new domain
82:    transition. Changed payload cannot evade conflict by changing its version.
83: 3. Only for an absent key, compare the expected opening digest with the current
84:    state of that branch. Mismatch returns STALE_OPENING_STATE without a posting.
85: 4. For a fresh new event, assess eligibility and construct/check the journal
86:    and independent delta. Only then may one atomic operation insert identity,
87:    journal, closing state and committed receipt. Recheck absence of the key and
88:    opening state atomically to prevent a concurrent writer racing these checks.
89:    Persistence must later specify isolation, crash recovery and audit storage.
90: 
91: The immutable receipt always retains status=committed and commit=true for the
92: original transaction. A retry response has status=replayed,
93: additional_commit=false and the same receipt digest; it must never rewrite
94: that receipt as replayed or return a newer closing state as its original result.
95: Its response separately identifies the current observed state. A conflict may
96: identify the existing receipt for diagnosis, without claiming it belongs to the
97: submitted fingerprint. A stale or conflicting response preserves the submitted
98: request and known facts; journal and delta are null, additional domain writes
99: are zero and before/after state and committed-receipt index are identical.
100: Optional audit logging is separate from domain writes and is not required or
101: modeled by these fixtures. Replay retrieval is not a fresh eligibility verdict.
102: 
103: Freshness-first on the specified retry sees the original opening state differ
104: from the now-current state and incorrectly reports STALE_OPENING_STATE. Both
105: orders reject the genuinely new stale request. Stable-key-only replay without
106: a fingerprint would incorrectly accept a changed payload. Including payload
107: or version in the lookup key would instead hide the conflict. These comparisons
108: justify the proposed order under the stated retry contract; they establish no
109: speed or storage advantage.
110: 
111: ## Concrete inputs and consequences
112: 
113: The fixture registry includes complete branch-scoped opening balances, pinned
114: context and request dependencies. A01 has price=fair value=100.00 and fee=2.00.
115: Eligibility is explicitly stipulated under the retained S9 5.1.1 source scope;
116: this task does not re-establish classification or jurisdiction applicability.
117: Cash starts at 1000.00, asset and expense at zero, and equity at -1000.00 in
118: debit-positive notation. The event directly implies cash -102.00, asset +100.00,
119: expense +2.00, equity zero change. Separately, debit asset 100.00, debit expense
120: 2.00 and credit cash 102.00 aggregate to the same delta. Closing cash is 898.00.
121: A second separately identified acquisition advances this branch to cash 796.00,
122: asset 200.00 and expense 4.00; its full request and receipt are retained as setup.
123: 
124: AR01 commits the control. AR02 retries AR01 after the second acquisition and
125: returns AR01's original receipt without changing either receipt or current
126: state. AR03 changes the fee to 3.00 under the same key and conflicts, preserving
127: that submitted fact without posting it. AR04 uses a new event ID with the old
128: opening digest and is stale. AR05 uses the original event label in another
129: explicit branch with its own opening state: it commits there while branch A
130: and both of its receipts remain unchanged. Branch B is a synthetic stipulated
131: alternative, not a newly inferred economically admissible history.
132: 
133: The calculation independently derives A01 deltas from event amounts and from
134: journal lines, checks complete receipt references and every source binding,
135: and derives outcomes before comparing authored expectations. It is an offline
136: finite document calculation, not a reusable runtime evaluator or product test
137: suite. Full lifecycle eligibility, general record typing, atomic failure modes,
138: interfaces, language/IR, persistence and initial-profile selection remain open.


FILE: docs/design/proposal/architecture/accounting-integration-contract-v1.md
SHA256: e5c1aa270b16af2ee7831ebaca77fc67d35a3072203d4e28eab7706039436639
1: # Acquisition request and assessment integration — proposal v1
2: 
3: This supplement binds the independently reviewed acquisition dossier and decision
4: supplement to immutable request and assessment records. It addresses MC08, MC13,
5: MC25, MC34 and MC35, with G4/G18 interactions. It is a proposed specification,
6: not a runtime API. The terminal bounded AGREE in
7: `data/accounting-master/runs/20261005T150545-71a70996/P16/execution-0/review_result-0.response.json`
8: accepts those source examples only. This integration requires its own review.
9: 
10: ## Question and evidence boundary
11: 
12: Can a recipient recover every reviewed condition, individual unknown and combined
13: adverse finding from the request and assessment, with reproducible identity?
14: The comparator is the existing records-plus-bindings specification on the same
15: synthetic facts, before it binds the ten conditions. Primary acceptance requires
16: complete C01–C10 references, matched results for E01–E17, all nine valuation pairs,
17: correct context and version bindings, and unchanged committed state. Lost findings,
18: unknown-to-false coercion, changed predecessor files, cross-version receipt aliases
19: or a diagnostic assessment granting posting permission veto acceptance. Hashes
20: and balance are explanatory checks, not accounting validation. There is no
21: scientific ranking, historical evidence admission or runtime claim.
22: 
23: The skeptical audit found a material date difference: the records illustrate
24: January acquisitions, while the eligibility facts use June. The new examples
25: therefore create new time/event/admission records, with June economic dates and
26: matching reporting intervals. They do not attach June facts to January requests.
27: C01 period-start variations E04/E16/E17 change the new context's annual-period
28: start; the event's reporting interval remains the explicitly stipulated 2024
29: interval. Those adverse examples already lie outside this authority profile;
30: no calendar-valid historical book is asserted. This is not a migration of a
31: committed transaction. Source labels such as “synthetic purchaser” are explicitly
32: mapped to opaque entity/book/branch identifiers; no real-company identity is inferred.
33: 
34: Stop after this contract, fixtures, finite calculation, integrity record, P16
35: checkpoint and one registered check. Language/IR is the next separately scoped
36: contract after review. Lifecycle methods and profile selection remain separate.
37: 
38: ## Versioned input contract
39: 
40: Use the predecessor ASCII canonical JSON encoding: sorted keys, compact
41: separators, ensure_ascii=True, allow_nan=False. Each new record has a SHA256 of
42: `accdsl.accounting.integration.v1/<kind>` + NUL + canonical content. Imported
43: records retain their original domain and bytes. The stable identity key retains
44: `accdsl.replay.v1/key`; a request fingerprint always includes its schema version,
45: operation and complete precondition references. Identical economic amounts do
46: not establish cross-version request equivalence. No old receipt may be relabelled.
47: 
48: The request preserves every v1 request field: identity, event, opening, context,
49: branch, time, chart, authority, method, evidence, admissions, assumptions and
50: lineage. Its schema_version is 2. It adds exactly `operation="assess_only"` and
51: `eligibility: Ref<eligibility_input>`. The operation cannot commit. A future
52: posting operation requires a separately reviewed extension and new fingerprints.
53: This explicitly limits the new examples without changing the retained R01–R06
54: posting, rejection, abort or acknowledgement-loss examples.
55: 
56: An eligibility_input has exactly schema_version=1, profile="acquisition-conditions-v1",
57: dossier and decision_rules FileRefs, source_case CaseRef, bindings, aliases and
58: conditions. CaseRef is `{file:{path,sha256},case_id}`; a ConditionRef is
59: `{case:CaseRef,condition_id,value_version}`. It resolves precisely the complete
60: input at cases[id=case_id].complete_inputs[condition_id], including value,
61: unknown_reason, provenance, scope and version. It never resolves an expected
62: assessment. All ten condition IDs are required once, in C01–C10 order. Pin both
63: the file bytes and value_version; a new version changes the request. The evidence
64: owner publishes new records rather than editing inputs in place.
65: 
66: Bindings contains the exact request references for context, branch, time, chart,
67: authority, method, assumptions, evidence and admissions. Every equality must hold;
68: context/branch versions are compared by complete reference, not names alone.
69: The existing five bindings remain mandatory: event.branch=request.branch,
70: opening.branch=request.branch, event.time=request.time,
71: opening.chart=request.chart and method.authority=request.authority. All existing
72: context, identity, account membership and admission/evidence/time checks remain.
73: Aliases maps the source C08 entity/book/branch labels to the request's identity
74: IDs and to the pinned context and branch references. It is a synthetic mapping
75: assertion with scope `synthetic_only`, not historical entity resolution.
76: 
77: C01 annual-period start must equal context.annual_period_start. C04 recognition
78: date must equal event.time.economic_date. C06 price/fair value and C07 fee must
79: equal event amounts exactly after decimal-string normalization. C08 units,
80: currency and scale must equal context. The old single observable_valuation
81: KnownBool is a derived convenience for the qualifying OR, never the evidence
82: source for the two routes; equal-price examples use explicit unknown/not-required.
83: The authoritative Q/O values remain individually accessible through C09.
84: Null route values mean unknown only where the reviewed condition specifies it;
85: C09.required=false means not applicable. Missing fields are malformed, never
86: unknown or zero. All v1 lexical/type rules remain, with these explicit additions.
87: 
88: ## Output and non-lossy assessment
89: 
90: The assessment retains request, status, reason_codes, preconditions, authority
91: and method. It adds schema_version=2, eligibility, findings, valuation_branch,
92: valuation_routes, method_applicability, source_assessment, evidence_level,
93: posting_permitted=false and diagnostic_example. Preconditions retains the v1
94: {name,status,support} shape: satisfied_conditionally/not_applicable maps to
95: satisfied; unresolved to unknown; ineligible/outside_scope to failed. This coarse
96: projection is for compatibility only. The exact finding, its reason and all
97: child route findings remain in findings; valuation_routes additionally exposes
98: both raw values and unknown/qualifies/does_not_qualify/not_applicable statuses.
99: No consumer may use the coarse projection to discard an outside-scope reason.
100: 
101: source_assessment pins the reviewed example as comparative provenance; the
102: calculation derives statuses from input facts and compares them with it. It is
103: not an input to eligibility inference. Summary precedence remains ineligible,
104: outside_scope, unresolved, eligible. Evaluate all ten conditions before selecting
105: a summary; retain every adverse reason in condition order. This precedence is a
106: reporting convention, not an accounting rule. method_applicability is conditional
107: for the equal-price example, unavailable for known unequal-price branches, and
108: unresolved for an unknown branch. It does not override recognition failures.
109: The conditional eligible control remains synthetic and grants no posting right.
110: 
111: The response retains submission, request, assessment, diagnostic_journal,
112: diagnostic_delta, receipt, observed_state, commit_status, additional_commit,
113: statuses and metadata. The new successful assessment response has status=assessed,
114: commit_status=not_committed, additional_commit=false and all journal/delta/receipt/
115: observed_state references null. diagnostic_example is a CaseRef only for E01's
116: existing explanatory arithmetic; it is not a journal reference. No assessment
117: constructs a journal, state delta or receipt. Accounting validity remains
118: not_assessed, empirical justification not_established, capability specified_only_no_runtime,
119: and human acceptance pending. The four committed domains are exactly the
120: identity index, committed journals, selected state and committed receipts.
121: 
122: ## Failure and replay order
123: 
124: First retain submission bytes; validate JSON, types, digests, all references,
125: versions and bindings before identity lookup. Duplicate keys, extra fields,
126: missing condition IDs, an unavailable pinned file or a value-version mismatch
127: are structural rejections. Canonical-byte/digest disagreement is corruption,
128: not a new assessment. Structural rejection returns request=null and
129: assessment=null, all candidate/receipt/state references null and a precise code;
130: no canonical request is admitted. Preserve the exact submitted bytes and failed
131: references in diagnostics. Never repair a version mismatch silently.
132: 
133: After validation, lookup precedes freshness. A same-key different fingerprint
134: is an identity conflict, even if its amounts or condition summaries match. A
135: matching committed request returns its original receipt without a fresh
136: assessment; a diagnostic assessment is never placed in the commit index.
137: A genuinely absent key checks freshness before assessing. Stale opening state
138: returns a rejection without assessment or writes. Unknown facts produce valid
139: unresolved findings; disproved recognition produces ineligible; an authority
140: outside the retained window produces outside_scope. These are semantic outcomes,
141: not malformed requests. Combined findings survive summary precedence.
142: 
143: Repeated assess_only submission has the same request and deterministic assessment
144: digests but no receipt. Its outcome is assessed again, not replayed committed.
145: The fixtures also reference exact R06 matching-receipt replay, preserving its
146: original fingerprint and receipt, and demonstrate that a v2 fingerprint cannot
147: retrieve that v1 receipt. R01–R06 are all retained by immutable CaseRefs; no
148: v2 committed receipt is invented merely to furnish a positive replay example.
149: An in-flight posting lookup remains unknown until authoritative finality; this
150: read-only operation is definitively not_committed because it cannot publish.
151: Rejection or assessment leaves all four domains byte-for-byte unchanged.
152: 
153: ## Alternatives, defaults and remaining decisions
154: 
155: Embedding mutable condition prose in request identity fails reproducibility.
156: Embedding complete immutable condition values can satisfy the same contract, but
157: would duplicate the reviewed packets; typed references are chosen here because
158: they preserve one inspectable source and explicit versions. A reference-only
159: design must retain resolvable bytes: a missing source is a veto, not permission
160: to use the latest file. The old category/one-Boolean input cannot represent both
161: valuation routes or ten separate obligations. A richer upstream classification
162: could satisfy this contract if it preserves the same facts and authority.
163: No storage or execution architecture is selected by these examples.
164: 
165: | Choice / provenance | Status and reason | Failure / early diagnostic |
166: | --- | --- | --- |
167: | Existing v1 field shapes and B1–B5 | Reviewed bounded baseline | Schema drift; compare retained keys and binding equalities |
168: | New domain and request version | Proposed convention to prevent aliases | Reused receipt; compare v1/v2 digests with the same identity |
169: | Ten typed condition references | Proposed representation of accepted dossier | Stale/missing source or lost unknown; resolve every field and pinned version |
170: | CU two-decimal amounts, synthetic mapping | Convenience from existing examples | False real-world precision/identity claim; exact Decimal and explicit aliases |
171: | Summary precedence | Accepted bounded reporting convention | Lost lower-priority finding; E15–E17 retain every finding |
172: | assess_only boundary | Conservative proposal scope | Eligibility mistaken for permission; all four domains and receipt stay unchanged |
173: 
174: The retained authority is AASB 9 Compilation 5, not a general current IFRS,
175: US GAAP or ASBE determination. The reviewed dossier supplies paragraph anchors
176: and limits; this integration adds no authority claim. Actual classification,
177: historical admission, lifecycle methods and wider company/sector support remain
178: open. The full MC01–MC35/G1–G18 mission survives this bounded representation.
179: 
180: | Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
181: | --- | --- | --- | --- | --- | --- |
182: | Submit integration for independent review | Finite report records preservation and linkage checks | Any failed binding or changed predecessor blocks slice acceptance | Generalized schemas and actual facts remain unvalidated | Inspect new contract and fixtures | Runtime or accounting validity |
183: | Keep P16 partial | Four architecture groups/profile/decisions remain open | Whole-architecture structural failure remains expected | Language, persistence, interfaces, failure semantics | Scope language/IR after review | Product readiness or human acceptance |
184: 
185: Post-run red team: hashes can preserve a wrong assertion perfectly. The strongest
186: alternative explanation is a deficient synthetic classification or context
187: mapping. A contradictory contract, source paragraph or binding would overturn
188: the affected assessment. Independent input-derived checks address representation
189: consistency only; they cannot validate the source facts or a production engine.


FILE: docs/design/proposal/architecture/uncertainty-rejection-status-contract-v1.md
SHA256: cc5ec2bd69cf4ba0bf4f0d7fb6e6d668cf7975244afa4464fbb7e412c4eeee8c
1: # Rejected uncertainty requests — status correction v1
2: 
3: This supplement corrects five specified rejection receipts in
4: `uncertainty-chaining-fixtures-v1.json`. The independent uncertainty review in
5: `data/accounting-master/runs/20261005T120206-bdb3a74d/P16/execution-0/review_result-0.response.json`
6: returned REVISE: its arithmetic agreed, but the receipts assigned `not_computed`
7: to `mathematical_status`, contrary to uncertainty-contract-v1.md §2. The current
8: fixtures are `uncertainty-chaining-fixtures-v2.json`. The original files and
9: records remain evidence of the defect, not active expected rejection outputs.
10: This proposal correction carries MC08–MC14, MC18, MC25, MC27 and MC33–MC35,
11: principally G1/G6/G15/G16. It requires independent result review.
12: 
13: ## 1. Bounded question and acceptance
14: 
15: Can a consumer interpret all five rejected requests using the existing common
16: status vocabulary? The comparator is uncertainty-contract-v1.md §2 and the
17: unchanged chaining v1 requests and rejection consequences. Acceptance of this
18: slice requires all seven status fields below, exactly five explicit correction
19: mappings, unambiguous active expected receipts, and preservation of every original
20: registry record and every successful case. Changed requests, laws, payloads,
21: masses, normalizers, selected state, parent hashes, audit writes or rejection
22: reasons veto the correction. Missing reference closure or an active malformed
23: predecessor also veto it. These are repair triggers; they do not reject the wider
24: uncertainty research direction. Checker totals explain structural coverage only.
25: 
26: Skeptical audit: the baseline is the declared exchange, not prototype behavior;
27: no arithmetic reassessment, runtime experiment, statistical ranking or environment
28: comparison is needed. The same requests and consequences are compared. Stop after
29: the supplement, versioned fixture, focused preservation report, registered check
30: and updated P16 records. No accounting design begins in this slice.
31: 
32: The status interpretation is a proposed clarification, with provenance in the
33: reviewed repair plan and the governing vocabulary. Its risk is that `unresolved`
34: could be mistaken for permission to continue an invalid request. The decisive
35: `REQUEST_INVALID` disposition, unchanged reason code, explicit no-computation
36: status and no-output postconditions prevent that inference. A focused field and
37: state check is the early diagnostic; independent review decides semantic adequacy.
38: No new empirical, accounting or mathematical default is selected.
39: 
40: ## 2. Common status envelope for pre-evaluation rejection
41: 
42: Request validation decides whether evaluation may proceed. Here it fails before
43: mathematical evaluation, so each corrected receipt contains:
44: 
45: | Field | Value | Meaning for this request |
46: | --- | --- | --- |
47: | `structural_validity` | `invalid` | Request validation failed, including semantic binding/admission/reuse checks. This does not mean the receipt itself is malformed. |
48: | `mathematical_status` | `unresolved` | The requested calculation was not evaluated. This is no finding that its mathematics is false or undefined. |
49: | `computation_status` | `not_computed` | Validation stopped evaluation; there is no computed result. |
50: | `empirical_justification` | `not_established` | The rejection establishes no empirical support. |
51: | `capability_status` | `specified_only_no_runtime` | This file specifies behavior; it reports no runtime execution. |
52: | `accounting_validity` | `not_assessed` | Rejection supplies no accounting eligibility judgment. |
53: | `human_acceptance` | `pending` | Neither fixture consistency nor the prior review establishes human acceptance. |
54: 
55: `disposition="REQUEST_INVALID"` and the existing `reason_codes` remain decisive.
56: `unresolved` never authorizes use of a result or admission of the request. Reserve
57: `undefined` for established undefined mathematics, such as the specified zero
58: normalizer; reserve `failed` for an established mathematical failure. Neither
59: finding was made for these five invalid requests.
60: 
61: The common envelope was chosen over a separate rejection schema because it uses
62: the vocabulary already required of consumers and retains one interpretation for
63: each status field. A separate schema could omit inapplicable mathematical fields,
64: but would require a new discriminator, consumer branches and explicit migration
65: rules. That broader change is unnecessary for this defect. This choice does not
66: settle the later language, interface or persistence design.
67: 
68: ## 3. Versioned correction and active selection
69: 
70: The v2 fixture copies all 125 v1 registry records without canonical JSON changes.
71: It adds exactly five records with the same logical receipt IDs, `version=2`, and
72: the corresponding `@1` receipt as `predecessor`. The only record changes are
73: version, predecessor, the corrected/added status fields, correction provenance,
74: and dependency closure including that predecessor. Requests remain version 1.
75: 
76: | Active case | Corrected receipt | Preserved rejection reason |
77: | --- | --- | --- |
78: | `candidate_only` | `CH.rejection.candidate_only@2` | `ADMISSION_REQUIRED` |
79: | `duplicate_D` | `CH.rejection.duplicate_D@2` | `DUPLICATE_INFORMATION` |
80: | `stale_law` | `CH.rejection.stale_law@2` | `LAW_VIEW_ATTACHMENT_MISMATCH` |
81: | `stale_attachment` | `CH.rejection.stale_attachment@2` | `LAW_VIEW_ATTACHMENT_MISMATCH` |
82: | `correction_on_posterior` | `CH.rejection.correction_on_posterior@2` | `CORRECTION_REQUIRES_REBASE` |
83: 
84: `rejection_status_corrections` is the explicit old-to-new map;
85: `active_rejection_receipts` and the five `cases[].expected_ref` values agree with
86: it. The `historical_rejection_receipts` entries mark each predecessor ineligible
87: as an active expected output. Registry presence alone confers no eligibility.
88: Consumers of this proposal select the named v2 fixture and its explicit case
89: references; they must not infer a version by scanning for the latest ID. Successful
90: case references, bundles, admissions and representation alternatives are unchanged.
91: 
92: This is a revision of authored specification examples, not a runtime replay or
93: an exception to request idempotency. No runtime receipt has been overwritten or
94: reissued. A future runtime implementing a fixed specification must still return
95: the same logical receipt for identical request bytes; operational migration and
96: historical replay rules remain obligations of the unfinished persistence contract.
97: 
98: ## 4. Unchanged rejection consequences and retained evidence
99: 
100: Every corrected receipt retains its request reference, exact reasons, selected
101: family/view/attachment/model snapshots, selection revision and parent hashes.
102: `state_before == state_after`, `domain_writes=[]`, the audit writes remain
103: `submitted_bytes` and `rejection_receipt`, and both `proposed_view_ref` and the
104: output `model_ref` remain null. No posterior, aggregate result or candidate view
105: is created. Corrected provenance identifies the pinned predecessor file and
106: terminal review; it is not a new observation or likelihood factor.
107: 
108: The current focused diagnostic is preserved in `uncertainty-rejection-status-check-v2.json`
109: with its command and input hashes; the fresh registered result and execution
110: record use `uncertainty-rejection-status-structural-check-v1.json` and
111: `uncertainty-rejection-status-structural-execution-v1.json`. Their actual outcomes
112: are recorded in P16/result.md. They test specification consistency, not runtime
113: enforcement. Five counterpart contracts, the integrated initial profile and
114: dependency order, fourteen open decisions, P17 methods, E05 and all wider mission
115: obligations remain. Accounting validity, empirical forecast validity, product
116: readiness and human acceptance remain unestablished.
117: 
118: Diagnostic correction: the first check treated the frozen `perimeter` value
119: `single_entity@1` as a registry reference solely because it contained `@1`.
120: It is a scope label in these fixtures; the v2 diagnostic excludes that field
121: from registry-reference traversal. The failed v1 report and checker source are
122: preserved. This changes no request or specified receipt. General perimeter
123: representation remains outside this bounded repair.


FILE: docs/design/proposal/architecture/platform-contract-calculation-v1.py
SHA256: 3d16fbb5040e3a8f5c176b63f00bbf894a00cf38db3854f5a0923f40f841ddd9
1: """Independent finite arithmetic for a proposal, not product implementation.
2: 
3: Read authored examples and the preserved company fixture. Derive financial
4: consequences from their inputs; do not treat agreement between frontends or a
5: specified transaction trace as executed conformance. Write one fresh report.
6: """
7: import hashlib
8: import json
9: import platform
10: import sys
11: import time
12: from collections import defaultdict
13: from fractions import Fraction as F
14: from pathlib import Path
15: 
16: START = time.monotonic()
17: ROOT = Path(__file__).resolve().parents[4]
18: EXAMPLES = ROOT / 'docs/design/proposal/architecture/platform-contract-examples-v1.json'
19: used = {Path(__file__).resolve()}
20: checks = []
21: 
22: 
23: def load(path):
24:     path = Path(path)
25:     used.add(path.resolve())
26:     return json.loads(path.read_text())
27: 
28: 
29: def check(label, value):
30:     checks.append({'id': label, 'passed': bool(value)})
31: 
32: 
33: def rat(value):
34:     if isinstance(value, dict):
35:         assert set(value) == {'n', 'd'}
36:         n, d = int(value['n']), int(value['d'])
37:         x = F(n, d)
38:         assert d > 0 and str(n) == value['n'] and str(d) == value['d']
39:         assert x.numerator == n and x.denominator == d
40:         return x
41:     return F(value)
42: 
43: 
44: def pins(value):
45:     if isinstance(value, dict):
46:         if 'path' in value and 'sha256' in value:
47:             path = (ROOT / value['path']).resolve()
48:             check('repository reference ' + value['path'], path.is_relative_to(ROOT))
49:             used.add(path)
50:             check('reference bytes ' + value['path'], path.is_file() and
51:                   hashlib.sha256(path.read_bytes()).hexdigest() == value['sha256'])
52:         for child in value.values():
53:             pins(child)
54:     elif isinstance(value, list):
55:         for child in value:
56:             pins(child)
57: 
58: 
59: examples = load(EXAMPLES)
60: pins(examples)
61: cases = {c['id']: c for c in examples['cases']}
62: check('unique example IDs', len(cases) == len(examples['cases']))
63: check('specified-only evidence', examples['evidence_mode'] == 'specification_example'
64:       and examples['product_implemented'] is False)
65: 
66: for key, stress in [('LX01', F(7, 100)), ('LX02', F(9, 100))]:
67:     row = cases[key]
68:     source = cases['LX01']['inputs']['typed_construction']
69:     if key == 'LX02':
70:         stress = rat(row['inputs']['replace']['floating_annual_rate'])
71:     else:
72:         stress = rat(source['floating_annual_rate'])
73:     principal, fixed, years = (rat(source[k]) for k in
74:                                ['principal', 'fixed_annual_rate', 'year_fraction'])
75:     values = [principal * ((1-x)*fixed+x*stress)*years for x in [F(0), F(1, 2), F(1)]]
76:     check(key + ' independent interest arithmetic', values == [rat(v) for v in row['expected']['at_x_0_half_1']])
77:     check(key + ' affine coefficients',
78:           values[0] == rat(row['expected']['interest_affine']['constant']) and
79:           values[2]-values[0] == rat(row['expected']['interest_affine']['coefficient_x']))
80: check('frontend agreement not asserted as executed',
81:       cases['LX01']['expected']['frontend_agreement'] == 'specified, not measured')
82: 
83: # Accumulate the preserved historical entries independently of their expected table.
84: ns = load(ROOT / examples['baseline']['path'])
85: balances = defaultdict(F, {k: F(v) for k, v in ns['opening'].items()})
86: check('opening balance', sum(balances.values()) == 0)
87: annual = defaultdict(F)
88: for period in ['2024H1', '2024H2']:
89:     movements = defaultdict(F)
90:     cashflows = defaultdict(F)
91:     for event in ns['historical_events']:
92:         if event['period'] != period:
93:             continue
94:         lines = [(p['account'], F(p['signed_amount'])) for p in event['postings']]
95:         check('balanced authored event ' + event['id'], sum(v for _, v in lines) == 0)
96:         for name, value in lines:
97:             balances[name] += value
98:             movements[name] += value
99:             if name == 'cash' and event['cash_class']:
100:                 cashflows[event['cash_class']] += value
101:     temporary = [k for k, role in ns['accounts'].items() if role in ['income', 'expense']]
102:     profit = -sum(movements[k] for k in temporary)
103:     revenue = -movements['revenue']
104:     for name in temporary:
105:         balances['retained'] += balances[name]
106:         balances[name] = F(0)
107:     assets = sum(balances[k] for k, role in ns['accounts'].items() if role in ['asset', 'contra_asset'])
108:     observed = {'cash': balances['cash'], 'receivables': balances['receivables'],
109:                 'inventory': balances['inventory'], 'plant_net': balances['plant_cost']+balances['accum_depreciation'],
110:                 'tax_prepaid': balances['tax_prepaid'], 'assets': assets,
111:                 'payables': -balances['payables'], 'debt': -balances['debt'],
112:                 'equity': -balances['capital']-balances['retained'],
113:                 'revenue': revenue, 'profit': profit,
114:                 **{k+'_cash': cashflows[k] for k in ['operating', 'investing', 'financing']}}
115:     for name, wanted in ns['expected'][period].items():
116:         check(period + ' ' + name, observed[name] == F(wanted))
117:     for name in ['revenue', 'profit', 'operating_cash', 'investing_cash', 'financing_cash']:
118:         annual[name] += observed[name]
119:     check(period + ' closed balance', sum(balances.values()) == 0)
120: annual['cash_change'] = balances['cash']-F(ns['opening']['cash'])
121: for name, wanted in ns['expected']['2024FY'].items():
122:     check('2024FY ' + name, annual[name] == F(wanted))
123: 
124: bridges = cases['IX01']['expected']['historical_reconstruction']
125: check('receivables bridge', F(ns['opening']['receivables'])+annual['revenue']-balances['receivables'] == rat(bridges['collections']))
126: historical_cogs = sum(F(p['signed_amount']) for e in ns['historical_events'] for p in e['postings'] if p['account'] == 'cost_of_sales')
127: purchases = balances['inventory']-F(ns['opening']['inventory'])+historical_cogs
128: check('inventory bridge', purchases == rat(bridges['purchases']))
129: check('payables bridge', -F(ns['opening']['payables'])+purchases+balances['payables'] == rat(bridges['supplier_payments']))
130: 
131: # Derive forecast flows from demand, collection, purchase and payment assumptions.
132: # Three x values check connected identities; the algebra is affine by construction.
133: f = {k: F(v) for k, v in ns['forecast'].items() if k not in ['start', 'end_exclusive']}
134: 
135: 
136: def company(x, floating_rate):
137:     revenue = f['demand_units']*f['price']
138:     cogs = f['demand_units']*f['unit_cost']
139:     ending_inventory = f['target_inventory_units']*f['unit_cost']
140:     purchases = ending_inventory-balances['inventory']+cogs
141:     collections = f['current_sales_collection_fraction']*revenue+f['legacy_receivable_collections']
142:     supplier_payment = f['old_payables_paid']+f['new_purchases_paid']
143:     # Existing plant and two additions: 10 + 10/5 + 12/12.
144:     depreciation = F(10)+F(10, 5)+F(12, 12)
145:     interest = -balances['debt']*((1-x)*F(1, 20)+x*floating_rate)
146:     pbt = revenue-cogs-f['payroll']-depreciation-interest
147:     tax = f['tax_rate']*max(F(0), pbt)
148:     profit = pbt-tax
149:     ocf = collections-supplier_payment-f['payroll']-interest-tax
150:     cash = balances['cash']+ocf-f['capex_at_period_end']-f['dividend']
151:     ar = balances['receivables']+revenue-collections
152:     ap = -balances['payables']+purchases-supplier_payment
153:     plant = balances['plant_cost']+balances['accum_depreciation']+f['capex_at_period_end']-depreciation
154:     equity = -balances['capital']-balances['retained']+profit-f['dividend']
155:     assets = cash+ar+ending_inventory+plant
156:     check('scenario balance ' + str((x, floating_rate)), assets == ap-balances['debt']+equity)
157:     return {'interest':interest,'profit_before_tax':pbt,'tax':tax,'profit':profit,
158:             'operating_cash':ocf,'cash':cash,'equity':equity,'assets':assets,
159:             'receivables':ar,'inventory':ending_inventory,'payables':ap,
160:             'debt':-balances['debt'],'plant_net':plant}
161: 
162: 
163: for x in [F(0), F(1, 2), F(1)]:
164:     result = company(x, F(7, 100))
165:     for name, coefficients in cases['IX01']['expected']['joint_affine'].items():
166:         check('joint forecast ' + str(x) + ' ' + name,
167:               result[name] == rat(coefficients['constant'])+x*rat(coefficients['coefficient_x']))
168:     for name, value in cases['IX01']['expected']['constant_balances'].items():
169:         check('constant balance ' + str(x) + ' ' + name, result[name] == rat(value))
170:     if x in [F(0), F(1)]:
171:         old = ns['expected']['2025_fixed' if x == 0 else '2025_floating']
172:         for name in result.keys() & old.keys():
173:             check('protected endpoint ' + str(x) + ' ' + name, result[name] == F(old[name]))
174:     else:
175:         for name, value in cases['IX01']['expected']['midpoint'].items():
176:             check('midpoint ' + name, result[name] == rat(value))
177: changed = company(F(1), F(9, 100))
178: for name, wanted in cases['IX02']['expected']['all_floating'].items():
179:     check('changed rate ' + name, changed[name] == rat(wanted))
180: 
181: partial = cases['FX01']
182: mass = [rat(x) for x in partial['inputs']['masses']]
183: known = rat(partial['inputs']['cash'][0])
184: check('partial mass conserved', sum(mass) == 1)
185: derived_bounds = [mass[0]*known+mass[1]*rat(b) for b in partial['inputs']['independent_unresolved_bounds']]
186: check('unconditional mean bounds', derived_bounds == [rat(v) for v in partial['expected']['mean_bounds']])
187: check('no invented mean', partial['expected']['unconditional_mean'] is None)
188: check('zero conditioning mass', sum(rat(v) for i,v in enumerate(cases['FX02']['inputs']['prior']) if i in cases['FX02']['inputs']['event_members']) == 0)
189: check('economic shortfall', rat(cases['FX04']['inputs']['due'])-rat(cases['FX04']['inputs']['available_cash']) == rat(cases['FX04']['expected']['shortfall']))
190: check('overlapping classifications', sum(rat(x) for x in cases['IX05']['inputs']['revenue_by_product']) == sum(rat(x) for x in cases['IX05']['inputs']['revenue_by_region']) == rat(cases['IX05']['expected']['revenue']))
191: check('migration exact decimal', F(cases['PX08']['inputs']['original_value']) == rat(cases['PX08']['inputs']['candidate_exact']) != rat(cases['PX08']['inputs']['adversarial_candidate']))
192: check('specified replay has no second post', cases['PX01']['expected']['event_posting_count'] == 1 and not cases['PX02']['expected']['additional_commit'])
193: check('counterpart traces explicitly unexecuted', all('no database' in c['evidence_limit'] for c in cases.values() if c['id'].startswith('PX')))
194: 
195: out = Path(sys.argv[1]).resolve()
196: failed = [c for c in checks if not c['passed']]
197: report = {'passed':not failed,'checks':checks,'failures':failed,
198:           'input_hashes':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(used)},
199:           'manifest':{'command':'python3 docs/design/proposal/architecture/platform-contract-calculation-v1.py '+str(out),
200:                       'git_commit':'N/A: historical repository marker is unusable',
201:                       'environment':platform.python_version()+' standard library',
202:                       'cpu_gpu':'CPU only; no accelerator framework imported',
203:                       'seeds':'N/A: deterministic exact arithmetic',
204:                       'data_version':examples['baseline'],
205:                       'wall_seconds':round(time.monotonic()-START,4),
206:                       'plan':'docs/plans/accounting-p16-direct-execution-20261006.md','result':str(out)},
207:           'limits':'Exact finite document calculations and pins only. No compiler, runtime, solver, storage/recovery, accounting-authority or empirical-forecast acceptance.'}
208: with out.open('x') as stream:
209:     json.dump(report,stream,indent=2)
210:     stream.write('\n')
211: print(json.dumps({'passed':not failed,'checks':len(checks),'failures':failed,'result':str(out)}))
212: sys.exit(1 if failed else 0)


FILE: docs/design/proposal/architecture/accounting-complete-exchanges-diagnostic-v1.py
SHA256: 00a990ba82a09147c6670e613dbe39dbe1f8578127f7de7cee4c294e8d678e3f
1: """Finite proposal-document checks; no product endpoint or accounting engine.
2: 
3: Derive adverse findings from submitted fields. Retained native comparators supply
4: unchanged treatment facts, not an oracle for the malformed/context predicates.
5: """
6: import copy
7: import datetime
8: import hashlib
9: import importlib.util
10: import json
11: import platform
12: import sys
13: import time
14: from fractions import Fraction
15: from pathlib import Path
16: 
17: START = time.monotonic()
18: B = Path('docs/design/proposal/architecture')
19: D = 'accdsl.accounting.integration.v1'
20: checks, results, used = [], [], {str(Path(__file__))}
21: 
22: 
23: def load(path):
24:     used.add(str(path))
25:     return json.loads(Path(path).read_text())
26: 
27: 
28: def check(label, value):
29:     checks.append({'id':label,'passed':bool(value)})
30: 
31: 
32: def canonical(value):
33:     return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)
34: 
35: 
36: def digest(domain, kind, value):
37:     return hashlib.sha256((domain+'/'+kind+'\0'+canonical(value)).encode('ascii')).hexdigest()
38: 
39: 
40: def pins(value):
41:     if isinstance(value,dict):
42:         if 'path' in value and 'sha256' in value:
43:             p=Path(value['path']);used.add(str(p))
44:             check('file pin '+str(p),p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==value['sha256'])
45:         for child in value.values():pins(child)
46:     elif isinstance(value,list):
47:         for child in value:pins(child)
48: 
49: 
50: f=load(B/'accounting-complete-exchanges-v1.json')
51: pins(f)
52: registry={}
53: for ref in f['imports']:
54:     for h,row in load(ref['path'])['records'].items():
55:         domains=[d for d in [D,'accdsl.accounting.records.v1','accdsl.accounting.record.v1'] if digest(d,row['kind'],row['content'])==h]
56:         check('unambiguous imported digest '+h,len(domains)==1)
57:         registry[h]={**row,'domain':domains[0]}
58: registry.update(f['records'])
59: for h,row in f['records'].items():
60:     check('new record digest '+h,digest(row['domain'],row['kind'],row['content'])==h)
61: old=load(B/'accounting-integration-fixtures-v2.json')
62: I={c['id']:c for c in old['cases']}
63: sources={c['id']:c for c in load(f['source_packets']['path'])['cases']}
64: field_path=B/'accounting-integration-c09-c10-conditions-field-diagnostic-v1.py'
65: used.add(str(field_path))
66: spec=importlib.util.spec_from_file_location('finite_field_diagnostic',field_path)
67: field=importlib.util.module_from_spec(spec)
68: spec.loader.exec_module(field)
69: ROUTES=['identical_instrument_active_market_quote','technique_only_observable_market_data']
70: 
71: 
72: def source(ref):
73:     return next(c for c in load(ref['file']['path'])['cases'] if c['id']==ref['case_id'])['complete_inputs']
74: 
75: 
76: def content(h):
77:     return registry[h]['content']
78: 
79: 
80: def native_branch(c09):
81:     if not c09['required']:return 'not_applicable'
82:     a,b=(c09[k] for k in ROUTES)
83:     if a is True or b is True:return 'B5.1.2A(a)'
84:     if a is False and b is False:return 'B5.1.2A(b)'
85:     return 'unknown'
86: 
87: 
88: def context_findings(s,q):
89:     found=[]
90:     def need(path,ok,code='SOURCE_CONTEXT_MISMATCH'):
91:         if not ok:found.append({'stage':'bindings','path':path,'code':code})
92:     values={k:v['value'] for k,v in s.items()}
93:     ev,ctx,tm=content(q['event']),content(q['context']),content(q['time'])
94:     el=content(q['eligibility'])
95:     c1=values['C01'];day=datetime.date.fromisoformat(c1['annual_period_start'])
96:     need('source/C01/value/annual_period_start',c1['annual_period_start']==ctx['annual_period_start'])
97:     need('source/C01/value/within_retained_window',c1['within_retained_window']==(datetime.date(2023,1,1)<=day<datetime.date(2026,7,1)))
98:     need('source/C04/value/recognition_date',values['C04']['recognition_date']==tm['economic_date'])
99:     need('source/C05/value/category',values['C05']['category']==ev['category'])
100:     for name in ['price','fair_value']:
101:         need('source/C06/value/'+name,Fraction(values['C06'][name])==Fraction(ev[name]))
102:     need('source/C06/value/valuation_date',values['C06']['valuation_date']==tm['economic_date'])
103:     need('source/C07/value/amount',Fraction(values['C07']['amount'])==Fraction(ev['fee']))
104:     for name in ['currency','unit','scale']:
105:         need('source/C08/value/'+name,values['C08'][name]==ctx[name])
106:     for name in ['entity','book','branch']:
107:         need('source/C08/value/'+name,values['C08'][name]==el['aliases']['source_labels'][name])
108:     c9=values['C09'];required=Fraction(values['C06']['price'])!=Fraction(values['C06']['fair_value'])
109:     need('source/C09/value/required',c9['required'] is required)
110:     # Branch/OR projection depend on a consistent required controller. This is
111:     # an explicit guard, not coercion of an invalid controller to false.
112:     if c9['required'] is required:
113:         need('source/C09/value/branch',c9['branch']==native_branch(c9))
114:         if not required:
115:             for k in ROUTES:need('source/C09/value/'+k,c9[k] is None)
116:         evidence=content(q['evidence'][0])['observable_valuation']
117:         if not required or native_branch(c9)=='unknown':
118:             need('evidence/observable_valuation',evidence['status']=='unknown')
119:         else:
120:             need('evidence/observable_valuation',evidence['status']=='known' and evidence['value'] is (native_branch(c9)=='B5.1.2A(a)'))
121:     for flag in ['unequal_price_a_method_available','unequal_price_b_method_available']:
122:         need('source/C10/value/'+flag,values['C10'][flag] is False,'METHOD_CAPABILITY_MISMATCH')
123:     return sorted(found,key=lambda d:(d['path'],d['code']))
124: 
125: 
126: def closure(q,label):
127:     reached=set()
128:     def walk(value):
129:         if isinstance(value,dict):
130:             if 'path' in value and 'sha256' in value:
131:                 pins(value);return
132:             for child in value.values():walk(child)
133:         elif isinstance(value,list):
134:             for child in value:walk(child)
135:         elif isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value):
136:             check(label+' reference resolves '+value,value in registry)
137:             if value in registry and value not in reached:
138:                 reached.add(value);walk(content(value))
139:     walk(q)
140:     return sorted(reached)
141: 
142: 
143: for c in old['cases']:
144:     q=content(c['request']);s=source(c['source_case'])
145:     shape=field.derive({k:s[k] for k in ['C09','C10']})
146:     findings=context_findings(s,q) if not shape else shape
147:     check(c['id']+' retained control satisfies new predicates',not findings)
148:     if findings:results.append({'id':c['id'],'derived':findings})
149: 
150: for x in f['exchanges']:
151:     label=x['id'];base=I[x['control']['case_id']];q=json.loads(x['raw_request'])
152:     check(label+' request bytes',canonical(q)==x['raw_request'] and digest(D,'request',q)==x['request'])
153:     check(label+' submitted bytes',content(x['submission'])['raw_text']==x['raw_request'])
154:     check(label+' exact closure',closure(q,label)==x['required_record_closure'])
155:     s=source(x['source_case']);before=source(base['source_case']);expected=copy.deepcopy(before)
156:     for change in x['mutations']:
157:         parts=change['path'].split('/')[1:];parent=expected
158:         for p in parts[:-1]:parent=parent[p]
159:         check(label+' mutation prior '+change['path'],parent[parts[-1]]==change['before'])
160:         if change['op']=='remove':del parent[parts[-1]]
161:         else:parent[parts[-1]]=change['after']
162:     check(label+' isolated source changes',s==expected)
163:     eligibility=content(q['eligibility'])
164:     check(label+' full condition order',[c['condition_id'] for c in eligibility['conditions']]==['C%02d'%i for i in range(1,11)])
165:     check(label+' refreshed source refs',eligibility['source_case']==x['source_case'] and all(c['case']==x['source_case'] for c in eligibility['conditions']))
166:     findings=[{k:d[k] for k in ['stage','path','code']} for d in field.derive({k:s[k] for k in ['C09','C10'] if k in s})]
167:     if not findings:
168:         check(label+' source version bindings',all(c['value_version']==s[c['condition_id']]['version'] for c in eligibility['conditions']))
169:         findings=context_findings(s,q)
170:     check(label+' derived findings',findings==x['expected_diagnostics'])
171:     response=content(x['response'])
172:     check(label+' committed domains unchanged',x['before']==x['after']==base['before'])
173:     check(label+' no posting or receipt publication',not response['additional_commit'] and response['commit_status']=='not_committed' and all(response[k] is None for k in ['diagnostic_journal','diagnostic_delta','receipt','observed_state']))
174:     check(label+' derived validation before lookup',x['lookup']==x['freshness']==x['assess']==(not findings))
175:     if findings:
176:         check(label+' invalid request not published',response['request'] is None and response['assessment'] is None and x['assessment'] is None and response['status']=='rejected')
177:         check(label+' rejection status dimensions',response['statuses']==dict(structural_validity='invalid',mathematical_status='unresolved',computation_status='not_computed',empirical_justification='not_established',capability_status='specified_only_no_runtime',accounting_validity='not_assessed',human_acceptance='pending'))
178:         check(label+' complete reason codes',response['reason_codes']==list(dict.fromkeys(d['code'] for d in findings)))
179:     else:
180:         original=content(base['assessment']);want=copy.deepcopy(original)
181:         want.update(request=x['request'],eligibility=q['eligibility'],source_assessment=x['source_case'])
182:         check(label+' complete assessment preservation',content(x['assessment'])==want)
183:         want_response=copy.deepcopy(content(base['response']));want_response.update(submission=x['submission'],request=x['request'],assessment=x['assessment'])
184:         check(label+' complete response preservation',response==want_response)
185:         # Only explanatory reasons may differ in these positive variations.
186:         original_facts=copy.deepcopy(before);new_facts=copy.deepcopy(s)
187:         for fact in [original_facts,new_facts]:
188:             fact['C09'].pop('unknown_reason');fact['C09']['value'].pop('unknown_reason');fact['C10'].pop('unknown_reason')
189:         check(label+' economic facts unchanged',original_facts==new_facts)
190:     results.append({'id':label,'derived':findings,'lookup':not findings})
191: 
192: # The V records were already materialized. Inspect their actual candidate data,
193: # without using their IDs, mutation paths, declared stages or expected findings
194: # to select a predicate.
195: v=load(f['retained_adverse_outputs']['path'])
196: 
197: 
198: def adverse_outcome(reg,q,output_digest):
199:     def rec(h):return reg[h]['content']
200:     if reg[q['eligibility']]['kind']!='eligibility_input':return 'dependencies','INVALID_REFERENCE_KIND'
201:     e=rec(q['eligibility'])
202:     if q['operation']!='assess_only' or e['profile']!='acquisition-conditions-v1':return 'shape','UNSUPPORTED_PROFILE_OPERATION'
203:     if type(e['schema_version']) is not int:return 'shape','INVALID_RECORD_VERSION_TYPE'
204:     if e['aliases']['scope']!='synthetic_only':return 'shape','INVALID_ALIAS_SCOPE'
205:     if [c['condition_id'] for c in e['conditions']]!=['C%02d'%i for i in range(1,11)]:return 'shape','INVALID_CONDITION_ORDER'
206:     if not {'context','branch','time','chart','authority','method','assumptions','evidence','admissions'}.issubset(e['bindings']):return 'shape','MISSING_FIELD'
207:     if any(e['aliases']['identity'][k]!=q['identity'][k] for k in ['entity_id','book_id','branch_id']):return 'bindings','ELIGIBILITY_BINDING_MISMATCH'
208:     s=source(e['source_case'])
209:     if any(e['aliases']['source_labels'][k]!=s['C08']['value'][k] for k in ['entity','book','branch']):return 'bindings','ELIGIBILITY_BINDING_MISMATCH'
210:     if any(c['case']!=e['source_case'] for c in e['conditions']):return 'bindings','CONDITION_CASE_MISMATCH'
211:     if output_digest is None:return None
212:     r=reg[output_digest]
213:     if r['kind']=='response':
214:         z=r['content']
215:         if z['additional_commit'] or z['commit_status']!='not_committed':return 'assessment_consistency','ASSESSMENT_OUTPUT_INVALID'
216:         a=rec(z['assessment'])
217:     else:a=r['content']
218:     if a['posting_permitted']:return 'assessment_consistency','ASSESSMENT_OUTPUT_INVALID'
219:     ids=[x['condition'] for x in a['findings']]
220:     if ids!=['C%02d'%i for i in range(1,11)]:return 'assessment_consistency','ASSESSMENT_OUTPUT_INVALID'
221:     statuses={x['status'] for x in a['findings']}
222:     summary=next((k for k in ['ineligible','outside_scope','unresolved'] if k in statuses),'eligible')
223:     if a['status']!=summary:return 'assessment_consistency','ASSESSMENT_OUTPUT_INVALID'
224:     for route in a['valuation_routes']:
225:         value=s['C09']['value'][route['field']]
226:         if route['value'] is not value:return 'assessment_consistency','ASSESSMENT_OUTPUT_INVALID'
227:     if a['diagnostic_example'] is not None and summary!='eligible':return 'assessment_consistency','ASSESSMENT_OUTPUT_INVALID'
228:     return None
229: 
230: 
231: for x in v['cases']:
232:     reg={**registry,**x['candidate_records']};q=json.loads(x['raw_request'])
233:     actual=adverse_outcome(reg,q,x.get('candidate_output_digest'))
234:     wanted=(x['expected']['stage'],x['expected']['code'])
235:     check(x['id']+' candidate-derived disposition',actual==wanted)
236:     check(x['id']+' unchanged four domains',x['expected']['before']==x['expected']['after'])
237:     results.append({'id':x['id'],'derived':actual})
238: 
239: out=Path(sys.argv[1]);failures=[c for c in checks if not c['passed']]
240: report={'passed':not failures,'checks':checks,'failures':failures,'derived_results':results,
241:         'input_hashes':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sorted(used)},
242:         'manifest':{'command':'python3 '+str(Path(__file__))+' '+str(out),
243:                     'environment':platform.python_version()+' standard library','cpu_gpu':'CPU only; no accelerator framework imported',
244:                     'git_commit':'N/A: existing unusable repository marker','random_seeds':'N/A deterministic examples',
245:                     'wall_seconds':round(time.monotonic()-START,4),'plan':'docs/plans/accounting-p16-direct-execution-20261006.md','result':str(out)},
246:         'scope':'27 complete new exchanges, 17 retained controls, 16 independently classified V outcomes; finite document checks only. No arbitrary validator, runtime, accounting-authority or phase acceptance.'}
247: with out.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
248: print(json.dumps({'passed':not failures,'checks':len(checks),'failures':failures,'result':str(out)}))
249: sys.exit(1 if failures else 0)


SPECIFIED PLATFORM EXAMPLES (not runtime wire receipts):
{
 "schema": "accdsl.proposal.platform.examples.v1",
 "evidence_mode": "specification_example",
 "product_implemented": false,
 "human_acceptance": "pending",
 "baseline": {
  "path": "docs/design/fixtures/northstar.json",
  "sha256": "3ca1b8c9f128e2ad77bf2e618388caf7b139203fafc1f60bffde1d4094b71b2e",
  "locator": "opening; historical_events; forecast; expected"
 },
 "references": [
  {
   "path": "docs/design/proposal/architecture/language-ir-contract-v1.md",
   "sha256": "e2cdc3c82d34786364ad4180b0b26581bd8b70eeb6179e4ef6e0e150208bdb1f",
   "locator": "Proposed contract sections and named example families"
  },
  {
   "path": "docs/design/proposal/architecture/persistence-contract-v1.md",
   "sha256": "64930493a2a4683cbb09816f979166b18d27401685fd37772f2aebe35fe1c584",
   "locator": "Proposed contract sections and named example families"
  },
  {
   "path": "docs/design/proposal/architecture/interfaces-contract-v1.md",
   "sha256": "a7235c3485e8942a6a0e4251ae893d3f531a7ea601ad62f506a57936975ca491",
   "locator": "Proposed contract sections and named example families"
  },
  {
   "path": "docs/design/proposal/architecture/failure-contract-v1.md",
   "sha256": "1de4e0151e5c6c8311aa7d4695134c7ee419501384a79ff227c66ad8bb79cdf6",
   "locator": "Proposed contract sections and named example families"
  },
  {
   "path": "docs/design/proposal/architecture/initial-profile-v1.md",
   "sha256": "7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb",
   "locator": "Proposed contract sections and named example families"
  },
  {
   "path": "docs/design/proposal/architecture/architecture-integration-v1.md",
   "sha256": "29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1",
   "locator": "Proposed contract sections and named example families"
  }
 ],
 "cases": [
  {
   "id": "LX01",
   "operation": "model.compile@1",
   "inputs": {
    "text_source": "module BorrowingExample version \"1\";\nuse DemoDebt version \"1\";\nsource note7 = external(\"synthetic-note-7\");\nentity Acme functional USD;\nbook Local entity Acme basis DemoDebt version \"1\";\naccount Cash : Asset book Local;\naccount Debt : Liability book Local;\naccount InterestExpense : Expense book Local;\naccount Retained : Equity book Local;\nopening after2025 for Local from external(\"after-2025-close\");\nobservation debt : Money<USD> instant @2025-12-31 = 100 USD from note7;\nsymbol x : Real in [0, 1] because \"Floating-rate proportion not disclosed\";\ncontract loans : DebtMix book Local {\n  principal = value(debt);\n  fixed_fraction = 1 - x;\n  fixed_rate = 0.05 per year;\n  initial_floating_rate = 0.05 per year;\n}\nscenario rateShock { set market_rate = constant(0.07 per year); }\nreport statements for Local { mapping = external(\"DemoDebt.statements.v1\"); }\n",
    "typed_construction": {
     "principal": {
      "n": "100",
      "d": "1"
     },
     "floating_fraction": {
      "symbol": "x",
      "domain": [
       {
        "n": "0",
        "d": "1"
       },
       {
        "n": "1",
        "d": "1"
       }
      ],
      "uncertainty": "unknown_economic_fact"
     },
     "fixed_annual_rate": {
      "n": "1",
      "d": "20"
     },
     "floating_annual_rate": {
      "n": "7",
      "d": "100"
     },
     "year_fraction": {
      "n": "1",
      "d": "1"
     },
     "currency": "USD",
     "admission": "authored synthetic assumption; not source or accounting acceptance"
    },
    "binding_obligations": [
     "source note7",
     "debt reading",
     "opening after2025",
     "DemoDebt package/report",
     "symbol assumption admission",
     "scenario assumption admission"
    ],
    "legacy_profile": "Core0 lexical/declaration fragment; proposed portable lowering; no execution of the old compiler"
   },
   "expected": {
    "semantic_projection": {
     "principal": {
      "n": "100",
      "d": "1"
     },
     "floating_fraction": {
      "symbol": "x",
      "domain": [
       {
        "n": "0",
        "d": "1"
       },
       {
        "n": "1",
        "d": "1"
       }
      ],
      "uncertainty": "unknown_economic_fact"
     },
     "fixed_annual_rate": {
      "n": "1",
      "d": "20"
     },
     "floating_annual_rate": {
      "n": "7",
      "d": "100"
     },
     "year_fraction": {
      "n": "1",
      "d": "1"
     },
     "currency": "USD",
     "admission": "authored synthetic assumption; not source or accounting acceptance"
    },
    "interest_affine": {
     "constant": {
      "n": "5",
      "d": "1"
     },
     "coefficient_x": {
      "n": "2",
      "d": "1"
     }
    },
    "at_x_0_half_1": [
     {
      "n": "5",
      "d": "1"
     },
     {
      "n": "6",
      "d": "1"
     },
     {
      "n": "7",
      "d": "1"
     }
    ],
    "frontend_agreement": "specified, not measured",
    "law": null
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "LX02",
   "operation": "model.compile@1",
   "inputs": {
    "base": "LX01",
    "replace": {
     "floating_annual_rate": {
      "n": "9",
      "d": "100"
     }
    }
   },
   "expected": {
    "interest_affine": {
     "constant": {
      "n": "5",
      "d": "1"
     },
     "coefficient_x": {
      "n": "4",
      "d": "1"
     }
    },
    "at_x_0_half_1": [
     {
      "n": "5",
      "d": "1"
     },
     {
      "n": "7",
      "d": "1"
     },
     {
      "n": "9",
      "d": "1"
     }
    ]
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "LX03",
   "operation": "model.compile@1",
   "inputs": {
    "add": [
     {
      "value": {
       "n": "1",
       "d": "1"
      },
      "currency": "USD"
     },
     {
      "value": {
       "n": "1",
       "d": "1"
      },
      "currency": "EUR"
     }
    ]
   },
   "expected": {
    "code": "CONTEXT_MISMATCH",
    "executable_ir": null,
    "committed": false
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "LX04",
   "operation": "model.compile@1",
   "inputs": {
    "candidate_symbol": "x",
    "admission_ref": null
   },
   "expected": {
    "code": "ADMISSION_REQUIRED",
    "executable_ir": null,
    "committed": false
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "LX05",
   "operation": "model.compile@1",
   "inputs": {
    "formula": "x*x",
    "domain": [
     {
      "n": "0",
      "d": "1"
     },
     {
      "n": "1",
      "d": "1"
     }
    ],
    "backend": "rational_affine"
   },
   "expected": {
    "code": "UNSUPPORTED_CAPABILITY",
    "executable_ir": null,
    "committed": false
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "LX06",
   "operation": "model.compile@1",
   "inputs": {
    "wire": "{\"revision\":1,\"revision\":2}"
   },
   "expected": {
    "code": "DUPLICATE_KEY",
    "executable_ir": null,
    "committed": false
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "LX07",
   "operation": "model.compile@1",
   "inputs": {
    "package": "Unknown@1",
    "lock": []
   },
   "expected": {
    "code": "MISSING_REQUIRED_DEPENDENCY",
    "executable_ir": null,
    "committed": false
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "LX08",
   "operation": "model.compile@1",
   "inputs": {
    "opening_stock": {
     "date": "2024-01-01",
     "cash": {
      "n": "60",
      "d": "1"
     }
    },
    "closing_stock": {
     "date": "2024-12-31",
     "cash": {
      "n": "373",
      "d": "5"
     }
    },
    "operation": "sum_as_flow"
   },
   "expected": {
    "code": "CONTEXT_MISMATCH",
    "executable_ir": null,
    "committed": false
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "PX01",
   "operation": "accounting.commit@1",
   "inputs": {
    "stable_key": [
     "E",
     "B",
     "projection-A",
     "event-1"
    ],
    "fingerprint": "fp1",
    "head": [
     "s0",
     0
    ],
    "schedule": [
     "validate",
     "commit journal j1/delta d1/state s1/receipt r1",
     "response lost",
     "retry same key/fingerprint"
    ]
   },
   "expected": {
    "client_first_observation": "unknown",
    "recovered_receipt": "r1",
    "recovered_head": [
     "s1",
     1
    ],
    "event_posting_count": 1,
    "additional_commit_on_retry": false
   },
   "evidence_limit": "Specified transaction trace; no database, crash or concurrency experiment."
  },
  {
   "id": "PX02",
   "operation": "accounting.commit@1",
   "inputs": {
    "stored_key": [
     "E",
     "B",
     "projection-A",
     "event-1"
    ],
    "stored_fingerprint": "fp1",
    "stored_receipt": "r1",
    "historical_opening": "s0",
    "current_head": [
     "s2",
     2
    ],
    "retry_fingerprint": "fp1"
   },
   "expected": {
    "disposition": "replayed",
    "receipt": "r1",
    "head": [
     "s2",
     2
    ],
    "additional_commit": false,
    "freshness_evaluated": false
   },
   "evidence_limit": "Specified transaction trace; no database, crash or concurrency experiment."
  },
  {
   "id": "PX03",
   "operation": "accounting.commit@1",
   "inputs": {
    "stored_fingerprint": "fp1",
    "same_stable_key": true,
    "submitted_fingerprint": "fp2",
    "changed": "event version or payload"
   },
   "expected": {
    "code": "EVENT_ID_CONFLICT",
    "committed_domains": "unchanged"
   },
   "evidence_limit": "Specified transaction trace; no database, crash or concurrency experiment."
  },
  {
   "id": "PX04",
   "operation": "accounting.commit@1",
   "inputs": {
    "head": [
     "s0",
     0
    ],
    "writers": [
     {
      "event": "a",
      "expected": [
       "s0",
       0
      ]
     },
     {
      "event": "b",
      "expected": [
       "s0",
       0
      ]
     }
    ],
    "commit_order": [
     "a",
     "b"
    ]
   },
   "expected": {
    "a": "committed",
    "b": "STALE_OPENING_STATE",
    "generation": 1,
    "event_posting_count": 1
   },
   "evidence_limit": "Specified transaction trace; no database, crash or concurrency experiment."
  },
  {
   "id": "PX05",
   "operation": "review.commit@1",
   "inputs": {
    "old_view": "v1",
    "edges": [
     [
      "candidate_membership",
      "selection"
     ],
     [
      "selection",
      "model"
     ],
     [
      "model",
      "result"
     ]
    ],
    "correction": "new eligible source member",
    "new_descendant": {
     "name": "late_result",
     "depends_on": "model",
     "created_after_correction": true
    }
   },
   "expected": {
    "new_view": "v2",
    "current_invalid": [
     "selection",
     "model",
     "result",
     "late_result"
    ],
    "historical_v1": "readable",
    "unrelated_closure": "usable"
   },
   "evidence_limit": "Specified transaction trace; no database, crash or concurrency experiment."
  },
  {
   "id": "PX06",
   "operation": "accounting.commit@1",
   "inputs": {
    "events": [
     {
      "key": [
       "E",
       "B",
       "projection-A",
       "event-1"
      ],
      "fingerprint": "fp1"
     },
     {
      "key": [
       "E",
       "B",
       "projection-B",
       "event-1"
      ],
      "fingerprint": "fpB"
     }
    ],
    "projection_B": "separately commissioned hypothetical"
   },
   "expected": {
    "separate_receipts": true,
    "realized_event_count": "cannot sum hypothetical projections",
    "retry_projection_A": "original identity"
   },
   "evidence_limit": "Specified transaction trace; no database, crash or concurrency experiment."
  },
  {
   "id": "PX07",
   "operation": "store.import@1",
   "inputs": {
    "manifest_required": [
     "request",
     "rule",
     "raw_source"
    ],
    "available": [
     "request",
     "rule"
    ]
   },
   "expected": {
    "code": "MISSING_REQUIRED_DEPENDENCY",
    "domain_mutation": false
   },
   "evidence_limit": "Specified transaction trace; no database, crash or concurrency experiment."
  },
  {
   "id": "PX08",
   "operation": "store.migrate@1",
   "inputs": {
    "original_value": "102.00",
    "decoded_exact": {
     "n": "102",
     "d": "1"
    },
    "candidate_exact": {
     "n": "102",
     "d": "1"
    },
    "adversarial_candidate": {
     "n": "100",
     "d": "1"
    },
    "original_identity": "legacy1"
   },
   "expected": {
    "representation_mapping": "preserve legacy1 and portable identity; exact value 102",
    "adversarial": "MIGRATION_COMPARISON_FAILED",
    "old_snapshot": "unchanged and usable"
   },
   "evidence_limit": "Specified transaction trace; no database, crash or concurrency experiment."
  },
  {
   "id": "FX01",
   "operation": "uncertainty.evaluate@1",
   "inputs": {
    "masses": [
     {
      "n": "3",
      "d": "5"
     },
     {
      "n": "2",
      "d": "5"
     }
    ],
    "cash": [
     {
      "n": "120",
      "d": "1"
     },
     null
    ],
    "independent_unresolved_bounds": [
     {
      "n": "80",
      "d": "1"
     },
     {
      "n": "110",
      "d": "1"
     }
    ]
   },
   "expected": {
    "disposition": "partial",
    "known_mass": {
     "n": "3",
     "d": "5"
    },
    "unresolved_mass": {
     "n": "2",
     "d": "5"
    },
    "unconditional_mean": null,
    "mean_bounds": [
     {
      "n": "104",
      "d": "1"
     },
     {
      "n": "116",
      "d": "1"
     }
    ],
    "without_independent_bounds": null
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "FX02",
   "operation": "specified_failure",
   "inputs": {
    "prior": [
     {
      "n": "1",
      "d": "2"
     },
     {
      "n": "1",
      "d": "2"
     }
    ],
    "event_members": []
   },
   "expected": {
    "math": "undefined",
    "normalizer": {
     "n": "0",
     "d": "1"
    },
    "posterior": null,
    "computation": "complete"
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "FX03",
   "operation": "specified_failure",
   "inputs": {
    "query": "bound x*x",
    "backend": "affine_only",
    "domain": "x in [0,1]"
   },
   "expected": {
    "disposition": "unsupported",
    "exact_bound": null,
    "family": "retained"
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "FX04",
   "operation": "specified_failure",
   "inputs": {
    "due": {
     "n": "100",
     "d": "1"
    },
    "available_cash": {
     "n": "80",
     "d": "1"
    },
    "funding_limit": {
     "n": "0",
     "d": "1"
    },
    "method": "authored contractual shortfall only"
   },
   "expected": {
    "shortfall": {
     "n": "20",
     "d": "1"
    },
    "economic_outcome": "payment_shortfall",
    "computation": "complete",
    "legal_insolvency_or_accounting_loss": "not inferred"
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "FX05",
   "operation": "specified_failure",
   "inputs": {
    "work": "solver",
    "checkpoint": "cp1",
    "service_timeout": true
   },
   "expected": {
    "math": "unresolved",
    "computation": "failed",
    "continuation": "cp1",
    "infeasible": false
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "FX06",
   "operation": "specified_failure",
   "inputs": {
    "C09_required": true,
    "C09_routes": [
     true,
     null
    ],
    "C09_inner_reason": null,
    "C09_outer_reason": "Second route unknown"
   },
   "expected": {
    "code": "INVALID_UNKNOWN_REPRESENTATION",
    "stage": "shape",
    "lookup_performed": false,
    "commit": "not_committed"
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "FX07",
   "operation": "specified_failure",
   "inputs": {
    "write_started": true,
    "acknowledgement": null
   },
   "expected": {
    "disposition": "commit_unknown",
    "commit": "unknown",
    "retry": "inspect_commit_then_retry_same_identity"
   },
   "evidence_limit": "Specified transaction trace; no database, crash or concurrency experiment."
  },
  {
   "id": "IX01",
   "operation": "scenario.project@1 → report.build@1",
   "inputs": {
    "northstar": {
     "path": "docs/design/fixtures/northstar.json",
     "sha256": "3ca1b8c9f128e2ad77bf2e618388caf7b139203fafc1f60bffde1d4094b71b2e",
     "locator": "opening; historical_events; forecast; expected"
    },
    "floating_fraction_domain": [
     {
      "n": "0",
      "d": "1"
     },
     {
      "n": "1",
      "d": "1"
     }
    ],
    "scenario_rate": {
     "n": "7",
     "d": "100"
    },
    "source_scope": "closed synthetic package",
    "measure": null,
    "method_status": "authored teaching assumptions"
   },
   "expected": {
    "joint_affine": {
     "interest": {
      "constant": {
       "n": "5",
       "d": "1"
      },
      "coefficient_x": {
       "n": "2",
       "d": "1"
      }
     },
     "profit_before_tax": {
      "constant": {
       "n": "82",
       "d": "1"
      },
      "coefficient_x": {
       "n": "-2",
       "d": "1"
      }
     },
     "tax": {
      "constant": {
       "n": "82",
       "d": "5"
      },
      "coefficient_x": {
       "n": "-2",
       "d": "5"
      }
     },
     "profit": {
      "constant": {
       "n": "328",
       "d": "5"
      },
      "coefficient_x": {
       "n": "-8",
       "d": "5"
      }
     },
     "operating_cash": {
      "constant": {
       "n": "243",
       "d": "5"
      },
      "coefficient_x": {
       "n": "-8",
       "d": "5"
      }
     },
     "cash": {
      "constant": {
       "n": "476",
       "d": "5"
      },
      "coefficient_x": {
       "n": "-8",
       "d": "5"
      }
     },
     "equity": {
      "constant": {
       "n": "741",
       "d": "5"
      },
      "coefficient_x": {
       "n": "-8",
       "d": "5"
      }
     },
     "assets": {
      "constant": {
       "n": "1441",
       "d": "5"
      },
      "coefficient_x": {
       "n": "-8",
       "d": "5"
      }
     }
    },
    "constant_balances": {
     "receivables": {
      "n": "55",
      "d": "1"
     },
     "inventory": {
      "n": "40",
      "d": "1"
     },
     "plant_net": {
      "n": "98",
      "d": "1"
     },
     "payables": {
      "n": "40",
      "d": "1"
     },
     "debt": {
      "n": "100",
      "d": "1"
     }
    },
    "historical_reconstruction": {
     "collections": {
      "n": "245",
      "d": "1"
     },
     "purchases": {
      "n": "155",
      "d": "1"
     },
     "supplier_payments": {
      "n": "145",
      "d": "1"
     }
    },
    "midpoint": {
     "cash": {
      "n": "472",
      "d": "5"
     },
     "profit": {
      "n": "324",
      "d": "5"
     },
     "tax": {
      "n": "81",
      "d": "5"
     }
    },
    "probabilities": null,
    "journal_effect": "proposals, no committed-book write"
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "IX02",
   "operation": "scenario.project@1 → report.build@1",
   "inputs": {
    "base": "IX01",
    "scenario_rate": {
     "n": "9",
     "d": "100"
    }
   },
   "expected": {
    "all_floating": {
     "interest": {
      "n": "9",
      "d": "1"
     },
     "cash": {
      "n": "92",
      "d": "1"
     },
     "profit": {
      "n": "312",
      "d": "5"
     },
     "equity": {
      "n": "145",
      "d": "1"
     },
     "assets": {
      "n": "285",
      "d": "1"
     }
    }
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "IX03",
   "operation": "scenario.project@1",
   "inputs": {
    "base": "IX01",
    "current_sales_collection_fraction": null,
    "reason": "not specified"
   },
   "expected": {
    "unresolved": [
     "collections",
     "cash",
     "receivables",
     "operating_cash",
     "assets"
    ],
    "still_conditional": [
     "revenue",
     "cost_of_sales",
     "interest",
     "profit"
    ],
    "cash_not_zero": true
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "IX04",
   "operation": "time.select@1",
   "inputs": {
    "mode": "investor_information",
    "cutoff": "2024-08-01T00:00:00Z",
    "candidate_available": "2025-02-01T00:00:00Z",
    "ingested": "2025-02-02T00:00:00Z"
   },
   "expected": {
    "candidate_admitted": false,
    "code": "AFTER_INFORMATION_CUTOFF",
    "old_view": "preserved"
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "IX05",
   "operation": "report.build@1",
   "inputs": {
    "revenue_by_product": [
     {
      "n": "180",
      "d": "1"
     },
     {
      "n": "120",
      "d": "1"
     }
    ],
    "revenue_by_region": [
     {
      "n": "200",
      "d": "1"
     },
     {
      "n": "100",
      "d": "1"
     }
    ],
    "same_total_population": true,
    "requested": "sum both classifications"
   },
   "expected": {
    "code": "OVERLAPPING_AGGREGATION",
    "revenue": {
     "n": "300",
     "d": "1"
    },
    "forbidden_total": {
     "n": "600",
     "d": "1"
    }
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  },
  {
   "id": "IX06",
   "operation": "accounting.assess@1",
   "inputs": {
    "extension": "insurance contract group",
    "typed_record_available": true,
    "eligible_measurement_method": null
   },
   "expected": {
    "assessment": "unresolved",
    "code": "MISSING_REQUIRED_METHOD",
    "journal": null,
    "commit": false
   },
   "evidence_limit": "Specified financial consequences only; no frontend, solver or runtime execution."
  }
 ],
 "canonical_examples": {
  "raw_source_a": "é",
  "raw_source_b": "é",
  "different_codepoints_distinct": true,
  "wire_equivalent": [
   "{\"label\":\"é\"}",
   "{\"label\":\"\\u00e9\"}"
  ],
  "metadata_boolean": {
   "revision": true
  },
  "rational_zero": {
   "n": "0",
   "d": "1"
  },
  "ordered_events_a": [
   "sale",
   "collection"
  ],
  "ordered_events_b": [
   "collection",
   "sale"
  ],
  "set_dependencies_a": [
   "a",
   "b"
  ],
  "set_dependencies_b": [
   "b",
   "a"
  ]
 }
}

CURRENT DECISION DISPOSITIONS:
[
 {
  "id": "P15-E01",
  "question": "When may a filing package be called complete?",
  "proposed_answer": "Declare separate acquired-unit, reviewed-assertion and query-exposure populations and retain material unresolved incorporated targets.",
  "alternative": "A single completeness score or closure only over acquired files.",
  "consequence": "An aggregate score could conceal absent contracts and overstate downstream support.",
  "next_step": "Evidence E1–E4 and extraction-v1 define three populations and missing targets. Complete one real declared annual/interim package and cross-reference/query example in P17; do not count the closed synthetic package as that evidence.",
  "blocks_proposal": true,
  "p16_status": "specified_contract; real_package_demonstration_pending",
  "owning_phase": "P17",
  "disposition_evidence": [
   {
    "path": "docs/design/proposal/architecture/architecture-integration-v1.md",
    "sha256": "29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1",
    "locator": "Cross-contract ownership, precedence, status mapping and dependent company outputs"
   },
   {
    "path": "docs/design/proposal/architecture/initial-profile-v1.md",
    "sha256": "7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb",
    "locator": "Explicit retained scope and later phase obligations"
   }
  ]
 },
 {
  "id": "P15-E02",
  "question": "How does a narrative reading become a constraint?",
  "proposed_answer": "Bind scope, time, modality, exceptions and contexts explicitly; accept translation separately and label added thresholds as assumptions.",
  "alternative": "Free-text scope with generic acceptance and implementation-defined translation.",
  "consequence": "Implementations could turn permissions into payments or fixed coupons into fixed aggregate exposure.",
  "next_step": "Evidence E3 plus L2–L4/I2 require scope, exceptions, contexts and separate translation admission. P17 supplies source-grounded operating/sector predicates and cases; no threshold is inferred from qualitative prose.",
  "blocks_proposal": true,
  "p16_status": "specified_translation_boundary; domain_translations_pending",
  "owning_phase": "P17",
  "disposition_evidence": [
   {
    "path": "docs/design/proposal/architecture/architecture-integration-v1.md",
    "sha256": "29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1",
    "locator": "Cross-contract ownership, precedence, status mapping and dependent company outputs"
   },
   {
    "path": "docs/design/proposal/architecture/initial-profile-v1.md",
    "sha256": "7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb",
    "locator": "Explicit retained scope and later phase obligations"
   }
  ]
 },
 {
  "id": "P15-E03",
  "question": "May source preparation infer a half-unit interval from displayed precision when the rounding rule is unknown?",
  "proposed_answer": "Separate display precision from the issuer rounding convention; retain unknowns and permit a named conditional nearest-rounding compatibility model with explicit assumption provenance.",
  "alternative": "Treat the displayed unit as sufficient evidence for a half-unit interval, or reject all conditional rounding analysis.",
  "consequence": "The first overstates source support; the second prevents useful conditional analysis. Existing P02 and the general contract are not yet aligned on this distinction.",
  "next_step": "Keep precision/convention/tie rules separate in evidence v3/L2. P17 dispositions source-specific P02 assumptions; conditional half-unit intervals stay explicitly assumed until source support exists.",
  "blocks_proposal": true,
  "p16_status": "specified_architecture; source_rounding_obligations_retained",
  "owning_phase": "P17",
  "disposition_evidence": [
   {
    "path": "docs/design/proposal/architecture/architecture-integration-v1.md",
    "sha256": "29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1",
    "locator": "Cross-contract ownership, precedence, status mapping and dependent company outputs"
   },
   {
    "path": "docs/design/proposal/architecture/initial-profile-v1.md",
    "sha256": "7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb",
    "locator": "Explicit retained scope and later phase obligations"
   }
  ]
 },
 {
  "id": "P15-E04",
  "question": "Which missing time/version fields may a query tolerate?",
  "proposed_answer": "Keep exploratory archival results explicitly qualified; reject or return unresolved for system-as-of claims without ingestion evidence and for investor-information evaluation without justified availability and byte vintage.",
  "alternative": "Carry P06 defaults forward: infer ingestion from availability and select unknown-vintage bytes by default.",
  "consequence": "The alternative can produce results labelled as historical knowledge that the retained evidence does not establish.",
  "next_step": "Time v2 and I1/I3/I5 distinguish investor/system/exploratory views and reject unsupported later-information use. Inspect the supplied missing-clock and IX04 exchanges in integrated review.",
  "blocks_proposal": true,
  "p16_status": "specified_pending_integrated_review",
  "owning_phase": "P16",
  "disposition_evidence": [
   {
    "path": "docs/design/proposal/architecture/architecture-integration-v1.md",
    "sha256": "29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1",
    "locator": "Cross-contract ownership, precedence, status mapping and dependent company outputs"
   },
   {
    "path": "docs/design/proposal/architecture/initial-profile-v1.md",
    "sha256": "7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb",
    "locator": "Explicit retained scope and later phase obligations"
   }
  ]
 },
 {
  "id": "P15-E05",
  "question": "What does review acceptance authorise across extraction and interpretation layers?",
  "proposed_answer": "Name the accepted layer, preserve alternatives/conflicts, and propagate status and transitive invalidation through explicit dependencies.",
  "alternative": "One undifferentiated accepted status usable as an accounting constraint.",
  "consequence": "A faithful extraction of a disputed or incorrect assertion could otherwise become an endorsed treatment.",
  "next_step": "Evidence v3/E05 plus P4 specify layer acceptance, alternatives and candidate-set/transitive invalidation. Seven inspected candidates yielded no qualifying real conflict; complete that real-source obligation without inventing one.",
  "blocks_proposal": true,
  "p16_status": "synthetic_semantics_specified; real_conflict_still_missing",
  "history_families_discussion": "H2–H6 and HF01–HF18 specify conditional branches, partial search, capability failures and query-dependent memory without closing this decision; counterpart contracts and independent review remain required.",
  "owning_phase": "P17",
  "disposition_evidence": [
   {
    "path": "docs/design/proposal/architecture/architecture-integration-v1.md",
    "sha256": "29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1",
    "locator": "Cross-contract ownership, precedence, status mapping and dependent company outputs"
   },
   {
    "path": "docs/design/proposal/architecture/initial-profile-v1.md",
    "sha256": "7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb",
    "locator": "Explicit retained scope and later phase obligations"
   }
  ]
 },
 {
  "id": "P15-E06",
  "question": "Which initial profile should be proposed for implementation?",
  "proposed_answer": "Choose connected corporate domain A with authoring variant B from the P15 matched comparison. Exposes operating/financing/history/reporting interactions; keeps banks, insurance, groups/FX and standards method obligations explicit. No cost, speed or usability ranking is claimed.",
  "alternative": "Choose Core 0/Northstar or the instrument prototype because it exists; treat typed-library-first as a smaller accounting domain; or label sectors supported before their methods are specified.",
  "consequence": "Conflating interface and domain scope creates an unfair comparison and can conceal dropped whole-company obligations. All candidates must preserve evidence, joint histories, time, treatment, failure, review/recovery and extension semantics.",
  "next_step": "Review CorporateJointHistory/1 and its separate typed/text choice in initial-profile-v1 against the same Northstar/evidence/task outcomes; all later domain obligations remain.",
  "blocks_proposal": true,
  "p16_status": "proposed_profile_specified_pending_review",
  "owning_phase": "P16",
  "disposition_evidence": [
   {
    "path": "docs/design/proposal/architecture/architecture-integration-v1.md",
    "sha256": "29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1",
    "locator": "Cross-contract ownership, precedence, status mapping and dependent company outputs"
   },
   {
    "path": "docs/design/proposal/architecture/initial-profile-v1.md",
    "sha256": "7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb",
    "locator": "Explicit retained scope and later phase obligations"
   }
  ]
 },
 {
  "id": "P15-E07",
  "question": "What authority is sufficient for cross-standard and sector treatment claims?",
  "proposed_answer": "Admit only dated, locally archived primary passages and company facts within their scope; keep US GAAP/ASBE, bank prudential and broad insurance operations partial until inspected.",
  "alternative": "Treat overview material, company policy or illustrative arithmetic as general authority.",
  "consequence": "Unbounded authority would turn structural examples into unsupported accounting claims.",
  "next_step": "Finish dated corporate/sector/cross-standard method dossiers with actual scope, inspected primary passages, facts, algorithm and matched consequences. Existing retained AASB acquisition is conditional and bounded.",
  "blocks_proposal": true,
  "p16_status": "source_and_method_blocker_open",
  "owning_phase": "P17",
  "disposition_evidence": [
   {
    "path": "docs/design/proposal/architecture/architecture-integration-v1.md",
    "sha256": "29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1",
    "locator": "Cross-contract ownership, precedence, status mapping and dependent company outputs"
   },
   {
    "path": "docs/design/proposal/architecture/initial-profile-v1.md",
    "sha256": "7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb",
    "locator": "Explicit retained scope and later phase obligations"
   }
  ]
 },
 {
  "id": "P15-E08",
  "question": "What evidence is sufficient for an end-to-end proposal readiness claim?",
  "proposed_answer": "Require P15 coverage, P16 contracts, P17 methods, P18 rendered manuscript/build review and P19 independent review, with engineering, accounting, forecast and human states separate.",
  "alternative": "Treat passing structural checks, a compiled PDF or prototype phase acceptances as readiness.",
  "consequence": "Proxy evidence could incorrectly enable implementation or imply accounting validity.",
  "next_step": "Require P15–P18 source/method/manuscript evidence and substantive P19 review. Current structural or arithmetic passes cannot mark the full proposal ready or enable implementation.",
  "blocks_proposal": true,
  "p16_status": "readiness_rule_specified; readiness_not_reached",
  "owning_phase": "P19",
  "disposition_evidence": [
   {
    "path": "docs/design/proposal/architecture/architecture-integration-v1.md",
    "sha256": "29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1",
    "locator": "Cross-contract ownership, precedence, status mapping and dependent company outputs"
   },
   {
    "path": "docs/design/proposal/architecture/initial-profile-v1.md",
    "sha256": "7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb",
    "locator": "Explicit retained scope and later phase obligations"
   }
  ]
 },
 {
  "id": "P15-E09",
  "question": "How should unresolved branches and partial execution appear in outputs?",
  "proposed_answer": "Preserve independent disposition/math/computation/admission fields, domain-native payloads, unresolved regions/mass and commit observation under F1–F4 and I1. No automatic branch dropping, successful-only weighting or default-as-computation-failure.",
  "alternative": "Return successful branches only or collapse unresolved branches into a default.",
  "consequence": "Downstream statements and forecasts would overstate certainty and lose dependence.",
  "next_step": "F1–F4, I3 and uncertainty chaining preserve domain/mass, native statuses and commit uncertainty; review FX01–FX07 and active v2 rejection receipts together.",
  "blocks_proposal": true,
  "p16_status": "specified_pending_integrated_review",
  "history_families_discussion": "H2–H6 and HF01–HF18 specify conditional branches, partial search, capability failures and query-dependent memory without closing this decision; counterpart contracts and independent review remain required.",
  "owning_phase": "P16",
  "disposition_evidence": [
   {
    "path": "docs/design/proposal/architecture/architecture-integration-v1.md",
    "sha256": "29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1",
    "locator": "Cross-contract ownership, precedence, status mapping and dependent company outputs"
   },
   {
    "path": "docs/design/proposal/architecture/initial-profile-v1.md",
    "sha256": "7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb",
    "locator": "Explicit retained scope and later phase obligations"
   }
  ]
 },
 {
  "id": "P15-E10",
  "question": "Which representation defines portable semantics, and which authoring interfaces are initially required?",
  "proposed_answer": "Adopt proposed portable typed record semantics with exact rationals, context/signature/effect checks and explicit legacy mappings; start typed corporate authoring and matched bounded debt text syntax. Frontend equivalence is specified, not measured for the new portable representation.",
  "alternative": "Make host-language state or a text parser the sole semantic authority, or infer correctness from shared-compiler agreement.",
  "consequence": "Portability, source provenance, corrections and migration require meaning independent of one caller; deferring a parser does not remove DSL design or accounting obligations.",
  "next_step": "L1–L5 define typed records, exact rationals, explicit legacy import and matched typed/text debt declarations. Inspect LX01–LX08; no executed new compiler is claimed.",
  "blocks_proposal": true,
  "p16_status": "portable_representation_and_matched_fragment_proposed",
  "owning_phase": "P16",
  "disposition_evidence": [
   {
    "path": "docs/design/proposal/architecture/architecture-integration-v1.md",
    "sha256": "29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1",
    "locator": "Cross-contract ownership, precedence, status mapping and dependent company outputs"
   },
   {
    "path": "docs/design/proposal/architecture/initial-profile-v1.md",
    "sha256": "7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb",
    "locator": "Explicit retained scope and later phase obligations"
   }
  ]
 },
 {
  "id": "P15-E11",
  "question": "Which numerical operations and incomplete outcomes can the initial profile honestly admit?",
  "proposed_answer": "Declare capability by formula/query after expansion, with exact/approximate status, rounding boundaries and typed partial/unsupported replies; retain linear/finite methods as candidate fragments.",
  "alternative": "Force all accounting methods into a linear solver, or promise general nonlinear inference without specified methods.",
  "consequence": "Unsupported sector formulas and resource limits must remain visible rather than producing misleading exact bounds or silent branch loss.",
  "next_step": "Initial affine/finite fragment is explicit after expansion; unsupported, strict endpoints and partial bounds retain their limits. P17 specifies selected sector/nonlinear/inference methods and method-specific numeric comparisons.",
  "blocks_proposal": true,
  "p16_status": "initial_capability_specified; broader_methods_open",
  "history_families_discussion": "H2–H6 and HF01–HF18 specify conditional branches, partial search, capability failures and query-dependent memory without closing this decision; counterpart contracts and independent review remain required.",
  "owning_phase": "P17",
  "disposition_evidence": [
   {
    "path": "docs/design/proposal/architecture/architecture-integration-v1.md",
    "sha256": "29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1",
    "locator": "Cross-contract ownership, precedence, status mapping and dependent company outputs"
   },
   {
    "path": "docs/design/proposal/architecture/initial-profile-v1.md",
    "sha256": "7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb",
    "locator": "Explicit retained scope and later phase obligations"
   }
  ]
 },
 {
  "id": "P15-E12",
  "question": "What entity and economic memory must survive aggregation and extension?",
  "proposed_answer": "Retain legal entity, evidence-backed control, perimeter versions and query-relevant contract/lot/cohort state with explicit refinement and invalidation.",
  "alternative": "Store aggregate account totals and assume omitted rights, timing and dependencies can be recovered later.",
  "consequence": "Histories with identical totals may have different scenario responses; a narrow initial schema could make later sector support impossible without semantic migration.",
  "next_step": "History H1–H7, I4 and integration define query-scoped memory and safe/unsafe grouping. P17 owes concrete group perimeter, banking/insurance and cross-standard state transitions/cases.",
  "blocks_proposal": true,
  "p16_status": "structural_memory_specified; domain_transitions_open",
  "history_families_discussion": "H2–H6 and HF01–HF18 specify conditional branches, partial search, capability failures and query-dependent memory without closing this decision; counterpart contracts and independent review remain required.",
  "owning_phase": "P17",
  "disposition_evidence": [
   {
    "path": "docs/design/proposal/architecture/architecture-integration-v1.md",
    "sha256": "29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1",
    "locator": "Cross-contract ownership, precedence, status mapping and dependent company outputs"
   },
   {
    "path": "docs/design/proposal/architecture/initial-profile-v1.md",
    "sha256": "7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb",
    "locator": "Explicit retained scope and later phase obligations"
   }
  ]
 },
 {
  "id": "P15-E13",
  "question": "What scenario and probability claims belong in the initial profile?",
  "proposed_answer": "Specify transparent conditional scenarios and optional justified joint measures; preserve unweighted alternatives, information cutoffs, dependence and unresolved mass.",
  "alternative": "Require probabilistic company forecasts by default or normalise successful branches alone.",
  "consequence": "Conditional stress is useful without calibrated probabilities; unsupported weighting would misstate evidence and can introduce look-ahead.",
  "next_step": "I3/F3 and uncertainty admission/chaining specify conditional stress and finite joint measures without branch-count weights or leakage. P17 owes continuous/causal/calibration methods and empirical evidence plan.",
  "blocks_proposal": true,
  "p16_status": "initial_exogenous_and_optional_finite_law_specified; inference_open",
  "history_families_discussion": "H2–H6 and HF01–HF18 specify conditional branches, partial search, capability failures and query-dependent memory without closing this decision; counterpart contracts and independent review remain required.",
  "owning_phase": "P17",
  "disposition_evidence": [
   {
    "path": "docs/design/proposal/architecture/architecture-integration-v1.md",
    "sha256": "29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1",
    "locator": "Cross-contract ownership, precedence, status mapping and dependent company outputs"
   },
   {
    "path": "docs/design/proposal/architecture/initial-profile-v1.md",
    "sha256": "7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb",
    "locator": "Explicit retained scope and later phase obligations"
   }
  ]
 },
 {
  "id": "P15-E14",
  "question": "Which reusable components may supply which financial operations?",
  "proposed_answer": "Separate evidence import, contract scheduling, valuation, accounting rule application and ledger exchange; propose pinned adapters with explicit retained fields and failures.",
  "alternative": "Let an upstream schedule/valuation/ledger engine decide accounting treatment, or defer interface analysis until implementation.",
  "consequence": "Tool presence or a plausible exchange format cannot establish semantic compatibility; P11 completed zero external integrations.",
  "next_step": "I4 and extraction-v1 separate extraction, schedule, valuation, treatment and ledger effects. P17 must inspect pinned official APIs/licences and matched/adverse mappings; P11 did not complete external integrations.",
  "blocks_proposal": true,
  "p16_status": "adapter_boundaries_specified; official_interface_evidence_open",
  "owning_phase": "P17",
  "disposition_evidence": [
   {
    "path": "docs/design/proposal/architecture/architecture-integration-v1.md",
    "sha256": "29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1",
    "locator": "Cross-contract ownership, precedence, status mapping and dependent company outputs"
   },
   {
    "path": "docs/design/proposal/architecture/initial-profile-v1.md",
    "sha256": "7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb",
    "locator": "Explicit retained scope and later phase obligations"
   }
  ]
 }
]