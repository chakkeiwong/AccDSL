# Formula duplicate binding: conditional support, no processor call count

The 2018 note's two-by-two example is correct as a conditional account of
possible singleton bindings. Its unqualified statement that the rule “will be
evaluated four times” is unsupported as a universal processor-call count.
Variables4/4.1, Value Assertions3 and Validation3 distinguish eligible fact
bindings, different assertion data sets and actual assertion evaluation.
Validation says an assertion **MAY** be evaluated once for each data set.
No processor was run and no performance or repeated-error count was measured.

The claimed target is the note's section5.2 processing account. The quantity
derived here is the number of different possible assertion data sets under
explicit hypotheses. These quantities are different: four logical data sets
do not establish four required physical invocations. The source says different
fact-variable evaluations depend on item identity, not merely equal numbers.
The exact anchors are N-bind, V-eval, V-identical, V-single, A-datasets and T-may
in source-ledger.json. This is a documentary comparison and local derivation,
not an installed-conformance result.

Let A1,A2 be two distinct aspect-matched nonnil nodes selected for variable A,
and B1,B2 the corresponding nodes for B. Fix these source sequences, explicitly
set implicitFiltering=false and bindAsSequence=false, and assume no dependencies,
fallbacks, preconditions or ambiguous aspects. Variables4.1 permits a singleton
choice from each source. The four pairs (A1,B1), (A1,B2), (A2,B1), (A2,B2) differ
in at least one fact-variable node and therefore give four different possible
data sets. This does not validate an actual XML document, filter or XPath test.

The countercases matter. Sequence binding with matches=true includes both
duplicates in each maximal sequence under the stated aspect assumptions, giving
one pair of sequences up to order. With matches omitted/false, aspect-matched
facts cannot share a result; in this same example each singleton is maximal,
so four possible pairs remain. A false precondition or empty source without
fallback can prevent evaluation. Implicit filters constrain compatible uncovered
aspects; they are not a general duplicate-removal operation. Thus neither “each
input occurrence always binds” nor “sequence binding always collapses duplicates”
is a correct general rule. The five symbolic cases and their hypotheses are
preserved in binding-example.json.

Occurrence removal can also change an observable test. In the matches=true
sequence example, the A binding has length2. A mathematical test of whether its
length equals2 is true; after removing A2 its length is1 and that test is false.
This is a cardinality argument, not an executed XPath expression. Formula
source text supplies no general guarantee that removing duplicate occurrences
preserves all assertion results. No information-losing reduction policy follows.

Thirteen bounded requests retained five normative XBRL technical documents,
five official histories, two XDM editions and one errata placeholder. There are
44 exact source anchors,18 claim/rule rows, five symbolic cases, seven inspected
HTML text-node/ancestor captures and six separate research ledgers. Reading is
selected and recorded, not a whole-Formula-family or whole-XDM review. The note
did not supply a Formula technical citation; the retained official index was
the independent discovery source. Its earlier complete inquiry stays frozen.

The undated XDM route returned3.1, Recommendation21March2017. The dated XPath2
XDM source identifies itself as the2010 Second Edition revised7September2015;
its2.3/2.5 identity and sequence wording supports the local distinction. The
separate retained second-edition errata page is only a placeholder. None of this
proves original2009/2010/2015 byte equivalence or absence of all later errata.
Variables AppendixF's header says corrections through9December2010 but includes
a20June2013 entry. Four other technical documents say no errata incorporated
through22June2009. The five retained histories constrain these statements only
within their own tables. Apparent Implicit Filters cross-reference/table wording
drift and the embedded schema's copied non-normative comment are preserved;
no silent correction or schema validation was performed.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept the conditional singleton derivation | Anchored governing rules and explicit hypotheses | Wrong-edition promotion avoided; source dependencies checked within scope | No actual processor trace | Preserve the qualified source comparison | Four mandatory calls, measured slowdown or error repetition |
| Reject universal binding/count and generally safe reduction claims | Sequence/filter/precondition/fallback countercases | Exact matches condition retained | Full suite, XPath/filter and installed behavior unchecked | Keep occurrences and unresolved differences traceable; do not change policy | Full Formula conformance or equivalence after removal |
| Complete this bounded source-preparation unit | Thirteen retained sources, precise reading and ledgers | Protected-byte checks and final replay required | Independent/domain/human acceptance pending | Continue ready internal preparation under a new audited plan | Manuscript, accounting, empirical or whole-row acceptance |

No candidate or research direction was rejected by an execution failure. The
source-account repair qualifies the guidance; it does not invalidate the
retained harness, target or evidence. No continuation veto fired. Four draft
quotation boundaries were repaired before freezing to include complete identity
definitions, sequence constraints and the errata header; anchor-repair.json
preserves the change. The source bodies and substantive conclusion did not change.

The strongest alternative explanation is that a particular processor deliberately
enumerates all four combinations and reports repeated failures. That behavior
would be compatible with the illustrative account, but it remains untested.
An inspected rule requiring a particular complete processing mode or a scoped
processor trace could refine the invocation claim; this result cannot supply it.
Historical edition equivalence and full filter semantics are the weakest limits.

Version3.48 remains401pages and **not_ready**. All53 obligations, six interactions
and46 operations remain; zero whole rows close. All192 vintages remain unadmitted,
and E3/six scientific choices remain unselected. No manuscript or default-policy
change follows. Runtime/controller, installations, empirical campaigns,
acquired-code execution, commits, outreach, publication and fees remain held.
Run-manifest.json records environment, commands, timing limits and artifacts.
No stochastic comparison or statistical ranking was made.
