# pylcs selected source: exact LCS with explicit string-unit limits

20 October2026. P15/P17/P19; MC01–05/23/26/28–35.

The selected source implements the standard longest-common-subsequence
recurrence. PyPI metadata identifies pylcs0.1.1 and links kuangkzh/pylcs,
described as a transfer of Meteorix/pylcs. Head
5eee78a655fbe34ef24c8240304646f7cd07543b is pinned; all three acquired source
blobs match its tree. Native reading covers lines1–61 and328–365 only,
including the splitter, LCS function and exported binding. The initializer
and setup.py were read completely. Six source acquisitions and24 anchors are
bound. No package distribution, build or compiled module was executed.

For token sequences of lengths m,n, the source creates a(m+1)-by-(n+1)
integer matrix. Empty prefixes score0. Equal final tokens extend the diagonal
prefix optimum by1; unequal final tokens take the larger optimum after
dropping one token. Induction on prefix lengths establishes exact LCS for the
supplied token sequences, subject to representable integer dimensions and
successful allocation. It uses quadratic DP storage, not a linear-memory
algorithm. The binding exports this function as lcs_sequence_length; the
Python initializer imports it from _pylcs. Substring length is a different
explicitly exported function.

The splitter groups UTF-8 bytes according to continuation-byte boundaries.
For valid UTF-8 encoding Unicode scalar values, each group is exactly one
codepoint's encoding. Under that condition, the token count agrees with Python
string length, and the newer GriTS wrapper's2L/(lenA+lenB) normalization has
consistent units. The selected source performs no canonical normalization or
grapheme segmentation. It is not an invalid-UTF8 validator. Pybind11's actual
Python-to-std::string conversion remains uninspected, so the valid-byte condition
is explicit rather than assumed proven for every public call.

| Fixed pair | Codepoint LCS length | Wrapper reward under valid UTF-8 | Meaning |
|---|---:|---:|---|
| 收入 / 税收入 | 2 | 4/5 | Multibyte encodings count as codepoints |
| precomposed é / e plus combining acute | 0 | 0 | Canonical equivalence is not performed; NFC comparison gives1 |
| woman-ZWJ-laptop / woman | 1 | 1/2 | Multi-codepoint emoji are not indivisible graphemes |
| A-NUL-B / A-NUL-C | 2 | 2/3 | Local valid-byte model retains embedded NUL |
| empty / 收 | 0 | 0 | One empty string has zero shared content |
| empty / empty | 0 | 1 | The wrapper's equality shortcut is a convention |

An independent exhaustive subsequence oracle verifies all six small pairs.
Fourteen selected Unicode scalar values, individually and concatenated, give
15 boundary checks. They supplement the encoding argument; they are not
exhaustive Unicode or native-runtime conformance. Two malformed byte examples
are grouped by the local boundary rule but rejected by strict UTF-8 decoding.
Whether the public binding accepts them remains unchecked. NFC was used only
to explain a different target, not selected as a data-cleaning policy.

PyPI's eight0.1.1 distribution files are unyanked in acquired metadata and
were uploaded24–25 October2023. setup.py also declares0.1.1 and
pybind11>=2.2. Equal version labels do not establish equality of repository,
distribution or installed bytes. The current GriTS requirement pylcs>=0.1.1
also permits future releases; it is not a reproducibility lock. Licence and
performance descriptions remain source declarations, without clearance or
measured speed claims.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Accept selected recurrence account | Checked symbol path and prefix induction |78 assertions/six altered controls pass; finite oracle agrees | Binding conversion, integer/resource limits | Inspect pybind11 string-conversion source | Installed runtime correctness |
| Preserve codepoint/normalization distinction | Exact string examples and encoding argument | No source-target contradiction found for declared codepoint target | Which normalization target downstream users require | Keep policy unselected and original strings traceable | Grapheme/semantic equality or a normalization default |
| Preserve source/version gap | PyPI and repository identities bound separately | No distribution bytes acquired | Release/head/installed equivalence | Retain gap until exact source-build binding is available | Historical benchmark reproduction |

No stochastic comparison or ranking occurred. This source account does not
repeat or negate the earlier SequenceMatcher mismatch; it explains why the
newer dependency path can target exact token LCS, conditionally on binding
and source identity. No manuscript defect or continuation veto was established.
Candidate3.44 remains396 pages/not_ready with53 obligations,six interactions,
46 operations and zero whole-row closures.

The staged acquisition wrapper preserved each actual invocation and receipt.
Local construction/check/record/replay used standard-library Python with -B,
CUDA_VISIBLE_DEVICES=-1 and no upstream imports. source-ledger.json binds
sources; run-manifest.json and completion.json bind execution and completion.
Safe future replay: verify.py without flags; completed stages are one-time.
