"""Preserve complete conditional acquisition views across one dated revision."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import importlib.util,json
H=Path(__file__).resolve().parent;R=H.parents[2];D=H.parent/'acquisition-consideration-20261027'
spec=importlib.util.spec_from_file_location('revision_worksheet',D/'reference.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w);h=w.h
PROFILE='ConditionalAcquisitionRevisionView/4';FLAGS=deepcopy(w.FLAGS)
FIELDS=['equipment','deferred_tax','expense_adjustment','tax_release']
def amounts(b):
    p=b['payload'];items={i['id']:i for i in p['acquired_items']}
    return dict(equipment=items['equipment']['recognised_balance'],deferred_tax=items['deferred_tax']['recognised_balance'],expense_adjustment=p['expense_adjustment'],tax_release=p['tax_release'])
def scrub(b):
    r=deepcopy(b);r.pop('expected_payload_sha256');p=r['payload']
    p['expense_adjustment']=p['tax_release']=None
    for item in p['acquired_items']:
        if item['id'] in ['equipment','deferred_tax']:item['recognised_balance']=None
    return r
def rebound(b,query):
    result=deepcopy(b);s=result['payload']['symbolic_request'];g=s['payload']['scope_request'];hr=g['history_request']
    h.need(hr['actor']==query['actor'],'single_actor_profile')
    hr['cutoff']=query['cutoff'];g['expected_history_sha256']=h.digest(hr)
    s['expected_payload_sha256']=h.digest(s['payload']);result['expected_payload_sha256']=h.digest(result['payload'])
    return result
def view(body):
    try:
        for p,d in json.loads((D/'attempt-01/source-lock.json').read_text()).items():h.need(sha256((R/p).read_bytes()).hexdigest()==d,'worksheet_dependency:'+p)
        h.need(len(json.dumps(body,allow_nan=False))<800000,'request_size')
        h.fields(body,['profile','payload','expected_payload_sha256'],'envelope');h.need(body['profile']==PROFILE,'profile')
        p=body['payload'];h.need(h.digest(p)==body['expected_payload_sha256'],'payload_binding')
        h.fields(p,['original','revised','revision','sources','query'],'payload')
        q=p['query'];h.fields(q,['actor','cutoff'],'query');h.text(q['actor']);cutoff=h.moment(q['cutoff'])
        r=p['revision'];h.fields(r,['original_sha256','revised_sha256','subject','source_sha256','effective_at','discovered_at','period_end_exclusive','provisional','disposition','available_at','dependent_adjustments','premise'],'revision')
        h.need(h.digest(p['original'])==r['original_sha256'],'original_binding');h.need(h.digest(p['revised'])==r['revised_sha256'],'revised_binding')
        h.text(r['premise']);h.need(type(p['sources']) is dict and len(p['sources'])==1,'one_source')
        h.need(r['source_sha256'] in p['sources'],'source_binding')
        source=p['sources'][r['source_sha256']];h.text(source);h.need(h.source_digest(source)==r['source_sha256'],'source_identity')
        sr=p['original']['payload']['symbolic_request']['payload'];hr=sr['scope_request']['history_request']
        h.need(r['subject']==hr['subject'],'subject');h.need(q['actor']==hr['actor'],'single_actor_profile')
        h.need(scrub(p['original'])==scrub(p['revised']),'unsupported_changed_field')
        h.need(type(r['provisional']) is bool,'provisional_boolean')
        h.need(r['disposition'] in ['acquisition_date_information','later_event','unresolved'],'revision_disposition')
        effective=h.moment(r['effective_at']);acq=h.moment(sr['acquisition']['at']);discovered=h.moment(r['discovered_at']);end=h.moment(r['period_end_exclusive'])
        h.need(acq==h.moment('2025-07-01T00:00:00Z'),'fixed_calendar_profile')
        h.need(acq<end<=h.moment('2026-07-01T00:00:00Z'),'measurement_period_limit')
        h.need(discovered>=acq,'discovery_before_acquisition')
        h.fields(r['available_at'],[q['actor']],'availability')
        available=r['available_at'][q['actor']]
        if available is not None:h.need(h.moment(available)>=discovered,'availability_before_discovery')
        old,new=amounts(p['original']),amounts(p['revised']);a=r['dependent_adjustments'];h.need(type(a) is list and len(a)==4,'dependent_adjustments_population')
        indexed={x.get('field'):x for x in a};h.need(set(indexed)==set(FIELDS),'dependent_adjustments_fields')
        for field,item in indexed.items():
            h.fields(item,['field','before','after','disposition','reason'],'dependent_adjustment');h.text(item['reason'])
            h.need(item['before']==old[field] and item['after']==new[field],'dependent_amount_binding:'+field)
            h.need(item['disposition']==('changed' if old[field]!=new[field] else 'reviewed_unchanged'),'dependent_disposition:'+field)
        h.need(old['equipment']!=new['equipment'],'no_measurement_change')
        original_request=rebound(p['original'],q);revised_request=rebound(p['revised'],q)
        original=w.report(original_request)
        h.need(original['status']=='conditional_worksheet','original_worksheet:'+original.get('reason','invalid'))
        common=dict(profile=PROFILE,**FLAGS,request_sha256=h.digest(body),original_submission=deepcopy(p['original']),revised_submission=deepcopy(p['revised']),revision=deepcopy(r),sources=deepcopy(p['sources']),query=deepcopy(q))
        alternatives=[dict(id='original',request=original_request,result=original)]
        # Future unavailable evidence cannot alter even the reported eligibility of an earlier actor view.
        if discovered>cutoff:
            return dict(**common,status='original_view',selected='original',reason='revision_not_yet_discovered',alternatives=alternatives[:1])
        if available is not None and h.moment(available)>cutoff:
            return dict(**common,status='original_view',selected='original',reason='revision_not_yet_available',alternatives=alternatives[:1])
        reasons=[]
        if effective!=acq:reasons.append('different_effective_date')
        if not r['provisional']:reasons.append('not_provisional')
        if discovered>=end:reasons.append('outside_measurement_period')
        if r['disposition']=='later_event':reasons.append('later_event_requires_other_method')
        if reasons and available is not None:
            return dict(**common,status='other_method_required',selected='original',reason=','.join(reasons),alternatives=alternatives)
        if not reasons:
            revised=w.report(revised_request)
            if revised['status']!='conditional_worksheet':
                return dict(**common,status='unresolved_candidate_method' if available is None else 'candidate_method_required',selected=None,reason='revised_worksheet:'+revised.get('reason','invalid'),alternatives=alternatives,held_candidate=dict(request=revised_request,result=revised),availability='unknown' if available is None else 'available',scope='Original remains preserved; no supported revised financial result is available.')
            alternatives.append(dict(id='revised',request=revised_request,result=revised))
        if available is None:
            if reasons:
                return dict(**common,status='unresolved_availability_other_method',selected='original',reason=','.join(reasons),alternatives=alternatives[:1],availability='unknown',conditional_requirement='If the actor has received this evidence, its supplied disposition requires another method; no retrospective revised worksheet is eligible.')
            return dict(**common,status='unresolved_views',selected=None,reason='revision_availability_unknown',alternatives=alternatives)
        if reasons:return dict(**common,status='other_method_required',selected='original',reason=','.join(reasons),alternatives=alternatives[:1])
        if r['disposition']=='unresolved':return dict(**common,status='unresolved_views',selected=None,reason='revision_disposition_unknown',alternatives=alternatives)
        return dict(**common,status='conditional_revised_view',selected='revised',reason='supplied_eligible_measurement_information',alternatives=alternatives,scope='One conditional revision under supplied provisional/acquisition-date premises; no actual recognition or overwrite.')
    except Exception as exc:return dict(profile=PROFILE,status='invalid',**FLAGS,reason=str(exc)[:350] or type(exc).__name__)
