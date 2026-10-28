"""Original scanned-reference discriminator with native and independent oracles."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import argparse
import gzip
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import fitz
import coverage as c

ROOT, H = c.ROOT, c.H
PLAN = 'docs/plans/company-state-reference-coverage-failure-20261028.md'
def dump(path, value): path.write_text(json.dumps(value, indent=2) + '\n')

def findings(node):
    if isinstance(node, dict):
        if node.get('id') == 'incorporated_principal_ceiling' and 'body_truth' in node: yield node
        for value in node.values(): yield from findings(value)
    elif isinstance(node, list):
        for value in node: yield from findings(value)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve()
    out.mkdir(exist_ok=False)
    start = time.monotonic()
    checks, cases, controls = [], [], []
    def ck(name, actual, expected):
        checks.append(dict(name=name, passed=actual == expected, actual=actual, expected=expected))
    with fitz.open(H / 'sources/covenant-scan.pdf') as pdf:
        ck('source/raster-only text', pdf[0].get_text(), '')
        ck('source/one page and image', [len(pdf), len(pdf[0].get_images())], [1, 1])
    ck('source/ceiling visibly transcribed', '80 currency units.' in (H/'sources/transcription.txt').read_text(), True)
    ck('source/synthetic identity', c.BASE['synthetic'], True)
    legacy = c.f.ex.native.Engine.apply
    c.f.ex.native.Engine.apply = lambda *a, **kw: (_ for _ in ()).throw(AssertionError('legacy fallback forbidden'))
    try:
        for owner in ['alpha', 'beta']:
            baseline, mapping = c.make_program(owner, ['100/1'], include_covenant=False)
            result = c.program.run(baseline)
            ck(owner + '/unguarded accepts100', result['status'], 'complete_provisional')
            ck(owner + '/unguarded exact balances', [result['current']['balances'][mapping[k]] for k in ['cash','debt']], ['120/1','-100/1'])
            ck(owner + '/unguarded replay', c.program.verify(baseline, result), True)
            ck(owner + '/unguarded independently violates ceiling', -Q(result['current']['balances'][mapping['debt']]) > 80, True)
            cases.append(dict(id=owner+'/unguarded', input=baseline, result=result))
            for amounts, accepted, final in [(['79/1'], True, 79), (['80/1'], True, 80),
                    (['100/1'], False, 0), (['40/1','40/1'], True, 80), (['40/1','41/1'], False, 40)]:
                name = owner + '/' + '+'.join(amounts)
                request = c.request(owner, amounts)
                before = deepcopy(request)
                response = c.assess(request)
                ck(name+'/request unchanged', request, before)
                ck(name+'/native called', response['status'], 'native_result')
                result = response.get('native_result') or {}
                ck(name+'/native status', result.get('status'), 'complete_provisional' if accepted else 'stopped_provisional')
                if result.get('status') not in ['complete_provisional','stopped_provisional']: continue
                ck(name+'/complete native equality', result, c.program.run(request['native_program']))
                ck(name+'/complete replay', c.program.verify(request['native_program'], result), True)
                expected = deepcopy(request['native_program']['opening'])
                expected['balances'][mapping['cash']] = c.f.fmt(20 + final)
                expected['balances'][mapping['debt']] = c.f.fmt(-final)
                expected['memory']['finance']['debt'] = c.f.fmt(-final)
                ck(name+'/all balances', result['current']['balances'], expected['balances'])
                ck(name+'/all memory', result['current']['memory'], expected['memory'])
                ck(name+'/opening preserved', request['native_program']['opening'], before['native_program']['opening'])
                ck(name+'/all boundary flags', [response[k] for k in ['source_admission','accounting_admission','complete_company_population']], [False]*3)
                if accepted:
                    report = result['trace'][-1]['result']
                    ck(name+'/profit zero', report['income']['profit'], '0/1')
                    ck(name+'/financing cash', report['cash_flows']['activities']['financing']['net'], c.f.fmt(final))
                    ck(name+'/reconciliations', report['reconciliations'], dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
                else:
                    stop = result['stop']
                    ck(name+'/native refusal', [stop['status'],stop['reason']], ['invalid','preconditions'])
                    ck(name+'/failed transition atomic', stop['after_sha256'], stop['before_sha256'])
                    ck(name+'/covenant is false', [r['body_truth'] for r in findings(stop)], ['false'])
                    ck(name+'/stops at violating command', stop['index'], len(amounts)-1)
                cases.append(dict(id=name,input=request,result=response))
            # Absence must prevent the financial executor, even though it is capable of applying100.
            actual_run = c.program.run
            c.program.run = lambda *a, **kw: (_ for _ in ()).throw(AssertionError('uncovered document reached execution'))
            try:
                for stage, missing in [('missing','retrieval'),('retrieved','parsing'),('parsed','modeling')]:
                    request = c.request(owner, stage=stage)
                    response = c.assess(request)
                    name = owner+'/'+stage
                    ck(name+'/unresolved stage', [response['status'],response.get('missing_stage')], ['unresolved',missing])
                    ck(name+'/no native execution', [response['financial_execution'],response['native_result']], [False,None])
                    ck(name+'/full opening unchanged', response['current'], request['native_program']['opening'])
                    ck(name+'/full population retained', response['required_documents'], request['required_documents'])
                    cases.append(dict(id=name,input=request,result=response))
            finally: c.program.run = actual_run
        mutations = [
            ('drop required target',lambda r:r['required_documents'].clear(),'required_document_population'),
            ('invent parent binding',lambda r:r.update(parent_sha256='0'*64),'parent_binding'),
            ('false admission',lambda r:r.update(source_admission=True),'false_admission'),
            ('false completeness',lambda r:r.update(complete_company_population=True),'false_admission'),
            ('wrong retrieved hash',lambda r:r['required_documents'][c.REF]['retrieval'].update(sha256='0'*64),'retrieval_binding'),
            ('false retrieval path',lambda r:r['required_documents'][c.REF]['retrieval'].update(path='sources/parent.txt'),'retrieval_binding'),
            ('changed scan transcription',lambda r:r['required_documents'][c.REF]['parsing'].update(text='Ceiling120'),'parsing_binding'),
            ('wrong extraction hash',lambda r:r['required_documents'][c.REF]['parsing'].update(sha256='0'*64),'parsing_binding'),
            ('invent automatic OCR',lambda r:r['required_documents'][c.REF]['parsing'].update(method='certified_ocr'),'parsing_binding'),
            ('changed modeled ceiling',lambda r:r['required_documents'][c.REF]['modeling']['interpretation'].update(total_principal_after_borrowing_max='120/1'),'modeling_binding'),
            ('wrong method binding',lambda r:r['required_documents'][c.REF]['modeling'].update(method_sha256='0'*64),'modeling_binding'),
            ('modeled without parsing',lambda r:r['required_documents'][c.REF].update(parsing=None),'coverage_order'),
            ('parsed without retrieval',lambda r:r['required_documents'][c.REF].update(retrieval=None),'coverage_order'),
            ('drop native rule',lambda r:r['native_program']['registry']['entries']['debt_issue']['method']['preconditions']['manifest']['requirements'].pop(),'native_method_binding'),
            ('alter native amount only',lambda r:r['native_program']['commands'][0]['event']['inputs']['amount']['value'].update(value='1/1'),'native_method_binding')]
        actual_run = c.program.run
        c.program.run = lambda *a, **kw: (_ for _ in ()).throw(AssertionError('tamper reached execution'))
        try:
            for name, mutate, reason in mutations:
                request = c.request()
                mutate(request)
                response = c.assess(request)
                ck('tamper/'+name, [response['status'],response.get('reason'),response['financial_execution']], ['invalid',reason,False])
                controls.append(dict(id=name,input=request,result=response))
        finally: c.program.run = actual_run
        # A per-event cap misses accumulated debt despite accepting each amount individually.
        wrong = c.request(amounts=['40/1','41/1'])
        entry = wrong['native_program']['registry']['entries']['debt_issue']
        rule = entry['method']['preconditions']['manifest']['requirements'][-1]
        rule['predicate']['left'] = c.financing.ref('amount')
        rule['requires'] = ['amount']
        entry['method_sha256'] = c.program.digest(entry['method'])
        wrong['required_documents'][c.REF]['modeling']['method_sha256'] = entry['method_sha256']
        result = c.program.run(wrong['native_program'])
        ck('per-event mistake/native accepts',result['status'],'complete_provisional')
        ck('per-event mistake/independent debt81',result['current']['balances']['debt'],'-81/1')
        ck('per-event mistake/bound semantic guard rejects',c.assess(wrong)['reason'],'modeling_binding')
        cases.append(dict(id='per-event-instead-of-cumulative',input=wrong,result=result,guard=c.assess(wrong)))
    finally: c.f.ex.native.Engine.apply = legacy
    fm = ROOT/'data/accounting-master/unified-program-20261028/failure-map.json'
    original = [r['original_row'] for r in json.loads(fm.read_text())['rows'] if r['original_row']['id']=='SIM-F002']
    ck('exact original discriminator',[r['discriminating_case'] for r in original],['Place decisive covenant in a referenced scanned note'])
    paths = {Path(__file__), H/'coverage.py', H/'create_fixture.py', H/'fixture-baseline.json', ROOT/PLAN, fm}
    paths.update((H/'sources').iterdir())
    paths.update(Path(x.__file__).resolve() for x in list(sys.modules.values()) if getattr(x,'__file__',None) and Path(x.__file__).resolve().is_relative_to(ROOT))
    for row in checks:
        if len(json.dumps(row)) > 1200:
            row['actual_sha256'] = c.program.digest(row.pop('actual'))
            row['expected_sha256'] = c.program.digest(row.pop('expected'))
    failed = [r for r in checks if not r['passed']]
    verdict = dict(status='fail' if failed else 'pass',checks=len(checks),cases=len(cases),tamper_controls=len(controls),
        failed=failed,original_rows=['SIM-F002'],source_admission=False)
    dump(out/'verification.json',verdict)
    dump(out/'checks.json',checks)
    dump(out/'original-row.json',original)
    with gzip.open(out/'full-results.json.gz','wt') as z: json.dump(dict(cases=cases,controls=controls),z)
    for name in ['coverage.py','check.py']:(out/name).write_bytes((H/name).read_bytes())
    dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU-only raster/source and exact native checks; no GPU imports',
        random_seeds='N/A deterministic',data_version='Original SIM-F002 plus explicit synthetic scanned covenant',
        utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,
        result_file=str((H/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}))
    print(json.dumps(verdict))
    return bool(failed)

if __name__ == '__main__': raise SystemExit(main())
