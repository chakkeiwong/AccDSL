from pathlib import Path
H=Path(__file__).resolve().parent;assert not (H/'advance.py').exists()
s=(H.parent/'prospective-policy-integration-20261027/advance.py').read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep('gap-prospective-integration-refresh-20261027','gap-policy-refinement-integration-refresh-20261027')
rep("NEXT='docs/plans/accounting-policy-domain-transport-20261027.md';DONE='docs/plans/accounting-prospective-policy-integration-20261027.md'","NEXT='docs/plans/accounting-two-decision-source-views-20261027.md';DONE='docs/plans/accounting-policy-domain-transport-20261027.md'")
rep("v['checks']==819","v['checks']==675")
rep("'5.37;806 pages;not_ready'","'5.38;810 pages;not_ready'")
rep("OLD.name=='gap-prospective-partial-refresh-20261027'","OLD.name=='gap-prospective-integration-refresh-20261027'")
rep("Version5.38 integrates prospective policy and supplied-partition evidence;5.37 sources retained.","Version5.39 integrates exact renaming/refinement;5.38 sources retained.")
rep("title='Protected prospective-policy manuscript integration'","title='Protected policy-refinement manuscript integration'")
rep('819 document checks preserve266 sources and261 evidence files;bounded author review;no repeated numerical credit or independent acceptance.','675 document checks preserve268 sources and121 evidence files;bounded author review;independent acceptance pending.')
needle="for row in packs['packages']:"
extra="""for folder,title,disposition in [('policy-domain-transport-20261027','Exact global policy-message renaming','22 comparisons,281 assertions,12 controls;full candidate permutation;not expansion.'),('policy-observation-refinement-20261027','Declared observation erasure and lifting','17 comparisons,360 assertions,10 controls;exact lift set and reached behavior comparisons.')]:
 evidence=H.parent/folder/'result.md'
 audit['successor_deltas'].insert(len(audit['successor_deltas'])-1,dict(id='',title=title,requirements=['MC03','MC05','MC11','MC12','MC13','MC18','MC24','MC25','MC26','MC28','MC33','MC34'],evidence=str(evidence.relative_to(R)),sha256=sha(evidence),current_disposition=disposition))
for i,item in enumerate(audit['successor_deltas']):item['id']='D'+str(i+1)
"""
rep(needle,extra+needle)
rep("Version5.38 integrates prospective policy and supplied transaction partition;independent acceptance pending.","Version5.39 integrates exact renaming and declared refinement;independent acceptance pending.")
rep('Execute accounting-policy-domain-transport-20261027.md;retain finite semantics and broader horizon/language residuals.','Execute accounting-two-decision-source-views-20261027.md;preserve fixed-input relation scope and broader horizons.')
rep("audit['successor_deltas'][:-1]==oa['successor_deltas']","audit['successor_deltas'][:-3]==oa['successor_deltas']")
rep('successor_deltas=91','successor_deltas=94')
rep("current_candidate='5.38;810 pages;not_ready'","current_candidate='5.39;812 pages;not_ready'")
rep('latest_result=result,current_program=DONE,full_gap_plan=DONE,','latest_result=result,latest_internal_result=str((H.parent/\'policy-observation-refinement-20261027/result.md\').relative_to(R)),latest_compression_result=str((H.parent/\'policy-observation-refinement-20261027/result.md\').relative_to(R)),policy_renaming_result=str((H.parent/\'policy-domain-transport-20261027/result.md\').relative_to(R)),policy_refinement_result=str((H.parent/\'policy-observation-refinement-20261027/result.md\').relative_to(R)),current_program=\'docs/plans/accounting-policy-refinement-integration-20261027.md\',full_gap_plan=\'docs/plans/accounting-policy-refinement-integration-20261027.md\',')
rep('Version5.38 integrates prospective policy and supplied transaction partition. Safe domain transport next;measured conversion-to-control locally evidence-blocked;all broad packages open.','Version5.39 integrates renaming/refinement. Joint two-decision source views next;measured conversion-to-control locally evidence-blocked;all packages open.')
rep("['Check safe policy-domain transport','Continue financing evidence','Continue broader language/source/reader acceptance work']","['Audit joint source views across two decisions','Continue financing evidence','Continue broader language/source/reader acceptance work']")
rep('**5.38**,810 main pages','**5.39**,812 main pages');rep('Simulation244 total/223 body pages','Simulation246 total/225 body pages')
rep("'Prospective message domains,partial-policy restrictions and supplied acquisition','partitions are integrated.819 document checks preserve266 sources and261 evidence'","'Exact message renaming and declared observation refinement are integrated.','675 document checks preserve268 sources and121 evidence'")
rep("('Version 5.37, 806 pages','Version 5.38, 810 pages'),('**241 pages**','**244 pages**'),('**220 body pages**','**223 body pages**'),('debt-exchange-integration-20261027/result.md','prospective-policy-integration-20261027/result.md')","('Version 5.38, 810 pages','Version 5.39, 812 pages'),('**244 pages**','**246 pages**'),('**223 body pages**','**225 body pages**'),('prospective-policy-integration-20261027/result.md','policy-refinement-integration-20261027/result.md')")
rep('Exact5.37 comparator and additive source transformation checked;bounded author review supports provisional5.38 only. No duplicate numerical credit;finance evidence plan,original obligations and all18 packages preserved.','Exact5.38 comparator and additive source transformation checked;bounded author review supports provisional5.39 only. Two previously uncredited methods plus one integration;finance plan andall18 packages preserved.')
rep('One integration delta. Independent acceptance and measured acquisition remain open;no requirement closure.','Two method deltas andone integration delta. Independent acceptance and measured acquisition remain open;no requirement closure.')
rep('Version5.38;all18 packages remain open.','Version5.39;all18 packages remain open.')
rep('.v538.tmp','.v539.tmp');rep('.v538-link','.v539-link')
(H/'advance.py').write_text(s);print('Created guarded5.39 advancement with three new deltas.')

