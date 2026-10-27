from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
source = ROOT / 'data/accounting-master/declared-dynamic-collection-clock-20261025/integrate.py'
target = HERE / 'integrate.py'
assert not target.exists()
text = source.read_text()
text = text.replace("SOURCE = ROOT / 'docs/design/proposal/manuscript-financing-schedules-repair-20261025'",
                    "SOURCE = ROOT / 'docs/design/proposal/manuscript-collection-clock-20261025'")
text = text.replace("TARGET = ROOT / 'docs/design/proposal/manuscript-collection-clock-20261025'",
                    "TARGET = ROOT / 'docs/design/proposal/manuscript-receivable-lifecycle-20261025'")
text = text.replace('8cf89d06298342a0b445ee115bb8dd48aee1dc314ee98f149cd901cbac6ce851',
                    'fe3abf909215f1f28e7651d863fee25c76d4e55dc7b2e9f597716d66880ebc56')
text = text.replace('4.16', '4.17').replace('4.15', '4.16')
text = text.replace("'Distinguish collecting a claim from assessing whether it is overdue.'",
                    "'A credit sale must create the claim that can later be collected.'")
text = text.replace("'A report can advance its observation date without supplying the missing'",
                    "'An invoice created after an earlier assessment therefore remains visibly'")
text = text.replace("'The existing command language can author these events, reports and carries'",
                    "'The versioned DeclaredReceivableText/1 adapter uses the existing'")
text = text.replace('/tmp/accdsl-collection-clock-20261025-tex-cache', '/tmp/accdsl-receivable-lifecycle-20261025-tex-cache')
target.write_text(text)
print('Prepared additive lifecycle integration script')
