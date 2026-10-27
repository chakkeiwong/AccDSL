# Bounded P18 types integration review

You are an independent read-only reviewer. No tools, files, commands, edits or further reviewers. Review only this self-contained packet, not the whole proposal.

Check portable values, interface and encoding integration against accepted architecture. Look for conflicting normative historical grammar, wrong operation or Ref shapes, lost schema boundaries, Unicode normalization or integer/rational mistakes. Do not demand runtime implementation.

Accepted P16 architecture and P17 scoped methods are comparison baselines, not proof of full readiness. The candidate builds (122 pages, zero serious LaTeX warnings); render inspection is separate. Current ASC, whole real-company semantics, insurance transition/full VFA, actual regulatory/actuarial data, and human acceptance remain open. Do not label those honestly retained gaps a new P18 transcription failure. Source provenance is frozen; no new literature search is claimed.

Budget the review to finish in one response. Give at most 6 concrete findings, each with exact file/section and necessary repair, plus a brief reason for the verdict. Focus first on material mismatches; do not perform or narrate an exhaustive re-derivation of every case. Limit your final answer to 1000 words. End with exactly VERDICT: AGREE or VERDICT: REVISE. AGREE accepts only this packet's integration scope, with any minor nonblocking findings explicitly labelled.


## FILE docs/design/proposal/manuscript/chapters/06-language.tex

\chapter{The accounting language}
\label{ch:language}

\section{Scope of the first language}

The historical AccDSL Core 0 proposal describes entities and books, accounts, observations, shared
unknowns, constraints, alternative interpretations, contract instances,
accounting rules and reporting mappings. It has pure expressions and a
restricted posting effect. Economic forecasting algorithms can live in typed
plugins; unrestricted numerical code does not need to be reimplemented in
the DSL. The historical grammar in Appendix~\ref{app:contracts} fixes the preserved
teaching examples. The proposed portable records and first company profile
below define the new authoring boundary; the first matched text frontend
supports the declared debt fragment.

The compiler has six ordered stages: parsing with source locations; name and
module resolution; type and temporal-context checking; lowering to the IR;
constraint and rule-applicability analysis; and execution-plan construction.
The compiler never silently supplies an economic assumption to make a program
compile. A program can be valid as a historical representation while requiring
additional assumptions before a particular simulation can run.

The language's meaning is defined by its IR and evaluator, rather than by the
surface spelling alone. Formatting changes cannot change a model's semantic
hash. A changed source span or reviewer decision changes evidence provenance
even if the numerical model remains the same. The system therefore maintains
separate evidence, semantic-model and execution identifiers.

For the preserved Core 0 examples, the complete grammar is supplied as
\code{spec/core-0.lark}; the original design directory retains
\code{spec/core-ir.schema.json} and \code{spec/core-contract.md}. They define reference resolution, expression arity,
type/context checks, operations, failures and identity. Structural schema
validation alone does not establish those semantic properties. ASCII
identifiers and UTF-8 strings are used in this revision; currency suffixes,
dates and decimal literals have explicit lexical rules. The grammar is checked
by parsing the complete demonstration file, not by claiming that its parser
also implements a compiler or solver.

\section{Types that protect meaning}

\begin{longtable}{L{40mm}L{96mm}}
\toprule Type & Meaning and checks\\\midrule\endhead
\code{Money<C>} & Exact amount in currency C. Addition requires identical
currency; conversion requires a dated rate and policy.\\
\code{Quantity<U>} & Units of shares, goods or other commodities. Quantities
cannot be added to money or used as a functional-currency posting.\\
\code{Rate<B>} and \code{YearFraction} & Rate with basis B, plus a separately
computed accrual fraction. Simple and compound accrual functions are distinct.\\
\code{Instant}, \code{Period}, \code{Calendar} & Instant observations and
flows over intervals; interval operations preserve calendar conventions.\\
\code{Account<K,Book>} & Account role K and owning book. Cross-book effects
require separate balanced batches linked by an economic event.\\
\code{Observation<T>} & Source assertion with contextual and precision
metadata; accessing its value retains its constraint and provenance.\\
\code{Symbol<T,D>} & Shared unknown with domain D; repeated references denote
the same value in a history.\\
\code{Choice<E>} & A finite structural choice over enumeration E. No probability
is implied.\\
\code{Distribution<T>} & Explicit probability measure with parameter,
conditioning and measure metadata. It is not a Symbol or a Choice.\\
\code{SourceRef}, \code{RuleRef}, \code{ModelRef} & Versioned evidence or
implementation references; unresolved references prevent concrete execution.\\
\code{Measurement<T>} & Value plus valuation date, basis, method, assumptions
and numerical status. Recognition remains a rule decision.\\
\bottomrule
\end{longtable}

Core expressions use exact integers and rationals, Boolean logic, enumerations,
dates, records, lists, comparisons and registered pure functions. A decimal
literal is parsed exactly, not first converted through binary floating point.
Numerical plugins can return approximate measurements, but must declare their
error or numerical status and the rounding used when posting money.

Missingness is a tagged type with distinct values: \code{notDisclosed},
\code{notApplicable}, \code{unreadable}, \code{withheld}, and
\code{unresolvedMeaning}. Zero is an ordinary known number. A missing datum can
be replaced by a declared Symbol or assumption in a model branch; the source
observation stays missing. An unknown is not necessarily random, and an
estimate is not necessarily missing.

Addition of monetary observations also requires compatible entity, perimeter,
time, dimensions and basis. These checks operate on contextual expressions in
addition to the currency type. An analyst can deliberately aggregate dimensions
or transform a basis using an explicit function. For example,
\code{sumOver(segment, ...)} records the dimension being removed and requires
the segment partition to be declared; it does not assume every disclosed
segment total is additive.

\input{sections/portable-values}
\section{A small model with a continuous interpretation family}

The following source uses a synthetic observation whose full context is stored
in the evidence registry. The example imports the demonstration debt package,
which uses one-year simple accrual, no fees and immediate rate resets. It is
not an IFRS rule package.

All dependencies are instantiated in
\code{fixtures/demo-debt-package.json}: the source reading, balanced opening
state, currency precision, contract state and dates, reset and interest
operations, closing and report mappings, request and expected outputs.
\code{fixtures/borrowing.acc} is the complete source, including the retained
earnings account and an \code{opening} declaration. The shorter listings below
explain its declarations in stages. They do not replace that full source.

\begin{lstlisting}
module BorrowingExample version "1";
use DemoDebt version "1";
source note7 = external("synthetic-note-7");
entity Acme functional USD;
book Local entity Acme basis DemoDebt version "1";
account Cash : Asset book Local;
account Debt : Liability book Local;
account InterestExpense : Expense book Local;

observation debt : Money<USD> instant @2025-12-31
  = 100 USD from note7;
symbol alpha : Real in [0, 1]
  because "The fixed-rate proportion is not disclosed";
\end{lstlisting}

The remaining declarations use this same unknown fraction in both loan
components. A change to the fraction therefore changes the whole debt mix
consistently.

\begin{lstlisting}
let fixedPrincipal = alpha * value(debt);
let floatingPrincipal = (1 - alpha) * value(debt);
constraint split:
  fixedPrincipal + floatingPrincipal == value(debt);

contract loans : DebtMix book Local {
  principal = value(debt);
  fixed_fraction = alpha;
  fixed_rate = 0.05 per year;
  initial_floating_rate = 0.05 per year;
}
alternative allFixed { assume alpha == 1; }
alternative allFloating { assume alpha == 0; }
scenario rateShock {
  set market_rate = constant(0.07 per year);
}
\end{lstlisting}

The parent model retains every $\alpha\in[0,1]$. The two named alternatives
are useful conditional views of that family, not a declaration that the
endpoints exhaust it. Requesting the parent family's exact bounds produces
$[5,7]$ for the next year's expense in this simple model. Requesting a
conditional run of \code{allFixed} supplies $\alpha=1$. Requesting a weighted
mixture requires a separate weight model; the two labels do not create equal
weights.

An observation declaration is a reference to evidence plus a proposed typed
reading. The compiler checks that the registry context agrees with the declared
period and type. If the evidence is rounded, \code{value(debt)} denotes a
shared constrained value rather than a silently exact 100. This synthetic
registry explicitly declares an exact value, which keeps the illustration
deterministic.

