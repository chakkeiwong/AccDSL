"""Documentary identity and config-consumer checks; imports no upstream code."""
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PIN = 'd1569fdffee1d09cb3111d6d5490991cb59d59fd'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(ROOT))


def save(name, value):
    with (OUT / name).open('x') as f:
        f.write(json.dumps(value, indent=2) + '\n')


def main():
    tick = time.monotonic()
    checks, inputs, anchors = [], {}, []
    def ck(name, ok): checks.append(dict(id=name, passed=bool(ok)))
    def bind(p): inputs[rel(p)] = sha(p); return p
    def source(name): return bind(OUT/'sources'/name.replace('/', '__'))
    def method(name, cls, method_name, finding):
        p = source('docling_ibm_models/tableformer/' + name)
        text = p.read_text(); tree = ast.parse(text)
        c = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
        n = next(n for n in c.body if isinstance(n, ast.FunctionDef) and n.name == method_name)
        anchors.append(dict(path=rel(p), sha256=sha(p), symbol=cls+'.'+method_name,
                            first_line=n.lineno, last_line=n.end_lineno, finding=finding))
        return n, ast.get_source_segment(text, n)
    base = read(bind(OUT/'baseline.json')); prior = ROOT/base['prior_manifest']
    ck('previous manifest identity', sha(prior) == base['prior_manifest_sha256'] == read(prior.with_name('completion.json'))['manifest_sha256'])
    reloc = {x['historical_path']: x['preserved_path'] for x in base['pointer_relocations']}
    inherited = {reloc.get(p,p): h for p,h in read(prior)['artifact_hashes'].items()}
    ck('1485 prior references preserved', len(inherited)==1485 and all(sha(ROOT/p)==h for p,h in inherited.items()))
    tree = read(source('tree.json')); tag = read(source('tag-v4.0.2.json'))
    ck('tag and complete tree identity', tag['object']['sha']==tree['sha']==PIN and not tree['truncated'])
    blobs = {x['path']:x for x in tree['tree'] if x['type']=='blob'}
    records = read(bind(OUT/'acquisitions.json'))
    ck('sixteen distinct source URLs', len(records)==13 and len({r['url'] for r in records})==13)
    for r in records:
        p = bind(ROOT/r['path']); raw = p.read_bytes()
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        ck('Git blob '+r['upstream_path'], r['exit_code']==0 and r['curl_receipt'].startswith('200 ') and blob==blobs[r['upstream_path']]['sha']==r['computed_blob_sha1'] and sha(p)==r['sha256'])
    meta = read(source('pypi-4.0.2.json'))['info']; project=source('pyproject.toml').read_text()
    ck('package version and repository', meta['version']=='4.0.2' and 'version = "4.0.2"' in project and 'https://github.com/docling-project/docling-ibm-models' in meta['project_urls'].values())
    deps = meta['requires_dist']; base_deps=[x for x in deps if ';' not in x]
    ck('seven base requirements without OpenCV', len(base_deps)==7 and not any(x.lower().startswith('opencv') for x in base_deps))
    ck('two OpenCV extras', len(deps)==9 and all('extra ==' in x for x in deps if x.startswith('opencv')))
    predictor=source('docling_ibm_models/tableformer/data_management/tf_predictor.py')
    ck('unconditional cv2 import', any(isinstance(n,ast.Import) and any(a.name=='cv2' for a in n.names) for n in ast.parse(predictor.read_text()).body))
    _, loader=method('data_management/tf_predictor.py','TFPredictor','_load_model','First glob match; missing checkpoint and mismatched state failures; no filename/hash verification.')
    ck('first glob selection', 'models_fn[\n                0\n            ]' in loader and 'sorted(' not in loader)
    ck('no training checkpoint loader call', '.load(' not in loader and '_load_best_checkpoint' not in loader)
    method('data_management/tf_predictor.py','TFPredictor','__init__','Construct matchers, word map and model; CPU threads set before load.')
    method('data_management/tf_predictor.py','TFPredictor','_init_word_map','Embedded word map unless prepared_data_dir supplied.')
    method('data_management/tf_predictor.py','TFPredictor','predict','Reads max_steps and beam_size and forwards them to model.predict; matching and postprocessing follow.')
    method('data_management/tf_predictor.py','TFPredictor','_prepare_image','Normalize, resize, transpose and divide by 255; functional numerical semantics remain uninspected.')
    _, init=method('models/table04_rs/tablemodel04_rs.py','TableModel04_rs','__init__','Consumes train.bbox and caches predict.max_steps; creates Encoder04 before checkpoint load.')
    n, pred=method('models/table04_rs/tablemodel04_rs.py','TableModel04_rs','predict','Greedy argmax; formal max_steps and k unused; train.bbox false reaches None.to.')
    loads={x.id for x in ast.walk(n) if isinstance(x,ast.Name) and isinstance(x.ctx,ast.Load)}
    ck('max_steps and k formal arguments unused', {'max_steps','k'} <= {a.arg for a in n.args.args} and not {'max_steps','k'} & loads)
    ck('greedy decoding and stored step bound', 'logits.argmax(1).item()' in pred and 'while len(output_tags) < self._max_pred_len:' in pred and 'self._max_pred_len = config["predict"]["max_steps"]' in init)
    ck('bbox false source hazard', 'self._bbox = config["train"]["bbox"]' in init and 'outputs_class, outputs_coord = None, None' in pred and 'outputs_class.to(self._device)' in pred)
    _, enc=method('models/table04_rs/encoder04_rs.py','Encoder04','__init__','resnet18() relies on unpinned torchvision default; no global no-download claim.')
    ck('backbone uses dependency default', 'torchvision.models.resnet18()' in enc)
    for file,cls in [('data_management/tf_cell_matcher.py','CellMatcher'),('data_management/matching_post_processor.py','MatchingPostProcessor'),('models/table04_rs/bbox_decoder_rs.py','BBoxDecoder'),('models/table04_rs/transformer_rs.py','Tag_Transformer')]:
        method(file,cls,'__init__','Constructor inspected; downstream helpers and dependency semantics remain bounded source gaps.')
    config_records=[]
    for mode in ['accurate','fast']:
        p=bind(ROOT/f'data/accounting-master/docling-model-metadata-20261010/sources/tableformer__model_artifacts__tableformer__{mode}__tm_config.json'); config=read(p)
        ck(mode+' retained inference premises', config['train']['bbox'] is True and config['predict']['bbox'] is True and config['model']['type']=='TableModel04_rs' and 'prepared_data_dir' not in config['dataset'] and 'dataset_wordmap' in config)
        config_records.append(dict(mode=mode,path=rel(p),sha256=sha(p),beam_size_declared=config['predict']['beam_size'],beam_search_implemented_in_inspected_method=False,max_steps=config['predict']['max_steps'],train_bbox=config['train']['bbox']))
    common=source('docling_ibm_models/tableformer/common.py').read_text()
    ck('config validation is limited', 'if "model" not in config:\n        return True' in common and 'if "preparation" not in config:\n        return True' in common)
    license_text=source('LICENSE').read_text()
    ck('MIT terms retained', 'MIT License' in license_text and 'Copyright (c) 2024 International Business Machines' in license_text and 'included in all' in license_text)
    ck('Version 2.26 unchanged', sha(ROOT/base['pdf']['path'])==base['pdf']['sha256'])
    save('source-anchors.json',anchors)
    save('configuration-consumers.json',config_records)
    save('dependency-record.json',dict(version='4.0.2',commit=PIN,role='lower-bound inspection hypothesis',declared_requirements=deps,requires_python=meta['requires_python'],exact_dependency_lock=None,opencv_provision='Explicitly choose one provider for future resolution; no complete installation failure claimed',runtime_compatibility='not checked',code_license='MIT',model_license='Separate TableFormer card declaration: CDLA-Permissive-2.0'))
    save('checks.json',dict(recorded_at=datetime.now(timezone.utc).isoformat(),passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),checks=checks,inputs=inputs,checker_sha256=sha(Path(__file__)),wall_seconds=time.monotonic()-tick,evidence_class='documentary identity and static source checks; no runtime call-chain validation'))
    print(json.dumps(dict(passed=sum(c['passed'] for c in checks),failed=[c['id'] for c in checks if not c['passed']],anchors=len(anchors))))
    assert all(c['passed'] for c in checks)


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and not (OUT/'checks.json').exists()
    main()
