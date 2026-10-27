"""Static EasyOCR source and metadata checks; no imports or model execution."""
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
rel=lambda p:str(p.relative_to(ROOT))


def main():
    tick=time.monotonic();checks=[];inputs={};anchors=[]
    def ck(name,ok):checks.append(dict(id=name,passed=bool(ok)))
    def bind(p):inputs[rel(p)]=sha(p);return p
    def src(name):return bind(OUT/'sources'/name.replace('/','__'))
    def method(file,name,finding):
        p=src(file);t=ast.parse(p.read_text());c=next(x for x in t.body if isinstance(x,ast.ClassDef) and x.name=='Reader');n=next(x for x in c.body if isinstance(x,ast.FunctionDef) and x.name==name)
        anchors.append(dict(path=rel(p),sha256=sha(p),symbol='Reader.'+name,first_line=n.lineno,last_line=n.end_lineno,finding=finding))
        return ast.get_source_segment(p.read_text(),n)
    b=read(bind(OUT/'baseline.json'));prior=ROOT/b['prior_manifest'];p=read(prior)
    ck('prior manifest identity',sha(prior)==b['prior_manifest_sha256']==read(prior.with_name('completion.json'))['manifest_sha256'])
    reloc={x['historical_path']:x['preserved_path'] for x in b['pointer_relocations']}
    inherited={reloc.get(k,k):v for k,v in p['artifact_hashes'].items()}
    ck('1539 prior references',len(inherited)==1539 and all(sha(ROOT/f)==h for f,h in inherited.items()))
    pin='c4f3cd7225efd4f85451bd8b4a7646ae9a092420'
    tags=read(src('tags.json'));tree=read(src('tree.json'))
    ck('official pinned tag/tree',next(x for x in tags if x['name']=='v1.7.2')['commit']['sha']==tree['sha']==pin and not tree['truncated'])
    blobs={x['path']:x for x in tree['tree'] if x['type']=='blob'}
    recs=read(bind(OUT/'acquisitions.json'))
    ck('bounded unique source requests',len(recs)==16 and len({r['url'] for r in recs})==16)
    for r in recs:
        f=bind(ROOT/r['path']);raw=f.read_bytes()
        ck('retrieval '+f.name,r['exit_code']==0 and r['curl_receipt'].startswith('200 ') and sha(f)==r['sha256'])
        if 'upstream_path' in r:
            blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            ck('Git blob '+f.name,blob==blobs[r['upstream_path']]['sha']==r['computed_blob'])
    info=read(src('pypi.json'))['info'];setup=src('setup.py').read_text();requirements=src('requirements.txt').read_text().splitlines()
    ck('PyPI/source version',info['version']=='1.7.2' and "version='1.7.2'" in setup and info['home_page'].lower()=='https://github.com/jaidedai/easyocr')
    ck('requirements match metadata',len(requirements)==len(info['requires_dist'])==12 and set(requirements)==set(info['requires_dist']))
    cfg=src('easyocr/config.py');literal=ast.parse(cfg.read_text());det=next(ast.literal_eval(x.value) for x in literal.body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='detection_models' for y in x.targets))
    rec_node=next(x.value for x in literal.body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='recognition_models' for y in x.targets))
    gen2=next(v for k,v in zip(rec_node.keys,rec_node.values) if ast.literal_eval(k)=='gen2')
    english=next(ast.literal_eval(v) for k,v in zip(gen2.keys,gen2.values) if ast.literal_eval(k)=='english_g2')
    selected=[dict(role='detector',name='craft',**det['craft']),dict(role='recognizer',name='english_g2',**english)]
    releases=[read(src('release-craft.json')),read(src('release-english.json'))]
    for item,release in zip(selected,releases):
        assert item['url'].split('/download/')[1].split('/')[0]==release['tag_name']
        asset=next(x for x in release['assets'] if x['browser_download_url']==item['url'])
        item.update(release_tag=release['tag_name'],release_published_at=release['published_at'],release_asset_bytes=asset['size'],release_asset_digest=asset.get('digest'),local_bytes_verified=False)
        ck('release asset '+item['name'],asset['size']>0 and asset.get('digest') is None and len(item['md5sum'])==32)
    init=method('easyocr/easyocr.py','__init__','English standard selects english_g2; default detector craft; no-download MD5 fail-closed; auxiliary path side effects.')
    ck('English selection',"if lang_list == ['en']:" in init and "recognition_models['gen2']['english_g2']" in init and 'detect_network="craft"' in init)
    ck('download false and MD5 guards',init.count('if not self.download_enabled:')>=2 and "calculate_md5(model_path) != model['md5sum']" in init)
    ck('auxiliary directory and sys.path',"Path(self.user_network_directory).mkdir" in init and 'sys.path.append(self.user_network_directory)' in init)
    detpath=method('easyocr/easyocr.py','getDetectorPath','Missing/corrupt detector uses download flag and MD5.')
    ck('detector download guard',detpath.count('if not self.download_enabled:')>=2 and 'calculate_md5(detector_path)' in detpath)
    lang=method('easyocr/easyocr.py','setLanguageList','English character data from package path.')
    ck('character data',"'character', lang + \"_char.txt\"" in lang or "'character', lang + \"_char.txt\"" in src('easyocr/easyocr.py').read_text())
    detection=src('easyocr/detection.py').read_text();recognition=src('easyocr/recognition.py').read_text()
    ck('both checkpoint loaders disable weights-only', 'torch.load(trained_model, map_location=device, weights_only=False)' in detection and 'torch.load(model_path, map_location=device, weights_only=False)' in recognition)
    docling=bind(ROOT/'data/accounting-master/docling-model-paths-20261010/sources/docling__models__stages__ocr__easyocr_model.py').read_text()
    ck('Docling passes model storage and flag', 'model_storage_directory=model_storage_directory' in docling and 'download_enabled=download_enabled' in docling)
    ck('Docling prefetch skips by existence', 'recognition_models: List[str] = ["english_g2", "latin_g2"]' in docling and 'exists() and not force' in docling and 'calculate_md5' not in docling)
    candidate=read(bind(ROOT/'data/accounting-master/docling-model-paths-20261010/configuration-records.json'))
    ck('candidate remains documentary', 'english_ocr' in str(candidate) and 'download_enabled' in str(candidate))
    ck('PDF unchanged',sha(ROOT/b['pdf']['path'])==b['pdf']['sha256'])
    (OUT/'source-anchors.json').write_text(json.dumps(anchors,indent=2)+'\n')
    (OUT/'asset-records.json').write_text(json.dumps(selected,indent=2)+'\n')
    (OUT/'dependency-record.json').write_text(json.dumps(dict(version='1.7.2',commit=pin,role='inspection hypothesis',declared_requirements=info['requires_dist'],exact_lock=None,code_license='Apache License 2.0',model_rights='not established; CRAFT pretrained model credited to external project',local_assets='not downloaded',runtime='not checked'),indent=2)+'\n')
    result=dict(recorded_at=datetime.now(timezone.utc).isoformat(),passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),checks=checks,inputs=inputs,checker_sha256=sha(Path(__file__)),wall_seconds=time.monotonic()-tick,evidence_class='static documentary; no runtime')
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=result['passed'],failed=[x['id'] for x in checks if not x['passed']],anchors=len(anchors))))
    assert result['failed']==0


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and not (OUT/'checks.json').exists()
    main()
