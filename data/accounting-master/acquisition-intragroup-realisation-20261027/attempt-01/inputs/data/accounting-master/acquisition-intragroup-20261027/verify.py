"""Bounded complete-output comparison with refusals and retained run inputs."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from datetime import datetime,timezone
import json,os,sys,time,platform,subprocess,resource,traceback,fitz
import reference as m
import fixtures as f
H=Path(__file__).resolve().parent;R=H.parents[2]
def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'
    resource.setrlimit(resource.RLIMIT_CPU,(110,110));out=H/sys.argv[1];out.mkdir(exist_ok=False)
    started=datetime.now(timezone.utc).isoformat();clock=time.monotonic();checks=[];cases=[];controls=[]
    files={R/p for p in json.loads((H/'predecessor-lock.json').read_text())}
    files.update(H/p for p in ['reference.py','fixtures.py','verify.py','prepare.py','source_audit.py','retain_followup.py','contract.md','tax-source-review.md','predecessor-lock.json'])
    files.add(R/'docs/plans/accounting-acquisition-intragroup-20261027.md')
    lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in files}
    for p in files:
        q=out/'inputs'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    def ck(name,actual,expected=True):
        checks.append(dict(name=name,passed=actual==expected))
        if actual!=expected:raise AssertionError(name+': '+repr(actual)[:180]+' != '+repr(expected)[:180])
    def run(election,mix,settled,tax):
        name='/'.join([election,mix,'settled' if settled else 'credit',tax]);b=f.fixture(election,mix,settled,tax);before=deepcopy(b)
        r=m.report(b);ck(name+'/status',r['status'],'tax_method_required' if tax=='unresolved' else 'conditional_intragroup_worksheet')
        ck(name+'/immutable',b,before);ck(name+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS))
        expected=f.expected(election,mix,settled,tax)
        for key,value in expected.items():ck(name+'/'+key,r[key],value)
        ck(name+'/request_binding',r['request_sha256'],f.digest(b))
        ck(name+'/base_binding',r['base_result_sha256'],b['payload']['base_result_sha256'])
        if tax=='unresolved':ck(name+'/no_final_report','report' not in r)
        else:
            ck(name+'/inventory',r['report']['inventory']['group_carrying'],'20/1')
            ck(name+'/nci_profit_unchanged',r['report']['nci_profit'],f.prior(election,mix)['result']['report']['nci_profit'])
            ck(name+'/cash_unchanged',r['report']['cash'],f.prior(election,mix)['result']['report']['cash'])
        cases.append(dict(id=name,request=b,result=r));return r
    def reject(name,b,reason,rehash=True):
        if rehash:f.bind(b)
        before=deepcopy(b);r=m.report(b)
        ck(name+'/status',r['status'],'invalid');ck(name+'/reason',r['reason'],reason)
        ck(name+'/immutable',b,before);ck(name+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS));ck(name+'/no_report','report' not in r)
        controls.append(dict(id=name,request=b,result=r))
    try:
        # Primary-source string anchors identify text, not entity applicability.
        sources=[('source-inspection-01/aasb112-compiled-sep2023.pdf',9,['In consolidated financial statements','tax base']),
          ('source-inspection-01/aasb112-compiled-sep2023.pdf',12,['probable that taxable profit','24']),
          ('source-inspection-01/aasb112-compiled-sep2023.pdf',14,['same taxation authority','same taxable entity']),
          ('source-inspection-01/aasb112-compiled-sep2023.pdf',17,['substantively enacted','manner in which']),
          ('source-inspection-01/aasb112-compiled-sep2023.pdf',21,['profit or loss','business combination']),
          ('source-inspection-01/aasb112-compiled-sep2023.pdf',33,['Unrealised profits resulting from intragroup','no equivalent adjustment']),
          ('source-inspection-02/aasb18-appendix-d.pdf',44,['AASB 112 Income Taxes','62A, 77']),
          ('source-inspection-02/aasb18-appendix-d.pdf',45,['98N','when it applies AASB 18']),
          ('source-inspection-02/aasb2026-2-compiled.pdf',21,['Amendments to AASB 112','AusCF1']),
          ('source-inspection-02/aasb10-2026.pdf',31,['eliminate in full','temporary differences'])]
        for path,page,anchors in sources:
            text=' '.join(fitz.open(H/path)[page-1].get_text().split())
            for anchor in anchors:ck('source/'+path+'/'+str(page)+'/'+anchor,anchor in text)
        run('proportional','cash',False,'recognised')
        for election in ['proportional','fair_value','none']:
            for mix in ['cash','equity','mixed']:
                for settled in [False,True]:
                    if (election,mix,settled)!=('proportional','cash',False):run(election,mix,settled,'recognised')
        for tax in ['unrecognised','unresolved']:
            for settled in [False,True]:run('proportional','cash',settled,tax)
        b=f.fixture();b['payload']['trade']['price']='31/1';reject('stale_request',b,'payload_binding',False)
        b=f.fixture();b['payload']['base_result_sha256']='0'*64;reject('base_result_tamper',b,'base_result_binding')
        b=f.fixture();b['payload']['source_lock_sha256']='0'*64;reject('source_lock_tamper',b,'source_lock_binding')
        for name,field,value,reason in [
          ('precontrol','at','2025-06-30T00:00:00Z','post_control_trade'),('closing_trade','at','2026-01-01T00:00:00Z','post_control_trade'),
          ('partner','buyer','X','downstream_only'),('upstream','seller','S','downstream_only'),('currency','currency','HKD','trade_units'),
          ('units','unit','thousands','trade_units'),('cost','cost','19/1','fixed_lot_amounts'),('price','price','29/1','fixed_lot_amounts'),
          ('loss','price','19/1','loss_requires_impairment_method'),('resale','inventory_remaining','half','inventory_scope'),
          ('impairment','impairment','unknown','inventory_scope'),('trade_id','id','reused','trade_identity')]:
            b=f.fixture();b['payload']['trade'][field]=value;reject(name,b,reason)
        b=f.fixture();b['payload']['elimination_fraction']='3/4';reject('ownership_scaled_elimination',b,'full_elimination_required')
        b=f.fixture();b['payload']['tax']={};reject('missing_tax',b,'tax_disposition_required')
        for name,field,value,reason in [('rate','buyer_rate','5/4','tax_basis_or_rate'),('tax_base','tax_base','20/1','tax_basis_or_rate'),('current_tax','current_tax','0/1','current_tax_binding'),('recoverability','recognition','unknown','recognition_disposition'),('tax_allocation','allocation','nci','tax_allocation_required'),('tax_premise','premise','','text_required')]:
            b=f.fixture();b['payload']['tax'][field]=value;reject(name,b,reason)
        for name,field,value,reason in [('pair','trade_id','other','settlement_pair'),('payer','payer','P','settlement_parties'),('settlement_too_early','at','2025-09-01T00:00:00Z','settlement_date'),('settlement_after_closing','at','2026-01-01T00:00:00Z','settlement_date'),('partial_settlement','amount','15/1','settlement_amount'),('settlement_currency','currency','HKD','settlement_units')]:
            b=f.fixture(settled=True);b['payload']['settlement'][field]=value;reject(name,b,reason)
        b=f.fixture();b['payload']['books']['P']['snapshots']['closing']['balances']['cash']='181/1';reject('unexplained_cash',b,'complete_legal_progression')
        b=f.fixture();p=b['payload']['books']['P']['snapshots']['closing']['balances'];p['cash']='181/1';p['capital']='-321/1';reject('balanced_unexplained_movement',b,'complete_legal_progression')
        b=f.fixture();b['payload']['books_sha256']='0'*64;b['expected_payload_sha256']=f.digest(b['payload']);reject('books_hash',b,'books_binding',False)
        b=f.fixture();b['payload']['trade']['extra']=True;reject('open_trade_schema',b,'trade_fields')
        for p,d in lock.items():ck('protected/'+p,sha256((R/p).read_bytes()).hexdigest(),d)
        result=dict(status='PASS',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False)
    except Exception:result=dict(status='FAIL',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),error=traceback.format_exc())
    for name,value in [('verification.json',result),('cases.json',cases),('controls.json',controls),('checks.json',checks),('source-lock.json',lock)]:
        (out/name).write_text(json.dumps(value,indent=2)+'\n')
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic comparison',started_utc=started,wall_seconds=time.monotonic()-clock,data_version='source-lock.json',plan='docs/plans/accounting-acquisition-intragroup-20261027.md',result=str((H/'result.md').relative_to(R)),output=str(out.relative_to(R)))
    (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(result))
    if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
