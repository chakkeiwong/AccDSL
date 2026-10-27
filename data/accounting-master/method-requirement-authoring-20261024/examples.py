"""Independently authored language cases, not new company or accounting evidence."""
from copy import deepcopy
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import method_requirements_v1 as core
import method_requirement_text_v1 as frontend


def simple(method, context, role, value, review):
    numeric = {'kind':'rational','context':context}
    definition = {'profile':core.PROFILE,'method_id':method,'version':'1',
        'inputs':{
            'amount':{'type':numeric,'role':role,'source_ref':'constructed-language-case:amount'},
            'review':{'type':{'kind':'boolean','context':{}},'role':'caller_finding',
                      'source_ref':'constructed-language-case:caller-finding'}},
        'requirements':[
            {'id':'nonnegative','predicate':{'op':'le',
                 'left':{'op':'const','type':deepcopy(numeric),'value':'0/1'},
                 'right':{'op':'ref','id':'amount'}},
             'requires':['amount'],'admission_refs':[],'on_false':'invalid','on_unknown':'unresolved'},
            {'id':'caller_scope','predicate':{'op':'ref','id':'review'},'requires':['review'],
             'admission_refs':['separate-review-required'],'on_false':'unsupported','on_unknown':'unresolved'}],
        'capabilities':[method],
        'residual_prerequisites':['Constructed grammar case only; no implemented accounting method.',
                                  'Legal state, authority, source admission and full method checks remain.']}
    return frontend.validate_exchange({'profile':frontend.EXCHANGE,'definition':definition,
        'selected_digest':core.digest(definition),'values':{'amount':value,'review':review},
        'available_capabilities':[method]})


def examples():
    prior = json.loads((HERE.parent/'method-requirements-20261024/examples.json').read_text())
    result = {key:{'profile':frontend.EXCHANGE,'definition':value['manifest'],
        'selected_digest':value['selected_digest'],'values':value['values'],
        'available_capabilities':value['manifest']['capabilities']} for key,value in prior.items()}
    known = lambda value:{'status':'known','value':value}
    unknown = lambda reason:{'status':'unknown','reason':reason}
    result['legal_cash'] = simple('example.legal_cash',
        {'entity':'SampleCo','book_role':'legal','unit':'USD','at':'2025-01-01'},
        'state',known('100/1'),known(True))
    result['reported_cash'] = simple('example.reported_cash',
        {'entity':'SampleGroup','book_role':'consolidated','unit':'USD millions','at':'2025-01-01'},
        'reported_measurement',known('100/1'),unknown('legal allocation not supplied'))
    result['insurance_cohort'] = simple('example.cohort',
        {'entity':'SampleInsurer','cohort':'C2025','unit':'coverage_units','at':'2025-01-01'},
        'assumption',unknown('cohort quantity not supplied'),unknown('scope review pending'))
    return result
