"""Read-only by default; record this documentary E3 protocol once."""
from datetime import datetime, timezone
import argparse, hashlib, json, os, platform, subprocess, sys
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
PLAN = R/'docs/plans/accounting-r05-fiscal-year-protocol-20261023.md'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))
bound = lambda p: {'path': rel(p), 'sha256': sha(p)}
CONTROLS = ['docs/plans/accounting-master-current.md',
            'docs/plans/accounting-master-checkpoint.md',
            'docs/plans/accounting-mission-requirements.md',
            'data/accounting-master/next-plan.md']
OLD = R/'data/accounting-master/r05-conditional-predictive-edition-20261023'
NEW = 'data/accounting-master/r05-fiscal-year-protocol-20261023'


def status_rows():
    raw = subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=no','-z'], cwd=R, text=True)
    return [row for row in raw.split('\0') if row]


def check():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    p = load(U/'protection.json')
    assert p['controls'] == CONTROLS
    for name,digest in p['protected'].items():
        assert sha(R/name) == digest, name
    assert sha(R/'.git/index') == p['index_sha256']
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip() == p['head']
    rows = status_rows()
    assert all(x[:2] == ' M' for x in rows)
    assert {x[3:] for x in rows} == set(p['tracked_dirty'])
    for name,digest in p['tracked_dirty'].items():
        if name not in CONTROLS:
            assert sha(R/name) == digest, name
    c = load(U/'choice.json')
    assert c['selected_design'] == 'repeated_origins'
    assert c['forecast_task']['interval_rule'] == 'next_complete_fiscal_year'
    assert c['forecast_task']['cutoff_rule'] == 'named_information_cutoff_strictly_before_target_start'
    assert list(c['issuer_weights']) == ['apple','caterpillar','jpmorgan','henkel','hsbc','munich_re','saic_motor','ping_an','midea']
    assert set(c['issuer_weights'].values()) == {'1/9'}
    assert c['within_issuer_origin_weights'] is None and c['empirical_execution'] is False
    assert c['historical_vintage_admissions'] == 0
    s = load(U/'calendar-sources.json')
    assert len(s['rows']) == 9 and s['coverage']['path'] == 'data/financial-report-benchmark/coverage.json'
    assert {x['issuer_id'] for x in s['rows']} == set(c['issuer_weights'])
    assert all(x['selected_byte_availability_admitted'] is False for x in s['rows'])
    apple = next(x for x in s['rows'] if x['issuer_id'] == 'apple')
    assert apple['reported_end'] == '2025-09-27' and apple['calendar_observation'].startswith('52_or_53')
    assert all(x['reported_end'] == '2025-12-31' for x in s['rows'] if x['issuer_id'] != 'apple')
    assert (U/'protocol.md').read_text().count('1/9') >= 3
    from check_examples import check as example_check
    examples = example_check()
    assert examples['empirical_observations_used'] == 0 and examples['inference_admitted'] is False
    return p, examples, {'protected_files':len(p['protected']), 'tracked_dirty_paths':len(rows),
        'calendar_sources':len(s['rows']), 'source_anchors':sum(len(x['anchors']) for x in s['rows']),
        'issuer_weights':9, 'example_assertions':examples['calendar_assertions']+examples['strict_prestart_cases']+examples['weight_scenarios'],
        'invalid_example_refusals':examples['invalid_input_refusals'], 'historical_vintage_admissions':0,
        'whole_rows_closed':0, 'readiness':'not_ready', 'manuscript_changed':False,
        'runtime_admitted':False, 'inference_admitted':False, 'empirical_execution':False}


REPLACEMENT = '''The E3 full-year/equal-company protocol is recorded at
data/accounting-master/r05-fiscal-year-protocol-20261023/: the user's exact
answers select the next complete fiscal year with a named information cutoff
strictly before its start, and equal contribution from each of the nine named
companies after the same as-of asset scaling. Retained 2025 reports supply
calendar anchors: Apple uses a 52/53-week year ending on September's last
Saturday; the other eight report calendar years. These anchors do not admit
future calendars, accounting mappings or exact historical byte availability.
The protocol preserves full denominator weights, asynchronous intervals,
first-release outcomes, pre-start forecast locks and target-specific refit
requirements. Ten invalid-input refusals and deterministic calendar/weight
checks pass; no forecast, probability law, inference or runtime is admitted.
Future origin law, within-company time weights, source-vintage admissions,
financial scope, refit/service policy, margin, confidence, inference and
sample design remain unresolved. The predecessor repeated-origins choice and
all 192 false vintage admissions remain unchanged. Read-only replay:
verify.py without flags; completed one-time stages are frozen.

Next E3 dependency: establish a source-timing feasibility matrix and exact
per-issuer future calendar/cutoff policy from retained evidence, then specify
origin grouping, within-issuer time weights and refit/service choices. Keep
unknown byte availability and early outcome releases unknown; do not rerun
completed acquisition, extraction, rendering or literature routes. The full
baseline ladder, CRPS/asset-scaling rules and all empirical/runtime holds
remain in force.

'''


