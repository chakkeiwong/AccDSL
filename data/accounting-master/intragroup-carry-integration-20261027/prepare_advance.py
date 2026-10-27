"""Prepare a new one-shot writer; never execute a predecessor writer."""
from pathlib import Path
H=Path(__file__).resolve().parent
p=H/'advance.py'
assert not p.exists()
s=(H.parent/'intragroup-integration-20261027/advance.py').read_text()
changes={
'5.31':'5.33','5.30':'5.32',
'gap-intragroup-integration-refresh-20261027':'gap-intragroup-carry-integration-refresh-20261027',
'gap-intragroup-realisation-refresh-20261027':'gap-partial-frontier-policy-refresh-20261027',
'accounting-intragroup-carry-20261027.md':'accounting-intragroup-upstream-20261027.md',
'accounting-intragroup-integration-20261027.md':'accounting-intragroup-carry-integration-20261027.md',
'intragroup-integration-20261027/result.md':'intragroup-carry-integration-20261027/result.md',
'acquisition-worked-integration-20261027/result.md':'observation-frontier-rebase-20261027/result.md',
'792':'798','794':'800','669':'685','258':'261','135 evidence':'145 evidence',
'225 pages':'233 pages','229 pages':'235 pages','206 body':'212 body','208 body':'214 body',
'**229 total / 214 body':'**235 total / 214 body',
'cross_interface_challenges=66,successor_deltas=69':'cross_interface_challenges=75,successor_deltas=75',
'Protected downstream inventory manuscript integration':'Protected two-year inventory carry manuscript integration',
'full downstream inventory, explicit tax, legal journals and external-resale explanations':'closed opening equity, carried inventory margin and recurring equipment/tax explanations',
'the full downstream inventory, explicit tax, legal journals and external-resale explanations':'closed opening equity, carried inventory margin and recurring equipment/tax explanations',
'Full downstream elimination, explicit conditional tax, dated legal journals and\nexternal resale are integrated.':'Closed opening equity, carried inventory margin and recurring equipment/tax\nare integrated. Negative NCI profit and the concurrent observation/frontier work are preserved.',
'Downstream inventory integrated':'Two-year inventory carry integrated',
'downstream inventory integration':'two-year inventory carry integration',
'downstream and realisation companions. Next is two-year carry':'two-year inventory carry. Next is upstream attribution',
'downstream inventory and external realisation. Next: audited two-year opening-equity and tax carry.':'two-year inventory carry. Next: audited upstream inventory and NCI attribution.',
'compare two-year closing/opening equity, acquisition-basis and tax carry with external resale; then upstream,prior interests/debt conversion,loss/ownership and general methods.':'compare complete upstream journals, supplier cash, group elimination and NCI attribution; then prior interests/debt conversion,loss/ownership and general methods.',
'Integrate verified intragroup and independent observation-map companions':'Integrate verified finance and independent partial/prospective-policy companions',
'Compare complete two-year equity, inventory, acquired-basis and tax carry':'Compare upstream inventory, external supplier cash and NCI attribution',
'Independent observation-map fields':'Independent partial/prospective-policy fields',
'Carried equity and recurring acquired-basis depreciation/tax are explicit dependencies of the next financial unit.':'Upstream seller attribution and external supplier cash are explicit dependencies of the next financial unit.',
'downstream inventory, explicit tax, legal journals and external-resale explanations':'two-year inventory carry and recurring depreciation/tax explanations',
}
for old,new in changes.items():
    if old not in s:
        if old.startswith('the full downstream') or old.startswith('downstream inventory, explicit'):continue
        raise AssertionError('missing template anchor:'+old)
    s=s.replace(old,new)
# Current README follows the concurrent observation/frontier integration.
s=s.replace("('Version 5.32, 798 pages','Version 5.33, 800 pages')", "('Version 5.32, 798 pages','Version 5.33, 800 pages')")
s=s.replace("'Continue independent observation-map, recovery and acceptance work'", "'Continue independent partial/prospective-policy, recovery and acceptance work'")
s=s.replace("title='Protected two-year", "title='Protected two-year")
compile(s,str(p),'exec')
p.write_text(s)
print('Prepared new guarded advancement; predecessor writer unchanged.')
