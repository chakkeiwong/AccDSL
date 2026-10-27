# Required P18/P19 evidence additions

This supplements the frozen `accounting-proposal-artifact-format.md` without
rewriting P15's accepted source. The fields below apply to the outstanding
P18/P19 artifacts. P15–P17 formats and accepted evidence are unchanged.

P18 `manuscript.json` adds `render_record` and `render_review_record`, each an
ordinary pinned `{path, sha256}` reference. Save the actual render command,
environment, integer `exit_code: 0`, `pdf_path`, `pdf_sha256_before`,
`pdf_sha256_after`, and `page_hashes` (repository page paths to full SHA256) in
the render record. Capture the PDF hash before and after the command and the
actual generated pages afterward. Both PDF hashes must match the candidate PDF;
the page map must exactly match `rendered_pages`. Rebuilds require rendering
again, with a new record. Do not update old evidence to imply a run occurred.

The render review record names `render_record_path` and
`render_record_sha256`, the exact `page_hashes` inspected, `review_hashes`
(paths/hashes of the notes in `render_review`), and nonempty `reviewer`,
`reviewed_at` and `scope`. Preserve actual observations and limits in those
review notes. A new render record requires renewed review; a PDF scalar alone
cannot bind old images to a rebuilt document. These checks bind evidence; they
do not replace visual inspection or establish human acceptance.

P19 `readiness.json` adds `decision_dispositions`. Each P15/P16/P17 decision
whose historical row has `blocks_proposal: true` needs exactly one row containing
`stage`, `decision_id`, `status` (`resolved` or `superseded`), substantive
`answer`, `rationale`, and nonempty pinned `evidence`. A superseded decision also
names `superseding_decision_id` present in P19's nonblocking `open_decisions`.
Stage plus decision ID is the key; repeated IDs in different stages must each
have a disposition. Preserve the historical blocker instead of editing accepted
evidence to make it disappear. Independent review judges whether the answer and
support actually resolve it. An empty final open-decision list is insufficient.

Current tests are `tests/test_accounting_proposal_current.py`: all 17 original
test cases retained, valid synthetic fixtures extended with the new render
records, plus targeted stale-render and dropped-blocker regressions. The
accepted predecessor remains at `tests/test_accounting_proposal.py` as evidence
of the prior checker contract, with its exact original hash unchanged.
# Full rendered page coverage

P18 uses the existing PyMuPDF (`fitz`) dependency to count pages from the actual
pinned PDF. Every `rendered_pages` entry must have a one-based `page_number`,
ordered from 1 through that count without omissions. The render record must
include `pdf_page_count` and the same ordered `page_numbers`; the review record
must bind those numbers as well as the page hashes. Partial page inspection
cannot satisfy whole-manuscript inspection. PDF parser failure leaves the stage
incomplete. Mechanical coverage does not certify human reading or prose quality.
