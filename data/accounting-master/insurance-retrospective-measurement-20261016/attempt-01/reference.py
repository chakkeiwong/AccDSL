"""Finite three-period, zero-rate transition reconstruction; documentary only."""
from pathlib import Path
from fractions import Fraction as Q
from datetime import date
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
SOURCE='docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt'
COMMON={'scope_nonparticipating','grouping_supported','complete_cash_including_expired','zero_rates_supported','no_tax_fx_oci','equal_service_units_supported','no_changes_in_remaining_expectations','no_incurred_unpaid_claims','prior_basis_balances_supported','transition_cash_unchanged'}
class Refusal(Exception):
    def __init__(self,status,reason):self.status=status;self.reason=reason
def fail(reason,status='rejected'):raise Refusal(status,reason)
def shape(x,keys,reason):
    if not isinstance(x,dict) or set(x)!=set(keys):fail(reason)
def num(x):
    if x is None:fail('missing_amount','unresolved')
    if not isinstance(x,str) or len(x)>80:fail('number_encoding')
    try:q=Q(x)
    except (ValueError,ZeroDivisionError):fail('number_encoding')
    if str(q)!=x or abs(q)>10**12:fail('number_encoding')
    return q
def nn(x):
    q=num(x)
    if q<0:fail('negative_amount')
    return q
def ff(x,keys):
    shape(x,keys,'finding_shape')
    for k,v in x.items():
        if v is None:fail('missing_'+k,'unresolved')
        if type(v)!=bool:fail('finding_encoding')
        if not v:fail('outside_'+k,'unsupported')
def day(s):
    try:d=date.fromisoformat(s)
    except (ValueError,TypeError):fail('date_encoding')
    if d.isoformat()!=s:fail('date_encoding')
    return d
def enc(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,list):return [enc(y) for y in x]
    if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
    return x
def calculate(req,reader=None):
    try:return enc(run(req,reader or (lambda p:(ROOT/p).read_bytes())))
    except Refusal as e:return dict(status=e.status,reason=e.reason,report=None,posts=False,mutations=[])
    except (ValueError,ZeroDivisionError):return dict(status='rejected',reason='numeric_domain',report=None,posts=False,mutations=[])

