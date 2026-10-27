from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
source=ROOT/'data/accounting-master/declared-collection-state-growth-20261025/integrate.py'
target=HERE/'integrate.py';assert not target.exists()
text=source.read_text()
text=text.replace("SOURCE = ROOT / 'docs/design/proposal/manuscript-collection-clock-20261025'",
                  "SOURCE = ROOT / 'docs/design/proposal/manuscript-receivable-lifecycle-20261025'")
text=text.replace("TARGET = ROOT / 'docs/design/proposal/manuscript-receivable-lifecycle-20261025'",
                  "TARGET = ROOT / 'docs/design/proposal/manuscript-conditional-opening-20261025'")
text=text.replace('fe3abf909215f1f28e7651d863fee25c76d4e55dc7b2e9f597716d66880ebc56',
                  '1a1c7e98c18a04496f0d62deb7181dc88954638f7554355581a7197fa5152fca')
text=text.replace('4.17','4.18').replace('4.16','4.17')
text=text.replace('A payment can change the decision that follows it.', 'Report the declared accounts and explain their movements.')
text=text.replace('A credit sale must create the claim that can later be collected.', 'A conditional history gives a conditional opening.')
text=text.replace('An invoice created after an earlier assessment therefore remains visibly', 'The boundary between the representations needs explicit premises.')
text=text.replace('The versioned DeclaredReceivableText/1 adapter uses the existing', 'This distinction matters for receivables.')
text=text.replace('/tmp/accdsl-receivable-lifecycle-20261025-tex-cache','/tmp/accdsl-conditional-opening-20261025-tex-cache')
target.write_text(text);print('Prepared conditional-opening integration script')
