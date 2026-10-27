"""Adapt the verified carry mechanism with explicit upstream journal changes."""
from pathlib import Path
H=Path(__file__).resolve().parent;p=H/'reference.py';assert not p.exists()
s=(H.parent/'acquisition-intragroup-carry-20261027/reference.py').read_text()
replacements=[
('acquisition-intragroup-realisation-20261027','acquisition-intragroup-upstream-20261027'),
('ConditionalDownstreamCarry/1','ConditionalUpstreamCarry/1'),
('conditional_realisation_worksheet','conditional_upstream_worksheet'),
("bp=p['prior_request']['payload']['predecessor_request']['payload']","bp=p['prior_request']['payload']"),
('external-year2-S-X','external-year2-P-X'),
('supplied_same_rates_recoverability_and_downstream_allocation','supplied_same_rates_recoverability_and_upstream_allocation'),
("h.need(bp['tax']['recognition']=='stipulated_recoverable','selected_tax_opening')","recognised=bp['tax']['recognition']=='stipulated_recoverable'\n        reversal=F(5,2)*sold if recognised else F(0)"),
("{'S.cash':40*sold,'S.merchandise_revenue':-40*sold,'S.cost_of_sales':30*sold,'S.inventory':-30*sold}","{'P.cash':40*sold,'P.merchandise_revenue':-40*sold,'P.cost_of_sales':30*sold,'P.inventory':-30*sold}"),
("{'S.current_tax_expense':F(5,2)*sold,'S.current_tax_payable':-F(5,2)*sold}","{'P.current_tax_expense':F(5,2)*sold,'P.current_tax_payable':-F(5,2)*sold}"),
("{'S.inventory':10*sold,'S.cost_of_sales':-10*sold},'parent_owners','Release carried downstream inventory adjustment'","{'P.inventory':10*sold,'S.cost_of_sales':-10*sold},'subsidiary_ordinary_rights','Release carried upstream inventory adjustment'"),
("{'group.inventory_deferred_tax_asset':-F(5,2)*sold,'P.inventory_tax_reversal_expense':F(5,2)*sold},'parent_owners'","{'group.inventory_deferred_tax_asset':-reversal,'S.inventory_tax_reversal_expense':reversal},'subsidiary_ordinary_rights'"),
('subsidiary=F(15,2)*sold-17','subsidiary=10*sold-reversal-17'),
('inventory_deferred_tax_asset=F(5,2)*(1-earlier-sold)','inventory_deferred_tax_asset=F(5,2)*(1-earlier-sold) if recognised else F(0)'),
("dict(entity='S',counterparty='X'","dict(entity='P',counterparty='X'"),
('upstream_multi_lot_impairment_fx_ownership','multi_lot_impairment_fx_ownership'),
]
for old,new in replacements:assert old in s,old;s=s.replace(old,new)
compile(s,str(p),'exec');p.write_text(s);print('Prepared explicit upstream carry candidate.')
