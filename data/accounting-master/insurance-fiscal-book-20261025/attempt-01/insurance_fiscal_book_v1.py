"""Explicit hypothetical calendar-year carries for two retained insurer schedules."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import insurance_loss_book_v1 as base

ROOT=Path(__file__).resolve().parents[1]
PROFILE='InsuranceFiscalBook/1'
FLAGS={**base.FLAGS,'fiscal_completeness':False}
core,engine,program=base.core,base.engine,base.program
PINS={'scripts/insurance_loss_book_v1.py':'d8a8f7bb9276ea522800fa4d8aaae0f26067460da25fedde863cdc661f00c77d',
      'scripts/company_book_carry_v1.py':'72a1b3d45b24742267b120b04ee0ba97e479b75b08710a66b014d32d88b70c5c',
      'scripts/declared_company_program_v2.py':'aa69e8bfb4628ddff5867bb243996b32d43c56119bd61f2baf1b87b23d5d1633'}
TEMPORARY=tuple(k for k,v in base.ROLES.items() if v in ['income','expense'])


def protected():
    for name,expected in PINS.items():
        core.need(sha256((ROOT/name).read_bytes()).hexdigest()==expected,'dependency_hash:'+name)
    base.protected()


def prepare(body):
    protected();engine.memory.bounded(body)
    core.need(len(core.canonical(body))<=16*core.MAX_BYTES,'fiscal_request_size')
    core.closed(body,['profile','base_request','base_result','base_result_sha256','fiscal_policy',
                      'retained_account','memory_policies'],'insurance_fiscal_request')
    core.need(body['profile']==PROFILE,'insurance_fiscal_profile')
    core.need(core.digest(body['base_result'])==body['base_result_sha256'],'stale_base_result')
    actual=base.propose(body['base_request'])
    if actual['status']!='proposed_provisional':raise base.NativeRefusal(actual)
    core.need(core.canonical(actual)==core.canonical(body['base_result']),'base_result_recomputation')
    policy=body['fiscal_policy']
    core.closed(policy,['kind','premise','event_completeness'],'explicit_fiscal_policy')
    core.need(policy['kind']=='calendar_years_2025_2027','supported_calendar_policy')
    core.need(policy['event_completeness']=='unknown','event_completeness_not_admitted')
    engine.text(policy['premise'],'fiscal_policy_premise')
    book=body['base_request']['opening'];retained=body['retained_account']
    core.need(book['period']=={'start':'2025-01-01','end_exclusive':'2027-01-02'},'retained_cumulative_interval')
    core.need(type(retained) is str and retained in book['accounts'] and
              book['accounts'][retained]['classification']=='equity','retained_equity_account')
    core.need(retained not in body['base_request']['roles'].values(),'retained_role_alias')
    policies=body['memory_policies']
    core.need(type(policies) is dict and set(policies)==set(book['memory_types']),'complete_preserve_policies')
    for p in policies.values():
        core.closed(p,['kind','provenance'],'preserve_memory_policy')
        core.need(p['kind']=='preserve','insurance_memory_must_survive')
        engine.text(p['provenance'],'memory_policy_provenance')
    return actual


def carry_command(body,year):
    return {'kind':'carry','id':'insurance.fiscal.close.'+str(year),'cutoff':str(year)+'-12-31',
        'equity_movements':[],'notes':[{'id':'event_completeness','label':'Hypothetical period observation',
        'status':'unresolved','reason':body['fiscal_policy']['premise']+'; event-population completeness remains unknown.'}],
        'retained_account':body['retained_account'],'next_end_exclusive':str(year+2)+'-01-01',
        'memory_policies':deepcopy(body['memory_policies'])}


def build(body):
    baseline=prepare(body);compiled=deepcopy(baseline['program'])
    compiled['name']+='.__calendar_carry';compiled['opening']['period']['end_exclusive']='2026-01-01'
    offsets={r:baseline['expected_steps'][2]['balances'][r] for r in TEMPORARY}
    transformations=[]
    for index in range(3,6):
        key='insurance.'+str(index+1);entry=compiled['registry']['entries'][key]
        old=deepcopy(entry['method']);method=entry['method'];deltas=[]
        for phase in ['preconditions','postconditions']:
            conditions=method[phase]['manifest']['requirements']
            for role in TEMPORARY:
                name='balance_'+role;matches=[r for r in conditions if r['id']==name]
                core.need(len(matches)==1,'single_balance_condition')
                predicate=matches[0]['predicate']
                core.need(predicate['op']=='eq' and predicate['left']=={'op':'ref','id':name}
                          and predicate['right']['op']=='const','literal_balance_condition')
                previous=predicate['right']['value']
                updated=base.fmt(Fraction(previous)-Fraction(offsets[role]))
                predicate['right']['value']=updated
                deltas.append({'phase':phase,'role':role,'before':previous,'subtract':offsets[role],'after':updated})
        entry['method_sha256']=core.digest(method)
        # Prove that reversing the stated constant substitutions recovers every byte.
        restored=deepcopy(method)
        for d in deltas:
            item=next(r for r in restored[d['phase']]['manifest']['requirements'] if r['id']=='balance_'+d['role'])
            item['predicate']['right']['value']=d['before']
        core.need(restored==old,'only_balance_conditions_change')
        transformations.append({'method_key':key,'before_sha256':core.digest(old),
            'after_sha256':entry['method_sha256'],'deltas':deltas})
    original=deepcopy(compiled['commands'])
    core.need(len(original)==8 and [c['kind'] for c in original]==['event']*3+['report']+['event']*3+['report'],
              'retained_command_sequence')
    compiled['commands']=[carry_command(body,2025)]+original[:4]+[carry_command(body,2026)]+original[4:]+[carry_command(body,2027)]
    return compiled,baseline,transformations


def propose(body):
    try:
        compiled,baseline,transformations=build(body);result=program.run(compiled)
        core.need(result['status']=='complete_provisional','fiscal_program:'+str(result.get('stop',result.get('reason')))[:200])
        events=[r for r in result['trace'] if r['command']['kind']=='event']
        oldevents=[r for r in baseline['execution']['trace'] if r['command']['kind']=='event']
        core.need(len(events)==len(oldevents)==6,'six_native_events')
        for row,prior in zip(events,oldevents):
            core.need(row['command']==prior['command'],'native_event_unchanged')
            a,b=row['result']['transition'],prior['result']['transition']
            core.need(a['journal']==b['journal'] and a['cash_flows']==b['cash_flows'],'native_journal_and_flow')
            core.need(a['monetary']==b['monetary'],'gross_monetary_correspondence')
            core.need(a['after']['memory']==b['after']['memory'],'native_and_complement_memory')
            for role in ['cash','liability']:
                account=body['base_request']['roles'][role]
                core.need(a['after']['balances'][account]==b['after']['balances'][account],'native_balance:'+role)
        carries=[r for r in result['trace'] if r['command']['kind']=='carry']
        core.need(len(carries)==3 and len(result['archives'])==3,'three_carry_archives')
        initial=body['base_request']['opening'];retained=body['retained_account']
        cumulative=Fraction(0)
        for row,profit,payments in zip(carries,['0/1','-5/1','10/1'],['0/1','50/1','45/1']):
            carry=row['result'];report=carry['report'];cumulative+=Fraction(profit)
            core.need(report['income']['profit']==profit,'fiscal_period_profit')
            core.need(report['cash_flows']['activities']['operating']['payments']==payments,'fiscal_period_payments')
            core.need(carry['cash_flows']==[] and carry['journal'][initial['cash_account']]=='0/1','carry_no_cash')
            core.need(carry['next_opening']['memory']==row['request']['report_request']['closing']['memory'],'carry_preserves_memory')
            core.need(carry['next_opening']['balances'][retained]==base.fmt(Fraction(initial['balances'][retained])-cumulative),'retained_profit_carry')
            for account,metadata in initial['accounts'].items():
                if metadata['classification'] in ['income','expense']:
                    core.need(carry['next_opening']['balances'][account]=='0/1','temporary_account_reset')
        ending=result['current'];oldending=baseline['execution']['current']
        for account,metadata in initial['accounts'].items():
            if metadata['classification'] not in ['income','expense'] and account!=retained:
                core.need(ending['balances'][account]==oldending['balances'][account],'final_complement_balance')
        core.need(ending['memory']==oldending['memory'],'final_memory_preserved')
        core.need(ending['period']=={'start':'2028-01-01','end_exclusive':'2029-01-01'},'final_period')
        opening_report=program.reports.report(program.reports.request(ending,ending,compiled['schemas'],compiled['mapping']))
        core.need(opening_report['status']=='reported' and opening_report['income']['profit']=='0/1','next_opening_report')
        core.need(opening_report['equity']['opening']==carries[-1]['result']['report']['equity']['closing'],'equity_continuity')
        return {'profile':PROFILE,**FLAGS,'status':'proposed_provisional','request_sha256':core.digest(body),
            'base_request_sha256':core.digest(body['base_request']),'base_result_sha256':core.digest(baseline),
            'native_result':deepcopy(baseline['native_result']),'loss_origins':deepcopy(baseline['native_result']['report']['loss_origins']),
            'fiscal_policy':deepcopy(body['fiscal_policy']),'transformations':transformations,
            'program':compiled,'execution':result,'next_opening_report':opening_report,
            'dependency_sha256':deepcopy(PINS),'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'unresolved':['Actual event population and accounting admission','General fiscal policies and insurer measurements',
                          'Source applicability, complete notes and durable posting']}
    except base.NativeRefusal as exc:
        status=exc.result['status']
        return {'profile':PROFILE,**FLAGS,'status':status if status in ['unresolved','unsupported'] else 'invalid',
                'reason':'base:'+exc.result.get('reason','refusal'),'base_refusal':deepcopy(exc.result)}
    except Exception as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350] or type(exc).__name__}


def verify(body,result):
    try:
        core.need(len(core.canonical(result))<=16*core.MAX_BYTES,'fiscal_result_size')
        return core.canonical(propose(body))==core.canonical(result)
    except Exception:return False
