"""Verify notice spans and author coverage without certifying permission."""
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
TERMS=ROOT/'data/accounting-master/taxonomy-reuse-20261007/sources'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
rel=lambda p:str(p.relative_to(ROOT))
LEGAL=re.compile(rb'copyright|permission|licen[cs]e|rights reserved|xbrl\.org/legal|termsconditions|conditions of use',re.I)


def save(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def main():
    started,timer=datetime.now(timezone.utc).isoformat(),time.monotonic()
    checks=[];inputs={}
    def ck(name,ok):checks.append(dict(id=name,passed=bool(ok)))
    def verify(mapping,name):
        bad=[p for p,h in mapping.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
        ck(name,not bad)
        if not bad:inputs.update(mapping)
    inv=read(OUT/'notice-inventory.json');author=read(OUT/'author-dispositions.json')
    verify(inv['inputs'],'all 27 original graph members and graph hashes')
    ck('inventory scanner bound',inv['scanner_sha256']==sha(OUT/'inventory.py'))
    ck('27 declared members',inv['node_count']==len(inv['records'])==27)
    assignments=[(n,g['id']) for g in author['groups'] for n in g['nodes']]
    ck('author dispositions cover each member once',len(assignments)==27 and len(dict(assignments))==27
       and set(dict(assignments))=={r['id'] for r in inv['records']})
    counts={g['id']:len(g['nodes']) for g in author['groups']}
    ck('six distinct source categories retain declared counts',list(counts.values())==[5,6,5,6,4,1])
    lookup={r['id']:r for r in inv['records']};notices={n['id']:n for r in inv['records'] for n in r['notices']}
    for row in inv['records']:
        raw=(ROOT/row['path']).read_bytes();span_ok=True
        for n in row['notices']:
            body=(ROOT/n['path']).read_bytes()
            span_ok &= body==raw[n['start_byte']:n['end_byte']] and sha(ROOT/n['path'])==n['sha256']
            span_ok &= raw[:n['start_byte']].count(b'\n')+1==n['first_line'] and raw[:n['end_byte']].count(b'\n')+1==n['last_line']
            inputs[n['path']]=n['sha256']
        ck(row['id']+' exact original notice byte spans',span_ok)
    ck('22 candidates with one declared false positive',len(notices)==inv['notice_count']==22
       and set(author['candidate_dispositions'])=={'node-19/notice-02'})
    ck('six explicitly unlocated notices',sum(not r['notices'] for r in inv['records'])==6)
    sec_ok=True
    for n in ['node-16','node-25','node-26','node-27']:
        body=(ROOT/lookup[n]['notices'][0]['path']).read_text()
        sec_ok &= all(t in body for t in ['staff of the U.S. Securities','government employees within the scope','domestic copyright protection. 17 U.S.C. 105.'])
    ck('complete three-comment SEC qualification retained',sec_ok)
    dim=(ROOT/lookup['node-24']['notices'][0]['path']).read_text()
    ck('dimensions copying and derivative conditions retained',all(t in dim for t in
        ['may be copied and furnished','comment on or otherwise explain','assist in its implementation',
         'copyright notice and this','included on all such copies','trademark or service mark']))

    keyword_dispositions=[]
    false=notices['node-19/notice-02'];raw=(ROOT/lookup['node-19']['path']).read_bytes()
    body=raw[false['start_byte']:false['end_byte']]
    for m in LEGAL.finditer(body):
        a=body.rfind(b'<',0,m.start());b=body.find(b'>',m.end())+1;tag=body[a:b]
        valid=bool(re.match(rb'<link:(?:loc|definitionArc)\s',tag)) and b'License' in tag
        ck('appinfo keyword at '+str(m.start())+' is a concept attribute',valid)
        keyword_dispositions.append(dict(node='node-19',source_path=lookup['node-19']['path'],
            start_byte=false['start_byte']+a,end_byte=false['start_byte']+b,text=tag.decode(),
            disposition='concept locator/arc attribute; no permission prose'))
    ck('nine appinfo keyword candidates disposed',len(keyword_dispositions)==9)
    unmatched=0
    for row in inv['records']:
        raw=(ROOT/row['path']).read_bytes()
        for offset in row['unmatched_keyword_offsets']:
            unmatched+=1
            if row['id'] in {'node-19','node-26'}:
                a=raw.rfind(b'<',0,offset);b=raw.find(b'>',offset)+1;context=raw[a:b]
                ck(row['id']+' keyword '+str(offset)+' is element metadata',context.startswith(b'<xs:element '))
                disposition='financial concept element attributes; no permission grant'
            else:
                assert row['id']=='node-06'
                a=max(0,offset-110);b=offset+220;context=raw[a:b]
                ck('instance keyword is financial disclosure',b'unconditional purchase obligations' in context
                   and b'licensed intellectual property and content' in context)
                disposition='Apple commitment disclosure about licensed content; no file-use notice'
            keyword_dispositions.append(dict(node=row['id'],source_path=row['path'],start_byte=a,end_byte=b,
                keyword_offset=offset,text=context.decode(),disposition=disposition))
    ck('all 61 unmatched keyword candidates disposed',unmatched==inv['unmatched_keywords']==61)
    save('keyword-dispositions.json',dict(records=keyword_dispositions,counts=dict(appinfo=9,unmatched=61),
        no_legal_completeness_claim=True))

    class Links(HTMLParser):
        def __init__(self):super().__init__();self.links=[];self.current=None
        def handle_starttag(self,tag,attrs):
            if tag=='a':self.current=dict(href=dict(attrs).get('href',''),text='')
        def handle_data(self,text):
            if self.current is not None:self.current['text']+=text
        def handle_endtag(self,tag):
            if tag=='a' and self.current is not None:self.links.append(self.current);self.current=None
    html=TERMS/'terms-xbrl-copyright-trusted.body';p=Links();p.feed(html.read_text())
    named=[r for r in p.links if 'software notice' in r['text'].casefold()]
    guessed='https://www.xbrl.org/legal/software-license-2009-01-01.html'
    ck('no exact Software Notice link in retained copyright page',not named and guessed not in [r['href'] for r in p.links])
    save('software-notice-route.json',dict(source=rel(html),sha256=sha(html),links=p.links,
        named_software_notice_links=named,old_guessed_url=guessed,old_status=404,
        old_receipt=rel(TERMS/'terms-xbrl-software-trusted.receipt.json'),
        decision='No new exact route from this retained page; do not repeat guessed address',network_requests=0))
    for n in ['terms-xbrl-copyright-trusted.body','terms-xbrl-copyright.txt','terms-usgaap.txt','terms-srt.txt',
              'terms-usgaap-trusted.body','terms-srt-trusted.body','terms-xbrl-software-trusted.receipt.json']:
        inputs[rel(TERMS/n)]=sha(TERMS/n)
    base=read(OUT/'baseline.json');prior=read(ROOT/base['prior_manifest'])
    reloc={x['historical_path']:x['preserved_path'] for x in base['pointer_relocations']}
    verify({reloc.get(n,n):h for n,h in prior['artifact_hashes'].items()},'1176 preceding references preserved')
    ck('preceding manifest identity',sha(ROOT/base['prior_manifest'])==base['prior_manifest_sha256'])
    ck('Version 2.25 unchanged',sha(ROOT/base['pdf']['path'])==base['pdf']['sha256'])
    for n in ['notice-inventory.json','author-dispositions.json','author-review.md','keyword-dispositions.json','software-notice-route.json']:
        inputs[rel(OUT/n)]=sha(OUT/n)
    report=dict(checker_sha256=sha(Path(__file__)),inputs=inputs,checks=checks,passed=sum(c['passed'] for c in checks),
        failed=sum(not c['passed'] for c in checks),category_counts=counts,started_at=started,wall_seconds=time.monotonic()-timer,
        command='CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 '+rel(Path(__file__)),
        python_executable=sys.executable,CUDA_VISIBLE_DEVICES='-1',cpu_gpu_status='CPU only; GPU devices intentionally hidden',
        readiness='not_ready',distribution_admission=False)
    save('checks.json',report)
    print(json.dumps(dict(passed=report['passed'],failed=report['failed'],category_counts=counts)))
    assert not report['failed'],[c['id'] for c in checks if not c['passed']]


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (OUT/'completion.json').exists()
    main()
