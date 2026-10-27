"""One-time documentary export; refuses to overwrite a recorded packet."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
from admission import canonical,record_digest,dependencies,blobs,extension_schemas,digest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
JOIN=ROOT/'data/accounting-master/company-operation-path-20261023'
OPS=ROOT/'data/accounting-master/company-operations-20261023'
ANNUAL=ROOT/'data/accounting-master/company-inputs-20261023'
PATH=ROOT/'data/accounting-master/company-path-20261023'
BASE=ROOT/'data/accounting-master/corporate-portable-20261015'

CONTRACTS={
 'purchase':('units * homogeneous unit cost','inventory += cost; payables -= cost; new payable claim','unique claim; nonnegative canonical units'),
 'delivery':('units * unit price; COGS = units * homogeneous cost','receivable and revenue; remove units and carrying cost','unique claim; known true control transfer; sufficient units'),
 'collection':('sum explicitly allocated receivable settlements','cash increases; receivables and named outstanding claims decrease','existing receivable IDs; unique allocations; no over-settlement'),
 'supplier_payment':('sum explicitly allocated payable settlements','cash decreases; payable liability and named outstanding claims decrease','existing payable IDs; unique allocations; no over-settlement; sufficient cash'),
 'payroll':('explicit payroll amount','payroll expense and cash payment','sufficient cash'),
 'plant_addition':('explicit cost and full-year service convention','plant cost and asset cohort increase; cash decreases','unique asset; positive life; service not before acquisition; no midyear fraction'),
 'dividend':('explicit dividend amount','retained earnings and cash decrease','sufficient cash; no legal distributability conclusion'),
 'facility_draw':('explicit principal bounded by limit - drawn - reserved','cash and debt increase; facility principal increases','known eligibility; capacity; one bridge draw'),
 'facility_interest':('principal * annual rate * calendar-date difference / 365','interest expense and cash payment','one bridge; no fees; same settlement date as principal; sufficient cash'),
 'facility_repayment':('explicit drawn principal','cash and debt decrease; facility principal decreases','existing draw; sufficient cash'),
 'depreciation':('sum min(cost/life, cost-accumulated) for assets in service at annual start','depreciation expense and accumulated depreciation increase','one annual event; full-year or no-year service only'),
 'interest':('legacy principal * ((1-floating share)*fixed rate + floating share*floating rate)','legacy interest expense and cash payment','one full-year coupon; share in [0,1]; sufficient cash'),
 'tax':('positive pre-tax profit * synthetic rate','tax expense and immediate payment','nonnegative pre-tax profit; one annual tax after income operations'),
 'close':('reverse temporary accounts; transfer their sum to retained earnings','temporary accounts zero; retained earnings changes by net profit','one final close after all operations')}


def build():
    if (HERE/'packet.json').exists():raise RuntimeError('Packet already exists')
    out=HERE/'blobs';out.mkdir(exist_ok=True)
    blob_index={}
    def blob_data(data,label):
        h=hashlib.sha256(data).hexdigest();p=out/(h+'.json')
        if p.exists():assert p.read_bytes()==data
        else:p.write_bytes(data)
        blob_index[h]={'path':str(p.relative_to(ROOT)),'byte_length':len(data),'label':label}
        return {'kind':'blob','algorithm':'sha256','digest':h,'byte_length':len(data)}
    def file_blob(path,label):
        path=path.resolve()
        if not path.is_relative_to(ROOT):raise ValueError('outside project blob')
        data=path.read_bytes();h=hashlib.sha256(data).hexdigest()
        blob_index[h]={'path':str(path.relative_to(ROOT)),'byte_length':len(data),'label':label}
        return {'kind':'blob','algorithm':'sha256','digest':h,'byte_length':len(data)}
    old=json.loads((BASE/'portable-exchanges.json').read_text())
    schemas=json.loads((BASE/'record-schemas.json').read_text());extra=extension_schemas()
    registry={};opening='888e2e9f8bf413df1f082ab25e48ab922015afe1f520b6271a232bad2d9d9c08'
    admission='17b7de2f921c7bc944a3a91e1c79de9d1600f31c0acb6fe70710d09433ad06d9'
    def collect(d):
        if d in registry:return
        entry=old['record_registry'][d];registry[d]=deepcopy(entry)
        for b in blobs(entry):
            p=ROOT/old['blobs'][b['digest']]['path'];got=file_blob(p,'original source evidence')
            if got!=b:raise ValueError('original blob changed')
        for dep in entry['dependencies']:collect(dep['digest'])
    collect(opening);collect(admission)
    def ref(d):return {'kind':registry[d]['kind'],'schema':registry[d]['schema'],'digest':d}
    def add(kind,key,body):
        entry={'kind':kind,'schema':extra['schema_ids'][kind],'key':key,'revision':0,
            'body':body,'dependencies':dependencies(body)}
        d=record_digest(entry);registry[d]=entry;return ref(d)
    # All code used by the trusted local replay, including imported helpers.
    files={'composition':JOIN/'composition.py','operations':OPS/'operations.py',
        'operation_reporting':OPS/'reporting.py','annual_path_helpers':PATH/'path_semantics.py',
        'annual_authoring':ANNUAL/'authoring.py','annual_semantics':ANNUAL/'semantics.py',
        'annual_reporting':ANNUAL/'reporting.py'}
    engine=[{'role':k,'blob':file_blob(p,'local documentary implementation')} for k,p in files.items()]
    method_code=next(e['blob'] for e in engine if e['role']=='operations')
    conformance=file_blob(OPS/'checks.json','174-check method evidence')
    op_schema=json.loads((OPS/'schema.json').read_text())
    payloads={r['properties']['kind']['const']:r['properties']['payload'] for r in op_schema['properties']['operations']['items']['oneOf']}
    method_refs=[]
    for kind,(calculation,effects,preconditions) in sorted(CONTRACTS.items()):
        mid='northstar.company-operations.'+kind+'@draft1'
        contract={'method_id':mid,'operation_kind':kind,'calculation':calculation,
            'effects':effects,'preconditions':preconditions,
            'common_preconditions':['same entity/book/USD','explicit authored assumption','exact rational input','atomic proposed change'],
            'limitations':['synthetic reference only','no real-book admission','no legal or predictive conclusion'],
            'payload_schema':payloads[kind]}
        method_refs.append(add('PathMethod','method.'+kind,{'method_id':mid,'operation_kind':kind,
            'payload_schema_sha256':digest(payloads[kind]),'contract_blob':blob_data(canonical(contract),'method contract '+kind),
            'implementation_blob':method_code,'conformance_blob':conformance,
            'evidence_scope':'checked_synthetic_reference_only'}))
    checked=json.loads((JOIN/'checks.json').read_text());path=checked['input'];run=checked['result']
    closing_refs=[];report_refs=[];previous=None
    for y in run['years']:
        close=add('ConditionalClose','conditional.close.'+str(y['index']),{
            'year_index':y['index'],'year_result_sha256':y['result_sha256'],'path_input_sha256':run['branch_sha256'],
            'memory_blob':blob_data(canonical(y['closing_memory']),'conditional closing memory'),
            'source_opening_ref':ref(opening),'predecessor_ref':previous,
            'state_kind':'conditional_projection','historical_admission':False})
        closing_refs.append(close)
        report_refs.append(add('PathReport','report.'+str(y['index']),{'year_result_sha256':y['result_sha256'],
            'report_blob':blob_data(canonical(y['report']),'linked annual report'),
            'closing_ref':close,'annual_complete':True}))
        previous=close
    root=add('PathExport','path.export',{'profile':'CompanyPathEvidenceDraft/1',
        'path_blob':blob_data(canonical(path),'authored operation path'),
        'result_blob':blob_data(canonical(run),'checked conditional result'),
        'source_bundle_blob':file_blob(BASE/'portable-exchanges.json','original source registry'),
        'schema_lock_blob':file_blob(BASE/'record-schemas.json','frozen v1 schema lock'),
        'path_schema_blob':file_blob(JOIN/'schema.json','joined path schema'),
        'engine_files':engine,'opening_ref':ref(opening),'synthetic_admission_ref':ref(admission),
        'method_refs':method_refs,'closing_refs':closing_refs,'report_refs':report_refs,
        'evidence_scope':'archival_synthetic_conditional_only','product_implemented':False})
    packet={'profile':'CompanyPathEvidenceDraft/1','root_ref':root,'record_registry':registry,'blobs':blob_index}
    (HERE/'extension-schemas.json').write_text(json.dumps(extra,indent=2)+'\n')
    (HERE/'packet.json').write_text(json.dumps(packet,indent=2)+'\n')
    protected={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in list(files.values())+[JOIN/'checks.json',OPS/'checks.json',BASE/'portable-exchanges.json',BASE/'record-schemas.json']}
    (HERE/'baseline.json').write_text(json.dumps(protected,indent=2)+'\n')
    print(json.dumps({'records':len(registry),'methods':len(method_refs),'conditional_closes':len(closing_refs),'reports':len(report_refs),'blobs':len(blob_index)}))


if __name__=='__main__':build()
