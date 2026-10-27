# Selected call and Unicode audit before calculation

Six acquisitions complete. PyPI metadata links kuangkzh/pylcs and describes
a transferred repository. Pin5eee78a655fbe34ef24c8240304646f7cd07543b, then
verify the three selected blobs. Native reading is limited to lines1–61
(includes,utf8_split,lcs_sequence_length) and328–365(the binding block).
The Python initializer and setup.py were read completely. Other native
functions were not audited merely because their bytes were downloaded.

The selected native function uses the standard longest-common-subsequence
recurrence: an empty prefix scores0; equal final tokens extend the preceding
diagonal optimum by1; unequal final tokens take the maximum after dropping
one final token. Induction on prefix lengths proves exact LCS for its token
sequences, provided dimensions fit the declared integer types and allocation
succeeds. The module exports that exact function under lcs_sequence_length;
the Python initializer imports it from _pylcs. setup.py names src/main.cpp,
version0.1.1 and pybind11>=2.2. These declarations do not bind the current
repository bytes to the published wheel/source distribution or an installed
module. Pybind11's str/std::string conversion remains uninspected.

utf8_split groups a byte with following continuation bytes by testing the
next byte's high bits. On valid UTF-8 for Unicode scalar values, every noninitial
byte of a codepoint is a continuation byte and every first byte is not; the
groups therefore equal codepoint encodings. Codepoints agree with Python str
length for strings without unpaired surrogates. This is conditional on valid
UTF-8 reaching C++; it is not an audit of the binding conversion. No Unicode
normalization, grapheme segmentation or invalid-byte validation is present in
the selected splitter/recurrence. Malformed bytes could be grouped, but whether
the public binding accepts them is a distinct uninspected question.

Pre-calculation finite contract: locally reconstruct byte-boundary splitting
and prefix LCS with standard library only. Check six pairs: Chinese收入/税收入,
precomposedé/decomposede+combining acute, emoji woman-ZWJ-laptop/woman,
embedded-NUL A-NUL-B/A-NUL-C, empty/Chinese, and identical empty strings.
Compute the wrapper's identity shortcut and otherwise2L/(lenA+lenB). An
independent enumeration of all subsequences verifies each small LCS result.
Normalization with unicodedata.NFC is an explanatory comparison only, not a
proposed policy. Both canonically equivalent strings and multi-codepoint emoji
make the unit of comparison visible without claiming a bug in codepoint LCS.

Additionally check14 selected Unicode scalar boundary/special values, including
1–4-byte UTF-8, NUL, combining acute and ZWJ, singly and concatenated; preserve
their actual list. This is a finite diagnostic supplement to the valid-encoding
argument, not exhaustive Unicode/runtime conformance. Two malformed byte
strings are compared with strict UTF-8 decoding solely to show that the local
boundary splitter is not a validator. No actual pylcs/pybind11 build or call.

Skeptical audit passes: Python/cell string units, package/repository identity,
empty conventions and limits are explicit. A codepoint reward differing from
grapheme or normalized equality is a target choice, not automatically a metric
defect. None is adopted as a default. Memory is O(mn) integer DP storage for
the selected source, plus token storage; no resource limit or runtime cost has
been measured. Binding or release-source uncertainty blocks those dependent
claims while permitting this bounded source account. No continuation veto.
