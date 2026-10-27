from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT=Path('/home/chakwong/python/AccDSL')
OUT=ROOT/'data/accounting-master/p08-diagnosis-20261003'
RUN=ROOT/'data/accounting-master/runs/20261003T075910-81c6e8bb/P08'
def read(p):return json.loads(p.read_text())
def save(name,d): (OUT/name).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
attempts=[]
for folder in sorted(RUN.glob('execution-*')):
    process_file=next(folder.glob('*.process.json'))
    process=read(process_file)
    log=next(folder.glob('*.log'))
    commands=[];messages=[];errors=[];bad=[];terminal=[]
    for line_number,line in enumerate(log.open(),1):
        try:row=json.loads(line)
        except json.JSONDecodeError:continue
        item=row.get('item',{})
        if row.get('type') in ('error','turn.failed','turn.completed'):
            terminal.append({'line':line_number,**row})
        if row.get('type')=='item.completed':
            if item.get('type')=='agent_message':
                messages.append({'line':line_number,'text':item.get('text','')})
            if item.get('type')=='command_execution':
                commands.append(item.get('command',''))
                if item.get('exit_code') not in (None,0):
                    bad.append({'line':line_number,'exit_code':item.get('exit_code'),'output_tail':item.get('aggregated_output','')[-1400:]})
    changes=read(folder/'changes.json')
    recovery=read(next(folder.glob('*.recovery.json')))
    attempts.append({'attempt':folder.name,'process':{k:process.get(k) for k in ('exit_code','reason','wall_seconds')},'completed_commands':len(commands),'agent_messages':messages,'failed_commands':bad,'terminal_events':terminal,'change_counts':{k:len(v) for k,v in changes.items()},'changed_code':[x for values in changes.values() for x in values if x.startswith(('scripts/','tests/'))],'structured_work_responses':[str(x.relative_to(ROOT)) for x in folder.glob('*.response.json')],'supervisor_checks':[str(x.relative_to(ROOT)) for x in folder.glob('checks.json')],'budget':recovery['budget'],'recovery_latest_check':recovery['recent_records'].get('checks',{}).get('path'),'recovery_latest_review':recovery['recent_records'].get('result_review',{}).get('path'),'log_path':str(log.relative_to(ROOT)),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
save('attempt-trace.json',attempts)

rdf=ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-metadata.rdf'
r=ET.parse(rdf).getroot();ns='{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
subject='http://publications.europa.eu/resource/celex/32023R1803'
relations={}
for node in r:
    if node.get(ns+'about')==subject:
        for edge in node:
            obj=edge.get(ns+'resource','')
            if obj:relations.setdefault(obj,[]).append(edge.tag.rsplit('}',1)[-1])
old=read(ROOT/'docs/design/research/p08-v3/authority-register.json')
matrix=[]
for item in old['missing_authority']:
    obj=item['url'].replace('https://','http://')
    predicates=relations.get(obj,[])
    matrix.append({'id':item['id'],'claimed_kind':item['kind'],'claimed_role':item['role'],'actual_predicates':predicates,'genuine_amendment_link':any('amended_by' in x for x in predicates),'genuine_correction_link':any('corrected_by' in x for x in predicates),'citation_only':bool(predicates) and all('cited_by' in x for x in predicates)})
save('source-dependency-trace.json',{'metadata':str(rdf.relative_to(ROOT)),'metadata_sha256':hashlib.sha256(rdf.read_bytes()).hexdigest(),'subject':subject,'all_missing_authority_rows':matrix,'citation_only_mislabeled_amendments':[row['id'] for row in matrix if row['claimed_kind']=='amendment' and row['citation_only']],'scope':'Direct inspection of subject and predicates, confirmed against retained EEA decision texts. This is not an applicability verdict on uninspected corrigenda.'})

access=[]
for version in ('p08-v3','p08-v4','p08-v5'):
    for path in sorted((ROOT/'docs/design/research'/version).glob('access*.json')):
        d=read(path)
        rows=d if isinstance(d,list) else d.get('attempts',[d])
        elapsed=d.get('elapsed_seconds') if isinstance(d,dict) else None
        if elapsed is None and all(isinstance(row.get('seconds'),(int,float)) for row in rows):elapsed=sum(row['seconds'] for row in rows)
        access.append({'path':str(path.relative_to(ROOT)),'records':len(rows),'recorded_total_seconds':elapsed,'status_counts':dict(Counter(str(row.get('status',row.get('error','unrecorded'))) for row in rows))})
save('retrieval-timing.json',{'records':access,'total_recorded_seconds':sum(x['recorded_total_seconds'] or 0 for x in access),'scope':'Sum of timings present in retained access records; not model-service time or proof of complete network accounting.'})
print(json.dumps({'attempts':[{k:a[k] for k in ('attempt','process','completed_commands','structured_work_responses','supervisor_checks')} for a in attempts],'citation_only_mislabeled_amendments':[x['id'] for x in matrix if x['claimed_kind']=='amendment' and x['citation_only']],'recorded_source_access_seconds':sum(x['recorded_total_seconds'] or 0 for x in access)},indent=2))
