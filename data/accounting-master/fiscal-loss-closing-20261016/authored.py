"""Freeze successor company and loss targets before calculation."""
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PACKET='data/accounting-master/company-composition-20261016/attempt-03/portable-exchanges.json'

def amounts(**items):return {k:str(Q(str(v))) for k,v in items.items()}
def expected(pcash,ppe,dta,pcarry,pprofit,pret,scash,taxpay,sequity,sprofit,sret,gcash,gequity,gprofit,parent,nci,parentprofit,eps,gret,loss,used,expired,rate_effect,unrec_used):
    return dict(P=amounts(cash=pcash,ppe=ppe,dta=dta,equity=pcarry,profit=pprofit,retained=pret),
        S=amounts(cash=scash,current_tax_payable=taxpay,equity=sequity,profit=sprofit,retained=sret),
        group=amounts(cash=gcash,equity=gequity,profit=gprofit,parent_equity=parent,nci=nci,parent_profit=parentprofit,
            basic_eps=eps,diluted_eps=eps,parent_retained=gret),
        loss=amounts(remaining=loss,used=used,expired=expired,rate_effect=rate_effect,unrecognised_used_benefit=unrec_used))

def main():
    packet=json.loads((ROOT/PACKET).read_text());state=packet['record_registry'][packet['states'][-1]['digest']]['body']
    opening=dict(P=amounts(cash='491.5',ppe=80,investment=100,capital=600,original_equity=10,retained='61.5'),
        S=amounts(cash='152.5',capital=100,retained='52.5'),group=amounts(equity=724,parent_equity='708.75',nci='15.25',parent_retained='106.65',ownership_reserve='-7.9'))
    findings=dict(continued_control=True,unchanged_ownership_policies_currency=True,outside_basis_exception=True,
        complete_book_tax_inventory=True,book_tax_depreciation_equal=True,no_group_relief_or_offset_right=True,
        no_other_operations_or_instruments=True,all_new_origins_profit=True,loss_usable_only_by_P=True,
        no_carryback=True,short_period_tax_law_admitted=True,all_cash_costs_expensed=True)
    def period(id,start,end,receipt,cost,dep,srate,stax,capacity):
        return dict(id=id,start=start,end_exclusive=end,information_date=end,findings=deepcopy(findings),
            P=dict(receipts=receipt,cash_costs=cost,depreciation=dep,tax_paid='0'),
            S=dict(receipts='20',cash_costs='0',depreciation='0',tax_paid=stax),
            tax=dict(current_rate=srate,recovery_rate=srate,law_date=start,effective_from=start,law_id='synthetic-rate-'+srate,
                enacted=True,complete_fiscal_terms=True),
            recovery=dict(supported_loss=capacity,assessment_complete=True,convincing_next_period_evidence=capacity!='0',
                evidence_id=id+'-recovery',taxable_entity='P',authority='P-tax',usable_before_expiry=True))
    periods=[period('stub2026','2026-01-01','2026-07-01','20','110','10','1/4','0','40'),
        period('fy2027','2026-07-01','2027-07-01','100','20','20','3/10','5','30'),
        period('fy2028','2027-07-01','2028-07-01','60','20','20','3/10','12','0')]
    base=dict(wire='FiscalLossClosing/1',operation='report',base_packet=PACKET,
        base_sha256=hashlib.sha256((ROOT/PACKET).read_bytes()).hexdigest(),opening=opening,
        ordinary_shares='10',share_findings=dict(complete_history=True,unchanged_ordinary_shares=True,no_potential_shares=True),
        calendar=dict(stub_reason='Align reporting year with operating cycle',short_comparatives_not_annualised=True),
        loss_expiry_exclusive='2028-07-01',periods=periods)
    targets=[expected('401.5',70,10,'581.5',-90,'-28.5','172.5',5,'167.5',15,'67.5',574,649,-75,'632.25','16.75','-76.5','-7.65','30.15',100,0,0,0,0),
        expected('481.5',50,9,'640.5',59,'30.5','187.5',6,'181.5',14,'81.5',669,722,73,'703.85','18.15','71.6','7.16','101.75',40,60,0,-2,6),
        expected('521.5',30,0,'651.5',11,'41.5','195.5',0,'195.5',14,'95.5',717,747,25,'727.45','19.55','23.6','2.36','125.35',0,20,20,0,0)]
    cases=[dict(id='supported-recovery',request=deepcopy(base),expected=targets)]
    n=deepcopy(base)
    for p in n['periods']:p['recovery'].update(supported_loss='0',convincing_next_period_evidence=False)
    cases.append(dict(id='no-deferred-asset',request=n,expected=[
        expected('401.5',70,0,'571.5',-100,'-38.5','172.5',5,'167.5',15,'67.5',574,639,-85,'622.25','16.75','-86.5','-8.65','20.15',100,0,0,0,0),
        expected('481.5',50,0,'631.5',60,'21.5','187.5',6,'181.5',14,'81.5',669,713,74,'694.85','18.15','72.6','7.26','92.75',40,60,0,0,18),
        expected('521.5',30,0,'651.5',20,'41.5','195.5',0,'195.5',14,'95.5',717,747,34,'727.45','19.55','32.6','3.26','125.35',0,20,20,0,6)]))
    n=deepcopy(base)
    for p in n['periods'][1:]:p['tax'].update(current_rate='1/4',recovery_rate='1/4',law_id='synthetic-rate-1/4')
    n['periods'][2]['S']['tax_paid']='10'
    cases.append(dict(id='constant-quarter-rate',request=n,expected=[targets[0],
        expected('481.5',50,'7.5',639,'57.5',29,'187.5',5,'182.5',15,'82.5',669,'721.5','72.5','703.25','18.25',71,'7.1','101.15',40,60,0,0,5),
        expected('521.5',30,0,'651.5','12.5','41.5','197.5',0,'197.5',15,'97.5',719,749,'27.5','729.25','19.75',26,'2.6','127.15',0,20,20,0,0)]))
    n=deepcopy(base);n['periods'][1]['recovery']['supported_loss']='10'
    cases.append(dict(id='reduced-recovery',request=n,expected=[targets[0],
        expected('481.5',50,3,'634.5',53,'24.5','187.5',6,'181.5',14,'81.5',669,716,67,'697.85','18.15','65.6','6.56','95.75',40,60,0,-2,6),
        expected('521.5',30,0,'651.5',17,'41.5','195.5',0,'195.5',14,'95.5',717,747,31,'727.45','19.55','29.6','2.96','125.35',0,20,20,0,3)]))
    n=deepcopy(base);n['periods']=n['periods'][:1]
    cases.append(dict(id='stub-only',request=n,expected=targets[:1]))
    offsets=[]
    def offset(id,category,other,authority,right,intent,future,expected):
        offsets.append(dict(id=id,request=dict(category=category,asset='10',liability='7',asset_entity='P',liability_entity=other,
            same_authority=authority,legal_current_offset_right=right,intends_net_or_simultaneous=intent,
            each_future_recovery_period=future),expected=expected))
    offset('current-net','current','P',True,True,True,True,dict(asset='3',liability='0',offset=True))
    offset('current-no-intent','current','P',True,True,False,True,dict(asset='10',liability='7',offset=False))
    offset('deferred-same-entity','deferred','P',True,True,False,False,dict(asset='3',liability='0',offset=True))
    offset('deferred-group-no-right','deferred','S',True,False,True,True,dict(asset='10',liability='7',offset=False))
    offset('deferred-group-net','deferred','S',True,True,True,True,dict(asset='3',liability='0',offset=True))
    offset('deferred-missing-period-intent','deferred','S',True,True,True,False,dict(asset='10',liability='7',offset=False))
    out=OUT/'authored-cases.json';assert not out.exists();out.write_text(json.dumps(dict(cases=cases,offsets=offsets),indent=2)+'\n')
    paths=[out,Path(__file__).resolve(),OUT/'source-reading.md',ROOT/'docs/plans/accounting-fiscal-loss-closing-20261016.md',ROOT/PACKET,
        ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
        ROOT/'data/accounting-master/company-composition-20261016/semantic-contract.md']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]),indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),offsets=len(offsets),protected_files=len(paths))))

if __name__=='__main__':main()
