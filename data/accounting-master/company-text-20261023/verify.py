"""Text/typed input equivalence; read-only replay by default."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from jsonschema.exceptions import ValidationError
from frontend import HERE,SCHEMA,render,lower

ROOT=HERE.parents[2];EXCHANGE=HERE.parent/'company-path-exchanges-20261023'
POLICY=HERE.parent/'company-policy-20261023'
sys.path.insert(0,str(EXCHANGE))
from support import context
from exchanges import digest,canonical


def conformance():
    previous,engine,validate=context()
    packet=json.loads((EXCHANGE/'packet.json').read_text());raw=previous.load_blob_files(packet)
    records=packet['record_registry'];root=records[packet['root_ref']['digest']]['body']
    export=records[root['baseline_export_ref']['digest']]['body'];source=raw[export['source_bundle_blob']['digest']]
    cases={}
    for ref in root['path_refs']:
        body=records[ref['digest']]['body'];cases[body['name']]={
            'path':json.loads(raw[body['path_blob']['digest']]),'result':json.loads(raw[body['result_blob']['digest']])}
    policy=json.loads((POLICY/'checks.json').read_text())
    cases['explicit_collection_policy']={'path':policy['materialization']['path'],'result':policy['generated_result']}
    checks=[];texts={};witnesses={}
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    for name,case in cases.items():
        original=deepcopy(case['path']);text=render(case['path']);restored=lower(text);texts[name]=text
        check('exact_typed_roundtrip:'+name,restored==original)
        check('canonical_identity:'+name,digest(restored)==digest(original))
        check('deterministic_text:'+name,render(restored)==text)
        check('no_input_mutation:'+name,original==case['path'])
        run=engine.wire(engine.execute(restored,source))
        check('exact_saved_execution:'+name,run==case['result'])
        check('all_report_bytes:'+name,[y['report'] for y in run['years']]==[y['report'] for y in case['result']['years']])
    original=cases['baseline']['path'];text=texts['baseline']
    check('all_fourteen_operation_kinds_present',len({o['kind'] for y in [original['initial_year']]+original['continuations'] for o in y['operations']})==14)
    check('all_sixty_three_operations_preserved',text.count('\noperation ')==63)
    quoted=deepcopy(original);quoted['name']='Northstar "quoted"; # not a comment'
    quoted['assumption']="It's an explicit assumption with spaces, backslash \\ and ; punctuation."
    check('quoted_text_preserved',lower(render(quoted))==quoted)
    check('blank_lines_ignored',lower('\n\n'+text+'\n\n')==original)
    for value in [True,False,'unknown']:
        p=deepcopy(original);next(o for o in p['initial_year']['operations'] if o['kind']=='delivery')['payload']['control_transferred']=value
        check('truth_literal_preserved:'+str(value),lower(render(p))==p)
    p=deepcopy(original);p['initial_year']['operations'][0]['at']='unknown'
    check('unknown_date_preserved',lower(render(p))==p)
    p=deepcopy(original);p['initial_year']['operations'][0]['payload']['units']='unknown'
    check('unknown_amount_preserved',lower(render(p))==p)
    def reject(name,bad):
        try:lower(bad);value={'rejected':False}
        except (ValueError,ValidationError) as exc:value={'rejected':True,'error':str(exc).splitlines()[0][:250]}
        witnesses[name]=value;check(name,value['rejected'])
    lines=text.splitlines();first=lambda prefix:next(l for l in lines if l.startswith(prefix))
    op=first('operation ');allocation=first('allocate ');asset=first('asset ')
    claim=first('opening_claim ');period=first('period ')
    reject('missing_semicolon',text.replace(op,op[:-1],1))
    reject('unknown_directive',text.replace(op,'include /etc/passwd;',1))
    reject('duplicate_scalar',text.replace(period,period+'\n'+period,1))
    reject('missing_required_scalar',text.replace(first('information '),'',1))
    reject('missing_explicit_array',text.replace('assets;\n','',1))
    reject('duplicate_array',text.replace('assets;','assets;\nassets;',1))
    reject('duplicate_operation',text.replace(op,op+'\n'+op,1))
    reject('duplicate_asset',text.replace(asset,asset+'\n'+asset,1))
    reject('duplicate_opening_claim',text.replace(claim,claim+'\n'+claim,1))
    reject('duplicate_allocation',text.replace(allocation,allocation+'\n'+allocation,1))
    reject('allocation_before_operation',text.replace('operations;','operations;\n'+allocation,1))
    reject('allocation_wrong_kind',text.replace(op,op+'\nallocate purchase-1-a arbitrary 1/1;',1))
    reject('extra_allocation_argument',text.replace(allocation,allocation[:-1]+' extra;',1))
    reject('unknown_operation',text.replace(' purchase ',' unimplemented_operation ',1))
    reject('missing_operation_payload',text.replace(op,'operation purchase-1-a purchase 2025-01-02T09:00:00Z;',1))
    reject('forbidden_continuation_opening',text.replace('continuation;','continuation;\nsource fake '+('0'*64)+';',1))
    reject('continuation_before_initial',text.replace('initial_year;','continuation;',1))
    reject('second_initial_year',text.replace('continuation;','initial_year;',1))
    reject('missing_end_path',text.replace('end_path;',''))
    reject('missing_end_year',text.replace('end_year;','',1))
    reject('trailing_executable_text',text+'exec system;\n')
    reject('noncanonical_rational',text.replace('17/1 purchase-ap-a','34/2 purchase-ap-a',1))
    reject('decimal_rational',text.replace('17/1 purchase-ap-a','17.0 purchase-ap-a',1))
    reject('invalid_truth',text.replace(' true sales-ar-a',' True sales-ar-a',1))
    reject('inline_comment_not_silently_ignored',text.replace(op,op+' # comment;'))
    reject('unterminated_quote',text.replace(op,"operation 'unterminated;",1))
    reject('unclosed_block',text[:text.rfind('end_year;')])
    reject('wrong_profile',text.replace('CompanyOperationPathDraft/1','OtherProfile',1))
    reject('empty_declaration',text.replace(op,';',1))
    reject('closing_directive_extra_argument',text.replace('end_year;','end_year extra;',1))
    p=deepcopy(original);p['assumption']='line one\nline two'
    try:render(p);rejected=False
    except ValueError:rejected=True
    check('multiline_values_explicitly_unsupported',rejected)
    # A parser preserves valid typed unknowns and negative assumptions; execution
    # retains responsibility for domain validity and failure status.
    p=deepcopy(original);p['initial_year']['operations'][0]['payload']['units']='-1/1'
    check('negative_numeric_input_not_silently_changed',lower(render(p))==p)
    protected=json.loads((HERE/'baseline.json').read_text()) if (HERE/'baseline.json').exists() else {}
    check('protected_inputs_unchanged',all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h for name,h in protected.items()))
    return {'checks':checks,'passed':all(c['passed'] for c in checks),'witnesses':witnesses,
            'case_identities':{n:digest(c['path']) for n,c in cases.items()}},texts


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record',action='store_true');args=parser.parse_args()
    target=HERE/'checks.json'
    if args.record and target.exists():raise RuntimeError('Existing evidence; use read-only verification')
    if args.record:
        protected={}
        for folder in [EXCHANGE,POLICY,HERE.parent/'company-operation-path-20261023']:
            for f in folder.iterdir():
                if f.is_file():protected[str(f.relative_to(ROOT))]=hashlib.sha256(f.read_bytes()).hexdigest()
        protected.update(json.loads((EXCHANGE/'baseline.json').read_text()))
        (HERE/'baseline.json').write_text(json.dumps(protected,indent=2)+'\n')
    start=datetime.now(timezone.utc).isoformat();clock=time.perf_counter();evidence,texts=conformance()
    if args.record:
        target.write_text(json.dumps(evidence,indent=2)+'\n')
        (HERE/'schema-lock.json').write_text(json.dumps(SCHEMA,indent=2)+'\n')
        examples=HERE/'examples';examples.mkdir(exist_ok=True)
        for name,text in texts.items():(examples/(name+'.accdsl')).write_text(text)
        manifest={'started_utc':start,'wall_seconds':time.perf_counter()-clock,
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/company-text-20261023/verify.py --record',
            'environment':'system Python '+platform.python_version()+'; jsonschema; shlex; trusted local execution',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES='+str(os.environ.get('CUDA_VISIBLE_DEVICES')),
            'data_version':json.loads((HERE/'baseline.json').read_text()),'random_seeds':'N/A: deterministic',
            'plan':'docs/plans/accounting-company-text-20261023.md','result':'data/accounting-master/company-text-20261023/result.md',
            'files':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in list(HERE.glob('*'))+list(examples.iterdir()) if f.is_file()}}
        (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    elif target.exists():
        if json.loads(target.read_text())!=evidence:raise AssertionError('Evidence mismatch')
        if json.loads((HERE/'schema-lock.json').read_text())!=SCHEMA:raise AssertionError('Schema mismatch')
        for name,text in texts.items():
            if (HERE/'examples'/(name+'.accdsl')).read_text()!=text:raise AssertionError('Saved text mismatch: '+name)
    failed=[c['name'] for c in evidence['checks'] if not c['passed']]
    print(json.dumps({'checks':len(evidence['checks']),'passed':not failed,'failed':failed,'recorded':args.record}))
    return bool(failed)


if __name__=='__main__':raise SystemExit(main())
