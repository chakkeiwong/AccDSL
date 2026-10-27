"""Prepare preservation checker without rebuilding existing model logic."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).resolve().parent
old=ROOT/'data/accounting-master/p17-completion-20261014/P17-07/connected-groups/verify_candidate.py'
s=old.read_text().replace('2.83 supplement','2.84 supplement').replace('{"accounting-product-proposal.tex","sections/insurance-methods.tex","sections/bank-methods.tex"}','{"accounting-product-proposal.tex","chapters/05-mathematics.tex"}').replace('{"sections/insurance-connected-groups.tex"}','{"sections/query-resolution-boundaries.tex"}').replace('final-render-v2/render-manifest.json','final-render/render-manifest.json')
(OUT/'verify_candidate.py').write_text(s)
(OUT/'content-dispositions.json').write_text(json.dumps({'modified':['accounting-product-proposal.tex','chapters/05-mathematics.tex'],'added':['sections/query-resolution-boundaries.tex'],'derivation':'Local rational algebra and retained2.82/2.83 conditional cases; no new external authority','narrative_repair':'Place after the existing grouping and finite-probability prerequisites; supply sector comparison inputs here, derive accounting later','removed_content':[]},indent=2)+'\n')
print(json.dumps({'checker_prepared':True,'manuscript_modified_sources':2,'added':1}))
