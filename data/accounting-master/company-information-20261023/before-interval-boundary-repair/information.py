"""Synthetic information selection; never authenticates a historical observation."""
from datetime import datetime,timedelta,timezone
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import sys
from jsonschema import Draft202012Validator,FormatChecker

HERE=Path(__file__).resolve().parent
EXCHANGE=HERE.parent/'company-path-exchanges-20261023'
sys.path.insert(0,str(EXCHANGE))
from exchanges import canonical,digest,closed

EVENTS=['authored','published','ingested','accepted']


def components(path):
    """Partition every authored path field; no timing inferred from fiscal dates."""
    if set(path)!={'profile','name','assumption','initial_year','continuations'}:
        raise ValueError('uncovered path fields')
    result=[{'slot':'header','value':{k:path[k] for k in ['profile','name','assumption']}}]
    result.extend({'slot':'year:'+str(i),'value':y} for i,y in
                  enumerate([path['initial_year']]+path['continuations']))
    return [{'slot':r['slot'],'sha256':digest(r['value'])} for r in result]


def schema():
    sha={'type':'string','pattern':'^[0-9a-f]{64}$'}
    missing=closed({'status':{'const':'unknown'},'reason':{'type':'string','minLength':1}})
    observed=closed({'status':{'const':'observed_synthetic'},'observation_sha256':sha})
    event={'oneOf':[missing,observed]}
    declaration=closed({'slot':{'type':'string','pattern':'^(header|year:[0-9]+)$'},
        'component_sha256':sha,'events':closed({k:event for k in EVENTS})})
    return closed({'profile':{'const':'CompanyInformationDraft/1'},
        'exchange_sha256':sha,'path_sha256':sha,'evidence_class':{'const':'authored_synthetic'},
        'declarations':{'type':'array','minItems':2,'items':declaration}})


def observation_schema():
    return closed({'profile':{'const':'SyntheticInformationObservation/1'},
        'component_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},
        'event':{'enum':EVENTS},'audience':{'enum':['public','internal']},
        'time':{'type':'string'},'precision':{'enum':['utc_instant','calendar_day_utc']},
        'provenance':{'const':'authored_test_clock_not_historical_evidence'}})


def interval(observation):
    value=observation['time']
    if observation['precision']=='calendar_day_utc':
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):raise ValueError('calendar day format')
        start=datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
        return start,start+timedelta(days=1)
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z',value):
        raise ValueError('UTC instant format')
    instant=datetime.fromisoformat(value[:-1]+'+00:00')
    return instant,instant


