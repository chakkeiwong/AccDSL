"""Add audit navigation only; preserve active plans and frozen acceptance records."""
from pathlib import Path
import json,hashlib,os
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
paths=['docs/README.md','docs/plans/accounting-master-program.md','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md','data/accounting-master/next-plan.json']
before={p:(R/p).read_bytes() for p in paths}
def sha(v):return hashlib.sha256(v).hexdigest()
live=json.loads(before['data/accounting-master/next-plan.json']);ae=live['active_execution'];cut=json.loads((H/'baseline.json').read_text());current=ae['current_candidate']
changes={}
for p in paths[:-1]:
 t=before[p].decode()
 if 'release-readiness-audit-20261027/result.md' in t:continue
 if p=='docs/README.md':
  addition='- [Release-readiness audit and key gaps](../data/accounting-master/release-readiness-audit-20261027/result.md).\n- [Dependency-ordered release closure plan](plans/accounting-release-closure-20261027.md).\n'
  t=t.replace('- [Current master program]',addition+'- [Current master program]',1)
 else:
  rel='../../data/accounting-master/release-readiness-audit-20261027/result.md' if p.startswith('docs/') else 'release-readiness-audit-20261027/result.md'
  plan='accounting-release-closure-20261027.md' if p.startswith('docs/') else '../../docs/plans/accounting-release-closure-20261027.md'
  t+='\n## Release-readiness audit — 27 October 2026\n\nThe [whole-program audit]('+rel+') identifies nine release gaps at the 5.50\ncutoff: current acceptance decisions, manuscript consistency, a reproducible\nbundle, compatible interfaces, accounting joins, real-company and adverse cases,\nclaim-level literature support, computational scope and independent acceptance.\nThe [closure plan]('+plan+') orders the work against the original requirements.\nThis is an audit annotation, not a successor manuscript or a broad requirement\nclosure. Active technical plans remain selected; reconcile later evidence before\nexecuting the closure sequence. S6 and E3 are not promoted.\n'
 changes[p]=t.encode()
ae['release_readiness_audit']={'date':'2026-10-27','cutoff_candidate':cut['candidate'],'result':'data/accounting-master/release-readiness-audit-20261027/result.md','closure_plan':'docs/plans/accounting-release-closure-20261027.md','gap_register':'data/accounting-master/release-readiness-audit-20261027/release-gap-register.json','requirement_crosswalk':'data/accounting-master/release-readiness-audit-20261027/requirement-crosswalk.json','status':'audit_complete_release_gaps_open','execution_effect':'Navigation and proposed release closure sequence only; no active plan switch, promotion or publication.'}
changes['data/accounting-master/next-plan.json']=(json.dumps(live,indent=2)+chr(10)).encode()
# Detect concurrent changes before committing any navigation file.
for p in paths:
 if (R/p).read_bytes()!=before[p]:raise RuntimeError('Concurrent edit before navigation: '+p)
for p,content in changes.items():
 target=R/p
 if target.read_bytes()!=before[p]:raise RuntimeError('Concurrent edit during navigation: '+p)
 backup=H/'navigation-before-v551'/p;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(before[p]);tmp=target.with_name(target.name+'.release-audit.tmp');tmp.write_bytes(content);os.replace(tmp,target)
after=json.loads((R/'data/accounting-master/next-plan.json').read_text());expected=json.loads(before['data/accounting-master/next-plan.json']);check=json.loads(json.dumps(after));check['active_execution'].pop('release_readiness_audit');expected['active_execution'].pop('release_readiness_audit',None);assert check==expected
record={'live_candidate_at_write':current,'audited_cutoff':cut['candidate'],'active_execution_preserved':True,'changes':[{ 'path':p,'before_sha256':sha(before[p]),'after_sha256':sha((R/p).read_bytes())} for p in changes]};(H/'navigation-changes.json').write_text(json.dumps(record,indent=2)+chr(10));print(json.dumps(record,indent=2))