\begin{minipage}{\linewidth}
\section{Posting rules and explicit exceptions}

An event type declares the information needed by a rule. The example below
assumes an event representing interest accrued and paid on the same date.
Separate accrual and settlement events are needed when those dates differ.

\begin{lstlisting}
event InterestPaid(principal: Money<USD>,
                   rate: Rate<annual_simple>,
                   fraction: YearFraction) book Local;

rule recogniseInterest for InterestPaid as e
when e.principal >= 0 USD {
  let charge = roundMoney(simpleInterest(e.principal, e.rate, e.fraction),
                         currencyScale(USD), "half_even");
  require charge >= 0 USD;
  post {
    debit InterestExpense charge;
    credit Cash charge;
  }
}
\end{lstlisting}
\end{minipage}

The rule cannot perform file I/O, mutate another entity or sample a random
number. It returns a proposed batch. The runtime verifies balance and all
preconditions before committing state. Negative interest requires an explicit
supported rule; it is not mishandled by this intentionally restricted example.
Rounding is a declared demonstration convention, not a universal accounting
default.

Rules can declare \code{overrides ruleName}. The resulting override graph
must be acyclic. For a concrete event, the evaluator determines all applicable
rules and removes any that are overridden by another applicable rule. Exactly
one maximal rule must remain for a required recognition operation. An empty
set of applicable rules produces \code{UnsupportedTreatment}; more than one
maximal rule produces
\code{RuleConflict}. File order and a hidden numeric priority never break ties.

If a guard depends on a symbolic value, the solver partitions the current
feasible family into the guard and its negation, subject to the existing
constraints. This is a logical partition, not a random draw. An incomplete
solver returns \code{UnknownApplicability}, not a guessed rule. Statically
provable disjointness or total coverage can be cached; otherwise the runtime
performs the same checks on every concrete event.

\section{Alternative readings, assumptions and updates}

An alternative adds constraints and possibly a supported semantic mapping to
its parent model. Its record contains a rationale, supporting spans, opposing
evidence, author, creation time and scope. Child alternatives inherit all
parent constraints; they cannot quietly discard an inconvenient disclosure.
A deliberate source rejection is a separate review decision with an explicit
reason and a new evidence view.

Two independent alternatives may coexist, while two mutually exclusive readings
of the same text require an explicit choice group. The representation stores
these relationships in a constraint graph. It does not take a Cartesian
product blindly. For example, interpreting an instrument as a liability affects
both its balance-sheet account and the treatment of its periodic payments;
those choices must be linked through one shared treatment variable.

New evidence narrows an existing family by conjunction when it concerns the
same definitions and reporting basis. If it changes the basis or corrects an
earlier assertion, the system creates a revised evidence view and records the
relationship. Posterior reweighting, when enabled, is a separate operation
with likelihood provenance. A branch that becomes inconsistent is retained
as historically considered and rejected, with the evidence that rejected it.

\section{Modules and stable intermediate representation}

A package identifies its namespace, semantic version, dependencies, effective
dates, jurisdiction, supported entity classes, recognition operations and
measurement policies. Standard packages define allowable treatments; industry
packages add economic objects and specialised rules; company packages map
source concepts and declare evidenced elections. A company extension cannot
override a mandatory standard rule merely because its package is loaded last.
An override is valid only at a declared extension point and within the selected
standard's policy domain.

The IR has separate node classes for evidence, contextual observations,
expressions, domains, constraints, alternatives, contracts, economic events,
measurement results, rules, journal batches, report mappings and runs.
Each node has a stable identifier and explicit input references. No expression
stores executable host-language text. Plugins are referenced by versioned
identifiers with typed signatures. This permits a second implementation to
execute the same supported program without evaluating arbitrary embedded code.

The IR serialisation version is independent of the DSL version and of any
accounting-standard edition. Migrations preserve the original payload and
record changed meanings. A syntax migration can be automatic when semantics
are unchanged. A changed recognition policy requires a new model version,
even if the source file still parses.

\begin{minipage}{\linewidth}
\section{Errors are part of the interface}

The compiler and runtime return typed diagnostics with a source span,
affected entity and period, dependency chain and suggested local action.
The principal diagnostic categories have distinct recovery paths:

\begin{center}
\begin{tabular}{L{61mm}L{75mm}}
\toprule Diagnostic & Meaning and next action\\\midrule
\code{TypeMismatch}, \code{ContextMismatch} & Resolve incompatible units,
periods, entities or measurement bases; do not coerce implicitly.\\
\code{MissingEvidence} & Supply a source or label a model input as an assumption.\\
\code{InfeasibleHistory} & Inspect the conflicting evidence and model
constraints; preserve the rejected candidate.\\
\code{RuleConflict}, \code{UnknownApplicability} & Resolve rule scope or
preserve a justified conditional partition.\\
\code{UnsupportedTreatment} & Add a reviewed capability or leave the affected
output incomplete.\\
\code{UnbalancedBatch} & Reject the atomic update and diagnose the posting rule.\\
\code{SolverIncomplete}, \code{NumericalFailure} & Preserve the target and
inputs; repair or change the computational method.\\
\code{InsufficientSimulationState} & Add declared conditional assumptions or
request a family of results.\\\bottomrule
\end{tabular}
\end{center}

Warnings can describe low extraction confidence or an approximate economic
model, but they do not replace these errors. A required unknown input prevents
a concrete unconditional result. The analyst can add a declared conditional
assumption, request bounds, or leave that output incomplete. Every path has a
different, explicit result type; there is no generic fallback to zero.
\end{minipage}\par


## FILE docs/design/proposal/manuscript/sections/portable-values.tex

\section{A portable record has an exact meaning}
\label{sec:portable-record}

A constructor and a textual frontend can describe the same financial model
only if they exchange values whose identity is independent of a Python object
or an incidental JSON writer. The proposed portable record therefore has six
fields: \code{kind}, \code{schema}, \code{key}, \code{revision}, \code{body} and
\code{dependencies}. Kind and schema identify a registered version; key is its
stable logical name; revision is a nonnegative integer. The body obeys that
schema's required, optional and nullable fields. Unknown fields reject.

A typed reference has exactly kind, schema and digest. The digest covers the
complete target record. Every body reference is also listed in dependencies;
additional dependencies need a schema-declared role. The submitted closure is
finite and acyclic. A receipt can refer to its request and old state, but the
old state cannot refer forward to that receipt. Stable business names can
relate counterparties without creating a cycle of content references.

Financial quantities use a reduced rational with signed numerator text $n$ and
positive denominator text $d$, with $\gcd(|n|,d)=1$ and zero represented by
$0/1$. The decimal token 2.50 therefore denotes $5/2$ exactly. Revisions,
ordinals and integer counts remain integers; a Boolean is never an integer.
Approximate measurements instead retain decimal text, method, error description
and environment. A rounded decimal cannot silently acquire exact status.

An absent required field is invalid. Unknown financial content is an explicit
value with a reason and outstanding evidence references. It can be retained,
but cannot satisfy a method that requires the missing fact. Null is permitted
only where the particular schema gives it a meaning; not applicable, unknown
and zero are distinct. A candidate also differs from a value admitted in a
specific immutable view. Admission checks the actual decision and its ancestors;
wrapping a candidate in an ``admitted'' type is insufficient.

Portable bytes use UTF-8 JSON with ASCII object keys sorted by their byte order,
no insignificant whitespace, no floats, duplicate keys, nonfinite numbers or
invalid Unicode scalar values. Decoded strings retain their code points.
An escaped Unicode character and the same literal character encode equally;
composed and decomposed spellings remain different unless an explicit named
transformation relates them. Global NFC normalisation would silently change
some source text and is therefore not part of this encoding.

The writer emits literal non-ASCII scalars, escapes quotation marks and reverse
solidus, and escapes control characters U+0000--U+001F. It uses the five named
JSON escapes where defined and lowercase \code{\textbackslash u00xx} for the
remaining controls; solidus is not escaped. Integers use minimal base-ten
spelling without plus signs, leading zeroes or negative zero. Dependencies,
module declarations by key, dimensions by axis and explicit all-of/any-of
operand sets are sorted after rejecting duplicates. Other arrays, including
journal lines, event schedules and diagnostic priority, retain order.

