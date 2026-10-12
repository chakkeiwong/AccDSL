# Tamer remains source-blocked on the inspected Harvard routes

13 October 2026. The bounded acquisition inquiry is complete. Three distinct
trusted requests supplied no paper: the repository download returned HTTP 405
with `x-amzn-waf-action: captcha`; its public metadata endpoint returned HTTP
401 with “Authentication is required”; the author-file URL returned HTTP 403
Access Denied. Two ordinary sandbox requests failed DNS before their trusted
retries. No access challenge was bypassed, no credentials were requested, and
the old 404 handle was not repeated.

The new download and author URL are supported by the retained institutional
landing page. The metadata endpoint was a derived public API probe using the
page's API base and bitstream identifier, not a discovered content URL. The
two error bodies fetched with `--fail-with-body` are retained. The first curl
used `--fail`, so its 405 body was not downloaded; headers and receipt preserve
the observed challenge. This missing error body is not a missing paper.

P17/E08; MC08–12/18/26/29–30/32–35 and G1/G3/G6/G8/G15. No technical section,
theorem, inference method, reference list or official code was inspected.
Historical OpenAlex and Semantic Scholar metadata remain discovery evidence;
their old retraction flag is not a current correction-history check. The
source remains `SOURCE_BLOCKED`, with no allowed technical claims. The existing
paper collection, source ledgers and Version 2.51 remain unchanged.

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Close these three source routes as blocked | No verified full text recovered | CAPTCHA, authentication requirement and access denial prevent source inspection | Technical content and exact edition | Retain the omission; use a different legitimate source only when a new lead exists | That the paper or method is invalid or unavailable everywhere |
| Preserve Version 2.51 and not_ready | No source finding supports a manuscript change | No existing artifact altered | Wider literature and human/domain acceptance | Continue the new Caiani institutional route | E08 or full proposal completion |

The blocked result concerns acquisition, not implementation, mathematics or
the research direction. The main weakness is that repository accessibility
can change; a verified full text from a legitimate route would overturn the
source-blocked status. No stochastic comparison or method ranking occurred.
No technical claim was inferred from titles, metadata or HTTP status.

Next execute `docs/plans/accounting-caiani-source-recovery-20261013.md` using
the retained 11566/358236 handle. This is distinct from the failed 11383 route.
E01/E05/E07/E08/E14 and all MC01–MC35/G1–G18 obligations remain open.
