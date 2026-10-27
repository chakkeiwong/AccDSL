"""Provisional prospective due-date terms with immutable assessment bases."""
from copy import deepcopy
from datetime import timedelta
from hashlib import sha256
from pathlib import Path
import declared_receivable_lifecycle_v1 as life

core=life.core;engine=life.engine;transition=life.transition;types=transition.types
PROFILE='ReceivableTermHistory/1';MIGRATION='ReceivableTermMigration/1';STEP='ReceivableTermEvent/1';CARRY='ReceivableTermCarry/1'
FLAGS={**life.FLAGS,'contractual_admission':False,'term_history_complete':False}
PINS={'declared_receivable_lifecycle_v1.py': 'd16b7b53f1509aaecc3ad682b23b2e16e694a20b4412f6e0f692d524a9468672', 'company_book_transition_v2.py': '286685e10e88abc6569b4f2f834a2aaf7fc2adb754a813971921bf7544c12ae4', 'company_book_carry_v1.py': '72a1b3d45b24742267b120b04ee0ba97e479b75b08710a66b014d32d88b70c5c'}
TEXT=life.TEXT;DATE=life.DATE

def protected():
    for name,h in PINS.items():core.need(sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==h,'term_dependency:'+name)
    life.protected()
def closed(value,keys,label):core.closed(value,keys,label)
def text(value,label):engine.text(value,label)
def bounded(value):engine.binding.bounded(value);engine.memory.bounded(value)
def invalid(exc):return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350] or type(exc).__name__}
def record(fields):return life.record({k:life.scalar(v) for k,v in fields.items()})
def term_type():return record({'due':DATE,'effective':DATE,'event_id':TEXT,'predecessor':TEXT,'premise':TEXT})
def assessment_type(book):
    money=engine.money_type(book)
    return record({'term_id':TEXT,'as_of':DATE,'remaining':money,'overdue':money,'origin':TEXT,'event_id':TEXT})
def claim_type(book):
    fields=deepcopy(life.claim_type(book)['fields'])
    fields.update(current_term=life.scalar(TEXT),latest_assessment=life.scalar(TEXT),
                  terms={'node':'map','max_items':32,'values':term_type()},
                  assessments={'node':'map','max_items':64,'values':assessment_type(book)})
    return life.record(fields)
def configure(book,definition,schemas):
    derived=types.derive(definition,book['memory'],book)
    core.need(derived['status']=='typed','term_memory:'+derived.get('reason','invalid'))
    book.update(memory_schema=derived['schema_sha256'],memory_types=derived['memory_types'])
    schemas[derived['schema_sha256']]=derived['schema']

