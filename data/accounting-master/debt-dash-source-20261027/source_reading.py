"""Explicit named-source selection; never change a PDF observation in place."""
from fractions import Fraction
from copy import deepcopy
GAAP='http://fasb.org/us-gaap/2024'
CONCEPT='{'+GAAP+'}ProceedsFromIssuanceOfLongTermDebt'
PDF_LABEL='Proceeds from issuance of term debt, net'
PERIOD={'startDate':'2023-10-01','endDate':'2024-09-28'}
ENTITY={'scheme':'http://www.sec.gov/CIK','identifier':'0000320193'}
UNIT='{http://www.xbrl.org/2003/iso4217}USD'

class Refusal(ValueError):pass
def need(ok,reason):
    if not ok:raise Refusal(reason)

def select(facts, binding):
    """Binding is supplied separately after source inspection, not generated here."""
    need(set(binding)=={'archive_sha256','instance_sha256','pdf_sha256','occurrence_ids','fact_sha256'},'binding_fields')
    selected=[]
    for f in facts:
        if f['concept']!=CONCEPT or f['context']['period']!=PERIOD:continue
        if f['context']['entity']!=ENTITY or f['context']['dimensions'] or f['context']['other_children']:continue
        selected.append(f)
    need(bool(selected),'missing_exact_context_fact')
    need([f['id'] for f in selected]==binding['occurrence_ids'],'occurrence_selection')
    for f in selected:
        need(f['unit']==UNIT,'unit_mismatch')
        need(f['nil'] is False,'nil_is_not_reported_number')
        need(f['decimals']=='-6','accuracy_mismatch')
        need(f['pdf_label']==PDF_LABEL,'caption_mismatch')
        need(f['presentation_role']=='http://www.apple.com/role/CONSOLIDATEDSTATEMENTSOFCASHFLOWS','presentation_role')
        need(f['calculation_weight']=='1.0','cashflow_sign')
        for k in ['archive_sha256','instance_sha256','pdf_sha256']:need(f[k]==binding[k],'source_identity:'+k)
        need(f['fact_sha256']==binding['fact_sha256'][f['id']],'fact_identity')
        need(Fraction(f['value'])==0,'reviewed_reported_value')
    return {'profile':'RetainedDebtIssuanceReading/1','status':'reported_value_alternative',
            'original_literal':'—','reported_value_usd':'0/1','displayed_value_usd_million':'0/1',
            'decimals':'-6','period':deepcopy(PERIOD),'entity':deepcopy(ENTITY),
            'occurrences':deepcopy(selected),'binding':deepcopy(binding),
            'original_observation_changed':False,'source_admission':False,'accounting_admission':False,
            'actual_history':'unknown','exact_economic_zero':False,'historical_information_cutoff_checked':False,
            'interpretation':'A separately retained named-source numerical reading at reported accuracy; no global dash-to-zero rule.'}
