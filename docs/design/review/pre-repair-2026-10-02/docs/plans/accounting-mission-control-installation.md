# Installing the AccDSL mission and requirements

Date: 2 October 2026 (Asia/Hong_Kong).
User request: list the main goals and requirements, install them as mission
control, and assess whether the earlier gap list covers the current document.

## Skeptical audit before installation

The baseline is the user's three original substantive requests, preserved in
the saved session, plus the current instruction. The existing document and its
P0–P6 stages are proposed means of meeting those requests; they cannot reduce
the mission by themselves. Distinguish the immediate governing design from
the eventual working product. Record direct user requirements, policy duties
and derived engineering requirements separately. Do not invent deadlines,
statistical thresholds, mandatory technology choices or production operations.

The earlier G1–G10 findings are a useful initial audit, not an exhaustive
requirements inventory. A broader assessment must look for omitted workflows
and interactions as well as missing chapter content. Mentions, compilation,
paper counts and arithmetic examples cannot close implementation requirements.
Some additional findings will refine earlier categories rather than constitute
independent defects; record those relationships explicitly.

Installation is local: add a root mission document and a short AGENTS.md
entry point; maintain a requirement/acceptance register; record the expanded
audit; and update the existing plan, checkpoint and document navigation to
avoid competing completion claims. Current user directions and higher-priority
instructions continue to control. No global agent setting, session database,
manuscript, paper, provider configuration or executable engine needs changing.

The audit passes with these boundaries. Validate local links, requirement and
gap references, and the protected manuscript hashes after installation. Stop
once the mission is installed and the question about remaining gaps is answered;
this request does not itself launch the entire implementation campaign.

## Planned records

- `MISSION_CONTROL.md`: purpose, goals, non-negotiable requirements and working
  rules for preserving the mission.
- `AGENTS.md`: automatic local entry point for future work.
- `docs/plans/accounting-mission-requirements.md`: stable requirement IDs,
  provenance, acceptance evidence and current gaps.
- `docs/design/review/mission-gap-audit-2026-10-02.md`: additional findings and
  their relationship to G1–G10.
- Existing authoring plan, checkpoint and design README: links and corrected
  current status, while retaining historical work records.

## Result

Installed the root mission document and AGENTS.md entry point, the 34-row
requirement register and the expanded G11–G18 audit. The eight additional
findings have explicit links to the original G1–G10 categories; the records
make no claim of permanent exhaustiveness. Updated the authoring plan,
checkpoint and design README so the old final-review-only status cannot
silently govern future work. The missing author-review record is now marked
pending instead of linked as though it exists.

Preserved the previous README, authoring plan, checkpoint and verification
record under `docs/design/review/mission-control-installation-2026-10-02/`.
Structural verification found 8 goals, 34 unique ordered MC IDs, 18 unique gap
IDs and 52 resolvable local links. Every requirement row records provenance,
acceptance evidence, present assessment and gap references. All 15 protected
LaTeX/bibliography/PDF files retain their pre-installation hashes. No manuscript
or paper content was changed.

Ran `python3 scripts/verify_design_document.py` after updating navigation:
passed, 60 pages, 31 papers, no configured consistency errors. The existing
arithmetic evidence remains unchanged; no new engine or numerical experiment
was run. Machine-readable installation results are in
`docs/design/review/mission-control-installation-2026-10-02/installation-checks.json`.

The installation makes the mission durable. It does not close the recorded
design gaps, establish accounting validity or start a background implementation
campaign. The user-facing answer lists the goals and the additional findings.