def record(p, examples, checks):
    assert not (U/'completion.json').exists()
    assert not (U/'checks.json').exists()
    assert not (U/'result.md').exists() and not (U/'review.md').exists()
    assert not (U/'controls-after').exists()
    for name in CONTROLS:
        original = (U/'controls-before'/name).read_text()
        marker = 'Next E3 decision dependency:'
        assert original.count(marker) == 1
        first = original.index(marker)
        last = original.index('Completed review evidence:', first)
        updated = original[:first] + REPLACEMENT + original[last:]
        # Also repair the stale six-choice sentence in the current top status.
        updated = updated.replace('six scientific choices remain unselected and all 192 vintage admissions remain false.',
                                  'five legacy scientific choices remain unselected and all 192 vintage admissions remain false.')
        assert 'The E3 full-year/equal-company protocol is recorded at' in updated
        target = R/name
        target.write_text(updated)
        snap = U/'controls-after'/name
        snap.parent.mkdir(parents=True, exist_ok=True)
        snap.write_text(updated)
    result = U/'result.md'
    result.write_text('''# Result — full fiscal-year/equal-company E3 protocol

The two user decisions are now recorded in `choice.json`: next complete
fiscal year with a named pre-start information cutoff, and nine equal issuer
weights of 1/9 after common as-of asset scaling. The retained annual source
records establish the observed calendar distinction, with Apple on a 52/53-week
September year and the other eight issuers on calendar years. The future
calendar and source-vintage admissions remain conditional.

`protocol.md` specifies interval identity, strict chronology, first-release
outcomes, original-weight denominators, asynchronous grouping and refit/tuning
obligations. It does not choose a future-origin law, within-issuer time weights,
financial mapping, missingness/fallback service, margin, inference or sample.
The deterministic checks cover 10 calendar assertions, 5 timing cases, 5
weight scenarios and 10 invalid-input refusals. No empirical observation,
forecast execution or inference is admitted.

Decision table:

| Decision | Primary criterion | Veto status | Uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Record horizon and issuer objective | Exact answers plus 9×1/9 weights | Pass; no chronology contradiction in examples | Future dates and exact cutoffs unresolved | Build source-timing feasibility matrix | No forecast performance or representative population |
| Calendar protocol | Distinct full intervals and pre-start rule | Invalid/overlap bounds refuse admission | Future calendar policy unverified | Obtain retained-date evidence or successor source record | Filing date is not byte availability |
| Aggregation | Original company weights preserved under missing cells | Survivor reweighting refused | Within-company time law unresolved | Specify origin grouping/time weights | Equal companies are not equal cells |
| Scientific promotion | No empirical run requested | Runtime and inference held | Margin/theory/sample absent | Match inference to Q and refit policy | No superiority or default readiness |

This result is a documentary design unit. It does not close any whole MC row.
''')
    review = U/'review.md'
    review.write_text('''# Review — full fiscal-year/equal-company protocol

The skeptical audit passed for the declared documentary scope. The baseline
is the frozen repeated-origins target and full E3 comparator ladder. The checks
do not promote source counts, calendar examples or conditional means into
forecast evidence. The main failure modes—misaligned fiscal labels, late
information, exposed retrospective locks and survivor reweighting—are explicit
refusals or unresolved statuses. The Apple interval extrapolation is labelled
conditional and no financial mapping is admitted.

The strongest alternative explanation is that exact calendar passages may
coexist with an unobserved earlier outcome release or a changed future fiscal
policy. That would overturn prospective admission but not the selected
objective. The weakest evidence is future availability and origin stability;
they require a later source-timing and inference unit.

No reviewer, domain, human or runtime acceptance follows.
''')
    write = lambda path,value: path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    write(U/'checks.json', checks)
    write(U/'run-manifest.json', {'git_commit':p['head'],'branch':p['branch'],
        'environment':sys.executable,'python':platform.python_version(),
        'cpu_gpu':'CPU only; GPU devices intentionally hidden; standard library checks only',
        'data_version':'Retained coverage.json and annual extracted texts; no source acquisition',
        'seeds':'N/A deterministic rational/date fixtures','recorded_utc':datetime.now(timezone.utc).isoformat(),
        'commands':['env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '+rel(U/'prepare.py'),
                    'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '+rel(U/'record_choices.py'),
                    'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '+rel(U/'check_examples.py'),
                    'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '+rel(U/'verify.py'),
                    'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '+rel(U/'verify.py')+' --record',
                    'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '+rel(U/'verify.py')],
        'plan':rel(PLAN),'result':rel(result),'review':rel(review),'output':NEW})
    supplement = R/'data/accounting-master/readability-repair-20261022-theta/r05-fiscal-year-protocol-supplement.json'
    write(supplement, {'scope':'E3 full fiscal-year and equal-company documentary protocol',
        'choice':bound(U/'choice.json'),'calendar_sources':bound(U/'calendar-sources.json'),
        'protocol':bound(U/'protocol.md'),'result':bound(result),'review':bound(review),
        'plan':bound(PLAN),'checks':checks,'candidate_version':'3.48',
        'manuscript_changed':False,'whole_rows_closed':0,'readiness':'not_ready',
        'runtime_admitted':False,'inference_admitted':False,'empirical_execution':False,
        'historical_vintage_admissions':0,'independent_human_acceptance':'pending'})
    files=[x for x in U.rglob('*') if x.is_file() and '__pycache__' not in x.parts] + [PLAN,supplement]
    completion={'status':'complete_documentary_protocol','checks':checks,
        'bindings':{rel(x):sha(x) for x in sorted(files)},
        'predecessor_completion':rel(OLD/'completion.json'),
        'control_replay_policy':'Immutable before/after snapshots; live controls advanced once in this unit'}
    write(U/'completion.json', completion)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--record',action='store_true'); a=ap.parse_args()
    p,examples,checks=check()
    if a.record: record(p,examples,checks)
    if (U/'completion.json').exists():
        c=load(U/'completion.json')
        for name,digest in c['bindings'].items(): assert sha(R/name)==digest,name
        assert c['checks']==checks==load(U/'checks.json')
        print(json.dumps({'status':'recorded and verified' if a.record else 'read-only replay passed',**checks}))
    else:
        print(json.dumps({'status':'read-only preflight passed; not yet recorded',**checks}))


if __name__ == '__main__': main()
