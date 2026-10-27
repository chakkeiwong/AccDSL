# Historical Core 0 specification component

This local bundle resolves the historical Core 0 contract/schema references in
AccDSL 5.51. It preserves the exact contract, schema, grammar, authored debt
fixture, 17-export registry and pure semantic validator. This component does
not contain all current portable/company/sector profiles or the full manuscript.

Run from this directory in the observed environment:

    env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 -I -B scripts/verify_relocated.py output-01

Use a fresh output directory for each invocation. No source writer is called.
The copied check_semantic_preparation.py and build_demo_registry.py main entry
points are retained reference material: do not run them to overwrite fixtures.
The new verifier calls only the pure validation and registry-construction APIs.
requirements-observed.txt records tested installed versions, not permission or
instructions to install software. Python version is in bundle-manifest.json.

Paths in reference-map.json are relative to this bundle. The normative files
retain their original wording and historical scope. No coercion to a later
profile or independent implementation acceptance is supplied. Source research
tools.json is a historical index, not evidence of current tool availability.

This is an internal reproducibility package. No retained papers or accounting
standards are copied. Redistribution rights for project material have not been
reviewed, so no public-distribution permission is asserted. Installed dependency
licence metadata is recorded separately; actual deployment notices require a
distribution-specific review.
