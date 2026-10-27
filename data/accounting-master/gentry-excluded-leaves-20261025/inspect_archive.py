"""Validate the retained archive identity and render selected original leaves."""
from pathlib import Path
from hashlib import sha1,sha256
from io import BytesIO
from PIL import Image
import json,re,xml.etree.ElementTree as ET,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
META=ROOT/'data/accounting-master/simulator-survey-source-recovery-20261025/gentry1974-archive-metadata.json'
SCAN=META.with_name('gentry1974-scandata.xml')
def sha(p):return sha256(p.read_bytes()).hexdigest()
def inspect():
    meta=json.loads(META.read_text());expected=next(f for f in meta['files'] if f['name']=='simulatingstrate180gent_jp2.zip')
    path=HERE/'source_jp2.zip';raw=path.read_bytes()
    assert len(raw)==int(expected['size']) and sha1(raw).hexdigest()==expected['sha1']
    scan_hash=next(f['sha1'] for f in meta['files'] if f['name'].endswith('_scandata.xml'))
    assert sha1(SCAN.read_bytes()).hexdigest()==scan_hash
    pages={int(p.attrib['leafNum']):p for p in ET.parse(SCAN).getroot().iter('page')}
    selected=[0,1,51,52,53,54,55];rows=[]
    with zipfile.ZipFile(path) as z:
        members={}
        for n in z.namelist():
            match=re.search(r'_(\d{4})\.jp2$',n)
            if match:
                leaf=int(match[1]);assert leaf not in members;members[leaf]=n
        assert set(members)==set(pages),('member_leaf_mapping',len(members),len(pages))
        for leaf in selected:
            data=z.read(members[leaf]);p=pages[leaf];original=HERE/('leaf-'+str(leaf)+'.jp2')
            if original.exists():assert original.read_bytes()==data
            else:original.write_bytes(data)
            image=Image.open(BytesIO(data));image.load();size=image.size
            image.thumbnail((1500,2100));out=HERE/('leaf-'+str(leaf)+'.png')
            image.convert('RGB').save(out)
            rows.append({'leaf':leaf,'member':members[leaf],'page_type':p.findtext('pageType'),
                'included':p.findtext('addToAccessFormats'),'printed_page':p.findtext('pageNumber'),
                'member_sha256':sha256(data).hexdigest(),'image_size':size,'render':str(out.relative_to(ROOT)),
                'render_sha256':sha(out)})
    result={'archive':str(path.relative_to(ROOT)),'archive_sha256':sha(path),'archive_sha1':sha1(raw).hexdigest(),
        'bytes':len(raw),'metadata_sha256':sha(META),'scandata_sha256':sha(SCAN),'member_count':len(members),'leaves':rows,
        'scope':'Identity and rendering only; visual findings recorded separately.'}
    target=HERE/'inspection.json';text=json.dumps(result,indent=2)+'\n'
    if target.exists():assert target.read_text()==text
    else:target.write_text(text)
    print(json.dumps({'archive_verified':True,'members':len(members),'selected':[{k:r[k] for k in ['leaf','page_type','included','printed_page']} for r in rows]}))
if __name__=='__main__':inspect()
