# Diagnostic attempt and repair

22 October 2026. The first exact checker invocation was:

    env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/r03-eps-additivity-boundary-20261022/check.py --record

It exited 1 at the fixture expectation assertion for
`strict-order-discriminator`. No checks or calculation-manifest output had
been written. Its hand-authored expectation was gap 4, copied from the draft;
the direct conditional-world calculation found gap 8. The four-condition
equivalence assertion had passed for that model before this assertion.

Independent substitution resolves the error: the baseline is 72, and isolated
increments are 8, 28 and 8. The reconstructed full-set earnings are therefore
116, whereas complete full-set earnings are 108. Their difference is 8.
The proof identity independently gives (1/2)(4/5)(10+10+10-10)=8.
The original frozen eight-world data and the selection-ratio difference
1/770 are unchanged. The draft proof/example sentence and fixture expectation
are corrected before rerunning. This is an example transcription failure,
not a theorem failure or a continuation veto. The checker implementation did
not change.
