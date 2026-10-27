from pathlib import Path
H=Path(__file__).resolve().parent;p=H/'advance.py'
assert not (H/'advancement.json').exists() and not (H/'control-before').exists()
s=p.read_text();assert '20262027' in s
(H/'advance-before-date-repair.py').write_text(s)
s=s.replace('20262027','20261027');compile(s,str(p),'exec');p.write_text(s)
(H/'advancement-repair.md').write_text('The first advancement stopped at its active-plan guard before any control, link or gap-program writes. A broad template substitution of source count261 to262 also changed20261027 paths to20262027. The failed writer is preserved in advance-before-date-repair.py; exact path dates were restored. This was a writer-generation defect, not live drift or evidence failure. Counts are now checked separately from dates.\n')
print('Restored exact dated paths; no prior advancement writes occurred.')
