from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[3]
ASSESS=ROOT/'docs/plans/accounting-proposal/p15-evidence-assessments-v1.json'
COMP=ROOT/'docs/plans/accounting-proposal/p15-evidence-assessments-v1.md'
OUT=ROOT/'docs/plans/accounting-proposal/p15-assessment-validation-v1.json'
ALLOWED={'open','partial','specified','checked_design'}
REQ={f'MC{i:02}' for i in range(1,36)}
GAPS={f'G{i}' for i in range(1,19)}
EXPECTED_DONE={'MC01','MC02','MC03','MC04','MC05','G11','G13','G17'}

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def norm(s): return ' '.join(str(s).split())

def resolve_pointer(obj,pointer):
    if pointer=='': return obj
    if not pointer.startswith('/'): raise KeyError(pointer)
    cur=obj
    for raw in pointer[1:].split('/'):
        tok=raw.replace('~1','/').replace('~0','~')
        if isinstance(cur,list): cur=cur[int(tok)]
        elif isinstance(cur,dict) and tok in cur: cur=cur[tok]
        else: raise KeyError(pointer)
    return cur

def check_ref(ref, counts, errors, refs_seen):
    if not isinstance(ref,dict): errors.append('reference is not an object'); return
    path=ref.get('path'); digest=ref.get('sha256')
    if not isinstance(path,str) or not path or Path(path).as_posix()!=path or '..' in Path(path).parts:
        errors.append(f'noncanonical path: {path!r}'); return
    p=ROOT/path
    refs_seen.append(path)
    if not p.is_file() or p.is_symlink() or p.stat().st_size==0:
        errors.append(f'missing/empty/symlink source: {path}'); return
    actual=sha(p)
    if actual != digest: errors.append(f'hash mismatch: {path} expected {digest} got {actual}')
    loc=ref.get('locator')
    if isinstance(loc,str) and loc.startswith('lines '):
        m=re.fullmatch(r'lines (\d+)-(\d+)',loc)
        if not m: errors.append(f'bad line locator: {path} {loc}')
        else:
            a,b=map(int,m.groups())
            try: n=len(p.read_text(encoding='utf-8').splitlines())
            except Exception as e: errors.append(f'cannot read text for {path}: {e}')
            else:
                counts['line_locators']+=1
                if a<1 or b<a or b>n: errors.append(f'line bounds: {path} {loc} (n={n})')
    elif isinstance(loc,str) and loc.startswith('JSON Pointer '):
        pointer=loc[len('JSON Pointer '):]
        try:
            obj=json.loads(p.read_text(encoding='utf-8'))
            resolve_pointer(obj,pointer)
            counts['json_pointers']+=1
        except Exception as e: errors.append(f'bad JSON pointer: {path} {pointer}: {e}')
    elif loc is not None:
        errors.append(f'unsupported locator: {path} {loc!r}')
    else:
        errors.append(f'missing locator: {path}')
    if 'quote' in ref:
        counts['quotes']+=1
        q=ref.get('quote')
        try: txt=p.read_text(encoding='utf-8')
        except Exception as e: errors.append(f'cannot read quote source {path}: {e}')
        else:
            if not isinstance(q,str) or not q.strip() or norm(q) not in norm(txt): errors.append(f'quote not found: {path}')

errors=[]; counts={'references':0,'line_locators':0,'json_pointers':0,'quotes':0}; refs_seen=[]
try: d=json.loads(ASSESS.read_text(encoding='utf-8'))
except Exception as e:
    d={}; errors.append(f'cannot load assessment JSON: {e}')
