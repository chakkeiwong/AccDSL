"""Source-specific historical AU support; never a current-law admission."""
M='docs/design/proposal/methods/'
A='docs/design/research/p08-v1/'
def au(base,method,anchors,start='2023-01-01',end='2026-07-01'):
    return dict(base=base,family='AU_AASB',start=start,end=end,method=M+method,anchors=anchors)
SOURCES={
 'transfer':au(A+'aasb9','bank-transfer-fees-20261015.md',
   ['AASB9.3.2.2','AASB9.3.2.13-15']),
 'guarantee':au(A+'aasb9','bank-transfer-fees-20261015.md',
   ['AASB9.3.2.16-22','AASB9.B3.2.13(a)']),
 'option':au(A+'aasb9','bank-option-transfers-20261015.tex',
   ['AASB9.3.2.16-22','AASB9.B3.2.13(c-e)','AASB9.B3.2.14']),
 'ac_option':au(A+'aasb9','bank-option-transfers-20261015.tex',
   ['AASB9.3.2.17-22','AASB9.B3.2.13(b)','AASB9.B3.2.14']),
 'asset':au(A+'aasb9','bank-asset-classification-20261015.tex',
   ['AASB9.4.1.1-5','AASB9.5.5.1-2','AASB9.5.7.5-6','AASB9.5.7.10-11',
    'AASB9.B4.1.9A-E','AASB9.B5.7.1-1A']),
 'service':au(M+'sources/aasb15-compiled-dec2022','bank-transfer-fees-20261015.md',
   ['AASB15.35(a)','AASB15.39-40']),
 'cash_AU_AASB':au(M+'preparation-20261005-v1/01-accounting/sources/aasb107-compiled-jun2023',
   'bank-asset-classification-20261015.tex',['AASB107.14-17','AASB107.31-33'],start='2024-01-01',end=None),
}
def supporting(tag):
    return ['cash_AU_AASB']+(['service'] if tag=='guarantee' else [])
