"""Named line-oriented declarations; no include, expression execution or I/O."""
import shlex
from return_schema import validate, schema, PROFILE, ROLES


def fields(tokens, rule):
    names=list(rule['properties'])
    if len(tokens)!=len(names):raise ValueError('declaration arity')
    out={}
    for name,token in zip(names,tokens):
        shape=rule['properties'][name]
        if 'oneOf' in shape and any(r.get('type')=='boolean' for r in shape['oneOf']):
            if token not in ['true','false','unknown']:raise ValueError('Boolean token')
            out[name]={'true':True,'false':False,'unknown':'unknown'}[token]
        else:out[name]=token
    return out


def lower(text):
    if type(text) is not str:raise ValueError('text required')
    props=schema()['properties'];body=None;ended=False;seen=set()
    event_rules={r['properties']['kind']['const']:r for r in props['events']['items']['oneOf']}
    for number,line in enumerate(text.splitlines(),1):
        line=line.strip()
        if not line:continue
        try:
            if ended or not line.endswith(';'):raise ValueError('terminated declaration required')
            tokens=shlex.split(line[:-1],comments=False,posix=True)
            if not tokens:raise ValueError('empty declaration')
            kind,*args=tokens
            if body is None:
                if kind!='return_module' or len(args)!=2:raise ValueError('module header required')
                body={'profile':args[0],'name':args[1]};continue
            if kind=='end_module':
                if args:raise ValueError('end arity')
                ended=True;continue
            if kind in ['source','context','period','component','tax']:
                if kind in seen:raise ValueError('duplicate declaration')
                body[kind]=fields(args,props[kind]);seen.add(kind)
            elif kind in ['accounts','lots','events']:
                if args or kind in seen:raise ValueError('collection declaration')
                body[kind]={} if kind=='accounts' else [];seen.add(kind)
            elif kind=='account':
                if 'accounts' not in seen or len(args)!=2 or args[0] in body['accounts']:raise ValueError('account declaration')
                body['accounts'][args[0]]=args[1]
            elif kind=='lot':
                if 'lots' not in seen:raise ValueError('lots declaration required')
                body['lots'].append(fields(args,props['lots']['items']))
            elif kind in ['settle','sell']:
                if 'events' not in seen:raise ValueError('events declaration required')
                rule=event_rules[kind];names=list(rule['properties'])
                # The command is the event kind; the other fields retain schema order.
                rule={'properties':{k:v for k,v in rule['properties'].items() if k!='kind'}}
                body['events'].append({**fields(args,rule),'kind':kind})
            else:raise ValueError('unknown declaration')
        except ValueError as exc:raise ValueError('line '+str(number)+': '+str(exc)) from exc
    if body is None or not ended:raise ValueError('incomplete module')
    return validate(body)


def render(body):
    validate(body)
    def token(value):
        if type(value) is bool:return 'true' if value else 'false'
        if type(value) is not str or '\n' in value or '\r' in value:raise ValueError('single-line scalar required')
        return shlex.quote(value)
    def line(kind,values):return ' '.join([kind]+[token(v) for v in values])+';'
    props=schema()['properties'];out=[line('return_module',[body['profile'],body['name']])]
    for kind in ['source','context','period']:
        out.append(line(kind,[body[kind][k] for k in props[kind]['properties']]))
    out.append('accounts;')
    for key in ROLES:out.append(line('account',[key,body['accounts'][key]]))
    for kind in ['component','tax']:
        out.append(line(kind,[body[kind][k] for k in props[kind]['properties']]))
    out.append('lots;')
    for lot in body['lots']:out.append(line('lot',[lot[k] for k in props['lots']['items']['properties']]))
    out.append('events;')
    event_rules={r['properties']['kind']['const']:r for r in props['events']['items']['oneOf']}
    for event in body['events']:
        out.append(line(event['kind'],[event[k] for k in event_rules[event['kind']]['properties'] if k!='kind']))
    out.append('end_module;')
    return '\n'.join(out)+'\n'
