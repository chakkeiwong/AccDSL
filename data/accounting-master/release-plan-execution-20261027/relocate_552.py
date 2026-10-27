from pathlib import Path
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
import fitz

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent / 'v552r1'
SOURCE = ROOT / 'docs/design/proposal/manuscript-release-prep-v552r1-20261027'
OUTPUT = HERE / 'relocation'
OUTPUT.mkdir(exist_ok=False)
TARGET = Path(tempfile.mkdtemp(prefix='accdsl-v552r1-source-'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

files = []
for path in sorted(SOURCE.rglob('*')):
    rel = path.relative_to(SOURCE)
    if not path.is_file() or path.is_symlink():
        continue
    if any(part.startswith('.') or part.startswith('output-') or part == '__pycache__' for part in rel.parts):
        continue
    if path.suffix in {'.aux', '.log', '.fls', '.fdb_latexmk', '.toc', '.bbl', '.blg', '.pdf', '.pyc'}:
        continue
    dest = TARGET / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    files.append({'path': str(rel), 'sha256': digest(path)})

cache = TARGET / '.tex-cache'
cache.mkdir()
env = dict(os.environ, TEXMFVAR=str(cache), TEXMFCACHE=str(cache), CUDA_VISIBLE_DEVICES='-1')

def build(name):
    command = ['latexmk', '-g', '-lualatex', '-interaction=nonstopmode', '-halt-on-error', '-no-shell-escape', name + '.tex']
    start = time.monotonic()
    with (OUTPUT / (name + '.stdout')).open('w') as stream:
        result = subprocess.run(command, cwd=TARGET, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=240)
    record = {'volume': name, 'command': command, 'cwd': str(TARGET), 'seconds': time.monotonic() - start, 'returncode': result.returncode}
    if result.returncode:
        return record
    log = (TARGET / (name + '.log')).read_text()
    actual = fitz.open(TARGET / (name + '.pdf'))
    expected = fitz.open(SOURCE / (name + '.pdf'))
    record['pages'] = len(actual)
    record['expected_pages'] = len(expected)
    record['different_text_pages'] = [i + 1 for i in range(min(len(actual), len(expected))) if actual[i].get_text() != expected[i].get_text()]
    record['candidate_pdf_sha256'] = digest(SOURCE / (name + '.pdf'))
    record['relocated_pdf_sha256'] = digest(TARGET / (name + '.pdf'))
    record['pdf_byte_equal'] = record['candidate_pdf_sha256'] == record['relocated_pdf_sha256']
    record['undefined_diagnostics'] = [line for line in log.splitlines() if 'undefined' in line.lower()]
    inputs = set()
    for line in (TARGET / (name + '.fls')).read_text().splitlines():
        if line.startswith('INPUT '):
            path = Path(line[6:])
            inputs.add(str((TARGET / path).resolve() if not path.is_absolute() else path.resolve()))
    record['original_worktree_reads'] = sorted(p for p in inputs if p.startswith(str(ROOT) + '/') or p.startswith('/home/chakwong/python/MathDevMCP/'))
    external = sorted(p for p in inputs if not p.startswith(str(TARGET) + '/'))
    (OUTPUT / (name + '-external-inputs.json')).write_text(json.dumps([{'path': p, 'sha256': digest(Path(p)) if Path(p).is_file() else None} for p in external], indent=2) + chr(10))
    record['external_inputs_count'] = len(external)
    record['pass'] = record['pages'] == record['expected_pages'] and not record['different_text_pages'] and not record['original_worktree_reads'] and not record['undefined_diagnostics']
    return record

# Initialize the font database once before concurrent typesetting.
warm_command = ['luaotfload-tool', '--update']
with (OUTPUT / 'font-cache.stdout').open('w') as stream:
    warm = subprocess.run(warm_command, cwd=TARGET, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=180)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    builds = list(pool.map(build, ['accounting-product-proposal', 'simulation-foundations']))
unchanged = all(digest(SOURCE / item['path']) == item['sha256'] for item in files)
result = {'source': str(SOURCE), 'relocated': str(TARGET), 'inputs': files, 'cache_command': warm_command, 'cache_returncode': warm.returncode, 'environment': {key: env[key] for key in ['TEXMFVAR', 'TEXMFCACHE', 'CUDA_VISIBLE_DEVICES']}, 'builds': builds, 'source_inputs_unchanged': unchanged, 'pass': unchanged and all(b.get('pass', False) for b in builds), 'plan': str(HERE / 'relocation-plan.md'), 'limits': 'Local source relocation and page-text comparison; system TeX/font environment retained and recorded. Not whole evidence closure, independent installation, process isolation or domain acceptance.'}
(HERE / 'relocation-result.json').write_text(json.dumps(result, indent=2) + chr(10))
print(json.dumps({key: value for key, value in result.items() if key != 'inputs'}, indent=2))
raise SystemExit(0 if result['pass'] else 1)
