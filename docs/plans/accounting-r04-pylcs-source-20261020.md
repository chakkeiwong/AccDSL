# R04 — pylcs source and string semantics

20 October2026. P15/P17/P19; MC01–05/23/26/28–35.
Output:data/accounting-master/r04-pylcs-source-20261020/.

Question: what algorithm and character unit does the dependency called by the
current GriTS wrapper implement, and what release/source correspondence is
actually established? The retained pyproject specifies pylcs>=0.1.1; its wrapper
calls pylcs.lcs_sequence_length and divides by Python string lengths. Query
official PyPI package metadata, follow its actual source link, pin the repository
head and inspect only the small source files needed to understand that call.
Do not equate latest repository head with every permitted release or an installed
package. Downloads of distributions, wheels and model/data artifacts are excluded.

Comparator: paper's normalized LCS cell reward versus original SequenceMatcher
expression and current wrapper at8a281a3e2fd4cfa600d1c1f70f33b5eccc6294f1.
The predecessor's finite counterexamples are already complete; do not rerun
them solely to reproduce completed evidence. Source reading can establish a
recurrence and binding contract, but installed equivalence needs separate work.

Evidence contract: primary criterion is reconstructible source support for
the exact LCS recurrence, return type, Unicode/byte unit, and empty handling
on the selected path. A version range is not a lock. Promotion vetoes are
claiming installed validation from source reading, ignoring encoding units,
or transferring code at head to an unverified release. Explanatory diagnostics
are package metadata and source defaults. If source reveals a semantic issue,
record a pre-calculation plan for bounded exact illustrations with an independent
oracle before computation. No empirical ranking or accounting validity follows.

Research intent: expected failure is a different LCS variant, byte/codepoint
mismatch, incomplete Unicode conversion or unresolved release provenance.
Repair trigger is a specific source/target discrepancy, not package adoption.
Missing binding/source identity blocks dependent claims; it does not reject the
research direction. Continuation vetoes remain changed protected bytes or held
runtime/installation/data/empirical activity.

Default audit: PyPI metadata is a discovery source; repository identity and
paths must be checked. Current head is an explicit source hypothesis. No
Unicode normalization/grapheme interpretation is silently added. Non-ASCII
examples must state whether equality is by byte, codepoint or user-perceived
grapheme. CPU-only standard-library Python, GPU hidden; no acquired modules,
build systems, bindings or native code execute.

Skeptical audit passes: algorithm/binding inspection answers a concrete unresolved
dependency contract. The earliest check is the actual PyPI home/source link,
then repository/tree identity. Pre-mortem: a plausible DP in one file may not
be the exported function, or Python len may count a different unit than C++.
Follow the binding and string conversion completely for the selected call;
record uninspected functions and dependencies explicitly.

At most six HTTPS requests,35seconds/2MiB each, with saved headers/bodies/actual
JSON receipts. Use a narrow staged wrapper restricted to the metadata-derived
repository and declared small file selection. No distributions or packages.
Deliver six additive ledgers, result/review, checks and R08 supplement; edit
only four authorised live controls. Preserve3.44/396/not_ready,53/6/46,
HEAD/index/empty staging and36 tracked dirty paths. One-time lifecycle stages;
no-flag replay is read-only. No controller, commit, outreach, publication or fees.
