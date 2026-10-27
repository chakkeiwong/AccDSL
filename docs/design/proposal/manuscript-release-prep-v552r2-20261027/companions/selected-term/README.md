# Selected term program component

This internal bundle contains the exact SelectedTermProgram/1 and its retained
semantic dependencies, two complete selected program inputs, independently
supplied selections and full-result hash commitments. Original full results
remain retained by path and digest in the source worktree; those large records
are not imported during execution. Each relocated result is fully recomputed
before its canonical and insertion-order hashes are compared.

Run from this directory in the recorded Python environment:

    env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 -I -B scripts/verify_relocated.py output-01

Use a fresh output directory. Other copied verifier files are historical
reference dependencies; do not invoke their writer entrypoints. The script
disables native lifecycle/financial builder callbacks and audits project file
access before importing program code. Only the bundle and recorded Python
runtime may be read; writes are limited to the fresh output directory.

This is not the full modern AccDSL package, production software, independent
accounting acceptance or publication. No papers/standards are included, and
redistribution rights for project material remain unreviewed. The selected
profile's complete refusal, population and report limits remain in contract.md
under data/accounting-master/selected-term-program-20261027/.
