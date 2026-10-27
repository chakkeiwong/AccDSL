# R06 — selected unitless lexical and value-space interpretation

19 October 2026. P15/P17/P19; MC01–06/23–25/27/30–35.

All seven selected tokens satisfy the narrow lexical checks justified by their
retained type chains and XML Schema 1.0 Second Edition. This establishes neither
full schema validity nor a validated processor value. The frozen portable Values
remain Unknown. A digits-only conversion to Int would be wrong relative to these
declared XML Schema value spaces: four are strings and three are calendar years.

| Facts | Retained token(s) | Source-defined interpretation in the checked scope |
| --- | --- | --- |
| f-57, f-934, f-935 | 2024, 2024, 2062 | Positive four-digit gYear lexical forms with no timezone; Gregorian calendar-year values, not integer quantities |
| f-59 | 0000320193 | token-derived string with exactly ten ASCII digits; the leading zeros belong to the value |
| f-13, f-14 | 95014, 408 | normalizedString values; numeric-looking text does not establish integer or measurement meaning |
| f-1127 | 42 | token-derived string matching [1-9][0-9]*; no leading zero, plus sign or substring matching |

Part 2 sections 3.2.1, 3.2.11, 3.3.1–2, 4.3.4, 4.3.6, Appendix A's built-in
definitions and Appendix F supply the selected semantics. Part 1 section 3.1.4
distinguishes initial character data from schema whitespace normalization. The
live Part 2 reference and its explicitly named 28 October 2004 edition are byte
identical in this acquisition. Three official source bodies/receipts and fourteen
bounded passages are retained; no XML Schema 1.1 rule was imported.

The examples make three information losses concrete. Integer conversion changes
0000320193 to 320193, which no longer satisfies the retained ten-digit pattern.
Converting 00408 and 408 to integers merges distinct string values. Python's
default split/strip family treats a non-breaking space as whitespace, while the
specified collapse operation replaces only TAB/LF/CR and collapses ASCII spaces.
The explicit ASCII range also excludes full-width digits that Unicode digit
predicates might accept. These are counterexamples to proposed shortcuts, not
findings that the frozen translator actually commits those shortcuts.

The checked source defines whole-string pattern matching. The two retained
patterns need only ASCII character-range membership, concatenation and zero-or-
more repetition, which the checker implements directly; it does not substitute
Python regex behavior for general XSD regex behavior. XML Schema 1.0 excludes
0000 as a year. Valid timezone, negative-year and longer-year forms are outside
the implemented illustrative subset and return unknown, rather than being
rejected as invalid. No timezone is inferred for the observed year tokens.

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Deliver seven documentary type interpretations | Seven retained chains join exactly; 22 examples and 76 explicitly counted assertions pass; fourteen passages bound | Eight selected corruption/invalid-conclusion fixtures rejected; no wrong-edition substitution | The complete schema, instance and installed processor have not been validated | Preserve the ledger alongside the frozen Unknown Values | PSVI values, whole-filing validity, inferred financial amounts or production type admission |
| Reject digits-only integer coercion as a declared-type interpretation | String/year value spaces and loss examples establish the mismatch | Leading-zero and non-breaking-space counterexamples survive | A separate domain mapping could intentionally derive an integer, but needs a distinct declared target | Require separate raw text, schema type/value and domain interpretation in a future admitted implementation | That every future integer transformation is forbidden or that current frozen code is defective |
| Continue independent source preparation | Source-copy and selected type gaps advance without runtime execution | No continuation veto fired | Other retained core schema copies and all installed conditions remain unverified | Compare the three retained companion core schemas against the already acquired historical Appendix A | A validated taxonomy or completed R06 |

Engineering evidence consists of deterministic joins, exact source bindings and
finite examples. No stochastic/numerical experiment, ranking or default change
was performed. The result is documentary type interpretation only. All 36 tracked
dirty paths, unrelated contents, HEAD/index, the protected 3.44 PDF and frozen
53 obligations/six interactions/46 operations are preserved. Readiness remains
not_ready; no whole requirement closes.

Post-run red-team: a lexical pass can coexist with invalid context attributes,
nillability, abstract elements, substitution relationships, taxonomy discovery
or financial misuse. The checker assumes the examples are XML-legal character
data and deliberately does not implement XML character validity. The strongest
alternative explanation would be a different effective type/facet or processor
configuration; this result binds the selected retained declarations, not an
unobserved installed choice. A changed source chain requires a new interpretation.

Safe replay: verify.py without flags. Do not repeat completed one-time stages.
