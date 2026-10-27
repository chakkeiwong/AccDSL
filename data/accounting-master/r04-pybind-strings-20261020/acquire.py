"""Bounded primary-source retrieval; never executes retrieved code."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
S = UNIT / 'sources'
TAGS = ('v2.2.0', 'v2.11.1')

def fetch(stem, url):
    assert not list(S.glob(stem + '.*')), 'one-time request'
    assert (UNIT / 'execution-audit.md').is_file(), 'scope repair record required'
    assert len(list(S.glob('*.invocation.json'))) < 14, 'request budget'
    command = ['curl', '--silent', '--show-error', '--location',
        '--connect-timeout', '10', '--max-time', '35', '--max-filesize', '2097152',
        '--proto', '=https', '--proto-redir', '=https',
        '--dump-header', str((S / (stem + '.headers')).relative_to(ROOT)),
        '--output', str((S / (stem + '.body')).relative_to(ROOT)),
        '--write-out', '%{json}\n', url]
    started = datetime.now(timezone.utc).isoformat()
    r = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    with (S / (stem + '.invocation.json')).open('x') as f:
        json.dump({'argv': command, 'started_utc': started,
            'returncode': r.returncode, 'stderr': r.stderr, 'stdout': r.stdout}, f, indent=2)
    receipt = json.loads(r.stdout)
    with (S / (stem + '.receipt.json')).open('x') as f:
        json.dump(receipt, f, indent=2)
    print(json.dumps({'source': stem, 'status': receipt['http_code'],
        'exitcode': r.returncode, 'bytes': receipt['size_download'],
        'seconds': receipt['time_total']}), flush=True)
    assert r.returncode == 0 and receipt['http_code'] == 200, 'retrieval failed; retain evidence'

def identity(i):
    d = json.loads((S / f'{i}-commit.body').read_text())
    assert len(d['sha']) == 40
    return d

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage', choices=('identity', 'trees', 'selected', 'python-docs', 'helpers'))
    stage = p.parse_args().stage
    assert (UNIT / 'protection.json').is_file(), 'prepare first'
    if stage == 'identity':
        for i, tag in enumerate(TAGS):
            fetch(f'{i}-commit', 'https://api.github.com/repos/pybind/pybind11/commits/' + tag)
    elif stage == 'trees':
        for i in range(2):
            fetch(f'{i}-tree', 'https://api.github.com/repos/pybind/pybind11/git/trees/'
                + identity(i)['commit']['tree']['sha'] + '?recursive=1')
    elif stage == 'helpers':
        for i in range(2):
            path = 'include/pybind11/detail/common.h'
            tree = json.loads((S / f'{i}-tree.body').read_text())
            assert not tree['truncated']
            entry = next(x for x in tree['tree'] if x['path'] == path)
            assert entry['type'] == 'blob' and entry['size'] <= 2097152
            fetch(f'helper{i}', 'https://raw.githubusercontent.com/pybind/pybind11/'
                + identity(i)['sha'] + '/' + path)
    elif stage == 'python-docs':
        fetch('python-unicode', 'https://docs.python.org/3.10/c-api/unicode.html')
        fetch('python-bytes', 'https://docs.python.org/3.10/c-api/bytes.html')
    else:
        selections = json.loads((UNIT / 'source-selection.json').read_text())
        assert len(selections) <= 8
        for n, row in enumerate(selections):
            i, path = row['version_index'], row['path']
            assert i in (0, 1) and '..' not in Path(path).parts
            assert Path(path).suffix in ('.h', '.rst', '.md', '.txt')
            tree = json.loads((S / f'{i}-tree.body').read_text())
            assert not tree['truncated']
            entry = next(x for x in tree['tree'] if x['path'] == path)
            assert entry['type'] == 'blob' and entry['size'] <= 2097152
            fetch(f's{n:02}', 'https://raw.githubusercontent.com/pybind/pybind11/'
                + identity(i)['sha'] + '/' + path)

if __name__ == '__main__':
    main()
