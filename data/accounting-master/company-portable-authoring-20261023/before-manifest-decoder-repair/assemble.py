"""Deterministic correspondence from original files to explicit typed records."""
from portable import Builder, FLAGS, PROFILE, canonical, legacy_digest

# Roles are local fixed data labels, never packet-supplied executable paths.
FILES = {
    'family_draft': ('company-family-20261023/fixture.json', 'CompanyScenarioFamilyDraft/1'),
    'family_result': ('company-family-20261023/result.json', 'CompanyScenarioFamilyResultDraft/1'),
    'program': ('company-expressions-20261023/fixture.json', 'CompanyExpressionsDraft/1'),
    'base_policy': ('company-policy-20261023/policy.json', 'SettlementPolicyDraft/1'),
    'expression_materialization': ('company-expressions-20261023/materialization.json', 'ExpressionPolicyMaterializationDraft/1'),
    'expression_result': ('company-expressions-20261023/accounting-result.json', 'CompanyPathResultDraft/1'),
    'recovery_fixture': ('company-recovery-20261023/fixture.json', 'CompanyScenarioFamilyDraft/1'),
    'recovery_method': ('company-recovery-20261023/method-lock.json', 'LocalRecoveryMethodDescriptor/1'),
    'recovery_response': ('company-recovery-20261023/final-result.json', 'CompanyFamilyResumeResultDraft/1'),
}


def assemble(raw_files, source, family):
    if set(raw_files) != set(FILES):
        raise ValueError('original-file roles differ')
    b = Builder()
    imports = {role: b.imported(role, raw_files[role], profile)
               for role, (_, profile) in FILES.items()}
    value = lambda ref: b.values[ref['digest']]
    draft, result = value(imports['family_draft']), value(imports['family_result'])
    family.validate(draft)
    if len(draft['members']) != len(result['members']):
        raise ValueError('member result coverage')
    members, paths, member_results = [], {}, {}
    def extract(role, parent, pointer, profile='LegacyValueDraft/1'):
        return b.extract(role, parent, pointer, profile)
    for i, (member, outcome) in enumerate(zip(draft['members'], result['members'])):
        if member['id'] != outcome['id']:
            raise ValueError('member ordering')
        prefix = 'member/' + str(i)
        path_ref = extract(prefix+'/path', imports['family_draft'], '/members/'+str(i)+'/path', 'CompanyPathDraft/1')
        run_ref = extract(prefix+'/result', imports['family_result'], '/members/'+str(i)+'/result', 'CompanyPathResultDraft/1')
        run = value(run_ref)
        if outcome['path_sha256'] != legacy_digest(member['path']) or outcome['result_sha256'] != legacy_digest(run) or outcome['status'] != run['status']:
            raise ValueError('family member identities')
        years = []
        for j, year in enumerate(run['years']):
            year_ref = extract(prefix+'/year/'+str(j), run_ref, '/years/'+str(j), 'CompanyYearResultDraft/1')
            report_ref = extract(prefix+'/report/'+str(j), year_ref, '/report', 'CompanyAnnualReportDraft/1')
            complete = year['run']['status'] == 'complete_conditional'
            if not complete and ('closing_memory' in year or year['report'].get('annual_complete') is True):
                raise ValueError('partial year claims a complete closing')
            memory_ref = extract(prefix+'/memory/'+str(j), year_ref, '/closing_memory', 'CompanyClosingMemoryDraft/1') if complete else None
            years.append(b.record('AnnualOutcome', prefix+'/annual/'+str(j), {
                'index': j, 'period': year['period'], 'year_ref': year_ref,
                'report_ref': report_ref, 'outcome': 'complete_conditional' if complete else 'partial',
                'closing_memory_ref': memory_ref, 'historical_admission': False}))
        ref = b.record('Member', prefix, {'name': member['id'], 'path_ref': path_ref,
            'result_ref': run_ref, 'context_ref': extract(prefix+'/context', path_ref, '/initial_year/context'),
            'opening_sha256': family.common(member['path'])['opening_sha256'],
            'year_refs': years, 'unexecuted_ref': extract(prefix+'/unexecuted', run_ref, '/unexecuted'),
            'status': run['status']})
        members.append(ref)
        paths.setdefault(legacy_digest(member['path']), []).append((ref, path_ref))
        member_results[ref['digest']] = run
    family_ref = b.record('Family', 'family', {'draft_ref': imports['family_draft'],
        'result_ref': imports['family_result'], 'member_refs': members, 'common': draft['common'],
        'meaning': draft['meaning'], 'weighting': draft['weighting'], 'coverage': draft['coverage']})
    policy = value(imports['base_policy'])
    parents = paths.get(policy['parent_path_sha256'], [])
    if not parents:
        raise ValueError('policy parent absent')
    material = value(imports['expression_materialization'])
    child = material['materialization']['path']
    matches = [item[0] for item in paths.get(legacy_digest(child), [])]
    if not matches:
        raise ValueError('expression child absent from authored family')
    for ref in matches:
        if canonical(member_results[ref['digest']]) != canonical(value(imports['expression_result'])):
            raise ValueError('expression and family result disagree')
    outputs = material['evaluation']['outputs']
    expr_ref = b.record('ExpressionPolicy', 'expression-policy', {
        'program_ref': imports['program'], 'base_policy_ref': imports['base_policy'],
        'parent_path_ref': parents[0][1],
        'output_map_ref': extract('expression/output-map', imports['expression_materialization'], '/output_map'),
        'evaluated_policy_ref': extract('expression/evaluated-policy', imports['expression_materialization'], '/policy'),
        'materialization_ref': imports['expression_materialization'],
        'child_path_ref': extract('expression/child', imports['expression_materialization'], '/materialization/path', 'CompanyPathDraft/1'),
        'result_ref': imports['expression_result'],
        'declared_inputs': {k: v['declared_dependencies'] for k, v in outputs.items()},
        'evaluated_inputs': {k: v['evaluated_inputs'] for k, v in outputs.items()},
        'matching_members': matches, 'temporal_admission': False})
    response = value(imports['recovery_response'])
    cp = response['checkpoint']
    if type(cp['next_index']) is not int or not 0 <= cp['next_index'] <= len(members):
        raise ValueError('checkpoint index')
    recovery_ref = b.record('Recovery', 'recovery', {'family_ref': family_ref,
        'fixture_ref': imports['recovery_fixture'], 'method_ref': imports['recovery_method'],
        'response_ref': imports['recovery_response'],
        'checkpoint_ref': extract('recovery/checkpoint', imports['recovery_response'], '/checkpoint', 'CompanyFamilyCheckpointDraft/1'),
        'next_index': cp['next_index'], 'completed_members': members[:cp['next_index']],
        'physical_durability': False, 'accounting_commit': False})
    root = b.record('AuthoringExchange', 'company-authoring', {'profile': PROFILE,
        'source_blob': b.blob(source), 'family_ref': family_ref, 'expression_ref': expr_ref,
        'recovery_ref': recovery_ref, 'original_imports': list(imports.values()), 'admission': dict(FLAGS)})
    return b.packet(root), b.blobs
