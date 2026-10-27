"""Map retained literature records to candidate citations without promoting claims."""
from pathlib import Path
import json,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
R=ROOT/'docs/design/research';M=ROOT/'docs/design/proposal/manuscript-corporate-residuals-20261015'
names=['source-support','citation-venue','backward-snowball','forward-snowball','claim-support','omissions']
D={n:json.loads((R/(n+'.json')).read_text()) for n in names}
sources={x['id']:x for x in D['source-support']['records']}
citations={}
for p in sorted(M.rglob('*.tex')):
    for lineno,line in enumerate(p.read_text().splitlines(),1):
        for match in re.finditer(r'\\cite\w*\*?(?:\[[^]]*\]){0,2}\{([^}]+)\}',line):
            for key in match.group(1).split(','):
                citations.setdefault(key.strip(),[]).append({'file':str(p.relative_to(M)),'line':lineno,'text':line})
rows=[]
for i,c in enumerate(D['claim-support']['records']):
    keys=c.get('sources',[c['source']] if 'source' in c else [])
    ss=[]
    for key in keys:
        s=sources.get(key)
        ss.append({'id':key,'classification':s.get('classification') if s else 'not_in_this_ledger',
          'technical_anchor':s.get('inspected_technical_anchors') if s else None,
          'source_path':s.get('local_path') if s else None,'text_path':s.get('text_path') if s else None,
          'current_citations':citations.get(key,[]),'correction_check':s.get('correction_check') if s else None})
    rows.append({'id':f'C{i+1:02d}','inherited_claim':c,'source_records':ss,
                 'review_state':'pending substantive reconciliation; counts are not support'})
result={'candidate':'3.00','claims':rows,'citation_locations':citations,
 'unmatched_citation_keys':sorted(set(citations)-set(sources)),
 'ledger_counts':{n:len(v['records']) for n,v in D.items()},
 'source_files_missing':[x['id'] for x in sources.values() if x.get('local_path') and not (ROOT/x['local_path']).exists()]}
(OUT/'inventory.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'claims':len(rows),'citation_keys':len(citations),'unmatched':result['unmatched_citation_keys'],'missing':result['source_files_missing']},ensure_ascii=False))
