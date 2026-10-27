"""Record rebased review and prepare guarded additive control advancement."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[2];OLD=H.parent/'acquisition-design-integration-20261027'
v=json.loads((H/'verification.json').read_text());assert v['status']=='PASS'
assert not (H/'result.md').exists()
review=(OLD/'author-review.md').read_text()
review=review.replace('Main physical pages1 and220–224; simulation pages1 and211–215','Main physical pages1 and223–227; simulation pages1 and214–218').replace('Both covers show5.28','Both covers show5.29')
review+='\nRebase review: all listed5.29 pages and covers were freshly viewed. The acquisition prose is byte-identical to the previously reviewed candidate; concurrent5.28 temporal/common-policy sources are protected. The new unique-prose locator selects the correct pages directly. The older locator defect remains historical evidence, not a defect in this candidate.\n'
(H/'author-review.md').write_text(review)
text=(OLD/'result.md').read_text()
for a,b in [('Version5.28 candidate has787 main pages and220 total/201 body','Version5.29 candidate has790 main pages and223 total/204 body'),('pass756 document checks','pass758 document checks'),('preserving255 predecessor','preserving256 predecessor'),('Retain5.28','Retain5.29'),('cab96861a1251e156858a365d3264aed82ff6855675b1a78f55048cdddfe30c1',v['documents'][0]['sha256']),('eff933b5020815f8cb0b0c9dd0ffe9d5d0208ee66a15907908b4e6d3e9116263',v['documents'][1]['sha256'])]:
    assert a in text,a;text=text.replace(a,b)
text+='\nConcurrent baseline: the first acquisition-only5.28 candidate was never advanced. This5.29 successor preserves the live family-policy5.28 edition and its independent observation-map plan. Original successful attempts remain intact.\n'
(H/'result.md').write_text(text)
code=(H.parent/'acquisition-progress-20261027/refresh.py').read_text()
code=code.replace("G=H.parent/'gap-acquisition-authority-refresh-20261027'","G=H.parent/'gap-acquisition-design-refresh-20261027'")
code=code.replace("PLAN='docs/plans/accounting-acquisition-symbolic-20261027.md'","PLAN='docs/plans/accounting-acquisition-worksheet-20261027.md'")
code=code.replace("startswith('5.27;')","startswith('5.28;')").replace("a['active_work_plan']=='docs/plans/accounting-acquisition-period-authority-20261026.md'","a['active_work_plan']=='docs/plans/accounting-acquisition-symbolic-20261027.md'")
code=code.replace("OLD.name=='gap-temporal-group-refresh-20261027'","OLD.name=='gap-family-policy-refresh-20261027'")
code=code.replace("audit['baseline']='Version 5.27 temporal/group integration preserved; the dated acquisition-authority companion awaits integration.'","audit['baseline']='Version5.29 preserves5.28 family policies and integrates dated acquisition authority and symbolic amount dependencies.'")
start=code.index('items=[');end=code.index('\nfor title,p,scope in items:',start)
code=code[:start]+"items=[('Conditional acquisition amount dependencies','data/accounting-master/acquisition-symbolic-20261027/result.md','25 cases,21 refusals,505 assertions; unknown amounts remain symbols and no report is authorized.'),('Protected acquisition design integration',str((H/'result.md').relative_to(R)),'5.29 preserves256 predecessor sources and227 evidence files;758 checks and bounded author review; independent acceptance pending.')]"+code[end:]
code=code.replace("audit['successor_deltas'][:-1]","audit['successor_deltas'][:-2]")
code=code.replace("('A debt claim is used as previously held equity or a missing acquisition measurement is replaced by a face value','Keep T/Q/P/A/L separately typed and unresolved; inspect pre-existing relationships and consideration before lowering.',AUTH+'/result.md')","('Balanced symbolic acquisition expressions are treated as a complete measured group worksheet','Require identified item-level measurements and full independently authored account,adjustment and report comparisons.','data/accounting-master/acquisition-symbolic-20261027/result.md')")
code=code.replace("Dated acquisition requirements now retain unknown measurements and inspected authority alternatives;13 PDFs pass242 identity/anchor checks.","Symbolic acquisition dependencies pass25 cases/505 assertions; the dated authority and conditional expressions are integrated in5.29.")
code=code.replace("Execute accounting-acquisition-symbolic-20261027.md; then complete supported acquisition measurements and independent full worksheet/report comparisons, including NCI, post-control results and cash perimeter.","Execute accounting-acquisition-worksheet-20261027.md with independently authored full accounts, adjustments and reports; then extend noncash/prior-interest/loss/revision branches and actual admission.")
code=code.replace("The checked acquisition-authority companion awaits integration into a successor to5.27; the group-scope argument is already integrated.","Version5.29 integrates the dated acquisition-authority and unknown-amount argument while preserving5.28 common policies.")
code=code.replace('Version5.27 remains governing','Version5.29 remains governing')
code=code.replace('Candidate5.27','Candidate5.29').replace('Preserve5.27','Preserve5.29').replace('Version5.27 unchanged','Version5.29 integrated')
code=code.replace('One checked companion delta and one interface challenge are added.','Two checked deltas and one interface challenge are added.')
code=code.replace('No new manuscript integration or accounting admission is implied.','The checked acquisition explanation is integrated; no accounting admission follows.')
code=code.replace("if row['id']=='W17':","if row['id']=='W17':")
code=code.replace("latest_internal_result=AUTH+'/result.md',latest_financing_result=AUTH+'/result.md'","latest_internal_result='data/accounting-master/acquisition-symbolic-20261027/result.md',latest_financing_result='data/accounting-master/acquisition-symbolic-20261027/result.md'")
code=code.replace("current_internal_status='Version5.27 preserved with group scope integrated. Dated acquisition-authority companion checked; symbolic acquisition dependencies next. Actual admission and full reports remain open.'","current_internal_status='Version5.29 preserves family-policy work and integrates dated authority/symbolic acquisition dependencies. Item-level worksheet comparison is next; actual accounting admission remains open.'")
code=code.replace("originals=[deepcopy(cat),deepcopy(np)]","""v=j(H/'verification.json');assert v['status']=='PASS'
T=R/j(H/'source-preservation.json')['target']
for doc in v['documents']:assert digest(T/(doc['document']+'.pdf'))==doc['sha256']
updates.update(current_candidate='5.29;790 pages;not_ready',latest_result=str((H/'result.md').relative_to(R)),current_program='docs/plans/accounting-acquisition-design-integration-20261027.md',full_gap_plan='docs/plans/accounting-acquisition-design-integration-20261027.md',current_pdf=str((T/'accounting-product-proposal.pdf').relative_to(R)),current_pdf_sha256=v['documents'][0]['sha256'],standalone_pdf=str((T/'simulation-foundations.pdf').relative_to(R)),standalone_pdf_sha256=v['documents'][1]['sha256'])
originals=[deepcopy(cat),deepcopy(np)]""")
code=code.replace("+[GROUP+'/result.md',AUTH+'/result.md']","+[GROUP+'/result.md',AUTH+'/result.md','data/accounting-master/acquisition-symbolic-20261027/result.md']")
code=code.replace("'Preserve unknowns in conditional symbolic acquisition expressions'","'Compare item-level acquisition worksheets and full reports against independent expectations'")
code=code.replace('Governing candidate **5.27**,783 main pages','Governing candidate **5.29**,790 main pages').replace('**216 total/197 body pages**','**223 total/204 body pages**')
code=code.replace('Stable PDF/TeX links unchanged.','Stable PDF/TeX links select the protected acquisition successor.')
code=code.replace('Version5.27 preserves temporal information families and integrates group scope:','Version5.29 preserves temporal families/common policies and integrates acquisition design:')
code=code.replace('New checked companion, awaiting manuscript integration:','Integrated dated authority and symbolic companions:')
code=code.replace('- {AUTH}/result.md:13 primary PDFs,242 checks,67 protected files.','- {AUTH}/result.md:13 primary PDFs,242 checks,67 protected files.\n- data/accounting-master/acquisition-symbolic-20261027/result.md:25 cases,21 refusals,505 assertions.')
code=code.replace('Version5.29 remains governing:783 main pages;216 total/197 body simulation pages;','Version5.29 now governs:790 main pages;223 total/204 body simulation pages;')
code=code.replace('not_ready. Group scope is integrated; the dated authority audit passes242\nchecks over13 PDFs and awaits manuscript integration.','not_ready. Dated acquisition authority and symbolic dependencies are integrated;\n25 cases/505 assertions and758 document checks preserve the inspected boundaries.')
code=code.replace('Active financing plan: {PLAN}.','Active financing plan: {PLAN}.')
needle="for p,s in new.items():put(R/p,s)"
code=code.replace(needle,"""for p,s in new.items():put(R/p,s)
for p in links:
    name='simulation-foundations' if 'simulation' in p else 'accounting-product-proposal'
    ext='.pdf' if p.endswith('.pdf') else '.tex';target=T/(name+ext)
    temp=(R/p).with_name(Path(p).name+'.acquisition-link');assert not temp.exists()
    temp.symlink_to(os.path.relpath(target,(R/p).parent));os.replace(temp,R/p)
    links[p]=str(target)""")
code=code.replace("digest(R/a[p])==old[k]","digest(R/a[p])==a[k]")
(H/'advance.py').write_text(code)
print('Rebased review/result and guarded advancement script prepared; not executed.')
