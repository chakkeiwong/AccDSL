"""Prepare explicit display checks and source-to-state limits, without admission."""
from pathlib import Path
from fractions import Fraction
from hashlib import sha256
import json
import fitz

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def dump(name,value):
    (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
    assert not (HERE/'display-checks.json').exists(), 'already prepared'
    data=json.loads((HERE/'observations.json').read_text())
    obs={o['id']:o for o in data['observations']}
    checks=[]
    def check(key,terms,expected,meaning,scope='display_comparison',excluded=()):
        value=sum((Fraction(weight)*Fraction(obs[name]['displayed_rational']) for name,weight in terms),Fraction())
        assert value==Fraction(expected),(key,value,expected)
        checks.append({'id':key,'terms':[{'observation':name,'coefficient':str(weight)} for name,weight in terms],
                       'result':str(value),'expected_display_result':str(expected),'scope':scope,
                       'interpretation':meaning,'excluded_observations':list(excluded),
                       'exact_underlying_equality_asserted':False,'role':'explanatory_diagnostic'})
    for year in [2024,2025]:
        for stem,expected in [('rou_net',0 if year==2024 else 1),('rou_gross',0),('rou_accumulated',1 if year==2024 else -1),('rou_additions',0 if year==2024 else 1)]:
            check(f'{year}.{stem}.category_residual',[(f'{year}.{stem}.total',1)]+[(f'{year}.{stem}.{k}',-1) for k in ['land_buildings','plant_machinery','factory_office']],expected,
                  'Reported total less the three numeric category displays. Construction dash remains unquantified; this does not treat it as zero.',
                  'numeric_categories_only',[f'{year}.{stem}.construction'])
        check(f'{year}.net_from_gross',[(f'{year}.rou_net.total',1),(f'{year}.rou_gross.total',-1),(f'{year}.rou_accumulated.total',1)],1 if year==2024 else 0,
              'Reported net minus gross less accumulated depreciation, evaluated only on displayed integers.')
        check(f'{year}.depreciation_categories',[(f'{year}.rou_depreciation',1)]+[(f'{year}.rou_dep_{k}',-1) for k in ['land','plant','office']],0,'Displayed depreciation categories versus displayed total.')
        check(f'{year}.liability_categories',[(f'{year}.liability.total',1),(f'{year}.liability.current',-1),(f'{year}.liability.noncurrent',-1)],0,'Current and noncurrent carrying-value displays.')
        check(f'{year}.maturity_categories',[(f'{year}.maturity.total',1)]+[(f'{year}.maturity.{k}',-1) for k in ['due_le_1y','due_1_to_5y','due_gt_5y']],0 if year==2024 else 1,'Undiscounted maturity bands versus their displayed total.')
        check(f'{year}.maturity_carrying',[(f'{year}.maturity.carrying',1),(f'{year}.liability.total',-1)],0,'The separately reported carrying column agrees at displayed precision.')
        check(f'{year}.cash_subtotal',[(f'{year}.reconciliation.cash',1),(f'{year}.reconciliation.interest_paid',-1),(f'{year}.reconciliation.redemption',-1)],0,'Cash subtotal contains interest and redemption; do not add all three in a roll-forward.')
        terms=[(f'{year}.reconciliation.closing',1)]+[(f'{year}.reconciliation.{k}',-1) for k in ['opening','cash','expense','additions','acquisitions','fx','fair_value','sundry']]
        check(f'{year}.signed_rollforward',terms,-1 if year==2024 else 0,'Closing display less opening and signed movements. Preserve any residual; no missing transaction is inferred.')
        check(f'{year}.closing_sign',[(f'{year}.reconciliation.closing',1),(f'{year}.liability.total',1)],0,'Signed reconciliation closing versus positive liability carrying display.')
        check(f'{year}.redemption_sign',[(f'{year}.reconciliation.redemption',1),(f'{year}.cashflow_redemption',1)],0,'Positive reduction in the reconciliation versus cash-flow outflow sign.')
        check(f'{year}.all_paid_less_recognised',[(f'{year}.total_paid',1),(f'{year}.reconciliation.cash',-1)],18 if year==2024 else 16,'Descriptive gap only. Cash timing and recognised/exempt/variable scope prevent automatic expense attribution.')
        check(f'{year}.excluded_expense_sum',[(f'{year}.{k}',1) for k in ['short_term_expense','low_value_expense','variable_expense']],19 if year==2024 else 17,'Expense sum is not established as the cash residual or a cash-flow allocation.')
    check('2025.opening_continuity',[('2025.reconciliation.opening',1),('2024.reconciliation.closing',-1)],0,'Comparative and current displays in the same document, not separate publication vintages.')
    check('2025.incomplete_rou_bridge',[('2025.rou_net.total',1),('2024.rou_net.total',-1),('2025.rou_additions.total',-1),('2025.rou_depreciation',1)],-44,'Closing ROU less opening plus additions less depreciation is an incomplete bridge. Disposals, FX and other changes have not been allocated to individual rights; no cause is inferred.')
    dump('display-checks.json',{'profile':'HenkelLeaseDisplayDiagnostics/1','arithmetic':'exact rational arithmetic on displayed literals only','checks':checks})
    missing=[
        ('right_membership','Actual lease IDs, individual right IDs and complete membership','Aggregated asset categories do not enumerate contracts or rights.'),
        ('legal_owner','Legal lessee and book for each lease','Consolidated Group is not a single legal owner or native book.'),
        ('unrounded_opening','Unrounded per-right ROU and liability amounts','Rounded category totals cannot be allocated uniquely.'),
        ('functional_currency','Contract/book currency and translation history per right','Group reporting EUR does not imply every contract is denominated in EUR.'),
        ('discount_rates','Numeric discount rate and its measurement basis per right','Country/duration/credit narrative does not supply rates.'),
        ('measurement_dates','Last measurement and commencement dates per right','Reporting dates are not individual contract measurement dates.'),
        ('cash_schedules','Dated contractual cash flows, calendars and exercise terms','Undiscounted maturity buckets do not identify annual payments.'),
        ('modifications','Modification/termination sequence, affected rights and reassessment findings','Aggregate liability changes do not identify applicable method events.'),
        ('depreciation','Per-right depreciation method, term and booked amount','Category expense totals do not allocate per-right depreciation.'),
        ('scope_findings','Method-specific applicability and option/exemption findings','Narrative policies do not establish all prerequisites for a selected contract.'),
        ('full_book','Complete opening book, shared cash and funding policy','This selected disclosure audit does not bind an executable balanced company book.'),
        ('authority','Checked issuer/accounting context for a reusable lease method','Fixed synthetic historical USD method cannot be renamed as Henkel.'),
        ('publication_clock','Exact-byte public availability time and revisions','Preparation/approval date is not an availability timestamp.'),
        ('rounding_rule','Unrounded measurement or evidenced rounding rule','All figures rounded does not specify tie-breaking or independent inverse images.'),
    ]
    dump('state-dependencies.json',{'profile':'HenkelLeaseStateDependencies/1','source_representation':'bounded_inventory',
        'native_execution':'unresolved','automatic_state_conversion':False,
        'dependencies':[{'id':key,'required':required,'status':'unresolved','reason':why} for key,required,why in missing],
        'fixed_native_context':'Retain scripts/lease_shared_book_v1.py and its original_scope unchanged.',
        'apple_binder':'SourceConstrainedCompanyStateDraft/1 remains bound to its named Apple evidence.',
        'unknowns_are_zero':False,'complete_right_collection_claimed':False})
    pages=[349,353,372,373,374,375,376,399,425,426,452,453]
    pdf=fitz.open(ROOT/'data/financial-report-benchmark/documents/henkel/henkel-2025-annual/original.pdf')
    records=[]
    for n in pages:
        img=Path(f'/tmp/accdsl-henkel-lease-review/page-{n}.png')
        assert img.exists(),img
        raw=HERE/'pdf-text'/f'physical-{n}.txt'
        raw.parent.mkdir(exist_ok=True)
        raw.write_text(pdf[n-1].get_text())
        records.append({'physical_page':n,'printed_page':n-2,'text_file':f'pdf-text/physical-{n}.txt',
                        'legacy_layout_file':f'page-text/physical-{n}.txt',
                        'legacy_layout_sha256':sha256((HERE/f'page-text/physical-{n}.txt').read_bytes()).hexdigest(),
                        'legacy_layout_status':'retained prior derived reading aid; extractor not recovered; not authoritative for anchors',
                        'pdf_text_sha256':sha256(pdf[n-1].get_text().encode()).hexdigest(),
                        'rendered_review':'completed in preceding session; recovery summary retained',
                        'render_image_path':str(img),'render_image_sha256':sha256(img.read_bytes()).hexdigest()})
    dump('source-coverage.json',{'profile':'HenkelLeaseSourceCoverage/1','scope':'named lease disclosures and directly followed statement/note links',
        'whole_filing_coverage':False,'whole_note_23_coverage':False,'pages':records,
        'cross_references':[{'from_physical':375,'to_physical':[372,373,374],'purpose':'ROU PPE schedules'},
                            {'from_physical':376,'to_physical':[425,426],'printed_note_range':[400,428],'purpose':'Note23 undiscounted maturities'},
                            {'from_physical':399,'to_physical':[452,453],'purpose':'Liability carrying amounts and cash/noncash reconciliation'},
                            {'from_physical':349,'to_physical':[452,453],'purpose':'Redemption sign and cash subtotal components'}],
        'unexamined_source_occurrences':[108,393,406,487],
        'limit':'Term occurrences outside inspected pages are not covered by this package; this is not a full-report completeness claim.'})
    print(json.dumps({'display_checks':len(checks),'state_dependencies':len(missing),'reviewed_pages':len(pages)}))

if __name__=='__main__':
    main()
