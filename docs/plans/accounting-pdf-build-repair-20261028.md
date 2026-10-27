# Repair the canonical PDF build entry points

28 October 2026. User reports a failed PDF compilation. Addresses MC24, MC31,
MC32 and MC33 only as build/reproducibility work; release acceptance stays open.

1. Inspect the selected TeX roots, current logs and editor/build configuration.
2. Reproduce the failure in a new output directory. Check engine selection and
   resolution of relative inputs through the stable symlinks before editing text.
3. Repair the build entry point and document one supported command. Preserve
   all protected source/package/PDF identities and unrelated workspace settings.
4. Rebuild both selected volumes using the repaired route. Check complete build
   logs, bibliography/references, page totals and normalized page text against
   the selected PDFs. Exercise the editor entry point where applicable.
5. Record the exact cause, commands and limitations; refresh only relevant
   navigation/checkpoint notes. No release promotion or long campaign follows.

Skeptical audit: the user's failed command/log is not yet available. Successful
historical builds do not refute the report. Wrong engine, symlink-relative paths
and unwritable caches are hypotheses, not diagnosed causes. Reproduce cheaply
before choosing a fix. Using the installed TeX environment is the observed
baseline, not a clean installation claim. Test the user-facing invocation,
not merely a manual build from the resolved source directory. Keep outputs
outside frozen packages and stop if source identities change. This is a build
repair, not a scientific experiment or manuscript-content revision.
