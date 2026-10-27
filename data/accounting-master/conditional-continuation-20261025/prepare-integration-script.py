from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
text=(ROOT/'data/accounting-master/history-to-opening-20261025/integrate.py').read_text()
text=text.replace("SOURCE = ROOT / 'docs/design/proposal/manuscript-receivable-lifecycle-20261025'",
                  "SOURCE = ROOT / 'docs/design/proposal/manuscript-conditional-opening-20261025'")
text=text.replace("TARGET = ROOT / 'docs/design/proposal/manuscript-conditional-opening-20261025'",
                  "TARGET = ROOT / 'docs/design/proposal/manuscript-conditional-continuation-20261025'")
text=text.replace('1a1c7e98c18a04496f0d62deb7181dc88954638f7554355581a7197fa5152fca',
                  '15bd4a7a00344446552421eb9754103ec59a7b49b43ee3b7d1adf56d8bfcca18')
text=text.replace('4.18','4.19').replace('4.17','4.18')
text=text.replace('A conditional history gives a conditional opening.', 'Keep the selected history attached when the book changes.')
text=text.replace('The boundary between the representations needs explicit premises.', 'For the two preceding histories, assume a cash distribution of USD 1')
text=text.replace('This distinction matters for receivables.', 'The checked wrapper agrees exactly with the unchanged transition and report')
text=text.replace('/tmp/accdsl-conditional-opening-20261025-tex-cache','/tmp/accdsl-conditional-continuation-20261025-tex-cache')
target=HERE/'integrate.py'; assert not target.exists(); target.write_text(text)
print('Prepared continuation integration script')
