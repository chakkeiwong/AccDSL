from pathlib import Path
HERE=Path(__file__).resolve().parent
text=(HERE.parent/'complete-claims-integration-20261026/advance.py').read_text()
start=text.index("note=f'''");end=text.index('proposed={}',start)
note="""note=f'''## Current governing candidate — Version 5.12 — 26 October 2026

Version 5.12 is the 728-page governing design candidate, not_ready. The nested
invariant source reader now preserves quoted Unicode separator data. Eight full
programs/54 commands and 32 prior controls remain exact; nine additional cases
reproduce and repair the defect. The run passes 41 controls/2,782 assertions
with 584 protected files. Financial evaluators are unchanged; native lifecycle
and builder callbacks remain disabled. All 222 predecessor manuscript sources
are protected under three named edits. The 26 simulation chapters and standalone
Version 5.5 (171 pages/155 body pages) remain exact. No new warnings; cover and
pages 692–696 inspected. All 53 obligations, six interactions and 46 operations
remain; no whole requirement closes. S1–S5 partial, S6 held, E3 deferred.
PDF: {v['pdf']}
SHA256: {v['pdf_sha256']}.
Result: {result}.
Next plan: {plan}.

'''
"""
text=text[:start]+note+text[end:]
start=text.index("remaining_text=(HERE.parent/");end=text.index("scope=ROOT/",start)
remaining="""remaining_text=(HERE.parent/'complete-claims-integration-20261026/remaining-work.md').read_text().split('## Next dependency',1)[0].replace('Version 5.11, 728 pages','Version 5.12, 728 pages')
remaining_text+='''## Next dependency

Complete supplied-claim openings and source remain integrated. The nested
invariant Unicode defect is repaired with exact prior full-result/control
correspondence and nine reproduced cases. Earlier partial population,
conditional history/opening/continuation and fiscal work remains credited.
The next audit maps native prospective term-history invariants to the current
declarative collection/binding language. Term history already has operations
and command authoring; nested rule authoring is the candidate gap, not a reason
to rebuild those operations. Missing real-company claims, wider sector/fiscal
algorithms, source/version gaps and independent acceptance remain. S6 held;
E3 deferred; no whole requirement closes.
'''
"""
text=text[:start]+remaining+text[end:]
pairs=[
('checked Version 5.11','checked Version 5.12'),
("v['version']=='5.11'","v['version']=='5.12'"),
("assert sha(m.TARGET/p['added_source'])==p['new_section_sha256']\n",''),
('accounting-post-opening-language-reassessment-20261026.md','accounting-nested-term-invariant-audit-20261026.md'),
('Current question: which consequential language/composition gap remains after the checked live-opening extension and earlier history/partial-population work?','Current question: which nested claim-term and assessment relationships lack explicit declarative invariant support?'),
('## Current governing candidate — Version 5.10','## Current governing candidate — Version 5.11'),
('## Prior governing candidate — Version 5.10','## Prior governing candidate — Version 5.11'),
("current_candidate='5.11;728 pages;not_ready'","current_candidate='5.12;728 pages;not_ready'"),
('data/accounting-master/complete-claims-source-20261026/result.md','data/accounting-master/invariant-unicode-repair-20261026/result.md'),
('Version5.11:728 pages;complete supplied claim openings and source;8 programs/54 commands;32 source controls;two exact order-identity exceptions','Version5.12:728 pages;quoted Unicode invariant repair;8 programs/54 commands and32 prior controls exact;9 reproduced defects'),
('Reassess actual language and partial-history dependencies without rebuilding completed bridges','Audit native nested term and assessment state invariants against current source primitives'),
('Select a consequential bounded repair with exact existing comparator','Specify missing general collection bindings before replacing native validation'),
("assert 'Version 5.10 is the current 726-page' in value","assert 'Version 5.11 is the current 728-page' in value"),
("value.replace('Version 5.10 is the current 726-page','Version 5.11 is the current 728-page',1)","value.replace('Version 5.11 is the current 728-page','Version 5.12 is the current 728-page',1)"),
('records complete supplied carried-claim openings and exact source correspondence. The [active plan]({plan}) reassesses the next language dependency against existing history, population and fiscal work.','records the nested-invariant Unicode repair with exact full-program correspondence. The [active plan]({plan}) audits declarative support for nested term and assessment histories.'),
("assert '**Version 5.10, 726 pages**' in value","assert '**Version 5.11, 728 pages**' in value"),
("value.replace('**Version 5.10, 726 pages**','**Version 5.11, 728 pages**',1).replace('selected-source-integration-20261026/result.md','complete-claims-integration-20261026/result.md',1)","value.replace('**Version 5.11, 728 pages**','**Version 5.12, 728 pages**',1).replace('complete-claims-integration-20261026/result.md','invariant-unicode-integration-20261026/result.md',1)"),
("assert 'Version 5.10,' in value","assert 'Version 5.11,' in value"),
("value.replace('Version 5.10,','Version 5.11,',1)","value.replace('Version 5.11,','Version 5.12,',1)"),
('Complete-claims typed and source evidence is frozen and integrated. Next: audited post-opening language reassessment. Main links select 5.11; standalone stays 5.5.','Complete-claims and Unicode repair evidence is frozen and integrated. Next: nested term-invariant audit. Main links select 5.12; standalone stays 5.5.'),
('docs/plans/accounting-complete-claims-integration-20261026.md','docs/plans/accounting-invariant-unicode-integration-20261026.md'),
("candidate='5.11'","candidate='5.12'")]
for old,new in pairs:
    assert old in text,old
    text=text.replace(old,new)
assert not (HERE/'advance.py').exists()
(HERE/'advance.py').write_text(text)
print('Configured Version 5.12 control advancement')
