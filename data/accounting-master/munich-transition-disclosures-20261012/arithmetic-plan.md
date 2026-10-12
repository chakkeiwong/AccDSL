# Pre-arithmetic refinement

Pre-arithmetic refinement after source reading: PDF 186 (printed 184) displays
an equity bridge in EUR billions to one decimal; PDF 3/157 warns of rounding.
Use exact decimal arithmetic for the displayed component sum and endpoint
difference. Check compatibility under an explicitly hypothetical nearest-0.1bn
rounding envelope, using an interior witness rather than assuming a tie rule.
The witness is not an inferred issuer balance. Compare the opening totals in
the separate issued-CSM and held-net-cost/gain transition tables (PDF 257 and
213) with the rounded bridge component, preserving their opposite signs and
EUR-million units. Do not infer each table's undisclosed group allocation or
call a rounded discrepancy a genuine source conflict. The extraction contains
control characters in decimal/grouping positions; bind raw tokens and use the
visually inspected numeric reading without altering the original extraction.

This refinement was recorded before check_sources.py ran. It is preserved here
as an addendum so the preceding integration's bound next-plan bytes stay frozen.
