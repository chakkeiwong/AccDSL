"""Check direct crate source identities and retain exact licence witnesses."""
import hashlib
import json
import tarfile
import tomllib
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PARENT = ROOT / 'data/accounting-master/easyocr-python-bidi-20261011/sources/python_bidi-0.6.11.tar.gz'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    checks, records = [], []
    def check(name, yes):
        checks.append({'check': name, 'passed': bool(yes)})
    assert digest(PARENT.read_bytes()) == '034090c597af250d699299d7e7f1e83eb016f9e47b3b707bd89ab2bdec77bce0'
    with tarfile.open(PARENT) as parent:
        lock = tomllib.loads(parent.extractfile('python_bidi-0.6.11/Cargo.lock').read().decode())
    locked = {p['name']: p for p in lock['package']}
    for name, version in [('pyo3', '0.29.0'), ('unicode-bidi', '0.3.18')]:
        stem = name + '-' + version
        metadata = OUT / 'sources' / (stem + '.json')
        meta = json.loads(metadata.read_text())['version']
        archive = OUT / 'sources' / (stem + '.crate')
        raw = archive.read_bytes()
        check(stem + ' metadata identity', meta['crate'] == name and meta['num'] == version and not meta['yanked'])
        check(stem + ' archive identity', digest(raw) == meta['checksum'] == locked[name]['checksum'])
        check(stem + ' archive size', len(raw) == meta['crate_size'])
        witnesses = []
        with tarfile.open(archive) as tar:
            members = tar.getmembers()
            check(stem + ' bounded member inventory', all(m.isfile() and m.size < 2000000 for m in members))
            declared = tomllib.loads(tar.extractfile(stem + '/Cargo.toml').read().decode())['package']
            original = tomllib.loads(tar.extractfile(stem + '/Cargo.toml.orig').read().decode())['package']
            check(stem + ' source version', declared['name'] == original['name'] == name and declared['version'] == original['version'] == version)
            check(stem + ' licence declarations agree', meta['license'] == declared['license'] == original['license'] == 'MIT OR Apache-2.0')
            wanted = ['Cargo.toml', 'Cargo.toml.orig', 'LICENSE-APACHE', 'LICENSE-MIT', 'README.md']
            wanted += ['COPYRIGHT', 'src/lib.rs', 'src/char_data/tables.rs'] if name == 'unicode-bidi' else ['pyo3-runtime/LICENSE-APACHE', 'pyo3-runtime/LICENSE-MIT']
            for rel in wanted:
                body = tar.extractfile(stem + '/' + rel).read()
                target = OUT / 'inspected' / stem / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    assert target.read_bytes() == body
                else:
                    target.write_bytes(body)
                text = body.decode()
                if rel == 'LICENSE-MIT':
                    check(stem + ' MIT grant and notice condition', 'Permission is hereby granted' in text and 'copyright notice and this permission notice' in text and 'shall be included' in text)
                if rel == 'LICENSE-APACHE':
                    check(stem + ' Apache edition and distribution clauses', 'Version 2.0, January 2004' in text and '4. Redistribution.' in text and 'NOTICE' in text and '3. Grant of Patent License.' in text)
                witnesses.append({'archive_member': stem + '/' + rel, 'path': str(target.relative_to(ROOT)), 'sha256': digest(body), 'lines': len(text.splitlines())})
            if name == 'pyo3':
                check('pyo3 bundled runtime licence bytes agree', tar.extractfile(stem + '/LICENSE-MIT').read() == tar.extractfile(stem + '/pyo3-runtime/LICENSE-MIT').read() and tar.extractfile(stem + '/LICENSE-APACHE').read() == tar.extractfile(stem + '/pyo3-runtime/LICENSE-APACHE').read())
        records.append({'crate': name, 'version': version, 'archive_path': str(archive.relative_to(ROOT)), 'sha256': digest(raw), 'metadata_path': str(metadata.relative_to(ROOT)), 'metadata_sha256': digest(metadata.read_bytes()), 'declared_licence': meta['license'], 'rust_version': declared['rust-version'], 'scope': 'exact direct crate source only; not final wheel or transitive clearance', 'witnesses': witnesses})
    report = {'checks': checks, 'passed': sum(c['passed'] for c in checks), 'failed': sum(not c['passed'] for c in checks)}
    (OUT / 'source-checks.json').write_text(json.dumps(report, indent=2)+'\n')
    (OUT / 'source-ledger.json').write_text(json.dumps({'parent_archive': str(PARENT.relative_to(ROOT)), 'parent_sha256': digest(PARENT.read_bytes()), 'crates': records, 'nonclaims': ['No installed build or wheel examined', 'No complete transitive terms clearance', 'No licence selected or distribution approved']}, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ['passed', 'failed']}))
    if report['failed']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
