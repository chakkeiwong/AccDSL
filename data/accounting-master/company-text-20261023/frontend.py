"""Line-oriented documentary authoring; no evaluation, includes or source I/O."""
from fractions import Fraction
from pathlib import Path
import json
import shlex
from jsonschema import Draft202012Validator,FormatChecker

HERE=Path(__file__).resolve().parent
SCHEMA=json.loads((HERE.parent/'company-operation-path-20261023/schema.json').read_text())
INITIAL=SCHEMA['properties']['initial_year']
CONTINUATION=SCHEMA['properties']['continuations']['items']
OP_SCHEMAS={r['properties']['kind']['const']:r for r in INITIAL['properties']['operations']['items']['oneOf']}
REPEATED={'asset':'assets','opening_claim':'opening_claims'}
ORDER=['profile','name','assumption','source','opening_digest','context','period',
       'information','inventory','opening_claims','assets','depreciation_method',
       'debt','facility','loan','tax','operations']


def validate(body):
    Draft202012Validator(SCHEMA,format_checker=FormatChecker()).validate(body)
    def visit(value,rule):
        if 'oneOf' in rule:
            matches=[r for r in rule['oneOf'] if Draft202012Validator(r).is_valid(value)]
            if len(matches)!=1:raise ValueError('ambiguous typed value')
            return visit(value,matches[0])
        if isinstance(value,dict):
            for k,v in value.items():visit(v,rule['properties'][k])
        elif isinstance(value,list):
            for v in value:visit(v,rule['items'])
        elif rule.get('pattern','').startswith('^(unknown|') and value!='unknown':
            number=Fraction(value)
            if value!=str(number.numerator)+'/'+str(number.denominator):
                raise ValueError('noncanonical rational')
    visit(body,SCHEMA)
    for year in [body['initial_year']]+body['continuations']:
        ids=[o['id'] for o in year['operations']]
        if len(set(ids))!=len(ids):raise ValueError('duplicate operation identity')
        for op in year['operations']:
            if op['kind'] in ['collection','supplier_payment']:
                ids=[a['claim_id'] for a in op['payload']['allocations']]
                if len(set(ids))!=len(ids):raise ValueError('duplicate allocation identity')
        for name in ['assets','opening_claims']:
            if name in year:
                ids=[v['id'] for v in year[name]]
                if len(set(ids))!=len(ids):raise ValueError('duplicate '+name+' identity')
    return body


def scalar(token,rule):
    if rule.get('enum')==[True,False,'unknown']:
        if token not in ['true','false','unknown']:raise ValueError('truth must be true, false or unknown')
        return {'true':True,'false':False,'unknown':'unknown'}[token]
    return token


def fields(args,rule):
    names=list(rule['properties'])
    if len(args)!=len(names):raise ValueError('wrong declaration arity')
    return {k:scalar(v,rule['properties'][k]) for k,v in zip(names,args)}


