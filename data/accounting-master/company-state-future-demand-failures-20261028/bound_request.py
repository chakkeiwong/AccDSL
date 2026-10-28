"""Explicit expected-identity admission for a supported finite policy request.
The expected identity is trusted caller state, never request self-authentication.
"""
from pathlib import Path
from hashlib import sha256
import json,importlib.util
ROOT=Path(__file__).resolve().parents[3]
NATIVE=ROOT/'data/accounting-master/cross-mechanism-policy-20261027/policy.py'
NATIVE_SHA='241e9399b878eb95d05b73a2fbffb58f4a4912396d295e9ae0832c3a69a67748'
SCHEMA='BoundFinitePolicyRequest/1'
def identity(request):
 return sha256(json.dumps(request,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()).hexdigest()
def solve(request,expected_request_sha256):
 if sha256(NATIVE.read_bytes()).hexdigest()!=NATIVE_SHA:
  return dict(status='refused',reason='native_identity',native_executed=False)
 if not isinstance(request,dict) or set(request)!={'schema','rows','actions1','actions2','reveal'} or request.get('schema')!=SCHEMA:
  return dict(status='refused',reason='request_shape',native_executed=False)
 try:actual=identity(request)
 except (TypeError,ValueError):return dict(status='refused',reason='request_encoding',native_executed=False)
 if not isinstance(expected_request_sha256,str) or actual!=expected_request_sha256:
  return dict(status='refused',reason='request_identity',native_executed=False,actual_request_sha256=actual)
 if type(request['actions1']) is not list or type(request['actions2']) is not list:
  return dict(status='refused',reason='action_domain_type',native_executed=False)
 spec=importlib.util.spec_from_file_location('bound_finite_policy_native',NATIVE);native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
 try:result=native.solve(request['rows'],request['actions1'],request['actions2'],request['reveal'])
 except (ValueError,TypeError,KeyError) as e:return dict(status='refused',reason='native_validation:'+str(e),native_executed=True,request_sha256=actual)
 return dict(status='complete_conditional',policies=sorted(result,key=repr),request_sha256=actual,native_sha256=NATIVE_SHA,native_executed=True,
  scope='Complete relative to externally admitted finite rows; no real-source or actor admission')