if d:
    if d.get('schema_version')!='accdsl.proposal.p15.partial-assessments.v1': errors.append('schema_version mismatch')
    if d.get('phase')!='P15': errors.append('phase mismatch')
    if d.get('product_implemented') is not False: errors.append('product_implemented must be false')
    if d.get('human_acceptance')!='pending': errors.append('human_acceptance must be pending')
    classes=d.get('evidence_classes')
    expected_classes={'specified_design','exploratory_implementation','tested_invariants','accounting_validity','empirical_forecast_validity','human_acceptance'}
    if not isinstance(classes,dict) or set(classes)!=expected_classes or any(not isinstance(v,str) or not v.strip() for v in classes.values()): errors.append('evidence_classes incomplete')
    req=d.get('requirements'); gaps=d.get('gaps')
    ids=[]
    for label, rows in [('requirements',req),('gaps',gaps)]:
        if not isinstance(rows,list): errors.append(f'{label} not list'); continue
        expected=REQ if label=='requirements' else GAPS
        got=[r.get('id') if isinstance(r,dict) else None for r in rows]
        if len(got)!=len(set(got)) or set(got) != (expected & EXPECTED_DONE): errors.append(f'{label} ids mismatch: {got}')
        for r in rows:
            if not isinstance(r,dict): errors.append(f'{label} row not object'); continue
            rid=r.get('id'); ids.append(rid)
            if r.get('status') not in ALLOWED: errors.append(f'{rid} bad status')
            for k in ('assessment','remaining_work','design_consequence'):
                if not isinstance(r.get(k),str) or not r[k].strip(): errors.append(f'{rid} missing {k}')
            ev=r.get('evidence')
            if not isinstance(ev,list) or not ev: errors.append(f'{rid} missing evidence')
            else:
                for ref in ev: counts['references']+=1; check_ref(ref,counts,errors,refs_seen)
    done=set(d.get('completed_ids',[])); rem=set(d.get('remaining_ids',[])); all_ids=REQ|GAPS
    if done != EXPECTED_DONE: errors.append(f'completed_ids mismatch: {sorted(done)}')
    if done & rem or done|rem != all_ids or len(rem)!=45: errors.append('completed/remaining partition mismatch')
    if set(ids)!=EXPECTED_DONE: errors.append('row ids do not equal completed ids')
    decisions=d.get('open_decisions')
    if not isinstance(decisions,list) or len(decisions)!=5 or len({x.get('id') for x in decisions})!=5: errors.append('decision count/uniqueness mismatch')
    else:
        for x in decisions:
            for k in ('id','question','proposed_answer','alternative','consequence','next_step'):
                if not isinstance(x.get(k),str) or not x[k].strip(): errors.append(f'decision {x.get("id")} missing {k}')
            if type(x.get('blocks_proposal')) is not bool: errors.append(f'decision {x.get("id")} blocks_proposal not bool')
    if not isinstance(d.get('source_evidence'),list) or not d['source_evidence']: errors.append('source_evidence missing')
    else:
        for ref in d['source_evidence']: counts['references']+=1; check_ref(ref,counts,errors,refs_seen)
    text=COMP.read_text(encoding='utf-8') if COMP.is_file() else ''
    missing=[x for x in sorted(EXPECTED_DONE) if not re.search(r'\b'+re.escape(x)+r'\b',text)]
    if missing: errors.append('companion missing ids: '+','.join(missing))
    for x in sorted(EXPECTED_DONE):
        if text.count(x)<1: errors.append(f'companion does not mention {x}')
    decision_linkage={
      'P15-E01': ['MC01','G11'], 'P15-E02': ['MC01','MC03','G11'],
      'P15-E03': ['MC02'], 'P15-E04': ['MC05','G13'], 'P15-E05': ['MC04','G17']}
    linkage_status={}
    for did, rows in decision_linkage.items():
        present=did in text
        linkage_status[did]={'rows':rows,'present_in_companion':present}
        if not present: errors.append(f'companion missing decision linkage {did}')
report={
 'schema_version':'accdsl.proposal.p15.assessment_validation.v1',
 'phase':'P15', 'created_at':datetime.now(timezone.utc).isoformat(),
 'passed':not errors, 'scope':'bounded_partial_work',
 'procedure': 'python3 -B docs/plans/accounting-proposal/p15-assessment-validator-v1.py; standard-library validation of the existing eight-row assessment slice',
 'validator': {'path':'docs/plans/accounting-proposal/p15-assessment-validator-v1.py','sha256':sha(Path(__file__).resolve())},
 'inputs': {'assessment_json': {'path':str(ASSESS.relative_to(ROOT)),'sha256':sha(ASSESS)}, 'companion_analysis': {'path':str(COMP.relative_to(ROOT)),'sha256':sha(COMP)}},
 'checked_ids': sorted(EXPECTED_DONE), 'remaining_count':45,
 'decision_linkage': linkage_status,
 'repairs': [{'path':'data/accounting-master/runs/20261003T204010-348e5b02/P15/approved-plan.json','old_sha256':'474e0178d701df124159668bd1d7048678fcb02f4ada43f8d39a7703caf8ab10','new_sha256':'418f48fd15abe7e902c5b832d517f8d76616211cf1817f86241a12e110f77f1c','reason':'source record changed after the assessment was written; reference was updated to the current bytes'}],
 'counts': counts, 'unique_reference_paths':len(set(refs_seen)),
 'checks': [
   {'id':'exact eight approved row IDs','passed':not any('ids mismatch' in e or 'row ids' in e for e in errors)},
   {'id':'required fields and allowed statuses','passed':not any('bad status' in e or 'missing assessment' in e or 'missing remaining_work' in e or 'missing design_consequence' in e for e in errors)},
   {'id':'exact 8/45 obligation partition','passed':not any('partition mismatch' in e for e in errors)},
   {'id':'five complete unique decisions','passed':not any('decision count' in e or 'decision ' in e for e in errors)},
   {'id':'evidence-class and acceptance boundary','passed':not any('evidence_classes' in e or 'product_implemented' in e or 'human_acceptance' in e for e in errors)},
   {'id':'source hashes and anchors','passed':not any(('source' in e or 'locator' in e or 'line ' in e or 'JSON pointer' in e or 'quote' in e) for e in errors)},
   {'id':'companion analysis covers all eight IDs','passed':not any('companion missing ids' in e for e in errors)},
   {'id':'decision linkage retained in companion analysis','passed':not any('decision linkage' in e for e in errors)},
 ],
 'errors':errors,
}
OUT.write_text(json.dumps(report,indent=2,sort_keys=False)+'\n')
print(json.dumps({'passed':report['passed'],'errors':errors,'counts':counts,'sha256':report['inputs']['assessment_json']['sha256']},indent=2))
