# Conditional refinancing reference

This standard-library Python companion checks the dated cash calculations in
section 14.13, *Discrete sale choices and continuous financing*. Use Python 3.11
or later from this directory:

```
python3 -I -B verify_refinancing.py --output-dir /tmp/accdsl-refinancing-new-run
```

The output directory must not already exist. The script writes full dated traces,
checks and a command/environment manifest there. It reads no worktree data,
uses no network or optional packages, and performs exact Fraction arithmetic
on CPU. The example's expected distinguishing outcomes are in
expected-counterexamples.json. No prior accepted writer is rerun.

There are three sale offers, continuous bridge/term quantities, two receipt
histories and specified price/covenant variants. Selected rational boundary
and interior amounts check the separate event sums against the written cash
inequalities. The manuscript proves the continuous domain under its explicit
order; no finite sampling or test count establishes that result.

The two diagnostic examples show why minimum funding is not necessarily the
maximum-minimum-cash policy, and why a day-5 receipt and a fee-bearing issue
cannot always be netted without preserving their order. The second uses a
small negative-net-proceeds issue to expose a prefix failure; it is not a
recommended financing action. Notice periods and information restrictions
still govern when management may choose the amount.

This is a deterministic documentary reference. It does not implement the whole
AccDSL event engine, prove general optimization completeness, supply real offer
terms, price an equilibrium, validate accounting treatment, or close independent
acceptance. Later term debt remains an obligation outside the day-6 cash horizon.
