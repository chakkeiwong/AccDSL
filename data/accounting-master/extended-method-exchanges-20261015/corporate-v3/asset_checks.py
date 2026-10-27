"""Independent asset calculations from declared facts; no author/builder imports."""
from copy import deepcopy
from fractions import Fraction as F

FAMILIES = {'revaluation', 'corpassets', 'ncigoodwill', 'reversal', 'rvrestoration'}

def distribute(amount, weights, capacities, require):
    require(amount >= 0 and all(w >= 0 for w in weights) and all(c >= 0 for c in capacities), 'allocation_input_invalid')
    remaining = min(amount, sum(capacities)); result = [F(0) for _ in weights]
    while remaining:
        eligible = [i for i in range(len(weights)) if capacities[i] > result[i]]
        denominator = sum(weights[i] for i in eligible)
        require(denominator > 0, 'allocation_basis_unresolved', 'partial')
        proposed = {i: remaining * weights[i] / denominator for i in eligible}
        capped = [i for i in eligible if proposed[i] >= capacities[i] - result[i]]
        if not capped:
            for i, value in proposed.items(): result[i] += value
            remaining = F(0)
        else:
            for i in capped:
                value = capacities[i] - result[i]; result[i] += value; remaining -= value
    return result

def calculate_assets(original, method, p, require):
    c = deepcopy(original); j = {}; cash = {}
    def line(a, value): j[a] = j.get(a, F(0)) + value
    family, op = method.split('.')
    if family == 'revaluation':
        require(c['complete_membership_admitted'], 'class_membership_unresolved', 'partial')
        members = c['members']; ids = [a['asset_id'] for a in members]
        require(len(ids) == len(set(ids)), 'duplicate_asset_identity')
        if op == 'depreciate':
            require(c['zero_residual'] and c['administrative_use'], 'depreciation_model_unsupported', 'unsupported')
            require(p['consumption_period_admitted'], 'consumption_period_unresolved', 'partial')
            for a in members:
                require(a['status'] == 'active' and 0 < p['years'] <= a['life'], 'depreciation_period_invalid')
                charge = (a['gross'] - a['accumulated']) * p['years'] / a['life']
                a['accumulated'] += charge; a['life'] -= p['years']
                line('ppe', -charge); line('expense', charge)
        elif op == 'measure':
            values = p['values']; value_ids = [a['asset_id'] for a in values]
            require(len(value_ids) == len(set(value_ids)) and set(value_ids) == set(ids), 'whole_class_required')
            require(p['whole_class_current'] and p['reliable_values'] and all(a['fair_value'] is not None for a in values),
                'class_valuation_unresolved', 'partial')
            by_id = {a['asset_id']: a['fair_value'] for a in values}
            for a in members:
                require(a['status'] == 'active' and by_id[a['asset_id']] >= 0, 'valuation_input_invalid')
                change = by_id[a['asset_id']] - (a['gross'] - a['accumulated'])
                line('ppe', change)
                if change >= 0:
                    gain = min(change, a['prior_loss']); reserve = change - gain
                    a['prior_loss'] -= gain; a['surplus'] += reserve
                    line('income', -gain); line('oci_revaluation', -reserve)
                else:
                    reserve = min(-change, a['surplus']); loss = -change - reserve
                    a['surplus'] -= reserve; a['prior_loss'] += loss
                    line('oci_revaluation', reserve); line('expense', loss)
                a['gross'] = by_id[a['asset_id']]; a['accumulated'] = F(0)
            c['valuation_sequence'] += 1
        elif op == 'dispose':
            require(p['control_passed'] and p['depreciation_current'], 'disposal_admission_unresolved', 'partial')
            require(len(p['asset_ids']) == len(set(p['asset_ids'])) and set(p['asset_ids']) <= set(ids) and p['cash'] >= 0,
                'disposal_members_invalid')
            amount = F(0)
            for a in members:
                if a['asset_id'] not in p['asset_ids']: continue
                require(a['status'] == 'active', 'asset_already_disposed')
                amount += a['gross'] - a['accumulated']
                a.update(gross=F(0), accumulated=F(0), status='disposed')
            line('ppe', -amount); line('cash', p['cash']); cash['investing'] = p['cash']
            if p['cash'] >= amount: line('income', amount - p['cash'])
            else: line('expense', amount - p['cash'])
        elif op == 'transfer':
            require(p['asset_id'] in ids and p['election_admitted'], 'surplus_transfer_admission')
            a = members[ids.index(p['asset_id'])]
            require(a['status'] == 'disposed', 'during_use_transfer_not_in_profile', 'unsupported')
            require(0 <= p['amount'] <= a['surplus'], 'surplus_transfer_exceeds_balance')
            a['surplus'] -= p['amount']; c['surplus_transferred'] += p['amount']
            line('oci_revaluation', p['amount']); line('retained', -p['amount'])
    elif family == 'corpassets':
        require(c['smallest_group_admitted'] and c['individual_allocation_unavailable'], 'corporate_allocation_unresolved', 'partial')
        require(p['perimeter_consistent'], 'impairment_perimeter_mismatch')
        require(p['recoverable'] is not None, 'measurement_unresolved', 'partial')
        require(p['recoverable'] >= 0 and not c['group_tested'], 'corporate_test_order')
        if op == 'test_unit':
            matching = [u for u in c['units'] if u['unit_id'] == p['unit_id']]
            require(len(matching) == 1 and not matching[0]['tested'], 'corporate_test_order')
            assets = [a for a in c['assets'] if a['unit_id'] == p['unit_id']]
            require(bool(assets) and c['corporate_asset_id'] not in [a['asset_id'] for a in assets], 'corporate_asset_wrong_unit')
            matching[0].update(tested=True, recoverable=p['recoverable'])
        else:
            require(all(u['tested'] for u in c['units']), 'leaf_tests_required')
            assets = c['assets']; c.update(group_tested=True, group_recoverable=p['recoverable'])
        require(all(a['floor_assessed'] and a['floor'] is not None for a in assets), 'individual_floor_unresolved', 'partial')
        carrying = [a['carrying'] for a in assets]
        requested = max(F(0), sum(carrying) - p['recoverable'])
        capacities = [a['carrying'] - a['floor'] for a in assets]
        losses = distribute(requested, carrying, capacities, require)
        require(sum(losses) == requested, 'unallocated_loss_requires_review', 'partial')
        for a, loss in zip(assets, losses): a['carrying'] -= loss
        c['loss_to_date'] += sum(losses); line('ppe', -sum(losses)); line('expense', sum(losses))
    elif family == 'ncigoodwill':
        require(not c['tested'], 'goodwill_test_already_applied')
        require(p['perimeter_consistent'] and p['profit_allocation_matches_ownership'], 'nci_allocation_unresolved', 'partial')
        require(p['recoverable'] is not None, 'measurement_unresolved', 'partial')
        parts = c['parts']
        require(len({a['part_id'] for a in parts}) == len(parts), 'duplicate_part_identity')
        for a in parts:
            require(0 < a['ownership'] <= 1 and a['identifiable'] >= 0 and a['test_goodwill'] >= 0, 'nci_input_invalid')
            require(a['proportional_goodwill_admitted'] and a['zero_floor_admitted'], 'nci_measurement_unresolved', 'partial')
            require(a['ownership'] == 1 or a['proportionate_nci'], 'nci_measurement_election_unsupported', 'unsupported')
            require(a['reported_goodwill'] == a['test_goodwill'] * a['ownership'], 'notional_goodwill_mismatch')
        goodwill = sum(a['test_goodwill'] for a in parts); identifiable = sum(a['identifiable'] for a in parts)
        require(p['recoverable'] >= 0, 'nci_input_invalid')
        loss = max(F(0), goodwill + identifiable - p['recoverable']); gwloss = min(loss, goodwill); assetloss = loss - gwloss
        parent = nci = unrecognized = posted_gw = F(0)
        for a in parts:
            g = gwloss * a['test_goodwill'] / goodwill if goodwill else F(0)
            v = assetloss * a['identifiable'] / identifiable if identifiable else F(0)
            pg = g * a['ownership']; ng = g - pg
            a['test_goodwill'] -= g; a['reported_goodwill'] -= pg; a['identifiable'] -= v
            parent += pg + v * a['ownership']; nci += v * (1 - a['ownership'])
            unrecognized += ng; posted_gw += pg
        recognized = parent + nci
        c.update(tested=True, recoverable=p['recoverable'], recognized_loss=recognized,
            unrecognized_loss=unrecognized, parent_loss=parent, nci_loss=nci)
        line('goodwill', -posted_gw); line('ppe', -assetloss); line('expense', recognized)
    elif family == 'reversal':
        assets = c['assets']
        if op == 'depreciate':
            require(c['phase'] == 'impaired' and p['zero_residual_straight_line'], 'reversal_depreciation_scope')
            for a in assets:
                require(0 < p['years'] < a['life'], 'depreciation_period_invalid')
                current = a['gross'] - a['accumulated'] - a['allowance']
                charge = current * p['years'] / a['life']
                a['no_impairment_carrying'] *= 1 - p['years'] / a['life']
                a['accumulated'] += charge; a['life'] -= p['years']
                line('ppe', -charge); line('expense', charge)
            c['phase'] = 'depreciated'
        else:
            require(c['phase'] == 'depreciated', 'reversal_event_order')
            require(p['changed_estimates_admitted'], 'changed_estimates_required', 'partial')
            require(p['recoverable'] is not None and all(a['individual_assessed'] for a in assets), 'measurement_unresolved', 'partial')
            require(p['recoverable'] >= 0, 'reversal_input_invalid')
            weights = [a['gross'] - a['accumulated'] - a['allowance'] for a in assets]
            caps = [min(a['no_impairment_carrying'], a['individual_recoverable'])
                if a['individual_recoverable'] is not None else a['no_impairment_carrying'] for a in assets]
            capacities = [max(F(0), cap - w) for cap, w in zip(caps, weights)]
            amounts = distribute(max(F(0), p['recoverable'] - sum(weights) - c['goodwill']), weights, capacities, require)
            for a, value in zip(assets, amounts):
                require(value <= a['allowance'], 'reversal_exceeds_prior_allowance')
                a['allowance'] -= value
            line('ppe', sum(amounts)); line('income', -sum(amounts))
            c.update(phase='reversed', unit_recoverable=p['recoverable'])
    elif family == 'rvrestoration':
        require(p['measurement_current'] and p['new_liability'] >= 0, 'restoration_measurement_unresolved', 'partial')
        require(c['class_valuation_current'] and p['class_review_supports_unchanged_ppe'], 'class_revaluation_required', 'partial')
        change = p['new_liability'] - c['liability']; profit = oci = F(0)
        if c['asset_exhausted']:
            require(c['ppe'] == 0, 'exhausted_asset_has_carrying_value')
            profit = -change
        elif change > 0:
            used = min(change, c['surplus']); c['surplus'] -= used
            oci = -used; profit = -(change - used); c['prior_loss'] += change - used
        else:
            require(c['cost_model_carrying'] is not None, 'cost_model_carrying_unresolved', 'partial')
            decrease = -change; excess = max(F(0), decrease - c['cost_model_carrying'])
            reversal = min(decrease - excess, c['prior_loss']); c['prior_loss'] -= reversal
            profit = excess + reversal; oci = decrease - profit; c['surplus'] += oci
        c.update(liability=p['new_liability'], restoration_oci=c['restoration_oci'] + oci)
        line('provision', -change); line('oci_revaluation', -oci)
        if profit >= 0: line('income', -profit)
        else: line('expense', -profit)
    else:
        raise AssertionError(method)
    return c, {k: v for k, v in j.items() if v}, {k: cash.get(k, F(0)) for k in ['operating', 'investing', 'financing', 'unclassified']}

