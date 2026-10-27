"""One-time synthetic exchange construction; never overwrites saved evidence."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
from exchanges import schemas, canonical, digest, record_digest, dependencies

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=HERE.parent/'company-path-admission-20261023'
JOIN=HERE.parent/'company-operation-path-20261023'


def build():
    if (HERE/'packet.json').exists():
        raise RuntimeError('Packet already exists; use read-only verify.py')
    baseline_bytes=(BASE/'packet.json').read_bytes()
    baseline=json.loads(baseline_bytes)
    registry=deepcopy(baseline['record_registry'])
    manifest=deepcopy(baseline['blobs'])
    extra=schemas();out=HERE/'blobs';out.mkdir(exist_ok=True)
    def blob_bytes(raw,label):
        h=hashlib.sha256(raw).hexdigest()
        if h not in manifest:
            p=out/(h+'.json')
            if p.exists():assert p.read_bytes()==raw
            else:p.write_bytes(raw)
            manifest[h]={'path':str(p.relative_to(ROOT)),
                         'byte_length':len(raw),'label':label}
        return {'kind':'blob','algorithm':'sha256','digest':h,'byte_length':len(raw)}
    def blob(value,label):return blob_bytes(canonical(value),label)
    def add(kind,key,body):
        entry={'kind':kind,'schema':extra['schema_ids'][kind],
               'key':key,'revision':0,'body':body,'dependencies':dependencies(body)}
        h=record_digest(entry);registry[h]=entry
        return {'kind':kind,'schema':entry['schema'],'digest':h}
    saved=json.loads((JOIN/'checks.json').read_text())
    cases={'baseline':{'path':saved['input'],'result':saved['result']}}
    for name in ['second_year_price_revision','first_year_price_revision',
                 'unknown_middle_payroll','middle_supplier_failure']:
        cases[name]=saved['witnesses'][name]
    path_refs={}
    for name,case in cases.items():
        path,run=case['path'],case['result'];years=[]
        for y in run['years']:
            complete=y['run']['status']=='complete_conditional'
            years.append(add('YearOutcome',name+'.year.'+str(y['index']),{
                'index':y['index'],'period':y['period'],
                'year_result_sha256':y['result_sha256'],
                'path_input_sha256':run['branch_sha256'],
                'year_blob':blob(y,name+' annual result'),
                'predecessor_ref':years[-1] if years else None,
                'outcome':'complete_conditional' if complete else 'partial',
                'closing_memory_blob':blob(y['closing_memory'],'conditional memory') if complete else None,
                'historical_admission':False}))
        path_refs[name]=add('PathOutcome',name,{
            'name':name,'path_blob':blob(path,name+' input'),
            'result_blob':blob(run,name+' result'),'branch_sha256':run['branch_sha256'],
            'baseline_export_ref':baseline['root_ref'],'year_refs':years,
            'status':run['status'],'unexecuted':run['unexecuted'],
            'historical_restatement':False})
    revisions=[]
    relations=[('baseline','second_year_price_revision',1,'Explicit second-year price change; settlements remain fixed.'),
               ('baseline','first_year_price_revision',0,'Explicit first-year price change; settlements remain fixed.'),
               ('baseline','unknown_middle_payroll',1,'Declare the unresolved second-year payroll input.'),
               ('baseline','middle_supplier_failure',1,'Declare the second-year supplier-payment stress.'),
               ('unknown_middle_payroll','baseline',1,'Supply the explicit original payroll amount and replay the suffix.')]
    for parent,child,index,reason in relations:
        path=cases[child]['path'];replacement=path['initial_year'] if index==0 else path['continuations'][index-1]
        revisions.append(add('PathRevision',parent+'.to.'+child,{
            'parent_ref':path_refs[parent],'child_ref':path_refs[child],
            'changed_year_index':index,'reason':reason,
            'replacement_blob':blob(replacement,'explicit annual replacement'),
            'parent_input_sha256':digest(cases[parent]['path']),
            'child_input_sha256':digest(path),'historical_restatement':False,'committed':False}))
    root=add('PathExchange','company.path.exchange',{
        'profile':'CompanyPathExchangeDraft/1',
        'baseline_packet_blob':blob_bytes(baseline_bytes,'immutable complete admission packet'),
        'baseline_export_ref':baseline['root_ref'],'path_refs':list(path_refs.values()),
        'revision_refs':revisions,'scope':'archival_synthetic_outcomes_and_assumption_revisions',
        'transactional_storage':False})
    packet={'profile':'CompanyPathExchangeDraft/1','root_ref':root,
            'record_registry':registry,'blobs':manifest}
    for name,value in [('packet.json',packet),('extension-schemas.json',extra)]:
        (HERE/name).write_text(json.dumps(value,indent=2)+'\n')
    protected={}
    for directory in [BASE,JOIN]:
        for p in directory.iterdir():
            if p.is_file():protected[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    protected.update(json.loads((BASE/'baseline.json').read_text()))
    (HERE/'baseline.json').write_text(json.dumps(protected,indent=2)+'\n')
    print(json.dumps({'records':len(registry),'blobs':len(manifest),
                      'paths':len(path_refs),'revisions':len(revisions)}))


if __name__=='__main__':build()
