"""Finite source-bound company schedule with explicit caller-owned capabilities."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import json,sys
from jsonschema import Draft202012Validator,FormatChecker
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
EXEC=HERE.parent/'company-return-execution-20261024'
sys.path.insert(0,str(EXEC))
from retained_execution_context import load,event_for,adapter_for,AUTHOR
from native_returns import initialize,propose,apply,Rejected,need,canon,digest,fmt
from native_reports import report,carry
PROFILE='RetainedCompanyProgramDraft/1'
FILES={'native-return':EXEC/'native_returns.py','native-tax':EXEC/'native_returns.py',
       'retained-corporate':EXEC/'retained_execution_context.py',
       'legal-annual':EXEC/'native_reports.py','annual-carry':EXEC/'native_reports.py'}

def closed(p):return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
def schema():
    name={'type':'string','minLength':1};sha={'type':'string','pattern':'^[0-9a-f]{64}$'}
    day={'type':'string','format':'date'};truth={'oneOf':[{'type':'boolean'},{'const':'unknown'}]}
    return {'$schema':'https://json-schema.org/draft/2020-12/schema',**closed({
        'profile':{'const':PROFILE},'name':name,
        'source':closed({'packet_sha256':sha,'opening_sha256':sha}),
        'context':closed({'entity':name,'book_role':{'const':'legal'},'currency':name,'case_id':name}),
        'period':closed({'start':day,'end_exclusive':day}),'return_module_sha256':sha,
        'capabilities':{'type':'array','minItems':1,'items':closed({'id':name,'implementation_sha256':sha})},
        'events':{'type':'array','minItems':1,'items':closed({'id':name,'source_pointer':name,'event_sha256':sha,
            'capability':name,'review_findings':{'type':'object','additionalProperties':truth}})},
        'report':closed({'capability':name,'method':{'const':'ReturnLegalAnnualReport/1'}}),
        'carry':closed({'capability':name,'next_end_exclusive':day})})}

def validate(body):
    Draft202012Validator(schema(),format_checker=FormatChecker()).validate(body)
    def strings(x):
        if type(x) is dict:
            for k,v in x.items():strings(k);strings(v)
        elif type(x) is list:
            for v in x:strings(v)
        elif type(x) is str:
            x.encode('utf-8',errors='strict')
            need(not any(ord(c)<32 or ord(c)==127 or c in '\x85\u2028\u2029' for c in x),'single-line scalar')
    strings(body)
    for key in ['capabilities','events']:
        ids=[r['id'] for r in body[key]];need(len(ids)==len(set(ids)),'duplicate '+key)
    known={r['id'] for r in body['capabilities']}
    need(all(e['capability'] in known for e in body['events']),'undeclared event capability')
    need(body['report']['capability'] in known and body['carry']['capability'] in known,'undeclared report/carry capability')
    need(body['period']['start']<body['period']['end_exclusive']<body['carry']['next_end_exclusive'],'nonconsecutive year bounds')
    return body

def fixture():
    author,packet,item,financial=load()
    manifest=json.loads((EXEC/'manifest.json').read_text())
    for group in ['inputs','implementation','outputs']:
        for name,h in manifest[group].items():need(sha256((ROOT/name).read_bytes()).hexdigest()==h,'protected execution bytes')
    capabilities=[{'id':k,'implementation_sha256':sha256(p.read_bytes()).hexdigest()} for k,p in FILES.items()]
    rows=[]
    for tr in packet['transitions']:
        key=tr['id'].removesuffix('.commit');original=item('event.'+key);event=event_for(key,original,author)
        cap={'settle':'native-return','sell':'native-return','tax':'native-tax','surrounding':'retained-corporate'}[event['kind']]
        pointer='/record_registry/'+packet['aliases']['event.'+key]['digest']+'/body'
        reviews={k:True for k,v in original['parameters'].items() if type(v) is bool}
        rows.append({'id':key,'source_pointer':pointer,'event_sha256':digest(original),'capability':cap,'review_findings':reviews})
    body={'profile':PROFILE,'name':'P complete retained legal year',
        'source':{k:author['source'][k] for k in ['packet_sha256','opening_sha256']},
        'context':deepcopy(author['context']),'period':deepcopy(author['period']),
        'return_module_sha256':digest(author),'capabilities':capabilities,'events':rows,
        'report':{'capability':'legal-annual','method':'ReturnLegalAnnualReport/1'},
        'carry':{'capability':'annual-carry','next_end_exclusive':'2027-01-01'}}
    return validate(body),author,packet,item,financial

def bind(body,expected):
    validate(body);comparison=deepcopy(body);comparison['name']=expected['name']
    need(len(body['events'])==len(expected['events']),'complete source schedule required')
    for i,(row,source) in enumerate(zip(body['events'],expected['events'])):
        need(set(row['review_findings'])==set(source['review_findings']),'review finding keys')
        comparison['events'][i]['review_findings']=source['review_findings']
    need(canon(comparison)==canon(expected),'source or capability binding mismatch')

def execute(body,available=None):
    """Availability is supplied by the local caller; body strings load no code."""
    try:
        expected,author,packet,item,financial=fixture();bind(body,expected)
    except Exception as exc:
        return {'status':'invalid','reason':type(exc).__name__+': '+str(exc).splitlines()[0][:220],'executed':False}
    available=set(FILES) if available is None else set(available)
    need(available<=set(FILES),'untrusted caller capability')
    native_open=initialize(author,item('opening')['books']['P'],item('opening')['compound']['prior_interest_expensed'])
    state=deepcopy(native_open);retained=item('opening');proposals=[]
    identity={'profile':PROFILE,'program_sha256':digest(body),'source':deepcopy(body['source']),
        'method_registry_sha256':digest(expected['capabilities']),'conditional':True,'source_admission':False,'durable_commit':False}
    def partial(status,reason,position):
        return {**identity,'status':'partial','stopped_status':status,'reason':reason,'stopped_index':position,
            'proposals':proposals,'state':state,'unexecuted':[r['id'] for r in body['events'][position:]],
            'complete_annual_opening':False}
    for i,row in enumerate(body['events']):
        try:
            need(row['capability'] in available,'capability unavailable:'+row['capability'],'unsupported')
            findings=row['review_findings']
            need(not any(v is False for v in findings.values()),'caller finding rejects method','unsupported')
            need(not any(v=='unknown' for v in findings.values()),'caller finding unresolved','unresolved')
            original=item('event.'+row['id']);event=event_for(row['id'],original,author)
            adapter=adapter_for(retained,financial) if row['capability']=='retained-corporate' else None
            p=propose(state,event,adapter);new=apply(state,event,p,adapter)
            next_retained,_,_=financial.derive(retained,original,lambda ok,why,*status:need(ok,why))
            need(new['balances']=={k:fmt(v) for k,v in next_retained['books']['P'].items()},'composed legal state diverged')
            state,retained=new,next_retained;proposals.append(p)
        except Rejected as exc:return partial(exc.status,exc.reason,i)
    annual=None
    try:
        need(body['report']['capability'] in available,'annual report capability unavailable','unsupported')
        annual=report(native_open,state)
        need(body['carry']['capability'] in available,'annual carry capability unavailable','unsupported')
        next_open=carry(native_open,state,body['carry']['next_end_exclusive'])
    except Rejected as exc:
        result=partial(exc.status,exc.reason,len(body['events']))
        if annual is not None:result['annual_report']=annual
        return result
    return {**identity,'status':'complete_conditional','proposals':proposals,'state':state,
        'annual_report':annual,'next_opening':next_open,'unexecuted':[],'complete_annual_opening':True}

def verify_result(body,result,available=None):
    return canon(execute(body,available))==canon(result)
