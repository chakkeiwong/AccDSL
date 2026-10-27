"""Exact expression and protected policy-adapter checks; no empirical comparison."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import os
import platform
import subprocess
import sys
import time
from expressions import PROFILE,BOOL,SCALAR,FLAGS,analyze,digest,evaluate,schema
from authoring import lower,render
from adapter import materialize

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; REL=HERE.relative_to(ROOT).as_posix()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
def literal(ident,value,typ=SCALAR): return {'id':ident,'op':'literal','type':deepcopy(typ),'value':value}
def node(ident,op,*args): return {'id':ident,'op':op,'args':list(args)}
def program(nodes,output='r',inputs=None):
    return {'profile':PROFILE,'name':'Exact expression example','inputs':inputs or {},'nodes':nodes,'outputs':{'result':output}}
def policy_program():
    return {'profile':PROFILE,'name':'Northstar collection fraction and installments',
            'inputs':{'ordinary':{'type':BOOL,'value':True},'discount':{'type':SCALAR,'value':'1/10'}},
            'nodes':[{'id':'ordinary','op':'input','target':'ordinary'},{'id':'discount','op':'input','target':'discount'},
                     literal('one','1/1'),literal('two','2/1'),literal('stress','4/5'),
                     node('regular','sub','one','discount'),node('fraction','if','ordinary','regular','stress'),node('half','div','one','two')],
            'outputs':{'fraction':'fraction','first_share':'half','second_share':'half'}}
def context():
    folder=HERE.parent/'company-family-20261023'; sys.path.insert(0,str(folder))
    family_checks=load('expression_family_fixture',folder/'verify.py')
    _,cases,source,engine=family_checks.fixtures()
    policy_module=load('expression_policy_generator',HERE.parent/'company-policy-20261023/policy.py')
    policy=json.loads((HERE.parent/'company-policy-20261023/policy.json').read_text())
    prior=json.loads((HERE.parent/'company-policy-20261023/checks.json').read_text())
    return cases['baseline']['path'],policy,prior,source,engine,policy_module.generate
def protected():
    p=HERE.parent/'company-family-20261023'
    base=json.loads((p/'baseline.json').read_text())
    for f in p.rglob('*'):
        if f.is_file() and '__pycache__' not in f.parts and 'control-before' not in f.parts:
            base[str(f.relative_to(ROOT))]=sha256(f.read_bytes()).hexdigest()
    for f in ['docs/design/spec/core-contract.md','docs/design/proposal/manuscript-company-authoring-20261023/sections/portable-values.tex']:
        base[f]=sha256((ROOT/f).read_bytes()).hexdigest()
    return base
def conformance(smoke=False):
    checks=[]; witnesses={}
    def check(name,value): checks.append({'name':name,'passed':bool(value)})
    def expected(name,body,status,value=None):
        outcome=evaluate(body); witnesses[name]=outcome
        check(name,outcome['status']==status and (value is None or outcome.get('outputs',{}).get('result',{}).get('value')==value))
        return outcome
    def reject(name,body): expected(name,body,'invalid')
    money={'kind':'number','dimensions':{'USD':1},'context':'Northstar:book:2026'}
    units={'kind':'number','dimensions':{'unit':1},'context':'Northstar:book:2026'}
    price={'kind':'number','dimensions':{'USD':1,'unit':-1},'context':'Northstar:book:2026'}
    expected('exact_add',program([literal('a','1/3'),literal('b','1/6'),node('r','add','a','b')]),'evaluated','1/2')
    expected('exact_sub',program([literal('a','1/1'),literal('b','1/10'),node('r','sub','a','b')]),'evaluated','9/10')
    mul=expected('units_times_price',program([literal('a','3/1',units),literal('b','5/2',price),node('r','mul','a','b')]),'evaluated','15/2')
    check('product_dimensions_are_money',mul['outputs']['result']['type']==money)
    expected('scalar_scales_money',program([literal('a','100/1',money),literal('b','9/10'),node('r','mul','a','b')]),'evaluated','90/1')
    expected('exact_division',program([literal('a','1/1'),literal('b','3/1'),node('r','div','a','b')]),'evaluated','1/3')
    expected('negation',program([literal('a','1/3'),node('r','neg','a')]),'evaluated','-1/3')
    for op,value in [('lt',True),('le',True),('eq',False)]:
        expected('comparison_'+op,program([literal('a','1/3'),literal('b','1/2'),node('r',op,'a','b')]),'evaluated',value)
    for op,value in [('and',False),('or',True)]:
        expected('logic_'+op,program([literal('a',True,BOOL),literal('b',False,BOOL),node('r',op,'a','b')]),'evaluated',value)
    expected('logic_not',program([literal('a',True,BOOL),node('r','not','a')]),'evaluated',False)
    body=policy_program(); before=deepcopy(body); text=render(body); restored=lower(text)
    check('policy_text_typed_identity',digest(restored)==digest(body))
    check('policy_text_idempotence',render(restored)==text)
    values=evaluate(restored)
    check('independent_fraction_and_shares',[values['outputs'][k]['value'] for k in ['fraction','first_share','second_share']]==['9/10','1/2','1/2'])
    path,policy,prior,source,engine,generate=context()
    mapping={'fraction':'fraction','installment_shares':['first_share','second_share']}
    joined=materialize(restored,path,policy,mapping,generate)
    check('exact_policy_comparator',digest(joined['policy'])==digest(policy))
    check('exact_materialized_path_comparator',digest(joined['materialization'])==digest(prior['materialization']))
    run=engine.wire(engine.execute(joined['materialization']['path'],source))
    check('full_accounting_result_comparator',digest(run)==digest(prior['generated_result']))
    check('no_input_mutation',digest(body)==digest(before))
    check('no_implicit_admission',all(joined[k] is False for k in FLAGS))
    if smoke: return {'passed':all(c['passed'] for c in checks),'checks':checks},body,text,joined,run
    reject('numeric_boolean_alias',program([literal('r',True)]))
    reject('boolean_numeric_alias',program([literal('r','1/1',BOOL)]))
    reject('noncanonical_fraction',program([literal('r','2/2')]))
    reject('float_literal',program([literal('r',0.5)]))
    reject('numeric_truth',program([literal('a','1/1'),node('r','not','a')]))
    reject('money_plus_units',program([literal('a','1/1',money),literal('b','1/1',units),node('r','add','a','b')]))
    other=deepcopy(money); other['context']='OtherCompany:book:2026'
    for op in ['add','mul','eq']:
        reject('cross_context_'+op,program([literal('a','1/1',money),literal('b','1/1',other),node('r',op,'a','b')]))
    uncontextual=deepcopy(units); uncontextual['context']=None
    reject('context_free_units_do_not_bypass_context',program([literal('a','1/1',uncontextual),literal('b','1/1',price),node('r','mul','a','b')]))
    for exponent in [True,0,1.0]:
        typ=deepcopy(money); typ['dimensions']['USD']=exponent
        reject('bad_dimension_'+str(type(exponent))+str(exponent),program([literal('r','1/1',typ)]))
    reject('missing_node',program([node('r','neg','missing')]))
    reject('missing_input',program([{'id':'r','op':'input','target':'missing'}]))
    reject('duplicate_node',program([literal('r','1/1'),literal('r','2/1')]))
    reject('cycle',program([node('a','neg','r'),node('r','neg','a')]))
    reject('dead_cycle_is_statically_invalid',program([literal('r','1/1'),node('a','neg','a')]))
    reject('unknown_operator',program([node('r','python_eval','a')]))
    reject('wrong_arity',program([literal('a','1/1'),node('r','add','a')]))
    forward=program([node('r','add','a','b'),literal('a','1/3'),literal('b','1/6')])
    expected('forward_references',forward,'evaluated','1/2')
    unknown=program([literal('a','unknown'),literal('b','1/1'),node('r','add','a','b')])
    expected('unknown_arithmetic',unknown,'unresolved')
    expected('division_known_zero',program([literal('a','1/1'),literal('b','0/1'),node('r','div','a','b')]),'invalid')
    expected('unknown_over_known_zero',program([literal('a','unknown'),literal('b','0/1'),node('r','div','a','b')]),'invalid')
    expected('unknown_denominator',program([literal('a','1/1'),literal('b','unknown'),node('r','div','a','b')]),'unresolved')
    conditional=program([literal('guard',True,BOOL),literal('one','1/1'),literal('zero','0/1'),node('bad','div','one','zero'),node('r','if','guard','one','bad')])
    expected('unselected_undefined_arithmetic',conditional,'evaluated','1/1')
    false=deepcopy(conditional); false['nodes'][0]['value']=False
    expected('selected_undefined_arithmetic',false,'invalid')
    missing=deepcopy(conditional); missing['nodes'][0]['value']='unknown'
    expected('unknown_guard_not_false',missing,'unresolved')
    mismatch=deepcopy(conditional); mismatch['nodes'][-1]['args'][2]='guard'
    reject('unselected_arm_type_checked',mismatch)
    guardtype=deepcopy(conditional); guardtype['nodes'][-1]['args'][0]='one'
    reject('numeric_guard_refused',guardtype)
    same=program([literal('guard','unknown',BOOL),literal('one','1/1'),node('r','if','guard','one','one')])
    expected('unknown_guard_no_symbolic_equivalence_claim',same,'unresolved')
    dependent=policy_program(); dependent['inputs']['ordinary']['value']=False; dependent['inputs']['discount']['value']='unknown'
    deps=evaluate(dependent)['outputs']['fraction']
    check('unselected_unknown_branch_not_evaluated',deps['status']=='known' and deps['value']=='4/5')
    check('declared_dependencies_include_both_arms',deps['declared_dependencies']==['discount','ordinary'])
    check('evaluated_inputs_exclude_unselected_arm',deps['evaluated_inputs']==['ordinary'])
    evidence=extra_checks(check,witnesses,body,text,joined,run,path,policy,source,engine,generate,mapping)
    evidence.update(passed=all(c['passed'] for c in checks),checks=checks)
    return evidence,body,text,joined,run

def extra_checks(check,witnesses,body,text,joined,run,path,policy,source,engine,generate,mapping):
    for name,bad in {
        'text_missing_end':text.replace('end_program;',''),
        'text_extra_after_end':text+'output other fraction;\n',
        'text_include_forbidden':text.replace('end_program;','include secret;\nend_program;'),
        'text_duplicate_input':text.replace('end_program;',next(x for x in text.splitlines() if x.startswith('input '))+'\nend_program;'),
        'text_duplicate_output':text.replace('end_program;','output fraction half;\nend_program;'),
        'text_missing_semicolon':text.replace(';','',1),
        'text_unknown_profile':text.replace(PROFILE,'Other/1',1)}.items():
        try: lower(bad); rejected=False
        except Exception: rejected=True
        check(name,rejected)
    quoted=deepcopy(body); quoted['name']='北星; '+chr(34)+'quote'+chr(34)+' # '+chr(39)
    check('unicode_and_quotes_text_roundtrip',digest(lower(render(quoted)))==digest(quoted))
    check('blank_lines_roundtrip',digest(lower('\n'+text+'\n'))==digest(body))
    try:
        from authoring import decode_type
        decode_type('{"kind":"number","kind":"boolean"}')
        rejected=False
    except ValueError: rejected=True
    check('duplicate_json_type_key_refused',rejected)
    changed=deepcopy(body); changed['inputs']['ordinary']['value']=False
    stress=materialize(changed,path,policy,mapping,generate)
    check('conditional_policy_fraction',stress['policy']['fraction']=='4/5')
    stress_run=engine.wire(engine.execute(stress['materialization']['path'],source))
    index=policy['year_index']; years=[path['initial_year']]+path['continuations']
    invoice=sum((Fraction(o['payload']['units'])*Fraction(o['payload']['unit_price']) for o in years[index]['operations'] if o['id'] in policy['delivery_operations']),Fraction(0))
    cash_delta=invoice*(Fraction(4,5)-Fraction(9,10))
    original_lines=run['years'][index]['report']['lines']; stress_lines=stress_run['years'][index]['report']['lines']
    check('independent_changed_cash',Fraction(stress_lines['cash']['value'])-Fraction(original_lines['cash']['value'])==cash_delta)
    check('independent_changed_receivables',Fraction(stress_lines['receivables']['value'])-Fraction(original_lines['receivables']['value'])==-cash_delta)
    check('changed_collections_profit_unchanged',stress_lines['profit']==original_lines['profit'])
    unresolved=deepcopy(body); unresolved['inputs']['ordinary']['value']='unknown'
    u=materialize(unresolved,path,policy,mapping,generate)
    check('unknown_guard_blocks_policy_materialization',u['status']=='unresolved' and 'materialization' not in u)
    unresolved=deepcopy(body); unresolved['inputs']['discount']['value']='unknown'
    check('unknown_fraction_blocks_policy',materialize(unresolved,path,policy,mapping,generate)['status']=='unresolved')
    wrongtype=deepcopy(body); wrongtype['outputs']['fraction']='ordinary'
    check('Boolean_cannot_be_policy_fraction',materialize(wrongtype,path,policy,mapping,generate)['status']=='invalid')
    badmap=deepcopy(mapping); badmap['fraction']='missing'
    check('missing_mapping_output_refused',materialize(body,path,policy,badmap,generate)['status']=='invalid')
    badmap=deepcopy(mapping); badmap['installment_shares']=['first_share']
    check('wrong_installment_count_refused',materialize(body,path,policy,badmap,generate)['status']=='invalid')
    negative=deepcopy(body); negative['inputs']['discount']['value']='2/1'
    check('negative_fraction_domain_refused',materialize(negative,path,policy,mapping,generate)['status']=='invalid')
    shares=deepcopy(body); next(n for n in shares['nodes'] if n['id']=='two')['value']='3/1'
    check('shares_not_summing_to_one_refused',materialize(shares,path,policy,mapping,generate)['status']=='invalid')
    extra=deepcopy(body); extra['outputs']['unused']='one'
    check('unmapped_output_refused',materialize(extra,path,policy,mapping,generate)['status']=='invalid')
    foreign=deepcopy(body); foreign['nodes'].append(literal('money','9/10',{'kind':'number','dimensions':{'USD':1},'context':'Northstar'})); foreign['outputs']['fraction']='money'
    check('money_cannot_be_policy_fraction',materialize(foreign,path,policy,mapping,generate)['status']=='invalid')
    check('stress_keeps_admission_false',all(stress[k] is False for k in FLAGS))
    witnesses.update(stress=stress,stress_result=stress_run,independent_cash_delta=str(cash_delta),unresolved_policy=u)
    return {'witnesses':witnesses}

def main():
    flags=set(sys.argv[1:]); assert flags <= {'--record','--smoke'} and len(flags)<=1
    record='--record' in flags; smoke='--smoke' in flags
    assert not record or not (HERE/'manifest.json').exists(),'one-time recording already exists'
    baseline=json.loads((HERE/'baseline.json').read_text()) if (HERE/'baseline.json').exists() else protected()
    for name,h in baseline.items(): assert sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    start=time.perf_counter(); started=datetime.now(timezone.utc).isoformat()
    evidence,body,text,joined,run=conformance(smoke)
    failed=[x['name'] for x in evidence['checks'] if not x['passed']]
    for name,h in baseline.items(): assert sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    if failed:
        dest=HERE/('failure-'+datetime.now(timezone.utc).strftime('%H%M%S')); dest.mkdir()
        for p in HERE.glob('*.py'): (dest/p.name).write_bytes(p.read_bytes())
        (dest/'failure.json').write_text(json.dumps(evidence,indent=2)+'\n')
    if record and not failed:
        for name,value in {'checks.json':evidence,'fixture.json':body,'schema.json':schema(),'materialization.json':joined,'accounting-result.json':run,'baseline.json':baseline}.items():
            (HERE/name).write_text(json.dumps(value,indent=2)+'\n')
        (HERE/'example.accdsl').write_text(text)
        manifest={'started_utc':started,'wall_seconds':time.perf_counter()-start,'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 python3 '+REL+'/verify.py --record','environment':'Python '+platform.python_version()+'; jsonschema; exact fractions; protected local engine','cpu_gpu':'CPU only; GPU intentionally hidden by CUDA_VISIBLE_DEVICES='+str(os.environ.get('CUDA_VISIBLE_DEVICES')),'random_seeds':'N/A: deterministic','data_version':baseline,'plan':'docs/plans/accounting-company-expressions-20261023.md','result':REL+'/result.md','files':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file()}}
        (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    elif not smoke and not failed and (HERE/'manifest.json').exists():
        for name,value in [('checks.json',evidence),('fixture.json',body),('schema.json',schema()),('materialization.json',joined),('accounting-result.json',run)]:
            assert digest(json.loads((HERE/name).read_text()))==digest(value),name
        assert (HERE/'example.accdsl').read_text()==text
        for name,h in json.loads((HERE/'manifest.json').read_text())['files'].items(): assert sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    print(json.dumps({'checks':len(evidence['checks']),'passed':not failed,'failed':failed,'protected_files':len(baseline),'recorded':record and not failed,'smoke':smoke,'wall_seconds':round(time.perf_counter()-start,3)}))
    return bool(failed)
if __name__=='__main__': raise SystemExit(main())
