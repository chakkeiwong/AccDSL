"""Closed types for the promised asset methods, separate from their arithmetic."""

def extend(components, events, obj, arr, enum, maybe, Q, ID, BOOL, INT):
    rv_asset = obj({'asset_id': ID, **{k: Q for k in ['gross', 'accumulated', 'life', 'surplus', 'prior_loss']},
                    'status': enum('active', 'disposed')})
    floor_asset = obj({'asset_id': ID, 'unit_id': ID, 'carrying': Q, 'floor': maybe(Q),
                       'floor_assessed': BOOL})
    reversal_asset = obj({'asset_id': ID, **{k: Q for k in ['gross', 'accumulated', 'allowance',
        'no_impairment_carrying', 'life']}, 'individual_recoverable': maybe(Q), 'individual_assessed': BOOL})
    components.update({
        'revaluation_class': obj({'class_id': ID, 'members': arr(rv_asset, 1),
            'complete_membership_admitted': BOOL, 'zero_residual': BOOL, 'administrative_use': BOOL,
            'valuation_sequence': INT, 'surplus_transferred': Q}),
        'corporate_assets': obj({'group_id': ID, 'corporate_asset_id': ID, 'assets': arr(floor_asset, 1),
            'units': arr(obj({'unit_id': ID, 'tested': BOOL, 'recoverable': maybe(Q)}), 1),
            'group_recoverable': maybe(Q), 'smallest_group_admitted': BOOL,
            'individual_allocation_unavailable': BOOL, 'group_tested': BOOL, 'loss_to_date': Q}),
        'partial_goodwill': obj({'group_id': ID, 'parts': arr(obj({'part_id': ID,
            'ownership': Q, 'reported_goodwill': Q, 'test_goodwill': Q, 'identifiable': Q,
            'proportionate_nci': BOOL, 'proportional_goodwill_admitted': BOOL,
            'zero_floor_admitted': BOOL}), 1), 'tested': BOOL, 'recoverable': maybe(Q),
            **{k: Q for k in ['recognized_loss', 'unrecognized_loss', 'parent_loss', 'nci_loss']}}),
        'reversal': obj({'unit_id': ID, 'assets': arr(reversal_asset, 1), 'goodwill': Q,
            'goodwill_loss': Q, 'unit_recoverable': Q, 'phase': enum('impaired', 'depreciated', 'reversed')}),
        'restoration_revalued': obj({'asset_id': ID, 'liability_id': ID,
            **{k: Q for k in ['ppe', 'liability', 'surplus', 'prior_loss', 'restoration_oci']},
            'cost_model_carrying': maybe(Q), 'asset_exhausted': BOOL, 'class_valuation_current': BOOL}),
    })
    events.update({
        'revaluation.depreciate': ('revaluation_class', obj({'years': Q, 'consumption_period_admitted': BOOL})),
        'revaluation.measure': ('revaluation_class', obj({'values': arr(obj({'asset_id': ID, 'fair_value': maybe(Q)}), 1),
            'reliable_values': BOOL, 'whole_class_current': BOOL})),
        'revaluation.dispose': ('revaluation_class', obj({'asset_ids': arr(ID, 1), 'cash': Q, 'control_passed': BOOL,
            'depreciation_current': BOOL})),
        'revaluation.transfer': ('revaluation_class', obj({'asset_id': ID, 'amount': Q, 'election_admitted': BOOL})),
        'corpassets.test_unit': ('corporate_assets', obj({'unit_id': ID, 'recoverable': maybe(Q), 'perimeter_consistent': BOOL})),
        'corpassets.test_group': ('corporate_assets', obj({'recoverable': maybe(Q), 'perimeter_consistent': BOOL})),
        'ncigoodwill.impair': ('partial_goodwill', obj({'recoverable': maybe(Q), 'profit_allocation_matches_ownership': BOOL,
            'perimeter_consistent': BOOL})),
        'reversal.depreciate': ('reversal', obj({'years': Q, 'zero_residual_straight_line': BOOL})),
        'reversal.restore': ('reversal', obj({'recoverable': maybe(Q), 'changed_estimates_admitted': BOOL})),
        'rvrestoration.change': ('restoration_revalued', obj({'new_liability': Q, 'measurement_current': BOOL,
            'class_review_supports_unchanged_ppe': BOOL})),
    })
