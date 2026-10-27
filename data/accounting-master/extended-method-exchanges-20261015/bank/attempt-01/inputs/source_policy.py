"""Retained historical source bindings. No current-law admission."""
M='docs/design/proposal/methods/'
A='docs/design/research/p08-v1/'
def au(base,method,anchors,start='2023-01-01',end='2026-07-01'):
    return dict(base=base,family='AU_AASB',start=start,end=end,method=M+method,anchors=anchors)
SOURCES={
 'loan':au(A+'aasb9','bank-restructuring-funding-20261015.md',
   ['AASB9.3.1.1','AASB9.5.1.1','AASB9.5.4.1-4','AASB9.5.5.1-20','AASB9.B5.5.28-33','AASB9.B5.5.44','AASB9.B5.5.55']),
 'commitment':au(A+'aasb9','bank-transfer-fees-20261015.md',
   ['AASB9.5.5.6','AASB9.5.5.17-20','AASB9.B5.5.39-40','AASB9.B5.5.47-50']),
 'fee':au(A+'aasb9','bank-transfer-fees-20261015.md',['AASB9.B5.4.1-4']),
 'liquidity':au(A+'aasb9','bank-restructuring-funding-20261015.md',['AASB9.3.1.1','AASB9.5.1.1']),
 'disclosure':au(A+'aasb7','bank-transfer-fees-20261015.md',['AASB7.B8E']),
 'service':au(M+'sources/aasb15-compiled-dec2022','bank-transfer-fees-20261015.md',
   ['AASB15.35(a)','AASB15.39-40','AASB15.105-106']),
 'cash_AU_AASB':au(M+'preparation-20261005-v1/01-accounting/sources/aasb107-compiled-jun2023',
   'bank-methods-v1.md',['AASB107.14-15','AASB107.17','AASB107.31-33'],start='2024-01-01',end=None),
}
def supporting(tag):
    return ['cash_AU_AASB']+(['disclosure'] if tag=='commitment' else ['service'] if tag=='fee' else [])
