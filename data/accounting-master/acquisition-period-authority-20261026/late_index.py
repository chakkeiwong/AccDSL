"""Inspect the newly retained separate-statements row without repeating writers."""
from pathlib import Path
import ast,json
H=Path(__file__).resolve().parent
tree=ast.parse((H/'index_inventory.py').read_text())
nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.ClassDef))]
namespace={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'retained_index_parser','exec'),namespace)
p=H/'index-attempt-04/accounting-index-fifth.html';parser=namespace['Parser']();parser.feed(p.read_text());rows=[]
for i,row in enumerate(parser.rows):
    if row['text'].startswith('AASB 127 '):rows.append(dict(standard=row,amendments=parser.rows[i+1]))
assert len(rows)==1
out=H/'index-inventory-02';out.mkdir(exist_ok=False)
(out/'aasb127.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
