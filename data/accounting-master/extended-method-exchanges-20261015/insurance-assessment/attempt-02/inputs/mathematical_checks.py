"""Independent exact derivations. Imports neither fixtures nor builder."""
from collections import defaultdict
from datetime import date
from fractions import Fraction as F
import hashlib
import json

class Refusal(Exception):
    def __init__(self, code): self.code = code; super().__init__(code)
def need(v, code):
    if not v: raise Refusal(code)
def enc(v): return json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()
def num(v):
    f = F(int(v['n']), int(v['d']))
    need(v == q(f), 'NONCANONICAL_RATIONAL')
    return f
def q(v):
    f = F(v); return dict(n=str(f.numerator), d=str(f.denominator))
def wire(v):
    if isinstance(v, F): return q(v)
    if isinstance(v, dict): return {k: wire(x) for k, x in v.items()}
    if isinstance(v, list): return [wire(x) for x in v]
    return v
def answer(detail, *codes): return dict(status='unresolved' if codes else 'resolved', diagnostics=sorted(codes), detail=wire(detail))
def mass(rows):
    ps = [num(r['probability']) for r in rows]
    need(all(p >= 0 for p in ps) and sum(ps) == 1, 'INVALID_LAW_MASS')
    return ps
def rank(matrix):
    a = [[F(x) for x in row] for row in matrix]; r = 0
    for j in range(len(a[0])):
        p = next((i for i in range(r, len(a)) if a[i][j]), None)
        if p is None: continue
        a[r], a[p] = a[p], a[r]; d = a[r][j]; a[r] = [x/d for x in a[r]]
        for i in range(len(a)):
            if i != r:
                d = a[i][j]; a[i] = [x-d*y for x,y in zip(a[i],a[r])]
        r += 1
    return r