def validate(state):
    protected();bounded(state)
    closed(state,['profile','book','memory_definition','schemas','roles','unit_cost_pointer','migration'],'term_state')
    core.need(state['profile']==PROFILE,'term_state_profile');book=state['book']
    transition.typed_book(book,state['memory_definition'],state['schemas'])
    fields=state['memory_definition']['root']['fields']
    core.need(fields['claims']['node']=='map' and fields['claims']['values']==claim_type(book),'term_claim_type')
    core.need(fields['collection_clock']==life.record({'cursor':life.scalar(DATE)}),'term_clock_type')
    life.operating.build(book,state['schemas'],state['roles'],state['unit_cost_pointer'])
    migration=state['migration'];closed(migration,['source_book_sha256','premise','scope'],'term_migration')
    engine.binding.hash_string(migration['source_book_sha256']);text(migration['premise'],'migration_premise')
    core.need(migration['scope']=='Imported last assessment and initial terms under supplied no-prior-amendment premise','migration_scope')
    cursor=book['memory']['collection_clock']['cursor'];core.scalar(cursor,'date')
    core.need(cursor<=book['period']['end_exclusive'],'term_cursor_period')
    claims=book['memory']['claims'];total=life.reports.total(life.reports.number(r['remaining']) for r in claims.values())
    core.need(total==life.reports.number(book['balances'][state['roles']['receivables']]),'claim_receivable_sum')
    for identity,row in claims.items():
        text(identity,'claim_id');core.need(row['sale_event'] in book['seen'],'claim_sale_event')
        core.need(row['issued']<=book['date'] and life.reports.number(row['remaining'])>=0,'claim_state')
        terms=row['terms'];core.need(bool(terms) and row['current_term'] in terms,'current_term')
        ordered=sorted(terms,key=lambda k:terms[k]['effective']);previous='none';last=None
        for key in ordered:
            term=terms[key];text(key,'term_id');text(term['premise'],'term_premise')
            core.need(term['predecessor']==previous,'term_chain')
            core.need(row['issued']<=term['effective']<=book['date'] and term['effective']<=term['due'],'term_dates')
            core.need(last is None or last<term['effective'],'ambiguous_term_effective_date')
            core.need(term['event_id'] in book['seen'],'term_event_missing')
            previous=key;last=term['effective']
        core.need(row['current_term']==ordered[-1] and row['due']==terms[ordered[-1]]['due'],'current_due_binding')
        assessments=row['assessments'];dates=set()
        for key,assessment in assessments.items():
            text(key,'assessment_id');at=assessment['as_of'];core.need(at not in dates,'duplicate_assessment_date');dates.add(at)
            core.need(row['issued']<=at<=book['date'] and at<cursor,'assessment_time')
            applicable=[k for k in ordered if terms[k]['effective']<=at]
            core.need(bool(applicable) and assessment['term_id']==applicable[-1],'assessment_term_basis')
            term=terms[assessment['term_id']];amount=life.reports.number(assessment['remaining'])
            core.need(amount>=0 and assessment['overdue']==(assessment['remaining'] if at>term['due'] else '0/1'),'historical_overdue')
            if assessment['origin']=='imported_snapshot':core.need(assessment['event_id']=='unknown','imported_assessment_event')
            else:core.need(assessment['origin']=='recorded_event' and assessment['event_id'] in book['seen'],'assessment_event_missing')
        core.need(row['assessed']==bool(assessments),'assessed_flag')
        if assessments:
            latest=max(assessments,key=lambda k:assessments[k]['as_of']);core.need(row['latest_assessment']==latest,'latest_assessment')
            a=assessments[latest]
            core.need((row['assessment_date'],row['assessed_remaining'],row['overdue'])==(a['as_of'],a['remaining'],a['overdue']),'assessment_summary')
        else:core.need(row['latest_assessment']=='none' and row['assessed_remaining']==row['overdue']=='0/1','unassessed_summary')
    return book

