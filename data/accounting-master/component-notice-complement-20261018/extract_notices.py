"""Extract the exact unreviewed notice complement without executing upstream code."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import hashlib
import json
import platform
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
NATIVE = ROOT / 'data/accounting-master/native-reuse-boundary-20261018'
PREVIOUS = ROOT / 'data/accounting-master/component-notice-inquiry-20261018'
PLAN = ROOT / 'docs/plans/accounting-component-notice-complement-20261018.md'
digest = lambda data: hashlib.sha256(data).hexdigest()
sha = lambda path: digest(path.read_bytes())
ref = lambda path: {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}

def read(path):
    return json.loads(path.read_text())

def write_new(path, value):
    with path.open('x') as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write('\n')

assert not (OUT / 'source-manifest.json').exists(), 'Do not overwrite completed/partial evidence.'
started = datetime.now(timezone.utc)
archive = NATIVE / 'sources/pypdfium2-5.9.0.tar.gz'
assert archive.stat().st_size == 272455
assert sha(archive) == 'db1274bd27844db6fda17ef1dbcd0026c47d357437058d838e98060c0da9e92e'
native_manifest = read(NATIVE / 'source-manifest.json')
previous = read(PREVIOUS / 'source-manifest.json')
for row in native_manifest['files'] + previous['files'] + previous['selected_texts']:
    assert sha(ROOT / row['path']) == row['sha256'], row['path']
inventory = read(NATIVE / 'extraction-manifest.json')['notice_inventory_only']
inventory_by_name = {row['archive_member']: row for row in inventory}
assert len(inventory_by_name) == len(inventory) == 28
earlier = {row['archive_member'] for row in previous['selected_texts']}
assert len(earlier) == 5 and earlier <= inventory_by_name.keys()
remaining = sorted(inventory_by_name.keys() - earlier)
assert len(remaining) == 23
prefix = 'pypdfium2-5.9.0/BUILD_LICENSES/'
selected = []
with tarfile.open(archive, 'r:gz') as handle:
    members = handle.getmembers()
    actual = {m.name for m in members if m.isfile() and m.name.startswith(prefix)}
    assert actual == inventory_by_name.keys()
    for name in remaining:
        matches = [m for m in members if m.name == name]
        assert len(matches) == 1, name
        member = matches[0]
        assert member.isfile() and not member.issym() and not member.islnk()
        path = PurePosixPath(member.name)
        assert not path.is_absolute() and '..' not in path.parts
        assert 0 < member.size < 50000 and member.size == inventory_by_name[name]['size']
        raw = handle.extractfile(member).read()
        assert len(raw) == member.size
        try:
            text = raw.decode('utf-8')
            encoding = 'utf-8'
        except UnicodeDecodeError:
            text = raw.decode('latin-1')
            encoding = 'latin-1 lossless inspection view; not publisher-declared'
        assert '\x00' not in text
        target = OUT / 'sources' / name.removeprefix(prefix)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as destination:
            destination.write(raw)
        selected.append({'archive_member': name, **ref(target), 'size': len(raw), 'lines': len(text.splitlines()), 'inspection_encoding': encoding, 'reading_status': 'pending'})

protected_paths = {row['path'] for row in previous['files'] + previous['selected_texts']}
protected_paths.update(str(path.relative_to(ROOT)) for path in [
    NATIVE / 'extraction-manifest.json', PREVIOUS / 'source-manifest.json',
    PREVIOUS / 'checks.json', PREVIOUS / 'run-manifest.json',
    ROOT / 'data/accounting-master/early-conversion-integration-20261018/component-notice-supplement.json',
    ROOT / 'data/accounting-master/early-conversion-integration-20261018/author-regression-supplement.json',
    ROOT / 'data/accounting-master/early-conversion-integration-20261018/regression/completion-bindings.json',
    ROOT / 'data/accounting-master/early-conversion-integration-20261018/operation-successor.json'])
manifest = {
    'schema': 'StaticComponentNoticeComplement/1', 'started_utc': started.isoformat(),
    'archive': ref(archive), 'plan': ref(PLAN),
    'protected_inputs': [ref(ROOT / name) for name in sorted(protected_paths)],
    'inventory_count': 28, 'earlier_selected_count': 5, 'complement_count': 23,
    'selected_texts': selected, 'anchors': [],
    'scope': 'Exact retained archive notice complement; extraction is not reading or actual-build applicability.',
    'status': 'extracted_reading_pending'}
write_new(OUT / 'source-manifest.json', manifest)
write_new(OUT / 'extraction-manifest.json', {
    'started_utc': started.isoformat(), 'finished_utc': datetime.now(timezone.utc).isoformat(),
    'archive': ref(archive), 'extractor': ref(Path(__file__).resolve()),
    'python_executable': sys.executable, 'python_version': platform.python_version(),
    'selected_member_count': len(selected), 'earlier_member_count': len(earlier),
    'total_bytes': sum(row['size'] for row in selected),
    'outcome': 'exact bytes retained; complete text reading pending',
    'native_execution': False, 'gpu_use': False})
print(json.dumps({'extracted': len(selected), 'inventory': 28, 'preserved_previous': len(earlier), 'protected_inputs': len(protected_paths), 'texts': [{'file': row['archive_member'].removeprefix(prefix), 'lines': row['lines'], 'encoding': row['inspection_encoding']} for row in selected]}, indent=2))
