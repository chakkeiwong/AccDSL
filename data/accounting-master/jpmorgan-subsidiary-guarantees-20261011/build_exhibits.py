"""Transcribe inspected full exhibits, separating display nesting from ownership."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import time

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda s:' '.join(s.split())
rel=lambda p:str(p.relative_to(ROOT))
read=lambda p:json.loads(p.read_text())


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (OUT/'exhibits.json').exists()
    started,tick=datetime.now(timezone.utc).isoformat(),time.monotonic()
    receipts=read(OUT/'extractions.json')['receipts'];records=[];spans=[]
    role_ledger=read(ROOT/'data/accounting-master/accounting-package-ledger-20261011/package-ledger.json')
    def span(receipt,label,a,b,role='layout'):
        src=next(x for x in receipt['outputs'] if x['role']==role)
        raw=(ROOT/src['path']).read_text();assert 0<=a<b<=len(raw)
        record=dict(id=f'{receipt["year"]}-ex{receipt["exhibit"]}-{label}',
            source_text=src['path'],source_text_sha256=src['sha256'],pdf_page=receipt['pdf_page'],
            source_pdf=receipt['source_pdf'],source_pdf_sha256=receipt['source_sha256'],
            raw_start=a,raw_end=b,raw_quote=raw[a:b])
        spans.append(record);return record['id']
    for y in range(2022,2026):
        r=next(x for x in receipts if x['year']==y and x['exhibit']=='21')
        path=ROOT/next(x['path'] for x in r['outputs'] if x['role']=='layout');raw=path.read_text()
        full=span(r,'full-page',0,len(raw))
        a=raw.index('While there are');b=raw.index(f'\nDecember 31, {y}',a)
        scope=span(r,'scope',a,b)
        row_pattern=re.compile(r'^( *)(\S.*?) {2,}(United States|United Kingdom|Japan|Germany|India|Luxembourg)\s*$',re.M)
        rows=[];stack=[]
        for m in row_pattern.finditer(raw,b):
            indent=len(m[1]);name=m[2];country=m[3]
            while stack and stack[-1]['indent']>=indent:stack.pop()
            parent=stack[-1]['name'] if stack else None
            rowid=span(r,f'row{len(rows)+1}',m.start(),m.end())
            rows.append(dict(row=len(rows)+1,name_as_printed=name,organized_under_laws_of=country,
                source_span=rowid,indent_spaces=indent,display_parent=parent,
                display_depth=len(stack),direct_ownership_confirmed=False,ownership_fraction=None,
                consolidation_basis=None,functional_currency=None,tax_residence=None))
            stack.append(dict(indent=indent,name=name))
        assert len(rows)==18,(y,len(rows))
        g=next(x for x in receipts if x['year']==y and x['exhibit']=='22.2')
        gpath=ROOT/next(x['path'] for x in g['outputs'] if x['role']=='layout');body=gpath.read_text()
        full_guarantee=span(g,'full-page',0,len(body))
        a=body.index('JPMorgan Chase Financial Company LLC')
        other=body.index('JPMorgan Chase & Co.',a);nl=body.index('\n',other)
        # Retain exact pieces of the Securities cell around the intervening Guarantor cell.
        pieces=[span(g,'securities-first-line',a,other),span(g,'securities-continuation',nl+1,body.index('\f'))]
        guarantor=span(g,'guarantor-cell',other,other+len('JPMorgan Chase & Co.'))
        text=norm(' '.join(next(s['raw_quote'] for s in spans if s['id']==q) for q in pieces))
        current=y<2024
        guarantee=dict(full_page_span=full_guarantee,securities_cell_spans=pieces,
            securities_cell_whitespace_normalized=text,guarantor_span=guarantor,
            issuer='JPMorgan Chase Financial Company LLC',guarantor='JPMorgan Chase & Co.',
            indenture_date_reported='2016-02-19',series='Global Medium-Term Notes, Series A',
            reported_guarantee='fully and unconditionally guaranteed',
            registration_numbers_reported=['333-236659','333-236659-01'] if current else ['333-270004','333-270004-01'],
            registration_effective_date_reported='2020-04-08' if current else '2023-04-13',
            registration_independently_verified=False,
            modality='issues; currently offered and sold' if current else 'issued; may issue debt securities including Series A Notes and warrants',
            separately_reported_future_warrants=not current,
            exhibit_economic_as_of=None,temporal_scope='Undated exhibit attached to this fiscal-year filing; past/current/possible-future wording retained.',
            outstanding_principal=None,guarantee_fair_value=None,guarantee_recognition=None,
            issuer_ownership_parent=None)
        package=next(p for p in role_ledger['records'] if p['period_year']==y)
        records.append(dict(year=y,source_roles=package['roles'],clocks=package['clock_policy'],
            roster_as_of=f'{y}-12-31',full_roster_page_span=full,scope_span=scope,entities=rows,
            roster_scope=dict(significant_entities=True,parents_of_significant_entities=True,
                selected_resolution_material_entities=True,aggregate_nonsignificant_exclusion=True,
                complete_legal_entity_roster=False),guarantee=guarantee,
            financial_company_in_roster=any(x['name_as_printed']==guarantee['issuer'] for x in rows),
            selected_byte_available_at=None,as_of_admission=False))
    findings=[
        dict(id='partial-roster',source_spans=[f'{y}-ex21-scope' for y in range(2022,2026)],
            finding='The list expressly excludes an aggregate category of non-significant subsidiaries and adds certain parents and resolution-planning entities. It is not a complete group roster.',
            consequence='A roster omission is not proof of non-existence, disposal or absence of an exposure.'),
        dict(id='guaranteed-issuer-outside-roster',source_spans=[f'{y}-ex22.2-full-page' for y in range(2022,2026)],
            finding='The guaranteed securities issuer is absent from each of the 18-row Exhibit 21 lists.',
            consequence='Represent the guaranteed issuer as a distinct known entity with unknown ownership placement; do not merge Financial Company LLC with Holdings LLC.'),
        dict(id='dated-guarantee-scope',source_spans=[f'{y}-ex22.2-full-page' for y in range(2022,2026)],
            finding='2022/2023 describe Series A Notes under the cited 2020-effective registration. 2024/2025 add possible debt securities and warrants under a cited 2023-effective registration.',
            consequence='Keep both dated source descriptions. Do not infer issuance of warrants, retirement of old notes, or a same-context conflict.'),
        dict(id='ownership-and-cash',source_spans=[f'{y}-ex21-full-page' for y in range(2022,2026)],
            finding='The table supplies display nesting and organization jurisdictions, not ownership percentages or free-transfer rights.',
            consequence='Retain the preceding parent/IHC funding restrictions; neither nesting nor a guarantee supplies distributable parent cash.')]
    data=dict(schema_version='accdsl.subsidiary_guarantee_exhibits.v1',recorded_at=started,records=records,
        spans=spans,findings=findings,prior_semantics='data/accounting-master/accounting-package-semantic-annotation-20261011/annotations.json',
        semantic_scope='All eight Exhibit 21/22.2 page bodies read at author level; full package remains open',
        human_acceptance='pending',domain_acceptance='pending',independent_acceptance='pending',
        dependencies=[dict(target='2016-02-19 indenture and any amendments',status='original operative instrument not inspected'),
            dict(target='Form S-3 333-236659 / 333-236659-01, reported effective 2020-04-08',status='issuer citation only'),
            dict(target='Form S-3 333-270004 / 333-270004-01, reported effective 2023-04-13',status='issuer citation only'),
            dict(target='Outstanding instrument balances, terms and accounting treatment',status='not supplied by the two exhibits'),
            dict(target='Financial Company LLC ownership placement and parent/IHC transfer thresholds',status='not supplied by the two exhibits')],
        wall_seconds=time.monotonic()-tick)
    (OUT/'exhibits.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(dict(exhibits=8,dated_entity_rows=sum(len(r['entities']) for r in records),spans=len(spans),guarantee_records=4)))


if __name__=='__main__':main()
