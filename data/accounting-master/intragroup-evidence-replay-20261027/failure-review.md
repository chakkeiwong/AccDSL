# Attempt-01: incorrect account-based NCI diagnostic repaired

The full replay stopped at downstream-carry/0/1/credit/1/2/known. All complete
native-result and independent expected-field comparisons for that exchange had
passed. The new auxiliary check incorrectly allocated one quarter of all income
in S/group accounts to NCI. That quantity is wrong relative to the specified
downstream profit-attribution target.

For half resale, reported S/group income before attribution correction is
−33/4. It includes a credit of 5 to S.cost_of_sales releasing the parent's
downstream margin. The explicit inventory-margin-release journal assigns that
profit to parent owners. Removing it gives subsidiary-attributed income
−33/4 − 5 = −53/4, and ordinary NCI receives (−53/4)/4 = −53/16, exactly the
reported result. The separate P tax-reversal expense does not enter the S/group
subtotal. Current manuscript simulation/carry.tex explains this distinction;
upstream-carry.tex separately locates upstream release in subsidiary earnings.

Repair the checker by removing parent-attributed income adjustments occurring
in S/group accounts before applying the 25% NCI fraction. The existing group
journal expectations independently fix those attribution labels. This changes
an incorrectly computed diagnostic, not the financial target, native result,
golden output or assumptions. Complete output equality remains exact and no
normalization is introduced. Balanced changes to reported owners/NCI profit
must still fail the repaired checker.

The failed attempt, access audit, original exact driver and completed unit outputs
are preserved in attempt-01/. The original driver did not save the partially
completed unit's raw exchanges before the exception; its checks record complete
equality with the retained original for that exchange. The repaired driver also
saves partial unit results on failure. No source identity or native behavior
failed and no global continuation veto fired. Prepare a fresh copied tree and
retry the complete population under the unchanged evidence contract.
