from pathlib import Path
H=Path(__file__).resolve().parent;out=H/'refresh.py';assert not out.exists()
text=(H.parent/'acquisition-intragroup-realisation-20261027/refresh.py').read_text()
changes=[
 ('gap-intragroup-realisation-refresh-20261027','gap-intragroup-carry-refresh-20261027'),
 ("NEXT='docs/plans/accounting-intragroup-integration-20261027.md';OLDPLAN='docs/plans/accounting-intragroup-realisation-20261027.md'","NEXT='docs/plans/accounting-intragroup-carry-integration-20261027.md';OLDPLAN='docs/plans/accounting-intragroup-carry-20261027.md'"),
 ("OLD.name=='gap-intragroup-refresh-20261027'","OLD.name=='gap-intragroup-integration-refresh-20261027'"),
 ('5.30;792 pages;not_ready','5.31;794 pages;not_ready'),
 ('Version 5.30','Version 5.31'),('version5.30','version5.31'),
 ('792 main pages; 225 total / 206 body','794 main pages; 229 total / 208 body'),
 ('Dated legal journals and full downstream external realisation','Complete two-year downstream opening bridge and retained-margin release'),
 ('66 full cases,24 controls,3015 assertions; full dated legal journals, worksheets and resale reports pass; actual admission remains false.','14 full cases,27 controls,598 assertions; full closed openings,bridge,journals,group reports and negative NCI profit pass; actual admission remains false.'),
 ("[('A same-year inventory method is reused as a next-year opening-equity reversal','Carry complete closing books, opening group adjustments and tax basis without replaying acquisition; compare next-year external resale.')]","[('A downstream attribution or unchanged opening is silently applied to an upstream sale','Acquire subsidiary inventory externally after control,then compare full upstream unrealised/realised profit and NCI without altering acquisition measurements.')]"),
 ('Same-year dated trace and realisation checked; cross-year opening equity remains next','Selected downstream carry checked; upstream attribution remains next'),
 ('Dated legal journals and external resale pass66 cases/3015 assertions with exact full account/report comparisons and explicit tax dispositions.','Two-year downstream carry passes14 cases/598 assertions with full closed opening/group bridge,recurring depreciation/tax and negative NCI attribution.'),
 ('Integrate verified intragroup companions under accounting-intragroup-integration-20261027.md; then compare cross-year opening equity and retained-margin release before upstream and general methods.','Integrate checked carry under accounting-intragroup-carry-integration-20261027.md; then compare post-control upstream trade and NCI with independent full accounts.'),
 ('intragroup_realisation_result=result','intragroup_carry_result=result'),
 ('Dated legal journals and external realisation checked; manuscript integration next.','Two-year opening carry and retained-margin release checked; manuscript integration next.'),
 ('Integrate checked downstream and external-realisation explanations','Integrate checked two-year opening carry and margin release'),
 ('## External inventory realisation checked','## Two-year downstream carry checked'),
 ('ConditionalDownstreamRealisation/1 passes66 cases,24 controls,3015 assertions.','ConditionalDownstreamCarry/1 passes14 cases,27 controls,598 assertions.'),
 ('Dated legal journals, external cash and tax/owner/NCI effects are checked; actual','Closed opening accounts,recurring depreciation/tax and negative NCI are checked; actual'),
 ('Full closure program after external inventory realisation','Full closure program after two-year downstream carry'),
 ('same-year complete legal-event journals and external resale do not establish next-year opening equity and retained-margin release.','downstream two-year carry does not establish upstream attribution or actual continuing schedules/control.'),
 ('Integrate the checked comparison, then continue the planned two-year comparison','Integrate checked carry,then compare upstream with an independent acquisition/post-control boundary'),
 ('One checked realisation delta and one cross-year interface challenge added.','One checked carry delta and one upstream interface challenge added.')]
for old,new in changes:assert old in text,old;text=text.replace(old,new)
out.write_text(text);print('Prepared separate carry refresh writer.')