With these rules, the record digest is
\[
\operatorname{SHA256}\bigl(
 \operatorname{UTF8}(\text{``accdsl.portable.v1/''}+\text{schema})
 \;\Vert\;\texttt{0x00}\;\Vert\;\operatorname{canonical}(\text{record})\bigr).
\]
This recognises representational identity, not economic equivalence or source
truth. Original documents retain a separate hash of their raw bytes. A blob
reference names that byte hash, algorithm and length; it is not a typed record
reference. A submission record links those bytes to media type, transport and
decoder, preserving a malformed request without pretending it was valid.

Historical Core 0 and replay examples keep their original encodings and IDs.
A declared legacy import retains original bytes, decoder, old identity, portable
output and field-by-field comparison. If one historical record maps to several
portable records, an import mapping names every output and conversion. Import
does not grant financial admission in a new view. This separation permits old
examples to remain reproducible while the proposed portable representation
becomes precise enough for two implementations to exchange.

\section{The first company profile and its authoring boundary}

The proposed \code{CorporateJointHistory/1} profile connects one legal entity and
book per branch to annual/interim sources, revisions, working capital, payroll,
tangible assets, simple financing, an explicitly declared tax model and complete
statements. Its types preserve entity, perimeter and currency even where an
operation is outside this initial scope. A real company cannot become eligible
for the profile by dropping its subsidiaries, leases or contingencies.

Typed constructors must express every included declaration in the portable IR
without opaque Python functions. The initially matched text frontend covers the
bounded debt and constraint fragment. Whole-company textual authoring remains
a subsequent frontend obligation; the whole-company typed model is part of the
initial domain. Thus domain scope and authoring syntax are separate decisions.
The following Core 0 listing teaches the shared debt family under its preserved
historical grammar. It is not a promise that the first new parser supports every
historical declaration.

Backend admission examines expanded expressions. Multiplication of an unknown
quantity by an unknown price is bilinear even when hidden inside a function
called revenue. The initial exact reconstruction fragment admits rational affine
constraints, finite choices and bounded integers under explicit templates.
Unsupported functions return a capability diagnostic. A type-correct historical
representation may therefore be retained even when a requested forecast still
requires an unavailable method or an additional admitted assumption.

The portable \code{CompileRequest} supplies source kind, source bytes or a typed
module, schema and profile references, the full package lock, evidence/time view
and requested capability target. Its stages are strict decoding and source
locations; name/import resolution; dependency and cycle checks; static type and
context checks; admission-layer checks; expanded-operation capability analysis;
and canonical record production. The earlier six-stage workflow describes the
historical Core 0 frontend; it does not add execution planning to this portable
compiler or permit it to call a solver.

The result contains candidate IR, source map, unresolved inputs, capability
analysis and a validation receipt bound to every input. Invalid structure or
types yield no executable IR. Valid structure with an unresolved financial input
can yield a retained candidate whose affected target has execution admission
false. Source maps retain decoded Unicode code-point half-open ranges for text
or constructor paths for typed input. Formatting can change source-map identity
without changing financial-model identity.

For a matched example, both authoring routes must describe debt 100, floating
share $x\in[0,1]$ and conditional interest
$100((1-x)/20+7x/100)=5+2x$. Endpoints are 5 and 7; $x=1/2$ gives 6. Changing
the floating assumption from 7\% to 9\% changes the upper endpoint to 9.
Independent arithmetic is needed because two frontends could share the same
wrong constant. Agreement between them alone does not establish correctness.


## FILE docs/design/proposal/manuscript/chapters/11-contracts.tex

\chapter{Core grammar, records and execution details}
\label{app:contracts}

\section{Preserved Core 0 teaching grammar}

The grammar governing the preserved Core 0 teaching examples is reproduced
from \code{spec/core-0.lark}. It does not enlarge the first matched text
frontend beyond the portable profile described in the body. Names are
case-sensitive ASCII identifiers; strings are UTF-8 with JSON escaping. All
literal words in the grammar are reserved. The companion contract specifies
valid dates, exact rational literals, argument arity, type/context checks and
package resolution. A syntax parse is not semantic validation.

\lstinputlisting[basicstyle=\scriptsize\ttfamily]{spec/core-0.lark}

\section{Required core record definitions}

The historical closed machine-readable definitions remain in the original
design directory at \path{spec/core-ir.schema.json}. They define contexts, source spans,
observations, narratives, coverage units, mappings, partitions, entity/control
records, books, accounts, symbols, choices, expressions, constraints, assumptions,
alternatives, contracts, events, rules, packages, measurements, states,
journals, scenarios, information views, review decisions, evidence views,
model scopes, historical families, probability models, report mappings,
result cells, branches, runs and diagnostics. For those historical records the schema fixes field spelling and structural
shape, and its companion contract fixes reference resolution and operations.
New portable records instead obey the exact versioned contracts introduced in
Chapters~\ref{ch:language}, \ref{ch:execution} and \ref{ch:implementation}.
No historical field list grants new posting authority.

\begin{minipage}{\linewidth}
For example, these selected records reproduce the schema's field names.
Each field is required; a nullable link is represented by explicit null.

\begin{lstlisting}
EvidenceView {
  id, cutoff, system_as_of, mode,
  documents[], observations[], decisions[],
  conflict_sets[][], transforms[]
}
Context {
  id, entity, perimeter, concept, basis, measurement,
  time, unit, currency, taxonomy_version, dimensions[]
}
Symbol {
  id, type, context, domain, uncertainty_kind,
  scope, dependencies[], admission, provenance[]
}
Journal {
  id, event, book, date, accrual_period,
  postings[], rule, measurements[], assumptions[],
  precondition_hash, explanation
}
ResultCell {
  id, context, history_condition, scenario, path, kind,
  value, expression, lower, upper,
  lower_attained, upper_attained, sample_ref,
  certificate, reason, dependencies[]
}
\end{lstlisting}
\end{minipage}

A value is a reduced rational, or a typed symbolic/domain reference. A
posting is nonnegative with its side carrying the sign, in the book's
functional currency. Original units and the valuation reference survive
conversion. Monetary contexts require currency; a period flow requires a
calendar and exclusive end boundary. Historical zero postings may preserve traceability but establish no economic
event. New portable proposals omit zero lines and retain their explanation in
the event and findings instead. The amount may have
finer precision before the declared posting-rounding operation.

Schema validation rejects unknown fields but cannot prove that a treatment
is permitted, a reference points to the correct kind of record, or two periods
are comparable. Those semantic checks precede solver or runtime dispatch.
The structural fixture and complete demonstration source/package are supplied
separately so that a future implementation can check both layers explicitly.
\path{fixtures/core-ir-demo.json} supplies an authored expected lowering;
the reference checker evaluates its selected debt expressions. A general
source-to-IR compiler and complete external-registry validation remain to be
implemented. Domain records retain disclosed display text and rounding rules
alongside their exact bounds.

\section{Typing and partial-information rules}

For expressions $x$ and $y$ in the same currency $C$, the money addition rule is
\[
 \frac{x:\operatorname{Money}\langle C\rangle\quad
       y:\operatorname{Money}\langle C\rangle}
      {x+y:\operatorname{Money}\langle C\rangle}.
\]
Context compatibility is a separate premise for observations. There is no
analogous implicit rule for different currencies. Explicit conversion uses
a dated measurement and records its rate and purpose. A rate-times-principal
calculation is typed through a declared accrual convention; the example's
annual simple rate and year fraction produce money in the principal's currency.

Known expressions evaluate normally. Shared symbols evaluate to symbolic
expressions subject to a joint constraint store. Missing source values cannot
enter arithmetic until the model supplies a symbol or a conditional assumption.
Boolean guards over symbols produce formulas, not the value false. This avoids
the common error in which ``unknown whether impaired'' silently means
``not impaired.'' Division requires a proven nonzero denominator or a
partitioned domain that excludes zero; otherwise the expression remains
unsupported for concrete execution.

