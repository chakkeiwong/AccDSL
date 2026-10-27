"""Restricted documentary frontend; independent of the product compiler."""
from datetime import datetime
from fractions import Fraction as Q
import json
from pathlib import Path
import shlex


class AuthoringError(ValueError):
    pass


def rational(token):
    try:
        n,d=token.split('/'); value=Q(int(n),int(d))
    except (ValueError,ZeroDivisionError):
        raise AuthoringError('Expected canonical numerator/denominator') from None
    if str(value.numerator)+'/'+str(value.denominator)!=token:
        raise AuthoringError('Noncanonical rational')
    return {'n':n,'d':d}


def lower(text):
    body={}; claims=[]; events=[]; seen=set()
    for number,line in enumerate(text.splitlines(),1):
        line=line.strip()
        if not line: continue
        if not line.endswith(';'): raise AuthoringError('Line '+str(number)+': missing semicolon')
        try: tokens=shlex.split(line[:-1],comments=False,posix=True)
        except ValueError as e: raise AuthoringError('Line '+str(number)+': '+str(e)) from None
        if not tokens: raise AuthoringError('Empty declaration')
        kind,*args=tokens
        expected={'profile':1,'name':1,'projection':2,'context':3,'share':1,
                  'source':2,'assumption':1,'claim':5,'facility':4,'loan':6,'tax':2,'event':2}
        if kind not in expected or len(args)!=expected[kind]:
            raise AuthoringError('Line '+str(number)+': unsupported declaration or arity')
        if kind not in {'claim','event'}:
            if kind in seen: raise AuthoringError('Duplicate '+kind)
            seen.add(kind)
        if kind in {'profile','name','assumption'}: body[kind]=args[0]
        elif kind=='projection': body['projection']={'alias':args[0],'digest':args[1]}
        elif kind=='context': body['context']=dict(zip(('entity','book','currency'),args))
        elif kind=='share': body['share']=rational(args[0])
        elif kind=='source': body['source']={'path':args[0],'sha256':args[1]}
        elif kind=='claim':
            claims.append(dict(zip(('id','ledger','origin'),args[:3]),recognised=rational(args[3]),settlement=rational(args[4])))
        elif kind=='facility':
            body['facility']={'id':args[0],'limit':rational(args[1]),'drawn':rational(args[2]),'reserved':rational(args[3])}
        elif kind=='loan':
            body['loan']={'facility_id':args[0],'principal':rational(args[1]),'annual_rate':rational(args[2]),
                          'day_count':args[3],'fee':rational(args[4]),'interest_cash_class':args[5]}
        elif kind=='tax': body['tax']={'rate':rational(args[0]),'method':args[1]}
        elif kind=='event': events.append({'kind':args[0],'at':args[1]})
    body['claims']=claims; body['events']=events
    return body


def closed(fields):
    return {'type':'object','additionalProperties':False,'required':list(fields),'properties':fields}


def schema():
    text={'type':'string','minLength':1}; amount=closed({'n':{'type':'string','pattern':'^(0|-?[1-9][0-9]*)$'},'d':{'type':'string','pattern':'^[1-9][0-9]*$'}})
    instant={'type':'string','format':'date-time','pattern':'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$'}
    result=closed({'profile':{'const':'FundedYearInputsDraft/1'},'name':text,'assumption':text,
        'projection':closed({'alias':text,'digest':{'type':'string','pattern':'^[0-9a-f]{64}$'}}),
        'source':closed({'path':text,'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}}),
        'context':closed({'entity':text,'book':text,'currency':text}),'share':amount,
        'claims':{'type':'array','minItems':1,'items':closed({'id':text,'ledger':{'enum':['receivable','payable']},'origin':{'enum':['opening','delivery','purchase']},'recognised':amount,'settlement':amount})},
        'facility':closed({'id':text,'limit':amount,'drawn':amount,'reserved':amount}),
        'loan':closed({'facility_id':text,'principal':amount,'annual_rate':amount,'day_count':{'const':'ACT365_calendar'},'fee':amount,'interest_cash_class':{'const':'operating'}}),
        'tax':closed({'rate':amount,'method':{'const':'immediate_deductible'}}),
        'events':{'type':'array','minItems':1,'items':closed({'kind':text,'at':{'oneOf':[instant,{'const':'unknown'}]}})}})
    result['$schema']='https://json-schema.org/draft/2020-12/schema'
    return result
