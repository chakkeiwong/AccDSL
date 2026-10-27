# PDF compilation repaired — 28 October 2026

The selected 5.55-R1 documents compile successfully through the new repository
command, python3 scripts/build_pdf.py. The main output has 837 pages and the
simulation output has 265. Every normalized page text matches its canonical
counterpart. Both final logs have no undefined references/citations, multiply
defined references or fatal errors. Sampled covers and mathematical pages were
rendered and visually inspected with no observed layout change or clipping.

## Reproduced causes

The user's exact failing invocation was not supplied. Two reproducible failures
existed in ordinary invocations of the canonical TeX link:

- latexmk -pdf docs/AccDSL-latest.tex selects pdfLaTeX and stops because fontspec
  requires LuaTeX or XeTeX.
- Changing only the engine to LuaLaTeX still fails when run from the repository
  root: reading-guide.tex is not found, because the symlink does not change
  LaTeX's working directory to the resolved source package.

diagnosis.json and the two diagnosis logs retain the commands, fresh output
directories and failures. Existing canonical PDFs and package logs were intact;
their successful historical builds did not address these entry-point failures.

## Repair

scripts/build_pdf.py resolves the selected source link, runs latexmk with
LuaLaTeX from that source directory, uses an explicit writable font cache and
writes PDFs, auxiliary files, SyncTeX and build logs to .build/pdf. Its default
builds both volumes; main and simulation select one. --tex also accepts the
extensionless form used by LaTeX Workshop. It preserves the requested alias's
job name so the editor can locate its expected PDF.

The workspace recipe and output directory now use this command. The existing
git.ignoreLimitWarning setting remains. README.md and docs/README.md document
the supported invocation, output paths and requirements; .gitignore excludes
the local build/cache directory. No source chapter, protected package manifest,
canonical PDF/link or frozen release acceptance record was changed.

## Validation

The full public command succeeded: main 82.15 seconds, simulation 26.09 seconds
in the installed TeX environment. Per-volume full logs and command manifests
are copied here as AccDSL-*-full.build.log/json. verification.json records all
page comparisons, unchanged identities of 452 declared package files, and
the exact editor-equivalent invocation from the docs directory. The latter
succeeds with an extensionless input; VS Code's GUI was not launched.

Missing-source and protected-output requests refuse with exit code 2. Python
syntax and workspace JSON parse checks pass. Four rendered pages and their
combined view are retained here. No dependency installation or new environment
compatibility claim is made. The invocation uses the installed latexmk/LuaLaTeX
and BibTeX observed in the logs; this is not a clean-install test.

This closes the reproduced compilation issues and supplies build evidence for
MC24/31/32/33. It does not close any broad mission requirement, manuscript review
or independent acceptance. Release status remains not_ready; the completed
eight-hour campaign is not resumed by this repair.
