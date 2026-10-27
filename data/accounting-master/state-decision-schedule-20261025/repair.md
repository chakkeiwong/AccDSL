# Comparison fixture repair

All18 focused scheduler tests passed. The first49-comparison pass failed one
new independent assertion: total inventory was incorrectly expected to equal
the selected recovered lot's remaining carrying amount5. The actual retained
book opens with total inventory80, including the selected lot20. Selling15 of
that lot leaves total inventory65 and selected-lot carrying5. Other inventory60
remains. Exact native-state and statement comparisons passed throughout.

The preserved initial comparison is in attempt-01/compare.py. Corrected only the
total-control expectation to65; compiler, scheduler, decision and accounting
engines are unchanged. This is a wrong-baseline fixture failure, not evidence
against state-dependent scheduling. Full comparisons must pass before recording.
