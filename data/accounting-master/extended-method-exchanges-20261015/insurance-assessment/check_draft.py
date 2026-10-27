"""Small pre-build arithmetic diagnostic; no immutable attempt generated."""
from fractions import Fraction
import hashlib
import json
import re
import sys
import time
from authored_cases import CASES
from mathematical_checks import derive, Refusal
from schema_design import schemas
from jsonschema import Draft202012Validator, FormatChecker
def wire(v):
    if isinstance(v,str) and re.fullmatch(r'-?[0-9]+(?:/[0-9]+)?',v):
        f=Fraction(v); return dict(n=str(f.numerator),d=str(f.denominator))
    if isinstance(v,dict): return {k:wire(x) for k,x in v.items()}
    if isinstance(v,list): return [wire(x) for x in v]
    return v
def main():
    start=time.monotonic(); checks=0; failures=[]
    schema=schemas(); validator=Draft202012Validator(schema['$defs']['AssessmentInput'],format_checker=FormatChecker())
    for k,v in schema['$defs'].items(): Draft202012Validator.check_schema(v)
    for c in CASES:
        try:
            inp=wire(c['input']); validator.validate(inp); checks+=1
            try: result=derive(inp)
            except Refusal as e:
                assert e.code==c['refusal'],(e.code,c['refusal']); checks+=1; continue
            assert not c['refusal'],'expected refusal'
            expected=wire(c['detail'])
            if inp['method_id']=='triangle.inspect@1': expected['triangle_sha256']=hashlib.sha256(json.dumps(inp,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            assert result==dict(status=c['status'],diagnostics=c['diagnostics'],detail=expected),(result,expected)
            checks+=1
        except Exception as e: failures.append(dict(case=c['id'],diagnostic=str(e)[:500]))
    print(json.dumps(dict(passed=not failures,checks=checks,cases=len(CASES),failures=failures,interpreter=sys.executable,wall_seconds=time.monotonic()-start)))
    return bool(failures)
if __name__=='__main__': raise SystemExit(main())
