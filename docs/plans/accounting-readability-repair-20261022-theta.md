# Define the simulation parameters before their first use

22 October 2026. P18/P19; R08; MC11/12/18/32–35. Continued provisional
manuscript preparation for accounting modellers and software implementers.

## Question and exact baseline

Can the reader identify the parameters shared by the behavioural policy and
event generator before equations 6.4–6.5, without importing a calibration or
probability model? Version 3.47 is the baseline: 144 source files, 401 pages,
PDF SHA256 b8003bfde4755e171f057588679b6b7a3cedf95685342e6ca438408e34bdd8db.
Its frozen author diagnosis covers all 401 pages and 676 nodes in 98 ordered
segments, with 17 chapter/appendix and eight cumulative-prefix syntheses.
Read-only diagnosis and local-repair replay passed on recovery. R347-D01 is
the sole confirmed defect; it is a missing local prerequisite, not a finding
that the displayed equations compute the wrong object.

The protected baseline is docs/design/proposal/manuscript-readability-20261022/.
Create the successor once at
docs/design/proposal/manuscript-readability-20261022-theta/ and preserve evidence
at data/accounting-master/readability-repair-20261022-theta/. The prior source,
PDF, completed diagnosis, immutable bindings, HEAD/index and unrelated dirty
work must retain their bytes. No earlier completed action is rerun.

## Bounded repair and reader task

Allowed source changes: Version 3.47 becomes 3.48 in the title, and one prose
replacement before the simulation display in chapters/05-mathematics.tex.
Define theta as the declared behavioural and event-generation parameters,
whose values are specified by the chosen history, scenario and model
assumptions. Preserve every equation, citation, label, reference and existing
qualification. Do not invent parameter values, a universal parameter domain,
calibration, a prior, or evidence that the model predicts real companies.

At entry, the reader knows why closing balances alone do not describe economic
state. The next question is how a chosen history evolves under drivers and
management actions. The new sentence supplies the parameters required by both
pi and G before their use. It leaves the existing event/accounting/transition
ordering and distinction between simulated and valuation measures intact.
The following conditional-law discussion must remain consistent with those
declared assumptions.

Local reconstruction questions, using only the rendered passage:

1. What does theta contain, and where do its values come from?
2. How do management actions and event generation differ from accounting?
3. Why do a history and a scenario not by themselves justify weights over
   alternative histories or identify a valuation measure with a forecast law?

## Evidence contract, defaults and skeptical audit

Primary local criterion: the rendered prerequisite answers question 1 before
equations 6.4–6.5, with exact reversal of the two allowed source replacements.
Exact preservation of 219 display contents and 727 citation occurrences,
labels/references, protected hashes and unrelated work can veto integration.
A failed build, clipped text, unexplained reflow or added unsupported claim
triggers repair with the failed attempt retained. Build success and source
counts are engineering diagnostics, not comprehension or acceptance criteria.
The result note and manifests preserve this local evidence.

Audit: pass for this bounded repair. The baseline is the actually completed
diagnosis, not an earlier candidate. Theta's interpretation follows the two
existing parameterised functions and subsequent conditioning on declared
behavioural assumptions. Its possible failure is an invented stronger scope;
the earliest check is the exact prose delta against the surrounding section.
The interpretation is a local notation clarification, not a numerical default.
Version numbering is metadata only. Existing CPU-only LuaLaTeX and PyMuPDF
are tooling conveniences; build logs and rendered review check their output.
No stochastic comparison, empirical promotion or model selection is involved.

Pre-mortem: a harmless-looking definition could imply universal calibration;
inspect its wording. Two extra lines could alter downstream page breaks;
compare page text/layout and inspect every reflowed page plus adjacent
transitions and the title. Neither unchanged page count nor a clean build
establishes whole-document readability. No full successor reading credit is
inherited from Version 3.47; complete successor regression remains pending
until actually performed. Independent and human acceptance remain pending.

## Execution and continuation

Protect, copy and edit once; retain an exact reversible patch. Run source
checks, then the existing build command:
`latexmk -lualatex -silent -g -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex`.
Set CUDA_VISIBLE_DEVICES=-1 and task-local TEXMFVAR/TEXMFCACHE under /tmp.
Use tfgpu python3 with -B for checks and rendering. Retain command, environment,
timing, logs and hashes. Render at most six pages per segment; view at most
three page images per tool call. Judge the actual pages before recording review.

Freeze the local repair separately from later regression. Create additive
assessment/operation successors, preserving 53 obligations, six interactions,
46 operations, zero whole-row closures and not_ready. Refresh the four live
controls with the exact successor identity and remaining work. Then continue
ready internal source/method preparation under a freshly audited bounded plan.
Missing human acceptance and unselected E3 choices block dependent promotion
or experiments, not independent preparation. Runtime/controller implementation,
installations, acquired-code execution, empirical campaigns, commits, outreach,
publication and fees remain held.
