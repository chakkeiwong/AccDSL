"""Preserve source-route outcomes and the checked wrong-identifier correction."""
import datetime
import hashlib
import json
import platform
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from bs4 import BeautifulSoup

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + "\n")


def main():
    assert not (OUT / "completion.json").exists()
    started = time.monotonic()
    baseline = json.loads((OUT / "baseline.json").read_text())
    checks=[]

    def ck(name, yes):
        checks.append({"name":name,"passed":bool(yes)})

    for rel,digest in baseline["input_hashes"].items():
        ck("preserved input "+rel,sha(ROOT/rel)==digest)
    recovery=json.loads((ROOT/'data/accounting-master/munich-publication-imprints-20261012/recovery-baseline.json').read_text())
    for rel,digest in recovery['protected_hashes'].items():
        ck('frozen evidence '+rel,sha(ROOT/rel)==digest)
    soup=BeautifulSoup((OUT/'sources/arxiv-abstract.html').read_text(),'html.parser')
    metadata={t['name']:t.get('content') for t in soup.find_all('meta',attrs={'name':True})}
    ck('arxiv identifier',metadata.get('citation_arxiv_id')=='1508.02248')
    ck('unrelated optics title',metadata.get('citation_title')=='Tuning of magnetic optical response in a dielectric nanoparticle by ultrafast photo-injection of dense electron-hole plasma')
    authors=[t['content'] for t in soup.find_all('meta',attrs={'name':'citation_author'})]
    ck('unrelated authors','Makarov, Sergey' in authors and not any('Caiani' in a for a in authors))
    n={'a':'http://www.w3.org/2005/Atom','o':'http://a9.com/-/spec/opensearch/1.1/'}
    search=ET.fromstring((OUT/'sources/arxiv-search.xml').read_bytes())
    ck('title query returns zero',search.findtext('o:totalResults',namespaces=n)=='0')
    author=ET.fromstring((OUT/'sources/arxiv-author.xml').read_bytes())
    entries=[{'id':e.findtext('a:id',namespaces=n),'title':' '.join(e.findtext('a:title',namespaces=n).split())}
             for e in author.findall('a:entry',n)]
    ck('five author-query results',len(entries)==5)
    rss=ET.fromstring((OUT/'sources/title-discovery.xml').read_bytes())
    excluded=[{'title':e.findtext('title'),'url':e.findtext('link'),'disposition':'unrelated title/topic; no source admission'}
              for e in rss.findall('.//item')]
    ck('ten excluded RSS results',len(excluded)==10)
    attempts=[]
    for p in sorted((OUT/'sources').glob('*-receipt.json')):
        d=json.loads(p.read_text());stem=p.name.removesuffix('-receipt.json')
        attempts.append({'attempt':stem,'permission_context':'sandbox' if 'sandbox' in stem else 'trusted',
            'url':d['url'],'effective_url':d['url_effective'],'http_status':d['http_code'],'exit_code':d['exitcode'],
            'wall_seconds':d['time_total'],'receipt':str(p.relative_to(ROOT))})
    ck('six distinct requested resources',len({x['url'] for x in attempts})==6)
    ck('twelve attempts retained',len(attempts)==12)
    statuses={a['attempt']:(a['http_status'],a['exit_code']) for a in attempts}
    ck('trusted source failures',statuses['handle-trusted']==statuses['ssrn-trusted']==(403,22))
    ck('five DNS failures',sum(a['exit_code']==6 for a in attempts)==5)
    controls={}
    for row in baseline['controls']:
        ck('prior control '+row['live'],sha(ROOT/row['snapshot'])==row['sha256'])
        p=ROOT/row['live'];t=p.read_text()
        ck('live control '+row['live'],all(s in t for s in ['Version 2.51','not_ready','caiani-source-recovery-20261013/result.md','accounting-intragroup-fx-20261013.md']))
        controls[row['live']]=sha(p)
    failed=[c['name'] for c in checks if not c['passed']]
    if failed:
        print(json.dumps({'failed':failed}));raise SystemExit(1)
    save('source-status.json',{'source':'caiani2016','status':'SOURCE_BLOCKED','technical_claims_allowed':[],
        'wrong_identifier':{'id':metadata['citation_arxiv_id'],'title':metadata['citation_title'],'authors':authors,
             'source':'sources/arxiv-abstract.html','verdict':'wrong relative to the intended Caiani source'},
        'arxiv_author_results':[dict(e,disposition='unrelated title/topic; no source admission') for e in entries],
        'rss_dispositions':excluded,'backward_reading':'not possible without full text',
        'forward_screening':'previous six dispositions preserved; no new citing-paper inquiry',
        'citation_venue_metadata':'historical metadata only; not refreshed',
        'correction_and_code_status':'not checked for intended paper',
        'omission_risk':'consequential stock-flow antecedent remains technically uninspected'})
    plan='docs/plans/accounting-caiani-source-recovery-20261013.md'
    paths=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]+[ROOT/plan]
    manifest={'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'git_commit':baseline['git_commit'],
        'plan':plan,'result':str((OUT/'result.md').relative_to(ROOT)),'attempts':attempts,
        'commands':'acquisition-commands.json plus exact SSRN tool receipts',
        'environment':{'python':platform.python_version(),'cpu_gpu':'CPU-only; no framework or GPU calls','seeds':'N/A deterministic inspection'},
        'data_version':'retained Caiani discovery/provenance records; hashes in baseline.json',
        'wall_seconds':{'curl_total':sum(a['wall_seconds'] for a in attempts),'closeout':time.monotonic()-started,'interactive_work':'not timed'},
        'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in paths},'controls_at_closeout':controls,
        'interpretation':'record fidelity and preservation pass; full-text acquisition failed','readiness':'not_ready'}
    save('run-manifest.json',manifest);digest=sha(OUT/'run-manifest.json')
    save('checks.json',{'checks':checks,'passed':len(checks),'failed':[],'manifest_sha256':digest})
    save('completion.json',{'status':'closed_source_blocked_with_identity_correction','checks':len(checks),'full_text_acquired':False,'manifest_sha256':digest,'readiness':'not_ready'})
    print(json.dumps({'checks':len(checks),'failed':[],'status':'closed_source_blocked_with_identity_correction'}))


if __name__ == '__main__':
    main()
