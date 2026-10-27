"""Explicit author selections following the ordered Chapter 2 diagnosis.

Ranges below enumerate reviewed records, never infer coverage from a filename.
Mechanism reuse preserves a source qualification without claiming literal
reproduction. Source-only dispositions leave detailed facts in their ledgers.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = 'docs/design/proposal/manuscript-quality-inventory-20261010/'
UNITS = {p.name.removeprefix('apple-').rsplit('-2026', 1)[0]: p.name
         for p in OUT.parent.glob('apple-*') if (p / 'source-claim-supplement.json').exists()}
FILES = {'s': 'source-claim-supplement.json', 'l': 'claim-query-ledger.json', 'r': 'revenue-history.json'}
groups = []


def R(unit, file, key, indices):
    return [f'data/accounting-master/{UNITS[unit]}/{FILES[file]}#/{key}/{i}' for i in indices]


def A(section, quote):
    path = 'chapters/13-reference-company.tex' if section == 'case' else f'sections/apple-{section}.tex'
    return {'path': BASE + path, 'quote': quote}


def G(name, status, reason, records, *anchors):
    groups.append(dict(id=name, disposition=status, reason=reason, records=records, anchors=list(anchors)))


G('note-headings', 'structural_provenance',
  'These rows identify note boundaries; they contain no financial assertion. They stay in the inventory and outside substantive-support counts.',
  R('revenue','s','units',[0,12])+R('commitments','s','units',[0,8,14])+R('assets','s','units',[0,3])+R('tax','s','units',[0]))
G('revenue-policy', 'mechanism_reuse',
  'The control/collection and bundle-allocation paragraphs explain the recognition mechanism. Individual returns, SSP estimates and service lives remain contract facts; no claim of reproducing every policy clause.',
  R('revenue','s','units',[1,2,3,4,8]), A('case','The note describes collection shortly'))
G('revenue-net-and-marginals', 'mechanism_reuse',
  'Net App Store commission and the separate product/geography marginals prevent inferring gross billings or multiplying shares; the qualitative Greater China exception remains a limit on numeric witnesses.',
  R('revenue','s','units',[6,7,10,13,15])+R('revenue','r','queries',[5,6]),
  A('case','The product and geographic tables'), A('segments','Note 2 reports 201,183 million'))
G('revenue-movement', 'mechanism_reuse',
  'The equation and its immediately following interpretation distinguish opening-origin releases, new-origin releases and the residual. The two witnesses explicitly do not identify collections.',
  R('revenue','s','units',[9,14])+R('revenue','r','queries',[1,2]), A('case','The source identifies $R_o$'))
G('revenue-expectation', 'mechanism_reuse',
  'Dated total/current balances and recognition buckets have distinct meaning and precision; unbilled undelivered consideration remains unquantified. Equal percentages do not identify cohorts or receipt dates.',
  R('revenue','s','units',[5,11,16])+R('revenue','r','queries',[0,3,4]),
  A('case','The percentages divide an expected amount'), A('case','The note leaves another part'))
G('revenue-period', 'exact_support', 'The December 2024 quarter is outside the September 2024 fiscal year, so the proposed subtraction compares incompatible periods.',
  R('revenue','r','queries',[7]), A('case','September 2024 fiscal year'))
G('lease-measurement', 'mechanism_reuse',
  'The lease paragraphs distinguish expense, payment, ROU asset, discounted liability, gross buckets and uncommenced leases. Weighted rate/term information does not identify dated contracts; detailed source-year cells remain in the supplement.',
  R('commitments','s','units',range(1,8))+R('commitments','s','queries',range(4)),
  A('case','Thus $14{,}790-2{,}360=12{,}430$'), A('case','The remaining lease information'), A('case','Fixed and variable costs'))
G('purchase-populations', 'mechanism_reuse',
  'The greater-than-one-year contract scope, near-term payment buckets, manufacturing balances and no-material-change qualifier are separated before the simplified delivery/payment witnesses. Residual populations and actual orders stay unresolved.',
  R('commitments','s','units',[9])+R('commitments','s','queries',[4,5,6,7]),
  A('case','The purchase note and management discussion'), A('case','The two manufacturing totals'))
G('commitment-contingencies', 'mechanism_reuse',
  'The same qualified management assessment is retained at two dates and is not a zero-loss assertion. Supply concentration, custom capacity and outsourced manufacturing constrain scenario feasibility without identifying firms or probabilities.',
  R('commitments','s','units',[10,11,12,13,15])+R('commitments','s','queries',[8]),
  A('case','Delivery assumptions also need'), A('case','The same note, and the interim contingency note'))
G('assets-later-method-detail', 'source_only',
  'The PP&E/inventory tables, -160 residual, rejected retirement book and unpaid-addition repairs belong to the Chapter 9 operating-asset method (sections/apple-operating-assets.tex). Chapter 2 uses the need for lot/quality/settlement facts; it need not repeat that later derivation. This disposition does not independently accept the later calculation.',
  R('assets','s','units',[1,2,4,5,6])+R('assets','s','queries',range(8)))
G('tax-later-method-detail', 'source_only',
  'Charge, payable, deferred, UTB and settlement calculations are developed in Chapter 9 (sections/apple-tax-settlement.tex), not earlier in Chapter 2. Preserve the full jurisdictional, carryforward and open-year detail here. Correct the pronouncement/legal backward references; no new tax law or exact settlement history follows.',
  R('tax','s','units',range(1,12))+R('tax','s','queries',range(9)))
G('eps-later-method-detail', 'source_only',
  'Period-weighted shares, award populations, withholding, repurchase limits and the accepted/rejected quantity witnesses belong to Chapter 10 (sections/apple-eps-ownership.tex). None is needed as another Chapter 2 risk section. The timing/measurement lesson recurs, but these records are not certified as literally covered by that generic lesson.',
  R('eps','s','units',range(16))+R('eps','s','queries',range(10)))
G('debt-measurement-introduction', 'mechanism_reuse',
  'Chapter 2 introduces the difference between principal, carrying amount, fair value and calendar/fiscal maturities. Exact commercial-paper flows, rates and instrument terms stay in the later debt method; the introduction is mechanism support only.',
  R('debt','s','narrative_claims',[1,2,4,5])+R('debt','s','queries',[3]), A('case','Apple\'s annual balance sheet reports assets'))
G('debt-later-calculation', 'source_only',
  'Commercial-paper rollover, principal/carrying/cash residuals, coupons, hedge accounting and derivative-only VaR are Chapter 10 debt-method material (sections/apple-debt.tex). A Chapter 2 financing example cannot establish those detailed targets. The disruption forward reference must point there for currency sensitivity.',
  R('debt','s','material_units',range(9))+R('debt','s','narrative_claims',[0,3,6,7,8,9,10,11,12,13,14,15,16])+R('debt','s','queries',[0,1,2,4,5,6,7,8,9]))
G('liquidity-table-provenance', 'source_only',
  'These full seven-column source tables and repeated headers preserve all instrument categories; the manuscript selects aggregate reconciliations. Its aggregate table does not reproduce every cell. Hedging bodies remain later-debt dependencies.',
  R('liquidity','s','material_units',[0,1,2,4,7,8,9,11]))
G('liquidity-maturity', 'mechanism_reuse',
  'The purchase-date cash-equivalent rule and two distinct maturity-band populations are explained together, without treating maturity as a sale date or freely spendable balance.',
  R('liquidity','s','material_units',[3,10])+R('liquidity','s','claims',[0])+R('liquidity','s','queries',[6]), A('liquidity','Maturity supplies a different kind of timing information.'))
G('liquidity-restrictions', 'mechanism_reuse',
  'The dated totals, rounded restriction subtraction and liquidity belief are present with precision and continued-financing qualifications. The exact tax payment belongs to the later tax method, not to a new spendable-cash assumption.',
  R('liquidity','s','claims',[2,3])+R('liquidity','s','queries',[0,1,2]),
  A('liquidity','At September 2024, cash includes'), A('liquidity','The December footnote'))
G('liquidity-tax-payment', 'source_only', 'The 11.0-billion-euro payment is retained as a tax-settlement dependency. Its financial consequence is developed in Chapter 9; a liquidity classification alone cannot establish the conversion and settlement journal.',R('liquidity','s','claims',[4]))
G('liquidity-stock-cash-valuation', 'mechanism_reuse',
  'The residual identity, specific-identification policy, OCI population difference, 772 opening population mismatch and dated interest-rate sensitivity each have an explicit paragraph. They cannot be exchanged for cash, fair-value or tax journals.',
  R('liquidity','s','claims',[1])+R('liquidity','s','queries',[3,4,5,7]),
  A('liquidity','The relation defines a'), A('liquidity','The valuation columns help'), A('liquidity','Even reported cash needs'), A('liquidity','Valuation risk is likewise'))
G('liquidity-customer-and-vendor', 'mechanism_reuse',
  'Receipts, whole-customer union membership and vendor non-trade receivables have distinct calculations and denominators. Conditional examples do not reveal customers or collections, and the vendor gain is not product revenue.',
  R('liquidity','s','material_units',[5,6,12,13])+R('liquidity','s','queries',[8,9,10]),
  A('liquidity','Receivables may turn into cash'), A('liquidity','Concentration describes who'), A('liquidity','Vendor non-trade receivables'))
G('segments-definitions', 'mechanism_reuse',
  'Issuer-defined regions and customer attribution are explained before the cost bridge. Country long-lived assets are a separate stock, not the unreported segment-asset denominator. Detailed historical cells remain in the source tables.',
  R('segments','s','material_units',[0,1,3,4,5])+R('segments','s','queries',[0,1,3,4]),
  A('segments','Apple\'s fiscal 2024 Note 13 names'), A('segments','The annual note separately presents country sales'))
G('segments-cost-and-coupling', 'mechanism_reuse',
  'Corporate R&D/other-cost reconciliation and the product-region witnesses expose two different missing allocations. Numerical marginals do not certify qualitative-mix compatibility, operating margins or cash response.',
  R('segments','s','material_units',[2,6])+R('segments','s','queries',[2,5]),
  A('segments','Apple defines each segment\'s operating income'), A('segments','Note 2 reports 201,183 million'))
G('segments-recast', 'mechanism_reuse',
  'The retrospective adoption statement remains a dated issuer plan; the pronouncement section explicitly requires later evidence for a recast observation.',R('segments','s','queries',[6]),A('pronouncements','These plans require separate historical query views.'))
G('perimeter-scope-and-roster', 'mechanism_reuse',
  'Wholly-owned membership is positive reported scope. The eighteen-name exhibit and its omission footnote do not enumerate all subsidiaries or identify immediate ownership paths; original and interim estimates remain qualified.',
  R('perimeter','s','material_units',[0,11])+R('perimeter','s','queries',[0,1,2,3]),
  A('perimeter','Wholly-owned membership and immediate ownership answer different questions.'))
G('perimeter-policy-dependencies', 'source_only',
  'These eleven selected Note 1 calendar/accounting-policy clauses preserve dependencies for revenue, assets, debt, EPS, taxes and leases. The entity discussion does not purport to restate all policies or establish operative treatment. Keep their original source pointers and later method locations.',R('perimeter','s','material_units',[1,2,3,4,5,6,7,8,9,10,12]))
G('perimeter-relationships', 'mechanism_reuse',
  'Sales attribution, outsourcing and equipment custody do not identify legal seller or control. Incorporation leaves functional currency, tax residence and intercompany elimination facts unresolved.',
  R('perimeter','s','queries',[4,5,6,7,8]), A('perimeter','Production adds a further distinction.'), A('perimeter','The jurisdiction column also leaves'), A('perimeter','These distinctions determine what a supported query can return.'))
for m in range(8):
    G(f'legal-body-{m}', 'source_only',
      'The complete matter body is retained as the source for its separately enumerated assertions below; it is not counted as another independent claim or another support verdict.',R('legal','s','matters',[m]))
for name, matter_ids, ns, query, phrase in [
    ('dma',[0,4],[5,6],[0],'The Digital Markets Act discussion reports'),
    ('doj',[1,5],[3,4],[1],'The Department of Justice discussion reports'),
    ('epic',[2,6],[7,7],[2],"Epic's case contains a reported court finding"),
    ('other',[3,7],[3,4],[4],'Settlement adds a further distinction.')]:
    refs=[]
    for m,n in zip(matter_ids,ns): refs+=R('legal','s',f'matters/{m}/assertions',range(n))
    G('legal-'+name,'mechanism_reuse',
      {'dma':'The two dated reports, preliminary findings, conditional cap, appeal/stay and management position remain distinct; the source is an issuer account, not a verified legal instrument or expected fine.',
       'doj':'The manuscript retains allegation, equitable relief versus related civil damages, and management defenses; no unified damages amount is inferred.',
       'epic':'The reported injunction, US storefront scope, compliance dispute and dated motion appear together; their repetition is disclosure continuity, not proof of identical intervening legal facts.',
       'other':'Fourth-quarter and first-quarter settlement assertions are period-specific and unquantified; above-expectation adverse resolution remains possible. Neither source selects a payment or accrual history.'}[name],
      refs+R('legal','s','queries',query),A('legal',phrase))
G('legal-assessment', 'exact_support', 'The quoted management assessment expressly allows a recorded accrual and supplies neither its amount nor zero exposure.',R('legal','s','queries',[3]),A('legal','It does not disclose a total legal accrual'))
G('legal-revenue-channel', 'mechanism_reuse', 'The proposed Google remedy can affect search-contract revenue; the contract economics and realised remedy remain missing.',R('legal','s','queries',[5]),A('legal','That channel differs from an Apple fine.'))
G('legal-clocks', 'exact_support', 'The September 30 motion postdates the September 28 annual period-end; event, period and availability dates must remain separate.',R('legal','s','queries',[6]),A('legal','The September 30 motion also falls'))
G('legal-package-limit','source_only','The issuer-selected proceedings do not close dockets, operative law or whole-package semantics. That open package question is retained here rather than repeating a completeness disclaimer inside every matter.',R('legal','s','queries',[7]))
G('pronouncements-plans-and-amounts','mechanism_reuse',
  'The table preserves fiscal adoption plans and the tax/segment/expense paragraphs name the disclosure populations. Thresholds and component amounts remain absent; the false tax backward reference requires repair.',
  R('pronouncements','s','units',range(5))+R('pronouncements','s','queries',[0,2,3]),
  A('pronouncements','The tax discussion says'),A('pronouncements','The segment discussion concerns'),A('pronouncements','The interim expense passage reports'))
G('pronouncements-views','mechanism_reuse','Original/recast views, adoption plans versus observations and the post-period January clarification are explained explicitly; a report period is not an availability timestamp.',
  R('pronouncements','s','queries',[1,4,6]),A('pronouncements','These plans require separate historical query views.'),A('pronouncements','The January clarification illustrates'))
G('pronouncements-estimates','mechanism_reuse','Judgment, reserve adjustment and the incurred-loss policy are retained as issuer descriptions; no material change cannot freeze every estimate or carrying amount.',
  R('pronouncements','s','units',[5,6,7,8])+R('pronouncements','s','queries',[5]),A('pronouncements','Annual Critical Accounting Estimates says'),A('pronouncements','The interim references both annual'))
G('litigation-indemnity-remedy','mechanism_reuse','The insured or indemnified party, claim, defense, settlement and operating remedy are different relationships. Source wording does not select an actual liability, lost sale or journal.',
  R('litigation-risk','s','units',range(5))+R('litigation-risk','s','queries',[0,1,2]),A('litigation-risk','The statement supplies neither an indemnified party'))
G('litigation-recovery','mechanism_reuse','Claim, operating and data-security insurance have different populations and qualifications; recovery needs terms, exclusions and timing. Qualitative trade-credit support supplies no numeric protection percentage.',
  R('litigation-risk','s','units',[5,6,7,8])+R('litigation-risk','s','queries',[3,4]),A('litigation-risk','Apple says it maintains insurance for certain types of claims'))
G('litigation-continuity','mechanism_reuse','Interim incorporation retains annual risks with exceptions, without proving identical contracts or policies.',R('litigation-risk','s','units',[9])+R('litigation-risk','s','queries',[5]),A('disruption',"The interim's incorporation"))
G('litigation-probability','source_only','The source ledgers retain the no-probability and bounded-coverage query. Listing a risk is not a measure, and no manuscript paragraph is treated as proof that all risks have been modelled.',R('litigation-risk','s','queries',[6]))
G('regulation-assertions','mechanism_reuse','The annual/interim regulated-subject lists, expanded executive-order/national-security wording, controls qualification and repeated import/notice paragraph are explained without inferring a new operative event. Exact law, date, product, route and response remain query inputs.',
  R('regulation','s','units',range(9))+R('regulation','s','queries',range(5)),A('regulation','The two reports preserve a broad list'),A('regulation','The policy qualification is essential'),A('regulation','A conditional operating scenario should start'))
G('regulation-scope-limit','source_only','Two general-regulation bodies cannot close ESG, data, other risks or the filing package. Their separate records remain in the source inventory; later risk claims below receive separate dispositions.',R('regulation','s','queries',[5]))
G('macro-original-paragraphs','source_only','Four full macroeconomic paragraphs are retained as original support. Their author abstractions are the four macro claims in the subsequent business-interruption ledger; do not count these two representations as independent claims.',R('macroeconomic','s','body/paragraphs',range(4)))
G('interruption-original-paragraphs','source_only','Six full interruption paragraphs support six explicitly enumerated interruption claims in the same unit. Retain the original prose, including qualifications, without treating source retention as another support verdict.',R('business-interruption','s','body/paragraphs',range(6)))
G('macro-geography-and-finance','mechanism_reuse','Distinct sales/facility populations, demand, partner credit, collections, counterparties and funding can respond to common conditions. Neither geographic labels nor the channel list identifies a joint law.',
  R('business-interruption','l','claims',range(4))+R('business-interruption','l','queries',[0,1]),A('disruption','Apple says that sales outside'),A('disruption','The macroeconomic passage describes'))
G('interruption-event-and-recovery','mechanism_reuse','Trade/hazard assertions and historical health effects remain separate from future measures. Feasible substitution and recovery require capacity, timing and terms; an imposed safety requirement does not certify outcomes.',
  R('business-interruption','l','claims',range(4,10))+R('business-interruption','l','queries',range(2,9)),A('disruption','An interruption raises a different operating question'),A('disruption','Consider two explicitly assumed histories'),A('disruption','Recovery adds another date.'))
for unit,n,why in [('competition-transition',8,'competitive-market and product-transition'),('component-availability',2,'supplier renewal, capacity and alternate-source'),('quality-inventory',3,'defect, inventory and forecasting'),('remaining-risks',38,'licensing, ecosystem, personnel, channels, IT, strategy, retail, ESG, data, margin, FX, portfolio, tax and stock-price')]:
    G(unit+'-original-spans','source_only',
      f'These complete {why} source paragraphs remain provenance for the separate explicit assertions. Paragraph boundaries and secondary details are preserved, not counted as additional independently supported claims; retaining all paragraphs does not establish exhaustive semantic abstraction.',R(unit,'s','units',range(n)))
G('competition-incentives','mechanism_reuse','Competition, integrated R&D, qualitative minority share, IP allegations and free-content alternatives explain why transition success need not produce a favourable margin. No numerical market share, return or adjudicated infringement is supplied.',
  R('competition-transition','l','claims',range(7))+R('competition-transition','l','queries',[1,2,3]),A('competition-transition','The preceding competitive-market discussion'))
G('competition-transition-clocks','mechanism_reuse','The replacement example separates acceptance, compatibility, commitments and capacity; transfer of control, service provision and collection require different dates. Third-party support is named but its nonphysical mechanism needs the bridge below.',
  R('competition-transition','l','claims',[7])+R('competition-transition','l','queries',[0,4,5,6,7]),A('competition-transition','The transition passage identifies'),A('competition-transition','Suppose, as an illustration'),A('competition-transition','Even a delivered replacement'))
G('component-renewal-and-capacity','mechanism_reuse','The supplier discussion distinguishes existing agreements from renewal, multiple sources from common shortages, and custom-component yield/capacity from purchase quantities. Past shipment delays do not calibrate future amounts.',
  R('component-availability','l','claims',range(8))+R('component-availability','l','queries',range(8)),A('component-availability','For an explicitly assumed delay'))
G('quality-customer-obligations','mechanism_reuse','Defects, performance, detection and customer remedies can affect delivered output. The section separates possible recall/liability and conditional third-party provisions from an actual charge or reimbursement.',
  R('quality-inventory','l','claims',range(4))+R('quality-inventory','l','queries',[0,1,2]),A('quality-inventory','Obtaining components and completing delivery'))
G('quality-inventory-valuation','mechanism_reuse','The final paragraphs distinguish inventory write-down, excess-order fees and class-specific impairment. Forecasting before shipment, typical 150 days and recoverability beliefs do not establish universal terms, probabilities or actual reserves.',
  R('quality-inventory','l','claims',range(4,9))+R('quality-inventory','l','queries',range(3,10)),A('quality-inventory','The link to product transitions'),A('quality-inventory','Consider an explicitly assumed reduction'))
G('service-access-missing','missing_bridge',
  'Chapter 2 names third-party support but does not explain that a usable product/service still needs continuing IP/content rights, developer participation and lawful/operational data/payment access. Those conditions have separate periods and scopes. Add a short integrated bridge; do not infer any actual termination, breach, price, probability or accounting treatment.',
  R('remaining-risks','l','claims',[0,1,2,3,6,8,23,24])+R('remaining-risks','l','queries',[0,1,2,6,11]),
  A('competition-transition','application software or other'))
G('application-quality','mechanism_reuse','Application compatibility and incorrect operation use the quality section\'s hardware/software/service distinction. The source does not identify an incident or customer cohort; this maps the mechanism, not all examples.',
  R('remaining-risks','l','claims',[4]),A('quality-inventory','Obtaining components and completing delivery'))
G('appstore-terms','mechanism_reuse','App Store distribution, payments, fees and tools are concrete channels in the legal section. The changes are reported assertions without a measured sales effect.',R('remaining-risks','l','claims',[5]),A('legal','The risk discussion connects these matters to operations.'))
G('content-creation-detail','source_only','Costly own-content creation and uncertain audience appeal are retained here. They need a content cohort, cost treatment and demand model before a distinct financial example is useful; a generic R&D paragraph is not literal support.',R('remaining-risks','l','claims',[7]))
G('personnel-culture-detail','source_only','The personnel/culture assertions and question supply no departure, compensation, retention or measured mechanism. Preserve them for the wider operating-model queue; another unquantified risk paragraph would not answer the question.',R('remaining-risks','l','claims',[9,10])+R('remaining-risks','l','queries',[3]))
G('carrier-reseller-detail','source_only','Specific carrier instalments/subsidies and reseller programmes require route populations, contracts and ordering facts. The existing customer/receivable examples cannot certify these missing commercial terms. Preserve them as distinct unresolved operating-model dependencies.',R('remaining-risks','l','claims',[11,12,13])+R('remaining-risks','l','queries',[4]))
G('it-continuity','mechanism_reuse','An IT interruption can use the existing unavailable-activity/recovery model, with its own systems, orders and recovery dates. Neither the generic source nor that model proves an outage occurred or that redundancy suffices.',R('remaining-risks','l','claims',[14])+R('remaining-risks','l','queries',[5]),A('disruption','An interruption raises a different operating question'),A('disruption','Recovery adds another date.'))
G('security-exposure-detail','source_only','Confidential-information, third-party and attack assertions remain individually retained. The chapter\'s disruption mechanism does not establish control effectiveness, incident frequency or security losses. The access bridge adds a prerequisite, not a cyber-risk model.',R('remaining-risks','l','claims',[15,16,17,18]))
G('data-insurance-reuse','mechanism_reuse','The prior insurance discussion already separates data-security coverage, exclusions and payment from an underlying loss. No additional risk list or recovery amount is justified.',R('remaining-risks','l','claims',[19])+R('remaining-risks','l','queries',[7]),A('litigation-risk','Apple says it maintains insurance for certain types of claims'))
G('acquisition-retail-detail','source_only','The strategic/acquisition and retail-store risk lists name possible transactions and costs without selecting any. Actual consideration, acquired positions, stores, inventory and leases belong on the wider fact/model queue; prior impairment and lease mechanisms are not an acquisition or store forecast.',R('remaining-risks','l','claims',[20,21])+R('remaining-risks','l','queries',[8,9]))
G('esg-detail','source_only','Stakeholder expectations, voluntary statements and changing reporting standards are not interchangeable legal duties. No identified statement, authority or amount permits a new obligation example; preserve the distinction and unresolved query.',R('remaining-risks','l','claims',[22])+R('remaining-risks','l','queries',[10]))
G('margin-drivers','mechanism_reuse','The product-transition and macro sections explain several competing demand, cost, mix and supply routes to margin changes. This reuses the mechanism without reproducing every listed driver or estimating a response function.',R('remaining-risks','l','claims',[25]),A('competition-transition','A new offering can replace demand'),A('disruption','The macroeconomic passage describes'))
G('seasonality-detail','source_only','Holiday and event timing cannot allocate annual totals to quarters. A calibrated seasonal sales path needs additional dated observations and behavioural assumptions; the source statement alone remains a query limit.',R('remaining-risks','l','claims',[26])+R('remaining-risks','l','queries',[12]))
G('operating-fx-detail','source_only','Operating currencies, pricing response and limited hedge horizons need instrument and product-specific dates, quantities and elasticities. The later derivative-only VaR is a different target and cannot supply them. Retain these three claims and two questions as unresolved operating-model detail.',R('remaining-risks','l','claims',[27,28,29])+R('remaining-risks','l','queries',[13,14]))
G('portfolio-value-reuse','mechanism_reuse','Liquidity\'s security stock/cash/valuation distinction and dated sensitivity preserve the route from holdings and market conditions to changed value without treating a risk statement as a realised loss.',R('remaining-risks','l','claims',[30])+R('remaining-risks','l','queries',[15]),A('liquidity','Securities can fund payments'),A('liquidity','Valuation risk is likewise'))
G('tax-risk-detail','source_only','Jurisdictional mix, changing law and tax examinations need actual laws, positions and dates. The Chapter 9 tax case is their later method context; neither the risk nor that example selects an adopted future tax rate or audit outcome.',R('remaining-risks','l','claims',[31,32])+R('remaining-risks','l','queries',[16]))
G('equity-price-detail','source_only','Market price can move separately from operating performance. Chapter 2 constructs conditional operating statements, not a market-price law; retain the assertion and question without substituting EPS or a repurchase calculation.',R('remaining-risks','l','claims',[33])+R('remaining-risks','l','queries',[17]))
G('remaining-scope-and-weights','source_only','Full body retention does not close exhibits, operative facts or semantic acceptance, and no probability measure is supplied. These are limits on the whole source unit, not new company facts to repeat in sixteen sections.',R('remaining-risks','l','queries',[18,19]))

if __name__ == '__main__':
    (OUT/'author-dispositions.json').write_text(json.dumps(groups,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'author_groups':len(groups),'selected_records':sum(len(g['records']) for g in groups)}))
