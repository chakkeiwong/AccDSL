"""Preserve the checked bank reproduction and exact MC21 acceptance wording."""
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import tarfile
import tempfile
import time

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
read=lambda p:json.loads(p.read_text())
digest=lambda p:sha256(p.read_bytes()).hexdigest()
def write(name,obj):
    with (HERE/name).open('x') as f:
        json.dump(obj,f,indent=2);f.write(chr(10))

started=time.monotonic()
stage=Path(read(HERE/'preparation-02/stage.json')['stage'])
manifest=read(stage/'bank-manifest.json')
assert read(HERE/'attempt-01/checks.json')['passed']
for name,row in manifest['entries'].items():
    assert digest(ROOT/name)==digest(stage/name)==row['sha256'],name
archive=HERE/'bank-interface-bundle.tar.gz'
assert not archive.exists()
with tarfile.open(archive,'w:gz') as t:
    for name in sorted([*manifest['entries'],'bank-manifest.json']):
        t.add(stage/name,arcname=name,recursive=False)
# Inspect actual archive members and bytes without trusting extraction paths.
with tarfile.open(archive,'r:gz') as t:
    members=t.getmembers()
    assert len(members)==len(manifest['entries'])+1
    for member in members:
        assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
        expected=digest(stage/'bank-manifest.json') if member.name=='bank-manifest.json' else manifest['entries'][member.name]['sha256']
        assert sha256(t.extractfile(member).read()).hexdigest()==expected,member.name

packet_path=Path('data/accounting-master/extended-method-exchanges-20261015/bank-assessment/attempt-03/portable-exchanges.json')
packet=read(ROOT/packet_path);reg=packet['record_registry'];body=lambda r:reg[r['digest']]['body']
q=lambda x: str(Fraction(int(x['n']),int(x['d']))) if x is not None else None
selected=['capital.opening','capital.final','capital.runoff25','capital.runoff40','capital.missing-average']
rows=[]
for identifier in selected:
    case=next(c for c in packet['cases'] if c['id']==identifier)
    inp=body(case['input_ref']);state=body(inp['state_ref']);out=body(case['output_ref'])
    rows.append(dict(case=identifier,input_ref=case['input_ref'],state_ref=inp['state_ref'],output_ref=case['output_ref'],
        balances={k:q(v) for k,v in state['balances'].items()},unpaid_withdrawal=q(state['unpaid_withdrawal']),
        amounts={k:dict(value=q(v['value']),status=v['status'],diagnostics=v['diagnostics']) for k,v in out['amounts'].items()},
        ratios={k:dict(value=q(v['value']),status=v['status'],diagnostics=v['diagnostics']) for k,v in out['ratios'].items()}))
write('worked-case-extract.json',dict(source=str(packet_path),sha256=digest(ROOT/packet_path),rows=rows,
    role='view of already checked retained expectations; not a newly independent oracle'))
