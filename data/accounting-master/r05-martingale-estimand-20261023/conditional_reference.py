"""Exact shared-regime calculation with two explicit filtrations."""

from fractions import Fraction as F
import json


def expectation(values, probabilities):
    return sum((p * v for p, v in zip(probabilities, values)), F(0))


def variance(values, probabilities):
    mu = expectation(values, probabilities)
    return expectation([(x - mu) ** 2 for x in values], probabilities)


def covariance(xs, ys, probabilities):
    mx, my = expectation(xs, probabilities), expectation(ys, probabilities)
    return expectation([(x - mx) * (y - my) for x, y in zip(xs, ys)], probabilities)


def main():
    probabilities = [F(1, 2), F(1, 2)]
    regimes = [F(0), F(1)]
    n_company, n_cohort = 9, 3
    rows = []
    for r in regimes:
        cells = [[r for _ in range(n_company)] for _ in range(n_cohort)]
        cohorts = [sum(row, F(0)) / n_company for row in cells]
        flat = [v for row in cells for v in row]
        realised = sum(flat, F(0)) / len(flat)
        sample_variance = sum(((v - realised) ** 2 for v in flat), F(0)) / (len(flat) - 1)
        known_predictable = [r] * n_cohort
        revealed_predictable = [F(1, 2)] + [r] * (n_cohort - 1)
        known_residuals = [v - m for v, m in zip(cohorts, known_predictable)]
        revealed_residuals = [v - m for v, m in zip(cohorts, revealed_predictable)]
        assert realised == sum(cohorts, F(0)) / n_cohort
        assert sum(known_predictable, F(0)) / n_cohort + sum(known_residuals, F(0)) / n_cohort == realised
        assert sum(revealed_predictable, F(0)) / n_cohort + sum(revealed_residuals, F(0)) / n_cohort == realised
        rows.append({
            'regime': str(r),
            'realised_average': str(realised),
            'initial_regime_known': {
                'predictable_means': list(map(str, known_predictable)),
                'residuals': list(map(str, known_residuals)),
                'target_given_initial_information': str(r),
            },
            'initial_information_trivial': {
                'predictable_means': list(map(str, revealed_predictable)),
                'residuals': list(map(str, revealed_residuals)),
                'target_given_initial_information': '1/2',
            },
            'iid_sample_variance': str(sample_variance),
            'iid_estimated_variance_of_average': str(sample_variance / len(flat)),
        })
    mu = expectation(regimes, probabilities)
    var = variance(regimes, probabilities)
    cross_cov = covariance(regimes, regimes, probabilities)
    correlation = cross_cov / var  # Both cells have the same positive variance.
    checks = {
        'unconditional_mean': mu == F(1, 2),
        'actual_variance': var == F(1, 4),
        'computed_cross_company_and_time_correlation': correlation == 1,
        'computed_iid_variance_zero': all(row['iid_sample_variance'] == '0' for row in rows),
        'known_initial_information_residuals_zero': all(set(row['initial_regime_known']['residuals']) == {'0'} for row in rows),
        'trivial_initial_information_first_residual_nonzero': [row['initial_information_trivial']['residuals'][0] for row in rows] == ['-1/2', '1/2'],
        'later_residuals_zero': all(set(row['initial_information_trivial']['residuals'][1:]) == {'0'} for row in rows),
        'first_residual_mean_zero': expectation([r - mu for r in regimes], probabilities) == 0,
        'first_residual_variance_retained': variance([r - mu for r in regimes], probabilities) == var,
    }
    assert all(checks.values()), checks
    return {
        'status': 'PASS', 'checks': checks, 'regimes': rows,
        'unconditional_mean': str(mu), 'actual_variance_of_average': str(var),
        'cell_covariance': str(cross_cov), 'cell_correlation': str(correlation),
        'independent_regime_draws': 1, 'nominal_cells': n_company * n_cohort,
        'population_iid_variance_if_independence_wrongly_assumed': str(var / (n_company * n_cohort)),
        'method_adopted': False,
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True))
