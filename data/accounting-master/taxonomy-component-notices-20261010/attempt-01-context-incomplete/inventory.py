"""Locate embedded legal-text candidates; do not infer permission from hosts."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
GRAPH=ROOT/'data/accounting-master/taxonomy-reuse-20261007/graph-final.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:str(p.relative_to(ROOT))
LEGAL=re.compile(rb'copyright|permission|licen[cs]e|rights reserved|xbrl\.org/legal|termsconditions|conditions of use',re.I)


def main():
    timer=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    graph=json.loads(GRAPH.read_text());assert len(graph['nodes'])==27
    bodies=OUT/'notices';bodies.mkdir(exist_ok=True)
    inputs={rel(GRAPH):sha(GRAPH)};records=[]
    for i,node in enumerate(graph['nodes'],1):
        p=ROOT/node['path'];assert sha(p)==node['sha256'];inputs[node['path']]=node['sha256'];raw=p.read_bytes()
        candidates=[]
        comment=re.compile(rb'<!--.*?-->',re.S)
        annotation=re.compile(rb'<((?:[A-Za-z_][\w.-]*:)?annotation)\b[^>]*>.*?</\1\s*>',re.S)
        for kind,pattern in [('comment',comment),('annotation',annotation)]:
            for match in pattern.finditer(raw):
                if LEGAL.search(match.group()):candidates.append((kind,match.start(),match.end(),match.group()))
        candidates.sort(key=lambda x:x[1]);notices=[]
        for j,(kind,start,end,body) in enumerate(candidates,1):
            q=bodies/f'node-{i:02}-notice-{j:02}.xmlfrag';q.write_bytes(body)
            notices.append(dict(id=f'node-{i:02}/notice-{j:02}',kind=kind,start_byte=start,end_byte=end,
                first_line=raw[:start].count(b'\n')+1,last_line=raw[:end].count(b'\n')+1,
                path=rel(q),sha256=sha(q),bytes=len(body)))
        unmatched=[m.start() for m in LEGAL.finditer(raw) if not any(a<=m.start()<b for _,a,b,_ in candidates)]
        records.append(dict(id=f'node-{i:02}',uri=node['uri'],path=node['path'],sha256=node['sha256'],
            target_namespace=node['target_namespace'],notices=notices,unmatched_keyword_offsets=unmatched,
            disposition='author review pending',no_notice_means='No nominated embedded permission; not permission to use'))
    value=dict(graph_sha256=sha(GRAPH),inputs=inputs,records=records,node_count=27,
        notice_count=sum(len(r['notices']) for r in records),
        unmatched_keywords=sum(len(r['unmatched_keyword_offsets']) for r in records),
        discovery='XML comments and annotations; keyword candidates only, not legal completeness',
        scanner_sha256=sha(Path(__file__)),started_at=started,wall_seconds=time.monotonic()-timer)
    (OUT/'notice-inventory.json').write_text(json.dumps(value,indent=2)+'\n')
    for r in records:print(r['id'],r['uri'],[(n['first_line'],n['last_line'],n['bytes']) for n in r['notices']],r['unmatched_keyword_offsets'])


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (OUT/'completion.json').exists()
    main()
