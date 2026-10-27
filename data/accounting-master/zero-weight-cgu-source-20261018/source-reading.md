# Zero-weight CGU reversal: inspected source and limits

18 October 2026. P17/R03–R04; MC17/19/24/26/29/30/35.
Plan: docs/plans/accounting-zero-weight-cgu-source-20261018.md.

## New official source

Australian Accounting Standards Board, AASB 136 *Impairment of Assets*,
compilation 3, 31 December 2022; prepared 6 February 2023, authorised version
F2023C00180 registered 9 February 2023. The cover applies it to annual periods
beginning on/after 1 January 2023 and before 1 July 2026. This is historical
technical support. It does not establish October 2026 applicability or a
complete amendment census. Australian additions remain distinguishable from
the IAS 36 text. No not-for-profit exception is imported into the company case.

Full PDF/text retained in sources/aasb136-dec2022.{pdf,txt}; exact URL and hashes
in source-manifest.json. This is a standard and its accompanying examples,
not a research paper or professional interpretation. Citation/venue counts and
research-paper retraction status do not apply; legal version/application is
the relevant limitation. No source-library or literature-coverage row closes.

| Inspected anchor | Source argument and consequence |
|---|---|
| Cover; paragraphs 104–107, printed 20–21 | Impairment first reduces goodwill, then other assets using carrying proportions and individual floors. Paragraph 106 describes the allocation when individual recoverable amounts cannot be estimated as arbitrary, but still refers to the specified impairment procedures. It supplies no all-zero reversal formula. |
| Paragraphs 109–121, printed 21–23 | A favourable indication prompts a recoverable-amount estimate. Reversal requires changed estimates, not merely discount unwinding. The hypothetical unimpaired carrying amount caps individual reversal. Revaluation origins and subsequent depreciation remain separate. |
| Paragraphs 122–125, printed 23 | CGU reversal uses carrying proportions, excludes goodwill and redistributes cap-blocked amounts pro rata. The inspected wording gives no alternative denominator for zero eligible carrying amounts. Goodwill reversal is prohibited. |
| Example 2, IE23A–IE31, printed 40–41 | Country A export restrictions reduce production. The recoverable amount is CU1,360; impairment is CU1,473, allocated first to goodwill. The 12-year life, forecasts and 15% rate are example inputs, not local defaults. |
| Example 4, IE38–IE43 and Schedules 1–3, printed 43–45 | Improving business conditions prompt re-estimation to CU1,910. Identifiable assets carry CU1,113 before reversal and CU1,500 on the unimpaired basis. Only CU387 is restored; goodwill stays zero. These are positive eligible carrying amounts, not the all-zero case. |

Example 4's CU797 excess is therefore not the permitted reversal: the
unimpaired-carrying cap limits it to CU387. Zero goodwill in that example is
irrelevant to the missing denominator, because goodwill is excluded before
allocation. Treating it as an all-zero CGU example would be wrong relative to
the stated question. The source does not prove that the requested boundary is
impossible.

## Local mathematical diagnosis

Let c_i be eligible non-goodwill carrying amounts before reversal, and R the
amount to allocate after the applicable unit-level findings. The ordinary
uncapped expression R c_i / sum_j c_j requires a positive denominator. If every
c_i is zero, the expression is undefined, rather than a prescribed zero
reversal or a direction to divide equally.

Caps do not generally repair this. With two assets, positive capacities m_1
and m_2 and 0 < R < m_1 + m_2, amounts satisfying the cap and total constraints
alone have x_1 in [max(0, R − m_2), min(m_1, R)] and x_2 = R − x_1. This
interval follows by substitution into 0 ≤ x_i ≤ m_i and has positive width
under those premises. At R = 0 or R = m_1 + m_2 it collapses; that mathematical
uniqueness still does not supply an authoritative allocation rule. These are
cap-compatible amounts, not a claim of IAS 36 admissibility. Choosing capacity
weights, pre-impairment weights or equal weights would add a policy not
established by the inspected passage.

## Access failures and search quality

IFRScommunity's impairment page returned HTTP 403 both in the sandbox and on
the trusted retry; challenge HTML and headers are retained separately. No
technical content was inspected or inferred from that page. The candidate
Grant Thornton article path returned HTTP 404; its large generic HTML response
is not the requested article. A Google search returned only a script/redirect
shell in the extracted text. Bing's RSS response returned unrelated literary
language pages despite the preserved IAS 36 query. These search responses
cannot establish topic coverage, source absence or an accounting conclusion.
No second retry or bypass was attempted after the trusted access result.

Proposed answer remains unresolved: reject automatic all-zero CGU allocation
with an explicit unsupported-method disposition and preserve the books. The
strongest competing route is asset-level recoverable-amount evidence or a
separately justified policy; either changes required premises and must be
inspected before use. A new lead is the professional impairment manual's
specific discussion of fully impaired CGUs and subsequent recovery, obtained
via its publisher's contents/index rather than the failed guessed article URL.
This lead is not yet inspected or support. Internal research remains open;
no accountant engagement or fees are requested.