components=[read(HERE/'attempt-01'/(x+'.json')) for x in ['bank','bank-v2','bank-assessment']]
exact=read(HERE/'attempt-01/exact-time.json')
checks=sum(len(x['checks']) for x in components)
exchange_count=sum(x['exchanges'] for x in components)
lines=['# Retained bank interfaces consolidated','',
    '27 October 2026. The separate-copy replay passes for all four retained profiles.',
    f'The three original packets reproduce {exchange_count:,} complete exchanges with {checks:,}',
    'source, record, independent-financial, response/world, recovery and adverse checks.',
    f'The exact-time successor reproduces all {len(exact["cases"])} saved full cases and {exact["exact_replays"]} retries;',
    f'{len(exact["controls"])} additional mutations confirm accounting immutability, missing-index refusal,',
    'stale-head refusal and rejection of predecessor requests. All declared inputs',
    f'({len(manifest["entries"]):,} files) retain their hashes in the worktree, copied root and verified archive.',
    '',
    'The target is retained documentary conformance. The quantities actually checked',
    'are complete journals, states, reports and query outcomes from saved cases,',
    'compared with the unchanged independent financial derivations. They agree.',
    'The time successor shares financial code with its predecessor; its full expected',
    'responses come from retained outputs with reference substitution and canonical',
    'dependency-set ordering. No financial numeric value is normalized.',
    '',
    '## What the consolidation establishes','',
    'BankComponents/1 supplies credit, deposits, commitments, fees and settlement',
    'methods. BankComponents/2 supplies separate transfer/option/classification',
    'methods. Their complete annual/lifetime reports and refusal/recovery exchanges',
    'reproduce. Both are conditional AU books. The US BankAssessment/1 has its own',
    'checked dated book, capital calculation, partial outputs and economic queries.',
    'BankAssessmentExactTime/1 preserves that financial meaning under explicit',
    'clock and request-identity rules. The compatibility map names each exact contract.',
    '',
    'The US worked case is already connected: opening book equity 21.2 becomes',
    '23.6 after income 2.4; cash is 21, gross loans 120 and allowance 2.4. The',
    'conditional calculation gives CET1 21.6, admitted allowance 1.5, excess 0.9,',
    'RWA 119.1 and total capital 23.1. A 25 withdrawal funded by borrowing 4',
    'settles fully; a 40 demand with maximum borrowing 10 leaves 9 unpaid.',
    'The ratios stay unchanged in both supplied runoff cases. Missing average',
    'assets leaves leverage unresolved rather than replacing its denominator.',
    'The exact retained fields and references are in worked-case-extract.json.',
    '',
    'The selected manuscript already teaches this separate US case in',
    'sections/bank-prudential.tex. Its preceding simpler bank example has different',
    'equity and an explicitly illustrative ratio; those examples must remain',
    'distinct. Likewise the newer CreditLinkedBook/1 projection, dated nominal',
    'schedule and recovery-intake work are separate profiles and retain their',
    'own closed financial domain and accounting-admission restrictions.',
    '',
    '## Decision','',
    '| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |',
    '| --- | --- | --- | --- | --- | --- |',
    '| Retain reproduction and compatibility supplement | Full saved exchanges agree with retained independent derivations | No financial drift, lost unknowns, false publication or input change | Shared author/source interpretation and finite synthetic premises | Link exact MC21 clauses and integrate navigation | Independent acceptance, actual bank or current-law compliance |',
    '| Preserve the separate within-profile US worked case | Book, funding/runoff and prudential quantities reconcile | No cross-jurisdiction mapping admitted | Actual rule applicability and supplied CECL/eligibility remain unadmitted | Keep applicability question separate from deterministic conformance | Calibrated CECL, lawful distributions or optimized policy |',
    '| Keep bank composition and release open | No same-book /1-to-/2 or AU-to-US migration supplied | Unsupported merge would veto its claim | Composite state, broader methods and independent implementation | Define a same-basis composition only where required, with complete state/report expectations | Whole-bank runtime or MC21 closure |',
    '',
    'Smoke-01 failed because the package scanner missed a dynamically loaded',
    'decoder. Preparation-02 closes the literal-path dependency; smoke-02 and',
    'attempt-01 pass without changing any frozen method or expectation. This was',
    'a packaging failure, not rejection of the bank model. No continuation veto fired.',
    '',
    'Historical Git/index preservation is not rerun. The original audit',
    'preservation results remain separate; the replay explicitly excludes that',
    'workspace-specific check and validates all copied input hashes instead.',
    'No historical preservation claim is silently replaced. This archive is',
    'internal only and is not included in the selected manuscript package.',
    '',
    'Post-run red team: a shared misunderstanding of the accounting source could',
    'survive separate financial code. Supplied legal, valuation, allowance and',
    'eligibility findings are the weakest evidence. A source contradiction,',
    'full-output mismatch or dropped dependency would overturn the affected',
    'bounded result. These deterministic checks do not support stochastic ranking,',
    'forecast accuracy, general completeness or production readiness.',
    'MC21 and independent domain/implementation acceptance remain open.','']
with (HERE/'result.md').open('x') as f:f.write(chr(10).join(lines))
write('preservation.json',dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),passed=True,
    declared_inputs=len(manifest['entries']),original_and_copy_verified=True,archive_members=len(members),
    archive_sha256=digest(archive),archive_bytes=archive.stat().st_size,manifest_sha256=digest(stage/'bank-manifest.json'),
    wall_seconds=time.monotonic()-started,old_git_state_revalidated=False))
print(json.dumps(dict(passed=True,checks=checks,original_exchanges=exchange_count,exact_cases=len(exact['cases']),archive_bytes=archive.stat().st_size)))