Logical queries first require a nonempty feasible family. An empty family
returns \code{Infeasible}; it must not produce vacuous answers to substantive
questions. For a nonempty family, constraint evaluation has three results.
\code{entailed} means every state in
the declared feasible family satisfies the proposition. \code{refuted} means
none does. \code{undetermined} means both remain feasible or the solver has
not decided; the response distinguishes those causes. Probabilistic truth is
a separate query requiring a measure. A language-level Boolean value must
never be inferred from an arbitrary probability threshold.

\section{Operational rule selection}

Let $V(e,h)$ be the applicable rules for event $e$ in concrete history $h$,
after package/date selection and guard evaluation. Let $r\prec r'$ mean that
$r'$ validly overrides $r$ through the declared acyclic graph. Define
\[
 \operatorname{Max}(V)=\{r\in V:\nexists r'\in V\text{ with }r\prec r'\}.
\]
For one required recognition operation, a singleton selects that rule; the
empty set yields \code{UnsupportedTreatment}; a larger set yields
\code{RuleConflict}. Multiple distinct operations, such as measurement and
recognition, are evaluated through separate declared interfaces. A rule that
intentionally produces no postings must belong to a supported non-recognition
event operation, whose economic state effect is still recorded.

Given a selected rule, the evaluator computes all local bindings and
preconditions, emits proposed postings, verifies
Equation~\eqref{eq:posting}, validates account/context restrictions and commits
the event transaction. Failure returns the original state plus a diagnostic.
This defines the atomicity requirement independently of the storage technology.

\begin{minipage}{\linewidth}
\section{Example run request and response}

The following request executes two named conditions under one scenario. It
does not request an aggregate probability distribution.

\begin{lstlisting}
{
  "model": "BorrowingExample@1",
  "evidence_view": "synthetic-2025-exact",
  "starting_state": "after-2025-close",
  "horizon": {"start": "2026-01-01", "end_exclusive": "2027-01-01"},
  "conditions": ["allFixed", "allFloating"],
  "scenarios": ["rateShock"],
  "mode": "conditional",
  "weight_model": null,
  "reports": ["balance_sheet", "income", "cash_flow", "equity", "journals"],
  "package_lock": "demonstration-packages-v1"
}
\end{lstlisting}
\end{minipage}

The response contains two separately labelled results with interest expense
5 and 7, cash 90 and 88, debt 100 in both, and equity $-10$ and $-12$.
A request for the parent symbolic family returns the formula
$7-2\alpha$ and, under exact linear bounds, $[5,7]$ before monetary
quantisation. The API rejects an unconditional mean request without a weight
model. A user can instead request an arbitrary clearly labelled representative
case, which does not stand in for the feasible family.

\section{Requirement traceability}

\begin{center}
\begin{tabular}{lll}
\toprule Requirement & Primary implementation area & Conformance cases\\\midrule
R1 & Evidence registry and extraction adapters & T03, T09\\
R2 & Context/version model and cutoff queries & T03, T04\\
R3 & Types, mappings and package selection & T02, T12, T13\\
R4 & Symbols, choices and constraint graph & T05--T10, T14\\
R5 & Posting, closing and consolidation & T01, T11--T13\\
R6 & Contract and behavioural interfaces & T05, T11, T15, T16\\
R7 & Conditional output and probability types & T06, T07, T18\\
R8 & Explanation graph and report dependencies & T09, T11--T13\\
R9 & Capabilities and versioned modules & T02, T14--T16\\
R10 & Run records, scheduler and replay & T03, T17, T18\\\bottomrule
\end{tabular}
\end{center}


## FILE docs/design/proposal/manuscript/chapters/17-portable-reference.tex

\chapter{Portable operation reference}
\label{app:portable-interfaces}

These proposed versioned operations share the request and result envelope in
Section~\ref{sec:versioned-operations}. Required inputs are explicit even when
a list is empty. An expected head mentioned below refers to the common envelope,
never a second argument. The registry is a lookup reference after the financial
and transaction meanings have been explained in the body. These are specified
exchanges, not deployed endpoints.

\hypertarget{source.prepare1}{%
\section{source.prepare@1}\label{source.prepare1}}

package manifest, source snapshot, adapter/config lock, prior review, traversal budget and optional continuation \ensuremath{\rightarrow} ExtractionPreparation

Acquires/preserves sources and constructs candidates under the source-preparation method; no semantic admission

\hypertarget{review.propose1}{%
\section{review.propose@1}\label{review.propose1}}

target Ref, layer, decision kind, evidence Refs, actor, rationale, replacement Ref or null \ensuremath{\rightarrow} ReviewProposal

Candidate construction; accepts no layer

\hypertarget{review.commit1}{%
\section{review.commit@1}\label{review.commit1}}

ReviewProposal, expected review view/revision \ensuremath{\rightarrow} immutable ReviewDecision and new view

Review transaction under the review and storage rules; admissible action/layer required

\hypertarget{time.select1}{%
\section{time.select@1}\label{time.select1}}

package/view, investor/system/exploratory mode, cutoffs, revision and unknown-time policy \ensuremath{\rightarrow} selected assertions, conflicts and temporal obligations

Pure selection under the time-admission rules; no invented ingestion or publication time

\hypertarget{model.compile1}{%
\section{model.compile@1}\label{model.compile1}}

the versioned CompileRequest \ensuremath{\rightarrow} candidate Module, source map, diagnostics and target admission/capability report

Candidate construction; no solver or posting

\hypertarget{history.construct1}{%
\section{history.construct@1}\label{history.construct1}}

admitted Module, opening, scope, template registry, query/horizon, resource budget \ensuremath{\rightarrow} HistoryFamily, partition, witnesses and unresolved formulas

History-construction contract; witnesses are examples within the family, not its definition

\hypertarget{history.refine1}{%
\section{history.refine@1}\label{history.refine1}}

frozen family, additional admitted constraint or refinement, dependency view, budget \ensuremath{\rightarrow} child family and inclusion relation

Candidate construction; record whether correction replaces constraints instead of intersecting them

\hypertarget{history.query1}{%
\section{history.query@1}\label{history.query1}}

family, typed joint observable, bound/feasibility request, capability manifest \ensuremath{\rightarrow} symbolic/partial/exact answer, coverage and endpoint attainability

Pure; unsupported expressions remain explicit

\hypertarget{uncertainty.evaluate1}{%
\section{uncertainty.evaluate@1}\label{uncertainty.evaluate1}}

exact native uncertainty request, law/attachment/admission and operation-specific event or observation block \ensuremath{\rightarrow} native UncertaintyResult and candidate derived bundle

Native admission/attachment/chaining rules; never selects its result automatically

\hypertarget{uncertainty.admit1}{%
\section{uncertainty.admit@1}\label{uncertainty.admit1}}

candidate bundle, target time/evidence/purpose, actor, rationale, requested assumption scope, expected selection revision \ensuremath{\rightarrow} admitted attachment and decision

Admission transaction; author-stipulated measures keep that label

\hypertarget{uncertainty.select1}{%
\section{uncertainty.select@1}\label{uncertainty.select1}}

admitted attachment/receipt, rationale and expected selection revision \ensuremath{\rightarrow} new selected-view revision

Selection transaction; no probability recomputation

\hypertarget{scenario.project1}{%
\section{scenario.project@1}\label{scenario.project1}}

family, exogenous scenario, policy/method lock, horizon/calendar, explicit information policy, resource budget \ensuremath{\rightarrow} conditional event/journal/state proposals by history and scenario

Candidate construction; budgets preserve unresolved regions; no historical-book commit

\hypertarget{accounting.assess1}{%
\section{accounting.assess@1}\label{accounting.assess1}}

native assessment request, event, opening, context/time, authority/method, evidence/assumptions and admissions \ensuremath{\rightarrow} TreatmentAssessment

Pure accounting assessment; inherited \texttt{assess\_only} profile cannot post

\hypertarget{accounting.authorize1}{%
\section{accounting.authorize@1}\label{accounting.authorize1}}

AccountingEventBasis and posting-profile Ref \ensuremath{\rightarrow} PostingAuthorization

Pure evaluation under a separately supported posting profile; an assess-only result cannot grant posting permission

\hypertarget{accounting.propose1}{%
\section{accounting.propose@1}\label{accounting.propose1}}

