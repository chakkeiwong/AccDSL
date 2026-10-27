"""Exact scale identities and a declared evidence-selection rule; no forecasts."""
from fractions import Fraction as F


def eligible_latest(rows, cutoff):
    """Fictional date-ordered rows; exact authenticated availability assumed."""
    eligible = [r for r in rows if r['period'] <= cutoff and r['available'] <= cutoff
                and r['mapped'] and r['scope'] == 'group' and r['amount'] > 0]
    if not eligible:
        return None
    last = max(r['period'] for r in eligible)
    choices = [r for r in eligible if r['period'] == last]
    if len(choices) != 1:
        return 'unresolved_version_tie'
    return choices[0]['id']


def check():
    cases = []
    def case(name, condition):
        assert condition, name
        cases.append(name)
    # Generic loss differences in money; these are not issuer scores.
    loss, assets, factor = F(-2), F(10), F(7,3)
    case('same_positive_currency_conversion_cancels', factor*loss/(factor*assets) == loss/assets)
    case('thousands_to_base_units_cancels', (loss*1000)/(assets*1000) == loss/assets)
    case('one_sided_unit_conversion_is_wrong', loss/(assets*1000) != loss/assets)
    rows=[{'id':'old','period':'2024-12-31','available':'2025-03-01','mapped':True,'scope':'group','amount':F(10)},
          {'id':'interim','period':'2025-06-30','available':'2025-08-01','mapped':True,'scope':'group','amount':F(11)},
          {'id':'late_annual','period':'2025-12-31','available':'2026-03-01','mapped':True,'scope':'group','amount':F(12)},
          {'id':'parent','period':'2025-09-30','available':'2025-11-01','mapped':True,'scope':'parent','amount':F(100)}]
    case('latest_available_group_not_latest_held_period',eligible_latest(rows,'2025-12-30')=='interim')
    case('later_release_changes_selection_only_at_later_cutoff',eligible_latest(rows,'2026-03-02')=='late_annual')
    case('ambiguous_latest_version_not_arbitrary_tie_break',eligible_latest(rows+[dict(rows[1],id='conflict',amount=F(13))],'2025-12-30')=='unresolved_version_tie')
    case('no_eligible_scale_preserves_unknown',eligible_latest(rows,'2024-01-01') is None)
    return {'passed_cases':cases,'passed_case_count':len(cases),'actual_issuer_scores':0,
            'as_of_admissions':0,'empirical_execution':False}


if __name__=='__main__':
    import json
    print(json.dumps(check()))
