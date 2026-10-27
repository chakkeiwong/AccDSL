"""Source anchors and query limits for the integrated risk argument."""
from pathlib import Path
import hashlib, json, os, re, sys
import fitz
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
norm=lambda s:' '.join(s.split())
rel=lambda p:str(p.relative_to(ROOT))


def main():
    inputs={};checks=[];ck=lambda n,ok:checks.append(dict(id=n,passed=bool(ok)))
    for p in [Path(__file__),ROOT/'docs/design/cases/apple/annual-2024.pdf',
              ROOT/'docs/design/cases/apple/interim-2025q1.html',OUT/'source-claim-supplement.json',
              ROOT/'data/accounting-master/apple-macroeconomic-20261010/source-claim-supplement.json']:
        inputs[rel(p)]=sha(p)
    macro=read(ROOT/'data/accounting-master/apple-macroeconomic-20261010/source-claim-supplement.json')
    business=read(OUT/'source-claim-supplement.json')
    doc=fitz.open(ROOT/'docs/design/cases/apple/annual-2024.pdf')
    for name,d,page in [('macro',macro,8),('interruption',business,9)]:
        original=norm(doc[page-1].get_text())
        ck(name+' heading original PDF',norm(d['body']['heading']['quote']) in original)
        for p in d['body']['paragraphs']:ck(name+' paragraph '+str(p['index'])+' original PDF',norm(p['quote']) in original)
    preamble=macro['interim_context']['quote']
    soup=BeautifulSoup((ROOT/'docs/design/cases/apple/interim-2025q1.html').read_text(),'html.parser')
    ck('interim incorporation original HTML',norm(preamble) in norm(soup.get_text(' ',strip=True)))
    entries=[
        ('macro',1,'current issuer assertions','International sales and supplier-facility majorities have different populations.', ['a majority','supplier facilities']),
        ('macro',2,'conditional demand mechanisms','Confidence/spending can respond to multiple economic factors; no elasticity.', ['can adversely impact consumer confidence','fiscal and monetary policy']),
        ('macro',3,'conditional partner outcomes','Operating partners can face financial instability, credit constraints and insolvency.', ['Potential outcomes include financial instability','developers']),
        ('macro',4,'conditional financial consequences','Trade collection, financial counterparties, debt access, liquidity and fair value remain distinct.', ['limitations on the Company’s ability to issue new debt','declines in the fair values']),
        ('interruption',1,'conditional affected populations','Customers, employees and operating partners are distinct affected actors.', ['customers, employees, suppliers','other channel partners']),
        ('interruption',2,'current assertions, management belief, historical report and future possibility','Preserve manufacturing locations, trade benefits belief, reported past restrictions and conditional escalation separately.', ['believes that it generally benefits','have in the past led to tariffs','If disputes and conflicts further escalate']),
        ('interruption',3,'issuer exposure/climate assertions and conditional effects','Facility/hazard exposure and climate statement are reported assertions, without facility-level hazard rates.', ['Global climate change is resulting','ransomware and other cybersecurity attacks']),
        ('interruption',4,'conditional operating consequences','Manufacture, delivery, service, cost and demand effects require different facts.', ['slowdowns and outages','consumer spending and demand']),
        ('interruption',5,'supplier requirement, reported past effect and future possibility','Required safe workplaces do not certify safety; COVID history and possible recurrence stay separate.', ['required to maintain safe working environments','have adversely affected, and could in the future']),
        ('interruption',6,'conditional recovery and qualified insurance assertion','Resumption takes time and expenditure; single-source exposure amplifies consequences; insurance is qualified.', ['substantial recovery time','single or limited sources','may be insufficient'])]
    claims=[]
    for name,index,kind,meaning,anchors in entries:
        d=macro if name=='macro' else business;p=d['body']['paragraphs'][index-1]
        for phrase in anchors:ck(name+' '+str(index)+' '+phrase,phrase in norm(p['quote']))
        claims.append(dict(id=name+'.'+str(index),source='annual',start=p['start'],end=p['end'],
            quote_sha256=p['sha256'],source_class=kind,author_interpretation=meaning,
            evidence='original PDF paragraph',independent_acceptance='pending'))
    queries=[
        ('joint_macro','Does the prose establish a joint loss law?','No. It identifies possible common economic conditions and distinct channels.','Dependence structure, probabilities, response functions and timing.'),
        ('geography','Can sales regions identify disrupted factories?','No. Customer geography and supplier-facility geography differ.','Product-component-supplier-route mappings and legal-entity facts.'),
        ('trade','Does a named historical tariff imply an operative future rate?','No. The source reports past restrictions and warns about escalation.','Named instrument, date, jurisdiction, scope and terms.'),
        ('past_health','Does this paragraph report a past public-health effect?','Yes, as an issuer assertion about COVID-19 and major public-health issues.','Event-level attribution, dates, amounts and matching transactions.'),
        ('response','Which alternate supplier is feasible?','Unresolved; the scenario must supply capacity, qualification and contract facts.','Available production, lead times, specification compatibility and terms.'),
        ('recovery','Does event cessation immediately restore delivery?','The source permits prolonged recovery; no fixed duration follows.','Capacity restoration, orders, inventory and spending/settlement dates.'),
        ('insurance','Does insurance guarantee a net recoverable loss?','No; coverage and adequacy are qualified.','Policy period, insured event, exclusions, deductible, limit, insurer and applicable recognition.'),
        ('safety','Does a supplier safety requirement prove no accident?','No; requirement and realised safety outcome are separate.','Facility compliance, incident facts and resulting obligations.'),
        ('interim','Does incorporation mean equal later exposure?','No; the interim preserves annual dependency with exceptions.','Later actual facilities, contracts, orders, counterparties and byte availability.')]
    ledger=dict(claims=claims,queries=[dict(id=i,question=q,answer=a,missing_facts=m) for i,q,a,m in queries],
        local_scenarios=[dict(id='open_route_weak_demand',classification='explicit modelling assumption; not identified Apple history',states=['available supply route','reduced orders']),
                         dict(id='interrupted_route_waiting_orders',classification='explicit modelling assumption; not identified Apple history',states=['orders remain','component cannot arrive'])],
        probability_weights=None,accounting_consequence='No automatic journal; recognition, measurement and settlement require separate facts and authority.')
    (OUT/'claim-query-ledger.json').write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n')
    inputs[rel(OUT/'claim-query-ledger.json')]=sha(OUT/'claim-query-ledger.json')
    report=dict(inputs=inputs,checks=checks,passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks))
    with (OUT/'meaning-checks.json').open('x') as f:f.write(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:report[k] for k in ['passed','failed']}));assert report['failed']==0,[x for x in checks if not x['passed']]

if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    main()
