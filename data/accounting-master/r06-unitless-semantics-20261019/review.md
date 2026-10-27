# Source review and interpretation boundary

The prior unit resolved correspondence for the retained instance schema only.
This unit reads official XML Schema 1.0 Second Edition definitions and joins
them to the existing seven chains. It neither revisits their extraction nor
changes their original source-copy caveat in historical evidence.

The exact research question is selected type interpretation, not full lexical
validation. Claimed target: what the retained declarations imply for seven
known ASCII tokens. Actually computed: declared chain/facet joins, specified
whitespace transformations and narrow membership predicates. They agree in this
selected scope; full XML/XSD/XBRL validity is not checked. A future PSVI-to-
portable mapping remains a distinct engineering decision.

Inspected passage IDs in passages.json are gYear, string, normalizedString,
token, pattern, whiteSpace, year-zero, year-lexical, regex, char-range,
normalization-stage and the three built-in declarations. Raw UTF-8 offsets and
hashes bind every excerpt; text extraction is for reading, not replacement of
the source. Relevant grammar includes full-string matching, concatenation,
star repetition and ordered UCS character ranges. Therefore [0-9] means the
ASCII digits in these selected patterns, not every Unicode numeric character.

The three initial-character-data year tokens have no timezone suffix and are
valid positive four-digit forms under the inspected rule. The illustrative
checker returns no verdict for forms outside that subset. It does not use
int() to construct a calendar value or pretend that absent timezone is UTC.
The use of int() in two counterexamples demonstrates information loss only.

The observed normalizedString tokens contain none of the replaced characters.
For hypothetical XML-legal examples the replace and collapse operations use only
the exact code points named by the source. No generic whitespace function is used
to implement those transformations; Python split() without a separator appears
only as the explicitly rejected NBSP shortcut.

Source acquisition: three bounded trusted curl requests, no redirects, all 200.
The first source's dated-version link identifies the second. Its whiteSpace
section links the third source for normalization timing. The three-URL budget
is complete. No source-wide errata audit or newer standard comparison is claimed.

record_sources.py initially stopped at a misspelled canonical-section anchor,
then at escaped HTML quote spelling. The acquisition ledger had already been
written and was verified equal on continuation; no recorded file was overwritten.
The successful continuation created passages, interpretations and examples once.
No semantic check failure occurred. Actual artifact commands use CPU-hidden
tfgpu Python: verify.py --prepare; record_sources.py (two failed boundaries,
one successful completion); verify.py --check; verify.py --record; verify.py
without flags for fresh replay. Manifest timestamps include tool/approval time.

The next finite source question is available without new downloads: three
retained linkbase/XL/XLink schema headers cite the same 2008-07-02 Appendix A.
Their raw source-copy identity has not yet been checked. Audit those three
comparisons and preserve edition/comment/namespace differences explicitly.
