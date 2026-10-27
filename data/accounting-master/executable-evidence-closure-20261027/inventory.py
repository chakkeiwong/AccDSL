"""Static discovery only: parse project code without importing it."""
import ast
from hashlib import sha256
import json
from pathlib import Path

H = Path(__file__).resolve().parent
R = H.parents[2]
roots = [
    'scripts/conditional_company_opening_v1.py',
    'scripts/conditional_company_continuation_v1.py',
    'scripts/company_book_carry_v1.py',
    'data/accounting-master/selected-reading-history-20261027/compose.py',
    'data/accounting-master/selected-reading-history-20261027/independent_check.py',
    'data/accounting-master/debt-reading-network-20261027/compose.py',
]
pending, records = list(roots), {}
while pending:
    name = pending.pop()
    if name in records:
        continue
    path = R/name
    raw = path.read_bytes()
    source = raw.decode()
    tree = ast.parse(source, filename=name)
    local, other = [], set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            modules = [node.module] if node.module else []
        else:
            continue
        for module in modules:
            candidates = [path.parent/(module.replace('.', '/')+'.py'), R/'scripts'/(module.replace('.', '/')+'.py')]
            found = next((p for p in candidates if p.is_file()), None)
            if found is None:
                other.add(module)
            else:
                rel = str(found.relative_to(R))
                local.append(dict(module=module, path=rel, line=node.lineno))
                pending.append(rel)
    io = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = ast.unparse(node.func)
            if any(part in func for part in ['read_text', 'read_bytes', 'open', 'write', 'mkdir', 'spec_from_file_location', 'exec_module', 'subprocess', 'system']):
                io.append(dict(line=node.lineno, expression=ast.get_source_segment(source,node)))
    top = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        top.append(dict(line=node.lineno, kind=type(node).__name__, source=ast.get_source_segment(source,node)))
    records[name] = dict(sha256=sha256(raw).hexdigest(), bytes=len(raw), local_imports=local,
                         nonlocal_imports=sorted(other), file_and_loader_calls=io, module_statements=top)
out = H/'static-dependencies.json'
with out.open('x') as stream:
    json.dump(dict(roots=roots, explicit_dynamic_edge=dict(
        caller=roots[3], callee=roots[5], reason='source_module uses spec_from_file_location'),
        records=records, limitation='Static discovery; dynamic closure requires a runtime read audit'), stream, indent=2)
    stream.write('\n')
print(json.dumps(dict(files=len(records), bytes=sum(v['bytes'] for v in records.values()),
    nonlocal_imports=sorted({n for v in records.values() for n in v['nonlocal_imports']}),
    file=str(out.relative_to(R)))))
