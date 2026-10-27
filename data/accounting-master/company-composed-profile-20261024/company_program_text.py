"""Named line syntax for the closed retained-company composition."""
import shlex
from company_program import validate,schema

def render(body):
    validate(body)
    def line(command,values):return ' '.join([command]+[shlex.quote(str(v)) for v in values])+';'
    p=schema()['properties'];out=[line('company_program',[body['profile'],body['name']])]
    for kind in ['source','context','period']:
        out.append(line(kind,[body[kind][k] for k in p[kind]['properties']]))
    out.append(line('return_component',[body['return_module_sha256']]))
    for cap in body['capabilities']:out.append(line('capability',[cap['id'],cap['implementation_sha256']]))
    for e in body['events']:
        out.append(line('event',[e[k] for k in ['id','source_pointer','event_sha256','capability']]))
        for k,v in e['review_findings'].items():
            out.append(line('review',[e['id'],k,'true' if v is True else 'false' if v is False else v]))
    for kind in ['report','carry']:out.append(line(kind,[body[kind][k] for k in p[kind]['properties']]))
    out.append('end_program;');return '\n'.join(out)+'\n'

def lower(text):
    if type(text) is not str:raise ValueError('text required')
    p=schema()['properties'];body=None;ended=False;events={}
    for number,line in enumerate(text.splitlines(),1):
        if not line.strip():continue
        try:
            if ended or not line.rstrip().endswith(';'):raise ValueError('terminated declaration required')
            tokens=shlex.split(line.rstrip()[:-1],comments=False,posix=True)
            if not tokens:raise ValueError('empty declaration')
            kind,*args=tokens
            if body is None:
                if kind!='company_program' or len(args)!=2:raise ValueError('company header')
                body={'profile':args[0],'name':args[1],'capabilities':[],'events':[]};continue
            if kind=='end_program':
                if args:raise ValueError('end arity')
                ended=True;continue
            if kind in ['source','context','period','report','carry']:
                keys=list(p[kind]['properties'])
                if kind in body or len(args)!=len(keys):raise ValueError('declaration arity or duplicate')
                body[kind]=dict(zip(keys,args))
            elif kind=='return_component':
                if len(args)!=1 or 'return_module_sha256' in body:raise ValueError('component declaration')
                body['return_module_sha256']=args[0]
            elif kind=='capability':
                if len(args)!=2:raise ValueError('capability declaration')
                body['capabilities'].append(dict(zip(['id','implementation_sha256'],args)))
            elif kind=='event':
                if len(args)!=4 or args[0] in events:raise ValueError('event declaration')
                e=dict(zip(['id','source_pointer','event_sha256','capability'],args));e['review_findings']={}
                events[e['id']]=e;body['events'].append(e)
            elif kind=='review':
                if len(args)!=3 or args[0] not in events:raise ValueError('review event reference')
                e=events[args[0]]['review_findings']
                if args[1] in e or args[2] not in ['true','false','unknown']:raise ValueError('review value or duplicate')
                e[args[1]]={'true':True,'false':False,'unknown':'unknown'}[args[2]]
            else:raise ValueError('unknown declaration')
        except Exception as exc:raise ValueError('line '+str(number)+': '+str(exc)) from exc
    if body is None or not ended:raise ValueError('incomplete program')
    return validate(body)
