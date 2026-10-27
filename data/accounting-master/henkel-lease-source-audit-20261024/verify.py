"""Replay source anchors and display arithmetic. This cannot admit native state."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction
from datetime import datetime, timezone
import argparse
import json
import platform
import subprocess
import sys
import time
import fitz

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
COUNT=0

def check(value, label):
    global COUNT
    if not value:
        raise AssertionError(label)
    COUNT+=1

def read(name):
    return json.loads((HERE/name).read_text())

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def dump(name,data):
    (HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def verify_anchor(doc,page,a):
    p=doc[page-1]
    if a['kind']=='pdf_word':
        words=p.get_text('words'); w=words[a['word_index']]
        check(a['token']==w[4] and a['bbox']==list(w[:4]),'literal and geometry')
        for t in a['row_tokens']:
            w=words[t['word_index']]
            check(t['token']==w[4] and t['bbox']==list(w[:4]),'row context')
    else:
        text=p.get_text(); check(a['kind']=='pdf_text_span','known anchor kind')
        check(text[a['start']:a['end']]==a['text'],'exact PDF text span')

def main():
    started=time.monotonic()
    parser=argparse.ArgumentParser();g=parser.add_mutually_exclusive_group()
    g.add_argument('--record',action='store_true');g.add_argument('--replay',action='store_true');args=parser.parse_args()
    if args.record:
        check(not (HERE/'checks.json').exists() and not (HERE/'manifest.json').exists(),'record once')
    lock=read('source-lock.json')
    for name,expected in lock.items():
        check(digest(ROOT/name)==expected,'protected source '+name)
    index=read('source-index.json'); doc=fitz.open(ROOT/index['pdf'])
    check(len(doc)==index['physical_pages']==490,'PDF page count')
    data=read('observations.json');obs=data['observations'];by_id={o['id']:o for o in obs}
    check(len(obs)==len(by_id)==104,'unique complete bounded observation set')
    context=data['context']
    check(context['currency']=='EUR' and context['unit']=='million EUR','reporting unit')
    check(context['measurement_policy']=='display_only' and context['rounding_tie_rule']=='unknown','precision unknown')
    check(context['native_state_admission'] is False and context['historical_as_of_admission'] is False,'admission withheld')
    for o in obs:
        page=o['physical_page'];a=o['anchor'];verify_anchor(doc,page,a)
        check(o['printed_page']==page-2,'printed numbering')
        check(o['source_sha256']==index['pdf_sha256']==lock[index['pdf']],'observation source binding')
        check(o['unit']=='million EUR' and o['currency']=='EUR' and o['context_id']=='henkel-consolidated-eur-2025-report','observation context')
        check(o['constraint_mode']=='display_only' and o['underlying_amount'] is None,'no exact amount inference')
        if a['kind']=='pdf_word': check(o['literal']==a['token'],'literal anchored')
        else: check(a['text'][a['literal_offset']:a['literal_offset']+len(o['literal'])]==o['literal'],'narrative literal anchored')
        if o['literal']=='–': check(o['display_kind']=='dash' and o['displayed_rational'] is None,'dash not zero')
        else: check(Fraction(o['literal'].replace(',',''))==Fraction(o['displayed_rational']),'rational display decoding')
        year=o['presentation_year'];check(year in [2024,2025] and o['id'].startswith(str(year)+'.'),'year keyed')
        check(o['comparative_role']==('current_in_2025_report' if year==2025 else 'comparative_in_2025_report'),'comparative source vintage')
        if o['period']:
            check(o['period']=={'start':f'{year}-01-01','end_exclusive':f'{year+1}-01-01'} and o['measurement_date'] is None,'flow period')
        else:
            expected=f'{year-1 if o["id"].endswith("reconciliation.opening") else year}-12-31'
            check(o['measurement_date']==expected,'stock date')
    check(by_id['2025.reconciliation.fair_value']['literal']=='-0','signed zero spelling preserved')
    check(sum(o['display_kind']=='dash' for o in obs)==8,'all construction dash cells preserved')
    check(len(data['qualitative'])==12,'qualitative inventory')
    for q in data['qualitative']: verify_anchor(doc,q['physical_page'],q['anchor'])
    diagnostics=read('display-checks.json')['checks']
    check(len(diagnostics)==32,'diagnostic inventory')
    for d in diagnostics:
        value=sum((Fraction(t['coefficient'])*Fraction(by_id[t['observation']]['displayed_rational']) for t in d['terms']),Fraction())
        check(value==Fraction(d['result'])==Fraction(d['expected_display_result']),'exact display arithmetic '+d['id'])
        check(d['role']=='explanatory_diagnostic' and d['exact_underlying_equality_asserted'] is False,'diagnostic role')
        if d['id'].endswith('signed_rollforward'):
            check(not any(t['observation'].endswith(('interest_paid','redemption')) for t in d['terms']),'cash subtotal not double counted')
        for excluded in d['excluded_observations']:
            check(by_id[excluded]['display_kind']=='dash' and excluded not in [t['observation'] for t in d['terms']],'unquantified dash retained')
    dependencies=read('state-dependencies.json')
    check(len(dependencies['dependencies'])==14 and all(d['status']=='unresolved' for d in dependencies['dependencies']),'unknown state retained')
    check(dependencies['automatic_state_conversion'] is False and dependencies['native_execution']=='unresolved','no automatic executable state')
    coverage=read('source-coverage.json')
    check(len(coverage['pages'])==12 and coverage['whole_filing_coverage'] is False and coverage['whole_note_23_coverage'] is False,'bounded coverage')
    for r in coverage['pages']:
        text=doc[r['physical_page']-1].get_text()
        check(sha256(text.encode()).hexdigest()==r['pdf_text_sha256'],'page text reproducible')
        check((HERE/r['text_file']).read_text()==text,'retained page text exact')
        check(digest(HERE/r['legacy_layout_file'])==r['legacy_layout_sha256'],'legacy reading aid preserved')
    report={'passed':True,'checks':COUNT,'observations':len(obs),'qualitative':len(data['qualitative']),
            'display_diagnostics':len(diagnostics),'state_dependencies':14,'protected_sources':len(lock),
            'reviewed_pages':12,'native_state_admission':False,'whole_requirements_closed':0}
    # Recording guard is not part of the reproducible substantive-check count.
    if args.record: report['checks']-=1
    if args.replay:
        check(report==read('checks.json'),'saved report replay')
        for name,expected in read('manifest.json')['package_sha256'].items():
            check(digest(HERE/name)==expected,'immutable package '+name)
        report['saved_replay']=True
    if args.record:
        files=['source-lock.json','source-index.json','observations.json','display-checks.json','state-dependencies.json','source-coverage.json','build_observations.py','build_evidence.py','verify.py','result.md','review.md','finish.py']
        files += [r['text_file'] for r in coverage['pages']]
        files += [r['legacy_layout_file'] for r in coverage['pages']]
        hashes={name:digest(HERE/name) for name in files}
        commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip()
        manifest={'recorded_at':datetime.now(timezone.utc).isoformat(),'git_commit':commit,
                  'dirty_worktree':'pre-existing extensive edits retained; protected byte hashes are operative provenance',
                  'command':'python3 -B '+str((HERE/'verify.py').relative_to(ROOT))+' --record',
                  'environment':{'python':platform.python_version(),'executable':sys.executable,'pymupdf':fitz.VersionBind},
                  'cpu_gpu':'CPU PDF parsing and exact rational arithmetic; no GPU libraries or devices used',
                  'random_seeds':'N/A: deterministic source verification','wall_seconds':time.monotonic()-started,
                  'data_version':index['pdf_sha256'],'plan':'docs/plans/accounting-henkel-lease-source-audit-20261024.md',
                  'result':str((HERE/'result.md').relative_to(ROOT)),'package_sha256':hashes}
        dump('checks.json',report);dump('manifest.json',manifest)
    print(json.dumps(report))

if __name__=='__main__':
    main()