PostingAuthorization, AccountingEventBasis and posting/rounding method \ensuremath{\rightarrow} JournalProposal and independent EconomicDelta

Candidate construction; revalidate bindings; unsupported method gives no journal

\hypertarget{accounting.commit1}{%
\section{accounting.commit@1}\label{accounting.commit1}}

AccountingCommitArguments/v1 and envelope expected branch head/generation \ensuremath{\rightarrow} StateTransitionReceipt

Single atomic transaction under the event-commit contract; the separate commit schema, separate from native assess-only

\hypertarget{report.build1}{%
\section{report.build@1}\label{report.build1}}

frozen branch/family result, statement-map version, interval/view, typed requested statements and presentation policy \ensuremath{\rightarrow} joint statement family, reconciliation and coverage

Pure; derive from retained state/journals, no balancing plug or hidden branch selection

\hypertarget{record.explain1}{%
\section{record.explain@1}\label{record.explain1}}

output Ref, its frozen view, requested lineage depth \ensuremath{\rightarrow} source/method/assumption/decision paths and unresolved dependencies

Pure; depth truncation is explicit; cannot substitute today's view

\hypertarget{work.resume1}{%
\section{work.resume@1}\label{work.resume1}}

checkpoint Ref, original semantic manifest, scheduling budget \ensuremath{\rightarrow} operation-specific resumed result

Resume the original operation; checkpoint ownership/atomicity under the durability contract; no model change hidden as resume

\hypertarget{store.export1}{%
\section{store.export@1}\label{store.export1}}

snapshot/root Refs, format/decoder, destination \ensuremath{\rightarrow} closed manifest or explicit incomplete export

Derivative publication under P3; no domain mutation

\hypertarget{store.import1}{%
\section{store.import@1}\label{store.import1}}

closed manifest, exact blobs/records, decoder and target namespace \ensuremath{\rightarrow} import receipt and original-to-local mappings

Verify before metadata transaction; import alone grants no financial admission

\hypertarget{store.migrate1}{%
\section{store.migrate@1}\label{store.migrate1}}

migration request from P5 \ensuremath{\rightarrow} preserved originals, new representation, comparison/mapping and receipt

Transaction only after required semantic comparisons; no changed-model-as-format claim

\section{Closed accounting records}

The following field lists are exact for the named versions. Every reference
uses the portable kind/schema/digest type; plural references are schema-declared
sets. Unknown fields reject. Source and admission sets can be empty only when
the method's admitted assumption scope explicitly permits and explains that.

\begin{lstlisting}
AccountingEventBasis/v1 {
  identity: {entity_id, book_id, branch_key, business_event_id},
  event_ref, opening_ref, context_ref, branch_ref, time_ref,
  chart_ref, authority_refs, method_ref, evidence_refs,
  admission_refs, assumptions_ref, view_ref
}
PostingAuthorization/v1 {
  basis_ref, posting_profile_ref, method_ref, authority_refs,
  status, findings, posting_permitted, evidence_level, view_ref
}
AccountingCommitArguments/v1 {
  basis_ref, authorization_ref, journal_ref, delta_ref
}
\end{lstlisting}

Identity fields are nonempty ASCII names. Each singular reference is nonnull.
Authority references identify applicable support or a specifically typed
synthetic authority for an explicitly synthetic example. Authorization status
is eligible, unresolved, ineligible or outside scope; posting permission is a
Boolean and can be true only for eligible status under a supporting profile.
A branch's immutable book mode is synthetic or real, and a profile names its
supported modes. Synthetic evidence cannot authorize a real-book posting.
Journal and delta both identify the same basis and authorization. Their domain
payloads obey the package's pinned journal and state schemas. No earlier record
refers forward to the final receipt.

\section{Method and extension definitions}

A versioned financial method supplies the following nonempty definitions:
\begin{lstlisting}
MethodDefinition {
  method_id, version, event_kind,
  state_schema, event_schema, journal_schema, delta_schema,
  output_schema, required_contexts, authority_requirements,
  preconditions, algorithm, account_roles, report_mappings,
  numerical_capability, examples, unsupported_cases
}
ExtensionPackage {
  package_key, version, record_schemas, operation_signatures,
  supported_contexts, state_requirements, authority_refs,
  method_refs, capability_requirements, migration_refs,
  example_refs
}
\end{lstlisting}
Each precondition has an identity, typed predicate, required input/admission
references and separate false/unknown consequences. Domain state and event
fields are specified with the financial methods in the body. Schema names and
package members resolve through immutable locks. An empty authority list makes
no accounting-authority claim. Registering a schema does not establish the
method's entity, instrument, reporting-period or probabilistic applicability.
The full machine-oriented contracts and finite exchanges accompany the proposal
in the architecture and methods directories; their exact versions are pinned
by the manuscript's dependency index.


## FILE docs/design/proposal/architecture/language-ir-contract-v1.md

# Portable financial records and authoring, proposed version 1

The portable representation is the meaning exchanged between extraction,
reconstruction, accounting and reporting. Text notation and typed constructors
are two ways of proposing those records. Neither authoring path can create an
accepted source reading, an accounting permission or a probability merely by
constructing a value. This contract addresses MC02–MC14 and MC23–MC27, especially
G2/G3/G12/G15/G18. `platform-contract-examples-v1.json` supplies specified examples;
the companion calculation checks finite consequences, not a compiler.

## L1. Representation and version boundary

A `Record` has exactly `kind`, `schema`, `key`, `revision`, `body`, and
`dependencies`. `kind` and `schema` name a registered, versioned record
definition; `key` is its stable, schema-scoped logical name; `revision` is a
nonnegative JSON integer (never Boolean). `body` conforms to that exact schema.
`dependencies` is a set of typed `Ref` values. A `Ref` has exactly `kind`,
`schema`, `digest`; its target digest covers the entire target record. Links
inside a body are also typed Refs and must occur in dependencies. Additional
dependencies are permitted only with a declared role in the body's schema.
The dependency graph of a submitted closure must be finite and acyclic. A new
receipt refers to its request and prior state; the prior state never refers
forward to that receipt. Stable business keys may refer to one another as names
without creating content-reference cycles.

Each schema declares required, optional and nullable fields separately, and
rejects unknown fields. Omission and null are not synonyms. Unknown scientific
or accounting content uses `Unknown {reason, obligation_refs}`; an absent required
field is an invalid record. A record with unknown content can be retained but
cannot satisfy an operation that requires that content. A `Candidate<T>` is
distinct from `Admitted<T, view_ref, decision_ref>`. Admission requires checking
the referenced decision in the requested immutable view, including ancestors;
possession of the wrapper alone is insufficient.

Quantities use reduced exact `Rational {n,d}` with signed base-ten numerator
text and positive denominator text: no leading plus or zeroes, `gcd(|n|,d)=1`,
zero `0/1`. Decimal source tokens are converted by their base-ten value, never
through binary floating point. Integer metadata and integer counts remain JSON
integers. This separates the old Core 0 phrase “all numeric values are rational”
from record revisions, ordinals and bounded counts. Approximate results instead
use `Approximation {decimal_text, method_ref, error_description, environment_ref}`;
they cannot be substituted into an exact operation without an explicit
approximation policy and its provenance.

New record digests use `SHA256(UTF8("accdsl.portable.v1/" + schema) || 0x00 ||
canonical(record))`. Canonical JSON is UTF-8, sorted ASCII object keys, no
insignificant whitespace and no floats, NaN, infinity, duplicate keys or invalid
Unicode scalar values. Strings retain their decoded code points; JSON escapes
and literal Unicode for the same code point are equivalent. Composed and
decomposed Unicode are distinct unless a named transformation explicitly maps
them. Identifiers are ASCII; financial labels and quoted source text may be
Unicode. This deliberately replaces implicit global NFC normalization in the
exploratory Core 0 proposal: source spelling must not be silently changed.
Raw source identity always hashes original bytes, outside this record encoding.

