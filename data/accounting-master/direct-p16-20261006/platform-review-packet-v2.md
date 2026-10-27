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
REVIEW SCOPE CLARIFICATION: Review architecture semantics and the included representative complete exchanges substantively. The 27-exchange and V01–V16 diagnostics have finite coverage; do not assert every supplied field was independently reviewed. Read, Glob and Grep tools are available for additional inspection of the exact files listed below; Bash/edit/network/agents are prohibited. The packet-only probe identified missing data. This appendix repairs it; final review may inspect cited original files if needed.

ACTUAL COMPLETE ACCOUNTING SAMPLES (JSON; immutable saved values):
{"exchanges":[{"id":"X002","control":{"file":{"path":"docs/design/proposal/architecture/accounting-integration-fixtures-v2.json","sha256":"234f7e7b31258d9fb3003d617d6b5591c4364c7e1ed4fdb74958524b95ba9acf"},"case_id":"I01"},"field_control":"F002","source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X002"},"mutations":[{"op":"replace","path":"source/C09/unknown_reason","before":null,"after":null},{"op":"replace","path":"source/C09/value/unknown_reason","before":"not applicable while price equals fair value","after":null}],"raw_request":"{\"admissions\":[\"00df3966fc62c6ce957bbe9385687d7c310ae58c17f8a3fef8a8a06e9cd8be85\"],\"assumptions\":\"55fa6518f2380495f24c0639b6ec39d6a0335497ff4b3a67cc9b8fbbcf6c731b\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"61ec1363be0c50e93c4f76d8db60224a12ef5e160f2ab51521086cacb360b8d5\",\"event\":\"e9a7c404613183ccd62033d0ccd47fd315970afde5d798671c83e5419dd2b975\",\"evidence\":[\"6afbdda56ec107aaf0e6ff6cccae9650fb3f755202a30c8000833c7f85cf508d\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E01\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}","request":"89a74768f1124b2ecb5c6a21c508a233451b0f9c63b49365badf59644644a49a","submission":"a5a3bd557cbb7a994119bd55795b76c8bba17c658bc3a46630901086d13bc5a2","required_record_closure":["00df3966fc62c6ce957bbe9385687d7c310ae58c17f8a3fef8a8a06e9cd8be85","0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","55fa6518f2380495f24c0639b6ec39d6a0335497ff4b3a67cc9b8fbbcf6c731b","61ec1363be0c50e93c4f76d8db60224a12ef5e160f2ab51521086cacb360b8d5","6afbdda56ec107aaf0e6ff6cccae9650fb3f755202a30c8000833c7f85cf508d","7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","e9a7c404613183ccd62033d0ccd47fd315970afde5d798671c83e5419dd2b975","fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0"],"assessment":"92831f62195c24559d01cff17206e1716db033eb95ed1974bdf43553290992c2","response":"8b39f2b5526db38e938b6cf80e3ff5fe20e42c5c27dcc477b633c70b2becdedd","expected_diagnostics":[],"lookup":true,"freshness":true,"assess":true,"before":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"after":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]}},{"id":"X007","control":{"file":{"path":"docs/design/proposal/architecture/accounting-integration-fixtures-v2.json","sha256":"234f7e7b31258d9fb3003d617d6b5591c4364c7e1ed4fdb74958524b95ba9acf"},"case_id":"I06"},"field_control":"F007","source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X007"},"mutations":[{"op":"replace","path":"source/C09/unknown_reason","before":"neither route assessed","after":"outer: route evidence absent"},{"op":"replace","path":"source/C09/value/unknown_reason","before":"neither qualifying valuation route evidenced","after":"inner: valuation input unresolved"}],"raw_request":"{\"admissions\":[\"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c\"],\"assumptions\":\"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"6298680567179a51f9610908611ac8a03af8e8ce6dbcedbcb10932950027237c\",\"event\":\"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f\",\"evidence\":[\"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E06\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}","request":"9d57a2b3eaae5c02eac0d11597f9494483c79e3e43f9db83b06ff6ffc72530b1","submission":"f6c80db388b4bbf5dae424ee449e2b31f706f0c8135578a0f9d294c7ede03059","required_record_closure":["0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c","48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","6298680567179a51f9610908611ac8a03af8e8ce6dbcedbcb10932950027237c","7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f","e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028","fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0"],"assessment":"3e71df06c1f530037f53937018977b28a27ba1f04bde42f2f8b5025cfc224035","response":"c49976ea1709a278bfbee3b22cf87a07aad2f0b644adf8845fe3aa1f1d20a377","expected_diagnostics":[],"lookup":true,"freshness":true,"assess":true,"before":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"after":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]}},{"id":"X008","control":{"file":{"path":"docs/design/proposal/architecture/accounting-integration-fixtures-v2.json","sha256":"234f7e7b31258d9fb3003d617d6b5591c4364c7e1ed4fdb74958524b95ba9acf"},"case_id":"I06"},"field_control":"F008","source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X008"},"mutations":[{"op":"replace","path":"source/C09/unknown_reason","before":"neither route assessed","after":null}],"raw_request":"{\"admissions\":[\"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c\"],\"assumptions\":\"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"ff6025ba31f7d4d28bbd04046edb5ec51b05073fd070cc7606140c566bf67a2a\",\"event\":\"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f\",\"evidence\":[\"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E06\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}","request":"7a7cd0039ad37aa1cc98602ff1e229d68344bbe169dacdf1f2ebd5e9a72269aa","submission":"2890f182341d858eb68c26d8ff06c876e99279a852b21039a1dcc225cf2dc3fb","required_record_closure":["0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c","48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f","e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028","fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","ff6025ba31f7d4d28bbd04046edb5ec51b05073fd070cc7606140c566bf67a2a"],"assessment":null,"response":"060e574b32947b7f26902561f397f5d2c25127ad6f9cdd797da0044dc6244c04","expected_diagnostics":[{"stage":"shape","path":"source/C09/unknown_reason","code":"INVALID_UNKNOWN_REPRESENTATION"}],"lookup":false,"freshness":false,"assess":false,"before":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"after":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]}},{"id":"X188","control":{"file":{"path":"docs/design/proposal/architecture/accounting-integration-fixtures-v2.json","sha256":"234f7e7b31258d9fb3003d617d6b5591c4364c7e1ed4fdb74958524b95ba9acf"},"case_id":"I06"},"field_control":"F188","source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X188"},"mutations":[{"op":"remove","path":"source/C09/value/required","before":true},{"op":"replace","path":"source/C09/unknown_reason","before":"neither route assessed","after":null},{"op":"replace","path":"source/C09/value/unknown_reason","before":"neither qualifying valuation route evidenced","after":null}],"raw_request":"{\"admissions\":[\"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c\"],\"assumptions\":\"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"99bac9fb82a55ae3bf65c7a7eff6799bcbd241f8d543a84822b91dd42f0445b3\",\"event\":\"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f\",\"evidence\":[\"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E06\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}","request":"bfabaf4c687fd9bf6f30f0c07173038c82e7ec8ad2404252829078bf0134534f","submission":"64d20a86908b0321a6b1ca7dfd8ed4d498cd76eadaca07deeecdd46357a0db7f","required_record_closure":["0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c","48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","99bac9fb82a55ae3bf65c7a7eff6799bcbd241f8d543a84822b91dd42f0445b3","abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f","e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028","fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0"],"assessment":null,"response":"b1eb35dd439443566fcfc39645094d9cd3219a86cecf1f887c573e9bf668e35f","expected_diagnostics":[{"stage":"shape","path":"source/C09/value/required","code":"INVALID_CONDITION_PACKET"}],"lookup":false,"freshness":false,"assess":false,"before":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"after":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]}},{"id":"X202","control":{"file":{"path":"docs/design/proposal/architecture/accounting-integration-fixtures-v2.json","sha256":"234f7e7b31258d9fb3003d617d6b5591c4364c7e1ed4fdb74958524b95ba9acf"},"case_id":"I06"},"field_control":"F202","source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X202"},"mutations":[{"op":"remove","path":"source/C09/value/identical_instrument_active_market_quote","before":null},{"op":"replace","path":"source/C09/unknown_reason","before":"neither route assessed","after":null},{"op":"replace","path":"source/C09/value/unknown_reason","before":"neither qualifying valuation route evidenced","after":null}],"raw_request":"{\"admissions\":[\"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c\"],\"assumptions\":\"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"da38ce395c7aeb3142d684c9b98fe71f740d25d84be89b8c60708b9212b6defd\",\"event\":\"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f\",\"evidence\":[\"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E06\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}","request":"6f080d929801cd86f5e0585870d1747fdeb3139639dea72c9703d31e2973ca41","submission":"80b9409ba45c57e8781beaf730ddf1df16144d10ec784c654446ad7183ff81d6","required_record_closure":["0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c","48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","da38ce395c7aeb3142d684c9b98fe71f740d25d84be89b8c60708b9212b6defd","e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f","e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028","fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0"],"assessment":null,"response":"bdd2f33d7a16aff19536f566c05ae8670f7e8923e210ffe9c77852d974b599e4","expected_diagnostics":[{"stage":"shape","path":"source/C09/unknown_reason","code":"INVALID_UNKNOWN_REPRESENTATION"},{"stage":"shape","path":"source/C09/value/identical_instrument_active_market_quote","code":"INVALID_CONDITION_PACKET"},{"stage":"shape","path":"source/C09/value/unknown_reason","code":"INVALID_UNKNOWN_REPRESENTATION"}],"lookup":false,"freshness":false,"assess":false,"before":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"after":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]}},{"id":"X241","control":{"file":{"path":"docs/design/proposal/architecture/accounting-integration-fixtures-v2.json","sha256":"234f7e7b31258d9fb3003d617d6b5591c4364c7e1ed4fdb74958524b95ba9acf"},"case_id":"I06"},"field_control":"F241","source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X241"},"mutations":[{"op":"replace","path":"source/C09/value","before":{"required":true,"identical_instrument_active_market_quote":null,"technique_only_observable_market_data":null,"unknown_reason":"neither qualifying valuation route evidenced","branch":"unknown"},"after":[]},{"op":"replace","path":"source/C09/unknown_reason","before":"neither route assessed","after":""},{"op":"replace","path":"source/C10/unknown_reason","before":null,"after":false}],"raw_request":"{\"admissions\":[\"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c\"],\"assumptions\":\"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"7a1a57da0f291f32b21aa9638f351e615960567859b74c2a1e68565af47fdde0\",\"event\":\"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f\",\"evidence\":[\"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E06\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}","request":"a85ec29dd5420f2d0d5a8995bab5a0cb633c0f2da8475205d1ab4d2c0f358512","submission":"0c785e643f317aa6c2a0c0d567431f33cca6db84940b017327a206e7015ed898","required_record_closure":["0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c","48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","7a1a57da0f291f32b21aa9638f351e615960567859b74c2a1e68565af47fdde0","abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f","e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028","fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0"],"assessment":null,"response":"5c6e6124b0116f7f6d8f46e4f0cfb58cf99e1666e60275903035875b965e025b","expected_diagnostics":[{"stage":"shape","path":"source/C09/unknown_reason","code":"INVALID_UNKNOWN_REPRESENTATION"},{"stage":"shape","path":"source/C09/value","code":"INVALID_FIELD_TYPE"},{"stage":"shape","path":"source/C10/unknown_reason","code":"INVALID_FIELD_TYPE"}],"lookup":false,"freshness":false,"assess":false,"before":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"after":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]}},{"id":"K01","control":{"file":{"path":"docs/design/proposal/architecture/accounting-integration-fixtures-v2.json","sha256":"234f7e7b31258d9fb3003d617d6b5591c4364c7e1ed4fdb74958524b95ba9acf"},"case_id":"I06"},"field_control":null,"source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K01"},"mutations":[{"op":"replace","path":"source/C09/value/required","before":true,"after":false}],"raw_request":"{\"admissions\":[\"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c\"],\"assumptions\":\"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"f6794fa664d2bdb039761d8db47a39b2675b465184fec864831f67de3ff7d5fb\",\"event\":\"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f\",\"evidence\":[\"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E06\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}","request":"a0fe3d57e8f51f9200a569d5ae657ec46087ec30735ce2e78f22861c8ec04713","submission":"c1c98853cc8192823fe353068c70d760328faa4834c0404e02c4065148c08719","required_record_closure":["0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c","48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f","e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028","f6794fa664d2bdb039761d8db47a39b2675b465184fec864831f67de3ff7d5fb","fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0"],"assessment":null,"response":"6b0307d2362ab1ae6cce8efd0b7352190055f42b81ff825ecce5078ddb47cbb0","expected_diagnostics":[{"stage":"bindings","path":"source/C09/value/required","code":"SOURCE_CONTEXT_MISMATCH"}],"lookup":false,"freshness":false,"assess":false,"before":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"after":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]}},{"id":"K04","control":{"file":{"path":"docs/design/proposal/architecture/accounting-integration-fixtures-v2.json","sha256":"234f7e7b31258d9fb3003d617d6b5591c4364c7e1ed4fdb74958524b95ba9acf"},"case_id":"I06"},"field_control":null,"source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K04"},"mutations":[{"op":"replace","path":"source/C10/value/unequal_price_a_method_available","before":false,"after":true}],"raw_request":"{\"admissions\":[\"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c\"],\"assumptions\":\"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"009ab9863371a17fa943eaa3a46a3b80a15e754c4e95202e2d02ece3a1b6b6ff\",\"event\":\"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f\",\"evidence\":[\"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E06\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}","request":"111c9e1e08996d9e1d3a67d467d725417a5eecf3436ac2839abb8219f4515078","submission":"c21fc6ae5892c5cb088cc6eb290bf7821a4b4841e8fa847d62e5682f97787810","required_record_closure":["009ab9863371a17fa943eaa3a46a3b80a15e754c4e95202e2d02ece3a1b6b6ff","0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c","48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f","e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028","fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0"],"assessment":null,"response":"3c25987b9a7a1a5afbd4daaf2c64b96504241b13632e804a09b68eefb6855f57","expected_diagnostics":[{"stage":"bindings","path":"source/C10/value/unequal_price_a_method_available","code":"METHOD_CAPABILITY_MISMATCH"}],"lookup":false,"freshness":false,"assess":false,"before":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"after":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]}}],"source_cases":[{"id":"X002","complete_inputs":{"C01":{"value":{"entity":"synthetic purchaser","reporting_basis":"AASB, for-profit Tier 1 stipulated","source":"S9 Compilation 5","annual_period_start":"2024-01-01","within_retained_window":true,"applicability":"stipulated; not an actual entity assessment"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"cover p1; comparison p6"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C02":{"value":{"holder_financial_asset":true,"instrument":"synthetic debt security","scope_exceptions":"none stipulated; no subsidiary/group, lease, benefit, issuer-equity, insurance, combination-forward, commitment, share-payment, reimbursement or revenue-contract feature","transfer_derecognition_obstacle":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"2.1 pp8–9; B3.1.1 p49"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C03":{"value":{"party_to_contract":true,"contractual_date":"2024-06-03","contract_evidence":"synthetic binding purchase agreement; not historical evidence"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.1 p10"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C04":{"value":{"trade_date":"2024-06-03","settlement_date":"2024-06-03","recognition_date":"2024-06-03","regular_way":true,"delivery_terms":"delivery on same date within stipulated market convention","net_settlement_permitted":false,"policy":"trade date; stipulated consistent for mandatory FVTPL classification","date_eligible_under_policy_if_contractual_condition_holds":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.2 p10; B3.1.3–B3.1.6 pp49–50"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C05":{"value":{"category":"FVTPL","instrument_kind":"debt","business_model":"held for trading; neither hold-to-collect nor collect-and-sell objective, stipulated","cash_flows":"fixed principal and coupon, stipulated; no completed SPPI analysis","route":"mandatory residual 4.1.4, stipulated upstream assessment","designation":false,"equity_OCI_election":"not applicable to stipulated debt","rationale_available":true,"rationale_status":"synthetic assumption; detailed B4.1 guidance not reviewed"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"4.1.1–4.1.5 pp15–16; detailed guidance uninspected"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C06":{"value":{"price":"100","fair_value":"100","valuation_date":"2024-06-03","fair_value_basis":"transaction price stipulated representative under B5.1.1; no independent valuation","other_consideration_component":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1–5.1.3 p18; B5.1.1 p74"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C07":{"value":{"amount":"2","payee":"synthetic third-party broker","purpose":"execution of acquisition","incremental":true,"directly_attributable":true,"would_incur_without_acquisition":false,"financing_or_internal_admin_or_holding_cost":false,"invoice":"stipulated invoice, separately paid","service_completed":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"Appendix A p47; B5.4.8 p77"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C08":{"value":{"settlement":"cash","entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission","currency":"CU","unit":"units","scale":0,"separate_tax_treatment":false,"FX":false,"other_asset_treatment":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method scope; not a universal source rule"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C09":{"value":{"required":false,"identical_instrument_active_market_quote":null,"technique_only_observable_market_data":null,"unknown_reason":null,"branch":"not_applicable"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1A p18; B5.1.2A pp74–75"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C10":{"value":{"method":"conditional equal-price FVTPL acquisition example v1","unequal_price_a_method_available":false,"unequal_price_b_method_available":false},"unknown_reason":null,"provenance":{"kind":"specified_method_limit","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method limitation"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"}},"comparator":{"file":{"path":"docs/design/proposal/architecture/accounting-eligibility-fixtures-v1.json","sha256":"8d61ecfe4005d4652ead2f8a06d74b0340f4735ae83066fec7c19b0ab104c6f3"},"case_id":"E01"},"mutations":[{"op":"replace","path":"source/C09/unknown_reason","before":null,"after":null},{"op":"replace","path":"source/C09/value/unknown_reason","before":"not applicable while price equals fair value","after":null}]},{"id":"E01","retained_example":"A01","variation":"conditional control","primary_changed_condition":null,"comparison_base":"E01","complete_inputs":{"C01":{"value":{"entity":"synthetic purchaser","reporting_basis":"AASB, for-profit Tier 1 stipulated","source":"S9 Compilation 5","annual_period_start":"2024-01-01","within_retained_window":true,"applicability":"stipulated; not an actual entity assessment"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"cover p1; comparison p6"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C02":{"value":{"holder_financial_asset":true,"instrument":"synthetic debt security","scope_exceptions":"none stipulated; no subsidiary/group, lease, benefit, issuer-equity, insurance, combination-forward, commitment, share-payment, reimbursement or revenue-contract feature","transfer_derecognition_obstacle":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"2.1 pp8–9; B3.1.1 p49"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C03":{"value":{"party_to_contract":true,"contractual_date":"2024-06-03","contract_evidence":"synthetic binding purchase agreement; not historical evidence"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.1 p10"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C04":{"value":{"trade_date":"2024-06-03","settlement_date":"2024-06-03","recognition_date":"2024-06-03","regular_way":true,"delivery_terms":"delivery on same date within stipulated market convention","net_settlement_permitted":false,"policy":"trade date; stipulated consistent for mandatory FVTPL classification","date_eligible_under_policy_if_contractual_condition_holds":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.2 p10; B3.1.3–B3.1.6 pp49–50"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C05":{"value":{"category":"FVTPL","instrument_kind":"debt","business_model":"held for trading; neither hold-to-collect nor collect-and-sell objective, stipulated","cash_flows":"fixed principal and coupon, stipulated; no completed SPPI analysis","route":"mandatory residual 4.1.4, stipulated upstream assessment","designation":false,"equity_OCI_election":"not applicable to stipulated debt","rationale_available":true,"rationale_status":"synthetic assumption; detailed B4.1 guidance not reviewed"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"4.1.1–4.1.5 pp15–16; detailed guidance uninspected"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C06":{"value":{"price":"100","fair_value":"100","valuation_date":"2024-06-03","fair_value_basis":"transaction price stipulated representative under B5.1.1; no independent valuation","other_consideration_component":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1–5.1.3 p18; B5.1.1 p74"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C07":{"value":{"amount":"2","payee":"synthetic third-party broker","purpose":"execution of acquisition","incremental":true,"directly_attributable":true,"would_incur_without_acquisition":false,"financing_or_internal_admin_or_holding_cost":false,"invoice":"stipulated invoice, separately paid","service_completed":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"Appendix A p47; B5.4.8 p77"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C08":{"value":{"settlement":"cash","entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission","currency":"CU","unit":"units","scale":0,"separate_tax_treatment":false,"FX":false,"other_asset_treatment":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method scope; not a universal source rule"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C09":{"value":{"required":false,"identical_instrument_active_market_quote":null,"technique_only_observable_market_data":null,"unknown_reason":"not applicable while price equals fair value","branch":"not_applicable"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1A p18; B5.1.2A pp74–75"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C10":{"value":{"method":"conditional equal-price FVTPL acquisition example v1","unequal_price_a_method_available":false,"unequal_price_b_method_available":false},"unknown_reason":null,"provenance":{"kind":"specified_method_limit","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method limitation"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"}},"condition_findings":[{"condition":"C01","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C02","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C03","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C04","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C05","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C06","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C07","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C08","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C09","status":"not_applicable","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C10","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"}],"expected_assessment":{"status":"eligible","evidence_level":"conditional_synthetic_only","reasons":{},"valuation_branch":"not_applicable","journal_proposal":[["asset","100","0"],["expense","2","0"],["cash","0","102"]],"state_delta":null,"posting_permitted":false},"limited_screen_input":{"category":"FVTPL","candidate_journal":[["asset","100","0"],["expense","2","0"],["cash","0","102"]],"role":"constructed diagnostic arithmetic only; unequal-price gain is not an endorsed posting"},"expected_limited_screen":"pass","no_mutation":{"posted_journals":"unchanged","account_state":"unchanged","event_identity_map":"unchanged","committed_receipts":"unchanged"}},{"id":"X007","complete_inputs":{"C01":{"value":{"entity":"synthetic purchaser","reporting_basis":"AASB, for-profit Tier 1 stipulated","source":"S9 Compilation 5","annual_period_start":"2024-01-01","within_retained_window":true,"applicability":"stipulated; not an actual entity assessment"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"cover p1; comparison p6"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C02":{"value":{"holder_financial_asset":true,"instrument":"synthetic debt security","scope_exceptions":"none stipulated; no subsidiary/group, lease, benefit, issuer-equity, insurance, combination-forward, commitment, share-payment, reimbursement or revenue-contract feature","transfer_derecognition_obstacle":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"2.1 pp8–9; B3.1.1 p49"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C03":{"value":{"party_to_contract":true,"contractual_date":"2024-06-03","contract_evidence":"synthetic binding purchase agreement; not historical evidence"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.1 p10"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C04":{"value":{"trade_date":"2024-06-03","settlement_date":"2024-06-03","recognition_date":"2024-06-03","regular_way":true,"delivery_terms":"delivery on same date within stipulated market convention","net_settlement_permitted":false,"policy":"trade date; stipulated consistent for mandatory FVTPL classification","date_eligible_under_policy_if_contractual_condition_holds":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.2 p10; B3.1.3–B3.1.6 pp49–50"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C05":{"value":{"category":"FVTPL","instrument_kind":"debt","business_model":"held for trading; neither hold-to-collect nor collect-and-sell objective, stipulated","cash_flows":"fixed principal and coupon, stipulated; no completed SPPI analysis","route":"mandatory residual 4.1.4, stipulated upstream assessment","designation":false,"equity_OCI_election":"not applicable to stipulated debt","rationale_available":true,"rationale_status":"synthetic assumption; detailed B4.1 guidance not reviewed"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"4.1.1–4.1.5 pp15–16; detailed guidance uninspected"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C06":{"value":{"price":"100","fair_value":"105","valuation_date":"2024-06-03","fair_value_basis":"105 is a supplied synthetic estimate; its evidence quality is assessed by C09","other_consideration_component":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1–5.1.3 p18; B5.1.1 p74"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C07":{"value":{"amount":"2","payee":"synthetic third-party broker","purpose":"execution of acquisition","incremental":true,"directly_attributable":true,"would_incur_without_acquisition":false,"financing_or_internal_admin_or_holding_cost":false,"invoice":"stipulated invoice, separately paid","service_completed":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"Appendix A p47; B5.4.8 p77"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C08":{"value":{"settlement":"cash","entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission","currency":"CU","unit":"units","scale":0,"separate_tax_treatment":false,"FX":false,"other_asset_treatment":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method scope; not a universal source rule"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C09":{"value":{"required":true,"identical_instrument_active_market_quote":null,"technique_only_observable_market_data":null,"unknown_reason":"inner: valuation input unresolved","branch":"unknown"},"unknown_reason":"outer: route evidence absent","provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1A p18; B5.1.2A pp74–75"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C10":{"value":{"method":"pending branch decision","unequal_price_a_method_available":false,"unequal_price_b_method_available":false},"unknown_reason":null,"provenance":{"kind":"specified_method_limit","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method limitation"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"}},"comparator":{"file":{"path":"docs/design/proposal/architecture/accounting-eligibility-fixtures-v1.json","sha256":"8d61ecfe4005d4652ead2f8a06d74b0340f4735ae83066fec7c19b0ab104c6f3"},"case_id":"E06"},"mutations":[{"op":"replace","path":"source/C09/unknown_reason","before":"neither route assessed","after":"outer: route evidence absent"},{"op":"replace","path":"source/C09/value/unknown_reason","before":"neither qualifying valuation route evidenced","after":"inner: valuation input unresolved"}]},{"id":"E06","retained_example":"A03","variation":"unequal price; valuation routes unknown","primary_changed_condition":"C09","comparison_base":"E06","complete_inputs":{"C01":{"value":{"entity":"synthetic purchaser","reporting_basis":"AASB, for-profit Tier 1 stipulated","source":"S9 Compilation 5","annual_period_start":"2024-01-01","within_retained_window":true,"applicability":"stipulated; not an actual entity assessment"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"cover p1; comparison p6"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C02":{"value":{"holder_financial_asset":true,"instrument":"synthetic debt security","scope_exceptions":"none stipulated; no subsidiary/group, lease, benefit, issuer-equity, insurance, combination-forward, commitment, share-payment, reimbursement or revenue-contract feature","transfer_derecognition_obstacle":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"2.1 pp8–9; B3.1.1 p49"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C03":{"value":{"party_to_contract":true,"contractual_date":"2024-06-03","contract_evidence":"synthetic binding purchase agreement; not historical evidence"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.1 p10"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C04":{"value":{"trade_date":"2024-06-03","settlement_date":"2024-06-03","recognition_date":"2024-06-03","regular_way":true,"delivery_terms":"delivery on same date within stipulated market convention","net_settlement_permitted":false,"policy":"trade date; stipulated consistent for mandatory FVTPL classification","date_eligible_under_policy_if_contractual_condition_holds":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.2 p10; B3.1.3–B3.1.6 pp49–50"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C05":{"value":{"category":"FVTPL","instrument_kind":"debt","business_model":"held for trading; neither hold-to-collect nor collect-and-sell objective, stipulated","cash_flows":"fixed principal and coupon, stipulated; no completed SPPI analysis","route":"mandatory residual 4.1.4, stipulated upstream assessment","designation":false,"equity_OCI_election":"not applicable to stipulated debt","rationale_available":true,"rationale_status":"synthetic assumption; detailed B4.1 guidance not reviewed"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"4.1.1–4.1.5 pp15–16; detailed guidance uninspected"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C06":{"value":{"price":"100","fair_value":"105","valuation_date":"2024-06-03","fair_value_basis":"105 is a supplied synthetic estimate; its evidence quality is assessed by C09","other_consideration_component":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1–5.1.3 p18; B5.1.1 p74"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C07":{"value":{"amount":"2","payee":"synthetic third-party broker","purpose":"execution of acquisition","incremental":true,"directly_attributable":true,"would_incur_without_acquisition":false,"financing_or_internal_admin_or_holding_cost":false,"invoice":"stipulated invoice, separately paid","service_completed":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"Appendix A p47; B5.4.8 p77"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C08":{"value":{"settlement":"cash","entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission","currency":"CU","unit":"units","scale":0,"separate_tax_treatment":false,"FX":false,"other_asset_treatment":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method scope; not a universal source rule"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C09":{"value":{"required":true,"identical_instrument_active_market_quote":null,"technique_only_observable_market_data":null,"unknown_reason":"neither qualifying valuation route evidenced","branch":"unknown"},"unknown_reason":"neither route assessed","provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1A p18; B5.1.2A pp74–75"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C10":{"value":{"method":"pending branch decision","unequal_price_a_method_available":false,"unequal_price_b_method_available":false},"unknown_reason":null,"provenance":{"kind":"specified_method_limit","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method limitation"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"}},"condition_findings":[{"condition":"C01","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C02","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C03","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C04","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C05","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C06","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C07","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C08","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C09","status":"unresolved","reason":"unequal price; valuation routes unknown"},{"condition":"C10","status":"unresolved","reason":"branch evidence missing; method decision pending"}],"expected_assessment":{"status":"unresolved","evidence_level":"conditional_synthetic_only","reasons":{"C09":"unequal price; valuation routes unknown","C10":"branch evidence missing; method decision pending"},"valuation_branch":"unknown","journal_proposal":null,"state_delta":null,"posting_permitted":false},"limited_screen_input":{"category":"FVTPL","candidate_journal":[["asset","105","0"],["expense","2","0"],["cash","0","102"],["hypothetical_gain","0","5"]],"role":"constructed diagnostic arithmetic only; unequal-price gain is not an endorsed posting"},"expected_limited_screen":"pass","no_mutation":{"posted_journals":"unchanged","account_state":"unchanged","event_identity_map":"unchanged","committed_receipts":"unchanged"}},{"id":"X008","complete_inputs":{"C01":{"value":{"entity":"synthetic purchaser","reporting_basis":"AASB, for-profit Tier 1 stipulated","source":"S9 Compilation 5","annual_period_start":"2024-01-01","within_retained_window":true,"applicability":"stipulated; not an actual entity assessment"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"cover p1; comparison p6"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C02":{"value":{"holder_financial_asset":true,"instrument":"synthetic debt security","scope_exceptions":"none stipulated; no subsidiary/group, lease, benefit, issuer-equity, insurance, combination-forward, commitment, share-payment, reimbursement or revenue-contract feature","transfer_derecognition_obstacle":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"2.1 pp8–9; B3.1.1 p49"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C03":{"value":{"party_to_contract":true,"contractual_date":"2024-06-03","contract_evidence":"synthetic binding purchase agreement; not historical evidence"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.1 p10"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C04":{"value":{"trade_date":"2024-06-03","settlement_date":"2024-06-03","recognition_date":"2024-06-03","regular_way":true,"delivery_terms":"delivery on same date within stipulated market convention","net_settlement_permitted":false,"policy":"trade date; stipulated consistent for mandatory FVTPL classification","date_eligible_under_policy_if_contractual_condition_holds":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.2 p10; B3.1.3–B3.1.6 pp49–50"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C05":{"value":{"category":"FVTPL","instrument_kind":"debt","business_model":"held for trading; neither hold-to-collect nor collect-and-sell objective, stipulated","cash_flows":"fixed principal and coupon, stipulated; no completed SPPI analysis","route":"mandatory residual 4.1.4, stipulated upstream assessment","designation":false,"equity_OCI_election":"not applicable to stipulated debt","rationale_available":true,"rationale_status":"synthetic assumption; detailed B4.1 guidance not reviewed"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"4.1.1–4.1.5 pp15–16; detailed guidance uninspected"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C06":{"value":{"price":"100","fair_value":"105","valuation_date":"2024-06-03","fair_value_basis":"105 is a supplied synthetic estimate; its evidence quality is assessed by C09","other_consideration_component":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1–5.1.3 p18; B5.1.1 p74"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C07":{"value":{"amount":"2","payee":"synthetic third-party broker","purpose":"execution of acquisition","incremental":true,"directly_attributable":true,"would_incur_without_acquisition":false,"financing_or_internal_admin_or_holding_cost":false,"invoice":"stipulated invoice, separately paid","service_completed":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"Appendix A p47; B5.4.8 p77"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C08":{"value":{"settlement":"cash","entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission","currency":"CU","unit":"units","scale":0,"separate_tax_treatment":false,"FX":false,"other_asset_treatment":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method scope; not a universal source rule"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C09":{"value":{"required":true,"identical_instrument_active_market_quote":null,"technique_only_observable_market_data":null,"unknown_reason":"neither qualifying valuation route evidenced","branch":"unknown"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1A p18; B5.1.2A pp74–75"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C10":{"value":{"method":"pending branch decision","unequal_price_a_method_available":false,"unequal_price_b_method_available":false},"unknown_reason":null,"provenance":{"kind":"specified_method_limit","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method limitation"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"}},"comparator":{"file":{"path":"docs/design/proposal/architecture/accounting-eligibility-fixtures-v1.json","sha256":"8d61ecfe4005d4652ead2f8a06d74b0340f4735ae83066fec7c19b0ab104c6f3"},"case_id":"E06"},"mutations":[{"op":"replace","path":"source/C09/unknown_reason","before":"neither route assessed","after":null}]},{"id":"X188","complete_inputs":{"C01":{"value":{"entity":"synthetic purchaser","reporting_basis":"AASB, for-profit Tier 1 stipulated","source":"S9 Compilation 5","annual_period_start":"2024-01-01","within_retained_window":true,"applicability":"stipulated; not an actual entity assessment"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"cover p1; comparison p6"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C02":{"value":{"holder_financial_asset":true,"instrument":"synthetic debt security","scope_exceptions":"none stipulated; no subsidiary/group, lease, benefit, issuer-equity, insurance, combination-forward, commitment, share-payment, reimbursement or revenue-contract feature","transfer_derecognition_obstacle":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"2.1 pp8–9; B3.1.1 p49"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C03":{"value":{"party_to_contract":true,"contractual_date":"2024-06-03","contract_evidence":"synthetic binding purchase agreement; not historical evidence"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.1 p10"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C04":{"value":{"trade_date":"2024-06-03","settlement_date":"2024-06-03","recognition_date":"2024-06-03","regular_way":true,"delivery_terms":"delivery on same date within stipulated market convention","net_settlement_permitted":false,"policy":"trade date; stipulated consistent for mandatory FVTPL classification","date_eligible_under_policy_if_contractual_condition_holds":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.2 p10; B3.1.3–B3.1.6 pp49–50"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C05":{"value":{"category":"FVTPL","instrument_kind":"debt","business_model":"held for trading; neither hold-to-collect nor collect-and-sell objective, stipulated","cash_flows":"fixed principal and coupon, stipulated; no completed SPPI analysis","route":"mandatory residual 4.1.4, stipulated upstream assessment","designation":false,"equity_OCI_election":"not applicable to stipulated debt","rationale_available":true,"rationale_status":"synthetic assumption; detailed B4.1 guidance not reviewed"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"4.1.1–4.1.5 pp15–16; detailed guidance uninspected"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C06":{"value":{"price":"100","fair_value":"105","valuation_date":"2024-06-03","fair_value_basis":"105 is a supplied synthetic estimate; its evidence quality is assessed by C09","other_consideration_component":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1–5.1.3 p18; B5.1.1 p74"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C07":{"value":{"amount":"2","payee":"synthetic third-party broker","purpose":"execution of acquisition","incremental":true,"directly_attributable":true,"would_incur_without_acquisition":false,"financing_or_internal_admin_or_holding_cost":false,"invoice":"stipulated invoice, separately paid","service_completed":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"Appendix A p47; B5.4.8 p77"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C08":{"value":{"settlement":"cash","entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission","currency":"CU","unit":"units","scale":0,"separate_tax_treatment":false,"FX":false,"other_asset_treatment":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method scope; not a universal source rule"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C09":{"value":{"identical_instrument_active_market_quote":null,"technique_only_observable_market_data":null,"unknown_reason":null,"branch":"unknown"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1A p18; B5.1.2A pp74–75"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C10":{"value":{"method":"pending branch decision","unequal_price_a_method_available":false,"unequal_price_b_method_available":false},"unknown_reason":null,"provenance":{"kind":"specified_method_limit","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method limitation"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"}},"comparator":{"file":{"path":"docs/design/proposal/architecture/accounting-eligibility-fixtures-v1.json","sha256":"8d61ecfe4005d4652ead2f8a06d74b0340f4735ae83066fec7c19b0ab104c6f3"},"case_id":"E06"},"mutations":[{"op":"remove","path":"source/C09/value/required","before":true},{"op":"replace","path":"source/C09/unknown_reason","before":"neither route assessed","after":null},{"op":"replace","path":"source/C09/value/unknown_reason","before":"neither qualifying valuation route evidenced","after":null}]},{"id":"X202","complete_inputs":{"C01":{"value":{"entity":"synthetic purchaser","reporting_basis":"AASB, for-profit Tier 1 stipulated","source":"S9 Compilation 5","annual_period_start":"2024-01-01","within_retained_window":true,"applicability":"stipulated; not an actual entity assessment"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"cover p1; comparison p6"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C02":{"value":{"holder_financial_asset":true,"instrument":"synthetic debt security","scope_exceptions":"none stipulated; no subsidiary/group, lease, benefit, issuer-equity, insurance, combination-forward, commitment, share-payment, reimbursement or revenue-contract feature","transfer_derecognition_obstacle":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"2.1 pp8–9; B3.1.1 p49"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C03":{"value":{"party_to_contract":true,"contractual_date":"2024-06-03","contract_evidence":"synthetic binding purchase agreement; not historical evidence"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.1 p10"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C04":{"value":{"trade_date":"2024-06-03","settlement_date":"2024-06-03","recognition_date":"2024-06-03","regular_way":true,"delivery_terms":"delivery on same date within stipulated market convention","net_settlement_permitted":false,"policy":"trade date; stipulated consistent for mandatory FVTPL classification","date_eligible_under_policy_if_contractual_condition_holds":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.2 p10; B3.1.3–B3.1.6 pp49–50"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C05":{"value":{"category":"FVTPL","instrument_kind":"debt","business_model":"held for trading; neither hold-to-collect nor collect-and-sell objective, stipulated","cash_flows":"fixed principal and coupon, stipulated; no completed SPPI analysis","route":"mandatory residual 4.1.4, stipulated upstream assessment","designation":false,"equity_OCI_election":"not applicable to stipulated debt","rationale_available":true,"rationale_status":"synthetic assumption; detailed B4.1 guidance not reviewed"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"4.1.1–4.1.5 pp15–16; detailed guidance uninspected"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C06":{"value":{"price":"100","fair_value":"105","valuation_date":"2024-06-03","fair_value_basis":"105 is a supplied synthetic estimate; its evidence quality is assessed by C09","other_consideration_component":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1–5.1.3 p18; B5.1.1 p74"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C07":{"value":{"amount":"2","payee":"synthetic third-party broker","purpose":"execution of acquisition","incremental":true,"directly_attributable":true,"would_incur_without_acquisition":false,"financing_or_internal_admin_or_holding_cost":false,"invoice":"stipulated invoice, separately paid","service_completed":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"Appendix A p47; B5.4.8 p77"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C08":{"value":{"settlement":"cash","entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission","currency":"CU","unit":"units","scale":0,"separate_tax_treatment":false,"FX":false,"other_asset_treatment":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method scope; not a universal source rule"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C09":{"value":{"required":true,"technique_only_observable_market_data":null,"unknown_reason":null,"branch":"unknown"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1A p18; B5.1.2A pp74–75"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C10":{"value":{"method":"pending branch decision","unequal_price_a_method_available":false,"unequal_price_b_method_available":false},"unknown_reason":null,"provenance":{"kind":"specified_method_limit","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method limitation"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"}},"comparator":{"file":{"path":"docs/design/proposal/architecture/accounting-eligibility-fixtures-v1.json","sha256":"8d61ecfe4005d4652ead2f8a06d74b0340f4735ae83066fec7c19b0ab104c6f3"},"case_id":"E06"},"mutations":[{"op":"remove","path":"source/C09/value/identical_instrument_active_market_quote","before":null},{"op":"replace","path":"source/C09/unknown_reason","before":"neither route assessed","after":null},{"op":"replace","path":"source/C09/value/unknown_reason","before":"neither qualifying valuation route evidenced","after":null}]},{"id":"X241","complete_inputs":{"C01":{"value":{"entity":"synthetic purchaser","reporting_basis":"AASB, for-profit Tier 1 stipulated","source":"S9 Compilation 5","annual_period_start":"2024-01-01","within_retained_window":true,"applicability":"stipulated; not an actual entity assessment"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"cover p1; comparison p6"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C02":{"value":{"holder_financial_asset":true,"instrument":"synthetic debt security","scope_exceptions":"none stipulated; no subsidiary/group, lease, benefit, issuer-equity, insurance, combination-forward, commitment, share-payment, reimbursement or revenue-contract feature","transfer_derecognition_obstacle":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"2.1 pp8–9; B3.1.1 p49"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C03":{"value":{"party_to_contract":true,"contractual_date":"2024-06-03","contract_evidence":"synthetic binding purchase agreement; not historical evidence"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.1 p10"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C04":{"value":{"trade_date":"2024-06-03","settlement_date":"2024-06-03","recognition_date":"2024-06-03","regular_way":true,"delivery_terms":"delivery on same date within stipulated market convention","net_settlement_permitted":false,"policy":"trade date; stipulated consistent for mandatory FVTPL classification","date_eligible_under_policy_if_contractual_condition_holds":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.2 p10; B3.1.3–B3.1.6 pp49–50"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C05":{"value":{"category":"FVTPL","instrument_kind":"debt","business_model":"held for trading; neither hold-to-collect nor collect-and-sell objective, stipulated","cash_flows":"fixed principal and coupon, stipulated; no completed SPPI analysis","route":"mandatory residual 4.1.4, stipulated upstream assessment","designation":false,"equity_OCI_election":"not applicable to stipulated debt","rationale_available":true,"rationale_status":"synthetic assumption; detailed B4.1 guidance not reviewed"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"4.1.1–4.1.5 pp15–16; detailed guidance uninspected"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C06":{"value":{"price":"100","fair_value":"105","valuation_date":"2024-06-03","fair_value_basis":"105 is a supplied synthetic estimate; its evidence quality is assessed by C09","other_consideration_component":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1–5.1.3 p18; B5.1.1 p74"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C07":{"value":{"amount":"2","payee":"synthetic third-party broker","purpose":"execution of acquisition","incremental":true,"directly_attributable":true,"would_incur_without_acquisition":false,"financing_or_internal_admin_or_holding_cost":false,"invoice":"stipulated invoice, separately paid","service_completed":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"Appendix A p47; B5.4.8 p77"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C08":{"value":{"settlement":"cash","entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission","currency":"CU","unit":"units","scale":0,"separate_tax_treatment":false,"FX":false,"other_asset_treatment":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method scope; not a universal source rule"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C09":{"value":[],"unknown_reason":"","provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1A p18; B5.1.2A pp74–75"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C10":{"value":{"method":"pending branch decision","unequal_price_a_method_available":false,"unequal_price_b_method_available":false},"unknown_reason":false,"provenance":{"kind":"specified_method_limit","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method limitation"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"}},"comparator":{"file":{"path":"docs/design/proposal/architecture/accounting-eligibility-fixtures-v1.json","sha256":"8d61ecfe4005d4652ead2f8a06d74b0340f4735ae83066fec7c19b0ab104c6f3"},"case_id":"E06"},"mutations":[{"op":"replace","path":"source/C09/value","before":{"required":true,"identical_instrument_active_market_quote":null,"technique_only_observable_market_data":null,"unknown_reason":"neither qualifying valuation route evidenced","branch":"unknown"},"after":[]},{"op":"replace","path":"source/C09/unknown_reason","before":"neither route assessed","after":""},{"op":"replace","path":"source/C10/unknown_reason","before":null,"after":false}]},{"id":"K01","complete_inputs":{"C01":{"value":{"entity":"synthetic purchaser","reporting_basis":"AASB, for-profit Tier 1 stipulated","source":"S9 Compilation 5","annual_period_start":"2024-01-01","within_retained_window":true,"applicability":"stipulated; not an actual entity assessment"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"cover p1; comparison p6"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C02":{"value":{"holder_financial_asset":true,"instrument":"synthetic debt security","scope_exceptions":"none stipulated; no subsidiary/group, lease, benefit, issuer-equity, insurance, combination-forward, commitment, share-payment, reimbursement or revenue-contract feature","transfer_derecognition_obstacle":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"2.1 pp8–9; B3.1.1 p49"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C03":{"value":{"party_to_contract":true,"contractual_date":"2024-06-03","contract_evidence":"synthetic binding purchase agreement; not historical evidence"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.1 p10"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C04":{"value":{"trade_date":"2024-06-03","settlement_date":"2024-06-03","recognition_date":"2024-06-03","regular_way":true,"delivery_terms":"delivery on same date within stipulated market convention","net_settlement_permitted":false,"policy":"trade date; stipulated consistent for mandatory FVTPL classification","date_eligible_under_policy_if_contractual_condition_holds":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.2 p10; B3.1.3–B3.1.6 pp49–50"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C05":{"value":{"category":"FVTPL","instrument_kind":"debt","business_model":"held for trading; neither hold-to-collect nor collect-and-sell objective, stipulated","cash_flows":"fixed principal and coupon, stipulated; no completed SPPI analysis","route":"mandatory residual 4.1.4, stipulated upstream assessment","designation":false,"equity_OCI_election":"not applicable to stipulated debt","rationale_available":true,"rationale_status":"synthetic assumption; detailed B4.1 guidance not reviewed"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"4.1.1–4.1.5 pp15–16; detailed guidance uninspected"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C06":{"value":{"price":"100","fair_value":"105","valuation_date":"2024-06-03","fair_value_basis":"105 is a supplied synthetic estimate; its evidence quality is assessed by C09","other_consideration_component":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1–5.1.3 p18; B5.1.1 p74"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C07":{"value":{"amount":"2","payee":"synthetic third-party broker","purpose":"execution of acquisition","incremental":true,"directly_attributable":true,"would_incur_without_acquisition":false,"financing_or_internal_admin_or_holding_cost":false,"invoice":"stipulated invoice, separately paid","service_completed":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"Appendix A p47; B5.4.8 p77"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C08":{"value":{"settlement":"cash","entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission","currency":"CU","unit":"units","scale":0,"separate_tax_treatment":false,"FX":false,"other_asset_treatment":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method scope; not a universal source rule"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C09":{"value":{"required":false,"identical_instrument_active_market_quote":null,"technique_only_observable_market_data":null,"unknown_reason":"neither qualifying valuation route evidenced","branch":"unknown"},"unknown_reason":"neither route assessed","provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1A p18; B5.1.2A pp74–75"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C10":{"value":{"method":"pending branch decision","unequal_price_a_method_available":false,"unequal_price_b_method_available":false},"unknown_reason":null,"provenance":{"kind":"specified_method_limit","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method limitation"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"}},"comparator":{"file":{"path":"docs/design/proposal/architecture/accounting-eligibility-fixtures-v1.json","sha256":"8d61ecfe4005d4652ead2f8a06d74b0340f4735ae83066fec7c19b0ab104c6f3"},"case_id":"E06"},"mutations":[{"op":"replace","path":"source/C09/value/required","before":true,"after":false}]},{"id":"K04","complete_inputs":{"C01":{"value":{"entity":"synthetic purchaser","reporting_basis":"AASB, for-profit Tier 1 stipulated","source":"S9 Compilation 5","annual_period_start":"2024-01-01","within_retained_window":true,"applicability":"stipulated; not an actual entity assessment"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"cover p1; comparison p6"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C02":{"value":{"holder_financial_asset":true,"instrument":"synthetic debt security","scope_exceptions":"none stipulated; no subsidiary/group, lease, benefit, issuer-equity, insurance, combination-forward, commitment, share-payment, reimbursement or revenue-contract feature","transfer_derecognition_obstacle":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"2.1 pp8–9; B3.1.1 p49"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C03":{"value":{"party_to_contract":true,"contractual_date":"2024-06-03","contract_evidence":"synthetic binding purchase agreement; not historical evidence"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.1 p10"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C04":{"value":{"trade_date":"2024-06-03","settlement_date":"2024-06-03","recognition_date":"2024-06-03","regular_way":true,"delivery_terms":"delivery on same date within stipulated market convention","net_settlement_permitted":false,"policy":"trade date; stipulated consistent for mandatory FVTPL classification","date_eligible_under_policy_if_contractual_condition_holds":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"3.1.2 p10; B3.1.3–B3.1.6 pp49–50"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C05":{"value":{"category":"FVTPL","instrument_kind":"debt","business_model":"held for trading; neither hold-to-collect nor collect-and-sell objective, stipulated","cash_flows":"fixed principal and coupon, stipulated; no completed SPPI analysis","route":"mandatory residual 4.1.4, stipulated upstream assessment","designation":false,"equity_OCI_election":"not applicable to stipulated debt","rationale_available":true,"rationale_status":"synthetic assumption; detailed B4.1 guidance not reviewed"},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"4.1.1–4.1.5 pp15–16; detailed guidance uninspected"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C06":{"value":{"price":"100","fair_value":"105","valuation_date":"2024-06-03","fair_value_basis":"105 is a supplied synthetic estimate; its evidence quality is assessed by C09","other_consideration_component":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1–5.1.3 p18; B5.1.1 p74"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C07":{"value":{"amount":"2","payee":"synthetic third-party broker","purpose":"execution of acquisition","incremental":true,"directly_attributable":true,"would_incur_without_acquisition":false,"financing_or_internal_admin_or_holding_cost":false,"invoice":"stipulated invoice, separately paid","service_completed":true},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"Appendix A p47; B5.4.8 p77"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C08":{"value":{"settlement":"cash","entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission","currency":"CU","unit":"units","scale":0,"separate_tax_treatment":false,"FX":false,"other_asset_treatment":false},"unknown_reason":null,"provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method scope; not a universal source rule"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C09":{"value":{"required":true,"identical_instrument_active_market_quote":null,"technique_only_observable_market_data":null,"unknown_reason":"neither qualifying valuation route evidenced","branch":"unknown"},"unknown_reason":"neither route assessed","provenance":{"kind":"synthetic_assumption","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"5.1.1A p18; B5.1.2A pp74–75"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"},"C10":{"value":{"method":"pending branch decision","unequal_price_a_method_available":true,"unequal_price_b_method_available":false},"unknown_reason":null,"provenance":{"kind":"specified_method_limit","origin":"retained A01/A03 amounts; additional facts explicitly introduced for conditional assessment","source_rule":"local method limitation"},"scope":"this synthetic assessment only","version":"eligibility-example-v1"}},"comparator":{"file":{"path":"docs/design/proposal/architecture/accounting-eligibility-fixtures-v1.json","sha256":"8d61ecfe4005d4652ead2f8a06d74b0340f4735ae83066fec7c19b0ab104c6f3"},"case_id":"E06"},"mutations":[{"op":"replace","path":"source/C10/value/unequal_price_a_method_available","before":false,"after":true}]}],"baselines":[{"id":"I01","source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-eligibility-fixtures-v1.json","sha256":"8d61ecfe4005d4652ead2f8a06d74b0340f4735ae83066fec7c19b0ab104c6f3"},"case_id":"E01"},"request":"11724d4569dd9bed11351cbc1e1e8fbe6bbab843d0b25c373a833a6b820bbf53","assessment":"8c685bf8d8a1575488a363a7f3cbf93ba966b19c9845af1000a547ab75c445a1","submission":"1954e381849038b491354b6602a9d1e3dc8484d451e97a6b8776947491a1df3b","response":"f7aa17bc8600b8414f21cd3622eb489e294d97a37f735e2966ec7b6230972546","before":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"after":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]}},{"id":"I06","source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-eligibility-fixtures-v1.json","sha256":"8d61ecfe4005d4652ead2f8a06d74b0340f4735ae83066fec7c19b0ab104c6f3"},"case_id":"E06"},"request":"d0568d432de4230d3d86e0306214ffd281a3d24a9ecb5bb01f8d748eb33a20dd","assessment":"af2cbb20dd7bf9d465bb299fedc7abff99165fc2c483e9de22da2356b77e92d0","submission":"57859e41601208ab6630db57f78a65f25acad65e2ccd96ddc532a97cd3720924","response":"8c672cba26760979dcc46b8a1e75bec8433f8ec0508a028079cf8c122d3c1d56","before":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]},"after":{"identity_index":{},"committed_journals":[],"selected_state":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","committed_receipts":[]}}],"records":{"009ab9863371a17fa943eaa3a46a3b80a15e754c4e95202e2d02ece3a1b6b6ff":{"kind":"eligibility_input","content":{"schema_version":1,"profile":"acquisition-conditions-v1","dossier":{"path":"docs/design/proposal/architecture/accounting-eligibility-dossier-v1.md","sha256":"5b5fa718b997d53dc43530cf30b4451a78c06b6e0b468aaa28313e0027ba7f84"},"decision_rules":{"path":"docs/design/proposal/architecture/accounting-eligibility-decision-supplement-v1.md","sha256":"b3fde2435f6ce4de3386a884321fed5b1a93a0b26d49da4f3f8b1eb31f942d46"},"source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K04"},"bindings":{"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","assumptions":"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","evidence":["f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028"],"admissions":["10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c"]},"aliases":{"scope":"synthetic_only","source_labels":{"entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission"},"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A"},"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e"},"conditions":[{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K04"},"condition_id":"C01","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K04"},"condition_id":"C02","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K04"},"condition_id":"C03","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K04"},"condition_id":"C04","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K04"},"condition_id":"C05","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K04"},"condition_id":"C06","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K04"},"condition_id":"C07","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K04"},"condition_id":"C08","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K04"},"condition_id":"C09","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K04"},"condition_id":"C10","value_version":"eligibility-example-v1"}]},"domain":"accdsl.accounting.integration.v1"},"00df3966fc62c6ce957bbe9385687d7c310ae58c17f8a3fef8a8a06e9cd8be85":{"kind":"admission","content":{"evidence":"6afbdda56ec107aaf0e6ff6cccae9650fb3f755202a30c8000833c7f85cf508d","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","status":"synthetic_only","known_at":null,"reviewed_at":null,"reason":"Scenario input, not a historically available company fact"}},"060e574b32947b7f26902561f397f5d2c25127ad6f9cdd797da0044dc6244c04":{"kind":"response","content":{"submission":"2890f182341d858eb68c26d8ff06c876e99279a852b21039a1dcc225cf2dc3fb","request":null,"status":"rejected","reason_codes":["INVALID_UNKNOWN_REPRESENTATION"],"assessment":null,"diagnostic_journal":null,"diagnostic_delta":null,"receipt":null,"observed_state":null,"commit_status":"not_committed","additional_commit":false,"statuses":{"structural_validity":"invalid","mathematical_status":"unresolved","computation_status":"not_computed","empirical_justification":"not_established","capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed","human_acceptance":"pending"},"metadata":{"response_id":"integration-E06","operation":"assess_only"}},"domain":"accdsl.accounting.integration.v1"},"0c785e643f317aa6c2a0c0d567431f33cca6db84940b017327a206e7015ed898":{"kind":"submission","content":{"wire_format":"ASCII_JSON","raw_text":"{\"admissions\":[\"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c\"],\"assumptions\":\"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"7a1a57da0f291f32b21aa9638f351e615960567859b74c2a1e68565af47fdde0\",\"event\":\"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f\",\"evidence\":[\"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E06\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}"},"domain":"accdsl.accounting.integration.v1"},"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a":{"kind":"state","content":{"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","sequence":0,"balances":{"cash":"1000.00","asset":"0.00","expense":"0.00","equity":"-1000.00"}}},"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c":{"kind":"admission","content":{"evidence":"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","status":"synthetic_only","known_at":null,"reviewed_at":null,"reason":"Scenario input, not a historically available company fact"}},"111c9e1e08996d9e1d3a67d467d725417a5eecf3436ac2839abb8219f4515078":{"kind":"request","content":{"schema_version":2,"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A","business_event_id":"integration-E06"},"event":"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f","opening":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","evidence":["f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028"],"admissions":["10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c"],"assumptions":"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","lineage":[{"file":{"path":"docs/design/proposal/methods/standards-fixtures-v1.json","sha256":"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798"},"locator":"acquisitions[id=A01]"}],"operation":"assess_only","eligibility":"009ab9863371a17fa943eaa3a46a3b80a15e754c4e95202e2d02ece3a1b6b6ff"},"domain":"accdsl.accounting.integration.v1"},"11724d4569dd9bed11351cbc1e1e8fbe6bbab843d0b25c373a833a6b820bbf53":{"kind":"request","content":{"schema_version":2,"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A","business_event_id":"integration-E01"},"event":"e9a7c404613183ccd62033d0ccd47fd315970afde5d798671c83e5419dd2b975","opening":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","evidence":["6afbdda56ec107aaf0e6ff6cccae9650fb3f755202a30c8000833c7f85cf508d"],"admissions":["00df3966fc62c6ce957bbe9385687d7c310ae58c17f8a3fef8a8a06e9cd8be85"],"assumptions":"55fa6518f2380495f24c0639b6ec39d6a0335497ff4b3a67cc9b8fbbcf6c731b","lineage":[{"file":{"path":"docs/design/proposal/methods/standards-fixtures-v1.json","sha256":"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798"},"locator":"acquisitions[id=A01]"}],"operation":"assess_only","eligibility":"38f9edd585bfe5360ebd9e408b0f4c79fb6864ce293bd4bf07dbcf120436c450"}},"1954e381849038b491354b6602a9d1e3dc8484d451e97a6b8776947491a1df3b":{"kind":"submission","content":{"wire_format":"ASCII_JSON","raw_text":"{\"admissions\":[\"00df3966fc62c6ce957bbe9385687d7c310ae58c17f8a3fef8a8a06e9cd8be85\"],\"assumptions\":\"55fa6518f2380495f24c0639b6ec39d6a0335497ff4b3a67cc9b8fbbcf6c731b\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"38f9edd585bfe5360ebd9e408b0f4c79fb6864ce293bd4bf07dbcf120436c450\",\"event\":\"e9a7c404613183ccd62033d0ccd47fd315970afde5d798671c83e5419dd2b975\",\"evidence\":[\"6afbdda56ec107aaf0e6ff6cccae9650fb3f755202a30c8000833c7f85cf508d\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E01\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}"}},"2890f182341d858eb68c26d8ff06c876e99279a852b21039a1dcc225cf2dc3fb":{"kind":"submission","content":{"wire_format":"ASCII_JSON","raw_text":"{\"admissions\":[\"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c\"],\"assumptions\":\"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"ff6025ba31f7d4d28bbd04046edb5ec51b05073fd070cc7606140c566bf67a2a\",\"event\":\"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f\",\"evidence\":[\"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E06\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}"},"domain":"accdsl.accounting.integration.v1"},"3c25987b9a7a1a5afbd4daaf2c64b96504241b13632e804a09b68eefb6855f57":{"kind":"response","content":{"submission":"c21fc6ae5892c5cb088cc6eb290bf7821a4b4841e8fa847d62e5682f97787810","request":null,"status":"rejected","reason_codes":["METHOD_CAPABILITY_MISMATCH"],"assessment":null,"diagnostic_journal":null,"diagnostic_delta":null,"receipt":null,"observed_state":null,"commit_status":"not_committed","additional_commit":false,"statuses":{"structural_validity":"invalid","mathematical_status":"unresolved","computation_status":"not_computed","empirical_justification":"not_established","capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed","human_acceptance":"pending"},"metadata":{"response_id":"integration-E06","operation":"assess_only"}},"domain":"accdsl.accounting.integration.v1"},"3e71df06c1f530037f53937018977b28a27ba1f04bde42f2f8b5025cfc224035":{"kind":"assessment","content":{"schema_version":2,"request":"9d57a2b3eaae5c02eac0d11597f9494483c79e3e43f9db83b06ff6ffc72530b1","status":"unresolved","reason_codes":["C09:unresolved","C10:unresolved"],"preconditions":[{"name":"C01","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C02","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C03","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C04","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C05","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C06","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C07","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C08","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C09","status":"unknown","support":"unequal price; valuation routes unknown"},{"name":"C10","status":"unknown","support":"branch evidence missing; method decision pending"}],"authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","eligibility":"6298680567179a51f9610908611ac8a03af8e8ce6dbcedbcb10932950027237c","findings":[{"condition":"C01","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C02","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C03","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C04","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C05","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C06","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C07","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C08","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C09","status":"unresolved","reason":"unequal price; valuation routes unknown"},{"condition":"C10","status":"unresolved","reason":"branch evidence missing; method decision pending"}],"valuation_branch":"unknown","valuation_routes":[{"field":"identical_instrument_active_market_quote","value":null,"status":"unknown"},{"field":"technique_only_observable_market_data","value":null,"status":"unknown"}],"method_applicability":"unresolved","source_assessment":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X007"},"evidence_level":"conditional_synthetic_only","posting_permitted":false,"diagnostic_example":null},"domain":"accdsl.accounting.integration.v1"},"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a":{"kind":"chart","content":{"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","version":1,"accounts":[{"account_id":"cash","concept_id":"synthetic.cash","normal_side":"debit","dimensions":{}},{"account_id":"asset","concept_id":"synthetic.asset","normal_side":"debit","dimensions":{}},{"account_id":"expense","concept_id":"synthetic.expense","normal_side":"debit","dimensions":{}},{"account_id":"equity","concept_id":"synthetic.equity","normal_side":"credit","dimensions":{}}]}},"55fa6518f2380495f24c0639b6ec39d6a0335497ff4b3a67cc9b8fbbcf6c731b":{"kind":"assumptions","content":{"version":1,"eligibility":"stipulated","cash_settlement":true,"no_other_flows":true,"branch_admissibility":"stipulated","balance_sign":"debit_positive"}},"57859e41601208ab6630db57f78a65f25acad65e2ccd96ddc532a97cd3720924":{"kind":"submission","content":{"wire_format":"ASCII_JSON","raw_text":"{\"admissions\":[\"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c\"],\"assumptions\":\"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"3cf81a06db6415b21ffdd037c5d44abe8d11122b1bf5c34ca0ba36eca72c63b1\",\"event\":\"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f\",\"evidence\":[\"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E06\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}"}},"5c6e6124b0116f7f6d8f46e4f0cfb58cf99e1666e60275903035875b965e025b":{"kind":"response","content":{"submission":"0c785e643f317aa6c2a0c0d567431f33cca6db84940b017327a206e7015ed898","request":null,"status":"rejected","reason_codes":["INVALID_UNKNOWN_REPRESENTATION","INVALID_FIELD_TYPE"],"assessment":null,"diagnostic_journal":null,"diagnostic_delta":null,"receipt":null,"observed_state":null,"commit_status":"not_committed","additional_commit":false,"statuses":{"structural_validity":"invalid","mathematical_status":"unresolved","computation_status":"not_computed","empirical_justification":"not_established","capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed","human_acceptance":"pending"},"metadata":{"response_id":"integration-E06","operation":"assess_only"}},"domain":"accdsl.accounting.integration.v1"},"61ec1363be0c50e93c4f76d8db60224a12ef5e160f2ab51521086cacb360b8d5":{"kind":"eligibility_input","content":{"schema_version":1,"profile":"acquisition-conditions-v1","dossier":{"path":"docs/design/proposal/architecture/accounting-eligibility-dossier-v1.md","sha256":"5b5fa718b997d53dc43530cf30b4451a78c06b6e0b468aaa28313e0027ba7f84"},"decision_rules":{"path":"docs/design/proposal/architecture/accounting-eligibility-decision-supplement-v1.md","sha256":"b3fde2435f6ce4de3386a884321fed5b1a93a0b26d49da4f3f8b1eb31f942d46"},"source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X002"},"bindings":{"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","assumptions":"55fa6518f2380495f24c0639b6ec39d6a0335497ff4b3a67cc9b8fbbcf6c731b","evidence":["6afbdda56ec107aaf0e6ff6cccae9650fb3f755202a30c8000833c7f85cf508d"],"admissions":["00df3966fc62c6ce957bbe9385687d7c310ae58c17f8a3fef8a8a06e9cd8be85"]},"aliases":{"scope":"synthetic_only","source_labels":{"entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission"},"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A"},"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e"},"conditions":[{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X002"},"condition_id":"C01","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X002"},"condition_id":"C02","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X002"},"condition_id":"C03","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X002"},"condition_id":"C04","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X002"},"condition_id":"C05","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X002"},"condition_id":"C06","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X002"},"condition_id":"C07","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X002"},"condition_id":"C08","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X002"},"condition_id":"C09","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X002"},"condition_id":"C10","value_version":"eligibility-example-v1"}]},"domain":"accdsl.accounting.integration.v1"},"6298680567179a51f9610908611ac8a03af8e8ce6dbcedbcb10932950027237c":{"kind":"eligibility_input","content":{"schema_version":1,"profile":"acquisition-conditions-v1","dossier":{"path":"docs/design/proposal/architecture/accounting-eligibility-dossier-v1.md","sha256":"5b5fa718b997d53dc43530cf30b4451a78c06b6e0b468aaa28313e0027ba7f84"},"decision_rules":{"path":"docs/design/proposal/architecture/accounting-eligibility-decision-supplement-v1.md","sha256":"b3fde2435f6ce4de3386a884321fed5b1a93a0b26d49da4f3f8b1eb31f942d46"},"source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X007"},"bindings":{"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","assumptions":"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","evidence":["f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028"],"admissions":["10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c"]},"aliases":{"scope":"synthetic_only","source_labels":{"entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission"},"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A"},"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e"},"conditions":[{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X007"},"condition_id":"C01","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X007"},"condition_id":"C02","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X007"},"condition_id":"C03","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X007"},"condition_id":"C04","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X007"},"condition_id":"C05","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X007"},"condition_id":"C06","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X007"},"condition_id":"C07","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X007"},"condition_id":"C08","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X007"},"condition_id":"C09","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X007"},"condition_id":"C10","value_version":"eligibility-example-v1"}]},"domain":"accdsl.accounting.integration.v1"},"64d20a86908b0321a6b1ca7dfd8ed4d498cd76eadaca07deeecdd46357a0db7f":{"kind":"submission","content":{"wire_format":"ASCII_JSON","raw_text":"{\"admissions\":[\"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c\"],\"assumptions\":\"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"99bac9fb82a55ae3bf65c7a7eff6799bcbd241f8d543a84822b91dd42f0445b3\",\"event\":\"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f\",\"evidence\":[\"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E06\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}"},"domain":"accdsl.accounting.integration.v1"},"6afbdda56ec107aaf0e6ff6cccae9650fb3f755202a30c8000833c7f85cf508d":{"kind":"evidence","content":{"version":1,"source":{"file":{"path":"docs/design/proposal/methods/standards-fixtures-v1.json","sha256":"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798"},"locator":"acquisitions[id=A01]"},"source_case":"A01","nature":"synthetic","observable_valuation":{"status":"unknown","reason":"not required or qualifying route unresolved; see C09"}}},"6b0307d2362ab1ae6cce8efd0b7352190055f42b81ff825ecce5078ddb47cbb0":{"kind":"response","content":{"submission":"c1c98853cc8192823fe353068c70d760328faa4834c0404e02c4065148c08719","request":null,"status":"rejected","reason_codes":["SOURCE_CONTEXT_MISMATCH"],"assessment":null,"diagnostic_journal":null,"diagnostic_delta":null,"receipt":null,"observed_state":null,"commit_status":"not_committed","additional_commit":false,"statuses":{"structural_validity":"invalid","mathematical_status":"unresolved","computation_status":"not_computed","empirical_justification":"not_established","capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed","human_acceptance":"pending"},"metadata":{"response_id":"integration-E06","operation":"assess_only"}},"domain":"accdsl.accounting.integration.v1"},"6f080d929801cd86f5e0585870d1747fdeb3139639dea72c9703d31e2973ca41":{"kind":"request","content":{"schema_version":2,"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A","business_event_id":"integration-E06"},"event":"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f","opening":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","evidence":["f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028"],"admissions":["10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c"],"assumptions":"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","lineage":[{"file":{"path":"docs/design/proposal/methods/standards-fixtures-v1.json","sha256":"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798"},"locator":"acquisitions[id=A01]"}],"operation":"assess_only","eligibility":"da38ce395c7aeb3142d684c9b98fe71f740d25d84be89b8c60708b9212b6defd"},"domain":"accdsl.accounting.integration.v1"},"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e":{"kind":"branch","content":{"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch_id":"A","family_id":"synthetic-family-1","version":1,"admissibility":"stipulated"}},"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f":{"kind":"context","content":{"entity_id":"example-company","book_id":"illustrative-book","currency":"CU","unit":"units","scale":0,"basis":"synthetic-A01-FVTPL","annual_period_start":"2024-01-01","schema_version":1}},"7a1a57da0f291f32b21aa9638f351e615960567859b74c2a1e68565af47fdde0":{"kind":"eligibility_input","content":{"schema_version":1,"profile":"acquisition-conditions-v1","dossier":{"path":"docs/design/proposal/architecture/accounting-eligibility-dossier-v1.md","sha256":"5b5fa718b997d53dc43530cf30b4451a78c06b6e0b468aaa28313e0027ba7f84"},"decision_rules":{"path":"docs/design/proposal/architecture/accounting-eligibility-decision-supplement-v1.md","sha256":"b3fde2435f6ce4de3386a884321fed5b1a93a0b26d49da4f3f8b1eb31f942d46"},"source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X241"},"bindings":{"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","assumptions":"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","evidence":["f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028"],"admissions":["10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c"]},"aliases":{"scope":"synthetic_only","source_labels":{"entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission"},"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A"},"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e"},"conditions":[{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X241"},"condition_id":"C01","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X241"},"condition_id":"C02","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X241"},"condition_id":"C03","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X241"},"condition_id":"C04","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X241"},"condition_id":"C05","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X241"},"condition_id":"C06","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X241"},"condition_id":"C07","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X241"},"condition_id":"C08","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X241"},"condition_id":"C09","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X241"},"condition_id":"C10","value_version":"eligibility-example-v1"}]},"domain":"accdsl.accounting.integration.v1"},"7a7cd0039ad37aa1cc98602ff1e229d68344bbe169dacdf1f2ebd5e9a72269aa":{"kind":"request","content":{"schema_version":2,"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A","business_event_id":"integration-E06"},"event":"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f","opening":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","evidence":["f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028"],"admissions":["10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c"],"assumptions":"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","lineage":[{"file":{"path":"docs/design/proposal/methods/standards-fixtures-v1.json","sha256":"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798"},"locator":"acquisitions[id=A01]"}],"operation":"assess_only","eligibility":"ff6025ba31f7d4d28bbd04046edb5ec51b05073fd070cc7606140c566bf67a2a"},"domain":"accdsl.accounting.integration.v1"},"80b9409ba45c57e8781beaf730ddf1df16144d10ec784c654446ad7183ff81d6":{"kind":"submission","content":{"wire_format":"ASCII_JSON","raw_text":"{\"admissions\":[\"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c\"],\"assumptions\":\"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"da38ce395c7aeb3142d684c9b98fe71f740d25d84be89b8c60708b9212b6defd\",\"event\":\"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f\",\"evidence\":[\"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E06\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}"},"domain":"accdsl.accounting.integration.v1"},"89a74768f1124b2ecb5c6a21c508a233451b0f9c63b49365badf59644644a49a":{"kind":"request","content":{"schema_version":2,"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A","business_event_id":"integration-E01"},"event":"e9a7c404613183ccd62033d0ccd47fd315970afde5d798671c83e5419dd2b975","opening":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","evidence":["6afbdda56ec107aaf0e6ff6cccae9650fb3f755202a30c8000833c7f85cf508d"],"admissions":["00df3966fc62c6ce957bbe9385687d7c310ae58c17f8a3fef8a8a06e9cd8be85"],"assumptions":"55fa6518f2380495f24c0639b6ec39d6a0335497ff4b3a67cc9b8fbbcf6c731b","lineage":[{"file":{"path":"docs/design/proposal/methods/standards-fixtures-v1.json","sha256":"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798"},"locator":"acquisitions[id=A01]"}],"operation":"assess_only","eligibility":"61ec1363be0c50e93c4f76d8db60224a12ef5e160f2ab51521086cacb360b8d5"},"domain":"accdsl.accounting.integration.v1"},"8b39f2b5526db38e938b6cf80e3ff5fe20e42c5c27dcc477b633c70b2becdedd":{"kind":"response","content":{"submission":"a5a3bd557cbb7a994119bd55795b76c8bba17c658bc3a46630901086d13bc5a2","request":"89a74768f1124b2ecb5c6a21c508a233451b0f9c63b49365badf59644644a49a","status":"assessed","reason_codes":[],"assessment":"92831f62195c24559d01cff17206e1716db033eb95ed1974bdf43553290992c2","diagnostic_journal":null,"diagnostic_delta":null,"receipt":null,"observed_state":null,"commit_status":"not_committed","additional_commit":false,"statuses":{"structural_validity":"valid","mathematical_status":"unresolved","computation_status":"specified_exact","empirical_justification":"not_established","capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed","human_acceptance":"pending"},"metadata":{"response_id":"integration-E01","operation":"assess_only"}},"domain":"accdsl.accounting.integration.v1"},"8c672cba26760979dcc46b8a1e75bec8433f8ec0508a028079cf8c122d3c1d56":{"kind":"response","content":{"submission":"57859e41601208ab6630db57f78a65f25acad65e2ccd96ddc532a97cd3720924","request":"d0568d432de4230d3d86e0306214ffd281a3d24a9ecb5bb01f8d748eb33a20dd","status":"assessed","reason_codes":["C09:unresolved","C10:unresolved"],"assessment":"af2cbb20dd7bf9d465bb299fedc7abff99165fc2c483e9de22da2356b77e92d0","diagnostic_journal":null,"diagnostic_delta":null,"receipt":null,"observed_state":null,"commit_status":"not_committed","additional_commit":false,"statuses":{"structural_validity":"valid","mathematical_status":"unresolved","computation_status":"specified_exact","empirical_justification":"not_established","capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed","human_acceptance":"pending"},"metadata":{"response_id":"integration-E06","operation":"assess_only"}}},"8c685bf8d8a1575488a363a7f3cbf93ba966b19c9845af1000a547ab75c445a1":{"kind":"assessment","content":{"schema_version":2,"request":"11724d4569dd9bed11351cbc1e1e8fbe6bbab843d0b25c373a833a6b820bbf53","status":"eligible","reason_codes":[],"preconditions":[{"name":"C01","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C02","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C03","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C04","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C05","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C06","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C07","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C08","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C09","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C10","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"}],"authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","eligibility":"38f9edd585bfe5360ebd9e408b0f4c79fb6864ce293bd4bf07dbcf120436c450","findings":[{"condition":"C01","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C02","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C03","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C04","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C05","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C06","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C07","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C08","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C09","status":"not_applicable","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C10","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"}],"valuation_branch":"not_applicable","valuation_routes":[{"field":"identical_instrument_active_market_quote","value":null,"status":"not_applicable"},{"field":"technique_only_observable_market_data","value":null,"status":"not_applicable"}],"method_applicability":"conditional","source_assessment":{"file":{"path":"docs/design/proposal/architecture/accounting-eligibility-fixtures-v1.json","sha256":"8d61ecfe4005d4652ead2f8a06d74b0340f4735ae83066fec7c19b0ab104c6f3"},"case_id":"E01"},"evidence_level":"conditional_synthetic_only","posting_permitted":false,"diagnostic_example":{"file":{"path":"docs/design/proposal/architecture/accounting-eligibility-fixtures-v1.json","sha256":"8d61ecfe4005d4652ead2f8a06d74b0340f4735ae83066fec7c19b0ab104c6f3"},"case_id":"E01"}}},"92831f62195c24559d01cff17206e1716db033eb95ed1974bdf43553290992c2":{"kind":"assessment","content":{"schema_version":2,"request":"89a74768f1124b2ecb5c6a21c508a233451b0f9c63b49365badf59644644a49a","status":"eligible","reason_codes":[],"preconditions":[{"name":"C01","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C02","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C03","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C04","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C05","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C06","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C07","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C08","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C09","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C10","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"}],"authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","eligibility":"61ec1363be0c50e93c4f76d8db60224a12ef5e160f2ab51521086cacb360b8d5","findings":[{"condition":"C01","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C02","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C03","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C04","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C05","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C06","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C07","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C08","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C09","status":"not_applicable","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C10","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"}],"valuation_branch":"not_applicable","valuation_routes":[{"field":"identical_instrument_active_market_quote","value":null,"status":"not_applicable"},{"field":"technique_only_observable_market_data","value":null,"status":"not_applicable"}],"method_applicability":"conditional","source_assessment":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X002"},"evidence_level":"conditional_synthetic_only","posting_permitted":false,"diagnostic_example":{"file":{"path":"docs/design/proposal/architecture/accounting-eligibility-fixtures-v1.json","sha256":"8d61ecfe4005d4652ead2f8a06d74b0340f4735ae83066fec7c19b0ab104c6f3"},"case_id":"E01"}},"domain":"accdsl.accounting.integration.v1"},"99bac9fb82a55ae3bf65c7a7eff6799bcbd241f8d543a84822b91dd42f0445b3":{"kind":"eligibility_input","content":{"schema_version":1,"profile":"acquisition-conditions-v1","dossier":{"path":"docs/design/proposal/architecture/accounting-eligibility-dossier-v1.md","sha256":"5b5fa718b997d53dc43530cf30b4451a78c06b6e0b468aaa28313e0027ba7f84"},"decision_rules":{"path":"docs/design/proposal/architecture/accounting-eligibility-decision-supplement-v1.md","sha256":"b3fde2435f6ce4de3386a884321fed5b1a93a0b26d49da4f3f8b1eb31f942d46"},"source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X188"},"bindings":{"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","assumptions":"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","evidence":["f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028"],"admissions":["10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c"]},"aliases":{"scope":"synthetic_only","source_labels":{"entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission"},"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A"},"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e"},"conditions":[{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X188"},"condition_id":"C01","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X188"},"condition_id":"C02","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X188"},"condition_id":"C03","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X188"},"condition_id":"C04","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X188"},"condition_id":"C05","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X188"},"condition_id":"C06","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X188"},"condition_id":"C07","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X188"},"condition_id":"C08","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X188"},"condition_id":"C09","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X188"},"condition_id":"C10","value_version":"eligibility-example-v1"}]},"domain":"accdsl.accounting.integration.v1"},"9d57a2b3eaae5c02eac0d11597f9494483c79e3e43f9db83b06ff6ffc72530b1":{"kind":"request","content":{"schema_version":2,"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A","business_event_id":"integration-E06"},"event":"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f","opening":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","evidence":["f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028"],"admissions":["10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c"],"assumptions":"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","lineage":[{"file":{"path":"docs/design/proposal/methods/standards-fixtures-v1.json","sha256":"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798"},"locator":"acquisitions[id=A01]"}],"operation":"assess_only","eligibility":"6298680567179a51f9610908611ac8a03af8e8ce6dbcedbcb10932950027237c"},"domain":"accdsl.accounting.integration.v1"},"a0fe3d57e8f51f9200a569d5ae657ec46087ec30735ce2e78f22861c8ec04713":{"kind":"request","content":{"schema_version":2,"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A","business_event_id":"integration-E06"},"event":"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f","opening":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","evidence":["f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028"],"admissions":["10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c"],"assumptions":"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","lineage":[{"file":{"path":"docs/design/proposal/methods/standards-fixtures-v1.json","sha256":"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798"},"locator":"acquisitions[id=A01]"}],"operation":"assess_only","eligibility":"f6794fa664d2bdb039761d8db47a39b2675b465184fec864831f67de3ff7d5fb"},"domain":"accdsl.accounting.integration.v1"},"a5a3bd557cbb7a994119bd55795b76c8bba17c658bc3a46630901086d13bc5a2":{"kind":"submission","content":{"wire_format":"ASCII_JSON","raw_text":"{\"admissions\":[\"00df3966fc62c6ce957bbe9385687d7c310ae58c17f8a3fef8a8a06e9cd8be85\"],\"assumptions\":\"55fa6518f2380495f24c0639b6ec39d6a0335497ff4b3a67cc9b8fbbcf6c731b\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"61ec1363be0c50e93c4f76d8db60224a12ef5e160f2ab51521086cacb360b8d5\",\"event\":\"e9a7c404613183ccd62033d0ccd47fd315970afde5d798671c83e5419dd2b975\",\"evidence\":[\"6afbdda56ec107aaf0e6ff6cccae9650fb3f755202a30c8000833c7f85cf508d\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E01\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}"},"domain":"accdsl.accounting.integration.v1"},"a85ec29dd5420f2d0d5a8995bab5a0cb633c0f2da8475205d1ab4d2c0f358512":{"kind":"request","content":{"schema_version":2,"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A","business_event_id":"integration-E06"},"event":"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f","opening":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","evidence":["f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028"],"admissions":["10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c"],"assumptions":"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","lineage":[{"file":{"path":"docs/design/proposal/methods/standards-fixtures-v1.json","sha256":"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798"},"locator":"acquisitions[id=A01]"}],"operation":"assess_only","eligibility":"7a1a57da0f291f32b21aa9638f351e615960567859b74c2a1e68565af47fdde0"},"domain":"accdsl.accounting.integration.v1"},"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce":{"kind":"authority","content":{"version":1,"source":{"file":{"path":"docs/design/research/p08-v1/aasb9.pdf","sha256":"8f5a87c67a76c193bedeee8ea7f3f21556b3886eee4184a62c7045256b3f84f0"},"locator":"AASB 9 compilation 5, paragraphs 5.1.1 and B5.1.2A; retained example scope"},"paragraphs":["5.1.1","B5.1.2A"],"application_scope":"For-profit annual period beginning 2024-01-01; applicability stipulated, no new source interpretation","applicability":"stipulated"}},"af2cbb20dd7bf9d465bb299fedc7abff99165fc2c483e9de22da2356b77e92d0":{"kind":"assessment","content":{"schema_version":2,"request":"d0568d432de4230d3d86e0306214ffd281a3d24a9ecb5bb01f8d748eb33a20dd","status":"unresolved","reason_codes":["C09:unresolved","C10:unresolved"],"preconditions":[{"name":"C01","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C02","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C03","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C04","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C05","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C06","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C07","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C08","status":"satisfied","support":"stipulated facts satisfy this condition only within this illustration"},{"name":"C09","status":"unknown","support":"unequal price; valuation routes unknown"},{"name":"C10","status":"unknown","support":"branch evidence missing; method decision pending"}],"authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","eligibility":"3cf81a06db6415b21ffdd037c5d44abe8d11122b1bf5c34ca0ba36eca72c63b1","findings":[{"condition":"C01","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C02","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C03","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C04","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C05","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C06","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C07","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C08","status":"satisfied_conditionally","reason":"stipulated facts satisfy this condition only within this illustration"},{"condition":"C09","status":"unresolved","reason":"unequal price; valuation routes unknown"},{"condition":"C10","status":"unresolved","reason":"branch evidence missing; method decision pending"}],"valuation_branch":"unknown","valuation_routes":[{"field":"identical_instrument_active_market_quote","value":null,"status":"unknown"},{"field":"technique_only_observable_market_data","value":null,"status":"unknown"}],"method_applicability":"unresolved","source_assessment":{"file":{"path":"docs/design/proposal/architecture/accounting-eligibility-fixtures-v1.json","sha256":"8d61ecfe4005d4652ead2f8a06d74b0340f4735ae83066fec7c19b0ab104c6f3"},"case_id":"E06"},"evidence_level":"conditional_synthetic_only","posting_permitted":false,"diagnostic_example":null}},"b1eb35dd439443566fcfc39645094d9cd3219a86cecf1f887c573e9bf668e35f":{"kind":"response","content":{"submission":"64d20a86908b0321a6b1ca7dfd8ed4d498cd76eadaca07deeecdd46357a0db7f","request":null,"status":"rejected","reason_codes":["INVALID_CONDITION_PACKET"],"assessment":null,"diagnostic_journal":null,"diagnostic_delta":null,"receipt":null,"observed_state":null,"commit_status":"not_committed","additional_commit":false,"statuses":{"structural_validity":"invalid","mathematical_status":"unresolved","computation_status":"not_computed","empirical_justification":"not_established","capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed","human_acceptance":"pending"},"metadata":{"response_id":"integration-E06","operation":"assess_only"}},"domain":"accdsl.accounting.integration.v1"},"bdd2f33d7a16aff19536f566c05ae8670f7e8923e210ffe9c77852d974b599e4":{"kind":"response","content":{"submission":"80b9409ba45c57e8781beaf730ddf1df16144d10ec784c654446ad7183ff81d6","request":null,"status":"rejected","reason_codes":["INVALID_UNKNOWN_REPRESENTATION","INVALID_CONDITION_PACKET"],"assessment":null,"diagnostic_journal":null,"diagnostic_delta":null,"receipt":null,"observed_state":null,"commit_status":"not_committed","additional_commit":false,"statuses":{"structural_validity":"invalid","mathematical_status":"unresolved","computation_status":"not_computed","empirical_justification":"not_established","capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed","human_acceptance":"pending"},"metadata":{"response_id":"integration-E06","operation":"assess_only"}},"domain":"accdsl.accounting.integration.v1"},"bfabaf4c687fd9bf6f30f0c07173038c82e7ec8ad2404252829078bf0134534f":{"kind":"request","content":{"schema_version":2,"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A","business_event_id":"integration-E06"},"event":"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f","opening":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","evidence":["f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028"],"admissions":["10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c"],"assumptions":"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","lineage":[{"file":{"path":"docs/design/proposal/methods/standards-fixtures-v1.json","sha256":"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798"},"locator":"acquisitions[id=A01]"}],"operation":"assess_only","eligibility":"99bac9fb82a55ae3bf65c7a7eff6799bcbd241f8d543a84822b91dd42f0445b3"},"domain":"accdsl.accounting.integration.v1"},"c1c98853cc8192823fe353068c70d760328faa4834c0404e02c4065148c08719":{"kind":"submission","content":{"wire_format":"ASCII_JSON","raw_text":"{\"admissions\":[\"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c\"],\"assumptions\":\"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"f6794fa664d2bdb039761d8db47a39b2675b465184fec864831f67de3ff7d5fb\",\"event\":\"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f\",\"evidence\":[\"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E06\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}"},"domain":"accdsl.accounting.integration.v1"},"c21fc6ae5892c5cb088cc6eb290bf7821a4b4841e8fa847d62e5682f97787810":{"kind":"submission","content":{"wire_format":"ASCII_JSON","raw_text":"{\"admissions\":[\"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c\"],\"assumptions\":\"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"009ab9863371a17fa943eaa3a46a3b80a15e754c4e95202e2d02ece3a1b6b6ff\",\"event\":\"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f\",\"evidence\":[\"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E06\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}"},"domain":"accdsl.accounting.integration.v1"},"c49976ea1709a278bfbee3b22cf87a07aad2f0b644adf8845fe3aa1f1d20a377":{"kind":"response","content":{"submission":"f6c80db388b4bbf5dae424ee449e2b31f706f0c8135578a0f9d294c7ede03059","request":"9d57a2b3eaae5c02eac0d11597f9494483c79e3e43f9db83b06ff6ffc72530b1","status":"assessed","reason_codes":["C09:unresolved","C10:unresolved"],"assessment":"3e71df06c1f530037f53937018977b28a27ba1f04bde42f2f8b5025cfc224035","diagnostic_journal":null,"diagnostic_delta":null,"receipt":null,"observed_state":null,"commit_status":"not_committed","additional_commit":false,"statuses":{"structural_validity":"valid","mathematical_status":"unresolved","computation_status":"specified_exact","empirical_justification":"not_established","capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed","human_acceptance":"pending"},"metadata":{"response_id":"integration-E06","operation":"assess_only"}},"domain":"accdsl.accounting.integration.v1"},"d0568d432de4230d3d86e0306214ffd281a3d24a9ecb5bb01f8d748eb33a20dd":{"kind":"request","content":{"schema_version":2,"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A","business_event_id":"integration-E06"},"event":"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f","opening":"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a","context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","evidence":["f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028"],"admissions":["10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c"],"assumptions":"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","lineage":[{"file":{"path":"docs/design/proposal/methods/standards-fixtures-v1.json","sha256":"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798"},"locator":"acquisitions[id=A01]"}],"operation":"assess_only","eligibility":"3cf81a06db6415b21ffdd037c5d44abe8d11122b1bf5c34ca0ba36eca72c63b1"}},"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae":{"kind":"assumptions","content":{"version":1,"eligibility":"unresolved","cash_settlement":true,"no_other_flows":true,"branch_admissibility":"stipulated","balance_sign":"debit_positive"}},"da38ce395c7aeb3142d684c9b98fe71f740d25d84be89b8c60708b9212b6defd":{"kind":"eligibility_input","content":{"schema_version":1,"profile":"acquisition-conditions-v1","dossier":{"path":"docs/design/proposal/architecture/accounting-eligibility-dossier-v1.md","sha256":"5b5fa718b997d53dc43530cf30b4451a78c06b6e0b468aaa28313e0027ba7f84"},"decision_rules":{"path":"docs/design/proposal/architecture/accounting-eligibility-decision-supplement-v1.md","sha256":"b3fde2435f6ce4de3386a884321fed5b1a93a0b26d49da4f3f8b1eb31f942d46"},"source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X202"},"bindings":{"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","assumptions":"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","evidence":["f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028"],"admissions":["10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c"]},"aliases":{"scope":"synthetic_only","source_labels":{"entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission"},"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A"},"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e"},"conditions":[{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X202"},"condition_id":"C01","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X202"},"condition_id":"C02","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X202"},"condition_id":"C03","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X202"},"condition_id":"C04","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X202"},"condition_id":"C05","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X202"},"condition_id":"C06","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X202"},"condition_id":"C07","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X202"},"condition_id":"C08","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X202"},"condition_id":"C09","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X202"},"condition_id":"C10","value_version":"eligibility-example-v1"}]},"domain":"accdsl.accounting.integration.v1"},"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f":{"kind":"event","content":{"business_event_id":"integration-E06","version":1,"kind":"cash_acquisition","context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","price":"100.00","fair_value":"105.00","fee":"2.00","category":"FVTPL"}},"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692":{"kind":"method","content":{"version":1,"name":"synthetic-A01-acquisition","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","rounding":"exact_two_decimal_reject_extra_precision","formula":"asset=price=fair_value; expense=fee; cash=-(price+fee); equity=0","scope":"A01 only; A03 requires resolution of valuation evidence before measurement"}},"e9a7c404613183ccd62033d0ccd47fd315970afde5d798671c83e5419dd2b975":{"kind":"event","content":{"business_event_id":"integration-E01","version":1,"kind":"cash_acquisition","context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","price":"100.00","fair_value":"100.00","fee":"2.00","category":"FVTPL"}},"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028":{"kind":"evidence","content":{"version":6,"source":{"file":{"path":"docs/design/proposal/methods/standards-fixtures-v1.json","sha256":"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798"},"locator":"acquisitions[id=A01]"},"source_case":"A03","nature":"synthetic","observable_valuation":{"status":"unknown","reason":"not required or qualifying route unresolved; see C09"}}},"f6794fa664d2bdb039761d8db47a39b2675b465184fec864831f67de3ff7d5fb":{"kind":"eligibility_input","content":{"schema_version":1,"profile":"acquisition-conditions-v1","dossier":{"path":"docs/design/proposal/architecture/accounting-eligibility-dossier-v1.md","sha256":"5b5fa718b997d53dc43530cf30b4451a78c06b6e0b468aaa28313e0027ba7f84"},"decision_rules":{"path":"docs/design/proposal/architecture/accounting-eligibility-decision-supplement-v1.md","sha256":"b3fde2435f6ce4de3386a884321fed5b1a93a0b26d49da4f3f8b1eb31f942d46"},"source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K01"},"bindings":{"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","assumptions":"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","evidence":["f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028"],"admissions":["10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c"]},"aliases":{"scope":"synthetic_only","source_labels":{"entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission"},"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A"},"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e"},"conditions":[{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K01"},"condition_id":"C01","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K01"},"condition_id":"C02","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K01"},"condition_id":"C03","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K01"},"condition_id":"C04","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K01"},"condition_id":"C05","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K01"},"condition_id":"C06","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K01"},"condition_id":"C07","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K01"},"condition_id":"C08","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K01"},"condition_id":"C09","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"K01"},"condition_id":"C10","value_version":"eligibility-example-v1"}]},"domain":"accdsl.accounting.integration.v1"},"f6c80db388b4bbf5dae424ee449e2b31f706f0c8135578a0f9d294c7ede03059":{"kind":"submission","content":{"wire_format":"ASCII_JSON","raw_text":"{\"admissions\":[\"10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c\"],\"assumptions\":\"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae\",\"authority\":\"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce\",\"branch\":\"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e\",\"chart\":\"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a\",\"context\":\"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f\",\"eligibility\":\"6298680567179a51f9610908611ac8a03af8e8ce6dbcedbcb10932950027237c\",\"event\":\"e077cf3b235ee0e9383f16338e01b0b1e399baf6d8c270582bddfe4fd975bd1f\",\"evidence\":[\"f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028\"],\"identity\":{\"book_id\":\"illustrative-book\",\"branch_id\":\"A\",\"business_event_id\":\"integration-E06\",\"entity_id\":\"example-company\"},\"lineage\":[{\"file\":{\"path\":\"docs/design/proposal/methods/standards-fixtures-v1.json\",\"sha256\":\"abc88bf75ded39516f43db0fdb45b9a905609ea11543072f7411540f33fd0798\"},\"locator\":\"acquisitions[id=A01]\"}],\"method\":\"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692\",\"opening\":\"0cdfd167f0919ce3b4dd24c9616ab633d031d2c7f4bf7b54cb7a5aceab35f39a\",\"operation\":\"assess_only\",\"schema_version\":2,\"time\":\"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0\"}"},"domain":"accdsl.accounting.integration.v1"},"f7aa17bc8600b8414f21cd3622eb489e294d97a37f735e2966ec7b6230972546":{"kind":"response","content":{"submission":"1954e381849038b491354b6602a9d1e3dc8484d451e97a6b8776947491a1df3b","request":"11724d4569dd9bed11351cbc1e1e8fbe6bbab843d0b25c373a833a6b820bbf53","status":"assessed","reason_codes":[],"assessment":"8c685bf8d8a1575488a363a7f3cbf93ba966b19c9845af1000a547ab75c445a1","diagnostic_journal":null,"diagnostic_delta":null,"receipt":null,"observed_state":null,"commit_status":"not_committed","additional_commit":false,"statuses":{"structural_validity":"valid","mathematical_status":"unresolved","computation_status":"specified_exact","empirical_justification":"not_established","capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed","human_acceptance":"pending"},"metadata":{"response_id":"integration-E01","operation":"assess_only"}}},"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0":{"kind":"time","content":{"economic_date":"2024-06-03","reporting_start":"2024-01-01","reporting_end":"2024-12-31","source_cutoff":"2026-10-05T00:00:00Z","review_cutoff":"2026-10-05T00:00:00Z","view":"restated","basis":"synthetic_scenario"}},"ff6025ba31f7d4d28bbd04046edb5ec51b05073fd070cc7606140c566bf67a2a":{"kind":"eligibility_input","content":{"schema_version":1,"profile":"acquisition-conditions-v1","dossier":{"path":"docs/design/proposal/architecture/accounting-eligibility-dossier-v1.md","sha256":"5b5fa718b997d53dc43530cf30b4451a78c06b6e0b468aaa28313e0027ba7f84"},"decision_rules":{"path":"docs/design/proposal/architecture/accounting-eligibility-decision-supplement-v1.md","sha256":"b3fde2435f6ce4de3386a884321fed5b1a93a0b26d49da4f3f8b1eb31f942d46"},"source_case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X008"},"bindings":{"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e","time":"fbbf380ce6878212a290ca1dd660701e7d5c1157385079762333e260741be0c0","chart":"48d2ecbe2e2c7a1f554a012665e6debd45191801f618a0d435e1001b58b86a3a","authority":"abca03c2ebe2085be99c8491949df7c485c63edac58577451278e15543e4e6ce","method":"e31ea0ce154f4c958f645222fe934220d876c81bb0a1404900b00830cc12b692","assumptions":"d538cbd49abb64d3ce1e73f843d85e60def88d65687a07fb76590a1ccabdd9ae","evidence":["f04de569c0066f2b8d68ea5be05c95c61dbc94cd50676f598d20ec27f40da028"],"admissions":["10e8d1447d41734e14fb298f8c4bfa8ced3c6da50ab7eac040ea686b7e20b27c"]},"aliases":{"scope":"synthetic_only","source_labels":{"entity":"synthetic purchaser","book":"synthetic own book","branch":"stipulated admissible A01 branch, not historical admission"},"identity":{"entity_id":"example-company","book_id":"illustrative-book","branch_id":"A"},"context":"76c3a5350809fa1f2014cad52da5ad3de75be75830f620f3fbd2a70148ba974f","branch":"7358954368e347c611b6eb61ee9233150dd79b5c0bd03261c17c6e6f0080e56e"},"conditions":[{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X008"},"condition_id":"C01","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X008"},"condition_id":"C02","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X008"},"condition_id":"C03","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X008"},"condition_id":"C04","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X008"},"condition_id":"C05","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X008"},"condition_id":"C06","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X008"},"condition_id":"C07","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X008"},"condition_id":"C08","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X008"},"condition_id":"C09","value_version":"eligibility-example-v1"},{"case":{"file":{"path":"docs/design/proposal/architecture/accounting-complete-source-packets-v1.json","sha256":"ee072fbf8b696b048ffb460292d5587e6ea5d59bb987692db72dad3a8c9e5497"},"case_id":"X008"},"condition_id":"C10","value_version":"eligibility-example-v1"}]},"domain":"accdsl.accounting.integration.v1"}}}

NORTHSTAR ACTUAL PROTECTED INPUT/EXPECTED FIXTURE:
{"schema":"accdsl-design-fixture/1","entity":"Northstar Components (synthetic)","currency":"USD","units":"one currency unit","basis":"DemoCorporate/1; not GAAP certification","disclosure_scope":"Closed synthetic goods company; the listed source package is complete by construction","assumptions":{"historical_resolution":"half-year aggregate flows; existence of intraperiod schedules required, not recovered invoices","inventory":"one homogeneous good at cost 5; purchases before delivery; quantities equal costs/5","sales":"delivery transfers control; no returns, services, variable consideration or foreign currency","tax":"20% positive taxable profit, all expenses deductible, no deferred tax; excess payment is prepaid tax","plant":"opening cost 100, annual depreciation 10; end-H1 addition 10 lives 5 years; end-H2 addition 12 lives 12 years; zero residuals","debt":"100 throughout; fixed and floating both 5% in 2024; fixed 5%, floating resets to 7% in 2025; all maturities after forecast","time":"half-year accrual fractions 1/2, annual 1; explicit teaching convention","closing":"temporary accounts closed after each H1/H2; annual income uses movements excluding closing","universe":"no omitted company, OCI, acquisition, tax or off-balance-sheet operations inside this synthetic package"},"accounts":{"cash":"asset","receivables":"asset","inventory":"asset","plant_cost":"asset","accum_depreciation":"contra_asset","tax_prepaid":"asset","payables":"liability","debt":"liability","capital":"equity","retained":"equity","revenue":"income","cost_of_sales":"expense","payroll":"expense","depreciation":"expense","interest":"expense","tax":"expense"},"opening":{"cash":"60","receivables":"20","inventory":"30","plant_cost":"100","accum_depreciation":"-20","tax_prepaid":"0","payables":"-20","debt":"-100","capital":"-50","retained":"-20"},"historical_events":[{"id":"2024H1.sale","date":"2024-06-30","period":"2024H1","postings":[{"account":"receivables","signed_amount":"110"},{"account":"revenue","signed_amount":"-110"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.collect","date":"2024-06-30","period":"2024H1","postings":[{"account":"cash","signed_amount":"110"},{"account":"receivables","signed_amount":"-110"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.buy","date":"2024-06-30","period":"2024H1","postings":[{"account":"inventory","signed_amount":"70"},{"account":"payables","signed_amount":"-70"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.supplier","date":"2024-06-30","period":"2024H1","postings":[{"account":"payables","signed_amount":"65"},{"account":"cash","signed_amount":"-65"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.deliver","date":"2024-06-30","period":"2024H1","postings":[{"account":"cost_of_sales","signed_amount":"75"},{"account":"inventory","signed_amount":"-75"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.wages","date":"2024-06-30","period":"2024H1","postings":[{"account":"payroll","signed_amount":"20"},{"account":"cash","signed_amount":"-20"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.plant","date":"2024-06-30","period":"2024H1","postings":[{"account":"plant_cost","signed_amount":"10"},{"account":"cash","signed_amount":"-10"}],"cash_class":"investing","state_changes":{}},{"id":"2024H1.depreciate","date":"2024-06-30","period":"2024H1","postings":[{"account":"depreciation","signed_amount":"5"},{"account":"accum_depreciation","signed_amount":"-5"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.interest","date":"2024-06-30","period":"2024H1","postings":[{"account":"interest","signed_amount":"2.5"},{"account":"cash","signed_amount":"-2.5"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.tax","date":"2024-06-30","period":"2024H1","postings":[{"account":"tax","signed_amount":"1.5"},{"account":"tax_prepaid","signed_amount":"2"},{"account":"cash","signed_amount":"-3.5"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.dividend","date":"2024-06-30","period":"2024H1","postings":[{"account":"retained","signed_amount":"4"},{"account":"cash","signed_amount":"-4"}],"cash_class":"financing","state_changes":{}},{"id":"2024H2.sale","date":"2024-12-31","period":"2024H2","postings":[{"account":"receivables","signed_amount":"150"},{"account":"revenue","signed_amount":"-150"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.collect","date":"2024-12-31","period":"2024H2","postings":[{"account":"cash","signed_amount":"135"},{"account":"receivables","signed_amount":"-135"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.buy","date":"2024-12-31","period":"2024H2","postings":[{"account":"inventory","signed_amount":"85"},{"account":"payables","signed_amount":"-85"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.supplier","date":"2024-12-31","period":"2024H2","postings":[{"account":"payables","signed_amount":"80"},{"account":"cash","signed_amount":"-80"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.deliver","date":"2024-12-31","period":"2024H2","postings":[{"account":"cost_of_sales","signed_amount":"90"},{"account":"inventory","signed_amount":"-90"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.wages","date":"2024-12-31","period":"2024H2","postings":[{"account":"payroll","signed_amount":"22"},{"account":"cash","signed_amount":"-22"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.plant","date":"2024-12-31","period":"2024H2","postings":[{"account":"plant_cost","signed_amount":"12"},{"account":"cash","signed_amount":"-12"}],"cash_class":"investing","state_changes":{}},{"id":"2024H2.depreciate","date":"2024-12-31","period":"2024H2","postings":[{"account":"depreciation","signed_amount":"6"},{"account":"accum_depreciation","signed_amount":"-6"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.interest","date":"2024-12-31","period":"2024H2","postings":[{"account":"interest","signed_amount":"2.5"},{"account":"cash","signed_amount":"-2.5"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.tax","date":"2024-12-31","period":"2024H2","postings":[{"account":"tax","signed_amount":"5.9"},{"account":"tax_prepaid","signed_amount":"-2"},{"account":"cash","signed_amount":"-3.9"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.dividend","date":"2024-12-31","period":"2024H2","postings":[{"account":"retained","signed_amount":"5"},{"account":"cash","signed_amount":"-5"}],"cash_class":"financing","state_changes":{}}],"expected":{"2024H1":{"cash":"65","receivables":"20","inventory":"25","plant_net":"85","tax_prepaid":"2","assets":"197","payables":"25","debt":"100","equity":"72","revenue":"110","profit":"6","operating_cash":"19","investing_cash":"-10","financing_cash":"-4"},"2024H2":{"cash":"74.6","receivables":"35","inventory":"20","plant_net":"91","tax_prepaid":"0","assets":"220.6","payables":"30","debt":"100","equity":"90.6","revenue":"150","profit":"23.6","operating_cash":"26.6","investing_cash":"-12","financing_cash":"-5"},"2024FY":{"revenue":"260","profit":"29.6","operating_cash":"45.6","investing_cash":"-22","financing_cash":"-9","cash_change":"14.6"},"2025_fixed":{"cash":"95.2","receivables":"55","inventory":"40","plant_net":"98","tax_prepaid":"0","assets":"288.2","payables":"40","debt":"100","equity":"148.2","revenue":"300","profit":"65.6","interest":"5","tax":"16.4","operating_cash":"48.6","investing_cash":"-20","financing_cash":"-8"},"2025_floating":{"cash":"93.6","receivables":"55","inventory":"40","plant_net":"98","tax_prepaid":"0","assets":"286.6","payables":"40","debt":"100","equity":"146.6","revenue":"300","profit":"64","interest":"7","tax":"16","operating_cash":"47","investing_cash":"-20","financing_cash":"-8"}},"forecast":{"start":"2025-01-01","end_exclusive":"2026-01-01","demand_units":"30","price":"10","unit_cost":"5","target_inventory_units":"8","current_sales_collection_fraction":"0.9","legacy_receivable_collections":"10","old_payables_paid":"30","new_purchases_paid":"130","payroll":"50","capex_at_period_end":"20","dividend":"8","tax_rate":"0.2","funding_limit":"0"},"coverage_units":[{"id":"NS.opening","kind":"statement","disposition":"structured","content":"Opening balance sheet and account balances"},{"id":"NS.h1.original","kind":"statement","disposition":"superseded_reading_preserved","content":"Originally revenue 120, receivables 30, tax expense/payment 3.5, profit 14, equity 80"},{"id":"NS.h1.correction","kind":"note","disposition":"structured","content":"Premature invoice 10: reverse revenue and receivable; reduce tax expense 2 into tax prepayment; corrected profit 6"},{"id":"NS.fy","kind":"statement","disposition":"structured","content":"Annual and revised interim statements derived from listed events"},{"id":"NS.operations","kind":"policy","disposition":"structured","content":"Goods, inventory, asset and working-capital assumptions above"},{"id":"NS.debt","kind":"note","disposition":"alternative_family","content":"Principal 100, interest 5; fixed/floating composition undisclosed"},{"id":"NS.equity","kind":"note","disposition":"structured","content":"Capital 50; original retained 20; dividends H1 4, H2 5"},{"id":"NS.reference","kind":"cross_reference","disposition":"resolved","target":"NS.debt","content":"Financing note applies to debt and interest in every statement"}]}

FILE: docs/design/proposal/architecture/evidence-contract-v3.md (complete)
# Evidence contract v3 — proposed semantics

This contract addresses MC01–MC04 and the admission boundary of MC27
(G2/G11/G17). It specifies evidence preparation for the whole product, including
later group, bank, insurance and cross-standard work. It does not select an
initial product profile. P15-E01–E03 receive concrete proposed answers; E05
still needs a real conflicting-disclosure walkthrough. Examples are in
`evidence-fixtures-v3.json`. Synthetic text is identified there and supplies
no accounting authority.

## E1. Input and output records

An input `SourceVersion` contains immutable original bytes, their SHA-256,
media type, source URL or original local origin, acquisition event, issuer,
document identity/version, and publication evidence. An extracted text file is
a separate derivative with its own hash, extraction method/version and link to
the original. Reacquiring different bytes creates a new version even if the URL
is unchanged. A URL, matching title or current download does not establish the
bytes available at an earlier date. The time contract determines that claim.

A `UnitOccurrence` identifies one source version and a locator: PDF physical
page plus printed page and bounding region where available; HTML element or
XBRL fact/context identifiers; text line/character span in a pinned extraction.
Locators retain table headings, footnotes and continuation links needed for
meaning. A text locator alone does not establish faithful PDF extraction.
Units identify parent section, annual/quarterly/semiannual package root, and
disposition. An occurrence is never deleted because another occurrence has the
same text. Byte-identical span content may share a content ID; semantic
equivalence additionally requires compatible context and an explicit review.

A `ReportedAssertion` links every supporting occurrence and preserves literal
text/value. An `ExtractionReading` identifies a candidate reading and its
review events. An `Interpretation` identifies the exact extraction versions,
financial scope, dependencies, modality and proposed meaning. A `Derivation`
records input versions, expression, result context and assumptions. An
`Assumption` has an author, rationale, scope and alternatives and cannot be
labelled issuer evidence. A `Conflict` links incompatible candidates and their
affected queries; conflicting faithful readings both survive.

Preparation returns (1) immutable source and reading records, (2) a package
coverage report with three separate populations, (3) proposed, admitted and
unresolved predicates, (4) query-specific evidence exposure, and (5) typed
issues containing record IDs, locators, dependencies and repair actions.
Every output identifies the evidence view and review snapshot. Neither an
extraction confidence score nor review acceptance supplies a probability over
company histories.

## E2. Package closure and three populations

Start with declared annual, quarterly and semiannual roots, dates, included
sections and expected statement/note indexes. Reconcile contents with actual
headings and tables, then follow references within the declared material scope.
A reference edge retains its source locator, target description, candidates,
resolution evidence and disposition. The permitted dispositions in these
fixtures are `resolved`, `duplicate_verified`, `cycle_closed`,
`missing_continuation`, `ambiguous_target`, `unavailable_target`, and
`resource_exhausted`. A verified cycle stops repeated traversal; its target must
exist and the closing edge remains visible. Similar names alone cannot resolve
an ambiguous target. A budget limit retains the unvisited frontier and the
limit reached, never an empty-success result.

The acquired-unit population counts retained occurrences and unique contents
separately. Its denominator is the declared inventory, with discovered missing
targets and unknown inventory extent reported alongside it. Parent and child
units cannot both contribute to a count of nonoverlapping leaf spans. A repeated
paragraph contributes two occurrence locators but one content body; this does
not merge assertions applying to different dates or entities.

The reviewed-assertion population counts identified assertion candidates at a
named layer, once per contextual assertion identity. It reports accepted,
rejected, pending and unresolved counts and aliases explicitly. It also retains
unread/unstructured source units, whose unknown assertion count cannot be
treated as zero. A denominator of six discovered candidates means six candidates
reviewed to some disposition, not six assertions in the whole real report.

The query-exposure population is the declared query set and each query's
transitive evidence dependencies. Each query is `supported`, `conditional`,
`unresolved`, or `unsupported` for its requested claim. `supported` means the
specified evidence-reading operation has met its admission rules, not that the
issuer's report is true or compliant. `conditional` requires explicit selected
assumptions; an unselected assumption leaves the query unresolved. Missing or
ambiguous references block only dependent claims, but uncertain relevance must
be reported as an unresolved dependency until reviewed. An unaffected disclosed
revenue lookup can succeed while debt-exposure reconstruction remains unresolved.

Package closure requires no unresolved material references, reconciled inventory
and a documented scope/materiality decision for exclusions. Semantic completion
additionally requires every in-scope unit to have its assertions and unresolved
meaning accounted for. Three root files, all retained known units, or a high
review count cannot establish either condition. The synthetic fixture has seven
occurrences, five unique contents, six contextual assertion candidates, seven
reference edges and five queries; its four unresolved edges veto package closure.

## E3. Numeric context and faithful display

A numeric reading includes legal entity and perimeter/version, concept and
mapping version, dimensions, instant or half-open reporting interval, fiscal
calendar/version, currency, unit, scale, sign convention, measurement basis,
reported lexeme, display decimals, and separately the rounding convention and
tie rule with their source or assumption references. Unknown fields are tagged
unknown, not supplied by a global currency/calendar default. Zero, missing,
not-applicable and a printed dash are distinct; a dash becomes zero only under
a supported interpretation.

For a reported lexeme 364,980 with USD and a million scale, the exact *scaled
displayed value* is 364,980,000,000 USD. That is not a claim that the issuer's
underlying unrounded amount equals it. Rendering must reproduce the lexeme,
scale label, sign convention and precision, including parentheses, without
round-tripping through binary floating point. Derived displays retain their
expression and do not masquerade as original disclosure.

For arithmetic, currencies, dimensions, bases, perimeters and concepts must
match or have an admitted explicit conversion/mapping. Flows require compatible
nonoverlapping intervals for addition; stocks are not summed over dates.
YTD subtraction follows T5 in the time contract. Mismatches return
`INCOMPATIBLE_CONTEXT`; unknown compatibility returns `UNRESOLVED_CONTEXT`.
Permissive archival display is possible without authorising arithmetic.

If source evidence establishes rounding to nearest unit u, a displayed value d
has interior compatibility d-u/2 < x < d+u/2. Endpoint membership follows the
specified tie rule. For ties-to-even, displayed integer 120 admits both half-unit
endpoints; 121 admits neither. With nearest established but tie rule unknown,
the closed interval is only an outer enclosure: both endpoint memberships are
unresolved. A query requiring exact endpoint feasibility must return unresolved.
If even the nearest convention is unknown, displayed precision alone supplies
no such interval. A user may explicitly choose assumption `nearest-model-v1`;
its interval and every dependent result then remain conditional. None of these
intervals supplies a distribution. P02's closed half-unit model is evidence of
a prior compatibility assumption, not issuer confirmation of that convention.

## E4. Narrative interpretation and admission

A narrative interpretation binds subject/entity, contract or instrument set,
valid dates, quantifier, modality (`reported_fact`, `permission`,
`conditional_obligation`, `policy`), predicate, exceptions, dependent facts and
affected quantities. Missing scope is unresolved, not universal. Literal wording
is retained even when no executable predicate is available.

“May repurchase up to 50” permits an action in the specified period and currency;
it imposes neither a purchase nor a payment. A selected scenario may add an
exercise decision and resulting cash flow, separately attributed as an
assumption. “Pays if borrower defaults” preserves the condition; with default
unknown it cannot become an unconditional payable. “Substantially all” supplies
no 95% threshold. A proposed threshold must be a named modelling assumption
and cannot replace the retained qualitative claim.

The source-backed Apple example uses Note 9 of the 2024 10-K (physical page 46, printed page 43),
the fixed-rate debt table and the adjacent swap paragraph. The coupon
classification applies to notes. The paragraph says certain USD notes are
effectively converted to floating rates by swaps; it does not identify each
instrument allocation here. Preserve a combined exposure query as unresolved
pending allocation and terms. Reject a translation stating all combined
note-and-swap cash flows are fixed. The adjacent Note 4 wording “may use” is a
policy/permission description, not evidence that every instrument is hedged.
These passages are compatible qualifications, not a genuine source conflict.

Review events name target ID/version, layer, action, reviewer/time and reason.
At each layer a candidate progresses `proposed -> accepted | rejected |
unresolved`. A new alternative starts at proposed. A correction creates a new
candidate and an explicit supersession link; it does not overwrite source bytes
or retroactively change old review snapshots. Rejected/unresolved candidates
can be reconsidered only by a new recorded decision. Extraction acceptance
means faithful reading; interpretation acceptance means accepted scoped meaning;
accounting admission additionally requires applicable treatment authority,
context and rule/version. No transition automatically accepts a higher layer.

Read-only disclosed-value queries can use accepted extraction and context.
Constraint queries require an accepted interpretation, admitted translation,
resolved predicates or explicit conditional assumptions. Posting requests also
require accounting admission. Dependency corrections invalidate current use of
transitive descendants; old results remain retrievable under their old evidence
view with a current superseded warning. Unrelated descendants stay usable.
The storage transaction and identity mechanics remain a later P16 contract.

## E5. Failure, alternatives and interaction obligations

Integrity mismatch or dangling required source IDs rejects the affected
record; missing meaning produces a retained unresolved record. A conflicting
accepted pair returns both alternatives plus affected-query status, never
last-write-wins. Unsupported translations return `UNSUPPORTED_PREDICATE` with
the original text. Resource limits return partial inventories and unfinished
frontiers; they cannot certify impossibility or complete coverage.

The main alternative is one aggregate completeness score. It is simpler to
display but hides missing contracts behind parsed pages; separate populations
are proposed because each answers a different question. Another alternative
lets accepted free text constrain a model implicitly. Explicit scoped admission
costs annotation work but prevents permissions, exceptions and qualitative
terms from acquiring invented mathematical meaning. Automatically inferring
nearest rounding is convenient but overstates source support; prohibiting all
conditional analysis is unnecessarily restrictive. Separate source facts and
named assumptions support both faithful reporting and useful conditional work.

Time supplies eligible source/review versions; history families receive admitted
constraints and unresolved predicates without manufactured weights; accounting
receives evidence plus authority requirements; language/IR must preserve every
scope and assumption; persistence must retain immutable versions and dependency
invalidation; interfaces must expose all three coverage populations and reasons.
Those counterpart contracts remain unfinished. Independent substantive review,
a real conflicting-disclosure case and later domain authority work are required
before closing E05 or the wider mission gaps.

## Revision record

v2 retains the v1 contract semantics and points to the corrected fixture set.
E-display describes assets and now names its sign convention `positive_assets`;
the v1 revenue sign label was wrong for that context. The scaled displayed
amount remains 364,980,000,000 USD. No source statement was changed.

## v3 source-locator correction

Original PDF inspection in e05-source-investigation-v1.md corrects the Note 9
locator. No substantive admission rule or expected output has changed; v3 fixtures
correct the same locator and remain the examples for E1–E5. E05 source evidence remains insufficient.

FILE: docs/design/proposal/architecture/time-contract-v2.md (complete)
# Time contract v2 — proposed semantics

This contract addresses MC05 with MC04/MC25/MC27 interactions (G13/G17/G18).
It supplies the proposed answer to P15-E04. Its fixtures are specification
examples, not a runtime implementation. The existing P06 chronology selector
is a counterexample where it substitutes availability for absent ingestion and
allows unverified historical bytes by default. Neither behaviour is adopted
for a claim requiring the missing evidence.

## T1. Records and query dimensions

An assertion version identifies economic instant or event dates, reporting
interval and calendar, public availability evidence, ingestion event, review
events, source byte hash and evidence of byte vintage. These are different
clocks. A payment date does not establish recognition time; reporting period
end does not establish publication. A later acquisition may preserve bytes
known to have been public earlier without establishing system possession then.

Economic and reporting periods use ISO calendar dates and explicit calendar
versions; flow intervals are [start, end_exclusive). Timestamp comparisons use
timezone-aware instants converted to UTC. Preserve the original timezone,
precision and source representation. Missing timezone rejects an instant
comparison (`MISSING_TIMEZONE`); it never means the machine's local zone.
Absent ingestion and explicit-null ingestion are separate diagnostic states,
`INGESTION_ABSENT` and `INGESTION_UNKNOWN`, but neither establishes an instant.

A query specifies `admission_mode`, `selection`, economic/reporting target,
information cutoff when applicable, system-as-of when applicable, review
snapshot, requested layer, and calendar/perimeter/measurement basis. Selection
is `original`, `latest_available`, or `harmonised`. No selection overrides
admission. Omitted required cutoffs or a nonexistent review snapshot reject the
request, rather than silently choosing today's data. Outputs contain selected
IDs, known exclusions/reasons, unresolved candidates/dependencies, derivation
lineage, assumptions, and claim status. Historical simulation receives only
admitted evidence; diagnostic knowledge of later rejected IDs belongs in the
audit output and must not become scenario input.

## T2. Three admission modes

`archival_exploration` allows inspection of retained bytes, including unknown
publication or ingestion. Such rows are labelled `historical_admissibility:
unestablished`. With a cutoff and unknown publication they may be displayed only
as unresolved archival candidates, not as cutoff-qualified selections. Without
a cutoff all retained rows may be selected under explicit lineage rules, but
the result remains archival; no historical knowledge claim follows. Source
integrity checks still apply. Exploration does not authorise accounting posting.

`investor_information` requires information cutoff K, supported public
availability at or before K, and evidence linking the exact selected source
bytes to that availability. Later ingestion is permitted. Unknown publication,
unverified historical bytes or date precision straddling K leaves a candidate
unresolved and excludes it from the admitted set. Known publication after K
is a definite exclusion. An accepted extraction performed later may read an
eligible old document using an explicitly chosen review snapshot. Any derived
interpretation that consumes later information is inadmissible for a historical
decision rule; its full information dependencies must pass K separately.
This view establishes public availability of evidence, not actual investor
awareness or a tradeable execution opportunity.

`system_as_of` requires S and an immutable receipt proving exact bytes were
ingested no later than S. Ingestion cannot be inferred from publication. The
requested accepted layer additionally needs review decisions visible by S;
later review cannot be projected back. Retained raw evidence may be returned
with its then-unreviewed status if the requested layer is raw. System possession
alone does not establish public availability. If a query also requests an
investor cutoff K, it must satisfy both filters, including public byte-vintage
evidence. Unknown publication alone need not block a *pure* system-possession
query. This separation permits later legitimate private/local records without
claiming that they were public.

A known later revision is excluded by its actual time; it does not suppress
an earlier eligible assertion. An unresolved potentially relevant version
keeps a result unresolved even if an older candidate is selected. Unaffected
keys retain supported results. `unresolved` is different from an empty set
proved to contain no eligible records.

## T3. Date-only evidence and byte verification

A publication date D with named timezone Z denotes an interval from local
midnight D through (but excluding) the next local midnight. The physical
instant is unknown within it. If K is before the interval, exclude the record;
if K is inside, return `PUBLICATION_PRECISION_UNRESOLVED`; if K is at or after
the interval's exclusive upper boundary, admission is supported by that date
evidence. This is a conservative availability convention, not a claim that
publication occurred at midnight. No fixed 24-hour duration is assumed across
daylight-saving changes. Missing Z keeps the interval unresolved. Conflicting
publication sources remain alternatives until resolved; choose neither the
earliest nor latest silently.

An ingestion date without an instant similarly proves only bounded possession;
queries inside the date remain unresolved. Review date precision is treated
the same way. A receipt must bind timestamp evidence, source ID and byte hash;
`ingested_at` alone without a receipt is `INGESTION_RECEIPT_UNVERIFIED`.
Public byte-vintage evidence and system receipt evidence are different proofs.
Current byte integrity failure is a hard rejection (`SOURCE_HASH_MISMATCH`),
whereas missing historical linkage is unresolved. An issuer timestamp on a
current webpage cannot by itself prove unchanged historical bytes.

## T4. Selection, supersession and review state

Supersession edges identify assertion IDs and the exact concept, period,
perimeter and dimensions replaced, plus supporting evidence. The graph must be
acyclic and targets must exist; a cycle or missing target rejects the affected
lineage. A document-wide replacement is not inferred from one corrected fact.
Duplicated content with no assertion change remains an alias with its original
lineage. Distinct same-date records need a supported ordering or a retained
conflict; IDs and filesystem order never break a semantic tie.

`original` returns eligible root assertions for each requested key. A later
revision is not an original merely because its root is unavailable. Multiple
unrelated roots remain competing assertions. `latest_available` returns eligible
assertions with no eligible admitted descendant superseding them for that key.
Only the eligible graph may remove an older record; future review acceptance
or later ingestion has no backward effect. If an eligible descendant's
intermediate ancestor is known but ineligible, the supported transitive edge
can still establish replacement; missing graph evidence cannot. Multiple live
leaves for the same exact quantity produce `CONFLICTING_VERSIONS` and remain
visible, rather than being averaged.

`harmonised` starts from latest eligible records and applies explicit admitted
transforms to a declared target basis, calendar and perimeter. Each transform
states input IDs, formula, authority/assumption support, review snapshot and
information dependencies. The output is a derived reading with a new ID;
original rows and their labels are preserved. Transform availability must pass
the same admission rules as other dependencies. Missing authority or a missing
opening bridge returns `HARMONISATION_UNSUPPORTED`; it does not relabel an old
number as comparable. An algebraic synthetic transform tests lineage only.

## T5. Period arithmetic and change treatments

Subtract YTD A from longer YTD B only when concept, unit, currency, measurement
basis, perimeter, calendar, interval start, aggregation dimensions and evidence
revision compatibility match. The shorter interval must be a proper prefix.
The remainder is [A.end_exclusive, B.end_exclusive). Same vintage labels are
not sufficient if other context differs. Different vintage labels require a
specific admitted compatibility bridge covering the fact, not general claims
that both reports are audited. Original selection may return H1-v1 and FY-v2
for display while arithmetic between them is rejected.

The synthetic retained example is H1-v1 = 120, revised H1-v2 = 110, FY-v2 = 260.
Compatible subtraction gives H2-v2 = 260 - 110 = 150. Subtracting 120 gives
140 arithmetically but fails the compatibility contract, so the financial query
returns no H2 value. A 52/53-week calendar change or a changed group perimeter
also requires an explicit bridge; endpoints alone cannot establish comparability.

An extraction correction changes the reading of unchanged source bytes; issuer
revision changes the reported assertion; an estimate update changes prospective
model inputs; a policy/error correction may require retrospective treatment.
The time contract requires change kind, authority/rule version, effective date,
affected periods/accounts, opening-balance bridge, transition method and review
evidence. It does not determine the standards-specific classification. Missing
authority returns `TREATMENT_UNSUPPORTED` and preserves original/revised views.
No fixture here certifies IFRS, US GAAP or ASBE retrospective/prospective rules;
P17 must supply the supporting methods and authoritative cases.

## T6. Alternatives, invariants and interactions

Permissive fallback makes archival data easier to query but cannot establish
system history: two systems can ingest the same public filing on different
days. Strict receipt-based system admission and separately qualified exploration
are therefore proposed. Treating all missing publication data as fatal to every
operation would wrongly prevent a supported system-possession query. Combining
admission and revision selection in one “latest” switch hides these differences.
The proposed orthogonal fields make the requested historical claim explicit.

For date-only publication, start-of-day admission is convenient but admits
possible future information during that day. End-of-interval admission is
conservative and preserves the unknown instant. An arbitrary noon default is
unjustified. Exact research backtests requiring intraday availability must obtain
better evidence or leave those observations unresolved.

For every selection, selected and definitely excluded IDs are disjoint; selected
IDs can coexist with unresolved competitors, in which case the affected claim
is unresolved. Hashes and old views are immutable; a correction invalidates
current dependent results without rewriting historical records. Increasing K
may legitimately change latest selected values, so value monotonicity is not
an invariant. Eligibility grows only if the evidence/review snapshot and other
filters stay fixed. No view claims the issuer's assertions are economically true.

Evidence supplies immutable versions and layer decisions; history/uncertainty
must retain live alternatives; accounting supplies transition authority and
opening bridges; language/IR must serialize cutoffs, intervals and required
contexts; persistence supplies receipts, immutable snapshots and transitive
invalidation; interfaces expose unavailable versus unresolved versus unsupported
outcomes. Full definitions of those interfaces, identity/replay and domain
treatment remain later contracts. Human acceptance remains pending.

## Revision record and fixture conventions

The current examples are `time-fixtures-v2.json`; v1 remains preserved.
The harmonisation example previously expected a conditional result despite an
empty request assumption list. That is wrong relative to E2's explicit-selection
rule. v2 selects `bridge-assumed`, records accepted synthetic review and byte
support for the transform, and names its information dependency. A transform
with an unselected required assumption must remain unresolved, with no admitted
derived value. An assumption ID is selected only by its presence in the request's
`assumptions` list; merely appearing in the transform does not select it.

Both harmonisation examples now use the documented `record_subset` operation.
Their restricted universe contains only h1-original; they illustrate a derived
reading of that source, not selection from a complete restatement history.
The all-record investor example still selects h1-restated and fy. Base review
acceptance assumes no later information dependencies beyond the stated bytes
and context. These explicit synthetic premises supply no historical-publication,
accounting-authority or issuer-restatement evidence.

FILE: docs/design/proposal/architecture/history-families-contract-v1.md (complete)
# History families: proposed contract, version 1

This contract specifies how one set of disclosures can support several joint
financial histories. It addresses MC08–MC11 and G1/G16, with evidence, chronology,
language and reproducibility dependencies under MC02/MC04/MC05/MC18/MC25/MC27.
It is a proposed specification. Its examples are deliberately synthetic;
independent review, accounting validity and human acceptance remain pending.
The companion `history-families-fixtures-v1.json` contains specified inputs and
expected results, not observations from an implemented engine.

## H1. Inputs and the question being answered

A reconstruction request supplies the following versioned records. References
mean immutable record versions and content hashes, not a mutable name such as
“latest”. A declared unknown differs from an omitted required field.

| Record | Required content | Admission consequence |
| --- | --- | --- |
| Evidence/time view | Source, reading, interpretation and review IDs; admission mode, selection mode, cutoffs, context-specific candidate-set revisions and unknown eligibility | Use the evidence v3 and time v2 rules. Unknown availability remains an affected-query obligation. |
| Observation | Concept, entity, perimeter version, economic instant or half-open reporting interval, calendar, basis, unit/currency, scale, sign and precision/rounding support; expression and source links | Two occurrences may refer to one quantity only through a supported context mapping. Never equate totals from different periods or bases by matching labels. |
| Interpretation and assumptions | Alternative IDs, conflict scope, admission layer, selected conditions, rationale, author and dependency versions; separate uncertainty category | Reading acceptance is not factual truth, treatment permission or a probability. An unselected assumption is not a constraint. |
| Opening state | Economic identities, rights/obligations, dated contract/lot/cohort state; accounting balances and reconciliation where supported; explicit unknown domains | Missing opening facts remain variables/obligations. Missing accounting support cannot be filled by balancing entries. |
| Model scope | Entities/perimeters, periods, candidate event/contract types, admissible domains, exclusions and reasons, template registry and mappings with versions | Finite slots or a bounded timeline are declared modeling restrictions, never evidence that excluded events did not occur. |
| Source obligations | Every in-scope observation/narrative obligation, applicability decision, dependent query and disposition | Unmapped, disputed, unsupported and not-yet-inspected content remains visible. An unexplained disposition prevents scope adequacy. |
| Query and budget | Requested layer, outputs, views/composition, scenario drivers and horizon, resolution, explicit resource ceilings, traversal policy and continuation reference | Omitted budget or view composition is a request error. Zero budget is valid; it is not an empty family. |

A template proposal must name its origin (source-supported, supplied assumption
or candidate requiring review), applicability conditions, economic state and event
effects, observation mappings, and accounting rules if it requests journals.
Each admitted constraint points to its exact support or selected assumption.
Unsupported accounting treatment is retained as an unresolved proposal with its
reason; it does not become an admissible treatment branch. Conversely, supported
reported-value arithmetic can proceed without claiming that a journal exists.

The output identifies its **target layer**. A conditional reported-value family
can be defined while the accounting-history family is unresolved. Calling both
simply “feasible” would conceal a different target. Any unresolved obligation
that can change membership in the requested family prevents an unconditional
admissibility claim, even if the currently enforced subset has a witness.

## H2. Joint trajectories, views and identity

Let h contain the chosen interpretations, dated economic states, events and,
where admitted, journals and balances. Within declared scope M and immutable
view v, define F(M,v) as the set of h satisfying all admitted opening,
transition, context-mapping and observation constraints jointly, conditional
on the listed assumptions. A missing required constraint leaves a partial
formulation; the implementation must retain the obligation and label witnesses
of the relaxed formulation as candidates, not validated members of the target.

Shared economic IDs link contracts across periods and accounts. Observation
IDs identify assertions; they are not substitute contract IDs. Two assertions
about the same balance constrain one shared variable after context alignment.
A bridge connects successive states using the same events. For example, the
synthetic opening 100 plus an event amount 20 implies closing 120. A candidate
closing 110 fails that bridge even if 110 appears elsewhere as a possible total.
This small identity assumes no omitted flows or valuation effects; actual
bridges require the accounting and domain contracts.

For the principal example, let nonnegative amounts x and y denote two components
of one reported total in synthetic USD. The disclosure condition is x+y=100.
The marginal ranges are each [0,100], but x=y=100 is impossible because its sum
is 200. Projection onto x may return [0,100], retaining the parent-family ID and
an extension obligation: any downstream use must find a y satisfying the same
family. Joining independent marginal ranges discards that obligation.

A named view is a predicate on the parent family, not another independent
history. Write A={h in F: x>=40} and B={h in F: x<=60}. Their intersection has
40<=x<=60 and y=100-x; their union is F. The overlap is not counted twice.
A request with several view IDs must say union or intersection. Views can also
leave parts of F uncovered. They provide no probability weights. Composition
across different family/view versions returns `FAMILY_CONTEXT_MISMATCH` unless
an explicit versioned alignment transformation proves the intended relation.

Family representation identity includes the full immutable semantic manifest:
view/review versions and candidate membership, scope, variables/domains,
constraints/support, selected assumptions, template/mapping versions and
resolution. Changing those fields creates a new family version. Merely changing
a search budget or traversal does not. A query has its own identity including
the family version, requested outputs, composition, layer, scenarios and horizon.

An individual witness identifies its family, complete assignments and dated
trajectory, interpretation choices and provenance. Two labels attached to the
same assignment do not create two witnesses. Different provenance manifests can
represent equal economic trajectories without sharing representation identity;
economic equivalence needs a stated comparison domain and argument. No solver
normal form or content hash proves that equivalence. A symbolic region is not
one witness and cannot be assigned one vote in a distribution.

For E05, an explicit conditional selector k in {A,B} gives
(k=A and revenue=120) or (k=B and revenue=110), with cash=40. These are assumptions
about which conflicting source to use, not evidence of a source's correctness.
The unconditioned reported-value response remains unresolved with both values;
the ratios conditional on A and B are 3 and 11/4. The target is not
revenue=120 and revenue=110. Choosing that conjunction would compute an empty
set for a different question. Missing treatment authority blocks journals in
both branches. Unknown source eligibility also propagates; constructing a
conditional branch cannot bypass time admission. E05 still lacks a qualifying
real-source conflict; this example does not repair that source gap.

## H3. Construction, search and continuation

The proposed interfaces are staged so that each decision has an accountable
input and an inspectable output. They do not select a solver or implement it.

| Operation | Input | Output and stopping rule |
| --- | --- | --- |
| ProposeCandidates | Reviewed view, opening state, scope and versioned template registry | Candidate instances, applicability reasons, exclusions and source-obligation dispositions. No arbitrary-disclosure discovery claim. |
| AdmitConstraints | Candidate instances plus category-specific evidence/assumption/treatment decisions | Supported constraints with origin IDs, rejected proposals with reasons, unresolved obligations and target-layer completeness. Stop target-dependent admission on missing authority. |
| BuildFamily | Admitted constraints, domains and full dependency manifest | Family formula/representation, shared symbol map, search partition specification, unresolved formulation obligations. Reject duplicate/conflicting IDs, missing context or undeclared symbols. |
| ValidateWitness | Family version and full candidate assignment/trajectory | Satisfied constraints with checked support, violated constraints, unsupported checks or missing fields. Valid only when every required target constraint is checked. |
| SearchFamily | Family version, explicit budget, capabilities, traversal and optional receipt | Evidence about regions, witnesses, infeasibility reasons/proofs, unresolved regions and a continuation receipt. A resource stop preserves the original formula. |
| QueryFamily | Family plus requested view/projection/scenario/resolution | Set/region or conditional results with completeness and dependency status. Bounds from explored regions are labelled explored-only. |

Source obligations use `mapped`, `not_applicable_with_reason`, `out_of_scope`,
`disputed` or `unresolved`. `Mapped` requires the actual constraint/support IDs;
several assertions can support one constraint without double-counting evidence.
`Not applicable` requires a reason and review version, not just a count.
Out-of-scope disclosures remain on the coverage report and wider mission queue.
A source count equal to a constraint count establishes none of these relations.
P17 must supply domain-specific candidate generation and applicability methods.

Search may partition a family into reproducible decision cells. Each cell
retains the original family formula AND its decision assignment/predicate.
A declared finite choice needs an explicit domain; continuous quantities remain
regions. The partition manifest states why its cells are exhaustive and
nonoverlapping. Named views are not automatically cells. If the backend cannot
establish a partition, retain the original region as unresolved instead of
inventing a finite-universe completeness claim.

For the examples, a cell key is the tuple (partition-version, decision-ID,
value-ID), or a sorted tuple of these assignments for several decisions. Decision
and value IDs come from the immutable manifest, never array positions or
traversal order. The retained key and manifest uniquely reconstruct the cell;
a digest can index them. General byte encoding belongs to language/IR. A search
receipt records the exact manifest, explicit traversal order, examined keys,
unvisited keys or a reconstructible range predicate, formulas, resource use,
backend/version and unresolved reasons. Ordinal suffixes are valid only with
the pinned ordering/domain manifest; changing order cannot reuse an old suffix.

A cell has one of three coverage dispositions: represented feasible region with
validated witness or another supported existence argument; proved infeasible
with checked contradiction/proof and scope; unresolved, retaining the region
and reason (`unvisited`, `unknown`, `unsupported`, `interrupted`, `cancelled`).
A feasible continuous region is preserved symbolically: one sample never
exhausts its points. “Every declared cell decided” means the whole family is
represented within M, not that every history was enumerated. All-cell
infeasibility proves emptiness only for the complete admitted formulation and
an exhaustive partition. Unsupported required operations or unresolved source
obligations veto that stronger conclusion.

The response therefore reports three independent fields: `existence` (witness,
proved_empty, unknown); `declared_search` (complete, partial, not_started);
`economic_scope` (supported_for_declared_scope, unresolved, explicitly_limited).
A scope may be explicitly limited even when search is complete. A partial
formulation also reports `formulation_complete=false`; its candidates do not
set target `existence=witness`. These statuses are scoped to the requested layer.
No value of these fields alone certifies whole-company coverage.

Resume requires exact semantic-manifest and partition identity. A changed
budget can continue unresolved cells. Changed evidence, assumptions, domains,
rules or partition create a new request and prevent blind continuation. Preserve
already committed partial work on cancellation; if a cell's result was not
committed, leave that whole cell unresolved. A zero-budget request returns the
entire original region unresolved and no proof of emptiness. No new solver is
required to specify this behavior.

## H4. Economic memory, grouping and refinement

A historical accounting balance does not describe all future contractual cash
flows. A principal of 100 with a fixed rate of 5% and a principal of 100 whose
floating rate was 5% can produce the same stipulated historical interest of 5.
If the next full-year rate is 7%, future interest is respectively 5 and 7. A
principal due next year and one due a year later can likewise have identical
current balances but different principal repayments within a one-year query.
The histories must retain rate/reset terms and maturity even when their
historical postings happen to agree. The example establishes arithmetic under
specified simple-interest assumptions, not a recognition or valuation method.

Required state is determined by requested scenarios, horizon and outputs plus
the applicable domain methods. It includes legal entity/perimeter, ownership and
rights, contract/lot/cohort identities, currency, principal/units, recognition
and measurement basis where applicable, rates/resets, schedules/maturities,
options/guarantees/collateral and linked dependencies whenever those affect the
query. “Unknown” is a value status requiring preservation; absence of a field
cannot silently mean no guarantee or no option. Later banks, insurance, groups,
FX, securities and cross-standard methods must extend these state requirements;
a scalar balance schema is not a whole-product substitute.

A grouping request names constituents, transformation/version, retained detail,
scenario domain, horizon, outputs, rules and exact/approximate claim. An exact
certificate must show that aggregation G commutes with every admitted transition
T for that domain, G(T(s,u))=T_group(G(s),u), and that requested outputs satisfy
O(s)=O_group(G(s)). These are proof obligations, not general facts about
financial balances. Missing proof/evaluation returns `GROUPING_UNSUPPORTED`;
it leaves detailed histories available and cannot delete them. A certificate is
part of query/resolution identity, with constituent and rule versions.

For the deliberately narrow simple-interest fixture, two principals 40 and 60
share entity, currency, a fixed 1/20 annual rate, a common day-count convention,
no intermediate principal change, and maturities after the half-year horizon.
Only total principal and interest are requested. Individual interest is
40*(1/20)*(1/2)+60*(1/20)*(1/2)=1+3/2=5/2. Grouping gives
(40+60)*(1/20)*(1/2)=5/2 by distributivity. Principal remains 100 under both
representations; any stipulated interest-payment cash transition subtracts the
same 5/2. This proves the named aggregate outputs/transitions for those
assumptions, not contract-level cash flows or other accounting measurements.
Constituent records remain linked so a later query can refine the group.

A changed output (individual contract exposure), rate/reset/maturity/guarantee
assumption, rule or horizon requires a new sufficiency decision. Reusing the old
certificate returns `RESOLUTION_REVALIDATION_REQUIRED`. Refinement produces a
new resolution version linked to its parent and constituent detail; if the
required detail was never preserved, return `DETAIL_UNAVAILABLE`, not fabricated
lots or contracts. Refinement can restore represented detail, not recover facts
that were never known.

Approximation is a distinct, optional future claim. Its record must name each
output, unit, scenario/horizon domain, absolute/relative tolerance, justification,
error argument or evaluation evidence, and exact-detail fallback. No tolerance,
empirical error bound or approximate grouping is approved by this contract.
Changing the query invalidates the approximation's applicability. Counts of
similar contracts and similarity of old postings are insufficient evidence.

## H5. Revisions, errors and layer interactions

Current eligibility depends on the candidate population as well as selected
assertions. Adding a competing source to an unchanged selection key creates a
new membership revision and invalidates affected family/query descendants.
Changed interpretation review, assumptions, template applicability, opening state
or treatment rules similarly changes the relevant semantic manifest. An old
result remains readable under its frozen view with a historical label. It must
not be relabelled current. Reuse requires a complete dependency comparison or an
explicitly supported independence argument; missing dependency information
means reuse is unestablished. An unrelated cash-only family can be reusable
while a revenue family is invalidated, subject to the same time/cutoff checks.

| Outcome | Required payload and consequence |
| --- | --- |
| `REQUEST_INVALID` / `CONTEXT_INCOMPLETE` | Missing fields, duplicate IDs or ambiguous composition with record locations; no admitted family is fabricated. |
| `CONSTRAINT_VIOLATION` | Candidate, failed original constraint and arithmetic/logic; candidate rejection is not family emptiness. |
| `PROVED_INFEASIBLE` | Complete target/formula, region, supported exhaustive scope and checked contradiction/proof; no conclusions about out-of-scope real histories. |
| `UNKNOWN` | Undecided formula and reason, even if no witness was returned. |
| `OPERATION_UNSUPPORTED` / `TREATMENT_UNSUPPORTED` | Exact operation or missing authority, affected target and retained formula/proposal; unsupported does not mean false. |
| `BUDGET_EXHAUSTED` / `CANCELLED` | Committed region results, all unresolved cells/regions and continuation receipt; partial valid witnesses survive. |
| `STALE_CONTINUATION` / `STALE_VIEW` | Expected and supplied immutable versions; require a new request or explicit frozen access, with no mutation of historical records. |
| `RESOLUTION_REVALIDATION_REQUIRED` | Changed query/rule/dependency fields and retained constituents; no use of an inapplicable certificate. |

These names specify distinctions for this contract. The later failure contract
must reconcile a common encoding with evidence/time/E05; this is not a claim
that a production exception hierarchy exists. A per-region outcome and a
request termination reason may coexist. For example, one feasible cell and
cancellation leave a partial family, not a cancelled mathematical truth.

| Neighbor | History-family input or output | Responsibility remaining outside this contract |
| --- | --- | --- |
| Evidence/time | Consume `SelectedEvidenceView`, contextual predicates, conflicts, membership revisions and unresolved eligibility; return dependency/obligation IDs | Complete source support and exact temporal admission belong to evidence v3/time v2. History construction cannot relax them. |
| Uncertainty | Consume category-labelled admission/selected assumptions; return joint family, conditional branch IDs and unresolved regions | Specify narrowing, elections, estimates, revisions and defensible joint measures. No equal weights or normalization over successful cells by default. |
| Accounting | Consume dated rule applicability, treatment constraints and opening/event bridges; return economic/history candidates plus unsupported obligations | Establish authority, recognition, measurement, journals and statements. Reported-value or economic feasibility cannot imply compliant accounting. |
| Language/IR | Supply shared identities, complete contexts, typed predicates, region/proof/status and source-location requirements | Define portable encoding, parser/typed authoring semantics, numerical capability and migration; symbolic prose is not an implemented IR. |
| Persistence | Supply immutable manifests, witness/region IDs, continuation receipts and dependency edges including membership | Define atomic commits, stale-write handling and reverse invalidation. Failed persistence cannot silently mark an unfinished cell complete. |
| Interfaces | Supply query layer, view composition, assumptions, scope/exclusions, coverage and unresolved outputs | Display those distinctions and allow conditional/frozen queries; avoid a single “complete” badge. |
| Failure semantics | Supply the outcome distinctions above with causal IDs and partial results | Harmonize names, retryability and recovery behavior without conflating mathematical and operational failures. |

## H6. Matched alternatives and proposed choices

Hold the same synthetic inputs x>=0, y>=0, x+y=100 and the same requested
outputs fixed: the joint feasible set, membership of (50,50) and (100,100),
and the A/B views from H2. A joint symbolic representation retains the line
segment, includes (50,50), rejects (100,100), and expresses overlap directly.
It is proposed because it preserves these meanings. Merely writing a formula
does not prove that construction captured all disclosures or that a backend can
solve it. An unsupported query still has to return its original region.

Explicit finite history enumeration is exact for an explicitly finite universe.
For example, if a separately justified scope limits x to {40,70}, enumerating
(40,60) and (70,30) represents that narrower family exactly. Under the original
continuous inputs, listing endpoints (0,100) and (100,0) alone misses (50,50).
An honest enumerator must report those as witnesses and leave the remainder
unresolved; it cannot change the input domain merely to report completeness.
Finite enumeration remains a suitable implementation candidate for genuinely
finite subproblems, with the same joint constraints and source obligations.

Independent account intervals [0,100] and [0,100] answer marginal questions, but
their Cartesian product admits (100,100). Using that product as the joint family
is wrong relative to the specified target. Retaining the linking equation with
the intervals repairs it, making them a presentation of the joint constraint
rather than an independent reconstruction. The proposed representation may
therefore expose intervals as summaries with their parent relation preserved.
No speed, usability or stochastic ranking is inferred from these examples.

| Choice and status | Provenance and justification | Failure mode and smallest diagnostic |
| --- | --- | --- |
| Joint constraints, proposed semantic requirement | MC08 and P15 audit; H2 proves the dependence counterexample | Independent marginal combination; HF01/HF02 reject it. |
| Region plus search evidence, proposed interface | MC09; historical P04 illustrates but does not authorize the design | Witness promoted to completeness; HF04/HF06/HF07 distinguish them. |
| Explicit scope/obligation report, proposed interface | G1/P15; supplied templates cannot discover omitted events | Complete cell count hides exclusions; HF05/HF09 preserve them. |
| Stable manifest and cell keys, proposed engineering choice | MC25 reproducibility; semantic keys survive traversal changes | Order-dependent replay; HF07/HF15 reject mismatched continuation. Byte encoding remains IR work. |
| Exact rational small examples, fixture convenience | Deliberately stipulated numbers make algebra independently checkable | Mistaken universal decimal/solver policy; HF04 preserves strict endpoints, accounting/numerics remain open. |
| Finite example decisions and cell budgets, fixture convenience | Two branches expose interruption with a tiny example | Whole-company or continuous completeness inferred from counts; H3 requires preserved regions and scope. |
| Query-dependent grouping, proposed interface | MC11/G16; H4 derives a narrow positive case and counterexamples | Same postings mistaken for same exposure; HF10–HF12 require detail/revalidation. |

Z3, Python, rational arithmetic, Boolean truth-cell expansion, slot limits,
traversal order, storage and compression are not chosen as whole-product defaults.
Historical `reconstruction-profile-v1.md` and `reconstruction_v1.py` (construction
and grouping functions) are bounded prototype evidence. P03's authored debt
lowering likewise does not establish disclosure-to-template discovery. The
current contract's arguments are the explicit set and arithmetic derivations
above; no uninspected paper or accounting authority is invoked.

## H7. Completion and remaining decisions

The companion fixtures cover joint dependence, contexts, source conflict,
continuous regions, scope, honest failure/search, economic memory, grouping,
revision invalidation and frozen access. Their algebra and file consistency can
be checked without building a product module. They do not establish semantic
completeness of this specification; that requires independent result review.

P15-E09 (partial outcomes), E11 (numerical capabilities), E12 (economic memory),
E13 (scenarios/weights), and E05 (layered review) now have concrete proposed
history-family consequences. They remain open pending counterpart contracts and
review. All fourteen P15 decisions and all MC01–MC35/G1–G18 obligations remain
active. In particular, sufficient state for every sector, source-grounded
candidate generation, dated accounting permissions, general grouping proofs,
and probability/calibration methods belong to further P16/P17 work. This slice
does not select the initial product profile or dependency order.

The stop condition is saved H1–H7, specified fixtures, architecture registration,
actual local/registered-check records, and explicit residuals. The next task is
a separately reviewed uncertainty contract. Pending E05/history-family bounded
result review and expected whole-architecture check failure do not prevent that
planning or authorised independent drafting. Full independent P16 result review
remains required before phase acceptance.

FILE: docs/design/proposal/architecture/uncertainty-contract-v1.md (complete)
# Integrated uncertainty operations — proposed contract v1

This specification completes the operation layer above uncertainty admission,
joint-measure attachment and history-family construction. It addresses MC08–MC14,
MC18, MC25, MC27 and MC33–MC35, principally G1, G6, G15 and G16. Its finite examples
are authored assumptions. They establish neither company probabilities nor an
accounting treatment. Product implementation and independent acceptance remain
pending. The initial profile and all fourteen P15 decisions remain open.

## 1. Question, evidence and default audit

Can a retained family support conditioning, new evidence and conditional outcomes
without invented weights, repeated information or discarded unresolved regions?
The baseline is the proposed admission U1–U6, attachment v2 A–F and history H1–H7
contracts. Core 0's uncertainty section and chapter 5's finite-model derivation
are mathematical design evidence, not approved product behavior. This document
extends their operation semantics; earlier supplements' deferrals describe their
historical scope. Their unchanged records and failure examples remain applicable.

The pass criterion for this bounded task is a coherent specified exchange and
independently recomputable finite examples, with preserved identities and failure
receipts. Invalid arithmetic, lost dependencies or contradictory state assertions
veto this document's internal check and trigger repair. Missing empirical support
vetoes an empirical claim, not continued specification. Checker counts and example
coverage are explanatory only. No stochastic experiment or architecture ranking
is performed. Results are retained in uncertainty-fixtures-v1.json and the P16
result note with fresh check records. Stop after this group; accounting is next.

| Choice and provenance | Reason; misleading failure | Early diagnostic; status |
| --- | --- | --- |
| Optional law, MC12 and attachment B | Facts and feasible alternatives need not have weights; uniform branch weights would invent information. | Unweighted fixture forbids aggregate mean/quantile; proposed invariant. |
| Immutable linked records, evidence/time/history contracts | Corrections must preserve earlier answers; pointer substitution would leak later evidence. | Parent hashes and explicit cutoff checks; provisional representation choice. |
| Exact finite rational examples, approved plan | Independently check normalization; finite success could be mistaken for continuous inference. | Fractions recomputation plus unsupported point-conditioning example; fixture convenience only. |
| Observation blocks, chapter 5 and extraction identity rules | Capture reused information; different files or IDs could disguise one observation. | Repetition, components, alternative extraction and correction examples; proposed invariant. |
| Dependence declared, never inferred from absence of links | Multiplying factors requires a conditional model; unjustified independence overstates information. | Unknown overlap rejects independent multiplication; proposed invariant. |
| Preserve every requested region, history H4 and chapter 5 | Solver failure is not an economic outcome; successful-only means would change the question. | Partial mass and explicit completion-condition examples; proposed invariant. |

Skeptical audit: the comparison fixes semantic inputs; neither prior prototypes,
branch counts nor execution success define the baseline or promotion rule. There
is no runtime/environment comparison. Continuous inference and causal evaluation
remain explicit capability limits, not evidence against those research directions.

## 2. Exchange, identities and validation

An immutable `UncertaintyRequest` has `request_id`, `version`, `predecessor`,
`operation`, `family_ref`, `view_ref`, `attachment_ref` (explicit null if absent),
`model_ref` (explicit null if unweighted), `time_ref`, `evidence_view_ref`,
`admission_ref`, `purpose`, `information_cutoff`, `evidence_cutoff`, `query`,
`dependencies` and `provenance`. References bind exact `id@version` records;
payload changes require a new version or identity. Time mode, publication and
byte-vintage eligibility follow T1–T3; a new observation can produce a later
view only with an explicit new time/admission record. Frozen earlier views remain
queryable. Source occurrence, semantic assertion, interpretation, observation
block and likelihood factor have separate identities.

The query declares the operation-specific condition, evidence update or outcome
selection, including scenario/path/date and typed quantities. Dependencies include
the transitive closure of all typed record references, including assumptions,
review selection, law, accounting method and source lineage. An empty selection
never means all. Outcome labels such as `a` are domain members, not record keys.
The fixture registry is self-contained: it instantiates this exchange without
silently importing the predecessor fixtures' registry. File references pin source
contracts by SHA-256; they do not count as observation blocks.

`UncertaintyResult` retains request identity, old/proposed view, disposition,
reason codes, support and preserved records, unresolved obligations, future
dependencies, `family_effect`, payload, and separate statuses:

* `structural_validity`: valid/invalid;
* `mathematical_status`: satisfied/failed/undefined/unresolved;
* `empirical_justification`: stipulated/not_established/supported_for_named_scope;
* `capability_status`: specified_only_no_runtime/unsupported;
* `computation_status`: specified_exact/specified_partial/symbolic/not_computed.

Fixture computations are expected outputs, never runtime success claims.
Accounting validity and human acceptance are separate fields, neither inferred
from mathematical status. Successful derivation creates a candidate child view;
it preserves the parent and changes no active view pointer. Admission/selection
is a separate explicit operation. Rejection stores submitted bytes and a receipt
but creates no child view, posterior, aggregate result or partial domain write.
`state_before` and `state_after` name the same selected family/view/attachment
and parent hashes on rejection. Receipt storage itself is not a domain update.
Retrying identical request bytes returns the same logical receipt; a reused
identity with different bytes fails `IDENTITY_CONFLICT`. Actual atomic storage,
crash recovery and concurrency are obligations for the later persistence contract.

| Validation stage | Invalid or unresolved condition | Disposition and consequence |
| --- | --- | --- |
| Envelope/registry | Missing field, scalar where reference array required, identity collision, unresolved reference | REQUEST_INVALID; record exact field/reference and preserve submission. |
| Binding/admission | Wrong family/view/model, event outside domain, incompatible unit/purpose, missing dependency, inadmissible cutoff | REQUEST_INVALID; no substitution of nearest/newest record. |
| Law/event | Missing masses, negative/nonfinite mass, nonunit total, unresolved measurability | Invalid laws fail mathematics; unresolved obligations remain symbolic; no computed probability. |
| Evidence reuse | Repeated information, unmodeled overlap, correction applied atop superseded evidence | REQUEST_INVALID with the specific reuse code; old law retained. |
| Normalization | Zero denominator/normalizer | UNDEFINED; undefined mathematics, no posterior. |
| Capability | No admitted law, unavailable evaluator, continuous point without conditional model | UNSUPPORTED or RETAINED_SYMBOLIC; preserve feasible family and expressions. |
| Outcome coverage | Unsupported method, numerical failure, unexplored domain | PARTIAL; retain region and mass/unknown mass, never silently condition on completion. |

These stages reuse the saved attachment/malformed supplements. Error lists are
ordered by stage then record key; later numerical evaluation does not run after
an earlier invalid prerequisite. Preserve all unresolved references in receipts.

## 3. Conditioning and scenarios

An observational condition names an admitted event A, the parent law P, the
information used to define A and its role. For finite elementary outcomes S,
require a measurable A subset of S and P(A)>0. Define

    P_A(s) = P(s) 1{s in A} / P(A),
    P(B | A) = sum_{s in A intersect B} P(s) / P(A).

The numerator sums elementary outcomes once even when display labels overlap.
The child retains S and records zero mass outside A, the event identity,
denominator and parent law. Keeping zero-mass members distinguishes the declared
domain from its positive-mass support. Reapplying A is mathematically idempotent;
it records no new information factor. If A came from observation block D, the
child's consumed-information set includes D and its semantic lineage, preventing
subsequent likelihood multiplication by the same information. A hard constraint
already used to construct the family is likewise consumed, even if it did not
appear as a numerical likelihood. Evidence used to fit a prior/model is declared
in that model's training/calibration lineage for the same check.

With masses a=1/2, b=1/3, c=1/6, A={a,b}, B={b,c}, the denominator is 5/6,
intersection mass is 1/3, and P(B|A)=2/5. The conditional masses are (3/5,2/5,0).
P(A)=0 returns `ZERO_CONDITION_MASS` and no child; an empty feasible subset in
an unweighted family is instead scoped infeasibility. An unweighted nonempty
restriction yields a feasible subset with `probability=null`, not a distribution.

An exogenous stress changes a declared driver/scenario while retaining history
weights unless an explicit observation model says that observing the scenario
provides information. Its result is labeled scenario-assumed, not P(.|observed
scenario). A structural intervention requires a causal model, modified equations,
intervened variables and an identification/validation argument; `do(X=x)` is
never lowered to filtering `X=x`. This proposal retains such requests as
unsupported until a declared evaluator and its evidence are supplied in P17.

For continuous/mixed laws, event conditioning uses the same measure formula when
the event has positive mass and the evaluator is supported. A continuous point
event of zero mass requires an explicit regular conditional kernel/version (or
justified reduced parameterization) with the conditioning variable, base measure,
support and chosen version at the queried point. A density value is not the
probability of that point. No epsilon window or Gaussian penalty is invented.
General existence, uniqueness at null points and numerical evaluation remain
method obligations; symbolic expressions may be retained without a numeric answer.

## 4. Evidence updates and information reuse

An `ObservationBlock` records its immutable identity, purpose, observed values and
full financial context, source occurrences and assertion/reading references,
`information_atoms`, relations (`same_information`, `component_of`, `derived_from`,
`supersedes`), availability/time view, admission and dependencies. Information atoms
name semantic observations, not bytes: a duplicated PDF, a new extraction or a
repeated table entry does not automatically supply new information. Where semantic
equivalence cannot be decided, overlap is `unknown`; new IDs alone cannot prove
independence. No general automatic duplicate detector is claimed.

A `LikelihoodModel` records target family/coordinates, law purpose, observation
block(s), base measure for observed data, conditional arguments, parameter version,
units, support, consumed information and justification. Its output is a
nonnegative measurable L(s). For discrete observations L is a probability of the
specified observation; for continuous observations it can be a density and may
exceed one. Extraction confidence, expert preference and solver success are not
likelihoods. A finite update requires finite nonnegative values on all S and

    Z = sum_s P(s)L(s) > 0;    P_new(s) = P(s)L(s)/Z.

The result records unnormalized masses, Z, the complete posterior including zeros,
new consumed-information set and parent view. With P=(1/2,1/3,1/6) and
L=(1/2,1,0), unnormalized masses are (1/4,1/3,0), Z=7/12 and posterior
(3/7,4/7,0). If Z=0, return `ZERO_NORMALIZER`; do not substitute equal weights or
silently broaden support. A later observation inconsistent with every positive-mass
history calls for an explicit model/family revision, not an invisible numerical fix.

Two observation blocks can enter one joint likelihood L(D1,D2|s). Sequential
updating must use L(D2|D1,s); replacing this by L(D2|s) requires an explicit
conditional-independence assumption with target-specific justification. Different
information atoms are necessary bookkeeping, not a proof of independence. A
dependent conditional model may legitimately reuse D1 as a conditioning argument;
it must name D1 as already consumed and add only D2 as incremental information.
Unknown dependence blocks the independent-factor route while retaining the blocks
for a later joint model. Marginal likelihood tables alone do not define the joint
likelihood.

| Submission | Required result |
| --- | --- |
| Same immutable request/bytes | Idempotent receipt lookup, no second child or factor. |
| New request, same source occurrence/information block | `DUPLICATE_INFORMATION`; preserve prior posterior. |
| Total plus all its components as independent factors | `DERIVED_INFORMATION_REUSE`; one joint block or an explicit conditional model is required. A deterministic total adds no independent information beyond all components. |
| Alternative extraction of one source span | `ALTERNATE_READING_NOT_NEW_OBSERVATION`; resolve/branch the reading under admission U rules. A new noisy measurement model must be explicitly justified if intended. |
| Potentially overlapping blocks with unknown relation | `DEPENDENCE_UNRESOLVED`; no independent update. |
| Corrected reading multiplied into an old posterior | `CORRECTION_REQUIRES_REBASE`; retract/supersede in a new evidence view and recompute from a retained base preceding the affected block. |

A correction supplies the superseded block, corrected block, base view and the
ordered retained incremental updates to replay. Validate that none of the old
block's descendants survives without revalidation. Recompute from the base with
the corrected likelihood and any still-admissible downstream conditional factors.
Do not divide by the old likelihood: it may be zero and its support restriction
may already have removed alternatives. The old posterior, evidence view and
receipt remain unchanged. The illustrative corrected L=(1,1/2,1) on the original
P gives Z=5/6 and (3/5,1/5,1/5). This is a newly specified view, not historical
knowledge rewritten in place. Full crash-safe replay is a persistence obligation.

## 5. Conditional outcome payloads

A query selects exact family/view, condition, scenario, path set, dates, accounting
methods and output quantities. Each row key is `(history_ref, condition_ref,
scenario_ref, path_ref, date)`. Cells carry entity/perimeter, concept, dimensions,
currency/unit/scale/sign, instant or interval and measurement basis, together with
state/journal/report references, assumptions and dependencies. A joint statement
vector shares its path and state references; marginals from incompatible histories
cannot be recombined into a synthetic balance sheet. Expected statements need not
describe any admissible history and remain summaries, not journal postings.

Cell status is `exact`, `symbolic`, `sampled`, `certified_bound`, `explored_range`
or `unresolved`. Exact means exact under the declared model and inputs. Sampled
requires sampler/seed/stream, weighting and uncertainty metadata; it is not exact.
Certified bounds require a cited proof/certificate, domain and endpoint semantics;
explored ranges describe only visited regions. Symbolic values retain expression,
domain and unresolved dependencies. No computational tag asserts accounting
eligibility or empirical forecast validity.

For weighted finite reporting, allocate every elementary outcome once to a
disjoint partition `completed`, `unsupported`, `numerical_failure`,
`solver_unknown`, `cancelled` or `unexplored`. Coverage masses total one (or the
explicit parent event mass for an unnormalized subquery); unknown mass stays
unknown and prevents a false exact total. Economic default is an economic-state
flag orthogonal to this partition: a fully computed default belongs to completed;
an unsupported default branch can remain unresolved. Report default mass separately
with its overlap with completion so it is never added twice. Default retains legal
obligations and usable state. Stop only affected descendants when a required method
is unsupported, retaining independent quantities through their dependencies.

Suppose a,b have exact expense 10,20 and c's valuation is unsupported. Under
P=(1/2,1/3,1/6), completed mass is 5/6, unresolved mass 1/6 and the completed
unnormalized contribution is 35/3. The unconditional mean and quantiles are
unresolved; 35/3 is not the mean of the full outcome. A separately requested
`condition_on_completion` query reports event {a,b}, denominator 5/6 and mean 14.
Its labels state that this is a computational selection, not an economic forecast
condition or evidence update. This view cannot silently feed back into historical
probabilities. Partial values may support bounds only with explicit bounds for
the missing region; a missing value is neither zero nor default.

When history weights are absent, retain the feasible set and separate within-history
future laws K(h,scenario) if available. No uniform averaging across histories.
Without a within-history law retain a deterministic/symbolic feasible outcome set.
A complete finite set {10,20,30} has exact range [10,30] but no mean or quantile.
If only {10,20} was explored and c is unresolved, [10,20] is merely an explored
range and cannot become a full-family bound. Even when every K is valid, an
envelope of their quantiles is not a predictive distribution. An optional history
law plus a measurable kernel defines a mixture; discrete reporting sums disjoint
history/innovation atoms, and continuous mixtures require a supported integrator.

## 6. Interactions, alternatives and acceptance boundary

Evidence supplies contextual assertions and observation lineage; time determines
admissible information; admission separates the six uncertainty categories. History
families supply compatible joint states, scope, residual regions and refinement
maps. Accounting consumes a history/scenario/path and returns typed states and
journals with eligibility status; uncertainty never makes an unsupported treatment
admissible by giving it positive probability. Language/IR must type conditions,
measures, units, model purpose and requested aggregation; implicit casts from sets
to distributions are forbidden. Interfaces expose denominators, unresolved mass,
view lineage and evidence reuse receipts. Persistence retains immutable requests,
models and child derivations with resumable frontiers; failure semantics propagate
dependency-scoped unknowns. These are requirements on unfinished counterpart
contracts, not evidence that they are complete.

The two credible storage alternatives are a law linked to a family registry and
a self-contained joint model carrying its definitions. Compare them with identical
S, typed assignments, masses, evidence blocks, cutoffs, parent lineage and queries.
Under a bijection f of elementary outcomes require equal assignments and
P_embedded(x)=P_linked(f(x)); also preserve event sets, likelihood values and consumed
information. Finite conditioning and normalization then have equal sums by a change
of index. Registry links simplify shared revisions but require dependency closure;
self-contained packages simplify portable inspection but risk copied evidence being
counted twice. Both must retain semantic observation identities. A paired fixture
specifies the same conditional and posterior values in both forms; no throughput,
memory, empirical or general continuous-equivalence conclusion follows.

The provisional preference is explicit immutable shared identities with a
self-contained export containing the same identities and definitions. It follows
from traceable revisions and reuse, not from prototype convenience. Ownership and
initial-profile selection remain open. Weighted and unweighted reporting answer
different questions and are not competing estimators to rank on these examples.
Single joint likelihood and conditional sequential factorization are both credible
when their models match; naive multiplication is valid only under the stated
conditional independence. Correction by replay is chosen over division because
zero likelihoods make division lose recoverable histories.

This group is ready for independent substantive review when the full exchange,
fixtures and internal arithmetic/reference checks agree. Its finite capability
boundary is specified; continuous/mixed inference, causal identification,
calibration and empirical validation remain P17 obligations. Accounting, language,
persistence, interfaces, failure semantics, integrated profile/acceptance order,
E05 source conflict and full MC01–MC35/G1–G18 reconciliation remain open. Neither a
successful checker nor this candidate contract enables product implementation.

FILE: docs/design/proposal/architecture/accounting-contract-v1.md (complete)
# Accounting and state-transition contract (proposed v1)

This document specifies one bounded handoff for the proposed whole-product
architecture. It is a design contract, not an accounting engine or a claim of
standards compliance. The handoff keeps source eligibility, treatment choice,
journal construction and state mutation distinct so that a balanced journal
cannot conceal an unsupported treatment.

## 1. Evidence and scope

The contract consumes an `EconomicEvent` only when the event has a stable
business identity, an entity/book perimeter, an economic interval, a declared
currency/unit/scale, an expected opening-state digest, and links to the
evidence, authority, method and assumption versions used to assess it. The
evidence link must identify the source bytes and the reviewed assertion or an
explicit unresolved reason. A source label or account name never supplies a
classification by itself. The illustrative fixtures bind to A01–A03 in
`standards-fixtures-v1.json` and to the inspected S9 paragraphs recorded in
`standards-source-register-v1.json`; their scope is a for-profit entity with an
annual period beginning 2024-01-01 under the retained 2022 compilations.

The proposed handoff is:

```text
EconomicEvent
  -> TreatmentAssessment
  -> JournalProposal
  -> StateTransitionReceipt
```

`TreatmentAssessment` answers whether the event is eligible under the declared
authority and method. It may be `eligible`, `unresolved`, `ineligible`, or
`outside_scope`. It must preserve the known facts and the reason for any
unresolved or rejected treatment. It does not mutate a book.

`JournalProposal` is produced only for an eligible assessment. It contains
typed lines with account, entity, concept, dimensions, currency, unit, basis,
debit/credit amount and rounding metadata, plus the independently computed
state delta. The line set and delta are checked together before commitment.

`StateTransitionReceipt` records the request identity, parent opening digest,
assessment and proposal digests, committed journal/state digests, status and
audit lineage. A rejected or unresolved receipt has no committed journal or
state delta and retains its reason and submitted evidence references.

## 2. Inputs and outputs

Required inputs are versioned `event`, `opening_state`, `authority`, `method`,
`evidence`, `time`, `identity`, and `cutoff` records. `opening_state` includes
the book version and all balances needed by the method; `cutoff` fixes which
source versions and publication times are admissible. `identity` binds the
business event, entity/book and event version. The method records recognition,
measurement, posting and rounding assumptions; it must not silently import an
unrecorded rate, classification or later source.

An eligible output contains `assessment.status=eligible`, a balanced journal,
an account/state delta, closing-state digest, and `receipt.status=committed`.
An unresolved output contains `assessment.status=unresolved`,
`receipt.status=rejected`, `mathematical_status=unresolved`,
`computation_status=not_computed`, `commit=false`, and `state_delta=null`.
Invalid identity, stale opening state, conflicting event payload, unsupported
authority or out-of-scope facts have distinct rejection codes. The common
status envelope does not turn a rejected request into a computed result.

## 3. Invariants and atomicity

1. Every committed line retains compatible context and exact source/method
   lineage. Labels do not perform standards conversion.
2. Debit and credit totals agree after the declared rounding rule, and the
   account roll-forward equals the independently calculated state delta.
3. A treatment is not eligible merely because its journal balances. Missing
   authority or required evidence is an eligibility veto.
4. Journal, state and committed receipt are one atomic transition. Any failed
   check writes none of them; a rejection receipt may be stored as an audit
   record with `commit=false`.
5. Replaying an identical `(book, business_event_id, event_version, payload,
   method/evidence/assumption versions)` returns the original receipt without a
   second posting. A different payload for the same identity is
   `EVENT_ID_CONFLICT`.
6. A new event whose expected opening digest differs from the current book is
   `STALE_OPENING_STATE`; it cannot overwrite or merge state implicitly.
7. Unresolved and invalid treatments preserve known facts and produce no
   domain write. A correction or alternative treatment requires a new explicit
   event/version and lineage.

## 4. Failure and interaction rules

The evidence contract supplies immutable bytes, reviewed assertions and
conflicts. The time contract supplies admissible source/review versions and
cutoffs. History families supply a branch-specific opening state and treatment
context; accounting must retain the branch identity in the receipt. The future
language/IR contract must carry these typed records without erasing status or
lineage. Persistence must make the identity lookup, opening digest and atomic
write durable; interfaces and failure semantics remain unfinished P16 work.

`MISSING_EVIDENCE`, `UNSUPPORTED_AUTHORITY`, `TREATMENT_UNRESOLVED`,
`CONTEXT_MISMATCH`, `ROUNDING_MISMATCH`, `UNBALANCED_JOURNAL`,
`EVENT_ID_CONFLICT`, and `STALE_OPENING_STATE` are separate outcomes. No
failure is converted to a zero amount, a guessed classification, or a sampled
future result. A failed transition is safe to retry only after receipt lookup
has established whether a prior commit exists.

## 5. Alternatives and provisional choice

Direct balanced posting is compact but entangles eligibility, arithmetic and
mutation; it is retained as a comparison baseline. Event-sourced projection
preserves history and replay but still needs a typed treatment boundary and
can leave projection timing ambiguous. The provisional choice is a typed
shared-IR adapter with the four explicit stages above: it makes method/source
identity portable, permits branch-specific state, and gives persistence a
single atomic receipt boundary. This choice is provisional until language,
persistence and interface contracts are specified and compared on the same
fixtures. No technology, database, solver or authoring syntax is selected.

## 6. Fixture interpretation and limits

Fixture A01 is an eligible FVTPL acquisition at price/fair value 100 with fee 2:
asset debit 100, expense debit 2, cash credit 102. A02 is the matched
amortised-cost case: asset debit 102 and cash credit 102, assuming that category
has been separately justified. A03 has price 100, fair value 105 and missing
evidence for the relevant observable-valuation condition; it remains
`TREATMENT_UNRESOLVED` with no journal or state write. Replay and stale-state
cases exercise identity and atomicity using A01's committed receipt.

These examples check the contract's distinctions and arithmetic only. They do
not cover leases, tax, pensions, impairment, groups/FX, banks, insurers,
IFRS/US GAAP/ASBE applicability, forecasting or complete disclosure packages.
Those later-domain obligations remain visible in the P16 profile and P17 plan.

FILE: docs/design/proposal/architecture/accounting-integration-c09-c10-conditions-field-diagnostic-v1.py (complete)
"""Finite proposal-example diagnostic. Not a runtime API or accounting engine.

Derive findings solely from submitted C09/C10 values, then compare the saved
expectations. The fixture purposes, IDs and expected findings never select rules.
Run from the repository root with one fresh output JSON path.
"""
import copy
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

B = Path('docs/design/proposal/architecture')
P = 'accounting-integration-c09-c10-conditions-field-'
ABSENT = object()
BLANK = frozenset(chr(n) for n in (
    list(range(0x9, 0xE)) + [0x20, 0x85, 0xA0, 0x1680]
    + list(range(0x2000, 0x200B)) + [0x2028, 0x2029, 0x202F, 0x205F, 0x3000]))
A = 'identical_instrument_active_market_quote'
T = 'technique_only_observable_market_data'
REASON = ('Required null or nonblank string; with exact required=true and any '
          'typed null route, a nonblank string is required.')
CONTEXT = 'Required null or nonblank contextual string; no route or method inference.'
OBJECT = 'Required object; malformed parent suppresses descendants only.'
BOOL = 'Required exact Boolean.'
ROUTE = 'Required Boolean or null.'
TEXT = 'Required nonblank string.'


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(',', ':'), allow_nan=False)


def type_name(value):
    if value is None:
        return 'null'
    return {bool: 'boolean', int: 'number', float: 'number', str: 'string',
            dict: 'object', list: 'array'}[type(value)]


def derive(candidate):
    """Presence/type/content inspection; no access to expectations or labels."""
    findings = []

    def inspect(parent, key, path, kind, rule, require_text=False):
        value = parent.get(key, ABSENT)
        code = None
        if value is ABSENT:
            code = 'INVALID_CONDITION_PACKET'
        else:
            valid_type = {
                'object': type(value) is dict,
                'boolean': type(value) is bool,
                'route': value is None or type(value) is bool,
                'reason': value is None or type(value) is str,
                'text': type(value) is str,
            }[kind]
            if not valid_type:
                code = 'INVALID_FIELD_TYPE'
            elif type(value) is str and kind in ('reason', 'text') and not any(
                    c not in BLANK for c in value):
                code = 'INVALID_UNKNOWN_REPRESENTATION'
            elif kind == 'reason' and require_text and value is None:
                code = 'INVALID_UNKNOWN_REPRESENTATION'
        if code:
            observed = {'present': value is not ABSENT}
            if value is not ABSENT:
                observed.update(type=type_name(value), value=value)
            findings.append({'stage': 'shape', 'path': path, 'code': code,
                             'expected_rule': rule, 'observed': observed})
            return ABSENT
        return value

    for cid in ('C09', 'C10'):
        path = 'source/' + cid
        packet = inspect(candidate, cid, path, 'object', OBJECT)
        if packet is ABSENT:
            continue
        value = inspect(packet, 'value', path + '/value', 'object', OBJECT)
        obligation = False
        if value is not ABSENT:
            if cid == 'C09':
                required = inspect(value, 'required', path + '/value/required',
                                   'boolean', BOOL)
                first = inspect(value, A, path + '/value/' + A, 'route', ROUTE)
                second = inspect(value, T, path + '/value/' + T, 'route', ROUTE)
                # ABSENT is distinct from typed null. Exact identity excludes 1.
                obligation = required is True and (first is None or second is None)
                inspect(value, 'unknown_reason', path + '/value/unknown_reason',
                        'reason', REASON, obligation)
                inspect(value, 'branch', path + '/value/branch', 'text', TEXT)
            else:
                inspect(value, 'method', path + '/value/method', 'text', TEXT)
                for flag in ('unequal_price_a_method_available',
                             'unequal_price_b_method_available'):
                    inspect(value, flag, path + '/value/' + flag, 'boolean', BOOL)
        inspect(packet, 'unknown_reason', path + '/unknown_reason', 'reason',
                REASON if cid == 'C09' else CONTEXT, obligation)
    return sorted(findings, key=lambda item: (item['path'], item['code']))


def main():
    started = time.monotonic()
    target = Path(sys.argv[1])
    if target.exists():
        raise SystemExit('Refusing to overwrite existing diagnostic evidence: ' + str(target))
    checks, results, inputs = [], [], {}

    def check(label, passed):
        checks.append({'id': label, 'passed': bool(passed)})

    def digest(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    def load(path):
        inputs[str(path)] = digest(path)
        return json.loads(Path(path).read_text())

    fixtures = load(B / (P + 'controls-v1.json'))
    inputs[str(Path(__file__))] = digest(__file__)
    for ref in fixtures['sources'] + [fixtures['specification'], fixtures['matrix']]:
        check('source pin ' + ref['path'], digest(ref['path']) == ref['sha256'])
        inputs[ref['path']] = digest(ref['path'])
    source_cases = {ref['path']: {c['id']: c for c in load(ref['path'])['cases']}
                    for ref in fixtures['sources']}
    check('explicit Unicode set', fixtures['blank_codepoints'] == [
        f'U+{ord(c):04X}' for c in sorted(BLANK)])
    ids = [c['id'] for c in fixtures['local_controls']]
    check('unique control IDs', len(ids) == len(set(ids)))
    pairs, null_controllers, preserved_strings = set(), 0, 0
    for control in fixtures['local_controls']:
        label = control['id']
        comparator = control['comparator']
        ref = comparator['file']
        check(label + ' comparator hash', digest(ref['path']) == ref['sha256'])
        original = source_cases[ref['path']][comparator['case_id']]['complete_inputs']
        rebuilt = {cid: copy.deepcopy(original[cid]) for cid in ('C09', 'C10')}
        check(label + ' comparator projection', comparator['projection'] == ['C09', 'C10'])
        mutated = []
        for mutation in control['mutations']:
            parts = mutation['path'].split('/')
            check(label + ' mutation root', parts[0] == 'source' and parts[1] in ('C09', 'C10'))
            parent = rebuilt
            for key in parts[1:-1]:
                parent = parent[key]
            key = parts[-1]
            check(label + ' exact prior value ' + mutation['path'],
                  key in parent and canonical(parent[key]) == canonical(mutation['before']))
            mutated.append(mutation['path'])
            if mutation['op'] == 'remove':
                del parent[key]
            elif mutation['op'] == 'replace':
                parent[key] = copy.deepcopy(mutation['after'])
            else:
                raise ValueError('Unsupported mutation operation')
        check(label + ' no repeated mutation paths', len(mutated) == len(set(mutated)))
        check(label + ' exact mutation reconstruction and unchanged fields',
              canonical(rebuilt) == canonical(control['candidate']))
        actual = derive(control['candidate'])
        check(label + ' complete findings including stage/path/rule/observation',
              canonical(actual) == canonical(control['expected_diagnostics']))
        check(label + ' path/code order', actual == sorted(actual, key=lambda x: (x['path'], x['code'])))
        reason_paths = [f['path'] for f in actual if f['path'].endswith('/unknown_reason')]
        check(label + ' at most one finding per reason', len(reason_paths) == len(set(reason_paths)))
        check(label + ' representation outcome', control['representation_valid'] is (not actual))
        check(label + ' accounting not assessed', control['accounting_outcome'] == 'not_assessed_representation_only')
        if not control['mutations']:
            v = rebuilt['C09']['value']
            if v['required'] is True:
                pairs.add((v[A], v[T]))
            elif v['required'] is False:
                null_controllers += 1
        for mutation in control['mutations']:
            if type(mutation.get('after')) is str:
                preserved_strings += 1
        results.append({'id': label, 'derived_diagnostics': actual,
                        'representation_valid': not actual,
                        'accounting_outcome': 'not_assessed_representation_only'})
    check('all nine retained required=true pairs', pairs == {(x,y) for x in (True,False,None) for y in (True,False,None)})
    check('retained equal-price control', null_controllers >= 1)
    failures = [c for c in checks if not c['passed']]
    report = {'schema_version': 'accdsl.proposal.c09-c10.field-verification.v1',
              'passed': not failures, 'control_count': len(results),
              'assertion_count': len(checks), 'failures': failures,
              'checks': checks, 'results': results, 'input_hashes': inputs,
              'manifest': {'command': ['python3', str(Path(__file__)), str(target)],
                  'environment': 'standard-library Python ' + platform.python_version(),
                  'git_commit': 'unavailable: pre-existing unusable .git marker; no initialization',
                  'cpu_gpu': 'CPU-only JSON diagnostic; no device/framework probing or imports',
                  'random_seeds': 'N/A: deterministic finite document diagnostic',
                  'data_version': inputs[str(B / (P + 'controls-v1.json'))],
                  'wall_seconds': round(time.monotonic()-started, 6),
                  'plan_file': 'data/accounting-master/runs/20261006T005135-d44c7a2e/P16/approved-plan.json',
                  'result_file': str(target), 'output_artifact_paths': [str(target)]},
              'limits': ['Representation-only finite controls.',
                        'No complete exchange, accounting assessment or runtime conformance evidence.']}
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'passed': report['passed'], 'controls': len(results),
                      'assertions': len(checks), 'failures': failures[:8], 'output': str(target)}))
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())

ACTIVE ARCHITECTURE INDEX (current fields, historical bounded-work metadata omitted):
{"schema_version":"accdsl.proposal.p16.v1","phase":"P16","status":"integrated_candidate_pending_independent_review","review_scope":"Nine proposed contract groups and connected initial profile; recent bounded historical acceptances preserved. New integrated direct candidate is document-checked, not independently accepted.","limitations":"Nine contract groups and proposed initial profile now exist. Finite document arithmetic and exchange checks do not implement runtime modules, establish accounting/forecast validity or supply human acceptance. P17 still owes source-grounded methods, real-package and E05 conflict evidence, sector/group/standards transitions and official adapter inspection; P18 manuscript and P19 readiness remain. Fourteen decisions have proposed answers/evidence/owning phases; proposal blockers remain explicit pending substantive review and later obligations.","contracts":[{"id":"evidence","inputs":"Immutable SourceVersion bytes and derivative hashes; located package units and reference edges; contextual numeric and narrative readings; interpretation, assumption and review records as E1–E4 specify.","outputs":"Separate acquisition, reviewed-assertion and query-exposure populations; admitted or unresolved predicates, conditional assumptions, faithful displayed values, conflict sets and query-specific issues.","invariants":"Preserve original bytes and contextual assertion identity. No semantic closure from file counts; no constraint or probability from extraction acceptance; no nearest-rounding interval from precision alone; no duplicate semantic count merely from repeated content.","failure_behavior":"Retain missing/ambiguous/unavailable/resource-exhausted references and affected queries; reject integrity/context mismatches; expose conflicts and unsupported predicates; invalidate current descendants while retaining old views.","alternatives":"Aggregate completeness versus three denominators; implicit narrative constraints versus scoped admission; inferred half-unit intervals versus source-supported or explicitly assumed rounding.","chosen_reason":"The proposed separation prevents acquisition and accepted reading from overstating financial meaning while allowing named conditional analysis and unaffected queries.","interactions":"Consumes and preserves exact domain versions under architecture-integration-v1 and interfaces I1–I5; platform wrappers preserve native receipts, admission, joint dependencies and immutable views. P17 supplies source-grounded method implementations as specifications, without runtime execution.","requirements":["MC01","MC02","MC03","MC04","MC27"],"gaps":["G2","G11","G17"],"specification":[{"path":"docs/design/proposal/architecture/evidence-contract-v3.md","sha256":"688dab1b7f194eb89abf789c70326463892f41d7893662a8b720300cb393801f","locator":"E1–E5; corrected source locator"},{"path":"docs/design/proposal/architecture/e05-source-investigation-v1.md","sha256":"259532f27292e717bf11fcf7355f7cb94964f58ddc2dc7147365e3f55d4b68c1","locator":"Admission predicate; three inspected groups; bounded conclusion"},{"path":"docs/design/proposal/architecture/e05-conflict-walkthrough-v1.md","sha256":"f8cdc84482aa320a86d6738bf243dc6704151298e1ee423045084a9377f21802","locator":"synthetic layer transitions, ownership, invalidation, alternatives and limits"},{"path":"docs/design/proposal/architecture/architecture-integration-v1.md","sha256":"29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1","locator":"Cross-contract ownership, precedence, status mapping and dependent company outputs"}],"fixtures":[{"path":"docs/design/proposal/architecture/evidence-fixtures-v3.json","sha256":"ee78e644774c8c1371a969f65a68d9a3d3d443afe6df67ee3e5c6e4e7027d042","locator":"unchanged expected semantics, corrected source locator"},{"path":"docs/design/proposal/architecture/e05-conflict-fixtures-v1.json","sha256":"9e7715a5f7e2e65d6d81673d68749784df76c7b6661418f38a9a93a7c7a48971","locator":"14 specified examples W01–W14; entirely synthetic"}]},{"id":"time","inputs":"Assertion economic/reporting intervals, public availability and exact-byte linkage, ingestion receipts, review snapshots, context/version graphs, query admission mode and independent selection mode.","outputs":"Selected and excluded assertion IDs, unresolved candidates with reasons, archival qualifications, conditional harmonised derivations, and admitted interval arithmetic with exact lineage.","invariants":"No publication-to-ingestion fallback; no later eligible version erases an earlier view; date precision remains explicit; eligible supersession is selective and acyclic; arithmetic requires compatible context and revision basis.","failure_behavior":"Distinguish absent/null ingestion, unverified receipt/bytes and unknown publication; reject malformed timezones, hash mismatch and invalid lineage; return unresolved intraday dates/conflicts and unsupported authority-dependent transitions.","alternatives":"Permissive archival exploration versus strict claim-specific historical evidence; combined latest switch versus orthogonal admission/selection; start-of-day/date guesses versus conservative end-of-interval qualification.","chosen_reason":"Public availability and system possession answer different questions. Explicit evidence requirements and orthogonal selection support both without manufacturing missing history.","interactions":"Consumes and preserves exact domain versions under architecture-integration-v1 and interfaces I1–I5; platform wrappers preserve native receipts, admission, joint dependencies and immutable views. P17 supplies source-grounded method implementations as specifications, without runtime execution.","requirements":["MC05","MC04","MC25","MC27"],"gaps":["G13","G17","G18"],"specification":[{"path":"docs/design/proposal/architecture/time-contract-v2.md","sha256":"3064ee8dde2c93543ffcaf7b1357d6ca1f6c8d50e61e2a2aea14b190b014cccd","locator":"T1–T6"},{"path":"docs/design/proposal/architecture/architecture-integration-v1.md","sha256":"29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1","locator":"Cross-contract ownership, precedence, status mapping and dependent company outputs"}],"fixtures":[{"path":"docs/design/proposal/architecture/time-fixtures-v2.json","sha256":"052548f4485d252bda467c218ce2955acbec1f717ed505dc64e183ca4025edf1","locator":"base_records; selection_cases; arithmetic_cases; transform_cases"}]},{"id":"history_families","inputs":"Immutable evidence/review/time view with candidate-membership revisions; complete observation contexts and interpretation alternatives; declared assumptions; opening economic/accounting state; versioned template and mapping applicability; model scope/exclusions and source obligations; target-layer query, resolution, explicit search budget and continuation manifest (H1).","outputs":"Joint conditional trajectory family with shared economic IDs; view union/intersection and parent-linked projection; candidate or validated witnesses and retained continuous regions; separate existence, declared-search and economic-scope status; complete formulation flag, source dispositions, reproducible cell/continuation identities and query-dependent grouping/refinement evidence (H2–H4).","invariants":"Joint dependence survives dates/accounts/views; overlap creates neither duplicate histories nor probability mass. Constraint admission preserves source/assumption/treatment distinctions. Witness existence, exhaustive declared search and scope adequacy are separate. No unsupported required constraint is dropped. Economic memory and full unresolved regions remain recoverable; changed semantic manifests create new family versions.","failure_behavior":"Reject invalid context/identity/composition; distinguish candidate violation, proved model infeasibility, unknown, unsupported operation/treatment, exhausted budget and cancellation. Preserve committed partial work and original unresolved formulas. Reject stale continuation or inapplicable grouping; frozen access stays historical. Missing authority cannot create an admissible accounting branch (H3–H5).","alternatives":"Matched continuous x+y=100 example compares joint symbolic regions, finite witness enumeration and independent marginal intervals. Finite enumeration is exact only for a separately declared finite universe; independent intervals lose the joint constraint. Proposed region representation does not itself prove construction or solver completeness (H6; HF16).","chosen_reason":"A jointly constrained family with explicit scope, dependencies and partial-search evidence preserves the requested financial alternatives without inventing independence, probability or complete reconstruction. H4 derives one narrow grouping and rate/maturity counterexamples; numerical backends and general aggregation remain unselected.","interactions":"Consumes and preserves exact domain versions under architecture-integration-v1 and interfaces I1–I5; platform wrappers preserve native receipts, admission, joint dependencies and immutable views. P17 supplies source-grounded method implementations as specifications, without runtime execution.","requirements":["MC08","MC09","MC10","MC11","MC02","MC04","MC05","MC18","MC25","MC27"],"gaps":["G1","G16"],"specification":[{"path":"docs/design/proposal/architecture/history-families-contract-v1.md","sha256":"87140fbbbbd9137d792f22ed92e92d274a0a1cf9b2c332f2e743df2d92bcc3bd","locator":"H1–H7; proposed semantics and local derivations"},{"path":"docs/design/proposal/architecture/architecture-integration-v1.md","sha256":"29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1","locator":"Cross-contract ownership, precedence, status mapping and dependent company outputs"}],"fixtures":[{"path":"docs/design/proposal/architecture/history-families-fixtures-v1.json","sha256":"56461d0011fbd954106d77602d6a2b02a3712a3ebb2cad597422b3f756d5efa1","locator":"HF01–HF18; synthetic specified inputs/outputs, no runtime evidence"}]},{"id":"uncertainty","inputs":"Versioned evidence/time/admission/family/view and optional joint-law attachment; declared conditions, observation blocks and likelihood models with consumed-information lineage; typed history/scenario/path/date outcome queries.","outputs":"Immutable candidate conditional/posterior views and complete receipts; separately typed weighted distributions, feasible sets, per-history laws and partial outcomes retaining unresolved mass. Each weighted child has its own governing derived law and candidate attachment; downstream requests require an explicit admission receipt.","invariants":"No invented weights or independence; elementary outcomes counted once; information consumed once across constraints, priors and likelihoods; zero normalization is undefined; prior views and full requested domain preserved; computational completion is not economic conditioning.","failure_behavior":"Ordered field/binding/admission/law/reuse checks; atomic rejection preserves parent and submitted bytes; explicit undefined zero denominator, unsupported model/capability and dependency-scoped unresolved outcomes. Corrections rebase and replay from a retained unaffected view.","alternatives":"Linked immutable family/law records versus self-contained joint packages under identical finite semantic inputs; joint likelihood versus justified conditional factorization; weighted mixture versus unweighted family answers distinct questions.","chosen_reason":"Provisional shared semantic identities plus portable self-contained export make evidence reuse and revision traceable. Exact finite arithmetic illustrates semantics, without selecting ownership, probability default or initial profile.","interactions":"Consumes and preserves exact domain versions under architecture-integration-v1 and interfaces I1–I5; platform wrappers preserve native receipts, admission, joint dependencies and immutable views. P17 supplies source-grounded method implementations as specifications, without runtime execution.","requirements":["MC08","MC09","MC10","MC11","MC12","MC13","MC14","MC18","MC25","MC27","MC33","MC34","MC35"],"gaps":["G1","G6","G15","G16"],"specification":[{"path":"docs/design/proposal/architecture/uncertainty-contract-v1.md","sha256":"77010c686d06d398b60e6fa861089f54ec628571770ff7eab12cea4194a7ed0a","locator":"Sections 1–6; integrated proposed uncertainty operations; independent review pending"},{"path":"docs/design/proposal/architecture/uncertainty-admission-contract-v1.md","sha256":"756bb611300b39e558e5f4274369e09135eb98b1e26531d8577ee6f7f9ad7a16","locator":"U1–U6 retained category admission"},{"path":"docs/design/proposal/architecture/uncertainty-measure-attachment-contract-v2.md","sha256":"3812e0f1f28f8bd77fbbd38f1b9b79810346a42ed47a42532b95d9aeb4a5a0b3","locator":"A–F retained attachment/event semantics"},{"path":"docs/design/proposal/architecture/uncertainty-chaining-contract-v1.md","sha256":"58be776f6587bf83b34157b8f9e8041189654bd47028134b40582c5087214d78","locator":"Sections 1–5 and target-context clarification; replaces governing-law meaning of legacy UC01 UC02 UC08 children"},{"path":"docs/design/proposal/architecture/uncertainty-rejection-status-contract-v1.md","sha256":"cc5ec2bd69cf4ba0bf4f0d7fb6e6d668cf7975244afa4464fbb7e412c4eeee8c","locator":"Sections 1–4: five pre-evaluation rejection corrections; bounded independent result review pending"},{"path":"docs/design/proposal/architecture/architecture-integration-v1.md","sha256":"29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1","locator":"Cross-contract ownership, precedence, status mapping and dependent company outputs"}],"fixtures":[{"path":"docs/design/proposal/architecture/uncertainty-fixtures-v1.json","sha256":"4c7cf8c1bbdc3dce3346747dc13689084b37f80d5547add0619bb8eafab3baf3","locator":"UC01–UC19 and matched_alternative; specified inputs/outputs only"},{"path":"docs/design/proposal/architecture/uncertainty-chaining-fixtures-v1.json","sha256":"70644fee4969843bdfee72e5a3d5a698c3acf1327438df30b8562fda3a949e3c","locator":"Historical immutable predecessor; five rejection expectations superseded by v2 correction map; successful cases retained"},{"path":"docs/design/proposal/architecture/uncertainty-chaining-fixtures-v2.json","sha256":"e96f91d4e26f1cef6691d826952a857f29e004b257e49a6f626c82568a41a488","locator":"Current chaining fixture; explicit corrections and active selection supersede five malformed v1 rejection expectations only"}]},{"id":"accounting","inputs":"Versioned EconomicEvent, opening-state digest, authority/method/evidence/assumption versions, economic time, identity and cutoff; branch identity from history families.","outputs":"TreatmentAssessment with eligible/unresolved/ineligible/outside_scope status; JournalProposal with typed lines and state delta only when eligible; StateTransitionReceipt with lineage, status and commit flag.","invariants":"Eligibility separate from arithmetic; compatible context and source/method lineage; independent event/journal/state reconciliation; atomic journal/state/receipt requirement. Lookup key is entity/book/branch/business-event ID; event version and payload belong to the full request fingerprint. Exact replay returns immutable original receipt before freshness; changed fingerprint conflicts; only new identities face current-opening-state validation. These are specified requirements, not runtime guarantees. Binding supplement B1-B5 requires event/opening branch, event time, opening chart and method authority to equal the corresponding request references by immutable version.","failure_behavior":"Return distinct MISSING_EVIDENCE, UNSUPPORTED_AUTHORITY, TREATMENT_UNRESOLVED, CONTEXT_MISMATCH, ROUNDING_MISMATCH, UNBALANCED_JOURNAL, EVENT_ID_CONFLICT and STALE_OPENING_STATE outcomes. Preserve known facts, rejection reason, submitted evidence and null state delta; retry only after receipt lookup. A binding mismatch rejects before identity lookup, eligibility or freshness, with null request/assessment/journal/delta/receipt, invalid structural status and no change to the four domain components.","alternatives":"Direct balanced posting is a compact baseline but entangles eligibility and mutation. Event-sourced projection preserves history but needs typed treatment and projection timing. The proposed typed shared-IR adapter keeps the four stages and a single atomic receipt boundary.","chosen_reason":"A typed shared-IR handoff preserves method/source identity and branch context while allowing independent eligibility, arithmetic, replay and atomicity checks. The choice remains provisional pending language/IR, persistence and interface contracts.","interactions":"Consumes and preserves exact domain versions under architecture-integration-v1 and interfaces I1–I5; platform wrappers preserve native receipts, admission, joint dependencies and immutable views. P17 supplies source-grounded method implementations as specifications, without runtime execution.","requirements":["MC08","MC09","MC13","MC16","MC17","MC20","MC22","MC25","MC27","MC33","MC34","MC35"],"gaps":["G4","G6","G7","G12","G14","G15","G16"],"specification":[{"path":"docs/design/proposal/architecture/accounting-contract-v1.md","sha256":"5f4416714a04c03d1a96c472742ab37341b607cb401be3710057f009533ae466","locator":"Sections 1-6; proposed EconomicEvent to StateTransitionReceipt handoff"},{"path":"docs/design/proposal/architecture/accounting-replay-contract-v1.md","sha256":"0575dbe1d050c7fe1fc894e344ff22fcfc52f81e4c0450b87af1218d369910f2","locator":"Proposed supplement; lookup key, fingerprint, validation order, immutable receipt and matched comparison"},{"path":"docs/design/proposal/architecture/accounting-records-contract-v1.md","sha256":"09a759c0cfd4e94ef1dda19b81ab0db287df63258e0c19f44a6b2f6fb0ac96e5","locator":"Complete finite acquisition records and six observable outcomes"},{"path":"docs/design/proposal/architecture/accounting-bindings-contract-v1.md","sha256":"2886ccda0680137b1351e65ec01bdc295c7e486e3673c719d5f5e7669b6b3fd9","locator":"Exact input relationships; rejection and ordering; six design examples"},{"path":"docs/design/proposal/architecture/accounting-eligibility-dossier-v1.md","sha256":"5b5fa718b997d53dc43530cf30b4451a78c06b6e0b468aaa28313e0027ba7f84","locator":"Bounded acquisition preconditions; conditional synthetic assessment only"},{"path":"docs/design/proposal/architecture/accounting-eligibility-decision-supplement-v1.md","sha256":"b3fde2435f6ce4de3386a884321fed5b1a93a0b26d49da4f3f8b1eb31f942d46","locator":"Nine new finite assessment examples and complete valuation table; pending independent substantive review"},{"path":"docs/design/proposal/architecture/accounting-integration-typing-contract-v1.md","sha256":"070f28768e50b0c5260a671be645e2fc2b53aea373d3eca4e0ed7a9d8299f877","locator":"Integer record versions, opaque condition-source versions, matched correction and limits"},{"path":"docs/design/proposal/architecture/accounting-integration-rejections-contract-v1.md","sha256":"5c9ccc94438828001afc4c7cf841945032f6732c77d96ead09a43e1ce42c22dd"},{"path":"docs/design/proposal/architecture/accounting-integration-source-reason-types-v1.md","sha256":"cf9677316bbfbe486255739c84ba0f14abec4475f7da8d775faa19f45009eb2c","locator":"Decision and amendment precedence; Local findings and their derivation"},{"path":"docs/design/proposal/architecture/accounting-integration-source-reason-types-matrix-v1.json","sha256":"c5bce691f025a6b21ee92ede740f52ef2a7c35c8efb5601f540078fc23b52b83","locator":"rows F154/F169/F182/F194/F229/F261; predicate_dispositions"},{"path":"docs/design/proposal/architecture/accounting-integration-c05-c07-conditions-v1.md","sha256":"55227651862d9d8b1f0dbc16a773946ed6a5d726aed699355ccc6309ce27bf79","locator":"Fields and precedence; ordered guarded diagnostics"},{"path":"docs/design/proposal/architecture/accounting-integration-c05-c07-conditions-matrix-v1.json","sha256":"e9ffef5fdee23478710d50a928db729ba4f4d1c3e793f253b3103ebb77293806","locator":"F211/F219/F243/F248/F253"},{"path":"docs/design/proposal/architecture/accounting-integration-c03-conditions-v1.md","sha256":"20ce189e2ed1413040e95a6987817b43a7cd2f78c125a7961860163bab6a7f96","locator":"C03 bounded specification and finite exchanges; accounting-integration-c03-conditions-v1.md"},{"path":"docs/design/proposal/architecture/accounting-integration-c03-conditions-matrix-v1.json","sha256":"9e9e2bb4bc2e03f5c6c08b47dc6b57f6b2fc0002ecee9bf87a68cb85dcca6465","locator":"C03 bounded specification and finite exchanges; accounting-integration-c03-conditions-matrix-v1.json"},{"path":"docs/design/proposal/architecture/accounting-integration-c09-c10-conditions-v1.md","sha256":"1f6b00093cdae23685a4ea938bf08994dd603eaaed3693dfb7a2b7d5ae1f8ce1","locator":"C09/C10 finite field slice; accounting-integration-c09-c10-conditions-v1.md"},{"path":"docs/design/proposal/architecture/accounting-integration-c09-c10-conditions-matrix-v1.json","sha256":"829a1b4d21860e1a03d73577d82132557e2e3c47b1ca1db761e2a87c6d7f380e","locator":"C09/C10 finite field slice; accounting-integration-c09-c10-conditions-matrix-v1.json"},{"path":"docs/design/proposal/architecture/accounting-integration-c09-c10-conditions-field-note-v1.md","sha256":"11ee0e4f5eeebd4266a03202b8692ffcdce6f9d84168077e030fc5c7c62e27f2","locator":"C09/C10 finite field slice; accounting-integration-c09-c10-conditions-field-note-v1.md"},{"path":"docs/design/proposal/architecture/architecture-integration-v1.md","sha256":"29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1","locator":"Cross-contract ownership, precedence, status mapping and dependent company outputs"},{"path":"docs/design/proposal/architecture/accounting-integration-field-validation-v1.md","sha256":"09c6e045a77bb86dbf14fc1ebce37aa77635c62a501f297155979ce84f5a77b5","locator":"299-path inventory and native validation ordering"},{"path":"docs/design/proposal/architecture/accounting-complete-exchanges-v1.md","sha256":"c85637bb5ee53feaa64a0de0d68056bc1c37f0e106354e67c1d726da3fc4fa49","locator":"C01–C10 context predicates, complete exchanges and V01–V16 dispositions"}],"fixtures":[{"path":"docs/design/proposal/architecture/accounting-fixtures-v1.json","sha256":"c4a2b7b0312e2b9ded6139826a54379b5b7bec30bd950b5255674d4d0ae2c2b1","locator":"AC01-AC05; A01/A02 eligible, A03 unresolved, replay and stale-state cases"},{"path":"docs/design/proposal/architecture/accounting-replay-fixtures-v1.json","sha256":"b6f855d3cdff8a6c45d5989cdea04232454a22b68d72f62250a4042004d999ee","locator":"37 concrete records; AR01-AR05 plus separately identified advance setup; supersedes AC04/AC05"},{"path":"docs/design/proposal/architecture/accounting-records-fixtures-v1.json","sha256":"a0b53c737b1415f70fe3565f3a174b1b6ebe9b18b3d81308825327f1bf08db72","locator":"Six complete exchanges R01-R06, typed immutable registry"},{"path":"docs/design/proposal/architecture/accounting-bindings-fixtures-v1.json","sha256":"7403a4fa8b11ca9cd2b3782f016ad653f20a5ed74df8f20e08f3e7e790c3fc6f","locator":"B00 retained R01 control and B01-B05 single-binding counterexamples"},{"path":"docs/design/proposal/architecture/accounting-eligibility-fixtures-v1.json","sha256":"8d61ecfe4005d4652ead2f8a06d74b0340f4735ae83066fec7c19b0ab104c6f3","locator":"Bounded acquisition preconditions; conditional synthetic assessment only"},{"path":"docs/design/proposal/architecture/accounting-eligibility-decision-fixtures-v1.json","sha256":"1d4560136ee9538cf2167c63383a5c54c851c3b8ea65c4bbd60e21a4c01c97db","locator":"Nine new finite assessment examples and complete valuation table; pending independent substantive review"},{"path":"docs/design/proposal/architecture/accounting-integration-fixtures-v2.json","sha256":"234f7e7b31258d9fb3003d617d6b5591c4364c7e1ed4fdb74958524b95ba9acf","locator":"17 corrected assess_only exchanges; retained schema and digest domain"},{"path":"docs/design/proposal/architecture/accounting-integration-typing-map-v1.json","sha256":"5db221f52adad1614a1af7f8901d93e97baff49dac60e041409785fc32bd4f50","locator":"148 old/new record references, 17 evidence-version mappings; never receipt aliases"},{"path":"docs/design/proposal/architecture/accounting-integration-typing-cases-v1.json","sha256":"15d7424abe9260ec149fbcc873e4800d29d358d062344c5652d110eeb2366612","locator":"11 record-version and 7 source-version cases; not full rejection exchanges"},{"path":"docs/design/proposal/architecture/accounting-integration-rejections-fixtures-v1.json","sha256":"4fb80056a460fa1369de66657fe8e84913716050c3ddc46ae3e5d2028a0562de"},{"path":"docs/design/proposal/architecture/accounting-integration-source-reason-types-fixtures-v1.json","sha256":"ee2e22745ac17f90eeed731f51b68131507b0989d8071dd359e507bd4b8ad97c","locator":"cases; aggregate_cases"},{"path":"docs/design/proposal/architecture/accounting-integration-c05-c07-conditions-fixtures-v1.json","sha256":"26026d7bea7d19d9f2fb2fd26fea01dc6f9d73cb9b15d34a56cdb90bbe5f8402","locator":"L001–L077 and X01–X12"},{"path":"docs/design/proposal/architecture/accounting-integration-c05-c07-conditions-verification-v2.json","sha256":"1678b9f42a650c1d0ab33f8aa141b07522b1311449b62d26982b65ca046e0e7d","locator":"passed; checks; derived_results"},{"path":"docs/design/proposal/architecture/accounting-integration-c03-conditions-fixtures-v1.json","sha256":"d19269c337f5851a16560e1b4ee74989fa3dfa4e65b232f413b7372ce81ea2a6","locator":"C03 bounded specification and finite exchanges; accounting-integration-c03-conditions-fixtures-v1.json"},{"path":"docs/design/proposal/architecture/accounting-integration-c03-conditions-verification-v1.json","sha256":"8940283b317bbfd5c9e683f12e17d249564bdaf5d3d2b7d3f7c1979f77f8d216","locator":"C03 bounded specification and finite exchanges; accounting-integration-c03-conditions-verification-v1.json"},{"path":"docs/design/proposal/architecture/accounting-integration-c03-conditions-verification-v2.json","sha256":"f20d077b0bb026efc8d6cc012d33cf8f79b718d67611dc2ab71e27b0babf85fc","locator":"Final C03 finite check, 2582 passed; refresh after precise date-rule provenance correction"},{"path":"docs/design/proposal/architecture/accounting-integration-c09-c10-conditions-field-controls-v1.json","sha256":"f6e50ad7836104b634380ec8d54430cbbf99bf383e5cf8a31c224040b1aeafdd","locator":"C09/C10 finite field slice; accounting-integration-c09-c10-conditions-field-controls-v1.json"},{"path":"docs/design/proposal/architecture/accounting-integration-c09-c10-conditions-field-verification-v1.json","sha256":"68a89ee6f53714b0762c56a9437e2844ed9c14e208b1c6fd5014bf6d8be8cca3","locator":"C09/C10 finite field slice; accounting-integration-c09-c10-conditions-field-verification-v1.json"},{"path":"docs/design/proposal/architecture/accounting-complete-exchanges-v1.json","sha256":"88ddf2281b1fd7588304db1550d56f7d1e6d3d9d3cab0aa84dd117634bc0a3ce","locator":"27 complete new exchanges; 17 retained controls; V01–V16 candidate-derived checks"}]},{"id":"language_ir","inputs":"Typed declarations, source/text bytes, evidence/time views and pinned schema/package signatures.","outputs":"Portable typed records and candidate IR; exact rational values, source maps, capability and admission diagnostics.","invariants":"Required/nullable/unknown fields distinct; Bool is not Int; shared symbols preserve dependence; no global Unicode normalization or legacy rehash; no implicit admission.","failure_behavior":"Reject malformed/types/context/imports; preserve unresolved financial candidates; unsupported formulas remain explicit.","alternatives":"Host-language execution, text-only meaning or shared portable IR with typed/text frontends.","chosen_reason":"Portable typed meaning exposes financial context and effects independent of authoring; no claimed usability or speed ranking.","specification":[{"path":"docs/design/proposal/architecture/language-ir-contract-v1.md","sha256":"e2cdc3c82d34786364ad4180b0b26581bd8b70eeb6179e4ef6e0e150208bdb1f","locator":"Complete proposed contract"},{"path":"docs/design/proposal/architecture/architecture-integration-v1.md","sha256":"29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1","locator":"Cross-contract ownership, precedence, status mapping and dependent company outputs"}],"fixtures":[{"path":"docs/design/proposal/architecture/platform-contract-examples-v1.json","sha256":"0f0e9c0d17e888e094ff39510a6239f4912d3b2fd63591fb2506f13c7ad0c355","locator":"LX01–LX08, PX01–PX08, FX01–FX07, IX01–IX06; specified examples only"}],"requirements":["MC21","MC22","MC23","MC24","MC25","MC26","MC27","MC33","MC34","MC35"]},{"id":"persistence","inputs":"Immutable records/blobs, validated requests, stable identities, expected head/generation and original semantic manifests.","outputs":"Atomic receipts and new states/views; exact replay, correction lineage, checkpoints, migration/export mappings.","invariants":"Single transaction owns event journal/delta/state/receipt; lookup key excludes payload/version; retry before freshness; immutable old views and transitive/candidate-set invalidation.","failure_behavior":"No domain write on rejection/replay; resolve unknown commit under same identity; reject corrupt closure/checkpoint/migration.","alternatives":"Transactional metadata plus blobs versus mutable documents or event-log projections under the same atomicity contract.","chosen_reason":"Proposed one logical writer makes observable behavior precise without selecting a universal database or claiming tested durability.","specification":[{"path":"docs/design/proposal/architecture/persistence-contract-v1.md","sha256":"64930493a2a4683cbb09816f979166b18d27401685fd37772f2aebe35fe1c584","locator":"Complete proposed contract"},{"path":"docs/design/proposal/architecture/architecture-integration-v1.md","sha256":"29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1","locator":"Cross-contract ownership, precedence, status mapping and dependent company outputs"}],"fixtures":[{"path":"docs/design/proposal/architecture/platform-contract-examples-v1.json","sha256":"0f0e9c0d17e888e094ff39510a6239f4912d3b2fd63591fb2506f13c7ad0c355","locator":"LX01–LX08, PX01–PX08, FX01–FX07, IX01–IX06; specified examples only"}],"requirements":["MC21","MC22","MC23","MC24","MC25","MC26","MC27","MC33","MC34","MC35"]},{"id":"interfaces","inputs":"Versioned OperationRequest and typed domain arguments, exact view/signature/profile locks, budget and expected head where applicable.","outputs":"Typed OperationResult/native payload, coverage/unresolved regions, lineage, diagnostics and separate commit observation.","invariants":"Extraction, review, history, uncertainty, accounting and reporting have separate effects; source and method admission cannot be inferred from type shape or arithmetic.","failure_behavior":"Native order and statuses retained; unknown capabilities fail explicitly; partial scope and later information never hidden.","alternatives":"Direct host-object calls or one omnipotent pipeline versus typed staged operations and pinned adapter capabilities.","chosen_reason":"Staged interfaces retain provenance and financial responsibility while remaining independent of local/CLI/service transport.","specification":[{"path":"docs/design/proposal/architecture/interfaces-contract-v1.md","sha256":"a7235c3485e8942a6a0e4251ae893d3f531a7ea601ad62f506a57936975ca491","locator":"Complete proposed contract"},{"path":"docs/design/proposal/architecture/architecture-integration-v1.md","sha256":"29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1","locator":"Cross-contract ownership, precedence, status mapping and dependent company outputs"}],"fixtures":[{"path":"docs/design/proposal/architecture/platform-contract-examples-v1.json","sha256":"0f0e9c0d17e888e094ff39510a6239f4912d3b2fd63591fb2506f13c7ad0c355","locator":"LX01–LX08, PX01–PX08, FX01–FX07, IX01–IX06; specified examples only"}],"requirements":["MC21","MC22","MC23","MC24","MC25","MC26","MC27","MC33","MC34","MC35"]},{"id":"failure_semantics","inputs":"Requested scope, native results, branch/mass coverage, checkpoint and commit observation.","outputs":"Separate disposition, math/computation/admission statuses, typed diagnostics and resumable unresolved regions.","invariants":"No successful-subset renormalization, unknown-to-zero coercion, default-as-solver-failure or infeasibility without proof; preserve native vocabulary.","failure_behavior":"Guard malformed controllers, preserve independent sibling findings; distinguish unavailable/unsupported/invalid/undefined/unknown commit and scoped retry advice.","alternatives":"One success flag or exceptions for all incomplete work versus structured scoped outcomes.","chosen_reason":"Explicit independent dimensions preserve useful partial work without overstating accounting, numerical or forecast evidence.","specification":[{"path":"docs/design/proposal/architecture/failure-contract-v1.md","sha256":"1de4e0151e5c6c8311aa7d4695134c7ee419501384a79ff227c66ad8bb79cdf6","locator":"Complete proposed contract"},{"path":"docs/design/proposal/architecture/architecture-integration-v1.md","sha256":"29fbdc2f42ab45aff4829994db85592228b13907d2ad8676fe5ec5fc32eecfb1","locator":"Cross-contract ownership, precedence, status mapping and dependent company outputs"}],"fixtures":[{"path":"docs/design/proposal/architecture/platform-contract-examples-v1.json","sha256":"0f0e9c0d17e888e094ff39510a6239f4912d3b2fd63591fb2506f13c7ad0c355","locator":"LX01–LX08, PX01–PX08, FX01–FX07, IX01–IX06; specified examples only"}],"requirements":["MC21","MC22","MC23","MC24","MC25","MC26","MC27","MC33","MC34","MC35"]}],"initial_profile":{"status":"proposed","decision_id":"P15-E06","name":"CorporateJointHistory/1 with typed authoring and a bounded matched text fragment","rationale":"Choose connected corporate domain A with authoring variant B from the P15 matched comparison. Exposes operating/financing/history/reporting interactions; keeps banks, insurance, groups/FX and standards method obligations explicit. No cost, speed or usability ranking is claimed.","included":"Annual/interim evidence and separate review/time views; typed portable records; joint affine histories plus finite choices; connected operations, assets, simple finance/equity/tax, exogenous scenarios and full conditional statements; immutable receipts/replay/recovery; optional admitted finite law. Exact boundaries and source requirements are in initial-profile-v1.","excluded":"Initial runtime excludes general nonlinear/continuous inference, causal intervention, calibrated forecast claims, distributed writers, and domain operations without P17 eligible methods. Full bank/insurance/groups/FX/standards designs remain mandatory later proposal obligations. The text frontend initially covers the matched debt/constraint fragment; full corporate typed authoring is required.","acceptance_criteria":"Six connected positive/adverse groups in initial-profile-v1; preserved Northstar joint statements and changed-rate arithmetic; full source-to-result lineage, unresolved coverage and replay semantics; real-filing and authority obligations retained. Structural/document checks are separate from runtime/human/accounting acceptance.","dependency_order":"Records/context/source -> review/time/store -> typed validation and matched text -> history/capability/checkpoint -> eligible corporate/event/accounting methods -> connected reporting/real-filing/recovery -> optional measures/adapters. P17 methods precede P18 manuscript and P19 readiness; implementation remains disabled.","specification":{"path":"docs/design/proposal/architecture/initial-profile-v1.md","sha256":"7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb","locator":"Scope, comparison, six acceptance groups and implementation dependency sequence"},"fixtures":[{"path":"docs/design/proposal/architecture/platform-contract-examples-v1.json","sha256":"0f0e9c0d17e888e094ff39510a6239f4912d3b2fd63591fb2506f13c7ad0c355","locator":"LX01–LX08, PX01–PX08, FX01–FX07, IX01–IX06; specified examples only"}]}}

Additional exact files available to read: docs/design/proposal/architecture/accounting-complete-exchanges-v1.json; accounting-complete-source-packets-v1.json; accounting-integration-field-validation-fixtures-v1.json and the imported registries under that same directory. Inspect their cases, records and imports fields. Do not use an AGREE to imply runtime execution or full mission closure.
