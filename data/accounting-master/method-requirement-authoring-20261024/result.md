# Matched requirement text and exchange

24 October 2026. The separate method_requirement_text_v1 frontend now renders,
parses and exchanges MethodRequirements/1 declarations through the protected
core evaluator. It uses a finite prefix-expression grammar with typed constants,
explicit contexts, separate unknown bindings and strict content selection.

The increment passes 139 checks with 19 unit-test methods (11 protected core,
eight frontend), five independently specified examples and 101 protected inputs.
Exact typed/text identity, canonical rendering, exchange decoding and evaluator
results agree. Examples include retained company operations/returns and three
constructed legal-book, reported-measurement and insurance-cohort contexts.
The constructed examples demonstrate language semantics, not accounting methods.

Adversarial checks reject duplicate nested JSON keys, duplicate declarations,
unknown operators, code-like commands, missing terminators, trailing content,
stale hashes, type coercions, noncanonical rationals, context mismatches and
oversized/deep inputs. Unicode and quoted delimiters retain exact identity.
The literal text unknown remains different from an unknown value binding.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain optional authoring reference | Exact records and semantic results agree with the independent typed baseline | No lost dependencies, duplicate acceptance, authority escalation or protected-input changes found | Human authoring usability, full grammar coverage and general method applicability | Integrate the coherent requirement design into a protected Version 3.59 candidate | DSL superiority, full compiler, source/accounting admission or production readiness |

Content hashes identify declarations; they do not authenticate senders or install
capabilities. Registry ownership and available capability assertions belong to
the trusted caller. All successful assessments remain selected_requirements_only
with method_eligible=false. The legacy unknown-first discrepancy documented by
the core increment remains preserved rather than hidden by text conversion.

This is deterministic engineering evidence, not stochastic or accounting
validation. The strongest alternative explanation is shared implementation
behavior: handwritten text, independently specified outcomes and the protected
core truth/context tests reduce that risk within the declared fragment only.
No global continuation veto fired. S1–S5 remain partial; S6 held and S7 deferred.
Version 3.58 remains 426 pages and not_ready until its successor is checked.

Reproduce with python3 -B data/accounting-master/method-requirement-authoring-20261024/verify.py --replay.
Exact inputs, code, outputs, commit, environment and commands are in manifest.json.
Next: docs/plans/accounting-method-requirement-integration-20261024.md.