A `BlobRef` is a distinct tagged object with exactly `kind="blob"`,
`algorithm="sha256"`, `digest` (64 lowercase hexadecimal digits), and
`byte_length` (nonnegative integer, never Boolean). It resolves to exact bytes,
not to a portable record. A `Submission` record has body exactly
`{blob_ref, media_type, transport, decoder_ref}`, with decoder_ref null when
decoding is unavailable. An OperationResult.submission_ref is a typed Ref to
this record; it is not a record digest falsely assigned to raw bytes. Record
dependencies list record Refs; schema-declared BlobRefs are a separate required
byte-closure obligation checked alongside them.

Native unknowns are decoded through a named LegacyImport adapter. A nullable
value with a required explanatory reason maps to an Unknown carrying that
reason and its source/obligation Refs, while retaining the original native
packet/inner/outer reasons in the import. A non-applicable null remains an
explicit NotApplicable variant, never Unknown or zero. Under native C09,
required=true with a null route requires both nonblank inner and outer reasons;
neither replaces the other. A contextual reason on a known value is annotation,
not an unknown. Missing or malformed native fields reject before conversion.
This mapping preserves source statements without giving the converted value
admission in a new view.

Array order is meaningful except for schema-declared sets. In this version,
`dependencies`, module declarations by key, context dimensions by axis key, and
the explicit IR `all_of`/`any_of` operand sets are canonical sets; reject duplicate
keys or members before sorting by canonical UTF-8 bytes. All other arrays,
including event schedules, journal lines, source spans and diagnostic priority
sequences, retain order. Rational reduction and set sorting occur during typed
construction; a purported canonical wire record violating them is rejected.
There is no general algebraic simplification, alias folding or equivalence proof
in hashing. Hash equality supports byte identity under the chosen encoding, not
economic equivalence or source truth.

For byte-level interoperability the serializer emits literal valid non-ASCII
Unicode scalars in UTF-8. Escape only quotation mark, reverse solidus and control
characters U+0000–U+001F: use `\b`, `\t`, `\n`, `\f`, `\r` for their five named
controls and lowercase `\u00xx` for the remainder. Do not escape solidus. Integers
use minimal base-ten text, with no leading plus, zeroes or negative zero. Input
escapes are decoded before canonical output. Object keys are ASCII and ordered
by unsigned ASCII bytes. These rules, set normalization and rational reduction
fix one byte string for every valid typed record; arbitrary JSON writer defaults
are not part of the definition.

Existing `accdsl.replay.v1/*`, uncertainty fixture and Core 0 digests retain
their original encodings. `LegacyImport {format, original_bytes_ref,
original_id, decoder_ref, portable_ref, comparison_ref}` connects them to a new
record. A migration must prove the stated field/value correspondence and retain
both IDs. A two-decimal acquisition fixture is not a general two-decimal money
rule. No historical digest or receipt is rewritten to fit this proposal.

When conversion produces multiple records, portable_ref points to an
`ImportMapping` record with exactly `{outputs, field_mappings}`. Outputs is a
nonempty schema-declared set of typed Refs. Each field mapping has source_path,
target_ref, target_path and relation (`equal_decoded_value` or
`explicit_conversion`); the latter additionally requires conversion_method_ref.
The LegacyImport comparison_ref covers every output and mapping. This supports
A6's CorrectionBasis plus InvalidationReport without overloading a single Ref,
and records branch_id → branch_key as an equal-decoded-value field mapping.
No mapping authorizes source facts or accounting treatment in a new scope.

## L2. Financial types and context

The primitive types are Bool, Int, Rational, Text, Date, Timestamp, Ref<T> and
explicit tagged Unknown. Containers are Option<T>, homogeneous List<T>,
schema-declared Set<T>, records and tagged unions. Bool is not Int. Dates use
valid Gregorian days; timestamps require an offset and retain the original
precision. Timestamp comparison uses the time contract's interval interpretation.

The financial types include `Money<currency>`, `Quantity<unit>`,
`Rate<convention>`, `YearFraction<calendar, convention>`, `InstantValue<T>` and
`Flow<T, [start,end)>`. Every contextual value carries a Context Ref identifying
legal entity, book, perimeter version, basis, currency/unit, economic instant
or reporting interval, calendar and a set of dimensions. Source locators,
reported display scale and reading provenance are retained alongside the value;
they do not silently change its arithmetic magnitude.

Addition, subtraction and comparison require equal financial types and
compatible contexts. A source scale is applied once during reading, while its
original value and spelling remain available. Entity, perimeter, basis,
currency, time or dimension changes require a named transformation with input
and output contexts, method, assumptions and evidence. `sumOver` removes an
axis only under a pinned disjoint/exhaustive partition. `convert` requires a
dated rate, purpose and measurement method. No label similarity converts IFRS
into US GAAP; the standards method must supply a transformation or report that
the comparison is unresolved.

An opening and closing stock cannot be added as flows. Deriving an interim
flow by annual-minus-prior-interim requires compatible interval endpoints,
perimeter, basis and revision view. Precision does not create an error tolerance:
nearest-rounding intervals require source support or an explicit admitted
rounding assumption. A displayed 100 at unit scale may conditionally denote
`[199/2,201/2)` only under the declared tie convention; unknown convention
remains unknown, and different tie rules have different endpoint inclusion.

## L3. Expression and model records

An Expression has `key`, `type`, nullable `context_ref` and one discriminated
operator payload. Literal carries one typed value; ref names one declaration;
negate/not take one operand; add/subtract/multiply/divide/comparisons take two;
`all_of`/`any_of` take nonempty operand sets; field takes a record and field key;
call carries a pinned operation Ref and ordered arguments. Each operator's
payload excludes the other payloads. Boolean expressions remain formulas when
their shared symbols are unknown; Unknown values are never coerced to false.

Multiplication by a dimensionless scalar preserves a financial type. A rate is
not dimensionless: simple interest requires principal, annual rate and an
explicit year fraction. Division requires a nonzero denominator; inability to
establish nonzero is an unresolved precondition, while an established zero
gives undefined mathematics. Backend admission classifies the expanded formula,
not the spelling of a function call. Symbolic products are not rational-linear
merely because the surrounding function has an accounting name.

A Module contains declaration sets for contexts, sources, readings,
interpretations, assumptions, symbols/domains, constraints, choices,
contracts/events, measurements, rules, scenarios and reports, plus a package
lock. Every symbol has one uncertainty category, type, domain and admission
dependencies. Reusing its key means the same unknown in every linked expression.
Global constraints apply to every alternative; a choice-local constraint stays
inside that named choice. Alternatives are joined under the history contract's
specified union/intersection, not silently intersected or independently selected
account by account. No declaration automatically creates a probability measure.

An OperationSignature declares input/output types, context relationships,
preconditions, postconditions, failure codes, effects, capability and method/
authority dependencies. Effects are one of pure calculation, candidate
construction, source acquisition, review proposal or requested transaction.
An accounting rule proposes an assessment/journal/delta; it cannot commit.
Opaque callbacks or arbitrary host-language execution are not portable IR.
Extension packages must declare record schemas and signatures, export hashes
and the unsupported-operation response; unknown required semantics cannot be
ignored. Names are qualified by package and version; no mutable “latest”.

The portable initial exact fragment permits rational affine constraints over
real unknowns plus explicitly finite discrete choices and bounded integers.
Negative rates are permitted when the operation's economic domain permits them;
the P03 nonnegative-rate restriction is not inherited globally. Unsupported
nonlinear, unbounded discrete, distribution or calendar methods return the
requested operation and missing capability. Partial linearization is a new
assumption-labelled model, never an exact solution of the original formula.

## L4. Compilation and matched authoring

`CompileRequest` supplies source kind (text or typed construction), source bytes
or typed Module, schema/profile refs, full package lock, evidence/time view and
requested capability target. Compilation performs, in order: strict decode and
source spans; name/import resolution; dependency/cycle checks; static types and
context checks; admission-layer checks; expanded-operation capability analysis;
canonical record production. Each stage returns all independently decidable
diagnostics in stage/path/code order. Dependent checks are `not_evaluated` with
their blocking diagnostic; they are not additional guessed type errors.

`CompileResult` returns candidate IR, source map, unresolved input obligations,
capability analysis and a validation receipt bound to every input. Invalid
structure/types produce no executable IR. A well-typed module can have unresolved
financial inputs: return a retained candidate and `execution_admitted=false` for
affected targets. Compilation does not call a solver, choose a history, post a
journal or turn source acceptance into method eligibility.

