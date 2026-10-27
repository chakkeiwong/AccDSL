"""Record bounded author review and exact final edition identities once."""
from pathlib import Path
import json,hashlib,fitz
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'edition-date-repair-02'
def j(p):return json.loads(p.read_text())
v=j(D/'verification.json');assert v['status']=='PASS'
lock=j(D/'source-preservation.json');T=R/lock['target'];main,sim=v['documents']
assert not (H/'result.md').exists()
checks=[]
for name in ['accounting-product-proposal','simulation-foundations']:
    before=fitz.open(H/'readability-repair-01/build-attempt-01'/(name+'.pdf'))
    after=fitz.open(T/(name+'.pdf'))
    assert len(before)==len(after)
    assert '27 October 2026' in after[0].get_text()
    assert all(before[i].get_text()==after[i].get_text() for i in range(1,len(after)))
    checks.append(dict(document=name,body_text_unchanged_after_cover_repair=True,cover_date='2026-10-27'))
(H/'edition-check.json').write_text(json.dumps(checks,indent=2)+'\n')
(H/'author-review.md').write_text('''# Bounded author review of Version 5.26

27 October2026. Status: independent_reader_pending. This is author review,
not independent human comprehension, domain acceptance or whole-document review.

Rendered reading covered the new argument on main physical pages124–126 and
simulation115–117; the earlier governance clarification on main72/simulation63;
the main financing-chapter cross-reference on392; and both covers. A citation
touching its preceding word was repaired in three places and re-read. The
inherited26 October cover date was corrected to27 October; all body-page text
is identical before and after that final date repair.

Mathematical ledger: the retained funding price17000/441 and owner9460/441
sum to60. The forced liability32000/441 leaves−5000/147; accreting the economic
price twice at5% gives85/2. These are the existing exact synthetic calculations,
not new accounting measurement facts. No equation or derivation is removed.

Source ledger: existing AASB132 anchors and the new retained AASB9 compilation
support the conditional issuer/holder discussion. The5.25 control-scope section
is reused rather than duplicated. Source truth, entity scope and the complete
2027/2028 authority chain remain unresolved. No frozen register is expanded.

Engineering ledger: named transforms, source/evidence hashes, bibliography,
labels, both builds and clipping checks pass. Both editions use one source
package, including every source-policy addition from5.25. The stale candidate
and earlier failures remain preserved; no successful writer was rerun.

Reader ledger: the transfer order precedes the measurement counterexample;
issuer and holder perspectives precede the interval-evidence example. The
comparison between snapshots and asserted intervals names its conditional
premise and unresolved financial methods. Cross-references resolve to the
existing control discussion. No clipping or broken citation remains in the
reviewed pages. Independent reader response and whole-document coherence remain
pending; these findings do not certify a human voice or design completeness.
''')
(H/'result.md').write_text(f'''# Funding and conditional control history integrated in Version 5.26

27 October2026. MC05/17/19/20/24/25/28/30/31/32/33/34/35;
W01/05/06/07/08/11/12/16/17. Both editions preserve the live5.25 source-policy
work and add the funding, measurement and interval-history argument.

The main candidate has{main['pages']} pages; simulation has{sim['pages']} total /
{sim['body_pages']} body pages across26 chapters. Final verification passes
{v['assertions']} structural checks, protects{v['protected_sources']} predecessor
sources and{v['protected_evidence']} evidence files, and finds no new warnings,
unresolved references or clipped text. Author review remains independent_reader_pending.

Main SHA256: {main['sha256']}.
Simulation SHA256: {sim['sha256']}.
Final build/check directory: edition-date-repair-02/.
Source package: {lock['target']}/.

The preceding5.24-based candidate passed922 checks but was not advanced because
the shared master had reached5.25. Rebase preserves both contributions. Earlier
duplicate-citation build failure, the successful pre-spacing candidate, and the
two bounded typography/date repairs remain available. None was erased or
rerun into a successful output directory.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain as governing design candidate, subject to guarded advancement | Named source transforms, exact evidence preservation and both rendered editions pass | Stale baseline veto repaired; no new build/reference/clipping defect | Actual contract facts, dated authority, group methods and independent comprehension | Bind interval evidence to the existing group-report boundary; complete acquisition-period authority and measurement | Complete DSL, accounting admission, whole-company simulator or forecast validity |

The22-case interval reference and30-case dependency repair remain conditional.
The original21-case dependency result does not cover its subsequently discovered
boundary defects. Financial, source and software claims remain separate.
Counts are descriptive; statistical ranking is N/A for this document integration.

Post-run red-team: complete conditional coverage can still rest on a false or
incomplete source assertion; balanced entries can still use the wrong measurement.
Those alternatives remain explicit. Real contract/authority evidence and full
changing-perimeter journal/report comparisons would be required to support more.

All53 obligations, six interactions,46 operations and18 broad packages remain
open. S1–S5 partial; S6 held; E3 deferred. No global continuation veto has fired.
Next financing plan: docs/plans/accounting-control-group-boundary-20261027.md.
Independent source-time work and the full programme continue. No installs,
GPU, agents, commits, outreach, fees or publication.
''')
print(json.dumps(dict(status='PASS',main_pages=main['pages'],simulation_pages=sim['pages'],protected_sources=v['protected_sources'],protected_evidence=v['protected_evidence'])))
