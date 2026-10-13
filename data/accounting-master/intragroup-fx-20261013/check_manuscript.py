"""Verify exact bounded changes, prior content and final rendered evidence."""
import collections
import json
import re
import time

import fitz

from build_candidate import BASE,CAND,OUT,ROOT,expected_text,save,sha


def features(folder,paths):
    t='\n'.join((folder/p).read_text() for p in paths if p.endswith('.tex'))
    citations=collections.Counter()
    for b in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',t):
        citations.update(k.strip() for k in b.split(','))
    displays=collections.Counter(re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation|align|gather|multline)\*?\}.*?\\end\{(?:equation|align|gather|multline)\*?\}',t,re.S))
    return citations,displays


def main():
    assert not (OUT/'completion.json').exists()
    start=time.monotonic();checks=[]

    def ck(name,p):
        checks.append({'name':name,'passed':bool(p)})

    candidate=json.loads((OUT/'candidate.json').read_text());source=json.loads((OUT/'source-checks.json').read_text())
    ck('49 source and arithmetic checks',source['passed']==49 and not source['failed'])
    ck('protected prior PDF',sha(BASE/'accounting-product-proposal.pdf')==candidate['baseline_pdf_sha256'])
    ck('current added passage identity',sha(OUT/'fx-addition.tex')==candidate['new_passage_sha256'])
    for rel,digest in candidate['source_hashes'].items():
        ck('protected source '+rel,sha(BASE/rel)==digest)
        ck('exact intended transformation '+rel,(CAND/rel).read_text()==expected_text(rel))
    oldc,oldd=features(BASE,candidate['source_hashes']);newc,newd=features(CAND,candidate['source_hashes'])
    ck('all old citation occurrences',not(oldc-newc));ck('all old display blocks',not(oldd-newd))
    ck('bibliography unchanged',sha(BASE/'references.bib')==sha(CAND/'references.bib'))
    keys=set(re.findall(r'@\w+\s*\{\s*([^,\s]+)',(CAND/'references.bib').read_text()))
    ck('all cited references exist',set(newc)<=keys)
    log=(CAND/'accounting-product-proposal.log').read_text()
    ck('clean final build',not re.search(r'Warning|Overfull|Underfull|undefined|^!',log,re.M))
    ck('build exit zero',json.loads((OUT/'build-run.json').read_text())['exit_code']==0)
    renders=json.loads((OUT/'candidate-renders.json').read_text());review=json.loads((OUT/'rendered-review.json').read_text())
    pdf=CAND/'accounting-product-proposal.pdf'
    ck('PDF identity',sha(pdf)==renders['pdf_sha256']==review['pdf_sha256'])
    with fitz.open(pdf) as d:
        t=' '.join(' '.join(p.get_text().split()) for p in d)
        ck('195 pages',len(d)==renders['pdf_pages']==195)
        ck('version and section present','Version 2.52' in t and 'Eliminating the loan, retaining the currency exposure' in t)
        ck('worked amounts present',all(s in t for s in ['settlement is neither planned nor likely','Consolidated OCI','USD1.30','opening 200','closing 212']))
    ck('six final pages reviewed',{x['pdf_page'] for x in review['pages'] if x['inspected']}=={1,5,118,119,120,121})
    for row in renders['pages']:
        ck('final render '+str(row['pdf_page']),sha(ROOT/row['path'])==row['sha256'])
    recovery=json.loads((ROOT/'data/accounting-master/munich-publication-imprints-20261012/recovery-baseline.json').read_text())
    for rel,digest in recovery['protected_hashes'].items():ck('frozen evidence '+rel,sha(ROOT/rel)==digest)
    failed=[x['name'] for x in checks if not x['passed']]
    save('manuscript-checks.json',{'checks':checks,'passed':len(checks)-len(failed),'failed':failed,
        'source_files':len(candidate['source_hashes']),'baseline_citation_occurrences':sum(oldc.values()),
        'candidate_citation_occurrences':sum(newc.values()),'baseline_unique_citation_keys':len(oldc),'candidate_unique_citation_keys':len(newc),
        'baseline_display_blocks':sum(oldd.values()),'candidate_display_blocks':sum(newd.values()),
        'pdf_sha256':sha(pdf),'wall_seconds':time.monotonic()-start})
    print(json.dumps({'passed':len(checks)-len(failed),'failed':failed}));raise SystemExit(bool(failed))


if __name__=='__main__':
    main()