The bounded text notation retains Core 0 lexical/precedence rules and its
registered declarations. Unsupported syntax is diagnosed; textual support is
advertised per declaration/signature. Typed constructors produce the same
abstract declarations; arbitrary Python objects or lambdas are not accepted.
Both frontends pass through the same typed IR admission rules. Text positions
are Unicode code-point half-open ranges in retained source bytes after a named
decode; typed positions are constructor paths. Source maps are outside model
semantic identity, but their own content hashes bind the exact authored source.
Formatting and comments may change a source-map ID without changing the model.

LX01 specifies matched text and typed declarations for debt 100, shared unknown
floating share x in [0,1] and interest `100*((1-x)*1/20+x*7/100)`. Both propose
the same financial expression and its explicitly conditional stress assumption.
Its expanded interest is `5+2x`; endpoints are 5 and 7 and x=1/2 gives 6.
The shared domain is continuous, not two equally probable cases. LX02 changes
7/100 to 9/100, so the upper endpoint becomes 9: frontend agreement alone would
miss a shared wrong constant, hence the independent arithmetic. LX03–LX08 reject
currency/context mixing, absent admission, symbolic nonlinearity at an exact
linear backend, duplicate keys and unknown imports. These are proposed expected
exchanges; the document calculation is not evidence of a completed compiler.

## L5. Alternatives and consequences

The old small text compiler and typed library are useful feasibility evidence,
but neither settles the portable representation. JSON records are proposed
because they are inspectable and already match retained evidence; a binary
encoding is permissible as a lossless transport with a specified decoder.
Embedding executable Python is rejected as the governing representation because
it leaves side effects, evaluation order and unknown handling outside a shared
contract. XBRL remains an evidence interchange, ledgers carry concrete postings,
and inference languages implement selected methods; none by itself preserves
all the required evidence, joint histories and accounting admission layers.
No authoring, performance or maintenance superiority has been measured.


## FILE docs/design/proposal/architecture/interfaces-contract-v1.md

# Operations across the financial model, proposed version 1

The interfaces connect an acquired disclosure to a proposed reading, an admitted
financial model, alternative histories and conditional statements. Each operation
names the version it consumes and the authority it needs. In particular, an
extraction service cannot accept its own interpretation, a valuation service
cannot authorize accounting, and a report cannot commit journals. This contract
addresses MC01–MC27 and MC33–MC35, with the software obligations of MC29–MC32.
It specifies exchanges; it does not provide runtime endpoints.

## I1. Common request and response

`OperationRequest` is a portable L1 record with schema
`accdsl.operation.request.v1`. Its body has exactly:

| Field | Required type and meaning |
| --- | --- |
| `operation` | Qualified operation name from I2; no implicit version selection |
| `request_id` | ASCII identifier, stable across retries of the same request |
| `workspace_key` | ASCII identifier for the store namespace |
| `profile_ref`, `signature_ref` | Exact profile and operation-signature Refs |
| `view_ref` | Immutable evidence/review/time view Ref; never a mutable `current` alias |
| `arguments` | Closed tagged record for the named signature, with fields in I2 |
| `execution` | `{mode, budget, environment_ref}`; mode is `specification_example` or `runtime`; budget explicitly states operation count and elapsed-time limits or a reason each is inapplicable |
| `expected_head` | Null for a read, or `{owner_key, state_ref, generation}` for a requested mutation |

All fields are present. Null is allowed only where stated. A caller asking for
the current view first resolves it and receives its revision; mutation compares
that revision again. Arguments contain typed Refs and typed values, never
arbitrary host-language objects. Required closure is the transitive closure of
request dependencies plus schema/package definitions in its lock. A missing
optional source attachment remains a named coverage obligation; a missing
required rule, record, admission or decoder rejects affected use. Schema version,
argument type or unsupported operation is diagnosed before calculation. A
request fingerprint covers the exact portable request, including expected head,
generation, request_id and execution settings; accounting's historical
fingerprint is retained by an explicit legacy adapter, not recomputed as this one.

`expected_head` occurs only in the common envelope. References to an expected
head or revision in the signature table below mean that envelope field, not a
duplicate argument. For accounting its owner is the entity/book/branch and
state_ref is the opening state; for review its owner is the review namespace
and state_ref is the review view; for uncertainty selection its owner is the
family/evidence/time selection and state_ref is the selection record. In each
case generation is that owner's monotone revision. Retry after unknown commit
resubmits the original expected head/generation and all original request bytes.
Refreshing the expected head constructs a different request and must never be
used to disguise a retry. Lookup precedes current-head freshness.

Accounting idempotency uses only P2's business-event lookup namespace.
request_id is correlation metadata, not a second accounting lookup index, though
it remains part of the complete fingerprint. Reusing it for a different
business-event key does not alias the events; changing it for an already
committed event changes the fingerprint and conflicts. Source/review/selection
mutations use their separately specified operation/workspace/request namespace.
The new branch_key maps to the native branch_id value through an explicit
LegacyImport binding, preserving the original entity/book/branch/event tuple.

`OperationResult` has exactly `submission_ref`, `request_ref`, `operation`, `input_view_ref`,
`disposition`, `statuses`, `payload`, `diagnostics`, `coverage`, `unresolved`,
`continuation_ref`, `commit_observation`, `receipt_ref`, and `evidence_mode`.
References are typed. `submission_ref` identifies the preserved exact submitted
bytes and transport/decoder metadata through L1's Submission record and BlobRef;
it always exists when submission retention succeeds, even when decoding fails.
If the retention store itself fails before writing it, return an out-of-band
transport failure carrying the original client correlation and no purported
OperationResult or committed outcome. The caller still retains its submission.
`request_ref` is null until a typed request passes all input validation, including
binding/admission/authorization before lookup. An input rejection, including
AX02's false posting permission, therefore keeps request_ref null even if typed
decoding succeeded. A separate optional audit record links the retained
Submission and diagnostic candidate bytes, never a purported validated request.
Output-producer rejection after successful input validation retains request_ref.
`operation` and
`input_view_ref` are null when the corresponding validated identities are not
available; a diagnostic may quote the untrusted submitted values. Continuation
and receipt references may also be null. `payload` is a tagged
union selected by the signature; rejected input has null payload. `diagnostics`
and `unresolved` are ordered lists (possibly empty). `coverage` contains the
requested domain Ref and completed/unresolved/unsupported/infeasible/cancelled
region Refs, with their partition/overlap relation. Reads may use one singleton
request region; they cannot invent an economic-family denominator. When request
validation prevents establishing the requested domain, coverage is null with
the blocking diagnostic; it is not an empty completed domain. `statuses`
and disposition obey F1. `evidence_mode` repeats specification/runtime, so an
expected `complete` in a document never asserts runtime execution.

`commit_observation` describes the mutation requested by this operation:
`committed`, `not_committed`, or `unknown`. A read returns `not_committed` even
when it inspects an earlier committed receipt. Accounting's replay payload may
say the original event is committed while the outer result says this invocation
made no new commit. The payload must carry `additional_commit=false`; this is
not a contradiction. A successful review or checkpoint mutation has its own
receipt and is never described as an accounting posting.

Transport status and financial status are independent. An HTTP error or client
timeout is not evidence of noncommit. A local Python, CLI or service binding
must preserve the same argument values, input versions and result union. There
is no required network deployment, server framework or user interface in P16.

## I2. Operation signatures and ownership

In this table each listed input is required unless explicitly marked optional.
Lists are explicit even when empty. Domain records retain the detailed fields
in their named contracts; the table does not replace them with untyped prose.

