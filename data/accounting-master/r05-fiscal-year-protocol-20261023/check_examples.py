"""Exact fictional calendar/weight checks; no empirical data or inference."""
from datetime import date, timedelta
from fractions import Fraction as F

ISSUERS = ('apple', 'caterpillar', 'jpmorgan', 'henkel', 'hsbc',
           'munich_re', 'saic_motor', 'ping_an', 'midea')


def apple_interval(year):
    """Conditional extrapolation of the inspected 2025 rule, not future evidence."""
    def ending(y):
        d = date(y, 9, 30)
        return d - timedelta(days=(d.weekday()-5) % 7)
    return ending(year-1)+timedelta(days=1), ending(year)+timedelta(days=1)


def next_full(cutoff, intervals, calendar_complete):
    """Dates denote exact fictional midnight instants in a shared timezone."""
    if not calendar_complete:
        raise ValueError('cannot establish next interval from an incomplete calendar')
    if not intervals or any(a >= b for a,b in intervals):
        raise ValueError('invalid intervals')
    if any(intervals[i][1] != intervals[i+1][0] for i in range(len(intervals)-1)):
        raise ValueError('calendar not ordered and contiguous')
    if cutoff < intervals[0][0]:
        raise ValueError('left calendar coverage does not establish the next interval')
    for a,b in intervals:
        if cutoff < a:
            return a,b
    raise ValueError('no complete future interval supplied')


def strictly_before(a, b):
    if a is None or b is None:
        return 'unverified'
    if a[0] > a[1] or b[0] > b[1]:
        raise ValueError('reversed bounds')
    if a[1] < b[0]:
        return 'supported'
    if a[0] >= b[1]:
        return 'contradicted'
    return 'unverified'


def aggregate(schedule):
    """Only fictional numeric paired losses; None retains an unavailable cell."""
    if set(schedule) != set(ISSUERS):
        raise ValueError('fixed issuer panel differs')
    weight, contribution, missing, counts = F(0), F(0), [], [0,0]
    for issuer, cells in schedule.items():
        if not cells or any(not isinstance(b,F) or b < 0 for _,b,_ in cells):
            raise ValueError('empty history or invalid time weights')
        if len({key for key,_,_ in cells}) != len(cells):
            raise ValueError('duplicate origin')
        if sum((b for _,b,_ in cells),F(0)) != 1:
            raise ValueError('issuer time weights do not sum to one')
        for key,b,d in cells:
            counts[0] += 1
            alpha = b/9
            if d is None:
                if alpha > 0:
                    missing.append((issuer,key))
                continue
            if not isinstance(d,F):
                raise ValueError('exact rational example required')
            counts[1] += 1
            weight += alpha
            contribution += alpha*d
    return {'coverage_weight': weight, 'contribution': contribution,
            'conditional_mean': contribution/weight if weight else None,
            'full_effect': None if missing else contribution,
            'missing_positive_cells': missing, 'counts': counts}


def check():
    intervals = [apple_interval(y) for y in range(2025,2030)]
    assert apple_interval(2025) == (date(2024,9,29), date(2025,9,28))
    assert (intervals[0][1]-intervals[0][0]).days == 364
    assert apple_interval(2028) == (date(2027,9,26), date(2028,10,1))
    assert (apple_interval(2028)[1]-apple_interval(2028)[0]).days == 371
    assert (date(2028,1,1)-date(2027,1,1)).days == 365
    assert (date(2029,1,1)-date(2028,1,1)).days == 366
    assert next_full(date(2026,10,23), intervals, True) == apple_interval(2028)
    assert next_full(date(2026,9,26), intervals, True) == apple_interval(2027)
    assert next_full(date(2026,9,27), intervals, True) == apple_interval(2028)
    assert next_full(date(2026,10,23), [(date(y,1,1),date(y+1,1,1)) for y in range(2025,2029)], True) == (date(2027,1,1), date(2028,1,1))
    timing = [(((1,1),(2,2)), 'supported'), (((2,2),(2,2)), 'contradicted'),
              (((3,3),(2,2)), 'contradicted'), (((1,3),(2,2)), 'unverified'),
              ((None,(2,2)), 'unverified')]
    for args,want in timing:
        assert strictly_before(*args) == want
    schedule = {i: [('a',F(1,2),F(1)),('b',F(1,2),F(1))] for i in ISSUERS}
    schedule['apple'] = [('a',F(1),F(-8))]
    full = aggregate(schedule)
    assert full['full_effect'] == 0 and full['coverage_weight'] == 1
    assert full['counts'] == [17,17]
    assert sum(d for cells in schedule.values() for _,_,d in cells)/17 == F(8,17)
    schedule['apple'] = [('a',F(1),None)]
    partial = aggregate(schedule)
    assert partial['coverage_weight'] == F(8,9) and partial['contribution'] == F(8,9)
    assert partial['conditional_mean'] == 1 and partial['full_effect'] is None
    assert partial['counts'] == [17,16]
    empty = aggregate({i: [('a',F(1),None)] for i in ISSUERS})
    assert empty['conditional_mean'] is None and empty['full_effect'] is None
    assert empty['coverage_weight'] == 0 and empty['counts'] == [9,0]
    zero = {i: [('a',F(1),F(1)),('unavailable',F(0),None)] for i in ISSUERS}
    assert aggregate(zero)['full_effect'] == 1
    refusals = [
        lambda: next_full(date(2026,10,23), intervals, False),
        lambda: next_full(date(2023,1,1), intervals, True),
        lambda: next_full(date(2030,1,1), intervals, True),
        lambda: next_full(date(2026,1,1), intervals[::2], True),
        lambda: strictly_before((2,1),(3,3)),
        lambda: aggregate({i:c for i,c in schedule.items() if i != 'apple'}),
        lambda: aggregate({**schedule,'apple': []}),
        lambda: aggregate({**schedule,'apple': [('a',F(1,2),F(1))]}),
        lambda: aggregate({**schedule,'apple': [('a',F(2),F(1)),('b',F(-1),F(1))]}),
        lambda: aggregate({**schedule,'apple': [('a',F(1,2),F(1)),('a',F(1,2),F(1))]})]
    for f in refusals:
        try:
            f()
        except ValueError:
            pass
        else:
            raise AssertionError('invalid illustrative input accepted')
    return {'calendar_assertions': 10, 'strict_prestart_cases': len(timing),
            'weight_scenarios': 5, 'invalid_input_refusals': len(refusals),
            'empirical_observations_used': 0, 'inference_admitted': False}


if __name__ == '__main__':
    import json
    print(json.dumps(check()))
