"""Named declaration grammar for the finite statement-context reference."""
import shlex
from statement_context import validate

def line(kind,args):return ' '.join([kind]+[shlex.quote(str(x)) for x in args])+';'

def render(body):
    validate(body)
    out=[line('statement_context',[body['profile'],body['name']])]
    out.append(line('source',[body['source'][k] for k in ['target','view','request_sha256','result_sha256']]))
    for o in body['observations']:
        r=o['observation_ref'];t=o['measurement_time']
        args=[o['alias'],o['collection'],r['kind'],r['schema'],r['digest'],t['kind']]
        args+=([t['at']] if t['kind']=='instant' else [t['start'],t['end_exclusive']])+[o['unit']]
        out.append(line('observation',args))
    for r in body['relations']:
        out.append(line('relation',[r[k] for k in ['id','group','source_pointer','source_record_sha256','kind','comparison']]))
        for side in ['lhs','rhs']:
            for t in r[side]:out.append(line(side,[r['id'],t['alias'],t['coefficient']]))
        for row in r['omitted_source_rows']:out.append(line('omitted',[r['id'],row]))
    for key in body['requirement_ids']:out.append(line('requirement',[key]))
    out.append('end_statement_context;');return '\n'.join(out)+'\n'

def lower(text):
    if type(text) is not str:raise ValueError('text required')
    body=None;ended=False;relations={}
    for i,raw in enumerate(text.splitlines(),1):
        if not raw.strip():continue
        try:
            if ended or not raw.rstrip().endswith(';'):raise ValueError('terminated declaration required')
            tokens=shlex.split(raw.rstrip()[:-1],comments=False,posix=True)
            if not tokens:raise ValueError('empty declaration')
            kind,*args=tokens
            if body is None:
                if kind!='statement_context' or len(args)!=2:raise ValueError('header')
                body={'profile':args[0],'name':args[1],'observations':[],'relations':[],'requirement_ids':[]};continue
            if kind=='end_statement_context':
                if args:raise ValueError('end arity')
                ended=True;continue
            if kind=='source':
                if len(args)!=4 or 'source' in body:raise ValueError('source arity or duplicate')
                body['source']=dict(zip(['target','view','request_sha256','result_sha256'],args))
            elif kind=='observation':
                if len(args) not in [8,9]:raise ValueError('observation arity')
                if args[5]=='instant' and len(args)==8:t={'kind':'instant','at':args[6]}
                elif args[5]=='period' and len(args)==9:t={'kind':'period','start':args[6],'end_exclusive':args[7]}
                else:raise ValueError('measurement time')
                body['observations'].append({'alias':args[0],'collection':args[1],
                    'observation_ref':dict(zip(['kind','schema','digest'],args[2:5])),
                    'measurement_time':t,'unit':args[-1]})
            elif kind=='relation':
                if len(args)!=6 or args[0] in relations:raise ValueError('relation arity or duplicate')
                r=dict(zip(['id','group','source_pointer','source_record_sha256','kind','comparison'],args))
                r.update(lhs=[],rhs=[],omitted_source_rows=[]);relations[r['id']]=r;body['relations'].append(r)
            elif kind in ['lhs','rhs']:
                if len(args)!=3 or args[0] not in relations:raise ValueError('relation operand')
                relations[args[0]][kind].append({'alias':args[1],'coefficient':args[2]})
            elif kind=='omitted':
                if len(args)!=2 or args[0] not in relations:raise ValueError('omission')
                relations[args[0]]['omitted_source_rows'].append(args[1])
            elif kind=='requirement':
                if len(args)!=1:raise ValueError('requirement arity')
                body['requirement_ids'].append(args[0])
            else:raise ValueError('unknown declaration')
        except Exception as exc:raise ValueError('line '+str(i)+': '+str(exc)) from exc
    if body is None or not ended:raise ValueError('incomplete statement context')
    return validate(body)
