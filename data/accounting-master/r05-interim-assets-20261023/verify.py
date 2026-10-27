"""Read-only source, state and completed-record checks; never writes."""
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess

U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())

def check():
    assert os.environ['CUDA_VISIBLE_DEVICES'] == '-1'
    start = load(U / 'start.json')
    assert sha(R / '.git/index') == start['index_sha256']
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip() == start['head']
    state = subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=no','-z'],cwd=R,text=True)
    dirty = [x for x in state.split('\0') if x]
    assert all(x[:2] == ' M' for x in dirty)
    assert {x[3:] for x in dirty} == set(start['tracked_dirty'])
    for name,digest in start['tracked_dirty'].items():
        if name not in start['controls']:
            assert sha(R / name) == digest, name
    for name in start['controls']:
        assert sha(U / 'controls-before' / name) == start['tracked_dirty'][name]
    data = load(U / 'candidates.json')
    for name in ('timing_matrix','coverage','actually_viewed_source_page'):
        assert sha(R / data[name]['path']) == data[name]['sha256']
    timing = load(R / data['timing_matrix']['path'])
    expected = {r['issuer_id'] for r in timing['rows'] if r['input_candidate_kind'] == 'latest_interim'}
    assert len(data['rows']) == 9 and {r['issuer_id'] for r in data['rows']} == expected
    for row in data['rows']:
        for key in ('original','text'):
            assert sha(R / row[key]['path']) == row[key]['sha256']
        lines = (R / row['text']['path']).read_text().split('\n')
        for anchor in row['anchors']:
            assert '\n'.join(lines[anchor['start_line']-1:anchor['end_line']]) == anchor['quote']
        assert Fraction(row['reported_total_assets']) > 0
        assert Fraction(row['amount_in_currency_units']) == Fraction(row['reported_total_assets'])*row['unit_multiplier']
        prior = timing['rows'][int(row['timing_matrix_pointer'].rsplit('/',1)[1])]
        assert row['document_id'] == prior['document_id']
        assert row['date_roles'] == prior['date_roles']
        assert row['original']['sha256'] == prior['selected']['sha256']
        assert row['as_of_admission'] is False and row['selected_for_actual_cutoff'] is False
        assert row['selected_byte_available_at'] is None
        for role in row['date_roles']:
            assert sha(R / role['source']['path']) == role['source']['sha256']
    old = load(R / 'data/accounting-master/r05-vintage-admission-20261018/reconciliation.json')
    assert len(old['rows']) == 192 and all(r['as_of_admission'] is False for r in old['rows'])
    checks = {'interim_candidates':9,'source_anchors':sum(len(r['anchors']) for r in data['rows']),
              'dated_role_rows':sum(any(d['date'] for d in r['date_roles']) for r in data['rows']),
              'actually_viewed_pages':1,'as_of_admissions':0,'tracked_dirty_paths':len(dirty),
              'whole_rows_closed':0,'empirical_execution':False,'readiness':'not_ready'}
    if (U / 'completion.json').exists():
        complete = load(U / 'completion.json')
        assert complete['checks'] == checks
        for name,digest in complete['bindings'].items():
            assert sha(R / name) == digest, name
    return checks

if __name__ == '__main__':
    print(json.dumps({'status':'read-only checks passed',**check()}))
