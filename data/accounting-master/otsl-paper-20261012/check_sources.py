"""Bound identity and technical examples, without upstream execution."""
import ast
import hashlib
import json
import time
from pathlib import Path
import fitz
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((OUT/n).read_text())
assert not (OUT/'completion.json').exists();start=time.monotonic();checks=[]
def ck(n,v):checks.append({'name':n,'passed':bool(v)})
p=OUT/'sources/paper.pdf';d=fitz.open(p)
ck('identified v1 PDF',sha(p)=='62f2a2163d768d5b125a207967797aefa6c9cc113de8bb5c725c582595dd0c1d' and len(d)==14)
c=read('paper-copy.json');ck('descriptive copy',sha(ROOT/c['copy'])==sha(p)==c['sha256'])
ck('title and version',all(t in d[0].get_text() for t in ['Optimized Table Tokenization','Maksym Lysak','2305.03393v1','5 May 2023']))
cr=json.loads((OUT/'sources/crossref.json').read_text())['message']
ck('published DOI identity',cr['DOI']=='10.1007/978-3-031-41679-8_3' and cr['page']=='37-50' and len(cr['author'])==5)
ck('published PDF response is HTML, not admitted PDF',(OUT/'sources/published-pdf.response').read_bytes().startswith(b'<!DOCTYPE html>'))
ck('archive exact identifier','2305.03393v1' in (OUT/'sources/arxiv-search.xml').read_text())
ck('archive history retained','[v1]' in (OUT/'sources/arxiv-landing.txt').read_text())
r=read('access-receipts.json');ck('seven resources within bound',r['distinct_resources']==len(r['attempts'])==7<=r['limit'])
for row in r['attempts']:
 ck('response '+row['name'],row['http_code']==200 and row['exit_code']==0 and sha(ROOT/row['body'])==row['sha256'] and (ROOT/row['body']).stat().st_size==row['bytes'])
for row in read('render-manifest.json'):ck('render '+str(row['page']),sha(ROOT/row['render'])==row['sha256'] and sha(p)==row['pdf_sha256'])
t7=' '.join(d[6].get_text().split());t8=' '.join(d[7].get_text().split())
for term in ['Left-looking cell rule','Up-looking cell rule','Cross cell rule','First row rule','First column rule','Rectangular rule']:
 ck('printed rule '+term,term in t7)
ck('source validity versus correctness','valid sequence by itself does not guarantee' in t8)
ck('example ranked heuristic','next highest confidence' in t8.replace('conﬁdence','confidence'))
finite=read('finite-diagnostic.json');cx=finite['cases']['counterexample']
ck('counterexample all six rules',cx['accepted'] and all(cx['rules'].values()))
ck('counterexample missing lower-right corner',cx['cells'][0]['missing_from_rectangle']==[[1,1]] and not cx['all_cells_rectangular'])
ck('counterexample distinct second origin',cx['cells'][1]['members']==[[1,1]] and cx['cells'][1]['origins']==[[1,1]])
for n in ['rectangle_control','simple_control','horizontal_control']:ck('positive '+n,finite['cases'][n]['accepted'] and finite['cases'][n]['all_cells_rectangular'])
ck('negative first-row control',not finite['cases']['invalid_first_row_control']['accepted'])
body=(OUT/'sources/otsl.py').read_bytes();tree=read('code-anchors.json')
ck('new helper Git blob',hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()==tree['git_blob']=='60b9151ef419aa3e8f45a640fd6a0c9839105736')
oldtree=json.loads((ROOT/'data/accounting-master/tableformer-loader-20261010/sources/tree.json').read_text())
ck('retained Git tree entry',any(x['path']=='docling_ibm_models/tableformer/otsl.py' and x['sha']==tree['git_blob'] for x in oldtree['tree']))
ck('read complete forward-conversion helpers',len(tree['read_ranges'])==7 and tree['read_ranges'][-1]['last']==241)
fact=finite['code_static_fact'];pt=ast.parse((ROOT/fact['path']).read_text())
pred=next(n for n in ast.walk(pt) if isinstance(n,ast.FunctionDef) and n.name=='predict')
ck('only zero row-counter assignment',fact['line_num_store_lines']==[170] and fact['value']==0 and [n.lineno for n in ast.walk(pred) if isinstance(n,ast.Name) and n.id=='line_num' and isinstance(n.ctx,ast.Store)]==[170])
ck('23 backward dispositions',len(read('backward-snowball.json')['candidates'])==23)
b=read('baseline.json');ck('protected 2.45 PDF',sha(ROOT/'docs/design/proposal/manuscript-tableformer-20261012/accounting-product-proposal.pdf')==b['pdf_sha256'])
for row in b['pointer_snapshots']:ck('control preserved '+row['live'],sha(ROOT/row['live'])==sha(ROOT/row['snapshot'])==row['sha256'])
failed=[x['name'] for x in checks if not x['passed']]
out={'checks':checks,'passed':len(checks)-len(failed),'failed':failed,'wall_seconds':time.monotonic()-start,
 'scope':'Identity/source anchors and finite claim-specific counterexample; no model/runtime/accuracy evidence'}
(OUT/'source-checks.json').write_text(json.dumps(out,indent=2)+'\n');print({k:out[k] for k in ['passed','failed']});raise SystemExit(bool(failed))
