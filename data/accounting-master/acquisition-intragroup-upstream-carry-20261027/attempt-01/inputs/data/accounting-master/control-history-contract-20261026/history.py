"""Conditional whole-interval control assertions with exact actor availability."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import importlib.util
import json

H=Path(__file__).resolve().parent;R=H.parents[2]
spec=importlib.util.spec_from_file_location('control_exact_time',R/'data/accounting-master/exact-information-time-20261026/projection.py')
clock=importlib.util.module_from_spec(spec);spec.loader.exec_module(clock)
PROFILE='ConditionalControlIntervalHistory/1'
RECORD='WholeIntervalControlAssertion/1'

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(x):return sha256(canonical(x)).hexdigest()
def source_digest(s):return sha256(s.encode()).hexdigest()
def need(p,message):
    if not p:raise ValueError(message)
def fields(x,keys,name):need(type(x) is dict and set(x)==set(keys),name+'_fields')
def text(x):need(type(x) is str and bool(x.strip()),'text_required')
def moment(x):return clock.instant(x)
def normalized(x):return str(x.numerator)+'/'+str(x.denominator)

def evaluate(body):
    fields(body,['profile','subject','basis','interval','actor','cutoff','records','sources'],'request')
    need(body['profile']==PROFILE,'profile')
    subject=body['subject'];need(type(subject) is list and len(subject)==2,'subject')
    for x in subject:text(x)
    need(subject[0]!=subject[1],'self_control')
    text(body['basis']);text(body['actor']);cut=moment(body['cutoff'])
    fields(body['interval'],['start','end_exclusive'],'query_interval')
    start=moment(body['interval']['start']);end=moment(body['interval']['end_exclusive']);need(start<end,'query_order')
    records=body['records'];sources=body['sources']
    need(type(records) is dict and len(records)<=128,'bounded_records')
    need(type(sources) is dict and len(sources)<=128,'bounded_sources')
    need(len(canonical(body))<=1_000_000,'request_size')
    for h,s in sources.items():text(s);need(source_digest(s)==h,'source_identity')
    times={}
    for h,r in records.items():
        need(digest(r)==h,'record_identity')
        fields(r,['profile','subject','basis','start','end_exclusive','status','coverage','evidence_sha256','available_at','supersedes'],'assertion')
        need(r['profile']==RECORD,'record_profile')
        need(r['subject']==subject and r['basis']==body['basis'],'record_context')
        need(r['status'] in ['yes','no','unknown'],'status')
        need(r['coverage']=='asserted_whole_interval','explicit_coverage_required')
        need(r['evidence_sha256'] in sources,'source_missing')
        a=moment(r['start']);b=moment(r['end_exclusive']);need(a<b,'assertion_order');times[h]=(a,b)
        need(type(r['available_at']) is dict and len(r['available_at'])<=64,'availability_map')
        for actor,at in r['available_at'].items():
            text(actor)
            if at is not None:moment(at)
        need(r['supersedes'] is None or type(r['supersedes']) is str,'parent_type')
    for h in records:
        seen=set();current=h
        while current is not None:
            need(current not in seen,'revision_cycle');seen.add(current)
            need(current in records,'missing_ancestry')
            need(times[current]==times[h],'revision_interval_mismatch')
            current=records[current]['supersedes']
    available=set();unknown=set();future=set()
    for h,r in records.items():
        stamp=r['available_at'].get(body['actor'])
        if stamp is None:unknown.add(h)
        elif moment(stamp)<=cut:available.add(h)
        else:future.add(h)
    ancestors=set()
    for h in available:
        parent=records[h]['supersedes']
        while parent is not None:ancestors.add(parent);parent=records[parent]['supersedes']
    heads=available-ancestors
    # A known available revision replaces its ancestors for this actor. An
    # unknown-availability descendant remains an unresolved competitor.
    unknown-=ancestors
    relevant={h for h in heads|unknown if times[h][0]<end and times[h][1]>start}
    points={start,end}
    for h in relevant:
        a,b=times[h];points.update([max(start,a),min(end,b)])
    points=sorted(points);atoms=[]
    for a,b in zip(points,points[1:]):
        covering=sorted(h for h in heads if times[h][0]<=a and b<=times[h][1])
        uncertain=sorted(h for h in unknown if times[h][0]<=a and b<=times[h][1])
        statuses={records[h]['status'] for h in covering};known=statuses-{'unknown'}
        reasons=[]
        if uncertain:reasons.append('unknown_actor_availability')
        if not covering:reasons.append('no_available_interval_assertion')
        if 'unknown' in statuses:reasons.append('unknown_control_assertion')
        if len(known)>1:reasons.append('conflicting_control_assertions')
        status=next(iter(known)) if not reasons and len(known)==1 else 'unresolved'
        atoms.append(dict(start=normalized(a),end_exclusive=normalized(b),status=status,reasons=reasons,
                          evidence_records=covering,unknown_availability_records=uncertain))
    complete=all(x['status'] in ['yes','no'] for x in atoms)
    transitions=[]
    for left,right in zip(atoms,atoms[1:]):
        if left['status'] in ['yes','no'] and right['status'] in ['yes','no'] and left['status']!=right['status']:
            transitions.append(dict(at=right['start'],kind='gain' if right['status']=='yes' else 'loss',
                                    evidence_records=sorted(set(left['evidence_records']+right['evidence_records']))))
    return dict(profile=PROFILE,status='conditionally_covered' if complete else 'partial',
                source_admission=False,accounting_admission=False,posting_authorized=False,
                time_axis=clock.AXIS,subject=deepcopy(subject),basis=body['basis'],actor=body['actor'],cutoff=body['cutoff'],
                atoms=atoms,conditional_transitions=transitions,available_heads=sorted(heads),
                excluded_future=sorted(future),continuous_control_under_assertions=complete and all(x['status']=='yes' for x in atoms),
                unresolved_atom_indices=[i for i,x in enumerate(atoms) if x['status']=='unresolved'],
                scope='Conditional coverage under supplied whole-interval assertions; source completeness and accounting control are not adjudicated.')
