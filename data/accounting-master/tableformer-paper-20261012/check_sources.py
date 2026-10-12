"""Verify source identity, preserved comparators and selected technical anchors."""
import ast
import hashlib
import json
import time
from pathlib import Path

import fitz
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n): return json.loads((OUT / n).read_text())
assert not (OUT / 'completion.json').exists()
start = time.monotonic()
checks = []
def ck(name, ok): checks.append({'name': name, 'passed': bool(ok)})
expected = {'paper':('dd02572fd5199bde6fdf41ca8e3494c1769bd995acd99ad81e8e0a40ff881c8d',10),
            'supplement':('6b603c344a8377238d0c60b1dc787f425a3cfd9f915e4d9972d620f45fa4faa3',6)}
for name,(digest,count) in expected.items():
    p = OUT / 'sources' / (name + '.pdf')
    ck(name + ' identified PDF', sha(p) == digest and len(fitz.open(p)) == count)
for row in read('paper-copies.json'):
    ck('descriptive copy ' + row['copy'], sha(ROOT / row['copy']) == sha(ROOT / row['source']) == row['sha256'])
receipts = read('access-receipts.json')
ck('four resources within bound', receipts['distinct_resources'] == 4 <= 8)
for r in receipts['attempts']:
    if r['body']:
        ck('response identity ' + r['attempt'], r['http_code'] == 200 and r['curl_exit_code'] == 0 and r['bytes'] == (ROOT / r['body']).stat().st_size and sha(ROOT / r['body']) == r['sha256'])
    else:
        ck('sandbox DNS failure separate', r['http_code'] == 0 and r['curl_exit_code'] == 6 and not r['trusted'])
landing = BeautifulSoup((OUT / 'sources/cvf-landing.html').read_text(), 'html.parser').get_text(' ',strip=True)
cr = json.loads((OUT / 'sources/crossref.json').read_text())['message']
ck('landing title and author', 'TableFormer' in landing and 'Nassar' in landing)
ck('DOI identity', cr['DOI'].lower() == '10.1109/cvpr52688.2022.00457')
ck('metadata page conflict preserved', cr['page'] == '4604-4613' and '4614-4623' in landing)
pages = read('paper-pages.json')
ck('PDF printed page range', '4614' in pages[0]['text'] and '4623' in pages[-1]['text'])
t7 = pages[6]['text']
ck('Table 4 content target', 'structure with content' in t7.lower() and 'cropped' in t7.lower())
for n in ['95.4','90.1','93.6','98.5','95.0','96.75','97.5','96.0','96.8','89.6','96.9','95.7','96.7']:
    ck('reported table value ' + n, n in t7)
ck('model card matching row', all(n in (ROOT / 'data/accounting-master/docling-model-metadata-20261010/sources/tableformer__README.md').read_text() for n in ['95.4','90.1','93.6']))
for row in read('render-manifest.json'):
    ck('inspected render binding ' + row['source'] + '-' + str(row['page']), sha(ROOT / row['render']) == row['sha256'] and sha(OUT / 'sources' / (row['source'] + '.pdf')) == row['source_sha256'])
code = read('code-anchors.json')
for r in code['sources']: ck('retained code hash ' + Path(r['path']).name, sha(ROOT / r['path']) == r['sha256'])
model = (ROOT / code['sources'][0]['path']).read_text()
predictor = (ROOT / code['sources'][1]['path']).read_text()
process = (ROOT / code['sources'][2]['path']).read_text()
tree = ast.parse(model)
method = next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name == 'predict')
used = {n.id for stmt in method.body for n in ast.walk(stmt) if isinstance(n,ast.Name)}
ck('predict does not consume max_steps or k', {'max_steps','k'}.isdisjoint(used))
ck('argmax and cached bound', 'logits.argmax(1).item()' in model and 'while len(output_tags) < self._max_pred_len' in model)
ck('later OTSL conversion and external text', 'otsl_to_html(prediction["rs_seq"], False)' in predictor and '"token": pdf_cell["text"]' in predictor)
ck('later matching 300-cell branches', 'len(pdf_cells) > 300' in process and 'len(table_cells_wo) <= 300' in process)
for arm,depth in [('accurate',(6,6)),('fast',(4,2))]:
    p = ROOT / f'data/accounting-master/docling-model-metadata-20261010/sources/tableformer__model_artifacts__tableformer__{arm}__tm_config.json'
    d = json.loads(p.read_text())
    ck(arm + ' architecture', (d['model']['enc_layers'],d['model']['dec_layers']) == depth and d['model']['nheads'] == 8 and d['model']['dropout'] == .1)
    ck(arm + ' inference declarations', d['predict']['max_steps'] == 1024 and d['predict']['beam_size'] == 5 and d['predict']['bbox'] and d['train']['bbox'])
forward = read('forward-snowball.json')
ck('Docling forward source identity', sha(ROOT / forward['source']) == forward['sha256'] == '82dd470712ce8389f19f20eb9330475e2166a281f8c7990a9f1d0763d73b4d22')
doc = fitz.open(ROOT / forward['source'])
ck('Docling exact follow-up', 'custom structure token language' in ' '.join(doc[2].get_text().split()) and 'Optimized Table Tokenization' in ' '.join(doc[5].get_text().split()))
ck('39 reference dispositions', len(read('backward-snowball.json')['candidates']) == 39)
b = read('baseline.json')
ck('protected 2.44 PDF', sha(ROOT / 'docs/design/proposal/manuscript-score-rounding-20261012/accounting-product-proposal.pdf') == b['pdf_sha256'])
for r in b['pointer_snapshots']: ck('unchanged control ' + r['live'], sha(ROOT / r['live']) == sha(ROOT / r['snapshot']) == r['sha256'])
failed = [r['name'] for r in checks if not r['passed']]
result = {'passed':len(checks)-len(failed),'failed':failed,'checks':checks,'wall_seconds':time.monotonic()-start,
          'scope':'Identity, preservation and selected source anchors; author reading is recorded separately. No model or ranking test.'}
(OUT / 'source-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['passed','failed']}))
raise SystemExit(bool(failed))
