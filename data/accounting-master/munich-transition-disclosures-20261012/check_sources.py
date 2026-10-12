"""Bind selected source claims and check disclosed arithmetic without valuation."""
import hashlib,json,time
from decimal import Decimal as D
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert not (OUT/'completion.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda n,v:(OUT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
b=json.loads((OUT/'baseline.json').read_text());pages=json.loads((OUT/'selected-pages.json').read_text())
checks=[];start=time.monotonic()
def ck(n,v):checks.append({'name':n,'passed':bool(v)})
ck('retained primary PDF identity',sha(ROOT/b['source_record']['local_path'])==b['source_record']['sha256'])
for r in pages:
    ck('text identity '+str(r['pdf_page']),sha(ROOT/r['text'])==r['text_sha256'])
    ck('render identity '+str(r['pdf_page']),sha(ROOT/r['render'])==r['render_sha256'])
norm=lambda s:' '.join(s.split())
texts={r['pdf_page']:norm((ROOT/r['text']).read_text()) for r in pages}
specs=[
('translation',3,'This document is a translation','the German original is binding.'),
('rounding',157,'Amounts are rounded to million euros.','refer to the comparative period.'),
('basis',157,'Munich Re’s consolidated financial statements have been','German Commercial Code (HGB).'),
('adoption',157,'Munich Re is applying IFRS 9, Financial Instruments,','has therefore been restated.'),
('judgment',158,'IFRS 17 transition approaches','retrospective approach.'),
('models',166,'The basic approach consists','eligible life and health primary insurance contracts.'),
('discount',167,'Discount rates are determined','life primary insurance business, in particular.'),
('riskmethod',167,'The risk adjustment for non-financial risk is determined','current conditions.'),
('retrospective',185,'We apply the full retrospective approach to remeasure','existing regular processes and internal reporting.'),
('impracticability',185,'Where it was impracticable to apply','the new accounting regime.'),
('modified',185,'The aim of the modified retrospective approach','insurance finance income or expenses.'),
('methodmix',185,'For certain existing contracts','make up over 90%.'),
('overlay',186,'In addition, we apply the classification overlay approach','expected credit losses under IFRS 9.'),
('property',186,'In connection with the initial application of IFRS 17 as at','has been restated accordingly.'),
('equity',186,'Equity as at 1 January 2022 was','have a contrary impact.'),
('csm',186,'As a component of insurance contracts issued and held','under IFRS 17.'),
('risktransition',187,'own funds to be calculated','same way as we do under Solvency II.'),
('result',187,'Initial application of IFRS 17 resulted in an increase','€1.9bn.'),
('presentation',187,'With the introduction of IFRS 17,','included in the insurance items.'),
('presentationbasis',188,'The balance sheet structure before','the measurement model of the VFA.'),
('heldpopulation',212,'The following table presents the effects on the net cost/gain','type of transition approach applied.'),
('issuedpopulation',256,'The following tables present the effects on the contractual','applying the premium allocation approach.'),
('issuedfootnote',257,'This only shows groups','in force at the transition date.')
]
anchors=[]
for key,n,a,z in specs:
    text=texts[n];i=text.index(a);j=text.index(z,i)+len(z);quote=text[i:j]
    ck('source anchor '+key,quote.startswith(a) and quote.endswith(z))
    anchors.append({'id':key,'pdf_page':n,'printed_page':n-2,'quote':quote,'normalization':'whitespace only','source_pdf_sha256':b['source_record']['sha256']})
save('source-anchors.json',anchors)
bridge={
'equity_ifrs4':'30.9','modified_measurement_basis':'25.3',
'contractual_service_margin':'-22.3','risk_adjustment':'-5.6',
'loss_component':'-1.4','deferred_taxes':'1.5','reported_change':'-2.5',
'equity_ifrs17':'28.5'}
raw=(OUT/'text/page-186.txt').read_text()
for key,value in bridge.items():
    raw_token=value.replace('-','–').replace('.','\x13')
    ck('raw bridge numeric token '+key,raw_token in raw)
total=sum(D(bridge[k]) for k in ['modified_measurement_basis','contractual_service_margin','risk_adjustment','loss_component','deferred_taxes'])
difference=D(bridge['equity_ifrs17'])-D(bridge['equity_ifrs4'])
ck('displayed components sum to reported change',total==D(bridge['reported_change']))
ck('displayed endpoints differ by -2.4 not -2.5',difference==D('-2.4') and difference!=total)
# An interior witness shows compatibility with rounding, not the true balances.
witness={**bridge,'equity_ifrs4':'30.94','modified_measurement_basis':'25.32','equity_ifrs17':'28.46','reported_change':'-2.48'}
ck('rounding witness is inside every display interval',all(abs(D(v)-D(bridge[k]))<D('.05') for k,v in witness.items()))
wsum=sum(D(witness[k]) for k in ['modified_measurement_basis','contractual_service_margin','risk_adjustment','loss_component','deferred_taxes'])
ck('witness component identity',wsum==D(witness['reported_change']))
ck('witness opening plus change identity',D(witness['equity_ifrs4'])+wsum==D(witness['equity_ifrs17']))
issued={'full':-596,'modified':-12128,'fair_value':-9965,'total':-22688}
held={'full':20,'modified':57,'fair_value':291,'total':368}
# Match the contiguous opening row, preserving raw control-character separators.
for page,title,values in [
(257,'Carrying amount at 1 January – Contractual service margin from insurance contracts issued',[-243,-13341,-9842,-23427,-596,-12128,-9965,-22688]),
(213,'Carrying amount at 1 January – Net cost/gain',[20,57,291,368])]:
    t=texts[page].replace('\x12','').replace('\x1c','').replace('–','-')
    phrase=title.replace('–','-')+' '+' '.join(str(v) for v in values)
    ck('visually checked opening row '+str(page),phrase in t)
ck('issued rounded row residual is one million',sum(v for k,v in issued.items() if k!='total')-issued['total']==-1)
ck('held opening row totals',sum(v for k,v in held.items() if k!='total')==held['total'])
net=(D(issued['total'])+D(held['total']))/D(1000)
ck('separate opening totals net to -22.320 billion',net==D('-22.320'))
ck('net total is consistent with displayed -22.3 billion',abs(net-D(bridge['contractual_service_margin']))<D('.05'))
save('numeric-evidence.json',{'units':{'bridge':'EUR billions, one decimal','method_openings':'EUR millions'},
  'date':'2022-01-01','bridge':bridge,'displayed_component_sum':str(total),'displayed_endpoint_difference':str(difference),
  'rounding_assumption':'Hypothetical nearest display increment, interior witness avoids tie convention; not recovered true balances.',
  'rounding_witness':witness,'issued_opening':issued,'held_opening':held,'net_margin_from_reported_totals_billion':str(net),
  'scope':'Disclosed group transition populations. No actual group valuation or default parameter inference.',
  'extraction_issue':'U+0013 used in decimal positions; U+0012/U+001C used in grouping positions. Raw text retained and numeric readings visually checked.'})
failed=[r['name'] for r in checks if not r['passed']]
save('source-checks.json',{'checks':checks,'passed':len(checks)-len(failed),'failed':failed,
  'selected_pages':len(pages),'anchors':len(anchors),'wall_seconds':time.monotonic()-start,'readiness':'not_ready'})
print(json.dumps({'passed':len(checks)-len(failed),'failed':failed,'pages':len(pages),'anchors':len(anchors),'net_margin_billion':str(net)}))
raise SystemExit(bool(failed))
