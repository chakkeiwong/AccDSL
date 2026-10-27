# Proposed native-XBRL field translation

This directory contains an authored synthetic XML fixture and documentary
portable records. Neither the input packet nor the expected records is Arelle
output. `prepare.py` constructs the fixture expectations from explicit type
hypotheses and the small local XML file; `verify.py` checks their consistency.
Neither is an adapter for arbitrary native instances.

Specification: `docs/design/proposal/architecture/native-xbrl-translation-proposed-v1.md`.
Plan: `docs/plans/accounting-native-xbrl-translation-20261018.md`.
Read the result and remaining obligations before interpreting any check count.
Only `python3 data/accounting-master/native-xbrl-translation-20261018/verify.py`
is a read-only replay command. Preparation and completion record creation are
one-shot operations and must not be repeated over bound evidence.
