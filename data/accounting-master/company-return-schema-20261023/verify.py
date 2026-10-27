"""Native component authoring evidence; static eligibility is not execution."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import os
import platform
import subprocess
import sys
import time
import traceback
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
from return_schema import assess,validate,schema,canonical,digest,ROLES
from return_text import render,lower
from retained_fixture import fixture,bound_to_retained,PACKET


def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def conformance():
    body,raw=fixture();checks=[];adverse={}
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    text=render(body);restored=lower(text);verdict=assess(body)
    check('exact_text_typed_identity',canonical(restored)==canonical(body))
    check('canonical_text_roundtrip',render(restored)==text)
    check('retained_source_binding',bound_to_retained(body,raw))
    check('known_example_statically_eligible',verdict['status']=='statically_eligible')
    check('eligibility_not_execution',verdict.get('executed') is False and verdict.get('accounting_admission') is False and verdict.get('source_admission') is False)
    check('all_shared_account_roles',set(body['accounts'])==set(ROLES))
    def trial(name,edit,expected='invalid'):
        value=deepcopy(body);edit(value);before=canonical(value);answer=assess(value)
        adverse[name]=answer;check(name,answer['status']==expected and answer.get('executed') is False)
        check(name+'_input_unchanged',canonical(value)==before)
    trial('missing_component',lambda b:b.pop('component'))
    trial('extra_component_field',lambda b:b['component'].__setitem__('wallet','100/1'))
    trial('wrong_profile',lambda b:b.__setitem__('profile','CompanyOperationPathDraft/1'))
    trial('integer_boolean',lambda b:b['component'].__setitem__('settled',0))
    trial('noncanonical_rational',lambda b:b['component'].__setitem__('refund','80/2'))
    trial('negative_refund',lambda b:b['component'].__setitem__('refund','-1/1'))
    trial('float_amount',lambda b:b['component'].__setitem__('refund',40.0))
    trial('bad_refund_allocation',lambda b:b['component'].__setitem__('refund','41/1'))
    trial('bad_recovery_allocation',lambda b:b['component'].__setitem__('recovery','17/1'))
    trial('wrong_opening_dta',lambda b:b['tax'].__setitem__('opening_dta','11/1'))
    trial('wrong_tax_basis',lambda b:b['tax'].__setitem__('refund_tax_base','1/1'),'unsupported')
    trial('missing_tax_source',lambda b:b['tax'].pop('source_pointer'))
    trial('unknown_tax_rate',lambda b:b['tax'].__setitem__('rate','unknown'),'unresolved')
    trial('unknown_tax_finding',lambda b:b['tax'].__setitem__('rate_enacted','unknown'),'unresolved')
    trial('false_tax_finding',lambda b:b['tax'].__setitem__('recovery_supported',False),'unsupported')
    trial('false_handling_finding',lambda b:b['events'][0].__setitem__('handling_is_selling_cost',False),'unsupported')
    trial('unknown_settlement',lambda b:b['events'][0].__setitem__('actual_units','unknown'),'unresolved')
    trial('known_contradiction_with_unknown',lambda b:(b['tax'].__setitem__('rate','unknown'),b['component'].__setitem__('refund','41/1')))
    trial('false_finding_with_unknown',lambda b:(b['tax'].__setitem__('rate','unknown'),b['tax'].__setitem__('recovery_supported',False)),'unsupported')
    trial('known_contradiction_with_false_finding',lambda b:(b['tax'].__setitem__('recovery_supported',False),b['component'].__setitem__('refund','41/1')))
    trial('unknown_refund_not_invented',lambda b:b['component'].__setitem__('refund','unknown'),'unresolved')
    trial('unknown_settled_not_truthy',lambda b:b['component'].__setitem__('settled','unknown'),'unresolved')
    trial('multiline_typed_name',lambda b:b.__setitem__('name','first\nsecond'))
    trial('unicode_line_separator',lambda b:b.__setitem__('name','first\u2028second'))
    trial('nul_in_typed_context',lambda b:b['context'].__setitem__('currency','US\x00D'))
    trial('bad_source_pointer_digest',lambda b:b['component'].__setitem__('source_pointer','/record_registry/absent/body'))
    trial('bad_source_pointer_escape',lambda b:b['component'].__setitem__('source_pointer',b['component']['source_pointer']+'/bad~2'))
    trial('zero_units_no_phantom_lot',lambda b:b['events'][0].update(actual_units='0/1',refund_cash='0/1',handling_cash='0/1'),'unsupported')
    trial('wrong_cash_fact',lambda b:b['events'][0].__setitem__('refund_cash','41/1'))
    trial('wrong_method',lambda b:b['events'][0].__setitem__('method','arbitrary.function'))
    trial('wrong_account_role',lambda b:b['accounts'].__setitem__('cash','capital'))
    trial('duplicate_event_identity',lambda b:b['events'][1].__setitem__('id',b['events'][0]['id']))
    trial('sale_before_settlement',lambda b:b['events'].reverse())
    trial('outside_period',lambda b:b['events'][1].__setitem__('date','2026-01-01'))
    trial('missing_lot_reference',lambda b:b['events'][1].__setitem__('lot_id','absent'))
    trial('unknown_identifier',lambda b:b['component'].__setitem__('id','unknown'))
    trial('partial_lot_sale',lambda b:b['events'][1].__setitem__('fraction','1/2'),'unsupported')
    trial('false_sale_control',lambda b:b['events'][1].__setitem__('performance_complete',False),'unsupported')
    trial('double_sale',lambda b:b['events'].append({**deepcopy(b['events'][1]),'id':'second_sale'}))
    # Source correspondence remains separate from generic static structure.
    for name,edit in [('owner',lambda b:b['context'].__setitem__('entity','Northstar')),
        ('currency',lambda b:b['context'].__setitem__('currency','EUR')),
        ('source_pointer',lambda b:b['component'].__setitem__('source_pointer','/record_registry/missing/body')),
        ('event_amount',lambda b:b['events'][1].__setitem__('proceeds','41/1'))]:
        value=deepcopy(body);edit(value)
        check('changed_'+name+'_source_binding_refused',not bound_to_retained(value,raw))
    check('changed_source_bytes_refused',not bound_to_retained(body,raw+b' '))
    uni=deepcopy(body);uni['name']='P Café';check('unicode_text_roundtrip',canonical(lower(render(uni)))==canonical(uni))
    nfd=deepcopy(uni);nfd['name']='P Café';check('unicode_no_normalization',digest(uni)!=digest(nfd))
    label=deepcopy(body);label['name']='unknown';check('unknown_label_not_unknown_amount',assess(label)['status']=='statically_eligible')
    quoted=deepcopy(body);quoted['name']='P "return"; it\'s \\ quoted'
    check('quoted_metadata_exact_roundtrip',canonical(lower(render(quoted)))==canonical(quoted))
    malformed=[text.replace('accounts;','accounts;\naccounts;',1),text.replace('end_module;',''),
        text+'source invalid;',text.replace('accounts;','include arbitrary;',1),text.replace(' false;',' 0;',1)]
    for i,value in enumerate(malformed):
        try:lower(value);bad=False
        except Exception:bad=True
        check('malformed_text_'+str(i),bad)
    # A settled opening can carry its explicit recovered lot, without creating cash.
    carry=deepcopy(body);carry['component'].update(settled=True,refund='0/1',recovery='0/1')
    carry['tax'].update(opening_dta='0/1',opening_dtl='0/1')
    carry['lots']=[{'id':'recovered','component_id':'return_component','units':'2/1','carrying':'20/1','tax_base':'20/1','acquired':'2024-12-31'}]
    carry['events']=carry['events'][1:]
    check('opening_lot_roundtrip',canonical(lower(render(carry)))==canonical(carry))
    check('settled_lot_static_eligibility',assess(carry)['status']=='statically_eligible')
    carry['lots'][0]['tax_base']='21/1'
    check('different_lot_tax_method_refused',assess(carry)['status']=='unsupported')
    # Existing frontend is tested through its own unchanged API.
    path=HERE.parent/'company-text-20261023/frontend.py';spec=importlib.util.spec_from_file_location('legacy_native_return_check',path)
    legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    family_path=HERE.parent/'company-family-20261023/fixture.json';family=json.loads(family_path.read_text())
    for member in family['members']:
        check('legacy_roundtrip_'+member['id'],canonical(legacy.lower(legacy.render(member['path'])))==canonical(member['path']))
    locks=json.loads((HERE.parent/'company-native-return-design-20261023/source-lock.json').read_text())
    for name in ['company-native-return-design-20261023/specification.md','company-native-return-design-20261023/checks.json',
                 'company-text-20261023/frontend.py','company-operation-path-20261023/schema.json']:
        p=HERE.parent/name;locks[str(p.relative_to(ROOT))]=sha(p)
    for name,h in locks.items():assert sha(ROOT/name)==h,name
    return {'passed':all(x['passed'] for x in checks),'checks':checks,'adverse':adverse,'assessment':verdict},body,text,locks


def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'record already exists'
    started=datetime.now(timezone.utc).isoformat();timer=time.monotonic()
    if mode=='--replay':
        m=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for name,h in m[group].items():assert sha(ROOT/name)==h,name
    result,body,text,locks=conformance()
    observation={'mode':mode,'passed':result['passed'],'checks':len(result['checks']),
        'failed':[x['name'] for x in result['checks'] if not x['passed']],
        'protected_files':len(locks),'wall_seconds':time.monotonic()-timer}
    if not result['passed']:dump(HERE/('failed-checks-'+str(time.time_ns())+'.json'),result)
    elif mode=='--record':
        dump(HERE/'checks.json',result);dump(HERE/'fixture.json',body);dump(HERE/'schema.json',schema());dump(HERE/'source-lock.json',locks)
        (HERE/'example.accdsl').write_text(text)
        outputs={str(p.relative_to(ROOT)):sha(p) for p in [HERE/'checks.json',HERE/'fixture.json',HERE/'schema.json',HERE/'source-lock.json',HERE/'example.accdsl']}
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':observation['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version()+'; exact static reference',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic',
            'inputs':locks,'implementation':{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.md']},
            'outputs':outputs,'plan':'docs/plans/accounting-company-return-schema-20261023.md','result':str(HERE.relative_to(ROOT)/'result.md')})
    elif mode=='--replay':
        assert canonical(result)==canonical(json.loads((HERE/'checks.json').read_text()))
        assert canonical(body)==canonical(json.loads((HERE/'fixture.json').read_text()))
        assert text==(HERE/'example.accdsl').read_text()
    print(json.dumps(observation));return 0 if result['passed'] else 1
if __name__=='__main__':
    try:sys.exit(main())
    except Exception as exc:
        p=HERE/('failure-'+str(time.time_ns())+'.txt');p.write_text(traceback.format_exc())
        print(json.dumps({'status':'failed','error':type(exc).__name__+': '+str(exc)[:400],'diagnostic':str(p.relative_to(ROOT))}));sys.exit(1)