def migrate(request):
    try:
        protected();bounded(request)
        closed(request,['profile','book','expected_book_sha256','memory_definition','schemas','roles','unit_cost_pointer','premise'],'term_migration_request')
        core.need(request['profile']==MIGRATION,'migration_profile');book=request['book'];text(request['premise'],'migration_premise')
        core.need(request['expected_book_sha256']==core.digest(book),'stale_migration_book')
        transition.typed_book(book,request['memory_definition'],request['schemas']);life.control(book,request['roles'])
        fields=request['memory_definition']['root']['fields']
        core.need(fields['claims']['values']==life.claim_type(book),'legacy_claim_type')
        after=deepcopy(book);definition=deepcopy(request['memory_definition']);schemas=deepcopy(request['schemas'])
        definition['root']['fields']['claims']['values']=claim_type(book)
        for identity,row in after['memory']['claims'].items():
            row.update(current_term='initial',latest_assessment='imported' if row['assessed'] else 'none',
                terms={'initial':{'due':row['due'],'effective':row['issued'],'event_id':row['sale_event'],
                    'predecessor':'none','premise':request['premise']}},assessments={})
            if row['assessed']:row['assessments']['imported']={'term_id':'initial','as_of':row['assessment_date'],
                'remaining':row['assessed_remaining'],'overdue':row['overdue'],'origin':'imported_snapshot','event_id':'unknown'}
        configure(after,definition,schemas)
        state={'profile':PROFILE,'book':after,'memory_definition':definition,'schemas':schemas,'roles':deepcopy(request['roles']),
            'unit_cost_pointer':request['unit_cost_pointer'],'migration':{'source_book_sha256':core.digest(book),'premise':request['premise'],
                'scope':'Imported last assessment and initial terms under supplied no-prior-amendment premise'}}
        validate(state)
        return {'profile':MIGRATION,**FLAGS,'status':'migrated_provisional','request_sha256':core.digest(request),'state':state,
                'source_book':deepcopy(book),'state_sha256':core.digest(state),'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
    except Exception as exc:return invalid(exc)

def literal(value):
    return {'kind':'object','fields':{k:literal(v) for k,v in value.items()}} if type(value) is dict else life.literal(value)
def state_request(state,event,operations):
    book=state['book'];identity='synthetic.receivable.term-history';money=engine.money_type(book)
    pre=life.operating.conditions(identity,{'approved':core.BOOL},[('approved',life.operating.ref('approved'),['approved'],'unsupported')])
    final=operations[-1];core.need(final['op']=='replace' and final['value']['kind']=='literal','term_postcondition_target')
    post=life.operating.conditions(identity,{'written_date':DATE},[('date_written',
        life.operating.binary('eq',life.operating.ref('written_date'),life.operating.constant(DATE,final['value']['value'])),['written_date'],'invalid')])
    for manifest in [pre,post]:manifest['residual_prerequisites']=['Supplied synthetic term premise; no modification accounting admission']
    empty={'type':'object','properties':{},'required':[],'additionalProperties':False};h=core.digest(empty);schemas=deepcopy(state['schemas']);schemas[h]=empty
    method={'profile':engine.METHOD,'id':identity,'version':'1','context':deepcopy(book['context']),
        'account_map':{k:state['roles'][k] for k in ['cash','receivables']},
        'preconditions':{'manifest':pre,'bindings':{'approved':life.operating.event('approved')}},
        'postconditions':{'manifest':post,'bindings':{'written_date':{'kind':'memory','pointer':types.pointer(final['path'])}}},
        'monetary':{'definition':{'profile':engine.monetary.PROFILE,'method_id':identity,'version':'1','inputs':{},'calculations':[],
            'accounts':{k:deepcopy(money) for k in ['cash','receivables']},'cash_account':'cash','postings':[],'flows':[]},'bindings':{}},
        'memory':{'definition':{'profile':engine.memory.PROFILE,'state_schema':book['memory_schema'],'input_schema':h,'operations':operations},'input_bindings':{}},
        'residual_prerequisites':['Date-only prospective terms under supplied assumptions; no modification gain/loss, interest or impairment']}
    return {'profile':transition.PROFILE,'expected_state_sha256':core.digest(book),'expected_method_sha256':core.digest(method),
        'method':method,'event':deepcopy(event),'schemas':schemas,'memory_definition':deepcopy(state['memory_definition'])}

def event_types(book,operation):
    if operation=='collect':return life.event_types(book,'collect')
    if operation=='amend':return {'approved':core.BOOL,'claim_id':TEXT,'customer':TEXT,'prior_term':TEXT,'term_id':TEXT,'due':DATE,'premise':TEXT}
    core.need(operation=='assess','term_operation');return life.event_types(book,'assess')

def step(state,request):
    try:
        book=validate(state);bounded(request)
        closed(request,['profile','expected_state_sha256','operation','event'],'term_event_request')
        core.need(request['profile']==STEP,'term_event_profile');core.need(request['expected_state_sha256']==core.digest(state),'stale_term_state')
        operation=request['operation'];event=request['event'];closed(event,['id','date','inputs'],'term_event')
        text(event['id'],'event_id');core.need(event['id'] not in book['seen'],'duplicate_event')
        day=core.scalar(event['date'],'date').isoformat();core.need(book['date']<=day<book['period']['end_exclusive'],'event_chronology')
        declared=event_types(book,operation);core.need(type(event['inputs']) is dict and set(event['inputs'])==set(declared),'exact_event_inputs')
        unknown=[];values={}
        for name,row in event['inputs'].items():
            closed(row,['type','value','provenance'],'event_input');text(row['provenance'],'event_provenance')
            core.need(row['type']==declared[name],'event_type:'+name)
            core.validate_values({'inputs':{name:{'type':engine.dimensions.encoded(declared[name])}}},{name:row['value']})
            if row['value']['status']=='unknown':unknown.append(name)
            else:values[name]=row['value']['value']
        if unknown:return {'profile':STEP,**FLAGS,'status':'unresolved','inputs':unknown}
        if values['approved'] is not True:return {'profile':STEP,**FLAGS,'status':'unsupported','reason':'applicability_not_selected'}
        cursor=book['memory']['collection_clock']['cursor'];claims=book['memory']['claims'];operations=[]
        def update(op,path,value):operations.append({'id':'term.'+str(len(operations)),'op':op,'path':path,'value':literal(value)})
        if operation in ['amend','collect']:core.need(day>=cursor,'assessment_day_sealed')
        if operation=='amend':
            identity=values['claim_id'];core.need(identity in claims,'unknown_claim');row=claims[identity]
            core.need(values['customer']==row['customer'],'claim_customer_mismatch')
            core.need(values['prior_term']==row['current_term'],'stale_current_term')
            term_id=values['term_id'];text(term_id,'term_id');core.need(term_id not in row['terms'] and term_id!='none','duplicate_term_id')
            text(values['premise'],'term_premise');core.need(day<=values['due'],'due_before_effective')
            core.need(day>row['terms'][row['current_term']]['effective'],'ambiguous_term_effective_date')
            term={'due':values['due'],'effective':day,'event_id':event['id'],'predecessor':row['current_term'],'premise':values['premise']}
            update('insert',['claims',identity,'terms',term_id],term)
            update('replace',['claims',identity,'current_term'],term_id);update('replace',['claims',identity,'due'],values['due'])
        elif operation=='assess':
            start,end=[core.scalar(values[k],'date') for k in ['start','end_exclusive']]
            core.need(values['start']==cursor and start<end,'assessment_cursor')
            core.need(day==(end-timedelta(days=1)).isoformat() and values['end_exclusive']<=book['period']['end_exclusive'],'assessment_window')
            for identity,row in claims.items():
                assessment={'term_id':row['current_term'],'as_of':day,'remaining':row['remaining'],
                    'overdue':row['remaining'] if day>row['due'] else '0/1','origin':'recorded_event','event_id':event['id']}
                core.need(event['id'] not in row['assessments'],'duplicate_assessment_id')
                update('insert',['claims',identity,'assessments',event['id']],assessment)
                for name,value in {'latest_assessment':event['id'],'assessed':True,'assessment_date':day,
                                   'assessed_remaining':assessment['remaining'],'overdue':assessment['overdue']}.items():
                    update('replace',['claims',identity,name],value)
            update('replace',['collection_clock','cursor'],values['end_exclusive'])
        command={'kind':'event','method_key':'collect','event':event}
        typed=life.make_request(book,state,command) if operation=='collect' else state_request(state,event,operations)
        result=transition.propose(book,typed);core.need(result['status']=='proposed','typed_transition:'+result.get('reason','invalid'))
        after=deepcopy(state);after['book']=result['after'];validate(after)
        return {'profile':STEP,**FLAGS,'status':'proposed','request_sha256':core.digest(request),'before_sha256':core.digest(state),
                'after':after,'after_sha256':core.digest(after),'typed_request':typed,'transition':result,
                'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
    except Exception as exc:return invalid(exc)

def carry(state,request):
    try:
        book=validate(state);bounded(request)
        closed(request,['profile','expected_state_sha256','report_request','close_id','retained_account','next_end_exclusive'],'term_carry')
        core.need(request['profile']==CARRY,'term_carry_profile');core.need(request['expected_state_sha256']==core.digest(state),'stale_term_state')
        core.need(core.canonical(request['report_request']['closing'])==core.canonical(book),'carry_closing_binding')
        policies={p:{'kind':'preserve','provenance':'Preserve immutable terms and assessment basis'} for p in book['memory_types']}
        policies['/collection_clock/cursor']={'kind':'next_period_start','provenance':'New period opens a contiguous assessment window'}
        typed=life.carry.request(request['report_request'],request['close_id'],request['retained_account'],request['next_end_exclusive'],policies)
        result=life.carry.propose(typed);core.need(result['status']=='proposed','term_carry:'+result.get('reason','invalid'))
        after=deepcopy(state);after['book']=result['next_opening'];validate(after)
        return {'profile':CARRY,**FLAGS,'status':'proposed','before_sha256':core.digest(state),'request_sha256':core.digest(request),
                'after':after,'after_sha256':core.digest(after),'carry':result,'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
    except Exception as exc:return invalid(exc)

def verify(state,request,result):
    try:
        fn=carry if request.get('profile')==CARRY else step
        return core.canonical(fn(state,request))==core.canonical(result)
    except Exception:return False