def run(q,reader):
    for item in json.loads((OUT/'input-lock.json').read_text())['files']:
        try:raw=reader(item['path'])
        except FileNotFoundError:fail('missing_protected_input','unresolved')
        if hashlib.sha256(raw).hexdigest()!=item['sha256']:fail('changed_protected_input')
    shape(q,{'wire','operation','context','route','dates','cash_history','measurement','acquisition','history','modified','treaty','prior_basis','findings'},'request_shape')
    if q['wire']!='InsuranceRetrospective/1' or q['operation']!='report':fail('wire_or_operation')
    shape(q['context'],{'entity','group','currency','unit','rule'},'context_shape')
    if any(not isinstance(v,str) or not v for v in q['context'].values()):fail('context_encoding')
    if q['context']['unit']!='currency units' or q['context']['rule']!='EU2023/1803-original-IFRS17':fail('context')
    ff(q['findings'],COMMON)
    route=q['route']
    if route not in ('full','modified'):fail('route','unsupported')
    shape(q['dates'],{'acquisition_payment','recognition','transition','initial_application'},'dates_shape')
    dates={k:day(v) for k,v in q['dates'].items()};rec=dates['recognition'];tr=dates['transition']
    if dates['acquisition_payment']>rec or tr!=date(rec.year+1,rec.month,rec.day) or dates['initial_application']!=date(tr.year+1,tr.month,tr.day):fail('date_contract')
    ch=q['cash_history'];shape(ch,{'capital','premium_received','acquisition_paid','claims_paid','reinsurance_premium_paid','recoveries_received'},'cash_shape')
    cash={k:nn(v) for k,v in ch.items()}
    cash_total=cash['capital']+cash['premium_received']-cash['acquisition_paid']-cash['claims_paid']-cash['reinsurance_premium_paid']+cash['recoveries_received']
    if cash_total<0:fail('cash_funding','unsupported')
    m=q['measurement'];shape(m,{'remaining_claims','remaining_ra','rate','coverage_units_past','coverage_units_remaining'},'measurement_shape')
    claims=nn(m['remaining_claims']);ra=nn(m['remaining_ra']);up=nn(m['coverage_units_past']);ur=nn(m['coverage_units_remaining'])
    if num(m['rate'])!=0:fail('nonzero_rate_outside_profile','unsupported')
    if up!=1 or ur!=2 or claims<=0:fail('three_equal_period_profile','unsupported')
    remaining_fraction=ur/(up+ur);fcf=claims+ra
    a=q['acquisition'];shape(a,{'allocation_mode','recognized_group','future_group','findings'},'acquisition_shape')
    if a['allocation_mode']=='supported':
        ff(a['findings'],{'allocation_supported','future_asset_recoverable','same_post_transition_allocation_method'})
        groupacq=nn(a['recognized_group']);asset=nn(a['future_group'])
        if groupacq+asset!=cash['acquisition_paid']:fail('acquisition_cash_allocation')
    elif a['allocation_mode']=='C14D_nil':
        if route!='modified':fail('nil_requires_modified','unsupported')
        ff(a['findings'],{'c14b_information_unavailable','c14d_applies'})
        if a['recognized_group'] is not None or a['future_group'] is not None:fail('nil_has_invented_allocation')
        groupacq=asset=Q(0)
    else:fail('acquisition_mode','unsupported')
    h=q['history'];mod=q['modified'];origins=[]
    if route=='full':
        if mod is not None:fail('full_has_modifications')
        shape(h,{'initial_claims','initial_ra','expected_past_claim_release','expected_past_ra_release','information_date','findings'},'history_shape')
        ff(h['findings'],{'contemporaneous_information','no_hindsight','full_retrospective_practicable'})
        if day(h['information_date'])>rec:fail('hindsight_information')
        initial_claims=nn(h['initial_claims']);initial_ra=nn(h['initial_ra']);pastclaims=nn(h['expected_past_claim_release']);pastra=nn(h['expected_past_ra_release'])
        if initial_claims-pastclaims!=claims or initial_ra-pastra!=ra:fail('full_history_measurement')
        origins.append(dict(kind='initial_estimate',source='contemporaneous_history',claims=initial_claims,ra=initial_ra,information_date=h['information_date']))
    else:
        if h is not None:fail('modified_does_not_accept_full_history')
        shape(mod,{'modifications','similar_contract_past_ra_release','information_date','findings'},'modified_shape')
        ff(mod['findings'],{'full_retrospective_impracticable','reasonable_supportable_modified_information','c12_history_unavailable','c14_history_unavailable','c15b_history_unavailable','acquisition_modification_admitted','similar_contract_ra_supported','maximise_available_retrospective_information'})
        required=['C12','C14','C15b',('C14B' if a['allocation_mode']=='supported' else 'C14D')]
        if mod['modifications']!=required:fail('unsupported_modification_set','unsupported')
        if day(mod['information_date'])>tr:fail('modified_information_after_transition')
        pastclaims=cash['claims_paid'];pastra=nn(mod['similar_contract_past_ra_release'])
        initial_claims=claims+pastclaims;initial_ra=ra+pastra
        origins.append(dict(kind='reconstructed_initial_estimate',source='C12/C14',claims=initial_claims,ra=initial_ra,known_past_cash=pastclaims,similar_contract_ra_release=pastra,information_date=mod['information_date']))
    # This finite no-change/equal-release population supports the same ratio at transition.
    if pastclaims*2!=claims or pastra*2!=ra:
        if route=='full' or pastra*2!=ra:fail('release_population_outside_profile','unsupported')
        # C12 actual claim experience can differ from expected past service;
        # the modified loss allocation below uses FCF release share, not a guessed one third.
    initial_fcf=initial_claims+initial_ra;initial_margin=cash['premium_received']-initial_fcf-groupacq
    initial_csm=max(initial_margin,Q(0));initial_loss=max(-initial_margin,Q(0))
    csm=initial_csm*remaining_fraction
    if initial_loss:
        if initial_fcf<=0:fail('loss_allocation_denominator')
        loss=initial_loss*fcf/initial_fcf
    else:loss=Q(0)
    liability=fcf+csm
    # Full reference history independently reconciles initial measurement and service.
    initial_profit=-initial_loss
    service_profit=(pastclaims+pastra)+(initial_csm-csm)-cash['claims_paid']
    projected_equity=cash['capital']+initial_profit+service_profit
    t=q['treaty'];held_asset=Q(0);held_fcf=Q(0);held_csm=Q(0);recovery_component=Q(0);held_details=None
    if t is None:
        if cash['reinsurance_premium_paid'] or cash['recoveries_received']:fail('unexplained_reinsurance_cash')
    else:
        shape(t,{'quota','initial_ra','remaining_ra','recovery_mode','information_date','findings'},'treaty_shape')
        ff(t['findings'],{'timely_treaty','all_claims_covered','quota_terms_supported','separate_ra_supported','ordinary_held_measurement_supported','same_service_pattern'}|({'loss_recovery_supported'} if t['recovery_mode']=='supported' else {'c16a_information_unavailable','c16c_applies'}))
        if day(t['information_date'])>(rec if route=='full' else tr):fail('treaty_information_date')
        quota=nn(t['quota']);hra0=nn(t['initial_ra']);hra=nn(t['remaining_ra'])
        if not 0<quota<=1 or hra0*remaining_fraction!=hra or cash['recoveries_received']!=cash['claims_paid']*quota:fail('treaty_measurement')
        ordinary_initial=cash['reinsurance_premium_paid']-initial_claims*quota-hra0
        if ordinary_initial<0:fail('held_net_gain_outside_profile','unsupported')
        ordinary_remaining=ordinary_initial*remaining_fraction
        if t['recovery_mode']=='supported':
            recovery_component=loss*quota
        elif t['recovery_mode']=='C16C_none':
            if route!='modified':fail('c16c_requires_modified','unsupported')
            recovery_component=Q(0)
        else:fail('recovery_mode','unsupported')
        held_fcf=claims*quota+hra;held_csm=ordinary_remaining+recovery_component;held_asset=held_fcf+held_csm
        held_details=dict(ordinary_initial_cost_csm=ordinary_initial,ordinary_remaining_cost_csm=ordinary_remaining,recovery_component=recovery_component,held_cost_csm=held_csm,held_fcf=held_fcf,held_asset=held_asset)
    prior=q['prior_basis'];shape(prior,{'liability','acquisition_asset','held_asset'},'prior_shape')
    oldL=nn(prior['liability']);oldA=nn(prior['acquisition_asset']);oldH=nn(prior['held_asset'])
    old_equity=cash_total+oldA+oldH-oldL;equity=cash_total+asset+held_asset-liability
    adjustment=oldL-liability+asset-oldA+held_asset-oldH
    if equity-old_equity!=adjustment:fail('transition_equity_identity')
    if route=='full' and t is None and equity!=projected_equity:fail('full_history_equity')
    journals=[dict(account='issued_liability',debit=oldL-liability),dict(account='acquisition_asset',debit=asset-oldA),dict(account='held_asset',debit=held_asset-oldH),dict(account='equity',debit=-adjustment)]
    if sum(x['debit'] for x in journals)!=0:fail('transition_journal')
    return dict(status='conditional_complete',reason='finite_three_period_zero_rate',posts=False,mutations=[],report=dict(route=route,context=q['context'],origins=origins,
        initial=dict(expected_claims=initial_claims,ra=initial_ra,acquisition_adjustment=groupacq,csm=initial_csm,loss_component=initial_loss),
        transition=dict(cash=cash_total,fcf=fcf,csm=csm,loss_component=loss,liability=liability,acquisition_asset=asset,held_asset=held_asset,held_cost_csm=held_csm,held_fcf=held_fcf,loss_recovery=recovery_component,equity=equity,oci=Q(0)),
        held=held_details,prior_equity=old_equity,equity_adjustment=adjustment,transition_journals=journals,transition_cash_flow=Q(0),known_acquisition_cash=cash['acquisition_paid'],
        full_history_profit=initial_profit+service_profit if route=='full' and t is None else None,
        missing_information_policy='only_explicit_C14D_C16C_prescribed_measurements',limits=['nonparticipating','three equal service periods','zero supported rates','no OCI','supplied valuations/classification']))
