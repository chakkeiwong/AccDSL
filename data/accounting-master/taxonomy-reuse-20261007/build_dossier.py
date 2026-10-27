#!/usr/bin/env python3
"""Produce a source-bound design supplement; does not import or execute Arelle."""
import ast
import hashlib
import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PRIOR = ROOT/'docs/design/proposal/methods/preparation-20261005-v1/03-adapters'
UPSTREAM = PRIOR/'sources/upstream/arelle'
graph = json.loads((OUT/'graph-final.json').read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def anchor(path, first, last):
    text = path.read_text()
    lines = text.splitlines(keepends=True)
    quote = ''.join(lines[first-1:last])
    return {'path':str(path.relative_to(ROOT)),'sha256':sha(path),'first_line':first,'last_line':last,
            'quote':quote,'quote_sha256':hashlib.sha256(quote.encode()).hexdigest()}


def paragraph(path, begin, end):
    t = path.read_text();a=t.index(begin);b=t.index(end,a)+len(end)
    return {'path':str(path.relative_to(ROOT)),'sha256':sha(path),'span':[a,b],'quote':t[a:b],
            'quote_sha256':hashlib.sha256(t[a:b].encode()).hexdigest()}


metadata = tomllib.loads((UPSTREAM/'pyproject.toml').read_text())
options = {
    'entrypointFile':'archive/aapl-20240928_htm.xml',
    'internetConnectivity':'offline','disablePersistentConfig':True,
    'validate':True,'validationExitCode':True,'formulaAction':'none',
    'keepOpen':True,'plugins':'','packages':[],
    'logFile':'logToStructuredMessage',
    'deduplicateFacts':None,'saveDeduplicatedInstance':False,
}
tree = ast.parse((UPSTREAM/'arelle__RuntimeOptions.py').read_text())
declared = {n.target.id for n in ast.walk(tree) if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name)}
assert set(options)<=declared
register = json.loads((PRIOR/'source-register.json').read_text())
for row in register['sources']:
    if row['repository']=='Arelle/Arelle':
        assert sha(PRIOR/row['path'])==row['sha256']