def select(path,declaration,observations,trusted_observation_hashes,
           exchange_sha256,source_view,mode,cutoff=None):
    """source_view is a trusted local callback, never a status from the packet."""
    try:
        Draft202012Validator(schema(),format_checker=FormatChecker()).validate(declaration)
        if declaration['exchange_sha256']!=exchange_sha256:raise ValueError('exchange identity')
        if declaration['path_sha256']!=digest(path):raise ValueError('path identity')
        expected=components(path);items=declaration['declarations']
        if len({x['slot'] for x in items})!=len(items):raise ValueError('duplicate component slot')
        supplied={x['slot']:x['component_sha256'] for x in items}
        if supplied!={x['slot']:x['sha256'] for x in expected}:raise ValueError('exact component coverage')
        if mode not in ['archival_exploration','investor_information','system_as_of']:
            raise ValueError('information mode')
        at=None
        if mode=='archival_exploration':
            if cutoff is not None:raise ValueError('archival cutoff')
        else:
            at=interval({'time':cutoff,'precision':'utc_instant'})[0]
        evidence={};chronology={};unknown=[];late=[];eligible=[]
        for item in items:
            clocks={}
            for event,ref in item['events'].items():
                if ref['status']=='unknown':continue
                h=ref['observation_sha256']
                if h not in observations:raise ValueError('observation bytes missing')
                observation=observations[h]
                if digest(observation)!=h:raise ValueError('observation digest mismatch')
                Draft202012Validator(observation_schema()).validate(observation)
                if observation['event']!=event or observation['component_sha256']!=item['component_sha256']:
                    raise ValueError('observation component or event mismatch')
                # Untrusted asserted times cannot validate chronology or eligibility.
                if h in trusted_observation_hashes:clocks[event]=interval(observation)
                else:interval(observation)
            # Reject only an impossible ordering, not overlapping day intervals.
            ambiguous=[]
            for before,after in [('authored','published'),('authored','ingested'),('ingested','accepted')]:
                if before in clocks and after in clocks:
                    first,last=clocks[before],clocks[after]
                    if first[0]>last[1]:
                        raise ValueError('impossible observation chronology')
                    if first[1]>last[0] or first[0]==last[0]:
                        ambiguous.append((before,after))
            evidence[item['slot']]=clocks;chronology[item['slot']]=ambiguous
        source=source_view(mode,cutoff)
        if source.get('status')=='invalid':raise ValueError('source timing invalid')
        if mode=='archival_exploration':
            if source.get('status')!='eligible_synthetic':raise ValueError('archival source unavailable')
            return {'status':'archival_synthetic','mode':mode,'cutoff':None,
                'source_timing':source,'component_count':len(items),'temporal_admission':False,
                'real_world_admission':False,'forecast_admission':False}
        required=['authored','published'] if mode=='investor_information' else ['authored','ingested','accepted']
        for item in items:
            ambiguous_pairs=chronology[item['slot']]
            needed_pairs=[('authored','published')] if mode=='investor_information' else [('authored','ingested'),('ingested','accepted')]
            for before,after in needed_pairs:
                if (before,after) in ambiguous_pairs:
                    unknown.append({'slot':item['slot'],'event':before+'<'+after,
                                    'reason':'CHRONOLOGY_ORDER_UNRESOLVED'})
            for event in required:
                ref=item['events'][event];entry={'slot':item['slot'],'event':event}
                if ref['status']=='unknown':
                    unknown.append(dict(entry,reason='MISSING_OBSERVATION'));continue
                h=ref['observation_sha256'];observation=observations[h]
                if h not in trusted_observation_hashes:
                    unknown.append(dict(entry,reason='UNTRUSTED_OBSERVATION'));continue
                if event=='published' and observation['audience']!='public':
                    unknown.append(dict(entry,reason='PUBLIC_AVAILABILITY_NOT_ESTABLISHED'));continue
                start,end=evidence[item['slot']][event]
                if at<start:late.append(dict(entry,reason='AFTER_INFORMATION_CUTOFF'))
                elif start!=end and at<end:unknown.append(dict(entry,reason='TIME_PRECISION_UNRESOLVED'))
                else:eligible.append(entry)
        status=('ineligible' if late or source.get('status')=='ineligible' else
                'unresolved' if unknown or source.get('status')=='unresolved' else 'eligible_synthetic')
        if source.get('status') not in ['ineligible','unresolved','eligible_synthetic']:
            raise ValueError('unrecognized source status')
        return {'status':status,'mode':mode,'cutoff':cutoff,'source_timing':source,
            'component_count':len(items),'eligible':eligible,'unavailable':late,'unresolved':unknown,
            'temporal_admission':status=='eligible_synthetic','real_world_admission':False,
            'forecast_admission':False,'scope':'synthetic temporal selection only'}
    except Exception as exc:
        return {'status':'invalid','reason':'information_semantics',
                'detail':type(exc).__name__+':'+str(exc).splitlines()[0][:400]}


def query(exchange,raw,path_name,declaration,observations,trusted_observation_hashes,
          trusted_exchange_sha256,trusted_validate,source_view,mode,cutoff=None):
    """Admit only a member of a previously locked and semantically replayed exchange."""
    try:
        if digest(exchange)!=trusted_exchange_sha256:raise ValueError('trusted exchange lock')
        admitted=trusted_validate(exchange,raw,True)
        if admitted.get('status')!='validated_synthetic_exchange' or admitted.get('verification_level')!='trusted_local_semantic_replay':
            raise ValueError('exchange semantic admission')
        records=exchange['record_registry'];root=records[exchange['root_ref']['digest']]['body']
        matches=[records[r['digest']]['body'] for r in root['path_refs'] if records[r['digest']]['body']['name']==path_name]
        if len(matches)!=1:raise ValueError('path membership')
        path=json.loads(raw[matches[0]['path_blob']['digest']])
        return select(path,declaration,observations,trusted_observation_hashes,
                      trusted_exchange_sha256,source_view,mode,cutoff)
    except Exception as exc:
        return {'status':'invalid','reason':'exchange_boundary',
                'detail':type(exc).__name__+':'+str(exc).splitlines()[0][:400]}
