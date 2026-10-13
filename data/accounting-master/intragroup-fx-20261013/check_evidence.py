"""Exact source and rational checks for one FX-only consolidation example."""
import datetime
import hashlib
import json
import time
from fractions import Fraction as F
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + "\n")


def main():
    assert not (OUT / "completion.json").exists()
    start=time.monotonic(); checks=[]

    def ck(name, passed):
        checks.append({"name":name,"passed":bool(passed)})

    for rel,digest in json.loads((OUT/'baseline.json').read_text())['input_hashes'].items():
        ck('protected input '+rel,sha(ROOT/rel)==digest)
    review=json.loads((OUT/'source-review.json').read_text())
    ck('seven source renders read',len(review['pages'])==7 and all(x['inspected'] for x in review['pages']))
    for row in review['pages']:
        ck('source render '+str(row['pdf_page']),sha(ROOT/row['path'])==row['sha256'])
    ck('entire retained IAS21 read',set(range(151,163))<=set(review['text_pages_read']))
    quotes=[
      ('IAS21.15',153,'settlement is neither planned nor likely to occur in the foreseeable future',
       'Net-investment condition; not an optional presentation election'),
      ('IAS21.15-exclusion',153,'They do not include trade receivables or trade payables.',
       'A trade balance cannot qualify merely because repayment is delayed'),
      ('IAS21.15A',153,'may be any subsidiary of the group.',
       'The lending group entity need not be the parent; the example selects the parent'),
      ('IAS21.23a',155,'foreign currency monetary items shall be translated using the closing rate;',
       'Parent EUR monetary receivable uses USD per EUR closing rate'),
      ('IAS21.24',155,'The carrying amount of an item is determined in conjunction with other relevant standards.',
       'Given carrying amount is a scoped input, not an initial-measurement rule'),
      ('IAS21.28',156,'shall be recognised in profit or loss in the period in which they arise, except as described in paragraph 32.',
       'Default exchange-difference presentation subject to the specific exception'),
      ('IAS21.32-separate',156,'shall be recognised in profit or loss in the separate financial statements of the reporting entity',
       'Net-investment condition does not move parent separate gain to OCI'),
      ('IAS21.32-group',156,'such exchange differences shall be recognised initially in other comprehensive income and reclassified from equity to profit or loss on disposal',
       'Group presentation differs; disposal follows paragraph 48, not loan maturity alone'),
      ('IAS21.33',156,'If such an item is denominated in the functional currency of the foreign operation, an exchange difference arises in the reporting entity',
       'EUR denomination creates parent-side FX in the selected USD/EUR case'),
      ('IAS21.39a',157,'assets and liabilities for each statement of financial position presented (ie including comparatives) shall be translated at the closing rate',
       'Translate subsidiary cash and payable together'),
      ('IAS21.39c',157,'all resulting exchange differences shall be recognised in other comprehensive income.',
       'Ordinary subsidiary net-asset translation component is OCI'),
      ('IAS21.45',159,'cannot be eliminated against the corresponding intragroup liability (or asset) without showing the results of currency fluctuations',
       'Eliminating intragroup balance does not erase the exchange result'),
      ('IAS21.50',160,'IAS 12 Income Taxes applies to these tax effects.',
       'Tax omitted from the authored FX-only step, not declared nonexistent in real cases'),
      ('IAS7.28',47,'Unrealised gains and losses arising from changes in foreign currency exchange rates are not cash flows.',
       'Cash-value movement is not a receipt'),
      ('IAS7.28-presentation',47,'This amount is presented separately from cash flows from operating, investing and financing activities',
       'Separate exchange effect reconciles group cash'),
      ('IFRS10.B86c',697,'eliminate in full intragroup assets and liabilities, equity, income, expenses and cash flows relating to',
       'Consolidation removes loan balances and parent investment against subsidiary equity')]
    support=[]
    for anchor,page,quote,meaning in quotes:
        text=' '.join((OUT/'source-pages'/f'page-{page}.txt').read_text().split())
        ck('exact source '+anchor,quote in text)
        support.append({'anchor':anchor,'pdf_page':page,'quote':quote,'local_interpretation':meaning})
    save('source-support.json',{'source':review['source'],'sha256':review['source_sha256'],'anchors':support,
        'edition':'Original 2023 EU incorporation; regulation date corrected to 13 September 2023',
        'limits':'Historical authority; no current amendment completeness, actual entity classification or compliance claim'})
    r0=F(6,5);r1=F(13,10);loan=F(100);capital=F(20);foreign_cash=loan+capital
    parent_cash=F(56);investment=capital*r0;parent_equity=F(200)
    parent_gain=loan*(r1-r0);translation=capital*(r1-r0)
    opening_group_cash=parent_cash+foreign_cash*r0
    closing_group_cash=parent_cash+foreign_cash*r1
    ck('parent opening balance',parent_cash+investment+loan*r0==parent_equity)
    ck('subsidiary opening balance in EUR',foreign_cash==loan+capital)
    ck('opening consolidated balance',opening_group_cash==parent_equity==200)
    ck('parent closing balance',parent_cash+investment+loan*r1==parent_equity+parent_gain)
    ck('translated subsidiary balance',foreign_cash*r1==loan*r1+investment+translation)
    # Debit-positive trial balances, including income and OCI before closing.
    combined={'cash':closing_group_cash,'investment':investment,'receivable':loan*r1,
              'payable':-loan*r1,'parent_capital':-parent_equity,'sub_capital':-investment,
              'fx_gain':-parent_gain,'translation_oci':-translation}
    ck('combined balances',sum(combined.values())==0)
    ordinary=combined.copy()
    for account,amount in {'payable':loan*r1,'receivable':-loan*r1,'sub_capital':investment,'investment':-investment}.items():
        ordinary[account]+=amount
    ck('eliminated loan and investment',all(ordinary[a]==0 for a in ['payable','receivable','sub_capital','investment']))
    ck('ordinary group trial balance',sum(ordinary.values())==0)
    ck('ordinary profit and OCI',-ordinary['fx_gain']==10 and -ordinary['translation_oci']==2)
    net_investment=ordinary.copy();net_investment['fx_gain']+=parent_gain
    net_investment['translation_oci']-=parent_gain
    ck('net-investment group trial balance',sum(net_investment.values())==0)
    ck('net-investment profit and OCI',net_investment['fx_gain']==0 and -net_investment['translation_oci']==12)
    ck('same total equity',parent_equity+parent_gain+translation==closing_group_cash==212)
    ck('cash exchange effect',closing_group_cash-opening_group_cash==foreign_cash*(r1-r0)==12)
    ck('no operating investing financing receipt',closing_group_cash==opening_group_cash+F(0)+F(0)+F(0)+12)
    ck('wrong erasure breaks statements',parent_equity+translation!=closing_group_cash)
    ck('wrong double cash gain breaks statements',parent_equity+parent_gain+translation+foreign_cash*(r1-r0)!=closing_group_cash)
    # These limiting cases test signs and invariants, not observed market rates.
    for closing,label in [(r0,'unchanged'),(F(11,10),'EUR falls')]:
        gain=loan*(closing-r0);oci=capital*(closing-r0);cash=parent_cash+foreign_cash*closing
        ck(label+' equity reconciliation',cash==parent_equity+gain+oci)
        ck(label+' expected cash',cash==(200 if label=='unchanged' else 188))
    save('calculations.json',{'units':'USD reporting units; EUR quantities stated separately',
        'rates_usd_per_eur':{'opening':str(r0),'closing':str(r1)},
        'scope':'FX-only measurement step from established carrying balances; non-FX measurement inputs fixed',
        'parent_open':{'cash_usd':56,'investment_usd':24,'receivable_eur':100,'receivable_usd':120,'equity_usd':200},
        'subsidiary_eur':{'cash':120,'payable':100,'paid_in_capital':20},
        'parent_entry_usd':{'debit_receivable':10,'credit_fx_gain':10},
        'subsidiary_translated_usd':{'cash':156,'payable':130,'historical_capital':24,'translation_oci':2},
        'elimination_entries_usd':[{'debit_payable':130,'credit_receivable':130},{'debit_sub_capital':24,'credit_parent_investment':24}],
        'ordinary_group':{'cash':212,'liabilities':0,'opening_equity':200,'profit':10,'oci':2,'closing_equity':212},
        'net_investment_group':{'cash':212,'liabilities':0,'opening_equity':200,'profit':0,'oci':12,'closing_equity':212},
        'group_only_presentation_entry':{'debit_fx_gain':10,'credit_oci':10},
        'cash_reconciliation':{'opening':200,'operating':0,'investing':0,'financing':0,'exchange_effect':12,'closing':212},
        'not_concluded':['Actual company facts','Initial fair value or interest-free loan measurement','Complete period accounting','Default current IFRS treatment without applicability check']})
    failed=[x['name'] for x in checks if not x['passed']]
    save('source-checks.json',{'checks':checks,'passed':len(checks)-len(failed),'failed':failed,'wall_seconds':time.monotonic()-start})
    print(json.dumps({'passed':len(checks)-len(failed),'failed':failed}))
    raise SystemExit(bool(failed))


if __name__=='__main__':
    main()
