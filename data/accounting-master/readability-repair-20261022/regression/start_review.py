"""Bind the fresh review protocol and start empty synthesis records once."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys

U=Path(__file__).resolve().parent
R=U.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bind=lambda p:{'path':str(p.relative_to(R)),'sha256':sha(p)}
ledger=json.loads((U/'structure-ledger.json').read_text())
assert not ledger['ordered_segments'] and len(ledger['nodes'])==676
assert all(x['reading_status']=='pending' for x in ledger['nodes']+ledger['pages'])
for name in ('run-manifest.json','synthesis-ledger.json'):
    assert not (U/name).exists()
manifest={'started_utc':datetime.now(timezone.utc).isoformat(),
    'git_commit':json.loads((U.parent/'protection.json').read_text())['head'],
    'environment':sys.executable,'python':platform.python_version(),
    'cpu_gpu':'CPU only; GPU devices intentionally hidden with CUDA_VISIBLE_DEVICES=-1',
    'data_version':'Exact Version 3.47, 401 pages; source/PDF fixed during diagnosis',
    'seeds':'N/A deterministic document review','wall_time':'Open review; final elapsed time pending',
    'commands_run':['setup.py','initialize.py init','initialize.py validate','start_review.py'],
    'command_environment':'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B',
    'tooling':bind(U/'tooling-manifest.json'),
    'plan':bind(R/'docs/plans/accounting-readability-regression-20261022.md'),
    'candidate_pdf':bind(R/ledger['baseline_pdf']),
    'initial_inventory':{'pages':401,'nodes':676,'sources':144,'reading':'all pending'},
    'result':str((U/'document-synthesis.md').relative_to(R)),
    'output':str(U.relative_to(R)),
    'recording_policy':'Actual ordered view calls precede each authored segment; no reading credit imported'}
(U/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
synthesis={'status':'in_progress','candidate_pdf':ledger['baseline_pdf'],
    'pdf_sha256':ledger['pdf_sha256'],'chapter_regressions':[],
    'cumulative_prefixes':[],'document_synthesis':None,
    'independent_reader':'pending','human_acceptance':'pending'}
(U/'synthesis-ledger.json').write_text(json.dumps(synthesis,indent=2)+'\n')
print(json.dumps({'review_started':'3.47','chapters_synthesized':0,'prefixes_synthesized':0}))
