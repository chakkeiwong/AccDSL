# Operation-limit test repair

The first verification attempt completed all retained request/transition
comparisons and earlier controls, then failed its own final expectation.
Repeating six large nested operations 43 times exceeded the generic 4,096-node
input bound before the 256-operation check. The candidate correctly refused
the oversized declaration; the test did not isolate the stated boundary.

The corrected control keeps 64 small scalar operations (3,479 declaration nodes)
and supplies four typed rows. Expansion would produce 257 writes including the
suffix, so the operation cap is reached without violating the input-node bound.
Only the verifier changes. Preserve attempt-01 and run attempt-02. This is a
harness repair, not a semantic candidate change or research-direction rejection.