def derive(v):
    m = v['method_id']
    if m == 'transition.route@1':
        initial = date.fromisoformat(v['initial_application'])
        comps = [date.fromisoformat(x) for x in v['adjusted_comparatives']]
        need(initial.month == initial.day == 1 and all(x.month == x.day == 1 and x < initial for x in comps), 'UNSUPPORTED_TRANSITION_CALENDAR')
        need(date(initial.year-1,1,1) in comps and len(set(comps)) == len(comps), 'INVALID_COMPARATIVE_SET')
        d = dict(transition_date=min(comps).isoformat(), permitted_routes=[], selected_route=None, measurements_performed=False)
        need(v['historical_evidence'] != 'hindsight', 'HINDSIGHT_FORBIDDEN')
        if v['impracticable'] == 'unknown' or (v['impracticable'] == 'yes' and v['reasonable_effort'] != 'documented'):
            return answer(d, 'IMPRacticability_UNRESOLVED'.upper())
        if v['impracticable'] == 'yes':
            d['permitted_routes'] = ['modified','fair'] if v['modified_information'] == 'available' else ['fair']
            if v['requested'] == 'modified' and v['modified_information'] == 'unknown':
                return answer(d, 'MODIFIED_INFORMATION_UNRESOLVED')
        else:
            d['permitted_routes'] = ['full']
            if v['object_type'] == 'issued_group' and all(v[k] for k in ('direct_participation','prospective_mitigation','mitigation_used_before_transition')):
                d['permitted_routes'].append('fair')
        need(v['requested'] in d['permitted_routes'], 'ROUTE_NOT_PERMITTED')
        if v['requested'] == 'full':
            if v['historical_evidence'] == 'unknown': return answer(d, 'HISTORICAL_EVIDENCE_UNRESOLVED')
            need(v['historical_evidence'] == 'contemporaneous', 'FULL_HISTORICAL_SUPPORT_REQUIRED')
        d['selected_route'] = v['requested']; return answer(d)
    if m == 'transition.recovery@1':
        loss, covered, share = (num(v[k]) for k in ('group_loss','covered_loss','expected_share'))
        need(0 <= covered <= loss and 0 <= share <= 1, 'INVALID_RECOVERY_INPUT')
        t, u, e = (date.fromisoformat(v[k]) for k in ('transition_date','underlying_recognition','treaty_entry'))
        need(u <= t and e <= t and v['remaining_coverage'], 'RECOVERY_SCOPE_INVALID')
        exception = v['mode'] == 'transition'
        d = dict(loss_recovery=None, measured_held_asset=v['measured_held_asset'], held_asset_derived=False, timing_exception=exception)
        if v['recognition_admission'] != 'admitted': return answer(d, 'LOSS_RECOVERY_ADMISSION_UNRESOLVED')
        if v['coverage_allocation'] != 'admitted': return answer(d, 'COVERAGE_ALLOCATION_UNRESOLVED')
        need(exception or e <= u, 'LOSS_RECOVERY_TIMING')
        d['loss_recovery'] = covered*share
        need(v['measured_held_asset'] is None or num(v['measured_held_asset']) >= covered*share, 'RECOVERY_EXCEEDS_HELD_ASSET')
        return answer(d)
    if m == 'transition.opening@1':
        gs = v['groups']; need(len({g['group_id'] for g in gs}) == len(gs), 'DUPLICATE_GROUP')
        rows = []; old = F(0); total = F(0)
        for g in gs:
            f, value, before = (num(g[k]) for k in ('fcf','fair_value','old_liability'))
            need(min(f,value,before) >= 0, 'UNSUPPORTED_SIGNED_OPENING')
            c, loss = max(value-f,F(0)), max(f-value,F(0))
            rows.append(dict(group_id=g['group_id'], csm=c, loss_component=loss, liability=f+c))
            old += before; total += f+c
        assets, oldheld, newheld, embedded = (num(v[k]) for k in ('other_assets','old_held_asset','new_held_asset','embedded_recovery'))
        need(min(assets,oldheld,newheld,embedded) >= 0 and embedded <= newheld, 'INVALID_HELD_ASSET')
        eq0, eq1 = assets+oldheld-old, assets+newheld-total
        return answer(dict(groups=rows, old_equity=eq0, new_equity=eq1, opening_equity_change=eq1-eq0, liability=total, cash_change=F(0), current_profit=F(0), held_asset=newheld))
    if m == 'triangle.inspect@1':
        xs, mask, origins = v['cumulative'], v['structural_missing'], v['origins']
        need(len(xs) == len(mask) == len(origins) == 3 and all(len(x)==3 for x in xs+mask), 'UNSUPPORTED_TRIANGLE_SHAPE')
        need(origins == list(range(origins[0], origins[0]+3)) and date.fromisoformat(v['valuation_date']).year == origins[-1], 'TRIANGLE_DATE_MISMATCH')
        need(num(v['tail_factor']) == 1, 'UNSUPPORTED_TAIL')
        a = [[None if x is None else num(x) for x in row] for row in xs]
        for i in range(3):
            for j in range(3):
                need(mask[i][j] == (i+j>=3) and (a[i][j] is None) == mask[i][j], 'STRUCTURAL_MASK_MISMATCH')
                if a[i][j] is not None: need(a[i][j] > (a[i][j-1] if j else 0), 'MODEL_SUPPORT_FAILURE')
        factors = [sum(a[i][j+1] for i in range(2-j))/sum(a[i][j] for i in range(2-j)) for j in range(2)]
        design = [[int(i==k) for k in range(3)]+[int(j==k) for k in (1,2)] for i in range(3) for j in range(3-i)]
        p = rank(design); n = len(design); need(n > p == 5, 'UNIDENTIFIED_TRIANGLE')
        pearson = F(0); reserve = F(0)
        for i in range(3):
            jlast = 2-i; fitted = [F(0)]*3; fitted[jlast] = a[i][jlast]
            for j in range(jlast-1,-1,-1): fitted[j] = fitted[j+1]/factors[j]
            for j in range(jlast+1):
                actual_inc = a[i][j]-(a[i][j-1] if j else 0)
                fitted_inc = fitted[j]-(fitted[j-1] if j else 0)
                need(fitted_inc>0,'MODEL_SUPPORT_FAILURE'); pearson += (actual_inc-fitted_inc)**2/fitted_inc
            ultimate = a[i][jlast]
            for f in factors[jlast:]: ultimate *= f
            reserve += ultimate-a[i][jlast]
        dispersion = pearson/(n-p)
        return answer(dict(factors=factors, point_reserve=reserve, observed_cells=n, parameter_count=p, residual_degrees=n-p, raw_dispersion=dispersion, predictive_status='dispersion_unresolved' if dispersion==0 else 'law_not_evaluated', triangle_sha256=hashlib.sha256(enc(v)).hexdigest(), risk_adjustment=None), 'DISPERSION_UNRESOLVED' if dispersion==0 else 'PREDICTIVE_LAW_NOT_EVALUATED')
    return derive_law(v)

