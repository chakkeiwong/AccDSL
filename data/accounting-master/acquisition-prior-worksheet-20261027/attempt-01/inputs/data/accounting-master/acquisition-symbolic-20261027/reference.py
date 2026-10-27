"""Bounded symbolic acquisition dependencies; never posts or admits accounting."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction
from copy import deepcopy
import importlib.util,json,re
H=Path(__file__).resolve().parent;R=H.parents[2]
PINS={
 'data/accounting-master/control-group-boundary-20261027/scope.py':'3ea678cd609568ca59468efb660f8bc7c5425acc28e32afa8f51455eb981ef38',
 'data/accounting-master/acquisition-period-authority-20261026/acquisition-period-contract.md':'ab889c87f2ab0d9c93940bbe29d9f4d2854ee7416911a78fc93a68c54f2cc05c',
 'data/accounting-master/acquisition-period-authority-20261026/authority-matrix.md':'3a2b59674b24fee78948cfa785b6bb0778d396565f64346db4fa03849ece8b1d',
 'data/accounting-master/acquisition-period-authority-20261026/verification-attempt-03/verification.json':'9cf111bf6d82c3d3464ca52786c931f5e00125c5e2497ef88a2f70a34f9f07a1'}
spec=importlib.util.spec_from_file_location('acquisition_group_scope',R/next(iter(PINS)))
scope=importlib.util.module_from_spec(spec);spec.loader.exec_module(scope)
h=scope.history
PROFILE='ConditionalAcquisitionExpressions/1'
FLAGS=dict(source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False,executed=False)
ROLES={'A':'recognised_assets','L':'assumed_liabilities','T':'consideration_transferred','P':'prior_equity_fair_value','Q':'nci_fair_value','R':'post_control_legal_profit','D':'post_control_expense_adjustment','O':'post_control_legal_oci','U':'post_control_oci_adjustment','V':'post_control_nci_distributions','M':'post_control_other_nci_changes'}
ACQ={'A','L','T','P','Q'}
def fmt(x):return str(x.numerator)+'/'+str(x.denominator)
def scalar(x):
    h.need(type(x) is str and len(x)<80 and re.fullmatch(r'-?(0|[1-9][0-9]*)/[1-9][0-9]*',x) is not None,'rational_required')
    q=Fraction(x);h.need(fmt(q)==x,'canonical_rational');return q
def plus(*terms):
    out={}
    for coefficient,expression in terms:
        for symbol,value in expression.items():out[symbol]=out.get(symbol,Fraction())+coefficient*value
    return {k:v for k,v in out.items() if v}
def serial(expression):return dict(constant='0/1',coefficients={k:fmt(v) for k,v in sorted(expression.items())})

def derive(body):
    try:
        for p,d in PINS.items():h.need(sha256((R/p).read_bytes()).hexdigest()==d,'dependency_hash:'+p)
        h.need(len(json.dumps(body,allow_nan=False))<=300000,'request_size')
        h.fields(body,['profile','payload','expected_payload_sha256'],'envelope')
        h.need(body['profile']==PROFILE,'profile')
        p=body['payload'];h.need(h.digest(p)==body['expected_payload_sha256'],'payload_binding')
        h.fields(p,['scope_request','route','prior_interest','ownership','acquisition','amounts','sources'],'payload')
        s=scope.scope(p['scope_request']);h.need(s['status']=='scope_assessed','scope:'+s.get('reason','invalid'))
        history=s['history'];hr=p['scope_request']['history_request'];actor=hr['actor'];subject=hr['subject'];cutoff=h.moment(hr['cutoff'])
        dependencies=[];used=set()
        h.need(type(p['sources']) is dict and len(p['sources'])<=32,'source_limit')
        for sid,source in p['sources'].items():
            h.fields(source,['text','subject','actor','available_at'],'source');h.text(source['text'])
            h.need(h.digest(source)==sid,'source_identity');h.need(source['subject']==subject,'source_subject')
            h.need(source['actor']==actor,'source_actor')
            if source['available_at'] is not None:h.moment(source['available_at'])
        def support(sid):
            h.need(type(sid) is str and sid in p['sources'],'missing_source');used.add(sid)
            available=p['sources'][sid]['available_at']
            if available is None:dependencies.append('source_availability_unknown:'+sid)
            elif h.moment(available)>cutoff:dependencies.append('source_after_cutoff:'+sid)
        for name in ['route','prior_interest']:
            h.fields(p[name],['kind','evidence_sha256'],name);h.text(p[name]['kind']);support(p[name]['evidence_sha256'])
        if p['route']['kind']!='ordinary_business_acquisition':dependencies.append('acquisition_route:'+p['route']['kind'])
        prior=p['prior_interest']['kind']
        h.need(prior in ['none','equity','debt','unresolved'],'prior_interest_kind')
        if prior in ['debt','unresolved']:dependencies.append('prior_interest_and_separate_transaction_analysis:'+prior)
        ow=p['ownership'];h.fields(ow,['fraction','rights','nci_election','evidence_sha256'],'ownership')
        f=scalar(ow['fraction']);h.need(0<f<=1,'ownership_range')
        h.need(f==Fraction(s['supplied_control_edge']['ownership_fraction']),'ownership_scope_binding')
        support(ow['evidence_sha256']);h.text(ow['rights'])
        if ow['rights']!='constant_ordinary_present_rights':dependencies.append('ownership_rights_method:'+ow['rights'])
        election=ow['nci_election']
        h.need(election in ['none','fair_value','proportional','unresolved'],'nci_election')
        if election=='unresolved':dependencies.append('nci_measurement_election')
        else:h.need((f==1 and election=='none') or (f<1 and election in ['fair_value','proportional']),'nci_election_ownership')
        q=1-f
        acq=p['acquisition'];h.fields(acq,['at','currency','unit'],'acquisition');instant=h.moment(acq['at'])
        h.need(type(acq['currency']) is str and re.fullmatch('[A-Z]{3}',acq['currency']) is not None,'currency')
        h.need(acq['unit']=='currency_unit','unit')
        for side in ['opening','closing']:
            for book in p['scope_request']['group_request'][side]['books'].values():h.need(book['context']['currency']==acq['currency'],'book_currency_binding')
        transitions=history['conditional_transitions'];atoms=history['atoms']
        if history['unresolved_atom_indices']:dependencies.append('unresolved_control_history')
        elif not (len(transitions)==1 and transitions[0]['kind']=='gain' and atoms[0]['status']=='no' and atoms[-1]['status']=='yes'):
            dependencies.append('single_gain_method_required')
        else:h.need(Fraction(transitions[0]['at'])==instant,'acquisition_control_date')
        h.need(h.moment(hr['interval']['start'])<instant<h.moment(hr['interval']['end_exclusive']),'acquisition_inside_period')
        amounts=p['amounts'];h.need(type(amounts) is dict and set(amounts)<=set(ROLES),'amount_roles')
        symbols=set()
        for role,item in amounts.items():
            h.fields(item,['symbol','kind','currency','unit','timing','basis','evidence_sha256'],'amount')
            h.need(type(item['symbol']) is str and re.fullmatch('[A-Za-z][A-Za-z0-9_]{0,31}',item['symbol']) is not None,'symbol')
            h.need(item['symbol'] not in symbols,'duplicate_symbol');symbols.add(item['symbol'])
            h.need(item['kind']==ROLES[role],'amount_kind:'+role)
            h.need(item['currency']==acq['currency'] and item['unit']==acq['unit'],'amount_unit:'+role)
            h.text(item['basis']);support(item['evidence_sha256'])
            if role in ACQ:
                h.fields(item['timing'],['at'],'amount_timing');h.need(h.moment(item['timing']['at'])==instant,'amount_date:'+role)
            else:
                h.fields(item['timing'],['start','end_exclusive'],'amount_timing')
                h.need(h.moment(item['timing']['start'])==instant and h.moment(item['timing']['end_exclusive'])==h.moment(hr['interval']['end_exclusive']),'post_control_interval:'+role)
        required={'A','L','T','R','D','O','U'}
        if f<1:required.update(['V','M'])
        else:h.need(not {'V','M'} & set(amounts),'no_nci_with_movements')
        if prior=='equity':required.add('P')
        if election=='fair_value':required.add('Q')
        if prior=='none':h.need('P' not in amounts,'prior_none_with_amount')
        if election in ['none','proportional']:h.need('Q' not in amounts,'nci_election_with_amount')
        for role in sorted(required-set(amounts)):dependencies.append('missing_amount:'+role)
        base=dict(profile=PROFILE,**FLAGS,request_sha256=h.digest(body),scope_result=deepcopy(s),descriptors=deepcopy(amounts),premises=deepcopy({k:v for k,v in p.items() if k not in ['scope_request','amounts']}),dependency_sha256=deepcopy(PINS),implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        if dependencies:return dict(**base,status='unresolved',dependencies=sorted(set(dependencies)),expressions={})
        v={k:{item['symbol']:Fraction(1)} for k,item in amounts.items()}
        z={};net=plus((1,v['A']),(-1,v['L']))
        nci=v['Q'] if election=='fair_value' else plus((q,net))
        prior_eq=v['P'] if prior=='equity' else z
        excess=plus((1,v['T']),(1,nci),(1,prior_eq),(-1,net))
        profit=plus((1,v['R']),(-1,v['D']));oci=plus((1,v['O']),(1,v['U']))
        closing_nci=plus((1,nci),(q,profit),(q,oci),(-1,v['V']),(1,v['M'])) if f<1 else z
        e=dict(net_identifiable_assets=net,nci_at_acquisition=nci,qualifying_prior_equity=prior_eq,acquisition_excess=excess,post_control_profit=profit,post_control_oci=oci,owners_profit=plus((f,profit)),nci_profit=plus((q,profit)),owners_oci=plus((f,oci)),nci_oci=plus((q,oci)),nci_closing=closing_nci)
        return dict(**base,status='conditional_expressions',dependencies=['unmeasured:'+k for k in sorted(required)],expressions={k:serial(x) for k,x in e.items()},recognition='not_assessed',outstanding=['source_truth_and_applicability','item_measurement_population_and_exceptions','consideration_and_separate_transactions','tax_and_elimination_completeness','excess_sign_and_required_reassessment','complete_worksheet_and_reports'],scope='Formal unknown-amount dependencies only; no amounts are measured and no financial report is produced.')
    except Exception as exc:return dict(profile=PROFILE,status='invalid',**FLAGS,reason=str(exc)[:350] or type(exc).__name__)
