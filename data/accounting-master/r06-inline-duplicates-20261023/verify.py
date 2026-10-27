"""Read-only documentary verification by default; final recording is once."""
import argparse
from datetime import datetime, timezone
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

sys.dont_write_bytecode = True
U = Path(__file__).resolve().parent
R = U.parents[2]
PLAN = R / 'docs/plans/accounting-r06-inline-duplicates-20261023.md'
REVIEW = R / 'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT = REVIEW / 'r06-inline-duplicates-supplement.json'
IDS = ('01-primer2013', '02-spec2013', '03-primer2026', '04-spec2026',
       '05-spechistory', '06-primerhistory')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def binding(value):
    assert sha(R / value['path']) == value['sha256'], value['path']


def check():
    p = load(U / 'protection.json')
    for name, digest in p['protected'].items():
        assert sha(R / name) == digest, name
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip() == p['head']
    assert sha(R / '.git/index') == p['index_sha256']
    raw = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True)
    rows = [x for x in raw.split('\0') if x]
    assert {x[3:] for x in rows} == set(p['tracked_dirty'])
    assert all(x[:2] == ' M' for x in rows)
    for name, digest in p['tracked_dirty'].items():
        if name not in p['controls']:
            assert sha(R / name) == digest, name
    d = load(U / 'source-ledger.json')
    assert set(d['sources']) == set(IDS) | {'note2018'}
    normalized = {}
    for key, value in d['sources'].items():
        binding(value)
        normalized[key] = ' '.join((R / value['path']).read_text().split())
    parser_path = R / 'data/accounting-master/r06-duplicates-guidance-20261023/extract.py'
    spec = importlib.util.spec_from_file_location('authored_retained_text_parser', parser_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert len(list((U / 'sources').glob('*.receipt.json'))) == 6
    texts = {}
    for ident in IDS:
        receipt = load(U / 'sources' / (ident + '.receipt.json'))
        body = U / 'sources' / (ident + '.body')
        meta = load(U / 'sources' / (ident + '.structure.json'))
        binding(d['new_documents'][ident])
        assert receipt['id'] == ident
        assert receipt['exit_code'] == 0 and receipt['metrics']['http_code'] == 200
        assert receipt['url'] in PLAN.read_text()
        assert body.stat().st_size == receipt['metrics']['size_download'] <= 12582912
        assert receipt['metrics']['num_redirects'] <= 5
        assert receipt['metrics']['time_total'] <= 45
        assert all(x in receipt['command'] for x in ('--connect-timeout 15', '--max-time 45', '--max-redirs 5', '--max-filesize 12582912'))
        assert all((U / 'sources' / (ident + suffix)).is_file() for suffix in ('.headers', '.stderr'))
        assert sha(body) == meta['body_sha256']
        assert sha(U / 'sources' / (ident + '.visible.txt')) == meta['visible_sha256']
        assert sha(parser_path) == meta['parser_sha256']
        parser = module.Text()
        parser.feed(body.read_text())
        assert '\n'.join(parser.parts) + '\n' == (U / 'sources' / (ident + '.visible.txt')).read_text()
        assert parser.images == meta['images'] and parser.links == meta['links']
        assert parser.headings == meta['headings'] and parser.table_count == meta['table_count']
        assert meta['images'] == ([{'src': 'css/assets/img/xbrl-logo.png', 'alt': 'XBRL'}] if ident.endswith('history') else [])
        texts[ident] = parser.parts
    anchors = {a['id']: a for a in d['anchors']}
    assert len(anchors) == len(d['anchors']) == 42
    for a in d['anchors']:
        first, last = a['normalized_character_span']
        assert normalized[a['source']][first:last] == a['quote'], a['id']
    body = (U / 'sources/04-spec2026.body').read_text()
    for ident in ('S2026-lang', 'S2026-lang-root'):
        a = anchors[ident]
        assert a['support_class'] == 'SOURCE_CLARIFICATION_NON_NORMATIVE'
    start = body.index('It should be noted that unlike')
    assert body.rfind('<div class="nonNormativeNote">', 0, start) > body.rfind('</div>', 0, start)
    assert d['clarification_html_class'] == 'nonNormativeNote'
    comparisons = load(U / 'version-comparison.json')['rows']
    assert len(comparisons) == 9
    for row in comparisons:
        blocks = []
        for ident in ('02-spec2013', '04-spec2026'):
            lines = texts[ident]
            first = lines.index(row['section'])
            last = lines.index(row['until_exclusive'], first + 1)
            blocks.append(lines[first:last])
        assert row['equal_visible_text'] == (blocks[0] == blocks[1])
        assert row['diff'] == list(difflib.unified_diff(*blocks, fromfile='2013', tofile='2026', n=2, lineterm=''))
    assert sum(row['equal_visible_text'] for row in comparisons) == 4
    claims = load(U / 'claim-support-ledger.json')['claims']
    obligations = load(U / 'obligation-comparison.json')['rows']
    assert len(claims) == len(obligations) == 14
    assert {c['id'] for c in claims} == {r['id'] for r in obligations}
    for row in claims + obligations:
        assert row['support'] and set(row['support']) <= set(anchors)
    reading = load(U / 'reading-ledger.json')
    assert reading['whole_specification_read'] is False
    assert {r['source'] for r in reading['sources']} == set(IDS)
    for row in reading['sources']:
        binding(row['binding'])
        n = len(texts[row['source']])
        assert row['visible_lines'] == n
        spans = row['actually_read_spans']
        assert all(1 <= a <= b <= n for a, b in spans)
        assert all(spans[i][1] < spans[i + 1][0] for i in range(len(spans) - 1))
        if row['source'].endswith('history'):
            assert spans == [[1, n]]
    for name in ('source-support', 'citation-venue', 'backward-snowball', 'forward-snowball', 'claim-support', 'omission-risk'):
        assert load(U / (name + '-ledger.json'))
    a, o = load(REVIEW / 'assessment-successor.json'), load(REVIEW / 'operation-successor.json')
    assert (len(a['rows']), len(a['interactions']), len(o['rows'])) == (53, 6, 46)
    assert a['readiness'] == o['readiness'] == 'not_ready'
    for name in ('result.md', 'review.md', 'recovery.md'):
        assert (U / name).read_text().strip()
    assert 'not_ready' in (U / 'result.md').read_text()
    return p, {'documents': 6, 'anchors': 42, 'claims': 14,
               'obligation_rows': 14, 'version_blocks': 9, 'identical_selected_blocks': 4,
               'research_ledgers': 6, 'whole_specification_read': False,
               'protected_files': len(p['protected']), 'tracked_dirty_paths': len(rows),
               'whole_rows_closed': 0, 'readiness': 'not_ready',
               'manuscript_changed': False, 'runtime_admitted': False}


def record(p, checks):
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    for path in (U / 'completion.json', U / 'checks.json', U / 'run-manifest.json', SUPPLEMENT):
        assert not path.exists(), path
    assert not (U / 'controls-after').exists()
    replacement = '''The Inline duplicate-processing comparison is complete at
data/accounting-master/r06-inline-duplicates-20261023/: six official documents,
42 anchors, 14 obligation rows and nine selected edition comparisons. Optional
item reduction remains subject to every input mapping obligation; the note's
complete-duplicate class is insufficient as a merging predicate. The added
language paragraph is a non-normative clarification; Primer tension remains.
No schema, suite, processor, policy or manuscript promotion follows. No whole
row closes. Read-only replay: verify.py without flags; one-time stages frozen.

Next: inspect retained sources for the exact Formula1.0 references behind the
2018 note's section5.2 processor claims. Audit a fresh bounded source plan before
acquisition or new technical conclusions. Other ready R03–R06 work remains
eligible; completed source checks and manuscript reviews stay frozen.

'''
    marker = 'Next: check retained sources for the exact2013 Inline XBRL Primer and'
    edits = []
    for name in p['controls']:
        assert (R / name).read_bytes() == (U / 'controls-before' / name).read_bytes(), name
        before = (R / name).read_text()
        assert before.count(marker) == 1, name
        start = before.index(marker)
        end = before.index('Completed review evidence:', start)
        edits.append((name, before[:start] + replacement + before[end:]))
    receipts = [load(U / 'sources' / (ident + '.receipt.json')) for ident in IDS]
    prefix = 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    stages = [prefix + rel(U / 'prepare.py')]
    stages += [prefix + rel(U / 'extract.py') + ' ' + ident for ident in IDS]
    stages += [prefix + rel(U / name) for name in
               ('recover_check.py', 'inspect_comparison.py', 'build_records.py', 'write_ledgers.py')]
    stages += [prefix + rel(U / 'verify.py') + ' --record', prefix + rel(U / 'verify.py')]
    # Every prerequisite and planned live edit is checked before first mutation.
    write(U / 'checks.json', checks)
    write(U / 'run-manifest.json', {
        'git_commit': p['head'], 'branch': p['branch'], 'environment': sys.executable,
        'python': platform.python_version(),
        'cpu_gpu': 'CPU only; GPU devices intentionally hidden; authored standard-library tools only',
        'data_version': 'Exact retained2013/2026 Inline editions and frozen2018 note; source-ledger.json',
        'seeds': 'N/A deterministic documentary inquiry; no stochastic comparison',
        'inquiry_started_utc': p['started_utc'], 'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'wall_time': 'Continuous active work not measured across restart; observed UTC receipt brackets are not process durations',
        'request_seconds': [r['metrics']['time_total'] for r in receipts],
        'commands': [r['command'] for r in receipts] + stages,
        'reading': rel(U / 'reading-ledger.json'), 'recovery': rel(U / 'recovery.md'),
        'plan': rel(PLAN), 'result': rel(U / 'result.md'), 'output': rel(U)})
    write(SUPPLEMENT, {
        'scope': 'Dated Inline duplicate mapping comparison; internal source preparation',
        'candidate_version': '3.48',
        'candidate_pdf': bind(R / 'docs/design/proposal/manuscript-readability-20261022-theta/accounting-product-proposal.pdf'),
        'protected_assessment': bind(REVIEW / 'assessment-successor.json'),
        'protected_operations': bind(REVIEW / 'operation-successor.json'),
        'completed_author_review': bind(REVIEW / 'regression/completion.json'),
        'all_original_obligations': 53, 'interactions': 6, 'operations': 46,
        'whole_rows_closed': 0, 'readiness': 'not_ready', 'plan': bind(PLAN),
        'result': bind(U / 'result.md'), 'review': bind(U / 'review.md'), 'checks': checks,
        'manuscript_changed': False, 'runtime_admitted': False,
        'independent_human_acceptance': 'pending'})
    for name, after in edits:
        (R / name).write_text(after)
        target = U / 'controls-after' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('x') as stream:
            stream.write(after)
    assert check()[1] == checks
    files = [path for path in U.rglob('*') if path.is_file() and '__pycache__' not in path.parts]
    files += [PLAN, SUPPLEMENT]
    write(U / 'completion.json', {
        'status': 'complete_source_comparison_no_policy_promotion', 'checks': checks,
        'bindings': {rel(path): sha(path) for path in sorted(files)},
        'control_replay_policy': 'Immutable before/after snapshots; live controls may advance in successor units'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    p, checks = check()
    if args.record:
        record(p, checks)
    if (U / 'completion.json').exists():
        completion = load(U / 'completion.json')
        for name, digest in completion['bindings'].items():
            assert sha(R / name) == digest, name
        assert load(U / 'checks.json') == completion['checks'] == checks
        status = 'recorded and verified' if args.record else 'read-only replay passed'
    else:
        status = 'read-only preflight passed; not yet recorded'
    print(json.dumps({'status': status, **checks}))


if __name__ == '__main__':
    main()
