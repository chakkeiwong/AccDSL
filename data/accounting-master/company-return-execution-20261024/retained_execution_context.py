"""Explicit retained-method adapter and source projection for finite replay."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
AUTHOR=HERE.parent/'company-return-schema-20261023'
sys.path.insert(0,str(AUTHOR))
from retained_fixture import fixture,bound_to_retained
from native_returns import fmt,need,q,FINDINGS,ACCOUNTS

def load():
    body,raw=fixture();need(bound_to_retained(body,raw),'source binding')
    packet=json.loads(raw);reg=packet['record_registry'];a=packet['aliases']
    item=lambda key:deepcopy(reg[a[key]['digest']]['body'])
    path=ROOT/packet['input_snapshots']['financial_checks.py']['path']
    need(sha256(path.read_bytes()).hexdigest()==packet['input_snapshots']['financial_checks.py']['sha256'],'retained method bytes')
    spec=importlib.util.spec_from_file_location('return_execution_retained_financial',path)
    financial=importlib.util.module_from_spec(spec);spec.loader.exec_module(financial)
    return body,packet,item,financial

def event_for(key,original,author):
    if key=='returns':return deepcopy(author['events'][0])
    if key=='recovered-sale':return deepcopy(author['events'][1])
    if original['method']=='tax.close':
        p=original['parameters']
        return {'id':key,'kind':'tax','method':'tax.close','date':original['date'],
            'start':p['period_start'],'end_exclusive':p['period_end_exclusive'],
            'rate':fmt(p['rate']),**{k:p[k] for k in FINDINGS}}
    return {'id':key,'kind':'surrounding','method':original['method'],'date':original['date'],'retained_event':deepcopy(original)}

def adapter_for(prior,financial):
    # Recompute surrounding journals from retained source state and methods.
    # Authored expected journals/states are never used here.
    def adapter(native,event):
        need({k:fmt(v) for k,v in prior['books']['P'].items()}==native['balances'],'adapter prior shared book mismatch')
        need(prior['currency']==native['context']['currency'] and native['context']['entity']=='P','adapter context')
        original=event['retained_event']
        need(original['date']==event['date'] and original['method']==event['method'],'adapter event binding')
        _,journals,flows=financial.derive(prior,original,lambda ok,why,*status:need(ok,why))
        selected=[{**f,'amount':fmt(f['amount'])} for f in flows if f['entity']=='P']
        interest=(q(native['opening_interest_remaining']) if original['method']=='compound.redeem' else 0)
        return {'journal':{k:fmt(journals['P'][k]) for k in ACCOUNTS},'flows':selected,'prior_interest':fmt(interest)}
    return adapter
