"""Finite scope-bound certificate frontier; registry validation is external."""
from copy import deepcopy as cp

def need(p,s):
 if not p:raise ValueError(s)
def seed(scope,registry):
 return {'profile':'SelectedCertifiedRegionQueue/1','scope':cp(scope),'roster':list(registry),'pending':list(registry),'certified':{}}
def validate(scope,registry,q):
 need(set(q)=={'profile','scope','roster','pending','certified'},'queue_fields')
 need(q['profile']=='SelectedCertifiedRegionQueue/1' and q['scope']==scope,'scope')
 need(q['roster']==list(registry),'roster')
 ids=q['pending']+list(q['certified']);need(len(ids)==len(set(ids)) and set(ids)==set(registry),'partition')
 need(all(q['certified'][k]==registry[k] for k in q['certified']),'proof_binding')
 need(q['pending']==[k for k in registry if k not in q['certified']],'pending_order')
 return True
def advance(scope,registry,q,budget):
 need(type(budget)==int and budget>=0,'budget');validate(scope,registry,q);out=cp(q)
 for k in list(out['pending'])[:budget]:out['certified'][k]=registry[k];out['pending'].remove(k)
 validate(scope,registry,out);return out
