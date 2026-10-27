"""Bounded CPU-only reference verification; record once, then replay read-only."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import os
import platform
import subprocess
import sys
import time
import traceback

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from portable_context import context
from portable import canonical, decode, schemas
from checks import conformance


def filehash(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def protected():
    baseline = decode((HERE.parent/'company-recovery-20261023/baseline.json').read_bytes())
    check_locks(baseline)
    for folder in ['company-recovery-20261023', 'company-expressions-20261023',
                   'company-family-20261023', 'company-path-admission-20261023']:
        for path in (HERE.parent/folder).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and 'control-before' not in path.parts:
                baseline[str(path.relative_to(ROOT))] = filehash(path)
    candidate = ROOT/'docs/design/proposal/manuscript-company-language-20261023'
    for path in candidate.rglob('*'):
        if path.is_file() and path.suffix in ['.tex', '.bib', '.pdf']:
            baseline[str(path.relative_to(ROOT))] = filehash(path)
    return baseline


def check_locks(locks):
    changed = [name for name, h in locks.items() if not (ROOT/name).is_file() or filehash(ROOT/name) != h]
    if changed:
        raise ValueError('protected files changed: '+repr(changed[:5]))


def main():
    mode = sys.argv[1] if len(sys.argv) == 2 else '--check'
    if mode not in ['--check', '--record', '--replay']:
        raise ValueError('expected --check, --record or --replay')
    if mode == '--record' and (HERE/'manifest.json').exists():
        raise ValueError('record already exists; use read-only replay')
    if mode == '--replay':
        locks = decode((HERE/'baseline.json').read_bytes())
        manifest = decode((HERE/'manifest.json').read_bytes())
        check_locks(manifest['implementation'])
        check_locks(manifest['outputs'])
    else:
        locks = protected()
    check_locks(locks)
    started = datetime.now(timezone.utc).isoformat(); timer = time.monotonic()
    raw, source, trusted = context()
    result, packet, blobs = conformance(raw, source, trusted)
    check_locks(locks)
    failed = [item['name'] for item in result['checks'] if not item['passed']]
    observation = {'mode': mode, 'passed': result['passed'], 'checks': len(result['checks']),
        'failed': failed, 'protected_files': len(locks), 'wall_seconds': time.monotonic()-timer,
        'records': len(packet['record_registry']), 'blobs': len(blobs)}
    if mode == '--replay':
        if canonical(decode((HERE/'checks.json').read_bytes())) != canonical(result):
            raise ValueError('recorded checks differ from read-only replay')
        if canonical(decode((HERE/'packet.json').read_bytes())) != canonical(packet):
            raise ValueError('recorded packet differs from read-only replay')
        for h, content in blobs.items():
            if (HERE/'blobs'/h).read_bytes() != content:
                raise ValueError('recorded blob differs from exact replay')
    elif not result['passed']:
        dump(HERE/('failed-checks-'+str(time.time_ns())+'.json'), result)
    elif mode == '--record':
        (HERE/'blobs').mkdir(exist_ok=False)
        for h, content in blobs.items():
            (HERE/'blobs'/h).write_bytes(content)
        dump(HERE/'baseline.json', locks)
        dump(HERE/'checks.json', result)
        dump(HERE/'packet.json', packet)
        dump(HERE/'schemas.json', schemas())
        migration = []
        for h, record in packet['record_registry'].items():
            if record['kind'] == 'DraftImport':
                body = record['body']
                migration.append({'role': body['role'], 'origin': body['origin'],
                    'original_blob_sha256': body['raw_blob']['digest'],
                    'decoded_draft_sha256': body['decoded_sha256'],
                    'portable_content_sha256': body['content_ref']['digest'],
                    'portable_import_sha256': h, 'parent_ref': body['parent_ref'], 'pointer': body['pointer']})
        dump(HERE/'migration.json', migration)
        outputs = {str(p.relative_to(ROOT)): filehash(p) for p in HERE.glob('*.json') if p.name in [
            'baseline.json', 'checks.json', 'packet.json', 'schemas.json', 'migration.json']}
        outputs.update({str(p.relative_to(ROOT)): filehash(p) for p in (HERE/'blobs').iterdir()})
        implementation = {str(p.relative_to(ROOT)): filehash(p) for p in HERE.glob('*.py')}
        dump(HERE/'manifest.json', {'started_utc': started, 'wall_seconds': observation['wall_seconds'],
            'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'command': 'python3 '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment': 'Python '+platform.python_version()+'; protected exact company engine',
            'cpu_gpu': 'CPU only; CUDA_VISIBLE_DEVICES=-1 set before local engine imports',
            'random_seeds': 'N/A: deterministic', 'data_version': locks,
            'implementation': implementation, 'outputs': outputs,
            'plan': 'docs/plans/accounting-company-portable-authoring-20261023.md',
            'result': str(HERE.relative_to(ROOT)/'result.md'),
            'output_artifacts': list(outputs), 'scope': 'synthetic legacy imports and trusted reference replay'})
    print(json.dumps(observation))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        path = HERE/('failure-'+str(time.time_ns())+'.txt')
        path.write_text(traceback.format_exc())
        print(json.dumps({'status': 'failed', 'error': type(exc).__name__+': '+str(exc)[:500],
                          'diagnostic': str(path.relative_to(ROOT))}))
        sys.exit(1)
