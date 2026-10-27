"""Independent hand-expanded coefficient oracle; does not import the candidate."""
from copy import deepcopy
COMMON={
 'net_identifiable_assets':{'A':'1/1','L':'-1/1'},
 'qualifying_prior_equity':{},
 'post_control_profit':{'R':'1/1','D':'-1/1'},
 'post_control_oci':{'O':'1/1','U':'1/1'},
 'owners_profit':{'R':'3/4','D':'-3/4'},
 'nci_profit':{'R':'1/4','D':'-1/4'},
 'owners_oci':{'O':'3/4','U':'3/4'},
 'nci_oci':{'O':'1/4','U':'1/4'}}
PROPORTIONAL={**COMMON,
 'nci_at_acquisition':{'A':'1/4','L':'-1/4'},
 'acquisition_excess':{'T':'1/1','A':'-3/4','L':'3/4'},
 'nci_closing':{'A':'1/4','L':'-1/4','R':'1/4','D':'-1/4','O':'1/4','U':'1/4','V':'-1/1','M':'1/1'}}
FAIR_VALUE={**COMMON,
 'nci_at_acquisition':{'Q':'1/1'},
 'acquisition_excess':{'T':'1/1','Q':'1/1','A':'-1/1','L':'1/1'},
 'nci_closing':{'Q':'1/1','R':'1/4','D':'-1/4','O':'1/4','U':'1/4','V':'-1/1','M':'1/1'}}
FULL={**COMMON,
 'nci_at_acquisition':{},'acquisition_excess':{'T':'1/1','A':'-1/1','L':'1/1'},
 'owners_profit':{'R':'1/1','D':'-1/1'},'nci_profit':{},
 'owners_oci':{'O':'1/1','U':'1/1'},'nci_oci':{},'nci_closing':{}}
def expected(election='proportional',prior='none'):
    coefficients=deepcopy({'proportional':PROPORTIONAL,'fair_value':FAIR_VALUE,'none':FULL}[election])
    if prior=='equity':
        coefficients['qualifying_prior_equity']={'P':'1/1'}
        coefficients['acquisition_excess']['P']='1/1'
    return {name:dict(constant='0/1',coefficients=dict(sorted(c.items()))) for name,c in coefficients.items()}
