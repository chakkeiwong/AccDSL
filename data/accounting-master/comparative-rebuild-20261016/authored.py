"""Freeze synthetic editions and independent comparative report targets."""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PREV=ROOT/'data/accounting-master/p17-completion-20261014/P17-04/error-estimate'


def write(path,value):
    assert not path.exists()
    path.write_text(json.dumps(value,indent=2)+'\n')


def main():
    fixture=json.loads((PREV/'fixture.json').read_text())
    context=dict(entity=fixture['entity'],book='separate',currency='CU',unit='currency units',
                 rule='EU2023/1803-original-comparative-PPE',profile='PPE-life-error/1')
    docs=[]
    for year in [2023,2024]:
        when=fixture['authorization'][str(year)]
        docs.append(dict(id='original-'+str(year),current_year=year,kind='original',context=context,
            authorized=when,published=when,ingested=when,years=[year],opening_year=None,
            source_kind='authored_synthetic_edition'))
    docs.append(dict(id='restated-2025',current_year=2025,kind='restated',context=context,
        authorized='2026-03-31',published='2026-04-02',ingested='2026-04-03',years=[2024,2025],
        opening_year=2024,source_kind='authored_synthetic_edition'))
    catalog=dict(context=context,discovery=fixture['discovery'],correction_accepted='2025-04-02',
                 editions=docs)
    write(OUT/'synthetic-editions.json',catalog)
    # Constant targets are independent of the new annual reconstruction.
    columns=fixture['columns']
    rows=dict(original_2023=['10','110','100','5/2','40','15/2','5/2','30','130','15/2','230'],
        original_2024=['10','100','80','5','40','15/2','5/2','30','345/2','15/2','260'],
        restated_2023=['20','100','100','0','30','15/2','0','45/2','130','15/2','445/2'],
        restated_2024=['20','80','80','0','30','15/2','0','45/2','345/2','15/2','245'],
        restated_2025=['20','60','60','0','30','15/2','0','45/2','215','15/2','535/2'])
    findings=dict(authority_profile_admitted=True,original_information_reliable=True,
        information_available_at_authorization=True,reasonably_obtainable=True,
        original_misapplication=True,material_error=True,fully_practicable=True,
        no_hindsight=True,tax_facts_admitted=True,material_earliest_opening_effect=True,
        public_shares=False,public_filing=False,voluntary_eps=False)
    base=dict(wire='ComparativeRestatement/1',operation='report',context=context,
        selector=dict(mode='latest_available',year=2024,edition=None),
        public_cutoff='2026-04-03',system_cutoff='2026-04-03',findings=findings)
    cases=[]
    for id,mode,year,edition,pub,sys,wanted in [
        ('before-discovery','latest_available',2024,None,'2025-03-31','2025-03-31','original-2024'),
        ('after-discovery-before-publication','latest_available',2024,None,'2025-12-31','2026-04-03','original-2024'),
        ('public-not-ingested','latest_available',2024,None,'2026-04-02','2026-04-02','original-2024'),
        ('public-cutoff-holds','latest_available',2024,None,'2026-04-01','2026-04-03','original-2024'),
        ('current-restated','latest_available',2024,None,'2026-04-02','2026-04-03','restated-2025'),
        ('original-still-retrievable','edition',2024,'original-2024','2026-04-03','2026-04-03','original-2024'),
        ('current-year','latest_available',2025,None,'2026-04-03','2026-04-03','restated-2025'),
        ('earlier-original','edition',2023,'original-2023','2026-04-03','2026-04-03','original-2023')]:
        req=json.loads(json.dumps(base));req.update(selector=dict(mode=mode,year=year,edition=edition),public_cutoff=pub,system_cutoff=sys)
        cases.append(dict(id=id,request=req,edition=wanted))
    targets=dict(rows={k:dict(zip(columns,v)) for k,v in rows.items()},
        earliest_opening=dict(date='2024-01-01',cash='130',ppe='100',current_payable='15/2',dtl='0',equity='445/2'),
        opening_correction=dict(ppe='-10',dtl='-5/2',equity='-15/2',cash='0',current_payable='0'),
        comparative_correction=dict(depreciation='10',ppe='-20',tax_base='0',dtl='-5',pretax_profit='-10',
            current_tax='0',deferred_expense='-5/2',net_profit='-15/2',cash='0',current_payable='0',equity='-15'),
        current_opening_correction=dict(ppe='-20',dtl='-5',equity='-15',cash='0',current_payable='0'),
        operating_cash=dict(original_2023='50',original_2024='85/2',restated_2024='85/2',restated_2025='85/2'))
    write(OUT/'authored-cases.json',dict(cases=cases,expected=targets))
    files=[OUT/'authored.py',OUT/'authored-cases.json',OUT/'synthetic-editions.json',OUT/'source-reading.md',
        ROOT/'docs/plans/accounting-comparative-rebuild-20261016.md',
        ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
        PREV/'fixture.json',PREV/'computed.json',PREV/'source-review.md',PREV/'verify_calculations.py',PREV/'result.md']
    write(OUT/'input-lock.json',dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]))
    print(json.dumps(dict(cases=len(cases),editions=len(docs),locked_files=len(files))))


if __name__=='__main__':main()
