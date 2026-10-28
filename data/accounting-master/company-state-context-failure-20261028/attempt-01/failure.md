The first run found all seven context mutations correctly refused, but the
harness expected one generic CONTEXT_MISMATCH code. The native API returns
specific unit, currency, scale, sign/precision, dimension and perimeter codes.
These exact codes were checked against context_chronology_v1.py lines250–256.
Attempt02 fixes the expected codes, retaining strict refusal assertions and
all original requests/results. No native implementation or criterion changes.
