# Isolated document reproduction for 5.54

The governing integration plan is docs/plans/accounting-selected-history-integration-20261027.md.
Copy only the 411 declared files plus their manifest to a fresh /tmp directory,
verify the package, then build both roots with a writable local font cache.
Both builds must succeed with resolved references, no new warnings and exactly
the same normalized text on every page as the reviewed candidate. Input logs
must contain no original-worktree dependencies. External TeX/font inputs remain
an explicit environment dependency; this is neither a clean installation nor
complete executable-evidence reproduction. Preserve original PDFs, sources and
all successful writers. Results go only to relocation-01/.