def check_asset_component(tag, c, b):
    if tag == 'revaluation_class':
        assert b['ppe'] == sum(a['gross'] - a['accumulated'] for a in c['members'])
        assert -b['oci_revaluation'] == sum(a['surplus'] for a in c['members'])
        assert all(a['gross'] >= a['accumulated'] >= 0 and a['surplus'] >= 0 and a['prior_loss'] >= 0 for a in c['members'])
    elif tag == 'corporate_assets':
        assert b['ppe'] == sum(a['carrying'] for a in c['assets'])
        assert len({a['asset_id'] for a in c['assets']}) == len(c['assets'])
        assert len({u['unit_id'] for u in c['units']}) == len(c['units'])
        corporate = [a for a in c['assets'] if a['asset_id'] == c['corporate_asset_id']]
        assert len(corporate) == 1 and corporate[0]['unit_id'] == c['group_id']
        assert all(a['unit_id'] in {u['unit_id'] for u in c['units']} | {c['group_id']} for a in c['assets'])
    elif tag == 'partial_goodwill':
        assert b['goodwill'] == sum(a['reported_goodwill'] for a in c['parts'])
        assert b['ppe'] == sum(a['identifiable'] for a in c['parts'])
        assert c['parent_loss'] + c['nci_loss'] == c['recognized_loss']
        assert b['expense'] == c['recognized_loss']
    elif tag == 'reversal':
        assert b['ppe'] == sum(a['gross'] - a['accumulated'] - a['allowance'] for a in c['assets'])
        assert b['goodwill'] == c['goodwill']
        assert all(a['allowance'] >= 0 and a['gross'] >= a['accumulated'] + a['allowance'] for a in c['assets'])
    elif tag == 'restoration_revalued':
        assert b['ppe'] == c['ppe'] and -b['provision'] == c['liability'] and -b['oci_revaluation'] == c['surplus']
    else:
        raise AssertionError(tag)
