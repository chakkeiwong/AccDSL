"""Bounded documentary reader. Never extracts paths or executes archive code."""
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile

U = Path(__file__).resolve().parent
R = U.parents[2]
PRIOR = R / 'data/accounting-master/r04-pylcs-source-20261020'
METADATA = PRIOR / 'sources/01-package.body'
ARCHIVE = U / 'sources/sdist-sandbox.body'


def read_archive():
    metadata = json.loads(METADATA.read_text())
    releases = [a for a in metadata['urls'] if a['packagetype'] == 'sdist']
    assert len(releases) == 1
    release = releases[0]
    assert release['filename'] == 'pylcs-0.1.1.tar.gz'
    assert metadata['info']['version'] == '0.1.1'
    assert ARCHIVE.stat().st_size == release['size'] <= 262144
    raw = ARCHIVE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == release['digests']['sha256']
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        expanded = stream.read(2 * 1024 * 1024 + 1)
    assert len(expanded) <= 2 * 1024 * 1024, 'decompression limit'
    entries, files, seen = [], {}, set()
    with tarfile.open(fileobj=io.BytesIO(expanded), mode='r:') as tar:
        members = tar.getmembers()
        assert len(members) <= 128
        for member in members:
            p = PurePosixPath(member.name)
            assert not p.is_absolute() and '..' not in p.parts and '\\' not in member.name
            assert p.parts and p.parts[0] == 'pylcs-0.1.1'
            assert member.name not in seen and str(p) not in seen
            seen.add(str(p))
            assert member.isdir() or member.isfile(), 'link or special member'
            assert 0 <= member.size <= 262144
            entry = {'name': member.name, 'type': 'directory' if member.isdir() else 'file',
                     'bytes': member.size}
            if member.isfile():
                content = tar.extractfile(member).read(262145)
                assert len(content) == member.size
                files[str(p.relative_to('pylcs-0.1.1'))] = content
                entry['sha256'] = hashlib.sha256(content).hexdigest()
            entries.append(entry)
    return release, entries, files, len(expanded)


if __name__ == '__main__':
    release, entries, files, expanded = read_archive()
    pairs = {'src/main.cpp': '04-source.body', 'pylcs/__init__.py': '05-source.body',
             'setup.py': '06-source.body'}
    print(json.dumps({'archive_bytes': release['size'], 'expanded_bytes': expanded,
                      'members': entries, 'selected_equal': {
                          name: files.get(name) == (PRIOR/'sources'/old).read_bytes()
                          for name, old in pairs.items()}}, indent=2))
