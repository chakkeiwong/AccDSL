"""Freeze independent expectations, source identities and a copied PAA run tree."""
import argparse
import ast
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

parser=argparse.ArgumentParser();parser.add_argument('--preparation',required=True);args=parser.parse_args()
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
digest=lambda p:sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('paa_independent_authoring',HERE/'authored.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
expected={case+'/'+chart+('/complement' if complement else ''):f.expected(case,chart,complement)
          for case,chart,complement in [(case,chart,False) for case in f.CASES for chart in ['named','renamed']]+[('base','named',True)]}
target=HERE/'authored-expectations.json'
if target.exists():assert json.loads(target.read_text())==expected
else:
    with target.open('x') as stream:json.dump(expected,stream,indent=2);stream.write('\n')
paths={HERE.relative_to(ROOT)/name for name in ['authored.py','authored-expectations.json','bridge.py','verify.py','prepare.py','source-note.md']}
paths.update(Path(name) for name in ['docs/plans/accounting-insurance-paa-dated-book-20261027.md',
    'docs/design/research/standards/aasb17.pdf','docs/design/research/standards/aasb17.txt','docs/design/fixtures/sectors.json',
    'docs/design/review/accounting-dossier-checks.json','scripts/check_accounting_dossiers.py',
    'docs/design/proposal/manuscript-financing-v554r2p2-20261027/chapters/16-insurance.tex'])
pending=[Path('scripts/declared_company_program_v2.py'),Path('scripts/declared_operating_methods_v1.py'),
    Path('data/accounting-master/company-portable-authoring-20261023/portable.py'),
    Path('data/accounting-master/company-path-admission-20261023/admission.py')]
seen=set()
while pending:
    path=pending.pop()
    if path in seen:continue
    seen.add(path);paths.add(path);tree=ast.parse((ROOT/path).read_text())
    for node in ast.walk(tree):
        names=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) and node.module else []
        for name in names:
            candidate=Path('scripts')/(name.split('.')[0]+'.py')
            if (ROOT/candidate).is_file():pending.append(candidate)
        if isinstance(node,ast.Constant) and isinstance(node.value,str) and node.value.endswith('.py'):
            candidates=[Path(node.value),path.parent/node.value]
            for candidate in candidates:
                if (ROOT/candidate).is_file():pending.append(candidate)
lock={str(p):digest(ROOT/p) for p in sorted(paths)}
with (HERE/'source-lock.json').open('w') as stream:json.dump(lock,stream,indent=2);stream.write('\n')
record=HERE/args.preparation;record.mkdir(exist_ok=False)
stage=Path(tempfile.mkdtemp(prefix='accdsl-paa-book-',dir='/tmp'))
for name in [*lock,str((HERE/'source-lock.json').relative_to(ROOT))]:
    dest=stage/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
    assert digest(dest)==digest(ROOT/name)
summary=dict(stage=str(stage),source_lock_sha256=digest(HERE/'source-lock.json'),files=len(lock),
    imported_native_modules=len(seen),source_lock=lock,expected_sha256=digest(target))
with (record/'stage.json').open('x') as stream:json.dump(summary,stream,indent=2);stream.write('\n')
print(json.dumps({k:v for k,v in summary.items() if k!='source_lock'}))
