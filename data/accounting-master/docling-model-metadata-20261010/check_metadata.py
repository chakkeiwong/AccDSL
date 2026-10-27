"""Validate official metadata and retained text; no weight/runtime validation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
rel=lambda p:str(p.relative_to(ROOT))


def save(name,data):
    with (OUT/name).open('x') as f:f.write(json.dumps(data,indent=2,ensure_ascii=False)+'\n')


def main():
    tick=time.monotonic();checks=[];inputs={}
    def ck(name,ok):checks.append(dict(id=name,passed=bool(ok)))
    def bind(p):inputs[rel(p)]=sha(p)
    base=read(OUT/'baseline.json');prior=ROOT/base['prior_manifest'];m=read(prior)
    ck('prior manifest',sha(prior)==base['prior_manifest_sha256']==read(prior.with_name('completion.json'))['manifest_sha256'])
    reloc={x['historical_path']:x['preserved_path'] for x in base['pointer_relocations']}
    inherited={reloc.get(p,p):h for p,h in m['artifact_hashes'].items()}
    ck('1441 references preserved',len(inherited)==1441 and all((ROOT/p).is_file() and sha(ROOT/p)==h for p,h in inherited.items()))
    records=[]
    expected={'heron':('docling-project/docling-layout-heron','main','8f39ad3c0b4c58e9c2d2c84a38465abf757272d8','apache-2.0',6),
              'tableformer':('docling-project/docling-models','v2.3.0','fc0f2d45e2218ea24bce5045f58a389aed16dc23','cdla-permissive-2.0',8)}
    for label,(repo,ref,pin,lic,count) in expected.items():
        p=OUT/f'sources/{label}-metadata.json';d=read(p);bind(p)
        ck(label+' repository identity',d['id']==repo and d['sha']==pin and not d['private'] and not d['disabled'])
        ck(label+' licence declaration',d['cardData']['license']==lic)
        ck(label+' returned inventory',len(d['siblings'])==count and len({x['rfilename'] for x in d['siblings']})==count)
        ck(label+' no standalone licence/notice in inventory',not any('license' in x['rfilename'].lower() or 'notice' in x['rfilename'].lower() for x in d['siblings']))
        items=[]
        for x in d['siblings']:
            weight='lfs' in x
            ck(label+' file metadata '+x['rfilename'],x['size']>0 and len(x['blobId'])==40 and (not weight or len(x['lfs']['sha256'])==64 and x['lfs']['size']==x['size']))
            items.append(dict(filename=x['rfilename'],bytes=x['size'],upstream_git_blob=x['blobId'],upstream_lfs_sha256=x.get('lfs',{}).get('sha256'),is_weight=weight,local_weight_bytes_verified=False if weight else None))
        records.append(dict(model=label,repository=repo,requested_revision=ref,resolved_commit=pin,metadata=rel(p),metadata_sha256=sha(p),declared_license=lic,files=items,
            promotion='inspection candidate only',historical_model_identity='not established' if ref=='main' else 'tag resolution observed at retrieval',license_scope='repository declaration; complete contributor/component authority not established'))
    save('model-records.json',records)
    acquisitions=read(OUT/'text-acquisitions.json');ck('seven text-only acquisitions',len(acquisitions)==7 and all(x['filename'].endswith(('.md','.json')) and x['bytes']<1048576 for x in acquisitions))
    for x in acquisitions:
        p=ROOT/x['path'];raw=p.read_bytes();bind(p)
        ck('exact text '+x['model']+'/'+x['filename'],sha(p)==x['sha256'] and x['exit_code']==0 and x['curl_receipt'].startswith('200 ') and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==x['expected_blob'])
    heron=read(OUT/'sources/heron__config.json');pre=read(OUT/'sources/heron__preprocessor_config.json')
    ck('Heron type and label vocabulary',heron['architectures']==['RTDetrV2ForObjectDetection'] and heron['model_type']=='rt_detr_v2' and len(heron['id2label'])==17 and {int(k):v for k,v in heron['id2label'].items()}=={v:k for k,v in heron['label2id'].items()})
    ck('Heron preprocessing declaration',pre['size']=={'height':640,'width':640} and pre['do_rescale'] and not pre['do_normalize'] and not pre['do_pad'] and abs(pre['rescale_factor']-1/255)<1e-16)
    accurate=read(OUT/'sources/tableformer__model_artifacts__tableformer__accurate__tm_config.json');fast=read(OUT/'sources/tableformer__model_artifacts__tableformer__fast__tm_config.json')
    differences=[]
    def compare(a,b,path=''):
        for k in sorted(a.keys()|b.keys()):
            x,y=a.get(k),b.get(k)
            if isinstance(x,dict) and isinstance(y,dict):compare(x,y,path+'/'+k)
            elif x!=y:differences.append(dict(path=path+'/'+k,accurate=x,fast=y))
    compare(accurate,fast)
    ck('only two table config differences',differences==[dict(path='/model/dec_layers',accurate=6,fast=2),dict(path='/model/enc_layers',accurate=6,fast=4)])
    save('configuration-differences.json',dict(differences=differences,meaning='Declared JSON settings only; speed, accuracy and executed inference consumers untested'))
    ck('table prediction settings',accurate['predict']['max_steps']==1024 and accurate['predict']['beam_size']==5 and accurate['predict']['pdf_cell_iou_thres']==0.05)
    apache=OUT/'sources/apache-2.0.txt';cdla=OUT/'sources/cdla-2.0.txt';bind(apache);bind(cdla);bind(OUT/'sources/cdla-2.0.html')
    ck('Apache complete numbered agreement',all(x in apache.read_text() for x in ['1. Definitions.','2. Grant of Copyright License.','3. Grant of Patent License.','4. Redistribution.','5. Submission of Contributions.','6. Trademarks.','7. Disclaimer of Warranty.','8. Limitation of Liability.','9. Accepting Warranty or Additional Liability.','APPENDIX: How to apply']))
    ck('CDLA complete numbered agreement',all(x in cdla.read_text() for x in ['1. Provision of the Data','2. Conditions for Sharing Data','3. No Restrictions on Results','4. No Warranty; Limitation of Liability','5. Definitions','5.4.']))
    ck('no local weights',not any(p.suffix in {'.safetensors','.bin','.pt','.pth','.onnx'} for p in OUT.rglob('*')))
    ck('candidate unchanged',sha(ROOT/base['pdf']['path'])==base['pdf']['sha256'])
    for p in OUT.glob('*.json'):
        if p.name not in {'checks.json','run-manifest.json','completion.json'}:bind(p)
    report=dict(passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),checks=checks,inputs=inputs,checker_sha256=sha(Path(__file__)),wall_seconds=time.monotonic()-tick,pdf=base['pdf'],recorded_at=datetime.now(timezone.utc).isoformat())
    save('checks.json',report);print(json.dumps({k:report[k] for k in ['passed','failed','wall_seconds']}));assert not report['failed'],[x['id'] for x in checks if not x['passed']]


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    main()
