"""Advance only the four authorised live controls; prior entries stay historical."""
from pathlib import Path
import json
U=Path(__file__).resolve().parent
R=U.parents[2]
block='''## 20 October 2026 — Version 3.45 integration

Current candidate: **Version 3.45, 401 pages; not_ready**.
PDF: docs/design/proposal/manuscript-reserve-risk-20261020/accounting-product-proposal.pdf
SHA256: 92b1ab24970cb301ba96d409edcadd3679fc778917c81e82b1c82da592e3dd0d

The finite reserve-risk method is integrated. The addition specifies boundary
atoms in expected shortfall, corrected PH survival weights, expected future
standard deviation, true-conditional-mean CDR variance sums and capital timing.
All 143 earlier source files, 208 displays and 718 citations are preserved;
eleven displays and nine citations are added. Local author review covers
physical 306–313, with title/contents inspected separately. Sources, first
attempt, build and review evidence are retained in
data/accounting-master/reserve-risk-integration-20261020/.

The exact-candidate R08 successor preserves all 53 obligations, six
interactions and 46 operations, with zero whole-row closures. Completed 3.44
author regression remains historical. Version 3.45 whole-document and
affected-chapter regression are pending; no inherited reading credit applies.
Independent implementability, domain and human acceptance remain pending.

Next: initialize the exact 3.45 reading inventory after correcting the old
review helper's hardcoded 396-page assumption in a new local copy. Read the
affected insurance chapter separately, and start the whole-document chain at
physical page 1. Record segments of at most six pages, at most three images
per call, with actual judgments and exact entry/exit continuity. Then continue
the named Wang1995 and Merz/Wüthrich2014 original-source inquiries and edition
comparison. Allocation, current authority and actual entity preferences remain
separate dependencies. The E3 target and its six scientific choices remain
unselected; all 192 vintage admissions remain false.

The plan was skeptically re-audited at recovery. No global continuation veto
has fired. Runtime/controller, installations, empirical campaigns, acquired-code
execution, commits, outreach, publication and fees remain held. Replay a
completed unit only through its no-flag verify.py; never rerun one-time stages.
All dated 3.44 entries below retain their historical scope.

'''
old='''Next: audit and integrate the finite risk-measure and future-information method
into a new provisional manuscript candidate, preserving3.44. Read the actual
changed pages and maintain all source/assumption boundaries. Original Wang1995,
Merz/Wüthrich2014,current authority and entity choices remain named dependencies;
no new default or empirical admission follows.'''
new='''The finite reserve-risk integration is now delivered in Version 3.45; see the
current integration entry above. Next complete actual 3.45 regression, then
continue the consequential original-source inquiries. Wang1995,
Merz/Wüthrich2014,current authority and entity choices remain named dependencies;
no new default or empirical admission follows.'''
for name in json.loads((U/'protection.json').read_text())['controls']:
    p=R/name;t=p.read_text()
    assert '## 20 October 2026 — Version 3.45 integration' not in t
    assert t.count(old)==1,name
    t=t.replace(old,new,1)
    t=t.replace('argument defect. Preserve3.44,396 pages,**not_ready**,53/6/46 and zero whole-row',
                'argument defect. Preserve3.45,401 pages,**not_ready**,53/6/46 and zero whole-row',1)
    t=t.replace('19 October 2026. Current candidate: **Version 3.44, 396 pages; not_ready**.',
                'Historical 19 October 2026 candidate: **Version 3.44, 396 pages; not_ready**.',1)
    t=t.replace('Updated 19 October 2026. Current proposal: **Version 3.44, 396 pages; not_ready**.',
                'Historical checkpoint, 19 October 2026: **Version 3.44, 396 pages; not_ready**.',1)
    t=t.replace('Current candidate update, 18 October 2026: the exact proposal is Version 3.44',
                'Historical candidate update, 18 October 2026: the exact proposal was Version 3.44',1)
    title,rest=t.split(chr(10),1)
    p.write_text(title+chr(10)*2+block+rest.lstrip(chr(10)))
print('Refreshed four live controls for exact Version 3.45; historical records retained.')
