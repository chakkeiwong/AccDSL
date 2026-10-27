"""Preserve concurrent family-policy edition and the earlier acquisition candidate."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[2];OLD=H.parent/'acquisition-design-integration-20261027'
assert not (H/'integrate.py').exists()
a=json.loads((R/'scripts/accounting_master_catalog.json').read_text())['active_execution_note']
assert a['current_candidate']=='5.28;786 pages;not_ready'
for name in ['acquisition-design.tex','references-additions.bib','reader-plan.md']:(H/name).write_bytes((OLD/name).read_bytes())
code=(OLD/'integrate.py').read_text()
for old,new in [
 ('manuscript-temporal-group-v527-20261027','manuscript-family-policies-v528-20261027'),
 ('manuscript-acquisition-design-v528-20261027','manuscript-acquisition-design-v529-20261027'),
 ('4e49b289233ab977352d8ca384ce18d502eabbee7b44d48b1f34fb08f732a66c',a['current_pdf_sha256']),
 ('aec5eac1c61ed048f64dd7c4a06227d788959ac4324c53750f535ca04f678fbc',a['standalone_pdf_sha256']),
 ("t.count('Version 5.27')==1;return t.replace('Version 5.27','Version 5.28')","t.count('Version 5.28')==1;return t.replace('Version 5.28','Version 5.29')"),
 ("startswith('5.27;')","startswith('5.28;')"),
 ("'Version 5.28' in texts[0]","'Version 5.29' in texts[0]"),
 ("starts=[i+1 for i,t in enumerate(texts) if title in t and len(t)>1000]","starts=[i+1 for i,t in enumerate(texts) if 'Suppose the financing arrangement eventually gives the creditor control of the debtor.' in t]")]:
    assert old in code,old;code=code.replace(old,new)
(H/'integrate.py').write_text(code)
(H/'recovery.md').write_text('# Rebase onto concurrent5.28\n\n27 October2026. The acquisition-only5.28 candidate based on5.27 passed756 structural checks and bounded render review but was never advanced. Concurrent family-policy work now governs5.28. Preserve its255 source baseline plus added common-policy chapter and independent observation-map plan. The unchanged acquisition section is rebased into5.29 with new source/evidence/build verification. The prior successful preparation/build/check writers do not rerun. The title-page locator is repaired before this new candidate by using unique body prose. No financial claim or source interpretation changes.\n')
print('Prepared new rebase scripts and unchanged prose; no live controls changed.')
