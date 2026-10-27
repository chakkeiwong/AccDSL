"""Exact finite counterexamples; no fitted forecasts or statistical inference."""
from fractions import Fraction as F
from pathlib import Path
import runpy

R=Path(__file__).resolve().parents[3]
crps=runpy.run_path(str(R/'data/accounting-master/r05-ocf-measurement-20261023/reference.py'))['crps']

def mixture(laws,weights):
    if len(laws)!=len(weights) or not laws or any(type(w) is not F or w<0 for w in weights) or sum(weights,F(0))!=1:
        raise ValueError('complete nonnegative exact component weights required')
    mass={}
    for law,w in zip(laws,weights):
        crps(law,F(0))
        for x,p in law:mass[x]=mass.get(x,F(0))+w*p
    return tuple(sorted((x,p) for x,p in mass.items() if p))

def cdf(law,z):
    return sum((p for x,p in law if x<=z),F(0))

def integrate(points,fn):
    knots=sorted(set(points))
    return sum(((b-a)*fn((a+b)/2) for a,b in zip(knots,knots[1:])),F(0))

def cdf_score(law,y):
    return integrate([x for x,p in law]+[y],lambda z:(cdf(law,z)-F(y<=z))**2)

def check():
    cases=[]
    def case(name,condition):
        assert condition,name
        cases.append(name)
    zero=((F(0),F(1)),);two=((F(2),F(1)),)
    third=((F(-1),F(1,4)),(F(3),F(3,4)))
    laws=(zero,two,third);weights=(F(1,2),F(1,3),F(1,6))
    pool=mixture(laws,weights);ys=tuple(map(F,(-2,0,1,2,4)))
    case('independent_cdf_and_absolute_distance_scores',all(cdf_score(law,y)==crps(law,y) for law in laws+(pool,) for y in ys))
    knots=[x for law in laws for x,p in law]
    variance=integrate(knots,lambda z:sum((w*(cdf(law,z)-cdf(pool,z))**2 for law,w in zip(laws,weights)),F(0)))
    gaps=[sum((w*crps(law,y) for law,w in zip(laws,weights)),F(0))-crps(pool,y) for y in ys]
    case('score_averaging_gap_is_positive_and_outcome_independent',variance>0 and all(g==variance for g in gaps))
    pairs=sum((weights[i]*weights[j]*integrate(knots,lambda z:(cdf(laws[i],z)-cdf(laws[j],z))**2)
               for i in range(len(laws)) for j in range(len(laws))),F(0))/2
    case('pairwise_cdf_diversity_equals_variance_gap',pairs==variance)
    same=mixture((third,third),(F(1,3),F(2,3)))
    case('identical_components_have_zero_diversity',same==third and all(crps(same,y)==crps(third,y) for y in ys))
    half=mixture((zero,two),(F(1,2),F(1,2)))
    d0=crps(half,F(0))-crps(zero,F(0));d2=crps(half,F(2))-crps(zero,F(2))
    case('locked_fixed_arm_wins_at_zero',d0==F(1,2))
    case('mixture_wins_at_two',d2==F(-3,2))
    expected=lambda p:(1-p)*d0+p*d2
    case('expected_tie_at_true_probability_one_quarter',expected(F(1,4))==0)
    case('expected_mixture_advantage_under_one_half_law',expected(F(1,2))==F(-1,2))
    case('expected_fixed_advantage_under_zero_law',expected(F(0))==F(1,2))
    split=mixture((zero,zero,two),(F(1,4),F(1,4),F(1,2)))
    case('duplicated_encoding_with_conserved_mass_is_invariant',split==half)
    counted=mixture((zero,zero,two),(F(1,3),F(1,3),F(1,3)))
    case('equal_encoding_weights_change_the_forecast_law',counted!=half and crps(counted,F(2))==F(8,9) and crps(half,F(2))==F(1,2))
    case('common_positive_asset_scaling_preserves_order',d0/F(7)>0 and d2/F(7)<0 and expected(F(1,4))/F(7)==0)
    refused=[]
    for name,bad in [('unresolved_component_mass',(F(1,2),F(1,4))),
                     ('negative_component_weight',(F(2),F(-1))),
                     ('unweighted_components',()),('float_component_weights',(0.5,0.5))]:
        try:mixture((zero,two),bad)
        except ValueError:refused.append(name)
        else:raise AssertionError(name)
    return {'passed_cases':cases,'passed_case_count':len(cases),'refused_cases':refused,
            'refused_case_count':len(refused),'independent_cdf_score_comparisons':len(laws+(pool,))*len(ys),
            'three_component_diversity':str(variance),'fixed_comparison_d0':str(d0),'fixed_comparison_d2':str(d2),
            'empirical_execution':False,'actual_issuer_forecasts':0}

if __name__=='__main__':
    import json
    print(json.dumps(check()))
