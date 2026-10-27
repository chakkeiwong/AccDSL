# Local preparation repair

prepare.py copied all protected Version 3.57 sources and updated the version
and language overview, then stopped at an exact paragraph match whose assumed
line wrapping differed from the source. It did not change the predecessor.
The failed script is retained. A targeted patch applied the intended local
transition and section include to the copied company-source-state.tex.
Do not rerun prepare.py: the successor directory and baseline are established.
The final preservation verifier must check all three intended source changes.
