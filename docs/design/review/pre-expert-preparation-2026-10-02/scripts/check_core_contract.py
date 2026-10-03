#!/usr/bin/env python3
"""Bounded structural/semantic design oracles, with explicit coverage limits."""
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import unicodedata
import jsonschema
from lark import Lark, UnexpectedInput

ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs/design';checks=[]
def ck(name,ok,detail):
    checks.append(dict(name=name,passed=bool(ok),detail=detail))
    if not ok:raise AssertionError(name)
def canonical(value):
    def normal(x):
        if isinstance(x,float):raise ValueError('FloatForbidden')
        if isinstance(x,str):return unicodedata.normalize('NFC',x)
        if isinstance(x,list):return [normal(i) for i in x]
        if isinstance(x,dict):return {k:normal(v) for k,v in sorted(x.items())}
        return x
    return json.dumps(normal(value),sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(domain,value):return hashlib.sha256(domain.encode()+b'\0'+canonical(value)).hexdigest()
def uniform(seed,group,entity,contract,date,kind,index):
    key=['stream-v1',seed,group,entity,contract,date,kind,index]
    v=int.from_bytes(hashlib.sha256(canonical(key)).digest()[:8],'big')
    return Q(2*v+1,2**65)
def main():
    source=(D/'fixtures/borrowing.acc').read_text();grammar=(D/'spec/core-0.lark').read_text()
    parser=Lark(grammar,parser='lalr',maybe_placeholders=False)
    a=parser.parse(source);b=parser.parse('// comment\n'+source.replace(';',';\n'))
    ck('grammar_format_invariance',a==b,'Same syntax tree after comments/whitespace')
    ck('declaration_closure',len(list(a.find_data('opening')))==1 and len(list(a.find_data('account')))==4,'Complete source has opening state and retained earnings account')
    try:parser.parse(source+'let bad = 1 + ;');raise AssertionError('Expected parse failure')
    except UnexpectedInput:ck('malformed_expression_rejected',True,'Incomplete binary expression rejected')
    package=json.loads((D/'fixtures/demo-debt-package.json').read_text())
    ck('opening_dependency_resolved',sum(Q(x) for x in package['registry']['after-2025-close']['signed_balances'].values())==0,'Cash 95, credit debt 100, debit retained loss 5')
    schema=json.loads((D/'spec/core-ir.schema.json').read_text());jsonschema.Draft202012Validator.check_schema(schema)
    fixture=json.loads((D/'fixtures/core-ir-structure.json').read_text());jsonschema.validate(fixture,schema)
    ck('closed_schema_fixture',True,'Structural validation only; full semantic compiler unimplemented')
    demo=json.loads((D/'fixtures/core-ir-demo.json').read_text());jsonschema.validate(demo,schema)
    ck('full_demo_ir_schema',True,'Author-entered expected lowering with source, context, review, state, contracts, alternatives, scenario and reporting package')
    expressions={e['id']:e for e in demo['expressions']};observations={o['id']:o for o in demo['observations']}
    def eval_expr(id,alpha):
        e=expressions[id]
        if e['op']=='literal':
            return Q(int(e['rational']['n']),int(e['rational']['d'])) if e['rational'] else e['text']
        if e['op']=='ref':return alpha if e['target']=='alpha' else observations[e['target']]
        if e['op']=='call':
            v=eval_expr(e['args'][0],alpha)
            if e['target']=='builtin:constant@1':return v
            if e['target']=='builtin:value@1':
                q=v['domain']['lower'];return Q(int(q['n']),int(q['d']))
        if e['op']=='eq':return eval_expr(e['args'][0],alpha)==eval_expr(e['args'][1],alpha)
        raise ValueError('UnsupportedReferenceExpression')
    fields={f['name']:f['expression'] for f in demo['contracts'][0]['fields']}
    for name,alpha,condition in [('allFixed',Q(1),'is.fixed'),('allFloating',Q(0),'is.floating')]:
        principal=eval_expr(fields['principal'],alpha);fixed=eval_expr(fields['fixed_rate'],alpha)
        floating=eval_expr(demo['scenarios'][0]['drivers'][0]['expression'],alpha)
        interest=principal*(alpha*fixed+(1-alpha)*floating)
        opening={x['account']:Q(int(x['signed_amount']['n']),int(x['signed_amount']['d'])) for x in demo['states'][0]['balances']}
        expected=package['expected'][name]
        ck('demo_ir_to_result_'+name,eval_expr(condition,alpha) and interest==Q(expected['interest']) and opening['Cash']-interest==Q(expected['cash']) and -opening['Retained']-interest==Q(expected['equity']),
           'Reference evaluator consumes authored IR; general source-to-IR compiler still pending')
    bad=deepcopy(fixture);bad['expressions'][0]['hidden_assumption']=True
    try:jsonschema.validate(bad,schema);raise AssertionError('Expected unknown field error')
    except jsonschema.ValidationError:ck('unknown_ir_field_rejected',True,'Closed record detects undeclared data')
    # A literal parsed from the real source agrees with a typed-library value.
    obs=list(a.find_data('observation'))[0];number=list(obs.find_data('number'))[0]
    parsed=Q(str(number.children[0]));typed=Q(100)
    ck('literal_frontend_equivalence',parsed==typed and fixture['expressions'][0]['rational']==dict(n=str(typed.numerator),d=str(typed.denominator)),'Limited literal lowering, not whole-program compiler conformance')
    x={'model':'M','amount':{'n':'5','d':'1'},'label':'caf\u00e9'}
    y={'label':'cafe\u0301','amount':{'d':'1','n':'5'},'model':'M'}
    ck('canonical_key_unicode',digest('model-v1',x)==digest('model-v1',y),'Dictionary order and Unicode composition do not change semantic digest')
    changed=deepcopy(x);changed['amount']['n']='7'
    ck('changed_model_identity',digest('model-v1',x)!=digest('model-v1',changed),'Rate/value change creates a different model')
    ck('identity_domains_separate',digest('evidence-v1',x)!=digest('model-v1',x),'Evidence and model hashes are not interchangeable')
    try:canonical({'amount':0.1});raise AssertionError('Expected float rejection')
    except ValueError:ck('canonical_float_rejected',True,'No accidental binary float identity')
    branches=['fixed','floating'];draws={b:uniform('seed1','shared','Acme','debt1','2026-01-01','rate',0) for b in branches}
    reversed_draws={b:uniform('seed1','shared','Acme','debt1','2026-01-01','rate',0) for b in reversed(branches)}
    ck('stable_branch_streams',draws==reversed_draws and draws['fixed']==draws['floating'],'Ordering absent; common coupling explicit')
    ck('measurement_outer_stream_separation',uniform('seed1','shared','Acme','loan1','2026-01-01','inner-default',0)!=uniform('seed1','shared','Acme','loan1','2026-01-01','outer-default',0),'No reuse of realised outer default in allowance draw')
    ck('uniform_open_interval',all(0<u<1 for u in draws.values()),'Reference primitive produces neither endpoint')
    # Dependency closure after a review correction.
    graph={'reading':['mapping'],'mapping':['constraint'],'constraint':['family'],'family':['run'],'run':['report'],'unrelated':[]}
    pending=['reading'];affected=set()
    while pending:
        k=pending.pop()
        for child in graph.get(k,[]):
            if child not in affected:affected.add(child);pending.append(child)
    ck('review_invalidation',affected=={'mapping','constraint','family','run','report'},'Transitive descendants stale; unrelated state reusable')
    # Information capability uses role/date rather than exposing the entire path.
    records=[dict(id='current-pd',date='2026-01-01',kind='forecast'),dict(id='future-default',date='2026-06-01',kind='realised')]
    visible=[r['id'] for r in records if r['date']<='2026-01-01']
    ck('no_future_realisation',visible==['current-pd'],'Measurement can use current PD, not future realised default')
    partitions={'geography':{'domestic':Q(180),'overseas':Q(80)},'channel':{'wholesale':Q(200),'retail':Q(60)}}
    ck('overlapping_axes',all(sum(v.values())==260 for v in partitions.values()) and sum(sum(v.values()) for v in partitions.values())==520,'Adding both axes double-counts the same population; require one partition')
    # Genuine joint counterexample: extrema of cash/equity cannot be selected independently.
    import z3
    alpha=z3.Real('alpha_joint');s=z3.Solver();s.add(alpha>=0,alpha<=1,z3.RealVal('93.6')+z3.RealVal('1.6')*alpha==z3.RealVal('93.6'),z3.RealVal('146.6')+z3.RealVal('1.6')*alpha==z3.RealVal('148.2'))
    ck('incompatible_marginal_extrema',s.check()==z3.unsat,'Lowest cash and highest equity do not describe one history')
    apple=json.loads((D/'cases/apple/manifest.json').read_text())
    ck('real_source_note_inventory',len([n for n in apple['notes'] if n['source']=='annual'])==13 and len([n for n in apple['notes'] if n['source']=='interim'])==10,'Note headings reconciled to annual/interim indices')
    for row in apple['statements']:
        ck('apple_balance_'+row['date'],Q(row['assets'])==Q(row['liabilities'])+Q(row['equity']),row['source'])
    d=apple['debt_measurements'];ck('apple_debt_measurements',Q(d['principal'])+Q(d['discount_cost_adjustment'])+Q(d['hedge_carrying_adjustment'])==Q(d['carrying']),'Note 9 principal differs from carrying and fair value')
    scenario=apple['marginal_stress'];i=Q(scenario['exposure_assumption'])*Q(scenario['rate_increment'])*Q(scenario['year_fraction']);last=apple['statements'][-1];expected=scenario['expected']
    ck('apple_marginal_forecast',i==Q(expected['interest']) and Q(last['cash'])-i==Q(expected['cash']) and Q(last['assets'])-i==Q(expected['assets']) and Q(last['equity'])-i==Q(expected['equity']),'Conditional extra interest 72.875 million, not estimated actual sensitivity')
    ck('external_reference_limit_visible',any(x['status'].startswith('not_acquired') for x in apple['cross_reference_obligations']),'Proxy/reference closure is not called complete')
    L=Q(5)/Q('1.1')+Q(105)/Q('1.21');L1=L*Q('1.1')-5;L2=L1*Q('1.1')-5
    ck('compound_bond',L==Q(11050,121) and L1==Q(1050,11) and L2==100 and (100-L)+L==100,'Separate issue components and amortisation before redemption/conversion')
    f1=(Q(150)+180)/(100+120);f2=Q(180)/150;reserve=180*f2-180+140*f1*f2-140
    ck('chain_ladder_point',f1==Q('1.5') and f2==Q('1.2') and reserve==148,'Point projection only; terminal variance not identified by one paired observation')
    decisions=json.loads((D/'research/forward-screening-decisions.json').read_text())['records'];ids={r['id'] for r in decisions}
    forward=json.loads((D/'research/forward-snowball.json').read_text())['records']
    ck('screening_traceability',all(c['id'] in ids and c.get('decision_source') for r in forward for c in r.get('candidates',[])),'Every retrieved candidate has an individual decision; metadata screening distinct from full-text support')
    out=D/'review/core-contract-checks.json';out.write_text(json.dumps(dict(status='passed',checks=checks,count=len(checks),scope='Reference grammar, selected schema/literal semantics, identities, information/dependency/financial counterexamples; no full compiler or adapter integration',command='python3 scripts/check_core_contract.py',sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [D/'spec/core-0.lark',D/'spec/core-ir.schema.json',D/'spec/core-contract.md']}),indent=2)+'\n')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out.relative_to(ROOT)))))

if __name__=='__main__':main()
