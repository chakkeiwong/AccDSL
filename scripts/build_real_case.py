#!/usr/bin/env python3
"""Inventory the acquired Apple package; retain unresolved semantic obligations."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from bs4 import BeautifulSoup, NavigableString

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/design/cases/apple'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    sources=[('annual-2024.pdf','/tmp/accdsl-apple-2024.pdf','https://www.annualreports.com/HostedData/AnnualReportArchive/a/NASDAQ_AAPL_2024.pdf'),
             ('interim-2025q1.html','/tmp/accdsl-apple-q1.html','https://www.sec.gov/Archives/edgar/data/320193/000032019325000008/aapl-20241228.htm')]
    documents=[]
    for name,temp,url in sources:
        target=OUT/name
        if not target.exists():shutil.copyfile(temp,target)
        documents.append(dict(id=name,url=url,local_path=str(target.relative_to(ROOT)),sha256=digest(target),access_date='2026-10-02',availability_precision='filing day; exact EDGAR acceptance time not established here'))
    subprocess.run(['pdftotext','-layout',str(OUT/'annual-2024.pdf'),str(OUT/'annual-2024.txt')],check=True)
    annual=(OUT/'annual-2024.txt').read_text();pages=annual.split('\f');pages=pages[:-1] if not pages[-1].strip() else pages
    soup=BeautifulSoup((OUT/'interim-2025q1.html').read_text(),'html.parser')
    for el in soup(['script','style']):el.decompose()
    interim=soup.get_text('\n',strip=True);(OUT/'interim-2025q1.txt').write_text(interim)
    # Page accounting is distinct from note inventory and structured observations.
    page_units=[]
    for i,p in enumerate(pages,1):
        footer=re.search(r'Apple Inc\. \| 2024 Form 10-K \| (\d+)',p)
        printed=int(footer.group(1)) if footer else None
        disposition='financial_disclosure_retained' if printed and 28<=printed<=50 else 'context_or_exhibit_retained'
        page_units.append(dict(id='annual.page.'+str(i),pdf_page=i,printed_page=printed,text_sha256=hashlib.sha256(p.encode()).hexdigest(),disposition=disposition,semantic_status='partially_structured' if printed in [31,38,43,44] else 'not_fully_formalised'))
    obligations={
        'Summary of Significant Accounting Policies':'Calendar, consolidation and FIFO policy recorded; complete policy-to-rule conversion pending.',
        'Basis of Presentation and Preparation':'Interim/annual linkage retained; all preparation qualifications require review before broader simulation.',
        'Revenue':'Product/service and segment classifications overlap; performance obligations, deferrals, returns and transaction-price models pending.',
        'Earnings Per Share':'Dated basic/diluted share denominators retained; dilution calculation unsupported in this marginal stress.',
        'Financial Instruments':'Interest-rate notional and hedge link structured; instrument schedules, valuation and OCI recycling remain unresolved.',
        'Property, Plant and Equipment':'Gross/net bridge retained; asset-cohort ages and future depreciation not reconstructed.',
        'Consolidated Financial Statement Details':'Detailed balances retained; component movement models and recognition rules pending.',
        'Condensed Consolidated Financial Statement Details':'Detailed balances retained; component movement models pending.',
        'Income Taxes':'Current/deferred/state-aid effects retained; no tax effect assumed only in the explicitly conditional marginal stress.',
        'Leases':'Maturities and policy retained; discounting, modifications and rent forecasts unmodelled.',
        'Debt':'Principal/carrying/fair value and dates separated; rate/reset/hedge state incompletely disclosed.',
        'Shareholders’ Equity':'Repurchase authorisation is permission, not an obligatory future cash outflow; quantities and reserves retained.',
        'Share-Based Compensation':'Vesting/award terms and cash-tax settlements retained; compensation/dilution simulation unmodelled.',
        'Commitments, Contingencies and Supply Concentrations':'Qualitative/conditional obligations retained; no unsupported numeric haircut or probability.',
        'Segment Information and Geographic Data':'Overlapping product/geography aggregation retained; no cross-axis summation.'}
    notes=[]
    for doc,text in [('annual',annual),('interim',interim)]:
        # Headings at line start distinguish actual notes from in-text references.
        pattern=r'(?m)^[\f \t]*Note (\d+)\s*[–-]\s*([^\n]+)'
        matches=list(re.finditer(pattern,text))
        for j,m in enumerate(matches):
            title=m.group(2).strip(); start=m.start();end=matches[j+1].start() if j+1<len(matches) else len(text)
            # Last note ends before the auditor/MD&A rather than incorporating the rest of the filing.
            tail=text[start:end]
            for marker in ['Report of Independent Registered','Item 2.','Item 2\n']:
                off=tail.find(marker)
                if off>0:end=min(end,start+off)
            notes.append(dict(id=doc+'.note.'+m.group(1),number=int(m.group(1)),title=title,
                source=doc,start_character=start,end_character=end,
                pdf_page=text[:start].count('\f')+1 if doc=='annual' else None,
                disposition='retained_with_specific_obligation',
                modelling_obligation=obligations.get(title,'Source text retained; detailed interpretation and operation mapping pending.'),
                internal_note_targets=sorted(set(re.findall(r'Note\s+(\d+)',text[start:end])))))
    # Every nonempty text leaf survives. This is segmentation evidence, not visual/OCR accuracy.
    leaves=[x for x in soup.descendants if isinstance(x,NavigableString) and x.strip()]
    leaf_units=[dict(id='interim.text.'+str(i),text=str(x),parent_tag=x.parent.name,
                     html_id=x.parent.get('id'),disposition='structured_fact_candidate' if x.parent.name=='ix:nonfraction' else 'retained_unformalised') for i,x in enumerate(leaves)]
    (OUT/'interim-source-units.json').write_text(json.dumps(leaf_units,ensure_ascii=False,indent=2)+'\n')
    tagged=[]
    keep={'us-gaap:Assets','us-gaap:Liabilities','us-gaap:StockholdersEquity','us-gaap:CashAndCashEquivalentsAtCarryingValue','us-gaap:LongTermDebtCurrent','us-gaap:LongTermDebtNoncurrent','us-gaap:CommercialPaper'}
    for fact in soup.find_all('ix:nonfraction'):
        if fact.get('name') in keep:
            cid=fact.get('contextref');ctx=soup.find(id=cid)
            tagged.append(dict(id=fact.get('id'),concept=fact.get('name'),literal=fact.get_text(),context_ref=cid,context_xml=str(ctx),unit_ref=fact.get('unitref'),decimals=fact.get('decimals'),scale=fact.get('scale'),sign=fact.get('sign'),format=fact.get('format'),status='tagged_reading_preserved; compared with rendered financial-statement text'))
    statements=[
        dict(date='2023-09-30',cash='29965',assets='352583',liabilities='290437',equity='62146',term_debt='105103',source='annual printed page 31'),
        dict(date='2024-09-28',cash='29943',assets='364980',liabilities='308030',equity='56950',term_debt='96662',source='annual printed page 31; Note 9 printed page 43'),
        dict(date='2024-12-28',cash='30299',assets='344085',liabilities='277327',equity='66758',term_debt='94804',source='interim printed page 3; Note 6 printed page 10')]
    result=dict(documents=documents,scope='All acquired bytes/pages/text leaves retained; selected numerical semantics only; external incorporation closure incomplete',
        page_units=page_units,notes=notes,
        interim_text_unit_count=len(leaf_units),interim_source_units='interim-source-units.json',tagged_selected_facts=tagged,
        annual_items=[dict(item=i,disposition='retained; see source page and note inventory') for i in ['1','1A','1B','1C','2','3','4','5','6','7','7A','8','9','9A','9B','9C','10','11','12','13','14','15','16']],
        interim_items=['I.1 financial statements','I.2 MD&A','I.3 market risk','I.4 controls','II.1 legal','II.1A risks','II.2 equity sales/repurchases','II.3 defaults','II.4 mine safety','II.5 other','II.6 exhibits'],
        cross_reference_obligations=[
            dict(source='annual Note 9',target='annual Note 4',relation='economic financing/hedge relationship; reviewer-created link supported by both notes',status='resolved_in_package'),
            dict(source='annual Note 2',target='annual Note 13',relation='literal disaggregated revenue/segment reference',status='resolved_in_package'),
            dict(source='interim Note 1',target='annual Note 1',relation='read interim with annual statements',status='resolved_in_package'),
            dict(source='annual Part III',target='2025 proxy statement',relation='incorporated by reference',status='not_acquired; blocks complete external-reference closure'),
            dict(source='annual exhibit index',target='incorporated prior-filed agreements/exhibits',relation='incorporated documents',status='retained index; external contracts not all acquired')],
        statements=statements,units='USD millions; shares separately typed; rounded presentations retain source precision',
        debt_measurements=dict(principal='97341',discount_cost_adjustment='-321',hedge_carrying_adjustment='-358',carrying='96662',fair_value_display_billions='88.4',interest_rate_contract_notional='14575',source='annual Note 9 pages 43–44 and Note 4 page 38'),
        marginal_stress=dict(start='2024-12-29',horizon_weeks=13,rate_increment='0.02',exposure_assumption='14575',year_fraction='13/52',tax_effect='0',all_other_movements='frozen conditional baseline; not a whole-company forecast',
            expected=dict(interest='72.875',cash='30226.125',assets='344012.125',liabilities='277327',equity='66685.125',profit='-72.875',operating_cash_flow='-72.875')))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    assert len([n for n in notes if n['source']=='annual'])==13
    assert len([n for n in notes if n['source']=='interim'])==10
    print(json.dumps(dict(annual_pages=len(pages),notes=len(notes),interim_text_units=len(leaves),selected_tagged_facts=len(tagged))))

if __name__=='__main__':main()
