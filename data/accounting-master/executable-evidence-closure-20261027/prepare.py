"""Stage the inspected native replay closure without importing project code."""
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = Path('data/accounting-master')
UNIT = HERE.relative_to(ROOT)


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def write(path, body):
    with path.open('x') as stream:
        json.dump(body, stream, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', required=True, type=Path)
    args = parser.parse_args()
    args.record.mkdir(parents=True, exist_ok=False)
    discovered = read(HERE / 'static-dependencies.json')
    dynamic = {
        'scripts/method_input_binding_v1.py': [
            str(BASE / 'company-portable-authoring-20261023/portable.py')],
        str(BASE / 'company-portable-authoring-20261023/portable.py'): [
            str(BASE / 'company-path-admission-20261023/admission.py')],
        'scripts/joint_source_relation_binding_v1.py': [
            str(BASE / 'statement-context-coverage-20261024/statement_context.py')],
        str(BASE / 'selected-reading-history-20261027/compose.py'): [
            str(BASE / 'debt-reading-network-20261027/compose.py')],
    }
    search_paths = [ROOT / 'scripts', *[
        ROOT / BASE / folder for folder in [
            'source-relations-20261024', 'source-constrained-state-20261024',
            'real-company-input-readiness-20261024']]]
    pending = list(discovered['roots']) + [
        str(BASE / 'debt-reading-network-20261027/independent_check.py')]
    graph, reasons = {}, {}

    def include(name, reason):
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        reasons.setdefault(name, set()).add(reason)

    while pending:
        name = pending.pop()
        if name in graph:
            continue
        path = ROOT / name
        tree = ast.parse(path.read_text(), filename=name)
        local, environment = set(dynamic.get(name, [])), set()
        for node in ast.walk(tree):
            modules = ([a.name for a in node.names] if isinstance(node, ast.Import)
                       else [node.module] if isinstance(node, ast.ImportFrom) and node.module
                       else [])
            for module in modules:
                found = next((d / (module.replace('.', '/') + '.py')
                              for d in [path.parent, *search_paths]
                              if (d / (module.replace('.', '/') + '.py')).is_file()), None)
                if found is None:
                    environment.add(module)
                else:
                    local.add(str(found.relative_to(ROOT)))
        graph[name] = {
            'local_dependencies': sorted(local), 'environment_imports': sorted(environment),
            'module_statements': [dict(line=n.lineno, source=ast.unparse(n))
                for n in tree.body if not isinstance(n, (ast.FunctionDef, ast.ClassDef,
                    ast.Import, ast.ImportFrom)) and not
                (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))],
        }
        include(name, 'inspected executable import graph')
        pending.extend(local - graph.keys())

    pin_name = str(BASE / 'joint-source-relation-binding-20261024/dependency-lock.json')
    pins = read(ROOT / pin_name)
    assert len(pins) == 183
    include(pin_name, 'native import checks this exact lock')
    for name in pins:
        include(name, 'native import hashes every entry in the 183-file lock')

    compatibility = BASE / 'source-opening-compatibility-20261027'
    selected = BASE / 'selected-reading-history-20261027'
    source = BASE / 'debt-reading-network-20261027'
    fixtures = [compatibility / 'attempt-01/cases.json', compatibility / 'expected.md',
                compatibility / 'compatibility.md', selected / 'expected.md',
                selected / 'attempt-01/request.json', selected / 'attempt-01/result.json',
                selected / 'attempt-01/controls.json', source / 'attempt-01/full-result.json',
                source / 'attempt-01/witnesses.json',
                BASE / 'company-return-execution-20261024/trace.json']
    fixtures += [selected / 'attempt-01' / (row['name'] + '.json')
                 for row in read(ROOT / selected / 'attempt-01/controls.json')]
    for name in fixtures:
        include(str(name), 'complete frozen replay input, oracle or independent expectation')
    authority = dict(pins)
    for lock in [compatibility / 'dependency-lock.json', selected / 'attempt-01/source-lock.json']:
        for name, value in read(ROOT / lock).items():
            if name in authority:
                assert authority[name] == value, 'conflicting authority: ' + name
            authority[name] = value
        include(str(lock), 'retained provenance index; entries outside replay are not executed')
    for name in ['replay.py', 'execution-review.md', 'prepare.py', 'plan-review.md']:
        include(str(UNIT / name), 'new replay harness and reviewed scope')
    include('docs/plans/accounting-executable-evidence-closure-20261027.md', 'governing plan')

    entries = {}
    for name, why in sorted(reasons.items()):
        path = ROOT / name
        value = digest(path)
        if name in authority:
            assert value == authority[name], 'frozen identity changed: ' + name
        entries[name] = dict(sha256=value, bytes=path.stat().st_size,
                             reasons=sorted(why), inherited_identity=name in authority)
    stage = Path(tempfile.mkdtemp(prefix='accdsl-executable-evidence-', dir='/tmp'))
    for name, entry in entries.items():
        target = stage / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
        assert digest(target) == entry['sha256']
    catalog = read(ROOT / 'scripts/accounting_master_catalog.json')['active_execution_note']
    manifest = dict(schema='accdsl.bounded-replay-bundle.v1', entries=entries,
        import_graph=graph, dynamic_edges=dynamic, original_root=str(ROOT),
        manuscript={k:catalog[k] for k in ['current_candidate','current_pdf','current_pdf_sha256',
            'standalone_pdf','standalone_pdf_sha256']},
        excluded='Source acquisition, source-decision reconstruction, manuscript build, arbitrary runtime paths and redistribution rights')
    write(stage / 'replay-manifest.json', manifest)
    write(args.record / 'bundle-manifest.json', manifest)
    record = dict(stage=str(stage), executable_modules=len(graph), files=len(entries),
        bytes=sum(e['bytes'] for e in entries.values()),
        manifest_sha256=digest(stage / 'replay-manifest.json'),
        command=['python3','-I','-B',str(stage / UNIT / 'replay.py'),
                 '--root',str(stage),'--output',str(stage / 'replay-output')])
    write(args.record / 'stage.json', record)
    print(json.dumps(record))


if __name__ == '__main__':
    main()
