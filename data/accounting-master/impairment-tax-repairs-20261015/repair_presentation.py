from pathlib import Path
import json
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
p = ROOT / 'docs/design/proposal/manuscript-impairment-tax-20261015/sections/impairment-tax.tex'
s = p.read_text()
repairs = {
    'C 4 therefore': 'C4 therefore',
    'C 8 prevents': 'C8 prevents',
    'C 6 allocates': 'C6 allocates',
    'C 7 separately': 'C7 separately',
    'IAS 12.61 A': 'IAS~12.61A',
    'IAS 12.4 A/88 A--88 D/98 M': 'IAS~12.4A, 88A--88D and 98M',
    'within 4 A': 'within paragraph 4A',
    '70+120+40=230': r'\(70 + 120 + 40 = 230\)',
    'asset,6': 'asset, 6',
    '31.5,31.5,54,54,36': r'\(31.5,\ 31.5,\ 54,\ 54,\ 36\)',
    '40→16': r'from \(40\) to \(16\)',
    'loss,56': 'loss, 56',
    '240→180': r'from \(240\) to \(180\)',
    '200:100': r'\(200:100\)',
    'from asset 140 less DTL 10=130 to asset 90 plus DTA 2.5=92.5': r'from \(140 - 10 = 130\) to \(90 + 2.5 = 92.5\)',
    '92.5→122.5': r'from \(92.5\) to \(122.5\)',
    r'25\%→30\%': r'from \(25\%\) to \(30\%\)',
    '10→12': r'from \(10\) to \(12\)',
}
for a, b in repairs.items():
    assert s.count(a) == 1, (a, s.count(a))
    s = s.replace(a, b)
p.write_text(s)
(OUT / 'presentation-repairs.json').write_text(json.dumps({'count': len(repairs), 'replacements': repairs}, indent=2) + '\n')
print(json.dumps({'presentation_repairs': len(repairs)}))
