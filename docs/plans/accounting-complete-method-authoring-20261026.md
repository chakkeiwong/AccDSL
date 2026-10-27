# Author complete declared company methods with existing semantics

26 October 2026. S2/S3/S4; MC20/23/24/25/33/34, G2/G12/G18 and I04.

Question: can text author the complete CompanyBookMethod/1 definition, including
guarded pre/postconditions, monetary and memory effects, while using the same
semantic owners as typed definitions? Baselines are the four inventoried payment
and claim-creating sale definitions under CompanyBookTransition/1 and /2.

Skeptical audit passes after adding explicit transition-version selection. v2
requires a separately supplied typed memory definition and supports insertion;
v1 fixed replacement remains distinct. The frontend has no execution callbacks,
dynamic imports, new accounting algorithms or source-admission shortcuts.

Write the exact line-oriented grammar first. Reuse MethodRequirementExchange/2
blocks with empty values/capabilities as authored manifests, preserving their
digest selection. Give monetary calculations/postings/flows explicit declarations
and prefix expressions; reuse existing expression validation and evaluation.
Give memory writes explicit ordered declarations with native data templates.
Schemas, book, event and optional v2 memory_definition are named compilation
inputs, not secretly authored or inferred by this method text.

Primary criteria: exact complete definition and digest equality across text and
typed paths; original prepare checks pass; full after-state/journals/gross flows
match the retained engine; duplicate/missing syntax, wrong context/type/schema,
forward references, false/unknown premises, invalid memory effects and proposal
tampering retain meaningful refusal. Source spans identify actual declarations.

1. Define grammar and compilation environment with explicit scope limits.
2. Implement a small bounded frontend reusing existing semantics.
3. Verify matched v1/v2 methods and adversarial cases, preserving all inputs.
4. Integrate the complete-method and exact-native timing group into a protected
   manuscript successor; refresh the program without whole-row closure.

Artifacts: data/accounting-master/complete-method-authoring-20261026/.
CPU only; no installs, agents, commits, fees, outreach, publication or E3.
