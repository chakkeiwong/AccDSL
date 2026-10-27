"""Retained allocation equations under explicitly retained finite-method premises."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(HERE.parent/'company-return-schema-20261023'))
import method_requirements_v1 as v1
import method_requirements_v2 as v2
import retained_fixture
import return_schema


def ref(key):
    return {'op':'ref','id':key}


def binary(op,a,b):
    return {'op':op,'left':a,'right':b}


def authored(body):
    # These contexts are a proposed interpretation of this synthetic method,
    # not a general migration of arbitrary v1 context strings.
    raw=v1.canonical(body)
    h=sha256(raw).hexdigest()
    context={'entity':body['context']['entity'],'book_role':body['context']['book_role'],
             'component':body['component']['id'],'period_start':body['period']['start'],
             'period_end_exclusive':body['period']['end_exclusive'],'basis':'retained_conditional_return'}
    currency='currency:'+body['context']['currency']
    dims={'amount':{currency:1},'units':{'goods:return_unit':1},
          'price':{currency:1,'goods:return_unit':-1},'rate':{}}
    fields={
        'expected':('/component/expected_units','units','assumption'),
        'refund_per_unit':('/component/unit_refund','price','state'),
        'cost_per_unit':('/component/unit_cost','price','state'),
        'handling_estimate':('/component/estimated_handling','price','assumption'),
        'deterioration_estimate':('/component/estimated_deterioration','price','assumption'),
        'refund':('/component/refund','amount','state'),
        'recovery':('/component/recovery','amount','state'),
        'rate':('/tax/rate','rate','assumption'),
        'dta':('/tax/opening_dta','amount','state'),
        'dtl':('/tax/opening_dtl','amount','state'),
        'actual':('/events/0/actual_units','units','state'),
        'actual_handling':('/events/0/unit_handling','price','state'),
        'refund_cash':('/events/0/refund_cash','amount','state'),
        'handling_cash':('/events/0/handling_cash','amount','state')}
    inputs,values={},{}
    for key,(pointer,kind,role) in fields.items():
        value=body
        for token in pointer[1:].split('/'):
            value=value[int(token)] if type(value) is list else value[token]
        inputs[key]={'type':{'kind':'rational','context':deepcopy(context),
                            'dimensions':deepcopy(dims[kind]),'scale':'1/1'},
                     'role':role,'source_ref':'sha256:'+h+'#'+pointer}
        values[key]=({'status':'unknown','reason':'retained_explicit_unknown'} if value=='unknown'
                     else {'status':'known','value':value})
    mul=lambda a,b:binary('mul',a,b)
    net=binary('sub',binary('sub',ref('cost_per_unit'),ref('handling_estimate')),ref('deterioration_estimate'))
    equations=[('refund_allocation',ref('refund'),mul(ref('expected'),ref('refund_per_unit')),
                ['refund','expected','refund_per_unit']),
               ('recovery_allocation',ref('recovery'),mul(ref('expected'),net),
                ['recovery','expected','cost_per_unit','handling_estimate','deterioration_estimate']),
               ('opening_dta',ref('dta'),mul(ref('refund'),ref('rate')),['dta','refund','rate']),
               ('opening_dtl',ref('dtl'),mul(ref('recovery'),ref('rate')),['dtl','recovery','rate']),
               ('refund_cash',ref('refund_cash'),mul(ref('actual'),ref('refund_per_unit')),
                ['refund_cash','actual','refund_per_unit']),
               ('handling_cash',ref('handling_cash'),mul(ref('actual'),ref('actual_handling')),
                ['handling_cash','actual','actual_handling'])]
    manifest={'profile':v2.PROFILE,'method_id':'retained.return.allocation_equations','version':'2',
        'inputs':inputs,'requirements':[{'id':key,'predicate':binary('eq',a,b),'requires':sorted(deps),
            'admission_refs':['retained-unsettled-zero-tax-base-premises'],
            'on_false':'invalid','on_unknown':'unresolved'} for key,a,b,deps in equations],
        'capabilities':['dimensional-return-equations'],
        'residual_prerequisites':[
            'Opening is unsettled, tax bases zero, and recovery estimate nonnegative under retained premises.',
            'Scope findings, collection/chronology, source authority and complete method are not evaluated.',
            'Dimension/context assignments are explicit caller declarations for this synthetic case.']}
    return manifest,values


def comparisons():
    body,raw=retained_fixture.fixture()
    assert body['component']['settled'] is False
    assert body['tax']['refund_tax_base']==body['tax']['recovery_tax_base']=='0/1'
    cases=[('baseline',None,None,'requirements_satisfied')]
    for name,path in [('refund',('component','refund')),('recovery',('component','recovery')),
                      ('dta',('tax','opening_dta')),('dtl',('tax','opening_dtl')),
                      ('refund_cash',('events',0,'refund_cash')),('handling_cash',('events',0,'handling_cash'))]:
        cases.extend([(name+'.wrong',path,'999/1','invalid'),(name+'.unknown',path,'unknown','unresolved')])
    records=[]
    for name,path,value,expected in cases:
        current=deepcopy(body)
        if path:
            target=current
            for key in path[:-1]:
                target=target[key]
            target[path[-1]]=value
        manifest,values=authored(current)
        key=v1.digest(manifest)
        result=v2.assess({key:manifest},key,values,manifest['capabilities'])
        old=return_schema.assess(current)
        mapped='requirements_satisfied' if old['status']=='statically_eligible' else old['status']
        records.append({'case':name,'expected':expected,'legacy_status':old['status'],
            'passed':result['status']==mapped==expected,'manifest':manifest,'values':values,'result':result})
    return records,sha256(raw).hexdigest()