sources = {
    'api_lifecycle':anchor(UPSTREAM/'arelle__api__Session.py',1,116),
    'api_return':anchor(UPSTREAM/'arelle__api__Session.py',191,202),
    'offline_early':anchor(OUT/'sources/arelle-cntlrcmdline-trusted.body',1678,1689),
    'offline_cache':anchor(UPSTREAM/'arelle__WebCache.py',591,615),
    'missing_file':anchor(UPSTREAM/'arelle__ModelDocument.py',208,220),
    'validation_errors':anchor(OUT/'sources/arelle-cntlrcmdline-trusted.body',2289,2302),
    'run_return':anchor(OUT/'sources/arelle-cntlrcmdline-trusted.body',2327,2327),
    'validation_default':anchor(UPSTREAM/'arelle__RuntimeOptions.py',151,164),
    'structured_logging':anchor(OUT/'sources/arelle-cntlr-trusted.body',423,432),
    'fact_container':anchor(OUT/'sources/arelle-modelxbrl-trusted.body',337,345),
    'base_dependencies':anchor(UPSTREAM/'pyproject.toml',1,80),
    'code_license':anchor(UPSTREAM/'LICENSE.md',1,17),
    'fasb_us_notice':paragraph(OUT/'sources/terms-usgaap.txt','To\nmeet the mission','FAF\n”).'),
    'fasb_srt_notice':paragraph(OUT/'sources/terms-srt.txt','To meet the mission','FAF\n”).'),
    'xbrl_document_vs_software':paragraph(OUT/'sources/terms-xbrl-copyright.txt','Public documents on the XBRL.ORG','No right to create modifications or derivatives of XBRL documents is granted pursuant to this license.'),
    'xbrldt_notice':anchor(OUT/'sources/import-07-trusted.body',2,9),
    'sec_notice':anchor(OUT/'sources/import-09-trusted.body',2,4),
    'schema_version_notice':anchor(OUT/'sources/import-03-trusted.body',2,18),
}
artifact={
    'status':'source_inspected_proposed_exchange_not_executed',
    'code_commit':'01f6a4656c2c6551d2f05f31c9d74366d133ee7e',
    'scope':'Local source analysis and a proposed optional offline Arelle native-instance adapter',
    'source_anchors':sources,
    'source_dependency_snapshot':{'graph':'data/accounting-master/taxonomy-reuse-20261007/graph-final.json',
                                  'sha256':sha(OUT/'graph-final.json'),'summary':graph['summary'],
                                  'status':'static_recorded_references_resolved; schema_and_xbrl_validation_not_run'},
    'proposed_runtime_options':options,
    'proposed_environment':{'python_requirement':metadata['project']['requires-python'],
                            'base_requirements':metadata['project']['dependencies'],
                            'build_requirements':metadata['build-system']['requires'],
                            'optional_groups_selected':[],
                            'optional_groups_available':metadata['project']['optional-dependencies'],
                            'exact_dependency_lock':None,'models_required_by_this_source_profile':'No ML models declared in this selected core role; not a claim about all plugins',
                            'distribution':'No external distribution in this task; dependency licence/lock and applicable historical taxonomy terms remain incomplete'},
    'proposed_input':{'archive_sha256':graph['archive_sha256'],'entry_member':'aapl-20240928_htm.xml',
                      'uri_map':{a:{'path':next(n['path'] for n in graph['nodes'] if n['uri']==b),
                                    'sha256':next(n['sha256'] for n in graph['nodes'] if n['uri']==b)}
                                 for a,b in graph['aliases'].items()},
                      'publication_byte_vintage':'unestablished','taxonomies':'Actual 2024 imports, not substituted current taxonomies'},
    'adapter_procedure':[
        'Verify archive/member and URI-map hashes before invoking a library; do not rewrite the original schemas to change locations.',
        'Populate only an isolated source cache/resolver from the declared URI map; validate all materialized paths and their hashes, including built-in fallback resources if used. The mapping into Arelle cache/resolver is a later implementation obligation.',
        'Create one Session in its owning thread in one process. Use explicit offline/validation/error-sensitive options; retain original occurrences, no deduplication export.',
        'Select logToStructuredMessage explicitly and retrieve Session.get_log_messages before close; the default print handler would not supply that buffer. After run, inspect the boolean, structured logs, loaded models and model.errors before any validation status. False return or a missing/invalid dependency cannot yield an admitted valid package.',
        'Copy required native facts/contexts/units and occurrence/relationship sidecars while keepOpen retains the model; then close the session. factsInInstance is a set at this pin, so use original occurrence identity/order rather than set iteration for deterministic output.',
        'Submit proposed evidence for review. File validation cannot admit accounting interpretation or historical availability.',
    ],
    'exchanges':[
        {'id':'all_recorded_sources','input':'Actual graph-final.json and original annual instance',
         'expected_design_result':{'source_dependency_status':'static_references_resolved','library_execution':'not_run','xml_schema_validation':'not_run','xbrl_validation':'not_run','accounting_admission':'pending'},
         'rationale':'Current checked source inventory is not an Arelle output.'},
        {'id':'missing_us_gaap_schema','input_delta':'Withhold URI https://xbrl.fasb.org/us-gaap/2024/elts/us-gaap-2024.xsd from a copy of the proposed URI map; originals stay retained',
         'expected_design_result':{'status':'unresolved_dependency','dependency_uri':'https://xbrl.fasb.org/us-gaap/2024/elts/us-gaap-2024.xsd','network_fallback':False,'valid_package':False,'preserve_available_source_bytes':True},
         'rationale':'An offline cache pathname can exist as a string while the resource is absent; preflight must test the file/hash. If loading reaches it, preserve IOerror and affected concepts. This is a fixture design, not an executed Arelle experiment.'},
        {'id':'schema_wrong_namespace','input_delta':'Map the us-gaap URI to the retained srt schema in a proposed input only',
         'expected_design_result':{'status':'invalid_dependency_identity','valid_package':False},
         'rationale':'Both files are valid XML and HTTP 200 responses; the namespace differs, so identity fails.'},
        {'id':'validator_error_boolean','input_delta':'Hypothetical completed library run with success=True, model.errors nonempty',
         'expected_design_result':{'default_validationExitCode_false_boolean':True,'proposed_validationExitCode_true_boolean':False,'valid_package':False,'retain_logs_and_errors':True},
         'rationale':'Derived directly from the pinned controller return and error accumulation; not an observed run.'},
    ],
    'distribution_dispositions':[
        {'component':'Arelle source','inspected_terms':'Apache-2.0 source declaration; full Apache text retained','proposed_obligation':'Retain licence/notices and modification attribution where required; separate every dependency and plugin term','status':'source_terms_inspected; distribution_not_authorised_or_cleared'},
        {'component':'FASB US GAAP / SRT','inspected_terms':'Named Authorized Uses notices permit specified reporting and unchanged incorporation in works explaining/assisting implementation, with notice on first page; restrict changes and retain third-party terms','proposed_obligation':'Keep original bytes; resolver maps externally; carry full source-specific notices if a permitted-work distribution is later chosen','status':'current_retrieved_notice_inspected; page displays 2027 and is unversioned; applicability/history for 2024 package not established'},
        {'component':'SEC-authored schemas','inspected_terms':'Individual headers state staff-created content is not subject to domestic copyright under 17 U.S.C. 105','proposed_obligation':'Preserve source notice and provenance; do not extend this statement to FASB/XBRL/issuer content or foreign rights','status':'bounded_header_statement_only'},
        {'component':'XBRL specifications/schemas','inspected_terms':'Dimensions schema carries its own notice; public document copyright page expressly refers schemas to a separate Software Notice; 2007/2009 IP policies and XBRL US policy retained','proposed_obligation':'Check each component-specific notice and the actual applicable software terms. Participant contribution grants do not automatically licence this application. Candidate Software Notice URL returned 404.','status':'software_notice_and_component_applicability_open'},
        {'component':'Arelle required dependencies','inspected_terms':'Fifteen declared base requirements plus three build ranges; no installed exact dependency resolution','proposed_obligation':'Resolve versions and transitive terms for the actual environment before any production/distribution claim','status':'requirements_inventory_only; no lock_or_licence_clearance'},
    ],
    'acceptance':{'E01':'open; this static taxonomy frontier repaired only','E14':'open; broader tools, exact dependency/model locks, terms and actual interfaces remain','whole_proposal':'not_ready'},
}
(OUT/'adapter-dossier.json').write_text(json.dumps(artifact,indent=2,ensure_ascii=False)+'\n')
print({'anchors':len(sources),'base_dependencies':len(metadata['project']['dependencies']),'exchanges':len(artifact['exchanges'])})
