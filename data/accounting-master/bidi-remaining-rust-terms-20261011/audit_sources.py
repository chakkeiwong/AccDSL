"""Bind 13 exact crate editions, grant texts and bounded provenance findings."""
import hashlib
import json
import re
import tarfile
import tomllib
from pathlib import Path, PurePosixPath

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PARENT = ROOT / 'data/accounting-master/easyocr-python-bidi-20261011/sources/python_bidi-0.6.11.tar.gz'
COPYRIGHT_WORDS = ('license', 'licence', 'copying', 'copyright', 'notice')
EXTRA = {
    'pyo3-ffi': ['src/compat/mod.rs', 'src/pyerrors.rs'],
    'portable-atomic': ['build.rs', 'src/imp/atomic128/detect/x86_64.rs', 'src/imp/fallback/mod.rs', 'src/imp/fallback/seq_lock.rs', 'src/imp/fallback/seq_lock_wide.rs', 'src/imp/fallback/utils.rs', 'src/imp/interrupt/armv6m.rs', 'src/imp/interrupt/avr.rs', 'src/imp/interrupt/msp430.rs', 'src/imp/msp430.rs', 'src/utils.rs'],
    'libc': ['src/fuchsia/aarch64.rs'],
    'unicode-ident': ['src/tables.rs'],
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2) + '\n')

def main():
    assert not (OUT/'completion.json').exists(), 'Closed source unit: use separate verification output'
    assert sha(PARENT.read_bytes()) == '034090c597af250d699299d7e7f1e83eb016f9e47b3b707bd89ab2bdec77bce0'
    with tarfile.open(PARENT) as tar:
        locked = tomllib.loads(tar.extractfile('python_bidi-0.6.11/Cargo.lock').read().decode())['package']
    packages = [p for p in locked if p['name'] not in {'python-bidi', 'pyo3', 'unicode-bidi'}]
    checks, records, hits, skipped = [], [], [], []
    def check(name, yes):
        checks.append({'check': name, 'passed': bool(yes)})
    check('fixed thirteen-package population', len(packages) == 13)
    for p in packages:
        name, version = p['name'], p['version']
        stem = name + '-' + version
        a = OUT/'sources'/(stem+'.crate')
        meta_path = OUT/'sources'/(stem+'.json')
        meta = json.loads(meta_path.read_text())['version']
        check(stem+' metadata edition', meta['crate'] == name and meta['num'] == version)
        check(stem+' immutable source identity', sha(a.read_bytes()) == meta['checksum'] == p['checksum'])
        check(stem+' archive size and non-yanked', a.stat().st_size == meta['crate_size'] and not meta['yanked'])
        witnesses = []
        with tarfile.open(a) as tar:
            members = tar.getmembers()
            check(stem+' bounded ordinary files', all(m.isfile() and m.size < 4000000 for m in members) and sum(m.size for m in members) < 20000000)
            names = tar.getnames()
            check(stem+' safe member paths', all(n.startswith(stem+'/') and '..' not in PurePosixPath(n).parts and not PurePosixPath(n).is_absolute() for n in names))
            source = tomllib.loads(tar.extractfile(stem+'/Cargo.toml').read().decode())['package']
            check(stem+' source edition', source['name'] == name and source['version'] == version)
            check(stem+' source/registry licence agreement', source['license'] == meta['license'])
            wanted = [n for n in names if any(w in PurePosixPath(n).name.lower() for w in COPYRIGHT_WORDS)]
            wanted += [stem+'/Cargo.toml', stem+'/Cargo.toml.orig']
            wanted += [stem+'/README.md'] if stem+'/README.md' in names else []
            wanted += [stem+'/'+n for n in EXTRA.get(name, []) if stem+'/'+n in names]
            for member in dict.fromkeys(wanted):
                raw = tar.extractfile(member).read()
                dest = OUT/'inspected'/member
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    assert dest.read_bytes() == raw
                else:
                    dest.write_bytes(raw)
                witnesses.append({'member': member, 'path': str(dest.relative_to(ROOT)), 'sha256': sha(raw), 'line_count': len(raw.decode().splitlines())})
            if name == 'target-lexicon':
                body = tar.extractfile(stem+'/LICENSE').read().decode()
                check(stem+' Apache and LLVM exception body', 'Apache License' in body and 'LLVM Exceptions' in body and 'Sections 4(a), 4(b) and 4(d)' in body and 'GPLv2' in body)
            else:
                mit = tar.extractfile(stem+'/LICENSE-MIT').read().decode()
                apache = tar.extractfile(stem+'/LICENSE-APACHE').read().decode()
                check(stem+' MIT grant and retention text', 'Permission is hereby granted' in mit and 'copyright notice and this permission notice' in mit and 'shall be included' in mit)
                check(stem+' Apache grant and notice text', 'Version 2.0, January 2004' in apache and '4. Redistribution.' in apache and 'NOTICE' in apache)
            if name == 'unicode-ident':
                body = tar.extractfile(stem+'/LICENSE-UNICODE').read().decode()
                readme = tar.extractfile(stem+'/README.md').read().decode()
                check(stem+' additional Unicode terms', 'COPYRIGHT AND PERMISSION NOTICE' in body and 'associated' in body and 'Documentation' in body and 'terms of both' in readme)
            for member in members:
                if not member.name.endswith(('.rs', '.md', '.txt', '.toml')):
                    continue
                if member.size > 500000:
                    skipped.append({'member':member.name, 'bytes':member.size, 'reason':'bounded diagnostic scan excludes files over 500 KB; source archive retained'})
                    continue
                text = tar.extractfile(member).read().decode('utf-8', 'replace')
                for i, line in enumerate(text.splitlines(), 1):
                    if re.search(r'(?i)SPDX|licen[cs]ed|copyright|permission notice|derived from|adapted from|ported from|third.party', line):
                        hits.append({'crate':name, 'member':member.name, 'line':i, 'text':line})
        records.append({'name':name, 'version':version, 'archive':str(a.relative_to(ROOT)), 'sha256':sha(a.read_bytes()), 'registry_metadata':str(meta_path.relative_to(ROOT)), 'metadata_sha256':sha(meta_path.read_bytes()), 'declared_licence':source['license'], 'rust_version':source.get('rust-version'), 'witnesses':witnesses, 'scope':'source declarations and retained terms; not final compiled contents or legal clearance'})
    report = {'checks':checks, 'passed':sum(x['passed'] for x in checks), 'failed':sum(not x['passed'] for x in checks)}
    write('source-checks.json', report)
    write('source-ledger.json', {'parent_archive':str(PARENT.relative_to(ROOT)), 'parent_sha256':sha(PARENT.read_bytes()), 'packages':records, 'population':13, 'scope':'fixed candidate lockfile, not an installed or complete build graph'})
    write('header-scan.json', {'role':'explanatory diagnostic; no exhaustive clearance', 'hits':hits, 'excluded_large_files':skipped})
    print(json.dumps({'passed':report['passed'], 'failed':report['failed'], 'source_packages':len(records), 'header_hits':len(hits), 'excluded_large_files':len(skipped)}))
    if report['failed']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
