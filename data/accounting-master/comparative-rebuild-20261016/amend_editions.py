"""Preserve the original catalog and add its missing covered comparative year."""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]


def main():
    lock=json.loads((OUT/'input-lock.json').read_text())
    for item in lock['files']:
        assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256']
    catalog=json.loads((OUT/'synthetic-editions.json').read_text())
    original=next(x for x in catalog['editions'] if x['id']=='original-2024')
    assert original['years']==[2024]
    original['years']=[2023,2024]
    output=OUT/'synthetic-editions-v2.json';assert not output.exists()
    output.write_text(json.dumps(catalog,indent=2)+'\n')
    for p in [OUT/'input-lock.json',OUT/'amend_editions.py',OUT/'catalog-audit.md',output]:
        lock['files'].append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    successor=OUT/'input-lock-v2.json';assert not successor.exists()
    successor.write_text(json.dumps(lock,indent=2)+'\n')
    print(json.dumps(dict(locked_files=len(lock['files']),original_2024_years=original['years'])))


if __name__=='__main__':main()
