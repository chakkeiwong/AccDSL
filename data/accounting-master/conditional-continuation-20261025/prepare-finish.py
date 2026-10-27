from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
text=(ROOT/'data/accounting-master/history-to-opening-20261025/finish.py').read_text()
text=text.replace('accounting-conditional-continuation-20261025.md','accounting-group-sector-composition-20261025.md')
text=text.replace('declared-receivable-lifecycle-coverage-20261025/inventory.json','conditional-opening-coverage-20261025/inventory.json')
text=text.replace("COVER = ROOT / 'data/accounting-master/conditional-opening-coverage-20261025'",
                  "COVER = ROOT / 'data/accounting-master/conditional-continuation-coverage-20261025'")
text=text.replace('4.18','4.19').replace('514','515')
text=text.replace('Conditional history opening checked','Conditional continuation checked')
text=text.replace('11 focused tests, 74 regressions and 36 named comparisons pass; read-only replay agrees.',
                  '5 focused tests, 50 regressions and 48 named comparisons pass; read-only replay agrees.')
text=text.replace('Two histories retain different memory at equal closing cash on two charts.\nContext, dates, units and unresolved obligations remain explicit.',
                  'Two histories retain memory 5/7 after the exact cash/equity 15/−15 to 14/−14 continuation.\nUnresolved obligations block composition and report signs remain explicit.')
text=text.replace('rendered pages 389–391','rendered pages 389–391')
text=text.replace('Conditional financial continuation, populated contracts, common sector interfaces',
                  'Group/bank/insurance composition, populated contracts, common sector interfaces')
text=text.replace('Current question: preserve conditional history provenance through one explicit\nfinancial continuation, retaining unresolved obligations and alternate histories.\nNext action: audit and compose the rechecked opening with a declared method,\nthen compare exact journal, cash flow and report effects on both charts.',
                  'Current question: compose company state across group, bank and insurer\nboundaries while retaining distinct accounting and source histories.\nNext action: audit the retained corporate/financing methods and choose the smallest\ncommon composition contract with explicit sector-specific gaps.')
text=text.replace('Conditional opening: 11 focused, 74 regressions, 36 comparisons; Version 4.18',
                  'Conditional continuation: 5 focused, 50 regressions, 48 comparisons; Version 4.19')
text=text.replace('Compose a rechecked conditional opening with explicit financial methods while retaining evidence obligations',
                  'Audit group/bank/insurance composition and preserve sector-specific source and measurement obligations')
target=HERE/'finish.py';assert not target.exists();target.write_text(text);print('Prepared continuation control refresh')