def lower(text):
    if not isinstance(text,str):raise ValueError('text must be a string')
    path=None;year=None;rule=None;closed=False;initial_seen=False
    for number,line in enumerate(text.splitlines(),1):
        line=line.strip()
        if not line:continue
        try:
            if closed:raise ValueError('content after end_path')
            if not line.endswith(';'):raise ValueError('missing semicolon')
            tokens=shlex.split(line[:-1],comments=False,posix=True)
            if not tokens:raise ValueError('empty declaration')
            kind,*args=tokens
            if path is None:
                if kind!='path' or len(args)!=3:raise ValueError('expected path profile name assumption')
                path={'profile':args[0],'name':args[1],'assumption':args[2],'continuations':[]}
                continue
            if year is None:
                if kind=='end_path' and not args:
                    if not initial_seen:raise ValueError('missing initial year')
                    closed=True;continue
                if kind not in ['initial_year','continuation'] or args:raise ValueError('expected year block')
                if kind=='initial_year':
                    if initial_seen:raise ValueError('duplicate initial year')
                    initial_seen=True;rule=INITIAL;year={};path['initial_year']=year
                else:
                    if not initial_seen:raise ValueError('continuation before initial year')
                    rule=CONTINUATION;year={};path['continuations'].append(year)
                continue
            if kind=='end_year':
                if args:raise ValueError('end_year takes no arguments')
                if set(year)!=set(rule['properties']):raise ValueError('missing year declarations')
                year=None;rule=None;continue
            if kind in REPEATED:
                key=REPEATED[kind]
                if key not in rule['properties']:raise ValueError('initial opening declaration in continuation')
                if key not in year:raise ValueError('missing explicit array declaration')
                year[key].append(fields(args,rule['properties'][key]['items']));continue
            if kind=='operation':
                if 'operations' not in year:raise ValueError('missing operations declaration')
                if len(args)<3:raise ValueError('operation requires id kind instant')
                ident,operation_kind,at,*payload=args
                if operation_kind not in OP_SCHEMAS:raise ValueError('unknown operation kind')
                if any(o['id']==ident for o in year['operations']):raise ValueError('duplicate operation identity')
                pr=OP_SCHEMAS[operation_kind]['properties']['payload']
                if operation_kind in ['collection','supplier_payment']:
                    if payload:raise ValueError('settlement uses allocation declarations')
                    body={'allocations':[]}
                else:body=fields(payload,pr)
                year['operations'].append({'id':ident,'kind':operation_kind,'at':at,'payload':body});continue
            if kind=='allocate':
                if len(args)!=3:raise ValueError('allocate requires operation claim amount')
                ident,claim,amount=args
                matches=[o for o in year.get('operations',[]) if o['id']==ident]
                if len(matches)!=1 or matches[0]['kind'] not in ['collection','supplier_payment']:
                    raise ValueError('allocation requires previously declared settlement operation')
                allocations=matches[0]['payload']['allocations']
                if any(a['claim_id']==claim for a in allocations):raise ValueError('duplicate allocation identity')
                allocations.append({'claim_id':claim,'amount':amount});continue
            if kind not in rule['properties']:raise ValueError('unknown or forbidden year declaration')
            if kind in year:raise ValueError('duplicate declaration '+kind)
            item=rule['properties'][kind]
            if item.get('type')=='array':
                if args:raise ValueError('array declaration takes no arguments')
                year[kind]=[]
            elif item.get('type')=='object':year[kind]=fields(args,item)
            else:
                if len(args)!=1:raise ValueError('scalar declaration takes one argument')
                year[kind]=scalar(args[0],item)
        except ValueError as exc:raise ValueError('line '+str(number)+': '+str(exc)) from exc
    if path is None or year is not None or not closed:raise ValueError('incomplete path or year block')
    return validate(path)


def render(path):
    validate(path)
    def token(value):
        if value is True:return 'true'
        if value is False:return 'false'
        if not isinstance(value,str) or any(c in value for c in ['\n','\r']):
            raise ValueError('line-oriented value contains newline or nontext scalar')
        return shlex.quote(value)
    def line(kind,args):return ' '.join([kind]+[token(v) for v in args])+';'
    out=[line('path',[path['profile'],path['name'],path['assumption']])]
    for index,year in enumerate([path['initial_year']]+path['continuations']):
        rule=INITIAL if index==0 else CONTINUATION
        out+=['','initial_year;' if index==0 else 'continuation;']
        for key in ORDER:
            if key not in rule['properties']:continue
            value=year[key];pr=rule['properties'][key]
            if key=='operations':
                out.append('operations;')
                for op in value:
                    payload=OP_SCHEMAS[op['kind']]['properties']['payload']
                    settlement=op['kind'] in ['collection','supplier_payment']
                    args=[op['id'],op['kind'],op['at']]
                    if not settlement:args += [op['payload'][k] for k in payload['properties']]
                    out.append(line('operation',args))
                    if settlement:
                        out += [line('allocate',[op['id'],a['claim_id'],a['amount']]) for a in op['payload']['allocations']]
            elif pr.get('type')=='array':
                out.append(key+';');name=next(k for k,v in REPEATED.items() if v==key)
                for entry in value:out.append(line(name,[entry[k] for k in pr['items']['properties']]))
            elif pr.get('type')=='object':out.append(line(key,[value[k] for k in pr['properties']]))
            else:out.append(line(key,[value]))
        out.append('end_year;')
    out.append('end_path;')
    return '\n'.join(out)+'\n'
