# Finite implementation audit

Before construction, the metadata interpreter bounds finite exponent evaluation
to |decimals|<=1000 to avoid unbounded integer allocation in authored fixtures;
all observed values lie between -9 and4. Larger exponents return outside_scope,
without a validity verdict. This is a resource convenience, not a numerical
standard. Integer forms use explicit ASCII grammar and XML whitespace collapse.
Whitespace-bearing INF forms are left outside the local union profile; the
actual sixteen INF attributes have exact spelling. The retained nonNegativeInteger
rule permits negative-zero spelling, which the precision fixture preserves.
No precision-to-decimals inference is implemented because no actual precision
attribute occurs. These restrictions do not alter the source evidence contract.
