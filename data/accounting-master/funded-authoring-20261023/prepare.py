"""Create separate text and typed examples once; no runtime compilation."""
import hashlib
import json
from pathlib import Path
from authoring import schema

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SOURCE=ROOT/'data/accounting-master/corporate-portable-20261015/portable-exchanges.json'


def q(n,d=1):
    return {'n':str(n),'d':str(d)}


def main():
    names=['schema.json','example.json','example.accdsl']
    if any((OUT/n).exists() for n in names): raise RuntimeError('Refuse overwrite')
    data=json.loads(SOURCE.read_text()); projection=data['aliases']['projection.stress7']['digest']
    source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assumption='Synthetic eligible facility; explicit draw and prompt collection; no other intervening changes; no fees; deductible interest under the retained demo tax method.'
    events=[('purchase','2025-01-02T09:00:00Z'),('delivery','2025-01-03T09:00:00Z'),
            ('facility_draw','2025-01-04T11:00:00Z'),('supplier_payment','2025-01-04T12:00:00Z'),
            ('collection','2025-01-05T09:00:00Z'),('facility_interest','2025-01-06T09:00:00Z'),
            ('facility_repayment','2025-01-06T10:00:00Z'),('payroll','2025-01-07T09:00:00Z'),
            ('plant_addition','2025-12-31T09:00:00Z'),('depreciation','2025-12-31T10:00:00Z'),
            ('interest','2025-12-31T11:00:00Z'),('tax','2025-12-31T12:00:00Z'),
            ('dividend','2025-12-31T13:00:00Z'),('close','2025-12-31T14:00:00Z')]
    claims=[{'id':'opening-ar','ledger':'receivable','origin':'opening','recognised':q(35),'settlement':q(10)},
            {'id':'sales-ar','ledger':'receivable','origin':'delivery','recognised':q(300),'settlement':q(270)},
            {'id':'opening-ap','ledger':'payable','origin':'opening','recognised':q(30),'settlement':q(0)},
            {'id':'purchase-ap','ledger':'payable','origin':'purchase','recognised':q(170),'settlement':q(160)}]
    body={'profile':'FundedYearInputsDraft/1','name':'NorthstarFundedYear','projection':{'alias':'projection.stress7','digest':projection},
          'source':{'path':str(SOURCE.relative_to(ROOT)),'sha256':source_hash},
          'context':{'entity':'Northstar','book':'DemoCorporate','currency':'USD'},'share':q(1,2),
          'assumption':assumption,'claims':claims,
          'facility':{'id':'bridge-facility','limit':q(100),'drawn':q(0),'reserved':q(0)},
          'loan':{'facility_id':'bridge-facility','principal':q(427,5),'annual_rate':q(1,20),
                  'day_count':'ACT365_calendar','fee':q(0),'interest_cash_class':'operating'},
          'tax':{'rate':q(1,5),'method':'immediate_deductible'},
          'events':[{'kind':k,'at':t} for k,t in events]}
    # Explicit textual authoring, not a serializer applied to the typed body.
    text='''profile FundedYearInputsDraft/1;
name NorthstarFundedYear;
projection projection.stress7 {projection};
context Northstar DemoCorporate USD;
share 1/2;
source data/accounting-master/corporate-portable-20261015/portable-exchanges.json {source_hash};
assumption "{assumption}";
claim opening-ar receivable opening 35/1 10/1;
claim sales-ar receivable delivery 300/1 270/1;
claim opening-ap payable opening 30/1 0/1;
claim purchase-ap payable purchase 170/1 160/1;
facility bridge-facility 100/1 0/1 0/1;
loan bridge-facility 427/5 1/20 ACT365_calendar 0/1 operating;
tax 1/5 immediate_deductible;
event purchase 2025-01-02T09:00:00Z;
event delivery 2025-01-03T09:00:00Z;
event facility_draw 2025-01-04T11:00:00Z;
event supplier_payment 2025-01-04T12:00:00Z;
event collection 2025-01-05T09:00:00Z;
event facility_interest 2025-01-06T09:00:00Z;
event facility_repayment 2025-01-06T10:00:00Z;
event payroll 2025-01-07T09:00:00Z;
event plant_addition 2025-12-31T09:00:00Z;
event depreciation 2025-12-31T10:00:00Z;
event interest 2025-12-31T11:00:00Z;
event tax 2025-12-31T12:00:00Z;
event dividend 2025-12-31T13:00:00Z;
event close 2025-12-31T14:00:00Z;
'''.format(projection=projection,source_hash=source_hash,assumption=assumption)
    (OUT/'schema.json').write_text(json.dumps(schema(),indent=2)+chr(10))
    (OUT/'example.json').write_text(json.dumps(body,indent=2)+chr(10))
    (OUT/'example.accdsl').write_text(text)
    print(json.dumps({'created':names,'events':len(events),'claims':len(claims)}))


if __name__=='__main__': main()
