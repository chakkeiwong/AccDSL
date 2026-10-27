"""Preserve both versions of the predecessor's post-completion control repair."""
import ast
import hashlib
import json
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
OLD = R/'data/accounting-master/r05-fiscal-year-protocol-20261023'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out = U/'history-repair'
    assert not out.exists()
    current = json.loads((OLD/'completion.json').read_text())
    original = json.loads((OLD/'completion.json').read_text())
    # Exact four initial hashes were printed before the post-completion edits.
    expected = {
        'data/accounting-master/next-plan.md': '2a7bf86955fd707bda5bdff70fe023438694f3308273cc2adf5752747aeb0ad2',
        'docs/plans/accounting-master-checkpoint.md': '0609e2dec448b3763ddb9998dcca9bc94f9941ef87df88d32f75aa2ec0ef096d',
        'docs/plans/accounting-master-current.md': '556a25a8243ce6dd50dadec9042407c4e9846a221fd1acd8bb77f3a1d6770cf0',
        'docs/plans/accounting-mission-requirements.md': '26da107e2e75a4e3e12240b520b9b29fcef8d5b4429fc875d6fb82ee3261c679'}
    tree = ast.parse((OLD/'verify.py').read_text())
    replacement = next(ast.literal_eval(n.value) for n in tree.body
                       if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id == 'REPLACEMENT' for t in n.targets))
    staged = []
    corrections = []
    for name,digest in expected.items():
        before = (OLD/'controls-before'/name).read_text()
        first = before.index('Next E3 decision dependency:')
        last = before.index('Completed review evidence:', first)
        initial = before[:first] + replacement + before[last:]
        initial = initial.replace('six scientific choices remain unselected and all 192 vintage admissions remain false.',
                                  'five legacy scientific choices remain unselected and all 192 vintage admissions remain false.')
        assert hashlib.sha256(initial.encode()).hexdigest() == digest
        path = OLD/'controls-after'/name
        key = str(path.relative_to(R))
        assert current['bindings'][key] == sha(path)
        assert sha(path) != digest
        original['bindings'][key] = digest
        staged.append((out/'initial-controls-after'/name, initial.encode()))
        corrections.append({'control': name, 'initial_sha256': digest,
                            'current_recorded_sha256': sha(path),
                            'initial_reconstruction': str((out/'initial-controls-after'/name).relative_to(R)),
                            'current_frozen_snapshot': key})
    assert all(sha(R/name) == digest for name,digest in current['bindings'].items())
    staged.extend([
        (out/'initial-completion-reconstructed.json', (json.dumps(original,ensure_ascii=False,indent=2)+'\n').encode()),
        (out/'current-completion-observed.json', (OLD/'completion.json').read_bytes())])
    for path,data in staged:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as f:
            f.write(data)
    record = {'issue': 'Four controls-after snapshots and their completion hashes were edited after recording',
              'effect': 'The immutable completion-history claim was wrong for those snapshots; content replay alone did not detect the rewritten hashes',
              'scope': 'No source calendar, user answer, calculation, protocol, or earlier predecessor file changed in this repair',
              'initial_snapshot_evidence': 'Initial four hashes printed by rg in tool history before the edits; snapshots reconstructed from protected before snapshots and literal REPLACEMENT',
              'initial_completion_evidence': 'Reconstructed JSON with those four original bindings; not a claim that an original copy was retained',
              'current_predecessor_completion_sha256': sha(OLD/'completion.json'),
              'corrections': corrections,
              'new_recovery_files': {str(path.relative_to(R)): sha(path) for path,_ in staged},
              'remaining_limit': 'Completion hashes do not independently authenticate past timestamps or tamper resistance',
              'predecessor_mutated_by_this_recovery': False,
              'scientific_choices_changed': False}
    with (out/'correction.json').open('x') as f:
        json.dump(record,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps({'reconstructed_initial_snapshots':4,'completion_versions_preserved':2,
                      'predecessor_files_changed':0,'historical_integrity_issue':'explicitly_reconciled'}))


if __name__ == '__main__':
    main()
