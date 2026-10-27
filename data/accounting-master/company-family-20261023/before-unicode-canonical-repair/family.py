"""Bounded unweighted scenario-family authoring over the protected company path."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import shlex
import sys
from jsonschema import Draft202012Validator, FormatChecker

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'company-text-20261023'))
import frontend

PROFILE='CompanyScenarioFamilyDraft/1'
def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(value): return sha256(canonical(value)).hexdigest()
def closed(properties):
    return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}
def schema():
    text={'type':'string','minLength':1}; hash_rule={'type':'string','pattern':'^[0-9a-f]{64}$'}
    period=deepcopy(frontend.INITIAL['properties']['period'])
    return dict(closed({'profile':{'const':PROFILE},'name':text,
        'meaning':{'const':'authored_exogenous_scenarios'},'weighting':{'const':'unweighted'},
        'coverage':{'const':'authored_members_only'},
        'common':closed({'source_sha256':hash_rule,'opening_sha256':hash_rule,
                         'periods':{'type':'array','minItems':2,'items':period}}),
        'members':{'type':'array','items':closed({'id':text,'path':deepcopy(frontend.SCHEMA)})}}),
        **{'$schema':'https://json-schema.org/draft/2020-12/schema'})

def periods(path): return [deepcopy(y['period']) for y in [path['initial_year']]+path['continuations']]
def opening(path):
    y=path['initial_year']
    return {**{k:deepcopy(y[k]) for k in ['source','opening_digest','context','assets','opening_claims']},
            'facility':{k:deepcopy(y['facility'][k]) for k in ['id','drawn']},
            'debt_principal':y['debt']['principal']}
def common(path):
    frontend.validate(path)
    return {'source_sha256':path['initial_year']['source']['sha256'],
            'opening_sha256':digest(opening(path)),'periods':periods(path)}
def validate(body):
    Draft202012Validator(schema(),format_checker=FormatChecker()).validate(body)
    ids=[m['id'] for m in body['members']]
    if len(ids)!=len(set(ids)): raise ValueError('duplicate member identity')
    dates=body['common']['periods']
    if any(p['start']>=p['end_exclusive'] for p in dates): raise ValueError('nonpositive period')
    if any(a['end_exclusive']!=b['start'] for a,b in zip(dates,dates[1:])):
        raise ValueError('nonconsecutive common periods')
    for member in body['members']:
        frontend.validate(member['path'])
        if digest(common(member['path']))!=digest(body['common']):
            raise ValueError('member differs from common historical opening or horizon: '+member['id'])
    return body

def render(body):
    validate(body)
    def token(value):
        if not isinstance(value,str) or '\n' in value or '\r' in value: raise ValueError('non-line token')
        return shlex.quote(value)
    def line(kind,*args): return ' '.join([kind]+[token(x) for x in args])+';'
    c=body['common']
    out=[line('family',body['profile'],body['name']),line('meaning',body['meaning'],body['weighting'],body['coverage']),
         line('common',c['source_sha256'],c['opening_sha256'])]
    out += [line('period',p['start'],p['end_exclusive']) for p in c['periods']]
    for member in body['members']:
        out += [line('member',member['id']),frontend.render(member['path']).rstrip(), 'end_member;']
    out.append('end_family;')
    return '\n'.join(out)+'\n'

def lower(text):
    if not isinstance(text,str): raise ValueError('text must be a string')
    body=None; current=None; path_lines=[]; ended=False; started_members=False
    for number,raw in enumerate(text.splitlines(),1):
        line=raw.strip()
        if not line: continue
        try:
            if ended: raise ValueError('content after end_family')
            if not line.endswith(';'): raise ValueError('missing semicolon')
            tokens=shlex.split(line[:-1],comments=False,posix=True)
            if not tokens: raise ValueError('empty declaration')
            kind,*args=tokens
            if current is not None:
                if kind=='end_member':
                    if args: raise ValueError('end_member arity')
                    body['members'].append({'id':current,'path':frontend.lower('\n'.join(path_lines)+'\n')})
                    current=None; path_lines=[]
                else: path_lines.append(raw)
                continue
            if body is None:
                if kind!='family' or len(args)!=2: raise ValueError('expected family profile name')
                body={'profile':args[0],'name':args[1],'members':[]}; continue
            if kind=='meaning' and len(args)==3 and 'meaning' not in body and not started_members:
                body.update(zip(['meaning','weighting','coverage'],args))
            elif kind=='common' and len(args)==2 and 'common' not in body and not started_members:
                body['common']={'source_sha256':args[0],'opening_sha256':args[1],'periods':[]}
            elif kind=='period' and len(args)==2 and 'common' in body and not started_members:
                body['common']['periods'].append(dict(zip(['start','end_exclusive'],args)))
            elif kind=='member' and len(args)==1 and 'common' in body and 'meaning' in body:
                started_members=True; current=args[0]
            elif kind=='end_family' and not args: ended=True
            else: raise ValueError('unknown, misplaced or repeated family declaration')
        except ValueError as exc: raise ValueError('line '+str(number)+': '+str(exc)) from exc
    if body is None or current is not None or not ended: raise ValueError('incomplete family/member')
    return validate(body)

FLAGS={'probability_admitted':False,'historical_family_admitted':False,
       'temporal_admission':False,'forecast_admission':False,'exhaustive_scenario_coverage':False}
def execute(body,source,engine):
    try:
        validate(body)
        if sha256(source).hexdigest()!=body['common']['source_sha256']: raise ValueError('source bytes mismatch')
    except Exception as exc:
        return dict(FLAGS,status='invalid',reason='family_input',detail=type(exc).__name__+':'+str(exc).splitlines()[0][:250])
    members=[]
    for member in body['members']:
        run=engine.wire(engine.execute(deepcopy(member['path']),source))
        members.append({'id':member['id'],'path_sha256':digest(member['path']),
                        'result_sha256':digest(run),'status':run['status'],'result':run})
    status=('empty_authored_family' if not members else
            'evaluated_all_members' if all(m['status']=='complete_conditional' for m in members) else
            'evaluated_with_incomplete_members')
    return dict(FLAGS,profile=PROFILE,status=status,family_sha256=digest(body),
                source_sha256=sha256(source).hexdigest(),members=members,
                coverage='authored_members_only',weighting='unweighted')

def verify(body,source,run,engine):
    expected=execute(body,source,engine)
    return expected['status']!='invalid' and digest(expected)==digest(run)

def joint_report(body,source,run,period_start,engine):
    if not verify(body,source,run,engine): return dict(FLAGS,status='invalid',reason='family_replay')
    if period_start not in [p['start'] for p in body['common']['periods']]:
        return dict(FLAGS,status='invalid',reason='outside_authored_horizon')
    members=[]
    for member in run['members']:
        years=member['result'].get('years',[])
        matches=[y for y in years if y['period']['start']==period_start]
        item={'id':member['id'],'path_sha256':member['path_sha256'],
              'result_sha256':member['result_sha256'],'execution_status':member['status']}
        if matches:
            item.update(status=matches[0]['report']['status'],report=deepcopy(matches[0]['report']))
        else:
            stopped=[y for y in member['result'].get('unexecuted',[]) if y['period']['start']==period_start]
            item.update(status='unresolved',reason=stopped[0]['reason'] if stopped else 'member_execution_incomplete',report=None)
        members.append(item)
    return dict(FLAGS,status='empty_authored_family' if not members else 'joint_authored_reports',
                family_sha256=run['family_sha256'],period_start=period_start,members=members,
                weighting='unweighted',coverage='authored_members_only')
