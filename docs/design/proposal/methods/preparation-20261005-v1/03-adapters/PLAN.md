# Filing adapter source audit and evaluation preparation

Date: 5 October 2026. This is packet 3 of the authorized independent preparation.
Outputs stay in this directory; the original AccDSL worktree is read-only.
Addresses MC01-MC07, MC25, MC27, MC31, MC33 and G5/G9/G11-G13.

Question: which inspected Arelle and Docling capabilities can preserve the
proposed extraction/evidence/time semantics, what must the AccDSL adapter add,
and what matched-task evidence would justify choosing an implementation?

Baseline: current extraction-contract-v1.md, evidence-contract-v3.md and
time-contract-v2.md plus the frozen 192-report corpus. Existing software files
are content-pinned branch snapshots, explicitly not release/commit pins. Copy
and retain these, then acquire a bounded set of official source files at recorded
commits. Do not assume that an old filename names a release or that upstream
HEAD is suitable for deployment.

Evidence contract: primary pass requires source claims reconstructible from
retained exact bytes and line anchors; proposed examples must be internally
consistent and keep original occurrences, financial context and unknowns.
Source-integrity/locator errors veto their dependent conclusions. Incomplete
implementation inspection limits the affected statement. Runtime behavior,
accuracy, latency, confidence calibration, production acceptance and accounting
validity are not established by this audit. Output is capability-matrix.md,
evaluation-protocol.md, adapter-cases-v1.json, source-register.json and checks.

Sequence: pin reference and existing software material; inspect relevant actual
interfaces, value/context/location handling and error/side-effect paths; acquire
missing upstream components only where needed; write capability/limit decisions
and source-to-output losses; prepare paired-case specifications and evaluation
protocol; check source hashes, anchor ranges, exact examples and cross-packet
field compatibility; give reviewed candidate files to the supervisor.

Skeptical audit: XBRL and PDF tools solve overlapping but distinct tasks, so
comparison must be stratified by input and task. Arelle context hashes do not
establish assertion equivalence; Docling text/provenance does not establish
financial context or source truth. Successful conversion is not disclosure
closure. Backend/model/download configuration can change behavior even with a
top-level commit pin. License metadata is a diagnostic; inspect license text,
while separate model/dependency terms remain a deployment check. Do not infer
historical availability from conversion timestamps. No undocumented defaults,
unmeasured thresholds or model choice can be promoted. These issues are handled
by preserving sidecar evidence, explicit configuration and separate review.
Audit decision: proceed with bounded source inspection and specification work.

Assumption audit: retained snapshots are a baseline (provenance tools.json), not
version locks; official pinned source is implementation evidence, not runtime
proof; synthetic fixtures isolate failure mechanisms, not corpus accuracy; the
existing corpus is exposed development material until split/exposure auditing;
PDF page numbering and coordinate conventions must be explicit; source gaps
block specific claims instead of causing invented behavior or endless search.

Stop after useful bounded deliverables. No package installation, runtime/model
downloads, training, product edits, new large corpus or professional outreach.
No statistical ranking is sought. Unavailable source is reported as a gap.
