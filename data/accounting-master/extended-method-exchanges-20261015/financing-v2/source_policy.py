"""Authored source bindings; historical support, never actual-law admission."""
EU='docs/design/research/p08-v3-preparation/eu-2023-1803-original'
AU='docs/design/research/p08-v1/aasb9'
CASH='docs/design/proposal/methods/preparation-20261005-v1/01-accounting/sources/aasb107-compiled-jun2023'
METHODS='docs/design/proposal/methods/'
NOTE='data/accounting-master/extended-method-exchanges-20261015/financing-v2/source-reading.md'
SOURCES={
 'amendment':dict(base=EU,family='EU_IFRS',start=None,end=None,
   method=METHODS+'financing-amendment-dates-20261015.tex',anchors=['IAS32.AG35','IFRS9.3.3.1-4']),
 'award':dict(base=EU,family='EU_IFRS',start=None,end=None,
   method=METHODS+'award-modifications-20261015.tex',anchors=['IFRS2.B42-B44C']),
 'cashflow':dict(base=AU,family='AU_AASB',start='2023-01-01',end='2026-07-01',
   method=METHODS+'financing-methods-v1.md',anchors=['AASB9.6.5.11-12']),
 'option':dict(base=AU,family='AU_AASB',start='2023-01-01',end='2026-07-01',
   method=METHODS+'financing-components-20261015.md',anchors=['AASB9.6.5.15','AASB9.B6.5.29-33']),
 'rebalancing':dict(base=AU,family='AU_AASB',start='2023-01-01',end='2026-07-01',
   method=METHODS+'financing-components-20261015.md',anchors=['AASB9.6.5.5-6','AASB9.B6.5.7-28']),
 'nethedge':dict(base=EU,family='EU_IFRS',start=None,end=None,
   method=METHODS+'net-hedge-timing-20261015.tex',anchors=['IFRS9.6.6.1-6','IFRS9.B6.6.9','IFRS9.B6.6.15']),
 'cash_EU_IFRS':dict(base=EU,family='EU_IFRS',start=None,end=None,
   method=METHODS+'financing-methods-v1.md',anchors=['IAS7.12','IAS7.14','IAS7.16-19','IAS7.31-33']),
 'cash_AU_AASB':dict(base=CASH,family='AU_AASB',start='2024-01-01',end=None,
   method=METHODS+'financing-methods-v1.md',anchors=['AASB107.16-19','AASB107.31-33']),
}

for tag,base,family,method,anchors in [
 ('debt',AU,'AU_AASB','financing-methods-v1.md',['AASB9.5.1.1','AASB9.5.4.1','AASB9.B5.4.1-3']),
 ('modification',AU,'AU_AASB','financing-methods-v1.md',['AASB9.3.3.1-3','AASB9.B3.3.6-6A']),
 ('shares',EU,'EU_IFRS','financing-methods-v1.md',['IAS32.33','IAS32.AG36']),
 ('compound',EU,'EU_IFRS','financing-methods-v1.md',['IAS32.28-32','IAS32.AG32-34']),
 ('vesting',EU,'EU_IFRS','awards-participation-20261015.md',['IFRS2.19-21A','IFRS2.28']),
 ('cashaward',EU,'EU_IFRS','awards-participation-20261015.md',['IFRS2.30-33D']),
 ('choice',EU,'EU_IFRS','awards-participation-20261015.md',['IFRS2.35-43']),
 ('eps',EU,'EU_IFRS','awards-participation-20261015.md',['IAS33.19-21','IAS33.41-47A','IAS33.58-60','IAS33.A13-14']),
 ('fvhedge',AU,'AU_AASB','financing-methods-v1.md',['AASB9.6.5.8-10']),
 ('reform',AU,'AU_AASB','financing-methods-v1.md',['AASB9.5.4.5-9','AASB9.6.9.1-8']),
]:
 SOURCES[tag]=dict(base=base,family=family,start='2023-01-01' if family=='AU_AASB' else None,
   end='2026-07-01' if family=='AU_AASB' else None,method=METHODS+method,anchors=anchors)
