"""Derive isolated parser successors; all financial evaluators remain frozen."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def sha(path): return sha256(path.read_bytes()).hexdigest()
def dump(name,value): (HERE/name).write_text(json.dumps(value,indent=2)+'\n')
assert not (HERE/'source-preservation.json').exists()
specs=[
 ('invariant-source-authoring-20261026/invariant_text.py','invariant_text_unicode.py',[
  (' for number,raw in enumerate(source.splitlines(keepends=True),1):',
   " pieces=source.split(NL)\n for number,piece in enumerate(pieces,1):\n  raw=piece+(NL if number<len(pieces) else '')"),
  ('body=rules.render(exchange).splitlines()',"body=rules.render(exchange).rstrip(NL).split(NL)")]),
 ('selected-company-source-20261026/company_text.py','company_text_unicode.py',[
  ('import invariant_text as invariant','import invariant_text_unicode as invariant')]),
 ('complete-claims-source-20261026/complete_text.py','complete_text_unicode.py',[
  ('import company_text as selected','import company_text_unicode as selected')]),
 ('complete-claims-source-20261026/source_controls.py','source_controls_unicode.py',[
  ('import complete_text as text','import complete_text_unicode as text')])]
records=[]
for origin,target,changes in specs:
    source=HERE.parent/origin
    value=source.read_text()
    for old,new in changes:
        assert value.count(old)==1,(origin,old)
        value=value.replace(old,new,1)
    assert not (HERE/target).exists()
    (HERE/target).write_text(value)
    records.append(dict(source=str(source.relative_to(ROOT)),target=target,source_sha256=sha(source),
                        target_sha256=sha(HERE/target),changes=[dict(old=a,new=b) for a,b in changes]))
lock={}
for folder in ('complete-claims-source-20261026','invariant-source-authoring-20261026'):
    directory=HERE.parent/folder
    for name,h in json.loads((directory/'source-lock.json').read_text()).items():
        assert name not in lock or lock[name]==h,name
        lock[name]=h
    for path in directory.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            name=str(path.relative_to(ROOT));assert name not in lock or lock[name]==sha(path),name
            lock[name]=sha(path)
dump('source-preservation.json',records)
dump('source-lock.json',lock)
print(json.dumps(dict(copied_modules=len(records),protected_files=len(lock))))
