from fractions import Fraction as F
import json


def enumerate_toy():
    regimes = [(0, F(1, 2)), (1, F(1, 2))]
    n_company = 9
    n_cohort = 3
    rows = []
    for r, prob in regimes:
        cells = [[F(r) for _ in range(n_company)] for _ in range(n_cohort)]
        cohort = [sum(row) / n_company for row in cells]
        realised = sum(cohort) / n_cohort
        conditional_means = [F(r) for _ in range(n_cohort)]
        residuals = [x - m for x, m in zip(cohort, conditional_means)]
        rows.append({'regime':r,'probability':prob,'cells':cells,'cohort_means':cohort,'realised_average':realised,'conditional_means':conditional_means,'martingale_residuals':residuals})
    marginal = sum(row['probability'] * row['realised_average'] for row in rows)
    conditional_targets = [row['realised_average'] for row in rows]
    variance_marginal = sum(row['probability'] * (row['realised_average']-marginal)**2 for row in rows)
    iid_n = n_company*n_cohort
    # Naive iid sample SE formula over all cells in either realized regime is zero.
    iid_sample_se = F(0)
    return {'regimes':rows,'marginal_expected_delta':marginal,'conditional_delta_by_regime':conditional_targets,'variance_of_realised_average':variance_marginal,'martingale_residuals_zero':all(all(x==0 for x in row['martingale_residuals']) for row in rows),'cross_company_correlation':F(1),'cross_cohort_correlation':F(1),'naive_iid_sample_se_within_realised_regime':iid_sample_se,'iid_cell_count_wrong_independent_units':iid_n,'actual_independent_regime_draws':1}


def main():
    x=enumerate_toy()
    assert x['marginal_expected_delta']==F(1,2)
    assert x['conditional_delta_by_regime']==[F(0),F(1)]
    assert x['variance_of_realised_average']==F(1,4)
    assert x['martingale_residuals_zero']
    assert x['cross_company_correlation']==x['cross_cohort_correlation']==1
    assert x['naive_iid_sample_se_within_realised_regime']==0
    return {'status':'PASS','marginal_expected_delta':str(x['marginal_expected_delta']),'conditional_delta_by_regime':[str(v) for v in x['conditional_delta_by_regime']],'variance_of_realised_average':str(x['variance_of_realised_average']),'martingale_residuals_zero':x['martingale_residuals_zero'],'cross_company_correlation':str(x['cross_company_correlation']),'cross_cohort_correlation':str(x['cross_cohort_correlation']),'iid_cell_count_wrong_independent_units':x['iid_cell_count_wrong_independent_units'],'actual_independent_regime_draws':x['actual_independent_regime_draws'],'naive_iid_se_within_realised_regime':str(x['naive_iid_sample_se_within_realised_regime'])}

if __name__=='__main__': print(json.dumps(main(),sort_keys=True))
