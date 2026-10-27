"""Focused checks for the post-run base/schema call-chain finding."""
import hashlib
import json
from pathlib import Path

from company_bridge import bridge, BASE_PATH, ROOT, OUT


def main():
    request=json.loads((OUT/'company-attempt-02/conversion-request.json').read_text())
    checks=[]
    for path in (BASE_PATH,'data/accounting-master/continuation-integrity-eps-20261016/ordered-eps/record-schemas.json'):
        seen=[]
        def reader(p):
            seen.append(str(p.relative_to(ROOT)))
            return b'changed-bound-input' if str(p.relative_to(ROOT))==path else p.read_bytes()
        result=bridge(request,resolve_bytes=reader)
        checks.append(dict(name=path,passed=path in seen and result['status']=='rejected' and result['reason']=='input_bytes_changed' and result['company'] is None))
    extra=dict(request,base={'unbound':'alternate replay'})
    result=bridge(extra)
    checks.append(dict(name='caller-cannot-supply-base',passed=result['status']=='rejected' and result['reason']=='request_shape'))
    lock=json.loads((OUT/'runtime-input-lock.json').read_text())
    checks.append(dict(name='schema-predecessor-authority',passed=hashlib.sha256((ROOT/lock['authority']).read_bytes()).hexdigest()==lock['authority_sha256']))
    p=OUT/'binding-repair-checks.json';assert not p.exists()
    result=dict(checks=len(checks),failures=sum(not c['passed'] for c in checks),detail=checks)
    p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('checks','failures')}))
    if result['failures']:raise SystemExit(1)


if __name__=='__main__':main()
