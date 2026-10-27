from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import json
import expander as e
c=e.c
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def literal(v,t=None):return {'expr':'literal','type':t or (e.BOOL if type(v) is bool else c.TEXT),'value':v}
def obj(**fields):return {'expr':'object','fields':fields}
def array(*items):return {'expr':'array','items':list(items)}
def scalar_write(field,value):
    return obj(id={'expr':'operation_id','prefix':'assess.'},op=literal('replace'),
               path=array(literal('claims'),{'expr':'key'},literal(field)),
               value=obj(kind=literal('literal'),value=value))
def main():
    out=HERE/'templates';assert not out.exists();out.mkdir()
    previous=HERE.parent/'parameterized-method-construction-20261026'
    lock=json.loads((previous/'source-lock.json').read_text())
    for n in ['constructor.py','prepare.py','verify.py','design.md','result.md','checks.json','run-manifest.json','cases.json','algorithm-variant.json']:
        p=previous/n;lock[str(p.relative_to(ROOT))]=sha(p)
    for p in (previous/'templates').glob('*.json'):lock[str(p.relative_to(ROOT))]=sha(p)
    dump(HERE/'source-lock.json',lock)
    rows=json.loads((HERE.parent/'event-specialization-audit-20261026/request-comparisons.json').read_text())
    for owner in ('alpha','beta'):
        row=next(r for r in rows if r['company']==owner and r['method']=='assess');req=row['request']
        method=deepcopy(req['method']);method['memory']['definition']['operations']=[]
        tree=e.encode(method)
        definition=tree['fields']['memory']['fields']['definition']['fields']
        definition['state_schema']={'node':'parameter','name':'state_schema'}
        definition['input_schema']={'node':'parameter','name':'input_schema'}
        pred=tree['fields']['postconditions']['fields']['manifest']['fields']['requirements']['items'][0]['fields']['predicate']['fields']
        assert pred['right']['fields']['op']['value']=='const'
        pred['right']['fields']['value']={'node':'parameter','name':'end_exclusive'}
        base={'profile':c.PROFILE,'transition_profile':req['profile'],'context':deepcopy(row['before']['context']),
              'parameters':[{'name':'state_schema','type':c.TEXT,'source':{'kind':'book_metadata','field':'memory_schema'}},
                            {'name':'input_schema','type':c.TEXT,'source':{'kind':'input_schema'}},
                            {'name':'end_exclusive','type':c.DATE,'source':{'kind':'event_input','name':'end_exclusive'}}],
              'method_template':tree,'input_schema_definition':{'profile':c.types.PROFILE,'root':{'node':'record','fields':{}}},
              'residuals':['Native full-intent eligibility remains selected; state-only assessment, not impairment.']}
        rowtypes={n:deepcopy(v['type']) for n,v in row['body_parameters']['memory_definition']['root']['fields']['claims']['values']['fields'].items()}
        due={'expr':'row','field':'due'};day={'expr':'event_metadata','field':'date'};remaining={'expr':'row','field':'remaining'}
        overdue={'expr':'if','condition':{'expr':'date_lt','left':due,'right':day},'then':remaining,'else':literal('0/1',rowtypes['remaining'])}
        ops=[scalar_write('assessed',literal(True)),scalar_write('assessment_date',day),scalar_write('assessed_remaining',remaining),scalar_write('overdue',overdue)]
        suffix=[obj(id=literal('cursor'),op=literal('replace'),path=array(literal('collection_clock'),literal('cursor')),
                    value=obj(kind=literal('literal'),value={'expr':'event_input','name':'end_exclusive','type':c.DATE}))]
        t={'profile':e.PROFILE,'base_template':base,'map_pointer':'/claims','row_types':rowtypes,'row_operations':ops,'suffix_operations':suffix,
           'residuals':['Exact order is caller supplied and bound; no probability or accounting admission.']}
        dump(out/(owner+'.assess.json'),t)
    print(json.dumps({'templates':2,'protected_files':len(lock)}))
if __name__=='__main__':main()
