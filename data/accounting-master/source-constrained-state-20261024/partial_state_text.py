"""Closed line syntax; parsed as data, never shell-executed."""
import shlex
from partial_state import validate,CONTEXT_KEYS

def line(kind,values):return ' '.join([kind]+[shlex.quote(str(v)) for v in values])+';'

def render(body):
    validate(body)
    out=[line('partial_company',[body['profile'],body['name']])]
    out.append(line('source',[body['source'][k] for k in ['target','view','readiness_request_sha256','readiness_result_sha256']]))
    for p in body['periods']:
        r=p['source_anchor'];out.append(line('period',[p['id'],p['kind'],r['kind'],r['schema'],r['digest'],p['source_period'],p['start'],p['end_exclusive']]))
    for a in body['assumptions']:
        out.append(line('rounding_assumption',[a[k] for k in ['id','rule','quantum','provenance','disposition']]))
    for b in body['bindings']:
        r=b['observation_ref'];out.append(line('snapshot',[b['id'],r['kind'],r['schema'],r['digest'],b['period_id'],b['measurement_date']]+[b['context'][k] for k in CONTEXT_KEYS]))
        if b['interpretation']['mode']=='assumed_rounding':out.append(line('use_rounding',[b['id'],b['interpretation']['assumption_id']]))
    for key in body['requirement_ids']:out.append(line('requirement',[key]))
    out.append('end_partial_company;');return '\n'.join(out)+'\n'

def lower(text):
    if type(text) is not str:raise ValueError('text required')
    body=None;ended=False;bindings={}
    for index,raw in enumerate(text.splitlines(),1):
        if not raw.strip():continue
        try:
            if ended or not raw.rstrip().endswith(';'):raise ValueError('terminated declaration required')
            tokens=shlex.split(raw.rstrip()[:-1],comments=False,posix=True)
            if not tokens:raise ValueError('empty declaration')
            kind,*args=tokens
            if body is None:
                if kind!='partial_company' or len(args)!=2:raise ValueError('header')
                body={'profile':args[0],'name':args[1],'periods':[],'bindings':[],'assumptions':[],'requirement_ids':[]};continue
            if kind=='end_partial_company':
                if args:raise ValueError('end arity')
                ended=True;continue
            if kind=='source':
                if len(args)!=4 or 'source' in body:raise ValueError('source arity or duplicate')
                body['source']=dict(zip(['target','view','readiness_request_sha256','readiness_result_sha256'],args))
            elif kind=='period':
                if len(args)!=8:raise ValueError('period arity')
                body['periods'].append({'id':args[0],'kind':args[1],
                    'source_anchor':dict(zip(['kind','schema','digest'],args[2:5])),
                    'source_period':args[5],'start':args[6],'end_exclusive':args[7]})
            elif kind=='rounding_assumption':
                if len(args)!=5:raise ValueError('assumption arity')
                body['assumptions'].append(dict(zip(['id','rule','quantum','provenance','disposition'],args)))
            elif kind=='snapshot':
                if len(args)!=12 or args[0] in bindings:raise ValueError('snapshot arity or duplicate')
                b={'id':args[0],'observation_ref':dict(zip(['kind','schema','digest'],args[1:4])),
                    'period_id':args[4],'measurement_date':args[5],'context':dict(zip(CONTEXT_KEYS,args[6:])),
                    'interpretation':{'mode':'display_only','assumption_id':None}}
                bindings[b['id']]=b;body['bindings'].append(b)
            elif kind=='use_rounding':
                if len(args)!=2 or args[0] not in bindings:raise ValueError('rounding target')
                b=bindings[args[0]]
                if b['interpretation']['mode']!='display_only':raise ValueError('duplicate rounding interpretation')
                b['interpretation']={'mode':'assumed_rounding','assumption_id':args[1]}
            elif kind=='requirement':
                if len(args)!=1:raise ValueError('requirement arity')
                body['requirement_ids'].append(args[0])
            else:raise ValueError('unknown declaration')
        except Exception as exc:raise ValueError('line '+str(index)+': '+str(exc)) from exc
    if body is None or not ended:raise ValueError('incomplete partial company')
    return validate(body)
