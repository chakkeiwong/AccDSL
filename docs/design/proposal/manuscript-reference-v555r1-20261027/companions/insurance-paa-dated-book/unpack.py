"""Check an included internal archive and extract into a new directory."""
import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import shlex
import sys
import tarfile

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--destination',type=Path,required=True)
    args=parser.parse_args()
    folder=Path(__file__).resolve().parent
    meta=json.loads((folder/'component.json').read_text())
    archive=folder/meta['archive']
    assert sha256(archive.read_bytes()).hexdigest()==meta['archive_sha256'],'archive identity'
    destination=args.destination.absolute()
    assert not destination.exists() and not destination.is_symlink(),'destination must be new'
    with tarfile.open(archive,'r:gz') as source:
        members=source.getmembers()
        assert len(members)==len(meta['entries']) and {m.name for m in members}==set(meta['entries']),'member set'
        for member in members:
            path=PurePosixPath(member.name)
            assert member.isfile() and not path.is_absolute() and '..' not in path.parts and path.as_posix()==member.name
            raw=source.extractfile(member).read();expected=meta['entries'][member.name]
            assert len(raw)==expected['bytes'] and sha256(raw).hexdigest()==expected['sha256'],member.name
        destination.mkdir(parents=True,exist_ok=False)
        for member in members:
            target=destination/member.name
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as stream:stream.write(source.extractfile(member).read())
    command=[sys.executable,'-B',str(destination/meta['driver'])]
    if meta['root_argument']:command+=['--root',str(destination)]
    command+=['--output',str(destination/'output-01')]
    print(json.dumps(dict(passed=True,files=len(members),destination=str(destination),next_command=shlex.join(command))))

if __name__=='__main__':main()
