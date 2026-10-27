# Two pybind11 snapshots: string inputs and GriTS consequences

20 October 2026. P15/P17/P19; MC01–05, MC23, MC26, MC28–35.

The selected argument casters encode scalar-valid Python strings as UTF8 and
construct std::string with an explicit byte length. Embedded NUL is retained.
Raw bytes bypass UTF8 validation in both snapshots. Bytearray is rejected by
the inspected v2.2.0 load path and accepted without decoding by v2.11.1.

The release sources are pinned independently:

| Tag | Commit | Source commit date |
|---|---|---|
| v2.2.0 | 2a5a5ec0a47c245fbf1bb1a8a90b4c3278e01693 | 31 August 2017 |
| v2.11.1 | 8a099e44b3d5f85b20f05828d919d2332a8de841 | 17 July 2023 |

These are a lower-bound source and a chronologically eligible comparator for
the October 2023 pylcs upload. Neither is identified as the version used to
build a distributed pylcs binary. Two snapshots do not establish behavior
throughout pybind11>=2.2. Fourteen bounded acquisitions, eight verified Git
blobs and 26 exact passage anchors preserve the reading. Only the listed
source spans and four Python C API sections were read, not all acquired files.

The older caster uses PyUnicode_AsEncodedString with UTF8 and the default
error policy. The newer eight-bit caster uses PyUnicode_AsUTF8AndSize. Both
check failure, clear the Python error and return false from load(). Their
same-version documentation says all Python str can be encoded in UTF8. That
universal assertion is wrong for strict encoding of strings containing
surrogate codepoints. A high surrogate, low surrogate and explicit surrogate
pair each fail the local standard-library strict encoder. A non-BMP scalar
such as U+1F680 is a different valid input and succeeds. This is source/API
analysis with a local codec illustration, not a compiled-binding test.
The function dispatcher was not inspected, so the ultimate Python exception
class is not established. In particular, clearing the codec error prevents
simply describing every failure as a propagated UnicodeEncodeError.

The separate py::str conversion operators were inspected to avoid confusing
their throw behavior with std::string argument load(). Likewise, C++ string
return decoding is not this pylcs function's result path: it returns an integer.
The common.h macros resolve to Python bytes APIs, which provide a buffer and
its full byte count. The explicit count, rather than a strlen call, explains
the embedded-NUL preservation for both Unicode and bytes.

The current GriTS wrapper at 8a281a3e2fd4cfa600d1c1f70f33b5eccc6294f1
annotates inputs as str but performs no runtime type validation in this
function. It checks equality before calling pylcs, then divides twice the
token LCS by the two Python lengths. This supports consistent codepoint units
for scalar-valid built-in str inputs through the selected source paths,
subject to the predecessor's allocation/integer limits. It does not support
silently treating bytes as the same domain.

| Fixed conditional illustration | Source-model result | Relevant comparison |
|---|---|---|
| Unicode or byte A-NUL-D / B-NUL-D | 2/3 | NUL retained; codepoint and byte units agree here |
| UTF8 bytes for é / aé | 2/5 | Decoded codepoint score is 2/3; Python bytes lengths are 2 and 3 |
| str é / UTF8 bytes for é | 2/3 | Decoded strings are identical, score 1; Python cross-type equality fails |
| Invalid bytes FF-41 / FF-42 | 1/2 token score | Strict Unicode decoding fails; no codepoint score exists |
| Unequal bytearrays for é / aé | Rejected in 2.2.0; 2/5 in 2.11.1 | Source-version difference |
| Equal surrogate strings | 1 from wrapper shortcut | Binding conversion is bypassed |
| Surrogate string / A | Conversion rejection | Final dispatcher exception class not checked |
| Empty str / empty bytes | Zero denominator after zero LCS | Cross-type empty equality is false |

Eleven pairs and fifteen individual inputs are retained. The LCS illustration
uses exhaustive subsequence intersection, independently of the acquired DP.
The byte-boundary model states conditional source implications; it does not
execute the acquired splitter. Bytes, mixed types and bytearrays are outside
the wrapper's annotated str contract, so these examples do not prove a defect
for valid str callers or a defect in historical experiments. Equal bytes and
equal bytearrays also take the wrapper shortcut; no conversion claim follows
from a score of one. No normalization or grapheme policy is chosen.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Accept the version-bounded input account | Exact caster/helper/API anchors | 205 assertions and ten altered-claim rejections pass | Actual binary build identity | Preserve explicit version and input-domain conditions | Installed or range-wide correctness |
| Reject universal str-encoding statement | Surrogate counterexamples plus selected conversion/error paths | Documentary overstatement confirmed | Final binding dispatcher exception | Record correction in source evidence | All Unicode inputs fail, or pylcs is unusable |
| Keep raw bytes outside codepoint normalization assumptions | Exact lengths and independent finite LCS implications | Type/unit mismatch exposed | Actual caller types and historical runs | Inspect current metric input/geometry validation and draft bounded adapter preconditions | Financial validity or historical score impact |

No stochastic comparison or model ranking occurred. Engineering integrity,
source semantics and downstream validity remain separate. No manuscript
statement was identified as wrong by this inquiry, so candidate 3.44 remains
396 pages/not_ready with 53 obligations, six interactions, 46 operations and
zero whole-row closures. Domain, independent and human acceptance remain open.

The restart did not change protected state. All stages used the tfgpu Python
interpreter with standard library only, -B and CUDA_VISIBLE_DEVICES=-1. No
upstream module, binding, build or native code executed. Actual acquisition
arguments and receipts are retained per request. Local calls were verify.py
--prepare before the restart, build_records.py, verify.py --check, then
verify.py --record and no-argument replay. Each uses
/home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B, with the unit-relative path;
the inherited run-manifest command templates omit the harmless -B flag, while
this paragraph preserves the actual flag. Completed stages must not be rerun.

Next: inspect the retained current metric/geometry/conversion sources for
nonfinite coordinates, cell text types and caller-level validation. This is a
documentary follow-up with no installed execution or data/model acquisition.

