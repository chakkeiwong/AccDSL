# Exact policy parent repair

28 October 2026. Policy-attempt-01 used the earlier operation example, but the
saved policy belongs to the second-year price revision retained in the exchange
packet. Native validation correctly returned parent_path_identity; the new
checker then raised KeyError by assuming materialization. This is a comparator
selection and checker error, not a failure of the existing policy method.

The failed checker, original plan and failure details are retained in
policy-attempt-01. Repair resolves the exact parent and saved result through
the exchange packet, verifies blob digests/lengths, and checks a complete native
replay before interpretation. The historical policy is unchanged. Its invoice
is 16*12=192 per new claim, not the earlier example's 16*11=176. Independent
expectations and the plan now use the correct comparator. Unexpected refusal
is checked before path access. Proceed in policy-attempt-02.