def derive_law(v):
    m = v['method_id']
    if m == 'estimation.predict@1':
        draws = v['draws']; weights = mass(draws)
        need(len({r['draw_id'] for r in draws}) == len(draws) == len({r['fit_id'] for r in draws}), 'DUPLICATE_ATTEMPT')
        dist = defaultdict(F); failed = []; unknown = F(0); cell_count = None
        for r,w in zip(draws,weights):
            if r['failure'] is not None:
                need(not r['outcomes'], 'FAILED_DRAW_HAS_OUTCOMES'); failed.append(r['draw_id']); unknown += w; continue
            outs = r['outcomes']; ps = mass(outs)
            n = len(outs[0]['cells']); need(n>0,'EMPTY_PROCESS_CELLS')
            if cell_count is None: cell_count = n
            need(n == cell_count and all(len(o['cells'])==n for o in outs),'CELL_ALIGNMENT_MISMATCH')
            means = [F(0)]*n
            for o,p in zip(outs,ps):
                cells = [num(x) for x in o['cells']]; need(all(x>=0 for x in cells),'MODEL_SUPPORT_FAILURE')
                for j,x in enumerate(cells): means[j] += p*x
                dist[sum(cells)] += w*p
            need(all(x==num(r['mean_per_cell']) for x in means),'PROCESS_MEAN_MISMATCH')
        knownmean = sum(x*p for x,p in dist.items())
        d = dict(attempted_draws=len(draws), failed_draw_ids=failed, known_mass=1-unknown, unresolved_mass=unknown, known_mean_contribution=knownmean, mean=None, variance=None, tail_probability=None, full_distribution=[], calibration='not_evaluated')
        if unknown: return answer(d,'FAILED_DRAW_MASS_UNRESOLVED')
        d.update(mean=knownmean,variance=sum(p*(x-knownmean)**2 for x,p in dist.items()),tail_probability=sum(p for x,p in dist.items() if x>num(v['threshold'])),full_distribution=[dict(amount=x,probability=p) for x,p in sorted(dist.items()) if p])
        return answer(d)
    if m == 'backward.condition@1':
        fs = v['forward']; need(len({num(r['x']) for r in fs})==len(fs),'DUPLICATE_CONDITION')
        for r in fs:
            mass(r['outcomes']); need(len({num(o['y']) for o in r['outcomes']})==len(r['outcomes']),'DUPLICATE_OUTCOME')
        d = dict(condition_mass=None,posterior=[],mean=None,variance=None,backward_law_status='unidentified')
        if v['prior'] is None: return answer(d,'BACKWARD_LAW_UNIDENTIFIED')
        pr = v['prior']; ps = mass(pr)
        need(len({num(r['x']) for r in pr})==len(pr) and {num(r['x']) for r in pr}=={num(r['x']) for r in fs},'PRIOR_SUPPORT_MISMATCH')
        likelihood = {num(r['x']):sum(num(o['probability']) for o in r['outcomes'] if num(o['y'])==num(v['observed_y'])) for r in fs}
        joint = {num(r['x']):p*likelihood[num(r['x'])] for r,p in zip(pr,ps)}; total = sum(joint.values())
        d['condition_mass'] = total
        if not total:
            d['backward_law_status']='zero_condition_mass'; return answer(d,'ZERO_CONDITION_MASS')
        mu = sum(x*p for x,p in joint.items())/total
        d.update(posterior=[dict(x=x,probability=p/total) for x,p in sorted(joint.items()) if p],mean=mu,variance=sum((x-mu)**2*p/total for x,p in joint.items()),backward_law_status='derived_from_joint')
        return answer(d)
    if m == 'reserve.error@1':
        need(v['conditioning']==v['center_conditioning'],'CONDITIONING_TARGET_MISMATCH')
        need(v['center_kind']=='reserve','RESERVE_CENTER_REQUIRED')
        paid, simulated, fitted = [[num(x) for x in v[k]] for k in ('paid','simulated_ultimate','fitted_ultimate')]
        need(len(paid)==len(simulated)==len(fitted) and all(p>=0 and s>=p and f>=p for p,s,f in zip(paid,simulated,fitted)),'RESERVE_CELL_ALIGNMENT')
        rs, rf = sum(simulated)-sum(paid), sum(fitted)-sum(paid)
        return answer(dict(simulated_reserve=rs,fitted_reserve=rf,reserve_error=rs-rf))
    if m == 'cdr.one-year@1':
        start,end = (date.fromisoformat(v[k]) for k in ('opening_date','closing_date'))
        need((end.year,end.month,end.day)==(start.year+1,start.month,start.day),'ONE_YEAR_HORIZON_REQUIRED')
        opening,paid,closing = (num(v[k]) for k in ('opening_reserve','payments','closing_reestimated_reserve'))
        need(min(opening,paid,closing)>=0,'UNSUPPORTED_SIGNED_CDR')
        return answer(dict(cdr=opening-paid-closing,opening_reserve=opening,paid=paid,closing_reserve=closing,calibration='not_evaluated'))
    if m == 'dependence.stoploss@1':
        hi,attach,p = (num(v[k]) for k in ('claim_high','attachment','marginal_high_probability'))
        need((hi,attach,p)==(40,60,F(1,2)),'UNSUPPORTED_STOPLOSS_FAMILY')
        lo,up = (num(v[k]) for k in ('parameter_min','parameter_max')); need(0<=lo<=up<=F(1,2),'INVALID_PARAMETER_INTERVAL')
        # Derive payoff from the four joint atoms, rather than assuming 20a.
        def expect(a): return sum(prob*max(x+y-attach,0) for x,y,prob in [(0,0,a),(0,hi,p-a),(hi,0,p-a),(hi,hi,a)])
        d = dict(expectation_min=min(expect(lo),expect(up)),expectation_max=max(expect(lo),expect(up)),selected_expectation=None,independent_expectation=expect(p*p),selected_joint_masses=[],second_high_after_high=None,second_high_after_zero=None,distribution_over_parameters=None)
        if v['selected_parameter'] is None: return answer(d)
        a = num(v['selected_parameter']); need(lo<=a<=up,'PARAMETER_OUTSIDE_FAMILY')
        d.update(selected_expectation=expect(a),selected_joint_masses=[a,p-a,p-a,a],second_high_after_high=a/p,second_high_after_zero=(p-a)/(1-p))
        return answer(d)
    raise Refusal('UNSUPPORTED_METHOD')

def expected_model(v):
    m = v['method_id']; z = 'not_applicable'
    group = v.get('covered_group', 'group.route' if m=='transition.route@1' else '/'.join(sorted(g['group_id'] for g in v['groups'])) if m=='transition.opening@1' else z)
    return dict(group_id=group, triangle_id=v.get('triangle_id',z),process_law_id=v.get('process_law_id',v.get('family_id',z)),backward_law_id=v.get('backward_law_id',z),conditioning=v.get('conditioning','full_triangle' if m=='triangle.inspect@1' else 'latest_diagonal' if m=='backward.condition@1' else z),horizon=v.get('horizon','lifetime_payments' if m in ('triangle.inspect@1','backward.condition@1','reserve.error@1') else z),calibration_status='not_evaluated')
