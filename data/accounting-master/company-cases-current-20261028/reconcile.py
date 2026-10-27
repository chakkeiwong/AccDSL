"""Preserve original company obligations; replay the finite synthetic reference."""
from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256
from copy import deepcopy
import gzip,importlib.util,json,os,subprocess,sys,time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=HERE.parent
def read(p):return json.loads(p.read_text())
def digest(p):return sha256(p.read_bytes()).hexdigest()
def main():
    assert len(sys.argv)==2 and len(Path(sys.argv[1]).parts)==1 and sys.argv[1] not in {'.','..'}
    out=HERE/sys.argv[1];out.mkdir(exist_ok=False);clock=time.monotonic();checks=[];lock={};passed=False
    def check(name,value):checks.append(dict(name=name,passed=bool(value)));assert value,name
    def protect(p,expected=None):
        h=digest(p);key=str(p.relative_to(ROOT));check('hash:'+key,expected is None or h==expected);lock[key]=h
    try:
        check('CPU-only',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1')
        for p in [Path(__file__),ROOT/'docs/plans/accounting-company-case-reconciliation-20261028.md']:protect(p)
        oldpath=BASE/'real-company-acceptance-20261027/attempt-01/current-decisions.json';protect(oldpath);old=read(oldpath);current=deepcopy(old)
        sources=['debt-reading-network-20261027/result.md','selected-reading-history-20261027/result.md','compatibility-current-20261028/registry.json','compatibility-current-20261028/attempt-02/run-manifest.json','sector-compatibility-current-20261028/attempt-02/run-manifest.json']
        for f in sources:protect(BASE/f)
        changes={
          'identity':('SelectedReadingHistoryAttachment/1 explicitly composes the selected source parent with exact context-specific supplied histories; all parent provenance survives.','Use the delivered selected-history adapter. A separately supported legal-entity/book mapping is still required; consolidated context does not identify a legal book.'),
          'context':('The checked selected reading retains236 observations/101 relations in two exact contexts; all180 target obligations remain.','Keep both contexts and every relation. Add an explicit conversion/perimeter premise before any cross-context company join; no joint history is supplied by separate witnesses.'),
          'opening':('ConditionalCompanyOpening/1 and continuation/report/carry have full native replay evidence; direct selected-history-wrapper and temporal-definition transfers are refused.','Complete source-to-final-account/memory mappings and a full typed witness under the native scale/date rules. Retain target obligations; a candidate opening cannot clear continuation.'),
          'claims':('SelectedTermProgram/1 executes the complete selected term-event source sequence with independent selection, full state/coverage and exact successful prefixes.','Reuse this delivered program for supplied populations. Actual issuer claim IDs, maturities, allocations and completeness still require evidence; do not promote synthetic completeness.'),
          'debt':('The exact retained XBRL reported-zero reading has been audited separately from the original PDF dash. Under the declared nearest-million ties-away premise, the selected latent interval is open(-1/2,1/2) USD million;1/4 remains feasible.','Reuse SelectedDebtReadingNetwork/1 and SelectedReadingHistoryAttachment/1. Preserve original PDF-only unknown, selected reading/rounding and full equations. Next address instrument terms, principal/noncash allocations and legal-book mappings; do not repeat the source-lead discovery or impose exact zero.'),
          'report_carry':('Twenty-one native conditional-opening/continuation/report/carry cases reproduce. The separate finite synthetic P reference checks returns, tax, annual statements and carry; it is not an issuer report.','Join only a complete same-context admitted conditional state to reporting and explicit carry policies. Finish issuer statement/notes dispositions and full affected-state expectations without inventing missing facts.')
        }
        for row,original in zip(current['rows'],old['rows']):
            check('original wording:'+row['id'],row['original_by_target']==original['original_by_target'])
            row['review_20261028']=dict(capability=changes.get(row['id'],(row['current_capability'],row['next_discriminating_action']))[0],next_action=changes.get(row['id'],(row['current_capability'],row['next_discriminating_action']))[1],issuer_dependency=original['remaining_issuer_dependency'],original_target_ready=False,actual_issuer_admission=False,evidence=sources if row['id'] in changes else original['evidence'])
            if row['id']=='debt':row['review_20261028']['issuer_dependency']='Selected reading does not establish actual instrument terms, noncash debt movements, principal allocations, legal books or source/accounting admission. The original PDF-only interpretation remains separately unresolved.'
        check('fifteen rows retained',len(current['rows'])==15);check('two original targets',current['original_targets']==old['original_targets'] and len(old['original_targets'])==2)
        check('all target admissions remain false',all(not row['review_20261028']['original_target_ready'] and not row['review_20261028']['actual_issuer_admission'] for row in current['rows']))
        current['continuation_scope']='Additive current interpretation; original fields preserved. Source conclusions inherited; synthetic replay newly executed.'
        (out/'current-decisions.json').write_text(json.dumps(current,indent=2)+'\n')
        ref=BASE/'company-return-execution-20261024';manifest=read(ref/'manifest.json');protect(ref/'manifest.json')
        for group in ['inputs','implementation','outputs']:
            for name,h in manifest[group].items():protect(ROOT/name,h)
        sys.path.insert(0,str(ref));spec=importlib.util.spec_from_file_location('current_company_case_reference',ref/'verify.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        actual,trace,inner_lock=m.conformance()
        check('native conformance passes',actual['passed']);check('all253 checks retained',len(actual['checks'])==253)
        check('complete original checks and refusals',m.canon(actual)==m.canon(read(ref/'checks.json')))
        check('complete trace, reports and carry',m.canon(trace)==m.canon(read(ref/'trace.json')))
        for name,h in inner_lock.items():protect(ROOT/name,h)
        for name,value in [('synthetic-checks',actual),('synthetic-trace',trace)]:
            p=out/(name+'.json.gz');p.write_bytes(gzip.compress(json.dumps(value,separators=(',',':')).encode(),mtime=0));check('roundtrip:'+name,json.loads(gzip.decompress(p.read_bytes()))==value)
        for f,h in lock.items():check('unchanged:'+f,digest(ROOT/f)==h)
        passed=True
    finally:
        (out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n');(out/'source-lock.json').write_text(json.dumps(lock,indent=2)+'\n')
        manifest=dict(passed=passed,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command='CUDA_VISIBLE_DEVICES=-1 python3 -B data/accounting-master/company-cases-current-20261028/reconcile.py '+sys.argv[1],environment=sys.version,cpu_gpu='CPU only; GPU intentionally hidden',random_seeds='N/A deterministic reference',wall_seconds=time.monotonic()-clock,timestamp=datetime.now(timezone.utc).isoformat(),data_version=digest(out/'source-lock.json'),plan_file='docs/plans/accounting-company-case-reconciliation-20261028.md',result_file='data/accounting-master/company-cases-current-20261028/result.md',artifacts={p.name:digest(p) for p in out.iterdir() if p.is_file()})
        (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(dict(passed=passed,checks=len(checks),failed=[x['name'] for x in checks if not x['passed']],protected=len(lock),wall_seconds=manifest['wall_seconds'])))
if __name__=='__main__':main()
