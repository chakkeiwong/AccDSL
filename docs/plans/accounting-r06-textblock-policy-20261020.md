# R06 — text-block validity policy source inquiry

20 October 2026, Asia/Shanghai. P15/P16/P17/P19; MC01–07,MC23–26,MC28–35.
Predecessor:r06-calc11-conditional-20261020.
Output:data/accounting-master/r06-textblock-policy-20261020/.

Question: which additional source duties distinguish the already checked56 XML
fragments from full DTR/XHTML or filing-system text validation? Comparator:
the frozen structural inquiry, whose56 fragments have empty namespaces under
its deliberately neutral wrapper. No content is currently declared invalid.

Evidence contract: inspect the exact DTR structure1.1 candidate recommendation
linked by the retained2021 OIM source, plus pinned Arelle text validation and
its directly referenced content schema/DTD if available. Initial acquisitions:
the linked2018 DTR structure page and arelle/ValidateFilingText.py at existing
commit01f6a4656c2c6551d2f05f31c9d74366d133ee7e. Up to2MiB/45seconds per
attempt, one trusted retry on sandbox/network failure. Bound a dependency
addition only after its actual caller/source reference is inspected.

Primary criterion: source-specific duties, edition/status, exact call branches,
wrapper/namespace/escaping policy and validation/error limitations. Distinguish
general DTR type semantics, a particular filing-system profile, and generic
XHTML document conformance. No current SEC legal/compliance guidance is given.
If a source does not define fragment validity, retain that gap explicitly.
Do not execute imported/acquired code, validators, DTD expansion, external
entities, browser or renderer. Standard-library AST/source checks and bounded
authored structural examples may document distinctions but cannot certify
the56 fragments' full validity.

Intent ledger: determine the smallest source-supported additional validation
contract before any installed runtime. Expected failure: a whole-document or
filing-system rule is mislabeled as general DTR acceptance. Promotion requires
exact source/edition support. Missing dependency or unchosen profile vetoes
that dependent validity claim, not continued source inspection. Protection
failure or uncontrolled execution vetoes continuation. Counts explain scope.

| Choice | Provenance / reason | Failure / early diagnostic | Status |
| --- | --- | --- | --- |
| DTR CR2018 dependency | Actual link in retained OIM | Call it a recommendation/current edition; inspect status/header | Source baseline |
| Existing Arelle pin | Already selected reuse inquiry | Import latest or execute code; exact URL/hash/static read | Baseline |
| Neutral structural wrapper | Frozen earlier diagnostic | Infer invalidity from empty namespace; preserve original evidence | Comparator only |
| Filing-system policy separate | Possible validator specialization | Mistake local profile for DTR semantics; inspect caller/config | Required distinction |

Skeptical audit passes after excluding a generic XHTML conformance verdict and
holding all installed execution. Premortem: valid XML and a successful profile
check can still violate another required policy; specify every source boundary.
No accounting acceptance, full schema/OIM validation or whole-row closure.

CPU-only standard library;CUDA_VISIBLE_DEVICES=-1
/home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B. Single prepare/build/check/
record lifecycle; no-flag replay afterward. Preserve3.44/396/not_ready,53/6/46,
HEAD/index,36 dirty paths,empty staging. Four live controls and additiveR08 only.
No installation,runtime,empirical run,commit,outreach,publication or fees.
