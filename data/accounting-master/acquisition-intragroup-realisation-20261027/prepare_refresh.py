"""Create a new one-shot refresh; never rerun predecessor writers."""
from pathlib import Path
H=Path(__file__).resolve().parent;out=H/'refresh.py';assert not out.exists()
text=(H.parent/'acquisition-intragroup-20261027/refresh.py').read_text()
changes=[
 ("G=H.parent/'gap-intragroup-refresh-20261027'","G=H.parent/'gap-intragroup-realisation-refresh-20261027'"),
 ("NEXT='docs/plans/accounting-intragroup-realisation-20261027.md';OLDPLAN='docs/plans/accounting-acquisition-intragroup-20261027.md'","NEXT='docs/plans/accounting-intragroup-integration-20261027.md';OLDPLAN='docs/plans/accounting-intragroup-realisation-20261027.md'"),
 ("OLD.name=='gap-acquisition-worked-refresh-20261027'","OLD.name=='gap-intragroup-refresh-20261027'"),
 ('conditional downstream inventory companion awaits integration','conditional legal-journal and external-realisation companion awaits integration'),
 ('Full downstream elimination with explicit conditional tax','Dated legal journals and full downstream external realisation'),
 ('22 full cases,33 controls,648 assertions; full elimination and cash origins pass, unknown tax holds final report. Actual admission remains false.','66 full cases,24 controls,3015 assertions; full dated legal journals, worksheets and resale reports pass; actual admission remains false.'),
 ("[('Ownership-scaled elimination or assumed zero tax preserves internal profit','Compare full credit/cash accounts and recognised,unrecognised,unresolved tax; unknown tax must not select a final report.'),('Closing worksheet agreement is mistaken for complete legal history and external realisation','Add dated legal journals and a half-resold external inventory comparison with full tax, cash and owner/NCI attribution.')]","[('A same-year inventory method is reused as a next-year opening-equity reversal','Carry complete closing books, opening group adjustments and tax basis without replaying acquisition; compare next-year external resale.')]"),
 ('Selected downstream case checked; event trace and realisation remain next','Same-year dated trace and realisation checked; cross-year opening equity remains next'),
 ("fail['cross_interface'][:-2]","fail['cross_interface'][:-1]"),
 ('Conditional downstream transfer passes22 cases/648 assertions with full elimination, paired cash and explicit tax dispositions.','Dated legal journals and external resale pass66 cases/3015 assertions with exact full account/report comparisons and explicit tax dispositions.'),
 ('Execute accounting-intragroup-realisation-20261027.md: complete legal event journals and external resale; then upstream,prior interests/debt conversion,loss/ownership and general methods.','Integrate verified intragroup companions under accounting-intragroup-integration-20261027.md; then compare cross-year opening equity and retained-margin release before upstream and general methods.'),
 ('intragroup_result=result','intragroup_realisation_result=result'),
 ('Conditional downstream elimination checked; legal-event journals and external realisation next.','Dated legal journals and external realisation checked; manuscript integration next.'),
 ('Add complete dated legal journals and external inventory realisation','Integrate checked downstream and external-realisation explanations'),
 ('## Downstream inventory comparison checked','## External inventory realisation checked'),
 ('ConditionalDownstreamInventory/1 passes22 cases,33 controls,648 assertions.','ConditionalDownstreamRealisation/1 passes66 cases,24 controls,3015 assertions.'),
 ('Full elimination, cash origins and explicit tax dispositions are checked; actual','Dated legal journals, external cash and tax/owner/NCI effects are checked; actual'),
 ('Full closure program after downstream inventory comparison','Full closure program after external inventory realisation'),
 ('complete downstream worksheets do not establish complete legal-event journals or external resale.','same-year complete legal-event journals and external resale do not establish next-year opening equity and retained-margin release.'),
 ('Continue the planned discriminating realisation comparison','Integrate the checked comparison, then continue the planned two-year comparison'),
 ('One checked downstream delta and two interface challenges added.','One checked realisation delta and one cross-year interface challenge added.')]
for old,new in changes:
    assert old in text,old;text=text.replace(old,new)
out.write_text(text);print('Prepared new realisation refresh writer.')
