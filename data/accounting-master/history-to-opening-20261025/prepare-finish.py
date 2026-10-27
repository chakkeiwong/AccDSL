from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
text=(ROOT/'data/accounting-master/declared-collection-state-growth-20261025/finish.py').read_text()
text=text.replace('accounting-history-to-opening-20261025.md','accounting-conditional-continuation-20261025.md')
text=text.replace('declared-collection-clock-coverage-20261025/inventory.json','declared-receivable-lifecycle-coverage-20261025/inventory.json')
text=text.replace("COVER = ROOT / 'data/accounting-master/declared-receivable-lifecycle-coverage-20261025'",
                  "COVER = ROOT / 'data/accounting-master/conditional-opening-coverage-20261025'")
text=text.replace('4.17','4.18').replace('513','514')
text=text.replace('Typed map insertion and declared sale/receipt/assessment/carry with matched text.',
                  'Rechecked conditional history mapped to a complete provisional opening with preserved alternatives and obligations.')
text=text.replace('Receivable lifecycle coverage','Conditional-opening coverage')
text=text.replace('checked typed-lifecycle scope','checked conditional-opening scope')
text=text.replace('Typed receivable lifecycle checked','Conditional history opening checked')
text=text.replace('41 focused tests, 110 regressions and 66 named comparisons pass; read-only replay agrees.',
                  '11 focused tests, 74 regressions and 36 named comparisons pass; read-only replay agrees.')
text=text.replace('Typed new claims, exact sale journals, identified receipts, per-claim assessments,\npreserved carry and matched text execute on two charts.',
                  'Two histories retain different memory at equal closing cash on two charts.\nContext, dates, units and unresolved obligations remain explicit.')
text=text.replace('rendered pages 396–398','rendered pages 389–391')
text=text.replace('Conditional histories to openings, contract populations, common sector interfaces',
                  'Conditional financial continuation, populated contracts, common sector interfaces')
text=text.replace('Current question: carry a selected conditional history into a declared opening\nwithout inventing invoice facts, discarding alternatives or promoting a witness.\nNext action: inspect typed-history replay/context/date/memory contracts and record\nthe smallest exact mapping before implementing an additive adapter.',
                  'Current question: preserve conditional history provenance through one explicit\nfinancial continuation, retaining unresolved obligations and alternate histories.\nNext action: audit and compose the rechecked opening with a declared method,\nthen compare exact journal, cash flow and report effects on both charts.')
text=text.replace('Typed receivable lifecycle: 41 focused, 110 regressions, 66 comparisons; Version 4.18',
                  'Conditional opening: 11 focused, 74 regressions, 36 comparisons; Version 4.18')
text=text.replace('Audit conditional history-to-opening mappings and preserve unresolved contract population facts',
                  'Compose a rechecked conditional opening with explicit financial methods while retaining evidence obligations')
target=HERE/'finish.py';assert not target.exists();target.write_text(text)
print('Prepared conditional-opening control refresh')
