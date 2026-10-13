"""Read exact retained interim tables; join annual rows without zero-filling."""
import hashlib
import html
import json
import re
from decimal import Decimal
from pathlib import Path
from bs4 import BeautifulSoup
import fitz

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
if (UNIT / 'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, x):
    (UNIT / name).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def norm(s):
    return ''.join(s.split())
def number(s):
    s=norm(s).replace(',','').replace('(','-').replace(')','').replace('$','')
    return None if s=='—' else str(Decimal(s))

source=ROOT/'docs/design/cases/apple/interim-2025q1.html'
assert sha(source)=='2f7629f0733f75b3155dd52f7ae6a8724468e3cde1a9ce32fbce96d98f1ec27e'
raw=source.read_text(); soup=BeautifulSoup(raw,'html.parser'); tables=soup.find_all('table')
fragments=list(re.finditer(r'<table\b[^>]*>.*?</table>',raw,re.S))
assert len(fragments)==len(tables)==37 and not any(t.find('table') for t in tables)
full=' '.join(soup.stripped_strings)
annual_unit=ROOT/'data/accounting-master/apple-statement-network-20261013'
annual=json.loads((annual_unit/'statement-readings.json').read_text())
annual_rows={r['id']:r for r in annual['rows']}
specs={
 'operations':(12,'97,960 26,340 124,300 59,447 6,578 66,025 58,275 8,268 7,175 15,443 42,832 (248) 42,584 6,254 36,330 2.41 2.40 15,081,724 15,150,865'),
 'comprehensive':(13,'36,330 (625) 1,651 784 2,435 (1,647) 220 (1,427) 383 36,713'),
 'balance':(14,'30,299 23,476 29,639 29,667 6,911 13,248 133,240 87,593 46,069 77,183 210,845 344,085 61,910 61,151 8,461 1,995 10,848 144,365 83,956 49,006 132,962 277,327 84,768 (11,221) (6,789) 66,758 344,085'),
 'equity':(15,'56,950 83,276 (1,891) 3,383 84,768 (19,154) 36,330 (3,819) (1,102) (23,476) (11,221) (7,172) 383 (6,789) 66,758 0.25'),
 'cash_flow':(16,'29,943 36,330 3,080 3,286 (2,009) 3,597 3,166 215 939 (6,671) (11,998) 29,935 (6,124) 15,967 3,492 (2,940) (603) 9,792 (2,921) (3,856) (23,606) (1,009) (7,944) (35) (39,371) 356 30,299 18,651'),
}
omitted={'equity.issued':'Annual common-stock issuance row is absent from the interim equity table; no zero reading created.',
         'cash_flow.debt_issuance':'Annual term-debt issuance row is absent from the interim cash-flow table; no zero reading created.'}
rows=[]; checks={}; sources=[]; values={}; rendered=[]
(UNIT/'sources').mkdir(exist_ok=True);(UNIT/'source-render').mkdir(exist_ok=True)
for statement,(index,expected) in specs.items():
    table=tables[index]; frag=fragments[index]
    fragment=UNIT/f'sources/table-{index}.html'; fragment.write_text(frag.group())
    checks['exact_fragment:'+statement]=norm(BeautifulSoup(frag.group(),'html.parser').get_text())==norm(table.get_text())
    table_text=' '.join(table.stripped_strings); start=full.index(table_text)
    prefix=full[max(0,start-430):start]; heading_start=prefix.rfind('Apple Inc. CONDENSED')
    heading=prefix[heading_start:]; assert heading_start>=0 and 'Unaudited' in heading and 'In millions' in heading
    checks['periods:'+statement]='December 28, 2024' in table_text and ('September 28, 2024' if statement=='balance' else 'December 30, 2023') in table_text
    all_rows=[]; numeric=[]; view_rows=[]
    for row_no,tr in enumerate(table.find_all('tr')):
        cells=tr.find_all(['td','th'],recursive=False)
        texts=[c.get_text(' ',strip=True) for c in cells]
        nonempty=[s for s in texts if s]
        if not nonempty:continue
        all_rows.append({'source_row':row_no,'cells':[{'literal':t,'colspan':int(c.get('colspan',1))} for c,t in zip(cells,texts)]})
        merged=[];i=0
        while i<len(nonempty):
            if nonempty[i]=='$':merged.append('$ '+nonempty[i+1]);i+=2
            else:merged.append(nonempty[i]);i+=1
        if len(merged)==2:
            assert merged[0].startswith('December'),merged
            merged=['']+merged
        assert len(merged) in {1,3},merged
        if len(merged)==1:
            view_rows.append('<tr><td colspan="3">'+html.escape(merged[0])+'</td></tr>')
        else:
            view_rows.append('<tr>'+''.join('<td style="width:'+str([66,17,17][j])+'%;text-align:'+('left' if j==0 else 'right')+'">'+html.escape(s)+'</td>' for j,s in enumerate(merged))+'</tr>')
            if re.fullmatch(r'\$?\s*[()\d,.\s]+|—',merged[1]):
                numeric.append((row_no,merged,texts))
    keys=[r['id'] for r in annual['rows'] if r['statement']==statement and r['id'] not in omitted]
    checks['all_current_rows:'+statement]=[norm(m[1][1]).replace('$','') for m in numeric]==expected.split() and len(numeric)==len(keys)
    assert checks['all_current_rows:'+statement]
    for key,(row_no,cells,original_cells) in zip(keys,numeric):
        old=annual_rows[key]; row={k:old[k] for k in ['id','statement','entity','unit','precision']}
        row.update({'label':cells[0],'period':'2024-12-28' if statement=='balance' else 'FY2025 Q1: 2024-09-29 through 2024-12-28',
             'basis':'US GAAP issuer condensed statements; unaudited','literal':cells[1],'value':number(cells[1]),'status':'reported reading',
             'source':str(source.relative_to(ROOT)),'source_sha256':sha(source),'html_table_index':index,'source_row':row_no,'printed_page':index-11,
             'original_cells':original_cells,'comparison':{'period':'2024-09-28' if statement=='balance' else 'FY2024 Q1 ended 2023-12-30','literal':cells[2],'value':number(cells[2])}})
        part=key.split('.')[1]
        if statement=='balance' or statement in {'equity','cash_flow'} and (part in {'opening','closing'} or part.endswith(('_opening','_closing'))):
            row['measurement_kind']='instant balance'
            row['measurement_date']='2024-09-28' if part=='opening' or part.endswith('_opening') else '2024-12-28'
        else:row['measurement_kind']='period amount or statistic'
        rows.append(row);values[key]=Decimal(row['value'])
        if statement=='balance':
            values['opening.'+part]=Decimal(row['comparison']['value'])
            checks['annual_endpoint:'+part]=row['comparison']['value']==old['value']
    view_table='<table>'+''.join(view_rows)+'</table>'
    checks['all_view_text:'+statement]=norm(BeautifulSoup(view_table,'html.parser').get_text())==norm(table.get_text())
    view='<html><body><h1>'+html.escape(heading)+'</h1><p>Derived view of retained HTML table '+str(index)+'. Original cell text/order preserved; not a browser screenshot.</p>'+view_table+'</body></html>'
    view_path=UNIT/f'sources/table-{index}-view.html';view_path.write_text(view)
    pdf=UNIT/f'source-render/table-{index}.pdf'
    story=fitz.Story(html=view,user_css='body {font-family:sans-serif;font-size:8.5pt;} h1 {font-size:12pt;} table {width:100%;font-size:8pt;} td {padding:2pt;}')
    writer=fitz.DocumentWriter(str(pdf));page=fitz.paper_rect('a4');where=page+(28,28,-28,-28);more=True;count=0
    while more:
        count+=1
        if count>3:raise RuntimeError('Source view needs layout review: '+statement)
        device=writer.begin_page(page);more,_=story.place(where);story.draw(device);writer.end_page()
    writer.close()
    with fitz.open(pdf) as d:
        for n,p in enumerate(d,1):
            image=UNIT/f'source-render/table-{index}-{n}.png';p.get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(image)
            rendered.append({'statement':statement,'table':index,'derived_page':n,'image':str(image.relative_to(ROOT)),'sha256':sha(image)})
    sources.append({'statement':statement,'heading':heading,'table_index':index,'printed_page':index-11,'fragment':str(fragment.relative_to(ROOT)),
          'fragment_sha256':sha(fragment),'raw_character_start':frag.start(),'raw_character_end':frag.end(),'view':str(view_path.relative_to(ROOT)),
          'all_source_rows':all_rows,'view_text_preserved':checks['all_view_text:'+statement]})

relations=[]
old_relations=json.loads((annual_unit/'relationship-ledger.json').read_text())['relations']
for relation in old_relations:
    terms=[t for t in relation['terms'] if t['row'] not in omitted]
    removed=[t['row'] for t in relation['terms'] if t['row'] in omitted]
    computed=sum(Decimal(t['coefficient'])*values[t['row']] for t in terms)
    target=relation['target'];name=relation['id'];role=relation['diagnostic_role']
    if target in values:rhs=values[target]
    elif name=='balance_changes':rhs=values['balance.equity']-values['opening.equity']
    elif name in {'other_equity_movements','operating_reconciliation_adjustments','operating_asset_liability_adjustments'}:
        rhs=computed;role='derived subtotal; explanatory only'
    else:rhs=Decimal(0)
    rec={'id':name,'terms':terms,'removed_annual_rows':removed,'target':target if target in values else str(rhs),'computed':str(computed),'target_value':str(rhs),
          'residual':str(computed-rhs),'purpose':relation['purpose'],'diagnostic_role':role}
    if name.startswith('diagnostic:'):
        rec['purpose']='Displayed signed difference for the CURRENT quarter under the recorded row coefficients. Causes unassigned; a zero difference does not identify gross transactions.'
    else:
        rec['purpose']=rec['purpose'].replace('FY2024','FY2025 Q1')
    if role.startswith('pass/fail'):checks['relation:'+name]=computed==rhs
    relations.append(rec)
for key,annual_key in [('equity.opening','equity.closing'),('equity.capital_opening','equity.capital_closing'),('equity.retained_opening','equity.retained_closing'),('equity.aoci_opening','equity.aoci_closing'),('cash_flow.opening','cash_flow.closing')]:
    checks['annual_flow_endpoint:'+key]=str(values[key])==annual_rows[annual_key]['value']
    relations.append({'id':'annual_to_quarter:'+key,'annual_row':annual_key,'interim_row':key,'value':str(values[key]),'diagnostic_role':'cross-period endpoint identity'})
checks['100_current_rows']=len(rows)==100
checks['unique_ids']=len({r['id'] for r in rows})==100
checks['no_synthetic_issued_rows']=all(r['id'] not in omitted for r in rows)
checks['comparative_dash_preserved']=next(r for r in rows if r['id']=='cash_flow.debt_repayments')['comparison']['value'] is None
checks['blank_commitments']=any('Commitments and contingencies'==c['literal'] for s in sources for rr in s['all_source_rows'] for c in rr['cells'])
combined={}
for key in ['operations.net_income','comprehensive.oci','comprehensive.comprehensive_income','cash_flow.operating','cash_flow.investing','cash_flow.financing','cash_flow.change']:
    combined[key]=str(Decimal(annual_rows[key]['value'])+values[key])
annual_other=next(x for x in old_relations if x['id']=='other_equity_movements')['computed']
quarter_other=next(x for x in relations if x['id']=='other_equity_movements')['computed']
combined['other_equity_movements']=str(Decimal(annual_other)+Decimal(quarter_other))
checks['combined_equity_bridge']=Decimal(annual_rows['equity.opening']['value'])+Decimal(combined['comprehensive.comprehensive_income'])+Decimal(combined['other_equity_movements'])==values['equity.closing']
checks['combined_cash_bridge']=Decimal(annual_rows['cash_flow.opening']['value'])+Decimal(combined['cash_flow.change'])==values['cash_flow.closing']
checks['combined_activities']=sum(Decimal(combined['cash_flow.'+key]) for key in ['operating','investing','financing'])==Decimal(combined['cash_flow.change'])
save('combined-period.json',{'period':'2023-10-01 through 2024-12-28; fiscal 2024 plus FY2025 Q1','status':'Derived sum of compatible adjacent period amounts, not an issuer annual or trailing-twelve-month statement','amounts_USD_million':combined,'excluded':'Endpoint balances, EPS, weighted-average shares and per-share dividends are not added. Original comparative quarter remains separate.'})
save('statement-readings.json',{'rows':rows,'sources':sources,'omitted_annual_rows':omitted,'source':str(source.relative_to(ROOT)),'sha256':sha(source),
 'limits':'Complete selected current-quarter tables and typed comparisons; no journal identification, package completeness or exact unrounded claim'})
save('relationship-ledger.json',{'relations':relations,'annual_basis_sha256':sha(annual_unit/'relationship-ledger.json'),
 'scope':'Reuse declared displayed relations with absent annual rows explicitly removed; prior-year quarter is a comparison, never the opening period'})
save('source-renders.json',{'source_sha256':sha(source),'images':rendered,'type':'Derived text/column-preserving views; no original-browser-render claim','scale':1.4,'scale_provenance':'Convenience reading size; text/column preservation checked separately'})
unresolved=[{'id':r['id'],'computed_difference':r['computed'],'terms':r['terms'],'status':'unassigned explanatory difference'} for r in relations if r['id'].startswith('diagnostic:')]
save('unresolved-edges.json',{'differences':unresolved,'nonconclusions':['No allocation of FX, settlement, timing, write-offs or taxes from a residual.','No Cartesian product of earlier note witnesses declared jointly admissible.','Future path needs explicit future operations, treatment, timing and funding dependencies.']})
failed=[k for k,v in checks.items() if not v]
save('source-arithmetic-checks.json',{'passed':sum(checks.values()),'failed':failed,'checks':checks})
print(json.dumps({'rows':len(rows),'relations':len(relations),'views':len(rendered),'passed':sum(checks.values()),'failed':failed}))
raise SystemExit(bool(failed))
