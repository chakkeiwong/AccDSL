"""Prepare the worked example against the checked live acquisition baseline."""
from pathlib import Path
import re,json
H=Path(__file__).resolve().parent;R=H.parents[2]
assert not (H/'integrate.py').exists()
a=json.loads((R/'scripts/accounting_master_catalog.json').read_text())['active_execution_note']
assert a['current_candidate']=='5.29;790 pages;not_ready'
p=H/'acquisition-worked.tex';text=p.read_text()
text=re.sub(r'\b(cash|capital|equipment|payables|profit|pays|investment|equity|depreciation|adjustment|liability|assets|liabilities|NCI|expense|payable|consideration|revenue|from|to|receipt|on|at|of|the|stipulated)(?=\d)',r'\1 ',text)
text=re.sub(r'(\d)(January|February|July)',r'\1 \2',text)
text=re.sub(r'(January|February|July)(\d)',r'\1 \2',text)
text=re.sub(r'(?<!\s)(\$[^$]+\$)',r' \1',text)
text=text.replace('disclosures need','disclosures need').replace('4 assets','4 assets')
p.write_text(text)
code=(H.parent/'acquisition-design-rebase-20261027/integrate.py').read_text()
for old,new in [
 ('manuscript-family-policies-v528-20261027','manuscript-acquisition-design-v529-20261027'),
 ('manuscript-acquisition-design-v529-20261027\'\nPDFS','manuscript-acquisition-worked-v530-20261027\'\nPDFS'),
 ('5e7f200137a1639e15b054bda26e55880f296eda2ec4106ce720e79f86dfe133',a['current_pdf_sha256']),
 ('95e3be3f29067a108427f80bc132e207e711183bb784c5542777b78aca581284',a['standalone_pdf_sha256']),
 ("t.count('Version 5.28')==1;return t.replace('Version 5.28','Version 5.29')","t.count('Version 5.29')==1;return t.replace('Version 5.29','Version 5.30')"),
 ("startswith('5.28;')","startswith('5.29;')"),
 ("'Version 5.29' in texts[0]","'Version 5.30' in texts[0]"),
 ('acquisition-design.tex','acquisition-worked.tex'),
 ('simulation/acquisition-design','simulation/acquisition-worked'),
 ("if n=='references.bib':return t+'\\n'+(H/'references-additions.bib').read_text()","if n=='references.bib':return t"),
 (",'references.bib']", "]"),
 ("['acquisition-worked.tex','references-additions.bib','reader-plan.md']","['acquisition-worked.tex','reader-plan.md']"),
 ("['acquisition-period-authority-20261026','acquisition-symbolic-20261027']","['acquisition-worksheet-20261027','acquisition-consideration-20261027','acquisition-revision-prefix-repair-20261027']"),
 ("[('acquisition-period-authority-20261026','verification-attempt-03'),('acquisition-symbolic-20261027','attempt-01')]","[('acquisition-worksheet-20261027','attempt-01'),('acquisition-consideration-20261027','attempt-01'),('acquisition-revision-prefix-repair-20261027','attempt-01')]"),
 ('docs/plans/accounting-acquisition-design-integration-20261027.md','docs/plans/accounting-acquisition-worked-integration-20261027.md'),
 ("'Suppose the financing arrangement eventually gives the creditor control of the debtor.'","'The unknown amounts in the preceding section protect the real financing question from invented measurements.'"),
 ("ending='they do not replace it.'","ending='without leaking pre-control activity or losing the acquired measurement basis.'"),
 ("['previously held equity','one-year maximum','cash','measurement','negative','prior debt','No'] if x!='No'","['pre-control','discovery','noncash','negative','original','tax']")]:
    assert old in code,old;code=code.replace(old,new)
(H/'integrate.py').write_text(code)
print('Prepared worked-example script and spacing-normalized prose.')
