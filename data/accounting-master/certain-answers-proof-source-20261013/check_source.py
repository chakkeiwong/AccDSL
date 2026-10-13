"""Integrity of source/version evidence; human proof reading is separately recorded."""
import hashlib,json,subprocess
from pathlib import Path
import fitz
U=Path(__file__).resolve().parent;R=U.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((U/'baseline.json').read_text());checks={}
for group in ['candidate_files','frozen']:
    for p,h in b[group].items():checks[group+':'+p]=sha(R/p)==h
receipts=json.loads((U/'receipts.json').read_text())
checks['bounded_requests']=receipts['distinct_request_count']==len(receipts['requests'])==4
for i,r in enumerate(receipts['requests'],1):
    checks[f'receipt_hash:{i}']=sha(R/r['file'])==r['sha256']
    checks[f'receipt_bytes:{i}']=(R/r['file']).stat().st_size==r['bytes']
    checks[f'receipt_status:{i}']='200' in (R/r['headers']).read_text()
    checks[f'provenance:{i}']=bool(r['provenance'])
p=R/'docs/papers/Certain answers as objects and knowledge Libkin (2016).pdf'
checks['archive_exact']=sha(p)==sha(U/'sources/objects-knowledge.pdf')=='ed3a343607504a2a83c709760d994052e963e56c474e500cab1d81fe9fa6db01'
with fitz.open(p) as d:
    checks['26_pages']=len(d)==26
    first=' '.join(d[0].get_text().split())
    checks['title']='Certain Answers as Objects and Knowledge' in first
    checks['author']='Leonid Libkin' in first
    checks['version']='Preliminary version appeared in KR 2014' in first and 'November 17, 2015' in first
    checks['theorem2_present']='Theorem 2.' in d[16].get_text() and 'representation system' in d[16].get_text()
    checks['corollary3_semantics']='OWA' in d[19].get_text() and 'Corollary 3.' in d[19].get_text()
meta=json.loads((U/'sources/crossref.json').read_text())['message']['items'][0]
checks['doi']='10.1016/j.artint.2015.11.004'==meta['DOI']
checks['exact_title']=meta['title']==['Certain answers as objects and knowledge']
checks['venue']=meta['container-title']==['Artificial Intelligence'] and meta['volume']=='232' and meta['page']=='1-19'
checks['inspected_all_pages']=json.loads((U/'reading-anchors.json').read_text())['all_26_pages_read']
checks['source_proof_review_recorded']=(U/'proof-review.md').is_file()
checks['source_support_recorded']=(U/'source-support-supplement.json').is_file()
index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=R)
checks['100_unrelated_entries_preserved']=len(index.splitlines())==100 and index==(U/'unrelated-index-before.txt').read_bytes()
failed=[k for k,v in checks.items() if not v]
(U/'source-checks.json').write_text(json.dumps({'checks':checks,'passed':sum(checks.values()),'failed':failed,'role':'integrity only; proof reconstruction is the author record'},indent=2)+'\n')
print(json.dumps({'passed':sum(checks.values()),'failed':failed}));raise SystemExit(bool(failed))
