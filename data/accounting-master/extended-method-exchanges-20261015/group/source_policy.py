"""Retained historical authority and exact technical anchors; no retrieval."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
EU='docs/design/research/p08-v3-preparation/'
AMEND='docs/design/research/p08-v4/'
METHOD='docs/design/proposal/methods/'
METHOD_SOURCES={
 'reciprocal.join@1':['eu2023'], 'inventory.eliminate@1':['eu2023'],
 'inventory.release@1':['eu2023'], 'inflation.restate@1':['eu2023'],
 'inflation.opening_tax@1':['eu2023'], 'goodwill.impair@1':['eu2023'],
 'corporate_asset.impair@1':['eu2023'], 'acquisition.tax@1':['eu2023'],
 'investment.taxable@1':['eu2023'], 'investment.deductible@1':['eu2023'],
 'exchangeability.assess@1':['exchange2024'],
 'exchangeability.transition@1':['exchange2024']}
def sources():
 return [dict(key='eu2023',path=EU+'eu-2023-1803-original.pdf',
  sha256='e4fde71d4db44ef7c6c74055a564c8cb071340442b63185ff1700c86a64579e5',
  text_path=EU+'eu-2023-1803-original.txt',
  text_sha256='37f207b1ecdde43e3971cf076f127576d3d7810c791385ba5b1c35f110f17664',
  methods=[METHOD+'group-fx-disposal-20261014.md',METHOD+'groups-fx-methods-v1.md',
           METHOD+'group-restatement-exchangeability-20261015.tex',METHOD+'impairment-tax-repairs-20261015.md'],
  anchors=['IFRS10 B86-B88,B92-B95: intragroup elimination, control timing and reporting alignment',
   'IAS21 42-47: restatement before translation, nonhyperinflationary comparatives',
   'IAS29 8-28,33-41: dated restatement, monetary position, cash-flow purchasing power',
   'IFRIC7 3-5: opening deferred tax before index restatement',
   'IAS36 100-105,Appendix C4-C8: corporate-asset order/floors, notional NCI goodwill',
   'IAS12 15(a),39,44,46-51,66-68: acquisition and outside-basis tax']),
  dict(key='exchange2024',path=AMEND+'202402862-text.response',
   sha256='8fb400f5cea4f58503c974c4bddda8bbba5956a402127cb97b59d2c67fb13acc',
   text_path=AMEND+'202402862.txt',
   text_sha256='62a73ba7413ab8ed24f19dc97e1700ae6d832a8e52852b3bd10bf76b68377c8c',
   methods=[METHOD+'group-restatement-exchangeability-20261015.tex'],
   anchors=['EU2024/2862 Article2: annual periods from 2025-01-01, earlier disclosure',
    'IAS21 8-8B,19A,26,57A-57B,A2-A20: ability, date, purpose and estimation objective',
    'IAS21 60L-60M: opening retained earnings/translation, no comparative restatement'])]
