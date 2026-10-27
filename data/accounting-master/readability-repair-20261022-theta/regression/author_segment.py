"""Expand explicit compact author judgments; never infer reading evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
FIELDS = ('entry_belief', 'open_question', 'parent_contribution',
          'belief_update', 'exit_question', 'removal_verdict', 'swap_verdict',
          'entry_verdict', 'exit_verdict', 'promise_verdict',
          'distinct_contribution_verdict')
EQUATION_FIELDS = ('exposition_role', 'symbols_units_domain',
                  'assumptions_timing', 'source_and_equality',
                  'interpretation', 'transition')

def main():
    draft = Path(sys.argv[1]).resolve()
    assert draft.is_relative_to(OUT)
    value = json.loads(draft.read_text())
    first, last = value['physical_pages']
    assert value['actual_view_order'] == list(range(first, last + 1))
    ledger = json.loads((OUT / 'structure-ledger.json').read_text())
    nodes = {n['id']: n for n in ledger['nodes']}
    judgments = {}
    for row in value.pop('authored_nodes'):
        identifier, pages, prose, *equations = row
        assert identifier in nodes and identifier not in judgments
        assert nodes[identifier]['reading_status'] == 'pending', identifier
        assert len(prose) == len(FIELDS) and all(isinstance(s, str) and s.strip() for s in prose)
        assert 1 <= pages[0] <= pages[1] <= last
        judgment = {'physical_pages': pages, **dict(zip(FIELDS, prose))}
        if nodes[identifier]['kind'] == 'equation':
            assert len(equations) == 1 and len(equations[0]) == len(EQUATION_FIELDS)
            assert all(isinstance(s, str) and s.strip() for s in equations[0])
            judgment['equation'] = dict(zip(EQUATION_FIELDS, equations[0]))
        else:
            assert not equations
        judgments[identifier] = judgment
    value['node_judgments'] = judgments
    value['authored_input'] = {'path': str(draft.relative_to(OUT)),
                              'sha256': hashlib.sha256(draft.read_bytes()).hexdigest()}
    target = OUT / f'segment-{first:03}-{last:03}.json'
    assert not target.exists(), 'Completed segments must never be overwritten'
    with target.open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    subprocess.run([sys.executable, '-B', str(OUT / 'initialize.py'), 'record',
                    '--segment-path', str(target)], check=True)

if __name__ == '__main__':
    main()
