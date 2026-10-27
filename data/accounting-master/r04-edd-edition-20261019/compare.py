"""Static source/edition checker; never imports acquired code."""
from pathlib import Path
import ast
import hashlib
import json
U=Path(__file__).resolve().parent
R=U.parents[2]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def defaults(text):
    out={}
    for n in ast.walk(ast.parse(text)):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='add_argument':
            if n.args and isinstance(n.args[0],ast.Constant):
                for k in n.keywords:
                    if k.arg=='default':out[n.args[0].value]=ast.literal_eval(k.value)
    return out

def check():
    l=json.loads((U/'source-ledger.json').read_text())
    assert len(l['acquisitions'])==6
    for x in l['acquisitions']:
        for k in ('body','headers'):
            p=R/x[k]['path'];assert sha(p)==x[k]['sha256'],str(p)
        assert (R/x['body']['path']).stat().st_size==x['bytes']
        assert x['status']==200 and x['redirects']==0
        assert '200' in (R/x['headers']['path']).read_text().splitlines()[0]
    for x in l['bindings']:assert sha(R/x['path'])==x['sha256'],x['path']
    for x in l['passages']:
        s=(R/x['path']).read_text();assert x['needle'] in s,x['id']
    for x in l['read_spans']:
        a=(R/x['path']).read_text().splitlines(keepends=True)
        assert hashlib.sha256(''.join(a[x['start']-1:x['end']]).encode()).hexdigest()==x['sha256']
    s=(U/'sources/04-training.py').read_text();d=defaults(s)
    expected={'--cell_embed_dim':16,'--encoded_image_size':14,'--tag_attention_dim':512,
              '--cell_attention_dim':512,'--tag_decoder_dim':512,'--batch_size':16,
              '--cell_decoder_type':1,'--predict_content':False,'--predict_bbox':False,
              '--detach':False,'--dropout':0.5,'--grad_clip':5.0}
    for k,v in expected.items():assert d[k]==v,k
    calls=[n for n in ast.walk(ast.parse(s)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='train_epoch']
    assert len(calls)==1
    bbox=next(k.value for k in calls[0].keywords if k.arg=='cell_bbox_regressor_optimizer')
    assert isinstance(bbox,ast.Name) and bbox.id=='cell_decoder_optimizer'
    prep=defaults((U/'sources/05-preparation.py').read_text())
    for k,v in {'--min_word_freq':5,'--max_tag_len':300,'--max_cell_len':100,'--max_image_size':512,'--image_size':448,'--keep_AR':False}.items():assert prep[k]==v
    ev=defaults((U/'sources/06-evaluation.py').read_text())
    assert ev['--beam_size']=={'tag':3,'cell':3}
    assert ev['--max_steps']=={'tag':1800,'cell':600}
    assert ev['--dual_decoder'] is False
    assert len([x for x in (U/'sources/02-published.txt').read_text().split('\f') if x.strip()])==17
    for n in ('source-support','citation-venue','backward-snowball','forward-snowball','claim-support','omitted-paper'):
        x=json.loads((U/(n+'-ledger.json')).read_text());assert x['scope'] and x['entries']
    return {'acquisitions':6,'pinned_code_files':4,'published_pages':17,
            'rendered_pages':[7],'selected_passages':len(l['passages']),
            'scoped_read_spans':len(l['read_spans']),'ast_default_checks':len(expected)+9,
            'bbox_optimizer_argument':'cell_decoder_optimizer; optional path disabled in selected recipe',
            'model_source_available':True,'full_dependency_audit':False,
            'published_supplement_read':False,'model_execution':False,'financial_admission':False}
