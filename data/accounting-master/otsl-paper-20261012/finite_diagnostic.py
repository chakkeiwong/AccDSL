"""Small mathematical examples; do not import or execute upstream software."""
import ast
import json
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert not (OUT/'completion.json').exists()

def evaluate(rows):
    grid=[r[:-1] for r in rows];height=len(grid);width=len(grid[0])
    rules={
      '1_left':all(c>0 and grid[r][c-1] in {'L','C'} for r,row in enumerate(grid) for c,t in enumerate(row) if t=='L'),
      '2_up':all(r>0 and grid[r-1][c] in {'U','C'} for r,row in enumerate(grid) for c,t in enumerate(row) if t=='U'),
      '3_cross':all(r>0 and c>0 and grid[r][c-1] in {'X','U'} and grid[r-1][c] in {'X','L'} for r,row in enumerate(grid) for c,t in enumerate(row) if t=='X'),
      '4_first_row':all(t in {'C','L'} for t in grid[0]),
      '5_first_column':all(row[0] in {'C','U'} for row in grid),
      '6_rectangular_rows':all(len(row)==width+1 and row[-1]=='NL' for row in rows),
      'vocabulary':all(t in {'C','L','U','X'} for row in grid for t in row)}
    if not all(rules.values()):return {'rows':rows,'rules':rules,'accepted':False,'cells':None,'all_cells_rectangular':None}
    parent={(r,c):(r,c) for r in range(height) for c in range(width)}
    def root(p):
        while parent[p]!=p:p=parent[p]
        return p
    def merge(a,b):parent[root(a)]=root(b)
    for r,row in enumerate(grid):
        for c,t in enumerate(row):
            if t in {'L','X'}:merge((r,c),(r,c-1))
            if t in {'U','X'}:merge((r,c),(r-1,c))
    groups={}
    for p in parent:groups.setdefault(root(p),[]).append(p)
    cells=[]
    for members in groups.values():
        rs=[p[0] for p in members];cs=[p[1] for p in members]
        rectangle={(r,c) for r in range(min(rs),max(rs)+1) for c in range(min(cs),max(cs)+1)}
        cells.append({'members':members,'bounding_rectangle':sorted(rectangle),'missing_from_rectangle':sorted(rectangle-set(members)),
                      'rectangular':set(members)==rectangle,'origins':[(r,c) for r,c in members if grid[r][c]=='C']})
    return {'rows':rows,'rules':rules,'accepted':True,'cells':cells,'all_cells_rectangular':all(c['rectangular'] for c in cells)}

start=time.monotonic()
cases={
 'counterexample':[['C','L','NL'],['U','C','NL']],
 'rectangle_control':[['C','L','NL'],['U','X','NL']],
 'simple_control':[['C','C','NL'],['C','C','NL']],
 'horizontal_control':[['C','L','NL'],['C','C','NL']],
 'invalid_first_row_control':[['C','U','NL'],['C','C','NL']]}
results={n:evaluate(rows) for n,rows in cases.items()}
assert results['counterexample']['accepted'] and not results['counterexample']['all_cells_rectangular']
for n in ['rectangle_control','simple_control','horizontal_control']:
    assert results[n]['accepted'] and results[n]['all_cells_rectangular']
assert not results['invalid_first_row_control']['accepted']
p=ROOT/'data/accounting-master/tableformer-loader-20261010/sources/docling_ibm_models__tableformer__models__table04_rs__tablemodel04_rs.py'
tree=ast.parse(p.read_text());pred=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='predict')
stores=[n.lineno for n in ast.walk(pred) if isinstance(n,ast.Name) and n.id=='line_num' and isinstance(n.ctx,ast.Store)]
assert stores==[170]
assign=next(n for n in ast.walk(pred) if isinstance(n,ast.Assign) and n.lineno==170)
assert isinstance(assign.value,ast.Constant) and assign.value.value==0
record={'cases':results,'code_static_fact':{'path':str(p.relative_to(ROOT)),'method':[pred.lineno,pred.end_lineno],
 'line_num_store_lines':stores,'value':0,'effect':'The line_num == 0 guard remains true for all iterations; raw xcel is rewritten to lcel at every row when reached.',
 'limit':'No model run, occurrence frequency or complete adapter failure rate established'},
 'conclusion':'The six printed rules are insufficient for nonoverlapping rectangular-cell geometry under the stated merge semantics.',
 'wall_seconds':time.monotonic()-start,'cpu_gpu':'CPU standard-library mathematical/AST check; no framework/device use'}
(OUT/'finite-diagnostic.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'cases':len(results),'counterexample_rules_pass':results['counterexample']['accepted'],
 'counterexample_rectangular':results['counterexample']['all_cells_rectangular'],'line_num_store_lines':stores}))
