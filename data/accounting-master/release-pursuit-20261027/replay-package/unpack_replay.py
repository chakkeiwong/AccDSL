"""Verify the included replay archive and extract into a new directory."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import shlex
import sys
import tarfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True,
                        help='New extraction directory; must not exist')
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent
    preservation = json.loads((folder/'preservation.json').read_text())
    manifest_bytes = (folder/'bundle-manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    archive_bytes = (folder/'replay-bundle.tar.gz').read_bytes()
    digest = lambda b: hashlib.sha256(b).hexdigest()
    if digest(archive_bytes) != preservation['bundle_sha256']:
        raise ValueError('Replay archive does not match its retained identity')
    if digest(manifest_bytes) != preservation['bundle_manifest_sha256']:
        raise ValueError('Replay manifest does not match its retained identity')
    expected = dict(manifest['entries'])
    expected['replay-manifest.json'] = {
        'sha256': digest(manifest_bytes), 'bytes': len(manifest_bytes)}
    destination = args.destination.absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError('Use a new extraction directory: '+str(destination))
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode='r:gz') as archive:
        members = archive.getmembers()
        if len(members) != len(expected) or {m.name for m in members} != set(expected):
            raise ValueError('Archive member population differs from its manifest')
        for member in members:
            relative = PurePosixPath(member.name)
            if (not member.isfile() or relative.is_absolute() or
                    '..' in relative.parts or relative.as_posix() != member.name):
                raise ValueError('Unsupported archive member: '+member.name)
            data = archive.extractfile(member).read()
            entry = expected[member.name]
            if len(data) != entry['bytes'] or digest(data) != entry['sha256']:
                raise ValueError('Archive member identity mismatch: '+member.name)
        destination.mkdir(parents=True, exist_ok=False)
        for member in members:
            output = destination/member.name
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open('xb') as stream:
                stream.write(archive.extractfile(member).read())
    driver = destination/'data/accounting-master/executable-evidence-closure-20261027/replay.py'
    command = [sys.executable, '-I', '-B', str(driver), '--root', str(destination),
               '--output', str(destination/'output-01')]
    print(json.dumps({'passed': True, 'files': len(expected),
                      'destination': str(destination),
                      'next_command': shlex.join(command)}))


if __name__ == '__main__':
    main()
