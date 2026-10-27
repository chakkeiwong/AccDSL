# Retained Text values and declared-type interpretations

20 October 2026. MC01–06, MC23–26, MC28–35; P15/P16/P17/P19.

All 157 selected Text occurrences support the narrow base-type and facet
interpretations recorded here. The selected set contains 14 booleans,
17 durations, one date, one recurring month/day, 77 strings, 23 normalized
strings and 24 tokens. The actual paths cover 112 concepts and 35 type nodes;
14 custom restricted nodes carry enumerations, character-length constraints
or one of five inspected pattern families.

The original packet calls these values UnvalidatedText and the portable
records call them Text. All 157 preserve the same decoded source text.
Neither tag identifies the schema value space. This separate interpretation
does not replace either record or create a processor-supplied value.
Whitespace processing changes none of the selected 157 spellings, although
the fixture evidence demonstrates the difference among preserve, replace
and collapse.

For booleans, false and 0 denote false. Testing whether their strings are
nonempty computes a different quantity. For durations, the separate record
retains the sign and year/month/day/hour/minute/second components. The source
defines a partial order: a month and 30 days have no universal equality.
The local calendar illustration gives 31 days from 1 January to 1 February
2024 and 29 days from 1 February to 1 March 2024. No fixed days-per-month
conversion, canonical duration equality or financial event date is inferred.

The observed date, 2024-09-28, has no timezone and denotes a one-day interval
on the nontimezoned timeline in the inspected specification. The observed
gMonthDay, --09-28, recurs annually and does not assign a year. The local
date checker supports positive four-digit unzoned dates; timezone, negative
year and longer-year forms return outside_scope. This is an explicit subset,
not a rejection of those valid source forms. Gregorian membership is checked
against independent standard-library date arithmetic in the supported range.

String restrictions are checked on their specified whitespace-processed
values. Enumeration alternatives are kept together, lengths count characters,
and pattern membership is whole-string. The inspected name/category rules
use an explicit ASCII subset; general Unicode name and initial-character
membership remains unknown. Python's Unicode digit/category defaults do not
stand in for a complete XSD pattern engine.

Passing these checks leaves consequential nonfacet obligations. Fifty-six
text-block occurrences inherit documented requirements for unescaped XML
nodes/XHTML content. Sixteen enumeration-set occurrences retain domain and
set-semantics obligations. Their string/pattern membership is supported here,
while those separate conditions remain not checked. No full schema/XBRL,
embedded-markup, installed-processor or financial validation was performed.

Nineteen bounded specification passages and thirteen input bindings support
the result. The verifier passes 529 explicitly counted assertions, including
71 base-type fixtures, 32 pattern fixtures and 13 altered-record controls.
The latter expose invalid booleans/durations/calendars, omitted enumeration
or length restrictions, malformed names and changed candidate text. There
were no new acquisitions or acquired code executions.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept 157 separate narrow interpretations | Actual source text, declaration paths, supported base values and facets agree | No selected facet failure or protected-byte mismatch | XML/XHTML and enumeration semantics remain unvalidated | Preserve the interpretations alongside original Text records | Fully valid facts, installed values or accounting meaning |
| Keep calendar/duration scope explicit | Component and unzoned forms match the inspected source rules | Invalid supported forms rejected; valid unsupported forms stay outside_scope | General timezone/year handling and duration equality/order are not implemented | Use a distinct future contract for any broader conversion | A fixed days-per-month rule or inferred timezone |
| Continue R06 preparation | A distinct semantic gap has been reduced | No global continuation veto | Nonfacet duties and installed conditions remain open | Audit the specific remaining content/domain duties against retained evidence | Whole-row closure or proposal acceptance |

Engineering evidence is retained-byte/path correspondence and fixture
behavior. The mathematical interpretations are bounded local formalizations
of the inspected historical specification. No stochastic experiment, method
ranking, financial measurement test or forecast validation occurred.

Post-run red-team: the strongest misleading inference would be that no
remaining value facet means all semantic requirements have passed. The
explicit 56/16 residuals prevent that conclusion. A different effective
type, overlooked source restriction, source-specific pattern counterexample
or incorrect character normalization would overturn the affected narrow
finding. Independent processor behavior and full content semantics are
the weakest basis for extrapolation because they were not tested.

The separate R08 supplement preserves Version 3.44, 396 pages, not_ready,
53 obligations, six interactions and 46 operations, with zero whole-row
closures. All original Values and validation flags remain unchanged.
Future replay: verify.py without flags. Completed stages are one-time.
