from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy
import importlib.util,json,re
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('debt_scope_helpers',H.parent/'acquisition-debt-relationship-20261027/reference.py')
h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
PROFILE='ConditionalAcquisitionTransactionPartition/1';FLAGS=h.FLAGS
ROLES=['acquisition_consideration','debt_settlement','acquisition_cost','other_separate']
KINDS={'cash_transfer':set(ROLES),'debt_claim_settlement':{'debt_settlement'},'service_fee':{'acquisition_cost'},'other_separate_transfer':{'other_separate'}}
def fmt(v):v=F(v);return str(v.numerator)+'/'+str(v.denominator)
def number(v):
    h.need(isinstance(v,str) and len(v)<70 and re.fullmatch(r'(0|[1-9][0-9]*)/[1-9][0-9]*',v),'canonical_nonnegative_amount')
    q=F(v);h.need(fmt(q)==v,'canonical_nonnegative_amount');return q
def derive(request):
    try:
        h.need(len(json.dumps(request,allow_nan=False))<150000,'request_size')
        h.fields(request,['profile','payload','expected_payload_sha256'],'envelope');h.need(request['profile']==PROFILE,'profile')
        p=request['payload'];h.need(h.digest(p)==request['expected_payload_sha256'],'payload_binding')
        h.fields(p,['declaration','source','evidence_sha256'],'payload');d=p['declaration']
        h.fields(d,['context','currency','unit','inventory','components','inventory_coverage','allocation_assessment'],'declaration')
        c=d['context'];h.fields(c,['subject','actor','at','cutoff'],'context')
        h.text(c['subject'],'subject');h.text(c['actor'],'actor');h.need(h.moment(c['at'])<=h.moment(c['cutoff']),'date_order')
        h.need(isinstance(d['currency'],str) and re.fullmatch('[A-Z]{3}',d['currency']),'currency');h.need(d['unit']=='currency_unit','unit')
        ids=d['inventory'];h.need(isinstance(ids,list) and 0<len(ids)<=16,'inventory_bound')
        for key in ids:h.need(isinstance(key,str) and re.fullmatch('[a-z][a-z0-9_]{0,39}',key),'component_id')
        h.need(len(ids)==len(set(ids)),'duplicate_inventory')
        rows=d['components'];h.need(isinstance(rows,list) and len(rows)==len(ids),'component_count')
        found=[];deps=[];sums={k:F(0) for k in ROLES}
        for r in rows:
            h.fields(r,['id','kind','role','amount','rationale'],'component');h.need(r['id'] in ids,'undeclared_component')
            found.append(r['id']);h.text(r['rationale'],'component_rationale')
            h.need(r['kind'] in KINDS,'component_kind');h.need(r['role'] in ROLES+['unknown'],'component_role')
            if r['role']!='unknown':h.need(r['role'] in KINDS[r['kind']],'kind_role_mismatch')
            else:deps.append('component_role:'+r['id'])
            if r['amount'] is None:deps.append('component_amount:'+r['id'])
            else:
                value=number(r['amount'])
                if r['role']!='unknown':sums[r['role']]+=value
        h.need(len(found)==len(set(found)) and set(found)==set(ids),'complete_unique_components')
        for k in ['inventory_coverage','allocation_assessment']:
            h.need(d[k] in ['supplied_complete','unresolved'],'assertion_'+k)
            if d[k]=='unresolved':deps.append(k)
        s=p['source'];h.fields(s,['text','rationale','subject','actor','at','available_at','declaration_sha256'],'source')
        h.text(s['text'],'source_text');h.text(s['rationale'],'source_rationale')
        h.need(s['subject']==c['subject'] and s['actor']==c['actor'],'source_context')
        h.need(h.moment(s['at'])==h.moment(c['at']),'source_date')
        h.need(s['declaration_sha256']==h.digest(d),'declaration_source_binding');h.need(p['evidence_sha256']==h.digest(s),'evidence_binding')
        unavailable=False
        if s['available_at'] is None:deps.append('source_availability_unknown');unavailable=True
        elif h.moment(s['available_at'])>h.moment(c['cutoff']):deps.append('source_after_cutoff');unavailable=True
        out=dict(profile=PROFILE,**FLAGS,request_sha256=h.digest(request),scope_assessment='supplied_assertions_only',
          declaration=deepcopy(d),source=deepcopy(s),debt_as_prior_equity=False,goodwill=None,journals=[],report=None)
        totals={k:fmt(v) for k,v in sums.items()}
        if deps:return dict(out,status='unresolved',dependencies=sorted(deps),known_partial_totals={} if unavailable else totals,partition_total=None,request=deepcopy(request))
        return dict(out,status='conditional_partition',dependencies=['actual_inventory_and_allocation','actual_measurements_and_period_authority',
          'control_business_and_preexisting_debt_analysis','acquired_basis_tax_and_reports'],totals=totals,
          partition_total=fmt(sum(sums.values())),acquisition_consideration=totals['acquisition_consideration'],
          scope='Arithmetic partition of supplied component measurements only; not goodwill or actual acquisition accounting.')
    except Exception as exc:return dict(profile=PROFILE,status='invalid',**FLAGS,reason=str(exc)[:300] or type(exc).__name__)