| Versioned operation | Arguments → payload | Effect and controlling contract |
| --- | --- | --- |
| `source.prepare@1` | package manifest, source snapshot, adapter/config lock, prior review, traversal budget and optional continuation → ExtractionPreparation | Acquires/preserves sources and constructs candidates under extraction-v1; no semantic admission |
| `review.propose@1` | target Ref, layer, decision kind, evidence Refs, actor, rationale, replacement Ref or null → ReviewProposal | Candidate construction; accepts no layer |
| `review.commit@1` | ReviewProposal, expected review view/revision → immutable ReviewDecision and new view | Review transaction under evidence E4/persistence P4; admissible action/layer required |
| `time.select@1` | package/view, investor/system/exploratory mode, cutoffs, revision and unknown-time policy → selected assertions, conflicts and temporal obligations | Pure selection under time T1–T6; no invented ingestion or publication time |
| `model.compile@1` | CompileRequest from L4 → candidate Module, source map, diagnostics and target admission/capability report | Candidate construction; no solver or posting |
| `history.construct@1` | admitted Module, opening, scope, template registry, query/horizon, resource budget → HistoryFamily, partition, witnesses and unresolved formulas | H1–H7; witnesses are examples within the family, not its definition |
| `history.refine@1` | frozen family, additional admitted constraint or refinement, dependency view, budget → child family and inclusion relation | Candidate construction; record whether correction replaces constraints instead of intersecting them |
| `history.query@1` | family, typed joint observable, bound/feasibility request, capability manifest → symbolic/partial/exact answer, coverage and endpoint attainability | Pure; unsupported expressions remain explicit |
| `uncertainty.evaluate@1` | exact native uncertainty request, law/attachment/admission and operation-specific event or observation block → native UncertaintyResult and candidate derived bundle | Native admission/attachment/chaining rules; never selects its result automatically |
| `uncertainty.admit@1` | candidate bundle, target time/evidence/purpose, actor, rationale, requested assumption scope, expected selection revision → admitted attachment and decision | Admission transaction; author-stipulated measures keep that label |
| `uncertainty.select@1` | admitted attachment/receipt, rationale and expected selection revision → new selected-view revision | Selection transaction; no probability recomputation |
| `scenario.project@1` | family, exogenous scenario, policy/method lock, horizon/calendar, explicit information policy, resource budget → conditional event/journal/state proposals by history and scenario | Candidate construction; budgets preserve unresolved regions; no historical-book commit |
| `accounting.assess@1` | native assessment request, event, opening, context/time, authority/method, evidence/assumptions and admissions → TreatmentAssessment | Pure accounting assessment; inherited `assess_only` profile cannot post |
| `accounting.authorize@1` | AccountingEventBasis and posting-profile Ref → PostingAuthorization | Pure evaluation under a separately supported posting profile; an assess-only result cannot grant posting permission |
| `accounting.propose@1` | PostingAuthorization, AccountingEventBasis and posting/rounding method → JournalProposal and independent EconomicDelta | Candidate construction; revalidate bindings; unsupported method gives no journal |
| `accounting.commit@1` | AccountingCommitArguments/v1 and envelope expected branch head/generation → StateTransitionReceipt | Single atomic transaction in P2; schema in cross-contract-amendment-v1, separate from native assess-only |
| `report.build@1` | frozen branch/family result, statement-map version, interval/view, typed requested statements and presentation policy → joint statement family, reconciliation and coverage | Pure; derive from retained state/journals, no balancing plug or hidden branch selection |
| `record.explain@1` | output Ref, its frozen view, requested lineage depth → source/method/assumption/decision paths and unresolved dependencies | Pure; depth truncation is explicit; cannot substitute today's view |
| `work.resume@1` | checkpoint Ref, original semantic manifest, scheduling budget → operation-specific resumed result | Resume the original operation; checkpoint ownership/atomicity in P3; no model change hidden as resume |
| `store.export@1` | snapshot/root Refs, format/decoder, destination → closed manifest or explicit incomplete export | Derivative publication under P3; no domain mutation |
| `store.import@1` | closed manifest, exact blobs/records, decoder and target namespace → import receipt and original-to-local mappings | Verify before metadata transaction; import alone grants no financial admission |
| `store.migrate@1` | migration request from P5 → preserved originals, new representation, comparison/mapping and receipt | Transaction only after required semantic comparisons; no changed-model-as-format claim |

Compilation and history queries may be pure with respect to committed accounting
state while producing immutable candidates in a scratch or candidate store.
Persisting those candidates requires the named owner and receipt. The effect
classification is not a promise that no bytes are written anywhere.

## I3. Scenario information and joint statements

The initial `ExogenousScenario` specifies dated values or formulas for named
drivers, their domains, units, admissibility assumptions and dependencies. An
`InformationView` exposed to a policy or measurement operation contains only
admitted historical information up to its decision instant and permitted
simulated past. Future simulated values are withheld, even when the scheduler
already knows the full imposed path. Deterministic stress does not by itself
authorize perfect-foresight decisions; a separate assumption must do that.
Observational conditioning uses the uncertainty interface. A causal intervention
requires a specified causal model/replacement operation and is unsupported by
the initial exogenous profile.

The result remains indexed by history, admissible treatment and scenario. Every
statement amount refers to that common index, opening and event sequence.
Cash flow, profit, balance sheet and equity movement are reconciled jointly.
Reporting may return separate conditional answers or a pushforward of an
admitted law. It cannot create one statement from independent minima/maxima
that occur in incompatible histories. Aggregating an axis requires a pinned
disjoint/exhaustive partition or returns an unallocated residual with a reason.
An unsupported tax/lease/FX method makes dependent lines unresolved; unaffected
amounts remain available with their dependence stated.

## I4. Extension boundary and adapters

An `ExtensionPackage` declares `{package_key, version, record_schemas,
operation_signatures, supported_contexts, state_requirements, authority_refs,
method_refs, capability_requirements, migration_refs, example_refs}` and pins
every member. Empty authority lists mean no accounting-authority claim, not
universal eligibility. Callers verify the method's dated entity/instrument/basis
scope and uncertainty admission separately from schema loading.

Corporate records retain receivable/payable terms, inventory lots and cost
method, assets and depreciation memory, tax bases, leases, debt/equity rights
and contingencies. Groups retain legal entity, control evidence, dated perimeter,
ownership/NCI, functional/presentation currencies and elimination links. Banks
add cash-flow terms, effective rate, credit-risk stage, default/cure history,
collateral/guarantees and prudential-rule context; prudential capital is not
accounting equity. Insurers add coverage units, cohort/group eligibility,
fulfilment cash-flow assumptions, discount/risk adjustment, CSM/loss component,
reinsurance and service history. These are structural obligations; P17 must
specify their method fields, transitions, authority and matched cases before an
operation using them becomes supported.

An extraction adapter returns located candidates; a contract scheduler returns
dated contractual events; a valuation adapter returns a quantity with method,
currency/date and numerical evidence; an accounting method returns an assessment
and proposed entries; a ledger adapter exchanges concrete entries/receipts.
None inherits another's authority. Each adapter manifest identifies upstream
version/license, supported subset, input/output schema mapping, calendar/unit/
rounding transformations, preserved lineage, information loss and unavailable-
backend behavior. Lost economically relevant fields veto that exchange. Retaining
raw upstream output permits inspection but does not repair lost meaning.
P17 owns pinned official-interface/license inspection and executable adapter
feasibility; existing exploratory tool presence is not completed integration.

## I5. Precedence and versioning

The active P16 architecture index pins its contracts. Domain-specific validation
and accounting/uncertainty vocabulary take precedence within their versioned
native interfaces. Platform v1 adds explicit wrappers and cross-contract rules;
it does not rewrite saved native receipts. `architecture-integration-v1.md`
records status mapping and the precise historical rules that are superseded.
A later amendment prevails only for the fields and profile it expressly names;
date alone or a file named “latest” grants no precedence.

Two conflicts are resolved explicitly. The stable accounting event key is P2's
entity/book/branch/business-event key, not an event-version or transient-run key.
For native assessment validation, the established parse → recognizable
dependencies → shape → source versions → bindings sequence prevails over a
generic platform ordering. A wrapper may reject its own malformed envelope
first; it cannot expose a receipt before native validation. New portable-only
operations use F2's order. This preserves historical outcomes without letting
the old generic Core 0 contracts silently select defaults for new domains.

IX01–IX06 in the shared example file cover a connected company, changed stress,
an unresolved operating input, later-information rejection, overlapping report
classes and a sector call without an eligible method. Together with the native
complete accounting exchanges they make the contracts' interaction inspectable.
They specify results; the document calculation verifies only finite arithmetic
and reference consistency. Compatible implementations still require actual
frontend, backend, storage and recovery conformance evidence.
