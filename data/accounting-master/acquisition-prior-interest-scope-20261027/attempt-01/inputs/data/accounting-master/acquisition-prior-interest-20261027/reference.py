"""Typed prior equity and OCI expressions; no measured report or legal postings."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
from copy import deepcopy
import importlib.util,json,re
H=Path(__file__).resolve().parent;R=H.parents[2];S=H.parent/'acquisition-symbolic-20261027'
sp=importlib.util.spec_from_file_location('prior_symbolic_base',S/'reference.py');base=importlib.util.module_from_spec(sp);sp.loader.exec_module(base)
h=base.h;FLAGS=base.FLAGS;PROFILE='ConditionalPriorEquityExpressions/1'
def derive(body):
    try:
        h.need(len(json.dumps(body,allow_nan=False))<500000,'request_size')
        h.fields(body,['profile','payload','expected_payload_sha256'],'envelope');h.need(body['profile']==PROFILE,'profile');p=body['payload']
        h.need(h.digest(p)==body['expected_payload_sha256'],'payload_binding')
        h.fields(p,['base_request','base_result_sha256','source_lock_sha256','prior','carrying','cumulative_oci','source'],'payload')
        lock=H/'predecessor-lock.json';h.need(sha256(lock.read_bytes()).hexdigest()==p['source_lock_sha256'],'source_lock_binding')
        for name,d in json.loads(lock.read_text()).items():h.need(sha256((R/name).read_bytes()).hexdigest()==d,'protected_dependency:'+name)
        old=base.derive(p['base_request']);h.need(old['status'] in ['conditional_expressions','unresolved'],'base_status')
        h.need(h.digest(old)==p['base_result_sha256'],'base_result_binding')
        bp=p['base_request']['payload'];hr=bp['scope_request']['history_request'];acq=bp['acquisition'];source=p['source']
        h.fields(source,['text','subject','actor','available_at'],'source');h.text(source['text']);sid=h.digest(source)
        h.need(source['subject']==hr['subject'] and source['actor']==hr['actor'],'source_context')
        deps=[]
        if source['available_at'] is None:deps.append('source_availability_unknown')
        elif h.moment(source['available_at'])>h.moment(hr['cutoff']):deps.append('source_after_cutoff')
        prior=p['prior'];h.fields(prior,['kind','fraction','classification','equity_eligible','irrevocable_election','hedging','oci_treatment','separate_transactions','separate_books','evidence_sha256'],'prior')
        h.need(prior['evidence_sha256']==sid,'prior_source_binding')
        h.need(prior['kind']==bp['prior_interest']['kind'],'prior_kind_binding')
        fraction=base.scalar(prior['fraction']);current=base.scalar(bp['ownership']['fraction'])
        h.need(0<fraction<current,'prior_fraction')
        h.need(prior['classification'] in ['fvtpl','equity_fvoci','equity_method','unresolved'],'classification')
        for flag in ['equity_eligible','irrevocable_election']:h.need(type(prior[flag]) in [bool,type(None)],'boolean_or_unknown')
        h.need(prior['hedging'] in ['none_stipulated','requires_method'],'hedging')
        h.need(prior['separate_transactions'] in ['none_stipulated','requires_method'],'separate_transactions')
        h.need(prior['separate_books']=='unresolved','separate_books_not_derived')
        if prior['kind']!='equity':deps.append('prior_interest_and_separate_transaction_analysis:'+prior['kind'])
        if old['status']=='unresolved':deps.extend('base:'+x for x in old['dependencies'])
        if prior['classification'] in ['equity_method','unresolved']:deps.append('prior_classification_method:'+prior['classification'])
        if prior['hedging']!='none_stipulated':deps.append('hedging_method')
        if prior['separate_transactions']!='none_stipulated':deps.append('separate_transaction_analysis')
        names={v['symbol'] for v in bp['amounts'].values()}
        for field,kind in [('carrying','prior_carrying_before_update'),('cumulative_oci','prior_cumulative_oci')]:
            d=p[field];h.fields(d,['symbol','kind','currency','unit','at','basis','evidence_sha256','zero_stipulated'],field)
            h.need(type(d['symbol']) is str and re.fullmatch('[A-Za-z][A-Za-z0-9_]{0,31}',d['symbol']) is not None,'symbol')
            h.need(d['symbol'] not in names,'duplicate_symbol');names.add(d['symbol'])
            h.need(d['kind']==kind,'descriptor_kind:'+field)
            h.need(d['currency']==acq['currency'] and d['unit']==acq['unit'],'descriptor_units:'+field)
            h.need(h.moment(d['at'])==h.moment(acq['at']),'descriptor_date:'+field)
            h.need(d['evidence_sha256']==sid,'descriptor_source:'+field);h.text(d['basis'])
            h.need(type(d['zero_stipulated']) is bool,'zero_premise')
        cls=prior['classification'];treatment=prior['oci_treatment']
        if cls=='fvtpl':h.need(treatment=='none' and p['cumulative_oci']['zero_stipulated'],'fvtpl_oci_must_be_zero')
        if cls=='equity_fvoci':
            h.need(treatment in ['retain_reserve','transfer_within_equity'],'equity_fvoci_no_recycling')
            if prior['equity_eligible'] is not True or prior['irrevocable_election'] is not True:deps.append('fvoci_eligibility_or_election')
        result=dict(profile=PROFILE,**FLAGS,request_sha256=h.digest(body),base_result=deepcopy(old),prior=deepcopy(prior),descriptors=deepcopy({k:p[k] for k in ['carrying','cumulative_oci']}),source=deepcopy(source))
        if deps:return dict(result,status='unresolved',dependencies=sorted(set(deps)),expressions={})
        # Acquisition excess retains its original fair-value term exactly once.
        fv={bp['amounts']['P']['symbol']:F(1)};car={} if p['carrying']['zero_stipulated'] else {p['carrying']['symbol']:F(1)}
        oci={} if p['cumulative_oci']['zero_stipulated'] else {p['cumulative_oci']['symbol']:F(1)}
        gain=base.plus((1,fv),(-1,car));cumulative=base.plus((1,oci),(1,gain))
        zero={};pl=gain if cls=='fvtpl' else zero;other=gain if cls=='equity_fvoci' else zero
        transfer=cumulative if cls=='equity_fvoci' and treatment=='transfer_within_equity' else zero
        reserve=cumulative if cls=='equity_fvoci' and treatment=='retain_reserve' else zero
        expressions=deepcopy(old['expressions'])
        for key,value in dict(prior_remeasurement=gain,prior_parent_profit_before_tax=pl,prior_parent_oci_before_tax=other,prior_oci_recycling_to_profit=zero,prior_transfer_to_retained=transfer,prior_oci_reserve_after=reserve,prior_nci_effect=zero,prior_remeasurement_cash=zero).items():expressions[key]=base.serial(value)
        return dict(result,status='conditional_prior_expressions',expressions=expressions,dependencies=sorted(set(old['dependencies']+['unmeasured:'+p['carrying']['symbol'],'prior_tax_method','separate_books_method','complete_worksheet_and_report']+([] if p['cumulative_oci']['zero_stipulated'] else ['unmeasured:'+p['cumulative_oci']['symbol']]))),scope='Conditional pretax parent-attributed prior-equity expressions only; no legal journals,measured consideration,tax or financial report.')
    except Exception as exc:return dict(profile=PROFILE,status='invalid',**FLAGS,reason=str(exc)[:350] or type(exc).__name__)
