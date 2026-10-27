"""Line-oriented text for the finite expression DAG; no evaluation of host code."""
import json
import shlex
from expressions import analyze, PROFILE

def scalar(token):
    if token=='true': return True
    if token=='false': return False
    return token
def decode_type(token):
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out: raise ValueError('duplicate type key')
            out[k]=v
        return out
    return json.loads(token,object_pairs_hook=unique,parse_constant=lambda x: (_ for _ in ()).throw(ValueError('invalid numeric constant')))
def lower(text):
    if not isinstance(text,str): raise ValueError('text required')
    body=None; ended=False
    for number,raw in enumerate(text.splitlines(),1):
        line=raw.strip()
        if not line: continue
        try:
            if ended: raise ValueError('content after end_program')
            if not line.endswith(';'): raise ValueError('semicolon required')
            tokens=shlex.split(line[:-1],comments=False,posix=True)
            if not tokens: raise ValueError('empty declaration')
            kind,*args=tokens
            if body is None:
                if kind!='program' or len(args)!=2: raise ValueError('program profile name required')
                body={'profile':args[0],'name':args[1],'inputs':{},'nodes':[],'outputs':{}}; continue
            if kind=='input' and len(args)==3:
                ident,typ,val=args
                if ident in body['inputs']: raise ValueError('duplicate input')
                body['inputs'][ident]={'type':decode_type(typ),'value':scalar(val)}
            elif kind=='literal' and len(args)==3:
                ident,typ,val=args
                body['nodes'].append({'id':ident,'op':'literal','type':decode_type(typ),'value':scalar(val)})
            elif kind=='input_ref' and len(args)==2:
                body['nodes'].append({'id':args[0],'op':'input','target':args[1]})
            elif kind=='node' and len(args)>=2:
                body['nodes'].append({'id':args[0],'op':args[1],'args':args[2:]})
            elif kind=='output' and len(args)==2:
                if args[0] in body['outputs']: raise ValueError('duplicate output')
                body['outputs'][args[0]]=args[1]
            elif kind=='end_program' and not args: ended=True
            else: raise ValueError('unknown declaration or arity')
        except ValueError as exc: raise ValueError('line '+str(number)+': '+str(exc)) from exc
    if body is None or not ended: raise ValueError('incomplete program')
    analyze(body); return body
def render(body):
    analyze(body)
    def token(x):
        if type(x) is bool: return 'true' if x else 'false'
        if not isinstance(x,str) or '\n' in x or '\r' in x: raise ValueError('line token required')
        return shlex.quote(x)
    def line(kind,*args): return ' '.join([kind]+[token(x) for x in args])+';'
    def typ(t): return json.dumps(t,sort_keys=True,separators=(',',':'))
    out=[line('program',PROFILE,body['name'])]
    for name,item in sorted(body['inputs'].items()): out.append(line('input',name,typ(item['type']),item['value']))
    for node in body['nodes']:
        if node['op']=='literal': out.append(line('literal',node['id'],typ(node['type']),node['value']))
        elif node['op']=='input': out.append(line('input_ref',node['id'],node['target']))
        else: out.append(line('node',node['id'],node['op'],*node['args']))
    for name,target in sorted(body['outputs'].items()): out.append(line('output',name,target))
    return '\n'.join(out+['end_program;'])+'\n'
