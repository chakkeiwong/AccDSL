from pathlib import Path, PurePosixPath
import hashlib
import json
import tarfile
from datetime import datetime, timezone

ROOT = Path('/home/chakwong/python/AccDSL')
PREV = ROOT / 'data/accounting-master/native-reuse-boundary-20261018'
OUT = ROOT / 'data/accounting-master/component-notice-inquiry-20261018'
PLAN = ROOT / 'docs/plans/accounting-component-notice-inquiry-20261018.md'
archive = PREV / 'sources/pypdfium2-5.9.0.tar.gz'
digest = lambda b: hashlib.sha256(b).hexdigest()
assert archive.stat().st_size == 272455
assert digest(archive.read_bytes()) == 'db1274bd27844db6fda17ef1dbcd0026c47d357437058d838e98060c0da9e92e'
assert not OUT.exists() or (OUT.is_dir() and not any(OUT.iterdir())), 'Do not overwrite completed or partial evidence.'
old = json.loads((PREV / 'source-manifest.json').read_text())
for row in old['files']:
    assert digest((ROOT / row['path']).read_bytes()) == row['sha256'], row['path']
OUT.mkdir(parents=True, exist_ok=True)
names = ['freetype.txt', 'libjpeg_turbo.md', 'libjpeg_turbo.ijg', 'libpng.txt', 'zlib.txt']
extracted = []
with tarfile.open(archive, 'r:gz') as tf:
    for name in names:
        member_name = 'pypdfium2-5.9.0/BUILD_LICENSES/' + name
        members = [m for m in tf.getmembers() if m.name == member_name]
        assert len(members) == 1
        m = members[0]
        assert m.isfile() and not m.issym() and not m.islnk()
        assert not PurePosixPath(m.name).is_absolute() and '..' not in PurePosixPath(m.name).parts
        assert 0 < m.size < 50000
        raw = tf.extractfile(m).read()
        assert len(raw) == m.size
        try:
            text_view = raw.decode('utf-8')
            encoding = 'utf-8'
        except UnicodeDecodeError:
            text_view = raw.decode('latin-1')
            encoding = 'latin-1 lossless inspection view; not publisher-declared'
        target = OUT / 'sources' / name
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(raw)
        extracted.append({'archive_member': m.name, 'path': str(target.relative_to(ROOT)),
                          'size': len(raw), 'sha256': digest(raw), 'lines': len(text_view.splitlines()),
                          'inspection_encoding': encoding})
protected_paths = [ROOT / r['path'] for r in old['files'] if r['role'] == 'protected comparator']
protected_paths += [archive, PREV / 'source-manifest.json', PREV / 'source-reading.md',
                   PREV / 'extraction-manifest.json',
                   ROOT / 'data/accounting-master/source-protocol-reuse-refresh-20261016/dependency-frontier.json']
manifest = {'schema': 'StaticComponentNoticeInquiry/1', 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'archive': str(archive.relative_to(ROOT)), 'archive_sha256': digest(archive.read_bytes()),
            'files': [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p.read_bytes()),
                       'role': 'protected comparator'} for p in protected_paths],
            'selected_texts': extracted, 'anchors': [], 'plan': str(PLAN.relative_to(ROOT)),
            'plan_sha256': digest(PLAN.read_bytes()),
            'scope': 'Five source-archive notice texts only; no actual-build component bill or rights clearance'}
(OUT / 'source-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
(OUT / 'extraction-attempt-01.json').write_text(json.dumps({'outcome': 'UTF-8-only assumption rejected before member write',
    'exception': 'UnicodeDecodeError: byte 0xa9 at position 2038', 'repair': 'exact bytes retained; per-file lossless inspection encoding recorded'}, indent=2) + '\n')
print(json.dumps({'archive_checked': True, 'protected_files_checked': len(old['files']),
                  'selected_texts': [{k:r[k] for k in ('path','size','lines')} for r in extracted]}, indent=2))
