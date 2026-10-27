"""Encode inspected passages; never infer semantic acceptance from hit counts."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda s:' '.join(s.split())
read=lambda p:json.loads(p.read_text())
rel=lambda p:str(p.relative_to(ROOT))
CFG={2022:dict(risk=11,parent=21,proxy=38,exhibits=40,end=43,sig=306,fs=156),
     2023:dict(risk=11,parent=21,proxy=40,exhibits=42,end=45,sig=324,fs=156),
     2024:dict(risk=12,parent=23,proxy=44,exhibits=46,end=49,sig=336,fs=169),
     2025:dict(risk=11,parent=21,proxy=39,exhibits=41,end=44,sig=330,fs=162)}


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (OUT/'annotations.json').exists()
    tick=time.monotonic();now=datetime.now(timezone.utc).isoformat()
    ledger=read(ROOT/'data/accounting-master/accounting-package-ledger-20261011/package-ledger.json')
    quotes=[];assertions=[];dependencies=[];packages=[]

    def quote(y,p,key,start,end=None,include_end=False,mode='columns'):
        if mode=='columns':
            path=OUT/'columns'/f'{y}-p{p}.txt';raw=path.read_text();page_offset=0
        elif mode=='front':
            path=OUT/'reading-order'/f'{y}-front.txt';parts=path.read_text().split('\f')
            raw=parts[p-3];page_offset=sum(len(t)+1 for t in parts[:p-3])
        elif mode=='target':
            path=OUT/'reading-order'/f'{y}-target-p{p}.txt';raw=path.read_text();page_offset=0
        else:
            path=OUT/'reading-order'/f'{y}-signatures.txt';raw=path.read_text();page_offset=0
        s=norm(raw);a=s.index(start)
        assert s.count(start)==1,(y,p,key,'ambiguous start')
        b=s.index(end,a+len(start))+(len(end) if include_end else 0) if end else a+len(start)
        body=s[a:b].strip();b=a+len(body)
        original=ROOT/f'data/accounting-master/jpmorgan-complete-filings-20261011/sources/jpmorgan-{y}-10k.txt'
        original_page=original.read_text().split('\f')[p-1]
        footer=original_page.rstrip().splitlines()[-1]
        assert re.search(r'(?<!\d)'+str(p-2)+r'(?!\d)',footer),(y,p,footer)
        qid=f'{y}-{key}'
        quotes.append(dict(id=qid,year=y,pdf_page=p,printed_page=p-2,printed_page_footer=footer,
            source_text=rel(path),source_text_sha256=sha(path),mode=mode,page_raw_offset=page_offset,
            normalized_start=a,normalized_end=b,quote=body,normalization='whitespace only',
            original_layout_text=rel(original),original_layout_sha256=sha(original)))
        return qid

    def claim(y,key,qids,source_claim,consequence,unknown,modality='issuer_reported'):
        assertions.append(dict(id=f'{y}-{key}',year=y,quotes=qids,modality=modality,
            source_claim=source_claim,local_consequence=consequence,unresolved_query=unknown,
            acceptance='author_annotation; independent/domain acceptance pending'))

    def dep(y,key,qids,target,kind,status):
        dependencies.append(dict(id=f'{y}-{key}',year=y,quotes=qids,target=target,
            relationship=kind,status=status,publication_at=None,historical_byte_admission=False))

    for source in ledger['records']:
        y=source['period_year'];c=CFG[y]
        packages.append(dict(year=y,roles=source['roles'],clock_policy=source['clock_policy'],
            semantic_annotation_recorded_at=now,selected_byte_available_at=None,
            complete_issuer_byte_available_at=None,as_of_admission=False,
            semantic_status='bounded passages annotated; full Item 1/1A and package closure open'))
        opening=quote(y,3,'overview','JPMorgan Chase & Co.','JPMorgan Chase’s principal bank' if y<2024 else 'JPMorganChase’s principal bank')
        entity=quote(y,3,'principal-subsidiaries','JPMorgan Chase’s principal bank' if y<2024 else 'JPMorganChase’s principal bank','The Firm’s website')
        claim(y,'identity',[opening,entity],
            'The registrant is a Delaware financial holding company. It identifies JPMorgan Chase Bank, N.A. and J.P. Morgan Securities LLC as principal bank/non-bank subsidiaries; J.P. Morgan Securities plc and J.P. Morgan SE are subsidiaries of the bank, based in the UK and Germany respectively.',
            'Retain entity and relationship types separately from reporting segments and locations.',
            'This is a partial principal-subsidiary description, not a full legal-entity/control/currency graph.')
        web=quote(y,3,'website-boundary','The Firm’s website',
            'or the Firm’s other filings with the SEC.',True)
        claim(y,'availability',[web],
            'Reports are made available on the issuer website as soon as reasonably practicable after electronic filing or furnishing; website information is expressly not incorporated by reference.',
            'Keep the filing event, retrieval, publication and annotation clocks separate. A website mention is not incorporation.',
            'Neither exact historical publication time nor equality with the historical regulator bytes is established.')
        dep(y,'website',[web],'Issuer website information','express_non_incorporation','not part of this filing by this clause')
        seg=quote(y,3,'segments','Business segments','Competition')
        segclaim=('Four major reportable business segments are CCB, Corporate & Investment Bank, Commercial Banking and AWM, with Corporate also described.' if y<2024 else
            'The second-quarter 2024 reorganization combines former Corporate & Investment Bank and Commercial Banking into Commercial & Investment Bank; three reportable business segments remain, plus Corporate activities.' if y==2024 else
            'The three reportable business segments are CCB, Commercial & Investment Bank and AWM, with remaining activities in Corporate.')
        if y==2023:segclaim+=' The source also reports the May 1, 2023 acquisition of certain First Republic assets and assumption of certain liabilities from the FDIC, with a Note 34 reference.'
        claim(y,'segment-context',[seg],segclaim,
            'Bind segment labels and abbreviations to the year and reorganization basis; CIB is not a time-invariant segment definition.',
            'Restated comparative amounts, allocations and complete segment-note semantics remain to be checked.')
        dep(y,'segment-note',[seg],'MD&A business segment results and Note 32; 2023 also Note 34','internal_cross_reference','body semantics not checked in this unit')
        risk=quote(y,c['risk'],'risk-scope','The following discussion','Summary')
        claim(y,'risk-scope',[risk],
            'The listed risks are not complete; individual risks or combinations could materially and adversely affect the firm.',
            'Retain modality and combinations. No exhaustive event set or numerical probability follows from the list.',
            'Full risk-body annotation, actual events, exposures and probabilities remain open.',modality='possibility_and_scope_qualification')
        stop='Reductions in JPMorgan' if y<2025 else 'JPMorganChase’s liquidity and cost of funding could'
        parent=quote(y,c['parent'],'parent-funding','JPMorgan Chase & Co. is a holding company and',stop)
        claim(y,'parent-funding',[parent],
            'The parent holds the bank and JPMorgan Chase Holdings LLC (IHC). The IHC lends to the parent; substantially all net securities-issuance proceeds must be contributed to the IHC. Bank distributions are restricted, and IHC dividends or credit to the parent are prohibited if certain capital/liquidity thresholds are breached or management/board limits apply.',
            'Group liquidity cannot automatically be assigned to the parent. Model funding source, legal entity, threshold conditions and management limits separately.',
            'Numerical thresholds, balances, contemporaneous headroom, contracts and actual transfers are not supplied by this passage. Preserve “generally” and “substantially all”; do not replace them with universal or 100% rules.',modality='reported_conditional_funding_restriction')
        proxy=quote(y,c['proxy'],'proxy','Information to be provided',f'December 31, {y}.',True,mode='front')
        claim(y,'proxy-incorporation',[proxy],
            f'Information required by Items 10–14 and not otherwise included is incorporated from the definitive proxy for the {y+1} annual meeting; the source says it will be filed within 120 days of year end.',
            'A complete 10-K PDF does not by itself close these incorporated disclosures.',
            'The proxy bytes, actual filing time, applicable sections and amendments are not checked.')
        dep(y,'proxy',[proxy],f'Definitive Proxy Statement for {y+1} annual meeting, Items 10–14 remainder','incorporated_by_reference','unresolved external document')
        fin=quote(y,c['exhibits'],'financial-statement-reference','The Consolidated Financial Statements',f'commencing on page {c["fs"]}.',True)
        claim(y,'item15-financials',[fin],f'Item 15 says the Item 8 statements, notes and auditor report commence on printed page {c["fs"]}.',
            'Resolve the target heading, rather than accepting a page number as evidence of the target.',
            'The 2023 pointer is wrong relative to the target: see the separate reference repair record.' if y==2023 else 'The target heading is located; full financial-statement semantics are outside this annotation.')
        indenture=quote(y,c['exhibits']+1,'indenture','4.4 Indenture','4.5')
        dep(y,'indenture',[indenture],'2016-02-19 indenture, Form S-3 file 333-209682, Exhibit 4(a)(7), filed 2016-02-24','incorporated_by_reference','unresolved external instrument')
        omitted=quote(y,c['exhibits']+1,'omitted-instruments','Other instruments defining','10.1')
        claim(y,'omitted-instruments',[omitted],
            'The issuer states that other long-term debt instruments are omitted under Item 601(b)(4)(iii)(A) and will be furnished to the SEC on request.',
            'File-level completeness does not imply that all debt terms are locally available.',
            'Individual instruments, request responses and their economic terms remain unidentified; operative legal compliance is not adjudicated.')
        dep(y,'other-debt',[omitted],'Other omitted long-term debt instruments','omitted_furnishable_on_request','not enumerated in inspected clause')
        listpage=c['end']-1 if y==2025 else c['end']
        roster=quote(y,listpage,'exhibit21','21 List','22.1')
        future=quote(y,listpage,'exhibit22-1','22.1 Annual Report','22.2')
        foot=quote(y,c['end'],'exhibit-footnotes','(a) This exhibit','(d) Pursuant')
        cert=quote(y,c['end'],'exhibit32','32 Certification','97 ' if y>=2023 else '101.INS')
        xbrl=quote(y,c['end'],'xbrl-packaging','101.INS','(a) This exhibit')
        claim(y,'exhibit-status',[roster,cert,foot,xbrl],
            'Exhibit 21 is marked filed herewith, Exhibit 32 is marked furnished herewith, and footnote (c) disclaims filed status and incorporation for that exhibit. The XBRL instance tags are embedded in an Inline XBRL document and separate taxonomy/linkbase documents are listed.',
            'Keep filed/furnished/incorporated and PDF/Inline-XBRL roles distinct. A PDF listing is not the listed digital file.',
            'Exhibit bodies and exact XBRL component bytes must be located and checked separately; footnote markers are retained without silently repairing extraction typography.')
        dep(y,'exhibit21',[roster,foot],'Exhibit 21 List of subsidiaries','filed_herewith','body not yet inspected in this unit')
        dep(y,'exhibit32',[cert,foot],'Exhibit 32 Section 906 certification','furnished_herewith_non_incorporated','body not yet inspected in this unit')
        dep(y,'xbrl',[xbrl],'Inline XBRL instance, 101 taxonomy/linkbase documents and 104 cover data','listed_digital_components','bytes and semantic equivalence not checked')
        dep(y,'exhibit22-1',[future],'Form 11-K for the plan-year stated verbatim in the source quote','to_be_filed','year/date require verification; source says 2019 for 2022 and 2024 for 2025')
        sig=quote(y,c['sig'],'signature','Signatures','Capacity Date',mode='signatures')
        claim(y,'signature',[sig],
            'The reproduced signature block names James Dimon as chairman/CEO, gives a date, and states that the issuer does not use power of attorney for directors’ signatures.',
            'This is source attestation text; signing time is separate from SEC acceptance and byte availability.',
            'Signatures are not independently authenticated and do not prove accounting accuracy.')

    # Preserve the actual inconsistent navigation and the proposed corrected target.
    i8=quote(2023,38,'item8-range','The Consolidated Financial Statements','appear on pages 163–309.',True,mode='target')
    wrong=quote(2023,158,'wrong-target','Management’s discussion and analysis',mode='target')
    actual=quote(2023,165,'actual-auditor','Report of Independent Registered Public Accounting Firm',mode='target')
    repair=dict(id='2023-item15-reference',source_assertion='2023-item15-financials',
        evidence=['2023-financial-statement-reference',i8,wrong,actual],
        literal_reference_printed_page=156,literal_target_pdf_page=158,
        actual_auditor_printed_page=163,actual_auditor_pdf_page=165,
        verdict='wrong relative to the stated target',disposition='preserve literal source; propose separate navigation correction',
        full_statement_audit=False,e05_accounting_conflict=False,
        remaining_uncertainty='No regulator-byte equivalence or source erratum checked; this is an internal navigation defect in the retained issuer PDF.')

    table_pages={2022:[38,39],2023:[40,41],2024:[44,45],2025:[39,40]}
    dispositions=[]
    for r in read(OUT/'column-extractions.json')['receipts']:
        rejected=r['pdf_page'] in table_pages[r['year']]
        dispositions.append(dict(year=r['year'],pdf_page=r['pdf_page'],text=r['text'],
            status='rejected_for_annotation' if rejected else 'available_for_bounded_passage_selection',
            reason='Full-width tables/prose cross the crop boundary; use intact full-page text.' if rejected else 'Single-column passages selected with exact locators; not all page content annotated.'))
    output=dict(schema_version='accdsl.jpmorgan_bounded_semantics.v1',recorded_at=now,
        packages=packages,quotes=quotes,assertions=assertions,dependencies=dependencies,
        reference_repairs=[repair],layout_dispositions=dispositions,
        paper_or_statistical_evidence=False,full_package_semantics=False,
        author_review_only=True,wall_seconds=time.monotonic()-tick)
    (OUT/'annotations.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(dict(packages=len(packages),quotes=len(quotes),assertions=len(assertions),dependencies=len(dependencies),reference_repairs=1)))


if __name__=='__main__':main()
