"""Read-only missing-input inspection for one pinned SectorCompany/1 owner."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
NATIVE=ROOT/'data/accounting-master/sector-company-composition-20261016'
NATIVE_SHA256='4ca4f3fa0a4471526785d8b6f8c5a1e3e6d0044a13d58a0a9d091b2d4ed6b454'
LOCK_SHA256='38281d80d8d88a6416f00fa7047b62f47bc4cfe30b85b1abe09d622df4238b49'
FIELDS=('id','beneficiary','opening_unamortized','income_releases','ecl')
SUPPORT=('guarantee_ifrs9_scope','guarantee_ecl_supported',
         'guarantee_service_release_supported','opening_guarantee_measurement_supported',
         'guarantee_tax_deductible_as_booked')

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def digest(value):return sha256(canonical(value)).hexdigest()

def inspect(request,expected_digest,reader=None):
    if digest(request)!=expected_digest:raise ValueError('request identity mismatch')
    if sha256((NATIVE/'reference.py').read_bytes()).hexdigest()!=NATIVE_SHA256:
        raise ValueError('native implementation identity mismatch')
    raw_lock=(NATIVE/'input-lock.json').read_bytes()
    if sha256(raw_lock).hexdigest()!=LOCK_SHA256:raise ValueError('native source-lock identity mismatch')
    read=reader or (lambda p:(ROOT/p).read_bytes())
    spec=importlib.util.spec_from_file_location('guarantee_input_inspection_native',NATIVE/'reference.py')
    native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
    result=native.calculate(deepcopy(request),read)
    answer=dict(profile='CompanyGuaranteeInputInspection/1',request_sha256=expected_digest,
        input=deepcopy(request),native_result=result,native_implementation_sha256=NATIVE_SHA256,
        source_lock_sha256=LOCK_SHA256,inspection_status='not_inspected',obligations=[],
        posts=False,mutations=[],source_admission=False,actor_information_admission=False,
        population_complete=False,history_family_constructed=False)
    # The native source check precedes request shape; never inspect through a refusal.
    if result['reason'] in {'missing_protected_input','changed_protected_input'}:
        answer['reason']='native_source_refusal';return answer
    if not isinstance(request,dict):
        answer['reason']='native_request_refusal';return answer
    if request.get('wire')!='SectorCompany/1' or request.get('operation')!='report':
        answer['reason']='native_request_refusal';return answer
    obligations=[]
    def obligation(pointer,state):
        obligations.append(dict(pointer=pointer,state=state,action='supply supported input; do not substitute zero'))
    if 'guarantee' not in request:obligation('/guarantee','omitted')
    elif request['guarantee'] is None:obligation('/guarantee','explicit_null')
    elif isinstance(request['guarantee'],dict):
        g=request['guarantee']
        for field in FIELDS:
            pointer='/guarantee/'+field
            if field not in g:obligation(pointer,'omitted')
            elif g[field] is None:obligation(pointer,'explicit_null')
            elif field in {'income_releases','ecl'} and isinstance(g[field],list):
                for i,value in enumerate(g[field]):
                    if value is None:obligation(pointer+'/'+str(i),'explicit_null')
                # Exact native profile requires two intervals; retain absent positions.
                for i in range(len(g[field]),2):obligation(pointer+'/'+str(i),'omitted')
    findings=request.get('findings')
    if isinstance(findings,dict):
        for field in SUPPORT:
            if field not in findings:obligation('/findings/'+field,'omitted')
            elif findings[field] is None:obligation('/findings/'+field,'explicit_null')
    answer['obligations']=obligations
    answer['inspection_status']=('incomplete_guarantee_inputs' if obligations else
        'supplied_guarantee_inputs' if result['status']=='conditional_complete' else 'native_refusal')
    answer['reason']=('missing inputs retained without admission' if obligations else result['reason'])
    return answer
