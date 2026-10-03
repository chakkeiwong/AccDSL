#!/usr/bin/env python3
"""Build dated research ledgers and bibliography from reviewed local records.

This script does not read papers on behalf of a reviewer. The support and
disposition fields below are author-entered reading records, not inferred
from citation counts or metadata.
"""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'docs/design/research'
DATE = '2026-10-02'

def load(p):
    return json.loads(p.read_text())

def dump(name, value):
    (BASE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

SUPPORT = {
 'green2007': ('FOUNDATIONAL', 'Sections 2--4; Definitions 3.1--3.2; Proposition 4.2; related-work discussion', 'Positive relational operations compose annotations; dependency and alternative derivations are distinct.', 'No general semantics for every nonlinear, negative or probabilistic accounting operation.'),
 'stuart2010': ('SURVEY_OR_TUTORIAL', 'Section 2.2, equations (2.1)--(2.5); discussion of underdetermination in Section 2', 'Observation operator, inversion, regularisation and priors are different modelling choices.', 'No transferred infinite-dimensional well-posedness or sampler guarantee for this mixed accounting model.'),
 'giacomini2021': ('DIRECT_METHOD', 'CWP12/20 Sections 2.1--2.6, equations (2.2)--(2.4), Theorem 1 and its assumptions; implementation discussion located in Section 5', 'Flat likelihood leaves conditional prior unresolved; posterior classes and lower/upper probabilities require specified sets and regularity.', 'No assertion that SVAR algorithms or asymptotic guarantees apply to arbitrary accounting DSLs.'),
 'hoeting1999': ('SURVEY_OR_TUTORIAL', 'Equations (1)--(3); Sections 3, 5 and 6; model-class discussion', 'Bayesian model averaging requires a model space, priors and marginal likelihoods.', 'No equal weights from candidate counts; no performance transfer to AccDSL.'),
 'pearl2009': ('FOUNDATIONAL', 'Section 3.2.1, equations (5)--(6); distinction between observational and intervention distributions', 'Replacing a structural equation is distinct from conditioning on observations.', 'Accounting fit alone does not identify a causal effect.'),
 'merigoux2021': ('DIRECT_METHOD', 'Sections 3--4; default calculus and Figures 8--9; compiler architecture Figure 13; examples/evaluation and related-work passages', 'Scopes, explicit exceptions, empty/conflict outcomes and staged compilation.', 'Catala compiler results do not prove accounting compliance, extraction correctness or exhaustive interpretations.'),
 'mernik2005': ('SURVEY_OR_TUTORIAL', 'CWI SEN-E0309 Sections 1.1, 2.2--2.5, implementation decision tree, Section 3.2', 'Application libraries are credible competitors; DSL decisions depend on domain and tooling costs.', 'No empirical superiority of this proposed DSL.'),
 'vandeursen2000': ('SURVEY_OR_TUTORIAL', 'Survey terminology, benefits/risks, design and implementation discussion; annotated bibliography', 'DSLs admit several implementation strategies and have development costs.', 'No claimed universal benefit or quantitative outcome.'),
 'jones2000': ('DIRECT_METHOD', 'Sections 3--5, primitive combinators and abstract/concrete valuation discussion', 'Contract composition can be separated from numerical valuation models.', 'No full accounting standard or journal reconstruction semantics.'),
 'vandeMeent2018': ('SURVEY_OR_TUTORIAL', 'Version 2: model-denotation discussion, first-order language sample/observe grammar and weighted-sampling derivation', 'Explicit probabilistic programs separate a model from approximate inference.', 'No default sampler choice or convergence claim; 301-page tutorial not read end to end.'),
 'chen2021': ('EMPIRICAL_EXAMPLE', 'Sections 3--6; operations, annotation, retrieval and program generation; Appendix operations; official eval_program source', 'Question-level executable arithmetic and supporting evidence; evaluation is task-specific.', 'Not a benchmark of full historical accounting reconstruction or simulation.'),
 'zhu2021': ('EMPIRICAL_EXAMPLE', 'Sections 2--4: hybrid annotation, aggregation operators, signed numerical evaluation', 'Tables and text jointly inform financial QA; signs matter to numeric correctness.', 'No complete accounting extraction or forecast guarantee.'),
 'reddy2024': ('EMPIRICAL_EXAMPLE', 'Dataset construction, retrieval/context methods and Table 2; evaluation and limitations passages', 'Long context and retrieval affect financial QA.', 'No performance claim for our system or exhaustive note coverage.'),
 'xie2024': ('EMPIRICAL_EXAMPLE', 'Task inventory and benchmark construction; Section 4 evaluation including 4.1; comparison to prior benchmarks', 'Financial NLP evaluation spans distinct tasks.', 'No model ranking transferred to accounting reconstruction.'),
 'smock2022': ('EMPIRICAL_EXAMPLE', 'Canonicalisation procedure, GriTS equation (1), dataset/evaluation tables and related work', 'Table detection, structure and functional analysis need separate evaluation.', 'Table scores do not establish accounting semantics.'),
 'li2020': ('EMPIRICAL_EXAMPLE', 'Sections 3.1--3.3 and 4.1: document-derived labels and detection baseline', 'Weak supervision from document structure is an extraction technique.', 'No accounting domain transfer established.'),
 'nassar2024': ('IMPLEMENTATION_OR_SOFTWARE', 'Local version 5 Section 3 processing pipeline; layout and TableFormer discussion; converter interface', 'Local document conversion combines parsing, layout and table recognition.', 'No guaranteed extraction accuracy or uniform model licence.'),
 'carpenter2017': ('IMPLEMENTATION_OR_SOFTWARE', 'Model language examples, sampling statements, Section 2.5 diagnostics; official model_base interface', 'Explicit probabilistic modelling and diagnostics; continuous-model backend candidate.', 'No accounting-model identifiability or sampler validation for this project.'),
 'bingham2019': ('IMPLEMENTATION_OR_SOFTWARE', 'Sections 2--3, example conditioning and design principles; official repository documentation', 'Probabilistic programming and composable inference machinery.', 'No tested integration, posterior accuracy or default engine selection.'),
 'damoura2008': ('IMPLEMENTATION_OR_SOFTWARE', 'Sections 2--3, clients, interface and implementation architecture', 'SMT interfaces and supported theory-solving architecture.', 'No unrestricted nonlinear solvability or performance promise.'),
 'zheng2021': ('EMPIRICAL_EXAMPLE', 'Sections 3--5: FinTabNet construction/company split, GTE methods and evaluation', 'Financial table structure is a useful domain-specific extraction benchmark.', 'Not all disclosures or interpretations are represented by its table annotations.'),
 'snodgrass1986': ('FOUNDATIONAL', 'Snapshot, rollback, historical and temporal examples; valid and transaction time discussion', 'Business validity and database history require distinct time semantics.', 'Publication availability is our additional domain requirement, not equated to transaction time.'),
 'libkin2014': ('FOUNDATIONAL', 'Sections 2--5: labelled nulls, possible worlds, conditional tables, certain answers', 'Shared missing values and dependencies need explicit semantics.', 'Finite relational theory is not a ready-made continuous financial inference engine.'),
 'doshi2024': ('DIRECT_METHOD', 'Chapters 4, 7--9: accounting language, temporal logs/corrections, examples and limits', 'An accounting DSL can expose time and corrections as language concepts.', 'No complete public-disclosure translation or latent-history inference established.'),
 'babcinetchi2022': ('BACKGROUND', 'All four pages, 342--345, grammar and accounting-language proposal', 'A small accounting DSL/grammar precedent exists.', 'Insufficient semantic and empirical evidence to govern full implementation.'),
 'nehmer1997': ('FOUNDATIONAL', 'Sections 2--5: balance state, admissible transactions and aggregation', 'Accounting conservation and transaction admissibility are distinct.', 'No inference of uniquely true transactions from reports.'),
 'shahnazarian2004': ('DIRECT_METHOD', 'Sections 2.3--2.8; selected Chapter 3 optimisation/econometric equations; Section 4.1 data; Section 8.3 evaluation; Appendix B', 'Accounting dynamics and behavioural/econometric relationships can be joined in company simulation.', 'Tax-data starting point and funds formulation do not supply generic modern disclosure extraction or cash-flow semantics.'),
 'halaj2016': ('DIRECT_METHOD', 'Sections 3.2--3.4, funding and portfolio equations, calibration/limitations discussion', 'Funding shocks and risk constraints can change portfolio decisions.', 'Homogeneous portfolios and parameters cannot be imported as target-company defaults.'),
 'behn2019': ('DIRECT_METHOD', 'Section 2 including setup, timing, funding rates and decisions; regulatory-constraint discussion', 'Bank behaviour can depend jointly on capital and liquidity constraints.', 'No accounting standard implementation or empirical parameter transfer.'),
 'pierson2020': ('DIRECT_METHOD', 'Sections 3--4, reporting accumulators, inventory and working-capital structures; supplementary Vensim equations inspected', 'Accrual/payment bridges and period reporting can be operationalised.', 'Payment delays, inventory simplification and limited equity model are not universal.'),
 'cosentino2026': ('COMPETITOR', 'Sections 3.1--3.2, 4.6 auditability checks and Section 5 discussion; surrounding evaluation design', 'Persistent evidence and recovery support financial RAG traceability.', 'No demonstrated financial-decision outcome or full accounting/simulation engine.'),
}

# Leads explicitly considered while inspecting technical/related-work passages.
# No omitted work below supplies a theorem or algorithm claim in the manuscript.
BACK = {
 'green2007': [('Imielinski and Lipski (1984), Incomplete Information in Relational Databases','FOUNDATIONAL','source blocked; Libkin technical treatment inspected'),('Buneman, Khanna and Tan (2001), Why and Where: A Characterization of Data Provenance','FOUNDATIONAL','defer where-provenance details; dependency representation specified locally'),('Benjelloun et al. (2006), ULDBs: Databases with Uncertainty and Lineage','DIRECT_METHOD','possible-world implementation lead; not a core solver dependency')],
 'libkin2014': [('Imielinski and Lipski (1984)','FOUNDATIONAL','source blocked; discussed transparently'),('Codd (1979), Extending the Database Relational Model to Capture More Meaning','FOUNDATIONAL','background; tagged missingness specified directly'),('Abiteboul, Hull and Vianu, Foundations of Databases','SURVEY_OR_TUTORIAL','book reference for database implementation phase')],
 'merigoux2021': [('Reiter (1980), A Logic for Default Reasoning','FOUNDATIONAL','Catala paper inspected for its restricted calculus; no general default-logic theorem imported'),('Merigoux et al., reverse engineering French income tax','DIRECT_METHOD','tax-language context; not corporate accounting evidence')],
 'mernik2005': [('van Deursen, Klint and Visser (2000)','SURVEY_OR_TUTORIAL','included'),('Spinellis (2001), Notable Design Patterns for Domain-Specific Languages','DIRECT_METHOD','background pattern taxonomy; shared IR decision supported by inspected Mernik report')],
 'vandeursen2000': [('Hudak, building domain-specific embedded languages','DIRECT_METHOD','embedded-library alternative retained; no implementation result imported'),('Batory et al., domain-specific program generation','DIRECT_METHOD','later code generation; reference interpreter is initial scope')],
 'jones2000': [('Musiela and Rutkowski, Martingale Methods in Financial Modelling','BACKGROUND','valuation theory outside current core'),('Harrison and Pliska, martingales and stochastic integrals in trading','FOUNDATIONAL','valuation extension; probability-measure distinction stated without importing pricing theorem')],
 'snodgrass1986': [('Snodgrass and Ahn (1985), A Taxonomy of Time in Databases','FOUNDATIONAL','1986 source covers needed distinctions'),('Snodgrass, The Temporal Query Language TQuel','DIRECT_METHOD','query-language history; SQL implementation not dependent on TQuel')],
 'stuart2010': [('Kaipio and Somersalo, Statistical and Computational Inverse Problems','SURVEY_OR_TUTORIAL','book-level expansion; no high-dimensional inference implemented'),('Tikhonov regularisation literature','FOUNDATIONAL','regularisation is discussed as a choice, not a method selected for implementation')],
 'giacomini2021': [('Manski (2007), Identification for Prediction and Decision','FOUNDATIONAL','book-level expansion; local feasible-set derivations supplied'),('Kitagawa (2012/2015), robust inference in partially identified SVARs','DIRECT_METHOD','SVAR implementation outside scope'),('Tamer (2010), Partial Identification in Econometrics','SURVEY_OR_TUTORIAL','primary PDF blocked')],
 'hoeting1999': [('Draper (1995), Assessment and Propagation of Model Uncertainty','DIRECT_METHOD','important alternative; future inference expansion'),('Kass and Raftery (1995), Bayes Factors','SURVEY_OR_TUTORIAL','prior/marginal-likelihood background; not separately used'),('Madigan and York (1995), Bayesian graphical models for discrete data','DIRECT_METHOD','specific model-space search not selected')],
 'pearl2009': [('Pearl (2000), Causality','FOUNDATIONAL','book background; intervention definition checked in 2009 article'),('Rubin potential-outcome literature','COMPETITOR','causal identification research outside deterministic scenario core')],
 'chen2021': [('DROP','EMPIRICAL_EXAMPLE','general numerical QA background'),('HybridQA','EMPIRICAL_EXAMPLE','hybrid text/table competitor; financial-specific tasks prioritised')],
 'zhu2021': [('FinQA','EMPIRICAL_EXAMPLE','parallel financial reasoning benchmark included'),('HybridQA','EMPIRICAL_EXAMPLE','background; no benchmark replication'),('DROP / NumNet','EMPIRICAL_EXAMPLE','numerical QA techniques outside selected product implementation')],
 'reddy2024': [('FinQA','EMPIRICAL_EXAMPLE','included'),('PIXIU','EMPIRICAL_EXAMPLE','broader task history represented through FinBen'),('BloombergGPT','COMPETITOR','closed training resources; no LLM choice made')],
 'xie2024': [('PIXIU','EMPIRICAL_EXAMPLE','predecessor benchmark; FinBen prioritised'),('FinanceBench','COMPETITOR','important QA comparator for later extraction evaluation'),('BizBench','EMPIRICAL_EXAMPLE','later program-reasoning comparison')],
 'smock2022': [('PubTabNet','EMPIRICAL_EXAMPLE','table-recognition comparator; no model training selected'),('GriTS','DIRECT_METHOD','metric discussion inspected within source; standalone metric implementation deferred')],
 'zheng2021': [('ICDAR 2013/2019 table competitions','EMPIRICAL_EXAMPLE','context for source evaluation, not accounting validity'),('PubTabNet','EMPIRICAL_EXAMPLE','general table dataset comparator')],
 'li2020': [('Faster R-CNN','DIRECT_METHOD','source baseline; no detector selected or trained'),('ImageNet and COCO','BACKGROUND','vision pretraining context; outside accounting semantic validation')],
 'nassar2024': [('TableFormer','DIRECT_METHOD','packaged component; evaluate as part of ingestion adapter'),('DocLayNet','EMPIRICAL_EXAMPLE','layout-data follow-up for extraction evaluation'),('RT-DETR','DIRECT_METHOD','detector architecture not a product-level decision')],
 'carpenter2017': [('Gelman and Rubin (1992), multiple-sequence convergence assessment','FOUNDATIONAL','inference phase must use current diagnostics; no sampling experiment now'),('Hoffman and Gelman, No-U-Turn Sampler','DIRECT_METHOD','optional backend implementation, not a chosen default')],
 'bingham2019': [('Stan','IMPLEMENTATION_OR_SOFTWARE','included'),('Edward','COMPETITOR','probabilistic backend alternative; no engine default selected')],
 'vandeMeent2018': [('Stan','IMPLEMENTATION_OR_SOFTWARE','included'),('Pyro','IMPLEMENTATION_OR_SOFTWARE','included'),('Sequential Monte Carlo and particle MCMC literature','DIRECT_METHOD','inference-stage expansion; not justified as accounting defaults')],
 'damoura2008': [('SMT-LIB','IMPLEMENTATION_OR_SOFTWARE','solver interchange candidate'),('DPLL(T) and theory combination literature','FOUNDATIONAL','solver internals delegated; no new SMT algorithm')],
 'pierson2020': [('Yamaguchi (2003), accounting system dynamics','DIRECT_METHOD','in local collection; selected Pierson implementation is sufficient for current bridge discussion'),('Sterman, Business Dynamics','SURVEY_OR_TUTORIAL','book context; no behavioural calibration imported'),('Pierson and Sterman, reporting-period formulation','DIRECT_METHOD','mechanism checked in source and supplied model')],
 'halaj2016': [('Birge and Judice (2013)','DIRECT_METHOD','portfolio optimisation extension'),('Halaj (2013), dynamic balance sheet model','DIRECT_METHOD','earlier model; later inspected liquidity model prioritised')],
 'behn2019': [('Bank capital and liquidity optimisation literature in related work','DIRECT_METHOD','bank package requires target-specific expansion before forecasting research')],
 'shahnazarian2004': [('Dynamic corporate microsimulation and tax-response models in Chapter 1','DIRECT_METHOD','historical context; do not import calibration defaults')],
 'doshi2024': [('Ledger','IMPLEMENTATION_OR_SOFTWARE','manual and transaction source inspected'),('Accounting DSL and database precedents in thesis related work','BACKGROUND','bounded language precedent; no full historical inference claim')],
 'babcinetchi2022': [('Domain-specific language definitions and parser/compiler literature','BACKGROUND','grammar context only; stronger surveyed DSL sources included')],
 'nehmer1997': [('Algebraic accounting and transaction-system antecedents','FOUNDATIONAL','local balance proof provided; no uninspected antecedent theorem used')],
 'cosentino2026': [('FinQA','EMPIRICAL_EXAMPLE','included and official evaluator inspected'),('Financial NLP and FinLLM surveys (2025)','SURVEY_OR_TUTORIAL','recent context; no model selection'),('RAG retrieval/chunking literature','DIRECT_METHOD','adapter evaluation research; no fixed chunk size promoted')],
}

# Concrete reference leads replace broad topic placeholders where the seed's
# bibliography was checked during the final source audit. These are candidates,
# not claims that their own full texts have been read.
BACK.update({
 'doshi2024': [('Merigoux, Chataing and Protzenko (2021), Catala', 'DIRECT_METHOD', 'included; thesis bibliography [7]'), ('Chamberlin and Boyce (1974), SEQUEL', 'COMPETITOR', 'typed database/query alternative; no imported theorem'), ('Ong, Papakonstantinou and Vernoux (2014), SQL++', 'COMPETITOR', 'semi-structured query alternative; not selected as execution core')],
 'babcinetchi2022': [('Nystrom (2021), Crafting Interpreters', 'BACKGROUND', 'compiler construction context; no novel compiler method required'), ('JetBrains, Domain-Specific Languages', 'BACKGROUND', 'web introduction; stronger technical surveys included')],
 'nehmer1997': [('Mattessich (1957), Towards a general and axiomatic foundation of accountancy', 'FOUNDATIONAL', 'important algebraic antecedent; local invariant proof and Nehmer technical text support current claim'), ('Mattessich (1964), Accounting and Analytical Methods', 'FOUNDATIONAL', 'book-level antecedent; no theorem imported'), ('Nehmer (1988), Accounting Information Systems as Algebras and First Order Axiomatic Models', 'DIRECT_METHOD', 'earlier thesis; inspected 1997 article supplies the technical basis used')],
 'behn2019': [('Adrian and Shin (2011), Financial intermediary balance sheet management', 'DIRECT_METHOD', 'bank behavioural-module expansion; no estimated response imported'), ('Bahaj and Malherbe (2017), A positive analysis of bank behaviour under capital requirements', 'COMPETITOR', 'bank policy-model comparison before calibration'), ('Boissay and Collard (2016), Macroeconomics of bank capital and liquidity regulations', 'COMPETITOR', 'aggregate equilibrium outside single-company core')],
 'shahnazarian2004': [('Francis (1983), Financial Planning and Forecasting Models: A Review', 'SURVEY_OR_TUTORIAL', 'historical financial-planning antecedents; no forecasting method selected'), ('Francis and Rowell (1978), A Simultaneous Equation Model of the Firm for Financial Analysis and Planning', 'COMPETITOR', 'explicit equation-model alternative; current algebra derived locally'), ('Gentry (1979), Simulating the Strategic Financial Planning Process', 'DIRECT_METHOD', 'behavioural-simulation expansion before predictive validation')],
})

BACK_ANCHORS = {
 'green2007': ['References [19]', 'References [6]', 'References [3]'],
 'libkin2014': ['References [40]', 'References [22]', 'References [2]'],
 'merigoux2021': ['References [41]', 'Introduction, citation [32]'],
 'mernik2005': ['Related work and bibliography', 'References [88]'],
 'vandeursen2000': ['References [40]', None],
 'jones2000': ['References: Musiela and Rutkowski (1997)', None],
 'snodgrass1986': ['References [5]', 'References: The Temporal Query Language TQuel'],
 'stuart2010': ['References: Kaipio and Somersalo (2005)', None],
 'giacomini2021': ['References: Manski (2007)', 'First-page acknowledgement of earlier working papers', None],
 'hoeting1999': ['References: Draper (1995)', 'References: Kass and Raftery (1995)', 'References: Madigan and York (1995)'],
 'pearl2009': ['References: Pearl (2000a)', None],
 'chen2021': ['References: DROP', 'References: HybridQA'],
 'zhu2021': [None, 'Related work and References: HybridQA', 'Related work and References: DROP and NumNet'],
 'reddy2024': ['Dataset construction: FinQA', 'References: PIXIU', 'References: BloombergGPT'],
 'xie2024': ['References: PIXIU', 'References: FinanceBench', 'References: BizBench'],
 'smock2022': ['Dataset comparison: PubTabNet', 'References [19]'],
 'zheng2021': ['Evaluation comparisons and references: ICDAR', 'PubTabNet evaluation comparison'],
 'li2020': ['References: Ren et al. (2015)', 'References: ImageNet and Microsoft COCO'],
 'nassar2024': ['References [12]', 'References and worked extraction example: DocLayNet', 'Section on layout model, citation [16]'],
 'carpenter2017': ['References: Gelman and Rubin (1992)', 'References: Hoffman and Gelman (2014)'],
 'bingham2019': ['References: Carpenter et al. (2017)', 'Related work: Edward; references: Tran et al. (2017)'],
 'vandeMeent2018': ['References: Stan Development Team (2014)', 'References: Bingham et al.', None],
 'damoura2008': ['References: SMT-LIB', None],
 'pierson2020': ['References [20]', 'References [4]', None],
 'halaj2016': ['Related work: Birge and Judice (2013)', 'Related work: Halaj (2013)'],
 'behn2019': ['References: Adrian and Shin (2011)', 'References: Bahaj and Malherbe (2017)', 'References: Boissay and Collard (2016)'],
 'shahnazarian2004': ['References, printed p. 263', 'References, printed p. 263', 'References, printed p. 263'],
 'doshi2024': ['Bibliography [7]', 'Bibliography [3]', 'Bibliography [8]'],
 'babcinetchi2022': ['References [4]', 'References [1]'],
 'nehmer1997': ['References [4]', 'References [5]', 'References [3]'],
}

def main():
    rows = load(BASE / 'catalog.json')
    supplemental = BASE / 'supplemental-support.json'
    if supplemental.exists():
        for record in load(supplemental)['records']:
            SUPPORT[record['id']] = tuple(record['support'])
            BACK[record['id']] = [tuple(x) for x in record['backward']]
            BACK_ANCHORS[record['id']] = record['backward_anchors']
    decisions = {r['id']: r for r in load(BASE / 'forward-screening-decisions.json')['records']}
    # Fail before writing any generated ledger when a retrieved candidate has
    # no human/model-authored individual screening record. Retrieval is not review.
    for r in rows:
        for order in ['high', 'recent']:
            path = BASE / 'raw' / f'{r["id"]}-citing-{order}.json'
            if path.exists():
                for candidate in load(path).get('results', []):
                    if candidate['id'] not in decisions:
                        raise ValueError(f'Unscreened candidate: {candidate["id"]} {candidate["title"]}')
    fixes = {
      'jones2000': ['Peyton Jones, Simon','Jean-Marc Eber','Julian Seward'],
      'li2020': ['Minghao Li','Lei Cui','Shaohan Huang','Furu Wei','Ming Zhou','Zhoujun Li'],
      'zheng2021': ['Xinyi Zheng','Douglas Burdick','Lucian Popa','Xu Zhong','Nancy Xin Ru Wang'],
      'carpenter2017': ['Bob Carpenter','Andrew Gelman','Matthew D. Hoffman','Daniel Lee','Ben Goodrich','Michael Betancourt','Marcus A. Brubaker','Jiqiang Guo','Peter Li','Allen Riddell'],
      'bingham2019': ['Eli Bingham','Jonathan P. Chen','Martin Jankowiak','Fritz Obermeyer','Neeraj Pradhan','Theofanis Karaletsos','Rohit Singh','Paul Szerlip','Paul Horsfall','Noah D. Goodman'],
    }
    support, metadata, backward, forward, omissions = [], [], [], [], []
    for r in rows:
        key=r['id']
        if key in fixes:r['authors']=fixes[key]
        if key=='behn2019':r['version_note']='ECB Working Paper 2233; local DOI 10.2866/943267. OpenAlex SSRN record used only for citation metadata.'
        if key=='halaj2016':r['version_note']='ECB Working Paper 1896, April 2016. Index journal DOI is not asserted to be the version read.'
        if not r.get('local_path'):
            support.append({**r,'classification':'SOURCE_BLOCKED','claims_allowed':[],'claims_forbidden':['Any technical claim based on uninspected full text'],'full_text_status':'not available','retraction_check':'metadata only; not used as technical support'})
            omissions.append({'id':key,'title':r['title'],'reason':'No verified accessible primary PDF after recorded retrieval attempts','status':'SOURCE_BLOCKED','reviewer_risk':'Important antecedent; qualified explicitly in manuscript','next_action':'Acquire primary full text before adopting its specific method','acceptable_for_current_claims':True})
            for order in ['high','recent']:
                path=BASE/'raw'/f'{key}-citing-{order}.json'
                if path.exists():
                    candidates=[]
                    for c in load(path).get('results',[]):
                        d=decisions[c['id']]
                        candidates.append({'id':c['id'],'title':c['title'],'year':c.get('publication_year'),'doi':c.get('doi'),'classification':d['classification'],'action':d['action'],'disposition':d['reason'],'inspection':d['inspection'],'decision_source':'docs/design/research/forward-screening-decisions.json'})
                    forward.append({'seed':key,'order':order,'source':'OpenAlex works filtered by cites','source_record':str(path.relative_to(ROOT)),'date':DATE,'status':'metadata discovery reviewed; seed full text blocked','coverage':'bounded top/recent query; no seed technical support','candidates':candidates})
            continue
        r['status'] = 'verified PDF archived; targeted technical review recorded in source-support.json'
        cls, anchors, allowed, forbidden=SUPPORT[key]
        cross=BASE/'raw'/f'{key}-crossref.json'
        if key=='cosentino2026':cross=BASE/'raw/cosentino-crossref-extra'
        crossdata=load(cross).get('message',{}) if cross.exists() else {}
        notice={k:crossdata[k] for k in ['update-to','updated-by','relation'] if crossdata.get(k)}
        record={**r,'classification':cls,'access_date':DATE,'full_text_status':'verified PDF archived; targeted technical reading',
                'inspected_technical_anchors':anchors,'claims_allowed':[allowed],'claims_forbidden':[forbidden],
                'reading_scope':'Only the specified technical and comparison portions; no independent replication',
                'publication_status': 'working/thesis/preprint version identified in catalogue' if r.get('version_note') or key in ['doshi2024','shahnazarian2004'] else 'published paper; source PDF inspected',
                'correction_check':{'openalex_is_retracted':r.get('is_retracted','not available'),'crossref_notice_relations':notice if cross.exists() else 'not available','date':DATE,'interpretation':'No adverse notice found in checked metadata; not a comprehensive certification. Version discrepancies recorded separately.'},
                'quarantine_status':'not quarantined; version qualifications retained'}
        support.append(record)
        metadata.append({'id':key,'citation_count':r.get('cited_by_count','not available'),'citation_source':'OpenAlex' if r.get('openalex_id') else 'not available','source_id':r.get('openalex_id','not available'),'access_date':DATE,'venue':r.get('venue') or 'not available','venue_metric':'not available','venue_metric_source':'not available','caveat':'Visibility metadata only. Index records can merge versions; never used as correctness evidence.'})
        leads=[]
        for i, (t, c, a) in enumerate(BACK[key]):
            refs = BACK_ANCHORS.get(key, [])
            anchor = refs[i] if i < len(refs) else None
            leads.append({'work':t,'classification':c,'action':a,
                          'discovery_relation':'checked seed reference or explicit discussion' if anchor else 'cross-survey addition or topic expansion; citation relation not asserted',
                          'seed_anchor':anchor or 'not established'})
        backward.append({'seed':key,'source_path':r['local_path'],'inspected_context':anchors+'; relevant related-work/reference passages','candidates':leads,'scope_note':'Selected relevant leads, with literal citation relationships distinguished from cross-survey additions. Topic groups and unverified reference relationships are expansion leads, not evidence of exhaustive reference coverage.'})
        for lead in leads:
            if 'included' not in lead['action'] and 'inspected' not in lead['action']:
                omissions.append({'seed':key,**lead,'status':'deferred within stated module scope','reviewer_risk':'Revisit if this method becomes an implementation dependency','acceptable_for_current_claims':True})
        for order in ['high','recent']:
            f=BASE/'raw'/f'{key}-citing-{order}.json'
            if not f.exists():
                forward.append({'seed':key,'order':order,'status':'not available','date':DATE,'reason':'No matching index record or retrieval not available; raw searches retained'})
                continue
            d=load(f)
            found=[]
            for a in d.get('results',[]):
                decision=decisions[a['id']]
                found.append({'title':a['title'],'year':a['publication_year'],'id':a['id'],'doi':a.get('doi'),'cited_by_count':a.get('cited_by_count','not available'),'disposition':decision['reason'],'classification':decision['classification'],'action':decision['action'],'inspection':decision['inspection'],'decision_source':'docs/design/research/forward-screening-decisions.json'})
            forward.append({'seed':key,'order':order,'source':'OpenAlex works filtered by cites','source_record':str(f.relative_to(ROOT)),'date':DATE,'status':'retrieved; individually recorded metadata relevance decisions','coverage':'top 3 by citations or newest 3 with publication cutoff; limited discovery, not exhaustive technical reading','candidates':found})
    omissions.extend({'id':d['id'],'title':d['title'],'reason':d['reason'],
                      'classification':d['classification'],'status':d['action'],
                      'inspection':d['inspection'],
                      'acceptable_for_current_claims':'no technical claim imported; revisit before adding the deferred method'}
                     for d in decisions.values() if d['action']!='already_archived')
    dump('catalog.json',rows)
    dump('source-support.json',{'date':DATE,'records':support})
    dump('citation-venue.json',{'date':DATE,'records':metadata})
    dump('backward-snowball.json',{'date':DATE,'records':backward})
    dump('forward-snowball.json',{'date':DATE,'records':forward})
    dump('omissions.json',{'date':DATE,'records':omissions,'global_limits':['Not an exhaustive worldwide literature survey','Detailed standards, actuarial models, process mining and multi-company equilibrium require module-specific expansion','Blocked primary sources supply no technical claims']})
    build_bib(rows)
    build_tools()
    build_paper_index(rows)
    print(f'Wrote six support/coverage records and bibliography for {len(SUPPORT)} archived papers; claim ledger maintained separately.')

def build_paper_index(rows):
    archived = sorted((r for r in rows if r.get('local_path')),
                      key=lambda r: (r['first_author_surname'].casefold(), r['year']))
    blocked = [r for r in rows if not r.get('local_path')]
    lines = ['# AccDSL research paper library', '',
             f'{len(archived)} verified PDFs support the [product design](../design/accounting-product-design.pdf). '
             'The collection includes seven preserved copies from the original user collection and additional external sources. '
             'The original files remain unchanged.', '',
             'Filenames use `Title First-author-surname (year).pdf`. Publication years are used when a working version '
             'underlies a later article; the actual archived version is identified below. Local copies are for research; '
             'their availability does not imply redistribution rights.', '',
             'Technical reading was targeted to the claims used. See the '
             '[source-support ledger](../design/research/source-support.json) for inspected sections, '
             'allowed claims and version/correction checks. The '
             '[catalogue](../design/research/catalog.json) records URLs, hashes and extracted text paths. '
             'Citation counts are dated visibility metadata, not correctness evidence.', '',
             '| Paper | Archived version |', '| --- | --- |']
    for r in archived:
        link = quote(Path(r['local_path']).name)
        title = r['title'].replace('|', '\\|')
        note = r.get('version_note', 'Verified local PDF; see source-support ledger for reading scope.').replace('|', '\\|')
        lines.append(f'| [{title}]({link}) — {r["first_author_surname"]} ({r["year"]}) | {note} |')
    lines += ['', '## Access gaps', '',
              'The following important candidates have no verified primary PDF after the recorded retrieval attempts. '
              'They supply no technical support for the design:', '']
    for r in blocked:
        lines.append(f'- {r["title"]} ({r["year"]}); catalogue ID `{r["id"]}`.')
    lines += ['', 'See [retrieval attempts](../design/research/retrieval-attempts.json) and '
              '[omissions](../design/research/omissions.json). Rejected downloads are excluded from this library. '
              'The survey is broad but bounded; specialised actuarial, detailed standards, process-mining '
              'and multi-company equilibrium work require further module-specific review.', '',
              'Regenerate this index and the bibliography from the repository root with '
              '`python3 scripts/build_design_research.py`.', '']
    (ROOT / 'docs/papers/README.md').write_text('\n'.join(lines))

def tex(s):
    return s.replace('&',r'\&').replace('%',r'\%').replace('_',r'\_').replace('‐','-').replace('–','--')

def build_bib(rows):
    venue={
      'green2007':'Proceedings of PODS','stuart2010':'Acta Numerica, 19:451--559',
      'giacomini2021':'Econometrica, 89; archived CWP12/20 working version',
      'hoeting1999':'Statistical Science, 14(4):382--417','pearl2009':'Statistics Surveys, 3:96--146',
      'merigoux2021':'Proceedings of the ACM on Programming Languages, 5(ICFP)',
      'mernik2005':'ACM Computing Surveys; archived CWI SEN-E0309 (2003)',
      'vandeursen2000':'ACM SIGPLAN Notices, 35(6):26--36',
      'jones2000':'Proceedings of ICFP; author manuscript dated 23 August 2000',
      'vandeMeent2018':'arXiv:1809.10756; version 2 (2021)',
      'chen2021':'Proceedings of EMNLP','zhu2021':'Proceedings of ACL-IJCNLP',
      'reddy2024':'Proceedings of ACL, short papers','xie2024':'NeurIPS Datasets and Benchmarks; arXiv:2402.12659',
      'smock2022':'Proceedings of CVPR; author manuscript','li2020':'Proceedings of LREC; arXiv:1903.01949',
      'nassar2024':'Technical report, arXiv:2408.09869v5',
      'carpenter2017':'Journal of Statistical Software, 76(1)','bingham2019':'Journal of Machine Learning Research, 20(28):1--6',
      'damoura2008':'Proceedings of TACAS','zheng2021':'Proceedings of WACV',
      'snodgrass1986':'Computer, 19(9):35--42','libkin2014':'Proceedings of PODS',
      'doshi2024':'Master thesis, Rochester Institute of Technology',
      'babcinetchi2022':'Technical University of Moldova student research conference, pp. 342--345',
      'nehmer1997':'Annals of Operations Research, 71:179--198',
      'shahnazarian2004':'Sveriges Riksbank Occasional Paper 11',
      'halaj2016':'European Central Bank Working Paper 1896',
      'behn2019':'European Central Bank Working Paper 2233',
      'pierson2020':'Systems, 8(1), article 9','cosentino2026':'Future Internet, 18, article 284',
      'mack1993':'ASTIN Bulletin, 23(2):213--225'}
    out=[]
    for r in rows:
        if not r.get('local_path'):continue
        authors=r['authors']
        if len(authors)>8:authors=authors[:3]+['others']
        if r['id']=='nassar2024':authors=authors[:4]+['others']
        url=r.get('download_url') or r.get('doi')
        fields={'author':' and '.join(authors),'title':'{'+r['title']+'}','year':str(r['year']),'howpublished':venue[r['id']]}
        if url:fields['url']=url
        if r.get('version_note'):fields['note']=r['version_note']
        out.append('@misc{'+r['id']+',\n'+',\n'.join('  '+k+' = {'+(v if k=='url' else tex(v))+'}' for k,v in fields.items())+'\n}\n')
    standards=[
      ('xbrloim','XBRL International','2021','Open Information Model 1.0: Recommendation, 13 October 2021','https://www.xbrl.org/Specification/oim/REC-2021-10-13/oim-REC-2021-10-13.html'),
      ('actus','ACTUS Financial Research Foundation','2026','ACTUS technical specifications: contract states, events, payoffs and risk-factor interface','https://github.com/actusfrf/actus-techspecs'),
      ('ifrs9','IFRS Foundation','2026','IFRS 9 Financial Instruments: issued-standard overview','https://www.ifrs.org/issued-standards/list-of-standards/ifrs-9-financial-instruments/'),
      ('ias32','IFRS Foundation','2026','IAS 32 Financial Instruments: Presentation: issued-standard overview','https://www.ifrs.org/issued-standards/list-of-standards/ias-32-financial-instruments-presentation/'),
      ('ifrs17','IFRS Foundation','2026','IFRS 17 Insurance Contracts: issued-standard overview','https://www.ifrs.org/issued-standards/list-of-standards/ifrs-17-insurance-contracts/'),
      ('ifrs18','IFRS Foundation','2026','IFRS 18 Presentation and Disclosure in Financial Statements: issued-standard overview','https://www.ifrs.org/issued-standards/list-of-standards/ifrs-18-presentation-and-disclosure-in-financial-statements/')]
    for key,author,year,title,url in standards:
        out.append('@misc{'+key+',\n author={{'+author+'}},\n year={'+year+'},\n title={{'+title+'}},\n url={'+url+'},\n note={Official source, accessed 2 October 2026}\n}\n')
    additions=BASE/'additional-references.bib'
    if additions.exists():out.append(additions.read_text())
    (ROOT/'docs/design/references.bib').write_text('\n'.join(out))

def build_tools():
    records=[]
    for p in (BASE/'software').glob('*-meta.json'):
        r=load(p);slug=r['full_name'].replace('/','_')
        files=[str(f.relative_to(ROOT)) for f in (BASE/'software').glob(slug+'-*') if not f.name.endswith('.json')]
        hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
        records.append({'repository':r['full_name'],'url':r['html_url'],'default_branch_at_access':r['default_branch'],'access_date':DATE,'last_push_metadata':r['pushed_at'],'archived':r['archived'],'github_license_detection':(r.get('license') or {}).get('spdx_id','not available'),'local_files':files,'sha256':hashes,'inspection_level':'official description/license and selected interfaces where archived; no integration executed','version_status':'content snapshots; branch names are mutable, implementation must pin a release or commit','fit_and_limits':'See Chapter 4 component table; no empirical performance endorsement'})
    dump('tools.json',{'date':DATE,'records':records,'additional_evidence':['docs/design/research/software/pierson-accounting-model.mdl','docs/design/research/raw/finqa-code-extra','docs/design/research/standards/actus-techspecs.tex'],'local_legalmath':['src/legalmath/translation/frontend.py','src/legalmath/translation/catala_structured.py','src/legalmath/translation/observations.py'],'local_legalmath_root':'/home/chakwong/python/legalmath','local_legalmath_scope':'Read-only inspection; shared typed interpretations and partial observations; ordinary execution selects one reading.'})

if __name__=='__main__':main()
