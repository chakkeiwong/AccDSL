# Selected-contract implementation audit

The generated runner initially used an overly broad text replacement that also
changed the invariant-hash dictionary lookup into a tuple lookup. The first
diagnostic refused before execution. Correct that single lookup and restrict
the generator replacement to the closed-field declaration. No native method,
accounting rule, source lock or preceding implementation changed.

Final evidence includes full original intent-request equality, exact previous
state/report results, native wrong-customer/missing-claim/unknown/false-approval/
interval/due/sealed-window/duplicate-claim refusals, and both projected-value and
half-payment specialization mismatches. The latter is refused only under the
explicitly selected native full-payment contract. General authoring retains its
independent semantics. No global policy is silently changed.
