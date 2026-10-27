# R06 — retained xBRL-XML compatibility and bounded OIM mapping

20 October 2026, Asia/Shanghai. P15/P16/P17/P19; MC01–07, MC23–26,
MC28–35. Predecessor: r06-calculations11-source-20261020.
Output: data/accounting-master/r06-oim-mapping-20261020/.

Question: which of the twelve xBRL-XML compatibility constraints are supported
by this exact retained instance and declarations, and does its proposed OIM
dimension mapping preserve or change the frozen XML duplicate partition?
Comparator: the unmodified 1,127 occurrences and XBRL 2.1 identity classes in
r06-duplicate-facts-20261020, not a deduplicated or inferred-default report.

Evidence contract: inspect the complete retained instance structure, all used
concept/type paths and the already retained 2021-10-13 xBRL-XML/OIM texts.
Recompute dimension mappings independently from source namespaces, contexts,
units and in-scope language; compare checked periods, typed dates and numeric
classification with the frozen prior records. Assess twelve constraints,
including entire-source tuples, fraction ancestry, footnote roles/effectivity,
linkbaseRef, roleRef/arcroleRef reachability and non-root xml:base. Where no
footnote or role reference exists, record finite absence rather than inventing
a generic link processor or schemaRef-only DTS certificate.

Primary pass criterion: exact source bindings, all occurrence IDs accounted
for, deterministic OIM dimension signatures and an explicit comparison of both
partitions. Fixtures distinguish language-sensitive text from non-text, pure
unit absence, date boundaries, typed versus explicit values, reported versus
default dimensions, context/container identity, and duplicate values from
duplicate identity. Source inconsistency, missing used declaration/type path,
or unsupported source feature blocks the affected mapping claim. Protection
failure or uncontrolled execution is a continuation veto. Differences between
partitions are findings, not failures unless the implementation disagrees with
its stated mapping. Counts are explanatory, never completeness certification.

Research intent: test whether old XML grouping is a sufficient prerequisite
for optional Calculations 1.1. Expected failure: omitted language, pure units,
period boundaries or typed values silently change grouping. Repair trigger:
an actual unsupported feature or mapping mismatch requires local repair or a
narrower conditional result. No full schema/DTS/XHTML validity, installed
correspondence, accounting admission, issuer rounding choice, or actual
Calculations 1.1 consistency is concluded. The missing normative schema and
the Calculations 1.1 §5.4 cross-reference ambiguity remain separate.

| Choice | Provenance / reason | Failure / early diagnostic | Status |
| --- | --- | --- | --- |
| Linked 2021 specifications | Frozen predecessor dependencies | Silent version migration; bind raw and visible sources | Baseline |
| Retained instance only | Existing exact 1,127-fact source | Generality claimed from one filing; explicit finite scope | Baseline |
| Namespace-expanded names | OIM dimensions/equality | Prefix aliases treated as distinct; QName fixtures | Required mapping |
| Text class from type ancestry | OIM text definition and exclusions | All nonnumeric facts receive language; excluded-type fixtures | Checked rule |
| Reported dimensions only | xBRL-XML §3.2 | Taxonomy defaults inserted; omission fixture | Checked rule |
| No missing timezone inference | Frozen period evidence | Local timezone changes period identity; boundary comparison | Checked rule |
| Distinct dimension and value tasks | OIM §5–6 | Correct grouping mistaken for full value/schema validation | Scope limit |

Skeptical audit: the frozen predecessor replay passes (3,234 protected files,
56 completion bindings). The exact instance contains one schemaRef, 193
contexts, seven units, 1,127 direct facts, root xml:lang=en-US and no footnotes.
This removes actual footnote-link construction and non-discoverable roleRef
cases from this finite inquiry, not from general implementation obligations.
The plan passes after separating dimension mapping from generic conformance
and excluding full value/XHTML normalization from its claim. Premortem: a
partition can agree accidentally despite an incorrect language classification;
therefore inspect type paths and use a language-changing discriminator.

CPU-only standard library: CUDA_VISIBLE_DEVICES=-1
/home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B. One-time preparation,
construction, --check and --record; then no-flag read-only replay. Preserve
all predecessor evidence, manuscript 3.44/396/not_ready, 53/6/46, HEAD/index,
empty staging and 36 existing dirty paths. Advance only four live controls and
an additive R08 supplement. No installation, upstream execution, empirical
run, runtime/controller, commit, outreach, publication or fees.
