"""Prepare a new guarded integration advancement from the checked pattern."""
from pathlib import Path
H=Path(__file__).resolve().parent;out=H/'advance.py';assert not out.exists()
text=(H.parent/'acquisition-worked-integration-20261027/advance.py').read_text()
# Stage version replacements through a placeholder to avoid cascading.
text=text.replace('5.30','NEXT_VERSION').replace('5.29','5.30').replace('NEXT_VERSION','5.31')
changes=[
 ('gap-acquisition-worked-refresh-20261027','gap-intragroup-integration-refresh-20261027'),
 ('accounting-acquisition-intragroup-20261027.md','accounting-intragroup-carry-20261027.md'),
 ('accounting-acquisition-worked-integration-20261027.md','accounting-intragroup-integration-20261027.md'),
 ("v['checks']==628","v['checks']==669"),
 ('5.30;790 pages;not_ready','5.30;792 pages;not_ready'),
 ("OLD.name=='gap-acquisition-revision-refresh-20261027'","OLD.name=='gap-intragroup-realisation-refresh-20261027'"),
 ('complete synthetic acquisition, consideration and repaired revision explanations','full downstream inventory, explicit tax, legal journals and external-resale explanations'),
 ('Protected worked acquisition manuscript integration','Protected downstream inventory manuscript integration'),
 ('628 checks preserve 257 predecessor sources and 96 evidence files','669 checks preserve 258 predecessor sources and 135 evidence files'),
 ('Version 5.31 integrates the complete synthetic acquisition, consideration and repaired revision explanations','Version 5.31 integrates full downstream inventory, legal journals and external realisation'),
 ('Execute accounting-intragroup-carry-20261027.md: inspect tax authority, compare complete downstream credit/cash transfers and full elimination; then prior interests/debt conversion, upstream allocation, loss/ownership and general items.','Execute accounting-intragroup-carry-20261027.md: compare two-year closing/opening equity, acquisition-basis and tax carry with external resale; then upstream,prior interests/debt conversion,loss/ownership and general methods.'),
 ('cross_interface_challenges=63,successor_deltas=66','cross_interface_challenges=66,successor_deltas=69'),
 ("current_candidate='5.31;792 pages;not_ready'","current_candidate='5.31;794 pages;not_ready'"),
 ('Version 5.31 integrates checked acquisition worksheets, consideration and repaired revision views. Next: source-qualified intragroup elimination.','Version 5.31 integrates downstream inventory and external realisation. Next: audited two-year opening-equity and tax carry.'),
 ('Resolve conditional intragroup tax interface and compare full downstream credit/cash elimination','Compare complete two-year equity, inventory, acquired-basis and tax carry'),
 ('**5.31**, 792 main pages','**5.31**, 794 main pages'),
 ('**225 total / 206 body pages**','**229 total / 208 body pages**'),
 ('The complete synthetic acquisition worksheet, cash/new-parent-equity comparison\nand repaired revision views are integrated. 628 document checks preserve 257\npredecessor sources and 96 evidence files.','Full downstream elimination, explicit conditional tax, dated legal journals and\nexternal resale are integrated. 669 document checks preserve 258\npredecessor sources and 135 evidence files.'),
 ('Worked acquisition integrated','Downstream inventory integrated'),
 ("('Version 5.30, 790 pages','Version 5.31, 792 pages')","('Version 5.30, 792 pages','Version 5.31, 794 pages')"),
 ("('**223 pages**','**225 pages**')","('**225 pages**','**229 pages**')"),
 ("('**204 body pages**','**206 body pages**')","('**206 body pages**','**208 body pages**')"),
 ("('acquisition-design-rebase-20261027/result.md','acquisition-worked-integration-20261027/result.md')","('acquisition-worked-integration-20261027/result.md','intragroup-integration-20261027/result.md')"),
 ("('gap-acquisition-design-refresh-20261027/remaining-work.md','gap-intragroup-integration-refresh-20261027/remaining-work.md')","('gap-intragroup-realisation-refresh-20261027/remaining-work.md','gap-intragroup-integration-refresh-20261027/remaining-work.md')"),
 ('Full closure program after worked acquisition integration','Full closure program after downstream inventory integration'),
 ('Version 5.31 integrates worked acquisition companions. Next is source-qualified intragroup elimination','Version 5.31 integrates downstream and realisation companions. Next is two-year carry'),
 ('Tax authority is a dependency of the next financial unit.','Carried equity and recurring acquired-basis depreciation/tax are explicit dependencies of the next financial unit.'),
 ('Worked acquisition program refresh','Downstream inventory program refresh')]
for old,new in changes:
    if old not in text:
        # Already covered by an earlier wider exact replacement.
        if old.startswith('Version 5.31 integrates the complete synthetic'):continue
        raise AssertionError(old)
    text=text.replace(old,new)
out.write_text(text);print('Prepared new intragroup advancement driver.')
