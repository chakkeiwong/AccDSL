"""Preserve frozen POCI financial targets while tightening write-off admission."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def main():
    original = json.loads((OUT / 'authored-cases.json').read_text())
    successor = deepcopy(original)
    for case in successor['cases']:
        request = case['request']
        request['acquisition']['findings']['no_full_or_partial_writeoff_required'] = True
        for event in request['events']:
            if event['operation'] in ('advance', 'revise_credit'):
                event['findings']['no_full_or_partial_writeoff_required'] = True
    for old, new in zip(original['cases'], successor['cases']):
        assert old['expected'] == new['expected']
        assert old['uncollected_contractual'] == new['uncollected_contractual']
    target = OUT / 'authored-cases-v2.json'
    lockpath = OUT / 'input-lock-v2.json'
    assert not target.exists() and not lockpath.exists()
    oldlock = json.loads((OUT / 'input-lock.json').read_text())
    for entry in oldlock['files']:
        assert hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest() == entry['sha256']
    target.write_text(json.dumps(successor, indent=2) + '\n')
    additional = [OUT / 'input-lock.json', Path(__file__).resolve(), target, OUT / 'admission-repair.md']
    entries = oldlock['files'] + [dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in additional]
    lockpath.write_text(json.dumps(dict(files=entries), indent=2) + '\n')
    print(json.dumps(dict(cases=len(successor['cases']), locked_files=len(entries), financial_targets='unchanged')))


if __name__ == '__main__':
    main()
