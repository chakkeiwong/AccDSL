"""In-memory corruption checks; never change saved reading evidence."""
import copy
import hashlib
import json
from pathlib import Path
import regression as r

OUT=Path(__file__).resolve().parent
d=json.loads(r.LEDGER.read_text())
s=json.loads((r.READ/'structure.json').read_text())
segments={row['path']:json.loads((r.ROOT/row['path']).read_text()) for row in d['segments']}
results=[dict(check='bound partial evidence',result=r.validate())]

def reject(name,change,complete=False):
    a,b,c=copy.deepcopy((d,s,segments));change(a,b,c)
    try:r.check_records(a,b,c,complete)
    except AssertionError as e:results.append(dict(check=name,rejected=True,reason=str(e)))
    else:raise AssertionError('Invalid evidence accepted: '+name)

reject('incomplete final review',lambda a,b,c:None,True)
reject('duplicate structural identity',lambda a,b,c:b['nodes'].append(copy.deepcopy(b['nodes'][1])))
reject('changed chapter conclusion',lambda a,b,c:a['chapter_regressions'][0].update(judgment='unbound change'))
reject('forged cumulative judgment',lambda a,b,c:a['cumulative_regressions'][0].update(judgment='unbound change'))
reject('broken entry continuity',lambda a,b,c:c[list(c)[1]].update(entry_state='unrelated entry'))
reject('unread page marked read',lambda a,b,c:b['pages'][a['page_count']-1].update(reading_status='author_read'))
reject('unbound whole-document conclusion',lambda a,b,c:a.update(document_regression={'judgment':'finished'}))
reject('unbound defect closure',lambda a,b,c:a['defect_dispositions'].update({'R07-D001':'closed'}))

def missing_field(a,b,c):
    key=next(iter(c[list(c)[1]]['node_judgments']))
    c[list(c)[1]]['node_judgments'][key].pop('open_question')
    next(n for n in b['nodes'] if n['id']==key)['judgment'].pop('open_question')
reject('missing unit reader question',missing_field)

def escape_parent(a,b,c):
    node=next(n for n in b['nodes'] if n.get('judgment') and n['parent'] not in (None,'document')
        and next(p for p in b['nodes'] if p['id']==n['parent']).get('judgment'))
    node['physical_pages'][0]=1;node['judgment']['physical_pages'][0]=1
    for seg in c.values():
        if node['id'] in seg.get('node_judgments',{}):seg['node_judgments'][node['id']]['physical_pages'][0]=1
reject('unit escapes reviewed parent',escape_parent)

result=dict(question='Can missing or unbound evidence be mistaken for completed successor reading?',
    scope='Engineering rejection checks only; no readership or accounting acceptance.',
    validator_sha256=hashlib.sha256((OUT/'regression.py').read_bytes()).hexdigest(),
    ledger_sha256=hashlib.sha256(r.LEDGER.read_bytes()).hexdigest(),checks=results,
    failures=0)
(OUT/'validator-checks.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(f'{len(results)} evidence validation checks passed; final reading remains incomplete.')
