"""Source windows restrict synthetic examples, not legal applicability."""
EU='docs/design/research/p08-v3-preparation/eu-2023-1803-original'
BASE='data/accounting-master/extended-method-exchanges-20261015/corporate-residuals/'
ANCHORS={
 'rcost':['IFRS15.B21-B27','IAS2.16'],
 'cgu':['IAS36.116-125'],
 'individual':['IAS36.117-119'],
 'lease':['IFRS16.12-16','IFRS16.43-46','IFRS16.50'],
 'cost':['IFRS15.91-104'],
 'distinct':['IFRS15.19-21(a)'],
 'integrated':['IFRS15.21(b)-(c)'],
 'acqdta':['IAS12.24','IAS12.46-51','IAS12.61A-68','IFRS3.45-46'],
 'taxlots':['IAS12.24','IAS12.46-51','IAS12.61A-63','IAS12.73-76'],
 'cash_EU_IFRS':['IAS7.14','IAS7.17-19','IAS7.31-33','IFRS16.50'],
}
SOURCES={k:dict(base=EU,family='EU_IFRS',start='2024-01-01',end='2026-01-01',method=BASE+'semantic-contract.md',anchors=v) for k,v in ANCHORS.items()}
