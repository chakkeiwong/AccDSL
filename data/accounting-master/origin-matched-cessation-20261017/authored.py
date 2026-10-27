"""Freeze manually derived expectations before the reference is written."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
FINDINGS = [
    'external_eligible_instruments', 'eligible_individual_items',
    'managed_together_proportional_risk', 'documented_exact_origin_matching',
    'qualifying_history', 'remaining_qualifies', 'stopped_portion_no_longer_qualifies',
    'portion_of_entire_instrument', 'zero_value_zero_cost_origins',
    'linear_zero_discount_no_carry_credit_basis', 'no_historical_ineffectiveness',
    'complete_values_and_events', 'continuing_loss_recoverable',
    'complete_stopped_loss_facts', 'inventory_recognition_and_nrv',
    'pretax_no_other_activity',
]


def write(path, value):
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2) + '\n')


def make(name, which, stop_price, terminal_price, expected, final, stopped,
         terminal, gross, loss='0', later=None, scale_q='1', scale_p='1',
         capital='300', third=False, single=False):
    """Marks are model inputs; all expected accounting amounts are literals."""
    qscale, pscale = Q(scale_q), Q(scale_p)
    origins = []
    specs = [('a', '2025-01-01', '10', '8')]
    if not single:
        specs.append(('b', '2025-04-01', '10', '9'))
    if third:
        specs.append(('c', '2025-05-01', '5', '10'))
    for key, date, qty, price in specs:
        origins.append(dict(id=key, item_id='item-' + key,
            instrument_id='forward-' + key, date=date,
            quantity=str(Q(qty)*qscale), price=str(Q(price)*pscale),
            initial_value='0', initial_cash='0', facts_available_on=date))
    z = Q(5)*qscale
    context = dict(entity='synthetic-origin-buyer', book='legal', currency='CU',
        unit='tonne', underlying='commodity-X', rule='EU2023/1803-original-IFRS9',
        maturity='2025-12-31', information_date='2026-02-01')

    def quote(key, date, price, stopped=False):
        price = Q(price)*pscale
        active = [o for o in origins if o['date'] <= date]
        values = {o['instrument_id']: str(Q(o['quantity'])*(price-Q(o['price']))) for o in active}
        items = {o['item_id']: str(-(Q(o['quantity'])-(z if stopped and o['id']==which else 0))
                    *(price-Q(o['price']))) for o in active}
        return dict(id=key, operation='measure', date=date, price=str(price),
            instrument_values=values, item_changes=items, facts_available_on=date)

    history = [quote('entry-'+o['id'], o['date'], Q(o['price'])/pscale) for o in origins]
    history.append(quote('stopping-mark', '2025-07-01', stop_price))
    after = []
    for i, (spot, still_expected, released_loss) in enumerate(later or []):
        after.append(quote('later-mark-'+str(i), '2025-10-01', spot, True))
        after.append(dict(id='assessment-'+str(i), operation='assess_stopped',
            date='2025-10-01', expected=still_expected,
            unrecoverable_loss=released_loss, facts_available_on='2025-10-01'))
    after.append(quote('terminal-mark', context['maturity'], terminal_price, True))
    still_expected = (later[-1][1] if later else expected)
    total_q = sum(Q(o['quantity']) for o in origins) - (0 if still_expected else z)
    r = dict(wire='OriginMatchedCessation/1', operation='report', context=context,
        opening_cash=capital, findings={key:True for key in FINDINGS}, origins=origins,
        history=history, stop=dict(id='named-stop', date='2025-07-01', origin_id=which,
            quantity=str(z), highly_probable=False, expected=expected,
            unrecoverable_loss=loss, facts_available_on='2025-07-01'), after=after,
        closing=dict(date=context['maturity'], quantity=str(total_q),
            unit_price=str(Q(terminal_price)*pscale),
            supplier_cash=str(total_q*Q(terminal_price)*pscale),
            settlements=deepcopy(after[-1]['instrument_values']),
            facts_available_on=context['maturity']))
    cash, inventory, profit = final
    c, f, p, d = stopped
    tc, tf, tp, td = terminal
    return dict(id=name, request=r,
        expected=dict(cash=cash, inventory=inventory, profit=profit, capital=capital,
            continuing_reserve='0', stopped_reserve='0', derivative_total='0'),
        stop_expected=dict(continuing_reserve=c, stopped_reserve=f, profit=p, derivative_total=d),
        terminal_expected=dict(continuing_reserve=tc, stopped_reserve=tf, profit=tp, derivative_total=td),
        frozen_gross=gross)


def main():
    assert not (OUT/'reference.py').exists(), 'Expectations must precede the reference'
    cases = [
        make('cancel-first','a','11','12',False, ('190','130','20'),
             ('35','0','15','50'), ('50','0','20','70'), '15'),
        make('cancel-second','b','11','12',False, ('190','125','15'),
             ('40','0','10','50'), ('55','0','15','70'), '10'),
        make('retain-first','a','11','12',True, ('130','175','5'),
             ('35','15','0','50'), ('50','15','5','70'), '15'),
        make('retain-second','b','11','12',True, ('130','175','5'),
             ('40','10','0','50'), ('55','10','5','70'), '10'),
        make('later-cancel','a','11','12',True, ('190','130','20'),
             ('35','15','0','50'), ('50','0','20','70'), '15',
             later=[('11',False,'0')]),
        make('negative-cancel','a','7','6',False, ('160','130','-10'),
             ('-25','0','-5','-30'), ('-40','0','-10','-50'), '-5'),
        make('negative-retain','a','7','6',True, ('130','165','-5'),
             ('-25','-5','0','-30'), ('-40','-5','-5','-50'), '-5'),
        make('negative-release-two','a','7','6',True, ('130','163','-7'),
             ('-25','-3','-2','-30'), ('-40','-3','-7','-50'), '-5',loss='2'),
        make('later-release-two','a','7','6',True, ('130','163','-7'),
             ('-25','-5','0','-30'), ('-40','-3','-7','-50'), '-5',
             later=[('6',True,'2')]),
        make('negative-to-positive','a','7','12',True, ('130','195','25'),
             ('-25','-5','0','-30'), ('50','-5','25','70'), '-5'),
        make('released-loss-price-reversal','a','7','12',True, ('130','193','23'),
             ('-25','-3','-2','-30'), ('50','-3','23','70'), '-5',loss='2'),
        make('positive-to-negative','a','11','6',True, ('130','145','-25'),
             ('35','15','0','50'), ('-40','15','-25','-50'), '15'),
        make('zero-stopped-origin','b','9','9',True, ('130','170','0'),
             ('10','0','0','10'), ('10','0','0','10'), '0'),
        make('no-post-stop-gain','a','11','11',False, ('185','130','15'),
             ('35','0','15','50'), ('35','0','15','50'), '15'),
        make('half-quantities','a','11','12',False, ('95','65','10'),
             ('35/2','0','15/2','25'), ('25','0','10','35'), '15/2',
             scale_q='1/2',capital='150'),
        make('double-prices','b','11','12',True, ('260','350','10'),
             ('80','20','0','100'), ('110','20','10','140'), '20',
             scale_p='2',capital='600'),
        make('exact-supplier-funding','a','11','12',False, ('70','130','20'),
             ('35','0','15','50'), ('50','0','20','70'), '15',capital='180'),
        make('full-stopped-loss-release','a','7','6',True, ('130','160','-10'),
             ('-25','0','-5','-30'), ('-40','0','-10','-50'), '-5',loss='5'),
        make('cancel-after-partial-loss','a','7','6',True, ('160','130','-10'),
             ('-25','-3','-2','-30'), ('-40','0','-10','-50'), '-5',loss='2',
             later=[('6',False,'0')]),
        make('three-origins','a','11','12',False, ('140','180','20'),
             ('40','0','15','55'), ('60','0','20','80'), '15',third=True),
        make('single-origin-comparator','a','11','12',False, ('280','40','20'),
             ('15','0','15','30'), ('20','0','20','40'), '15',single=True),
    ]
    p=OUT/'authored-cases.json'
    write(p,dict(cases=cases,nominal_counterexample=dict(aggregate='50',
        nominal_fraction='1/4',nominal_result='25/2',named_first='15',named_second='10'),
        provenance='Final, stop and terminal expectations manually derived before reference code.'))
    paths=[p,Path(__file__).resolve(),OUT/'source-reading.md',OUT/'semantic-contract.md',
        ROOT/'docs/plans/accounting-origin-matched-cessation-20261017.md',
        ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
        ROOT/'data/accounting-master/partial-hedge-discontinuation-20261016/semantic-contract.md',
        ROOT/'data/accounting-master/instrument-reduction-20261016/semantic-contract.md',
        ROOT/'data/accounting-master/zero-cost-collar-20261017/review-delta.json']
    write(OUT/'input-lock.json',dict(files=[dict(path=str(p.relative_to(ROOT)),
        sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]))
    for name in ('docs/plans/accounting-master-checkpoint.md',
                 'docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md'):
        target=OUT/'controls-before'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        assert not target.exists()
        shutil.copy2(ROOT/name,target)
    print(json.dumps(dict(authored_cases=len(cases),protected_inputs=len(paths),reference_exists=False)))


if __name__=='__main__':
    main()
