"""Propose a declared-book trace for two retained exact insurer loss schedules."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import importlib.util
import json

import declared_company_program_v2 as program
import declared_operating_methods_v1 as helpers

ROOT = Path(__file__).resolve().parents[1]
NATIVE = 'data/accounting-master/insurance-service-finance-origins-20261016/'
PROFILE = 'InsuranceLossBook/1'
FLAGS = {**program.FLAGS, 'native_accounting_admission': False, 'source_complete': False}
PINS = {
    'scripts/declared_company_program_v2.py': 'aa69e8bfb4628ddff5867bb243996b32d43c56119bd61f2baf1b87b23d5d1633',
    'scripts/declared_operating_methods_v1.py': '0201b1d8934e9ec40aeee301609090cc6f5d40829eb9d3dd603757f2a61a7590',
    NATIVE+'reference.py': 'ae2dc29a60854c623a715b42a648163893c7172652de7dd3cd99a2a005a41dd8',
    NATIVE+'input-lock-v2.json': 'da14627130a78e67e83f2014251d109d6e66bea0a2b38ae81dfe14dcafe59528',
    NATIVE+'attempt-02/exchanges.json': 'b9ba0931fb536ea642d7fd9e90abc2a0f28ced82b1660106f4ad973b4b459ca4',
}
ROLES = {'cash':'asset','liability':'liability','finance_expense':'expense',
         'revenue':'income','loss_reversal':'income','claims_expense':'expense'}
CASES = ('loss-service-finance','zero-loss-boundary')
core, engine = program.core, program.engine
DATE = {'kind':'date','context':{}}
TEXT = {'kind':'text','context':{}}


def fmt(value):
    q = Fraction(value)
    return str(q.numerator)+'/'+str(q.denominator)


class NativeRefusal(Exception):
    def __init__(self, result):
        self.result = result


def protected():
    for name, expected in PINS.items():
        core.need(sha256((ROOT/name).read_bytes()).hexdigest() == expected, 'dependency_hash:'+name)
    program.protected()


def native_case(case_id):
    protected()
    core.need(case_id in CASES, 'supported_native_case')
    rows = json.loads((ROOT/(NATIVE+'attempt-02/exchanges.json')).read_text())
    return deepcopy(next(r for r in rows if r['id'] == case_id))


def native_result(request):
    spec = importlib.util.spec_from_file_location('insurance_loss_book_native', ROOT/(NATIVE+'reference.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.calculate(deepcopy(request))


def prepare(body):
    protected()
    engine.memory.bounded(body)
    core.need(len(core.canonical(body)) <= core.MAX_BYTES, 'insurance_request_size')
    core.closed(body, ['profile','case_id','native_request','native_result','native_request_sha256',
        'native_result_sha256','opening','schemas','roles','memory_map','context_adapter','mapping','cash_policy'],
        'insurance_loss_book_request')
    core.need(body['profile'] == PROFILE, 'insurance_loss_book_profile')
    selected = native_case(body['case_id'])
    request, result = body['native_request'], body['native_result']
    core.need(core.digest(request) == body['native_request_sha256'] and
              core.digest(result) == body['native_result_sha256'], 'stale_native_input')
    actual = native_result(request)
    if actual['status'] != 'conditional_complete':
        raise NativeRefusal(actual)
    core.need(core.canonical(request) == core.canonical(selected['request']), 'outside_retained_native_request')
    core.need(core.canonical(actual) == core.canonical(result) == core.canonical(selected['result']),
              'native_result_recomputation')
    book, schemas, roles, pointers = (body[k] for k in ['opening','schemas','roles','memory_map'])
    engine.validate_book(book, schemas)
    context = request['context']
    core.need(book['context']['entity'] == context['entity'], 'native_owner_binding')
    core.need(context['currency'] == 'CU' and book['context']['currency'] == 'XCU', 'illustrative_currency_alias')
    adapter = body['context_adapter']
    core.closed(adapter, ['native_context_sha256','host_context_sha256','unit_scale','premise'], 'native_context_adapter')
    core.need(adapter['native_context_sha256'] == core.digest(context) and
              adapter['host_context_sha256'] == core.digest(book['context']), 'context_adapter_binding')
    core.need(context['unit'] == 'currency units' and adapter['unit_scale'] == '1/1', 'unit_scale_one_required')
    engine.text(adapter['premise'], 'currency_alias_premise')
    data = request['data']
    core.need(book['date'] == book['period']['start'] == data['opening_date'], 'native_opening_date')
    core.need(book['period']['end_exclusive'] > data['periods'][-1]['date'], 'native_dates_within_host_period')
    core.need(not book['flows'], 'empty_opening_cash_flows')
    core.need(type(roles) is dict and set(roles) == set(ROLES), 'exact_insurance_roles')
    core.need(all(type(a) is str for a in roles.values()) and len(set(roles.values())) == len(roles), 'injective_insurance_roles')
    for role, kind in ROLES.items():
        core.need(roles[role] in book['accounts'] and book['accounts'][roles[role]]['classification'] == kind,
                  'insurance_role_class:'+role)
    core.need(roles['cash'] == book['cash_account'], 'insurance_cash_role')
    expected = {k:'0/1' for k in ROLES}
    expected.update(cash=fmt(data['cash']),liability=fmt(-Fraction(data['liability'])))
    for role, value in expected.items():
        core.need(book['balances'][roles[role]] == value, 'native_opening_balance:'+role)
    core.need(type(pointers) is dict and set(pointers) == {'loss_component','next_step','case_ref'}, 'exact_insurance_memory')
    core.need(all(type(p) is str for p in pointers.values()) and len(set(pointers.values())) == 3, 'distinct_memory_pointers')
    money = engine.money_type(book)
    scalar = {'kind':'rational','context':engine.type_context(book),'dimensions':{},'scale':'1/1'}
    memory_values = {'loss_component':fmt(data['loss_component']),'next_step':'0/1','case_ref':core.digest(request)}
    for key, typ in [('loss_component',money),('next_step',scalar),('case_ref',TEXT)]:
        pointer = pointers[key]
        core.need(book['memory_types'].get(pointer) == typ, 'insurance_memory_type:'+key)
        found, value = engine.binding.located(book['memory'],pointer)
        core.need(found and value == memory_values[key], 'insurance_memory_value:'+key)
    policy = body['cash_policy']
    core.closed(policy, ['claims_activity','premise'], 'insurance_cash_policy')
    core.need(policy['claims_activity'] == 'operating', 'supported_claim_cash_activity')
    engine.text(policy['premise'], 'claim_cash_premise')
    opening_report = program.reports.report(program.reports.request(book,book,schemas,body['mapping']))
    core.need(opening_report['status'] == 'reported', 'opening_report:'+opening_report.get('reason',''))
    return expected, memory_values, money, scalar


def build(body):
    balances, memories, money, scalar = prepare(body)
    book, pointers, roles = body['opening'], body['memory_map'], body['roles']
    request, native = body['native_request'], body['native_result']
    native_report = native['report']
    empty = {'type':'object','properties':{},'required':[],'additionalProperties':False}
    schemas = {**deepcopy(body['schemas']),core.digest(empty):empty}
    registry = {'profile':program.methods.REGISTRY,'context':deepcopy(book['context']),'entries':{}}
    commands, expected_steps = [], []
    cumulative_profit = Fraction(0)
    report_expectations = []
    for index, journal in enumerate(native_report['journals']):
        period_index, part = divmod(index,3)
        period = request['data']['periods'][period_index]
        row = native_report['rows'][period_index]
        origin_rows = native_report['loss_origins'][period_index*3:period_index*3+3]
        if part == 0:
            loss_delta = Fraction(origin_rows[0]['loss_change'])
        elif part == 1:
            loss_delta = sum(Fraction(r['loss_change']) for r in origin_rows[1:])
        else:
            loss_delta = Fraction(0)
        before, memory_before = deepcopy(balances), deepcopy(memories)
        for role, amount in journal.items():
            core.need(role in ROLES, 'native_journal_role')
            balances[role] = fmt(Fraction(balances[role])+Fraction(amount))
        memories['loss_component'] = fmt(Fraction(memories['loss_component'])+loss_delta)
        memories['next_step'] = fmt(index+1)
        key = 'insurance.'+str(index+1)
        identity = body['case_id']+'.'+key

        def conditions(expected_balances, expected_memory, include_date):
            types, bindings, checks = {}, {}, []
            for role, amount in expected_balances.items():
                name='balance_'+role;types[name]=money;bindings[name]=helpers.account(role)
                checks.append((name,helpers.binary('eq',helpers.ref(name),helpers.constant(money,amount)),[name],'invalid'))
            for field, typ in [('loss_component',money),('next_step',scalar),('case_ref',TEXT)]:
                name='memory_'+field;types[name]=typ;bindings[name]={'kind':'memory','pointer':pointers[field]}
                checks.append((name,helpers.binary('eq',helpers.ref(name),helpers.constant(typ,expected_memory[field])),[name],'invalid'))
            if include_date:
                types['actual_date']=DATE;bindings['actual_date']=helpers.event('actual_date')
                checks.append(('native_event_date',helpers.binary('eq',helpers.ref('actual_date'),helpers.constant(DATE,period['date'])),['actual_date'],'invalid'))
            return {'manifest':helpers.conditions(identity,types,checks),'bindings':bindings}

        memory_ops=[]
        for field in ['loss_component','next_step']:
            pointer=pointers[field]
            memory_ops.append({'id':'write.'+field,'op':'replace',
                'path':[p.replace('~1','/').replace('~0','~') for p in pointer[1:].split('/')],
                'value':{'kind':'literal','value':memories[field]}})
        flows=[]
        if 'cash' in journal:
            flows=[{'id':'claims','activity':body['cash_policy']['claims_activity'],
                'origin':'Native '+body['case_id']+' period '+str(period_index+1)+' claims',
                'expression':helpers.constant(money,fmt(journal['cash'])),'requires':[]}]
        method={'profile':engine.METHOD,'id':identity,'version':'1','context':deepcopy(book['context']),
            'account_map':deepcopy(roles),'preconditions':conditions(before,memory_before,True),
            'postconditions':conditions(balances,memories,False),
            'monetary':{'definition':{'profile':engine.monetary.PROFILE,'method_id':identity,'version':'1',
                'inputs':{},'calculations':[],'accounts':{r:deepcopy(money) for r in ROLES},'cash_account':'cash',
                'postings':[{'id':r,'account':r,'expression':helpers.constant(money,fmt(a)),'requires':[]} for r,a in journal.items()],
                'flows':flows},'bindings':{}},
            'memory':{'definition':{'profile':engine.memory.PROFILE,'state_schema':book['memory_schema'],
                'input_schema':core.digest(empty),'operations':memory_ops},'input_bindings':{}},
            'residual_prerequisites':['Exact retained native request '+core.digest(request),
                body['context_adapter']['premise'],body['cash_policy']['premise'],
                'Historical conditional measurement; no source/accounting admission or posting authority.']}
        registry['entries'][key]={'method_sha256':core.digest(method),'method':method,'schemas':deepcopy(schemas),
            'account_classes':deepcopy(ROLES),'event_inputs':{},'metadata_bindings':{'actual_date':'date'},
            'clock':{'kind':'direct_event_date'}}
        commands.append({'kind':'event','method_key':key,'event':{'id':identity,'date':period['date'],'inputs':{}}})
        expected_steps.append({'id':identity,'date':period['date'],'native_journal':deepcopy(journal),
            'balances':deepcopy(balances),'memory':deepcopy(memories),
            'loss_origins':deepcopy(origin_rows[1:] if part==1 else [origin_rows[0]] if part==0 else [])})
        if part==2:
            cumulative_profit += Fraction(row['profit'])
            core.need(balances['cash']==fmt(row['cash']) and balances['liability']==fmt(-Fraction(row['liability'])) and
                      memories['loss_component']==fmt(row['loss_component']), 'native_step_state')
            rid='native.period.'+str(period_index+1)
            commands.append({'kind':'report','id':rid,'cutoff':period['date'],'equity_movements':[],
                'notes':[{'id':'native_scope','label':'Insurance measurement scope','status':'unresolved',
                    'reason':'Retained exact conditional loss schedule; complete notes and accounting admission remain unresolved.'}]})
            report_expectations.append({'id':rid,'date':period['date'],'cash':fmt(row['cash']),
                'liability':fmt(row['liability']),'loss_component':fmt(row['loss_component']),
                'cumulative_profit':fmt(cumulative_profit)})
    compiled={'profile':program.PROFILE,'name':body['case_id']+'.book','opening':deepcopy(book),
        'schemas':schemas,'registry':registry,'mapping':deepcopy(body['mapping']),'commands':commands}
    return compiled, expected_steps, report_expectations


def propose(body):
    try:
        compiled, steps, report_expectations = build(body)
        result = program.run(compiled)
        core.need(result['status']=='complete_provisional', 'compiled_program:'+str(result.get('reason',result.get('stop')))[:200])
        events=[row for row in result['trace'] if row['command']['kind']=='event']
        core.need(len(events)==len(steps),'exact_insurance_events')
        for row, expected in zip(events,steps):
            transition=row['result']['transition']
            journal={a:'0/1' for a in body['opening']['accounts']}
            for role,amount in expected['native_journal'].items():journal[body['roles'][role]]=fmt(amount)
            core.need(transition['journal']==journal,'native_full_journal')
            for role,amount in expected['balances'].items():
                core.need(transition['after']['balances'][body['roles'][role]]==amount,'native_scoped_balance')
            for field,value in expected['memory'].items():
                found,actual=engine.binding.located(transition['after']['memory'],body['memory_map'][field])
                core.need(found and actual==value,'native_memory_sequence')
        reports=[row for row in result['trace'] if row['command']['kind']=='report']
        for row,expected in zip(reports,report_expectations):
            core.need(row['result']['income']['profit']==expected['cumulative_profit'],'native_cumulative_profit')
            core.need(row['result']['cash_flows']['closing_cash']==expected['cash'],'native_report_cash')
        return {'profile':PROFILE,**FLAGS,'status':'proposed_provisional','request_sha256':core.digest(body),
            'native_request':deepcopy(body['native_request']),'native_result':deepcopy(body['native_result']),
            'native_request_sha256':body['native_request_sha256'],'native_result_sha256':body['native_result_sha256'],
            'context_adapter':deepcopy(body['context_adapter']),'roles':deepcopy(body['roles']),
            'memory_map':deepcopy(body['memory_map']),'cash_policy':deepcopy(body['cash_policy']),
            'program':compiled,'execution':result,'expected_steps':steps,'report_expectations':report_expectations,
            'scope':'Two retained exact insurer schedules; proposed host trace with supplied identity/unit mapping',
            'unresolved':['Historical source and accounting admission','Complete insurance measurements and note package',
                'Annual closing/carry policy','General native inputs, estimates, CSM, tax, FX and source populations'],
            'dependency_sha256':deepcopy(PINS),'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
    except NativeRefusal as exc:
        status=exc.result['status']
        return {'profile':PROFILE,**FLAGS,'status':status if status in ['unresolved','unsupported'] else 'invalid',
                'reason':'native:'+exc.result.get('reason','refusal'),'native_refusal':deepcopy(exc.result)}
    except Exception as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350] or type(exc).__name__}


def verify(body,result):
    try:
        core.need(len(core.canonical(result)) <= 16*core.MAX_BYTES,'insurance_result_limit')
        return core.canonical(propose(body))==core.canonical(result)
    except Exception:
        return False
