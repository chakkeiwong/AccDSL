"""Verify source transcription, complete page coverage and unpromoted unknowns."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import time

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
norm=lambda s:' '.join(s.split())
rel=lambda p:str(p.relative_to(ROOT))


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (OUT/'checks.json').exists()
    tick=time.monotonic();checks=[];inputs={}
    def ck(n,x):checks.append(dict(id=n,passed=bool(x)))
    def bind(p):inputs[rel(p)]=sha(p);return p
    b=read(bind(OUT/'baseline.json'));a=read(bind(OUT/'exhibits.json'))
    prior=ROOT/b['prior_manifest'];p=read(bind(prior));done=read(bind(prior.with_name('completion.json')))
    ck('prior identity',sha(prior)==b['prior_manifest_sha256']==done['manifest_sha256'])
    reloc={x['historical_path']:x['preserved_path'] for x in b['pointer_relocations']}
    inherited={reloc.get(k,k):v for k,v in p['artifact_hashes'].items()}
    ck('2131 inherited references',len(inherited)==2131 and all((ROOT/k).is_file() and sha(ROOT/k)==v for k,v in inherited.items()))
    ck('manuscript unchanged',sha(ROOT/b['pdf']['path'])==b['pdf']['sha256'])
    receipts=read(bind(OUT/'extractions.json'))['receipts']
    ck('eight distinct exhibit pages',len(receipts)==8 and len({(r['year'],r['exhibit']) for r in receipts})==8)
    for r in receipts:
        ck(f'{r["year"]} {r["exhibit"]} extraction identities',sha(bind(ROOT/r['source_pdf']))==r['source_sha256'] and all(sha(bind(ROOT/x['path']))==x['sha256'] for x in r['outputs']) and all(x['exit_code']==0 for x in r['commands']))
    spans={s['id']:s for s in a['spans']}
    ck('unique spans',len(spans)==len(a['spans']))
    for s in spans.values():
        file=bind(ROOT/s['source_text']);raw=file.read_text()
        ck(s['id']+' exact bytes',sha(file)==s['source_text_sha256'] and raw[s['raw_start']:s['raw_end']]==s['raw_quote'])
    # Manually transcribed from the eight rendered tables, independent of indentation parser.
    expected=[('JPMorgan Chase Bank, National Association','United States'),('Paymentech, LLC','United States'),
        ('J.P. Morgan International Finance Limited','United States'),('JPMorgan Securities Japan Co., Ltd.','Japan'),
        ('J.P. Morgan Capital Holdings Limited','United Kingdom'),('J.P. Morgan Securities plc','United Kingdom'),
        ('J.P. Morgan SE','Germany'),('JPMorgan Chase Holdings LLC','United States'),
        ('J.P. Morgan Services India Private Limited','India'),('JPMorgan Asset Management Holdings Inc.','United States'),
        ('JPMorgan Distribution Services, Inc.','United States'),('JPMorgan Asset Management International Limited','United Kingdom'),
        ('JPMorgan Asset Management (UK) Limited','United Kingdom'),('JPMorgan Asset Management Holdings (Luxembourg) S.à r.l.','Luxembourg'),
        ('JPMorgan Asset Management (Europe) S.à r.l.','Luxembourg'),('J.P. Morgan Investment Management Inc.','United States'),
        ('J.P. Morgan Broker-Dealer Holdings Inc.','United States'),('J.P. Morgan Securities LLC','United States')]
    ledger=read(bind(ROOT/'data/accounting-master/accounting-package-ledger-20261011/package-ledger.json'))
    for r in a['records']:
        y=r['year'];rows=r['entities'];g=r['guarantee']
        exp=[(name.replace(' plc',' PLC') if y<2024 else name,country) for name,country in expected]
        ck(f'{y} all 18 named entities and jurisdictions',[(x['name_as_printed'],x['organized_under_laws_of']) for x in rows]==exp)
        scope=norm(spans[r['scope_span']]['raw_quote'])
        ck(f'{y} scope qualifiers and date',all(t in scope for t in [f'December 31, {y}','parent company','Excluded from the list','in the aggregate','resolution planning']) and r['roster_as_of']==f'{y}-12-31' and not r['roster_scope']['complete_legal_entity_roster'])
        ck(f'{y} ownership not invented',all(not x['direct_ownership_confirmed'] and all(x[k] is None for k in ['ownership_fraction','consolidation_basis','functional_currency','tax_residence']) for x in rows))
        ck(f'{y} visually checked nesting',rows[5]['display_parent']=='J.P. Morgan Capital Holdings Limited' and rows[-1]['display_parent']=='J.P. Morgan Broker-Dealer Holdings Inc.' and rows[0]['display_parent'] is None and rows[7]['display_parent'] is None)
        cell=norm(' '.join(spans[x]['raw_quote'] for x in g['securities_cell_spans']))
        ck(f'{y} securities and guarantor cells',cell==g['securities_cell_whitespace_normalized'] and spans[g['guarantor_span']]['raw_quote']==g['guarantor']=='JPMorgan Chase & Co.' and cell.startswith(g['issuer']) and 'fully and unconditionally guaranteed' in cell)
        early=y<2024
        ck(f'{y} registration and modality',all(n in cell for n in g['registration_numbers_reported']) and ('April 8, 2020' if early else 'April 13, 2023') in cell and ('currently offered and sold' if early else 'may issue, from time to time, debt securities') in cell and (('warrants' in cell)==(not early)))
        ck(f'{y} no amount or historical admission',all(g[k] is None for k in ['exhibit_economic_as_of','outstanding_principal','guarantee_fair_value','guarantee_recognition','issuer_ownership_parent']) and not g['registration_independently_verified'] and not r['as_of_admission'] and r['selected_byte_available_at'] is None)
        ck(f'{y} issuer absent from partial roster',not r['financial_company_in_roster'] and not any(x['name_as_printed']==g['issuer'] for x in rows) and g['issuer']!='JPMorgan Chase Holdings LLC')
        old=next(x for x in ledger['records'] if x['period_year']==y)
        ck(f'{y} source roles and clocks unchanged',r['source_roles']==old['roles'] and r['clocks']==old['clock_policy'])
    ck('eight whole page spans',sum(s['id'].endswith('full-page') for s in spans.values())==8)
    ck('all findings trace to spans',all(all(x in spans for x in f['source_spans']) for f in a['findings']))
    result=dict(recorded_at=datetime.now(timezone.utc).isoformat(),passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),checks=checks,inputs=inputs,checker_sha256=sha(Path(__file__)),builder_sha256=sha(OUT/'build_exhibits.py'),wall_seconds=time.monotonic()-tick,evidence_class='documentary source and transcription checks; no independent semantic acceptance')
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=result['passed'],failed=[c['id'] for c in checks if not c['passed']])))
    assert result['failed']==0


if __name__=='__main__':main()
