from pathlib import Path
import json,re
p=Path(__file__).resolve().parent
def write(n,x):(p/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
# Reasons describe a metadata screen unless technical reading is explicitly linked.
decisions={
'10.1007/s00780-020-00426-3':('inspected','Direct sequential financial stability method; see source-reading.md and theorem transfer limits.'),
'10.1007/s00440-020-00993-8':('partially inspected','Unifies competing information topologies; full proof-chain adoption remains pending.'),
'10.1214/21-aap1687':('inspected','Material estimator failure/repair; iid path and Lipschitz-rate conditions mapped.'),
'10.5802/ojmo.15':('targeted survey screen','Broad DRO alternatives and multistage references; primary proofs remain separate.'),
'10.1111/j.1467-937x.2007.00464.x':('seed duplicate','Indexed seed appears among its own citing records; do not count as independent follow-up.'),
'10.1111/j.1540-6261.2008.01314.x':('access-blocked lead','Information-quality ambiguity is directly relevant; Wiley403; author page links same journal route.'),
'10.3982/ecta7618':('technical follow-up open','Learning and asset returns may alter posterior/pricing interaction; not screened beyond metadata.'),
'10.1016/j.ejor.2015.05.048':('technical follow-up open','Risk aversion and multistage decisions are relevant to preference/update distinction.'),
'10.1287/opre.2024.0997':('access/linkage open','Causal transport with side information directly relevant; OpenAlex has no full text; arXiv title query returned different2006 paper, rejected as identity mismatch.'),
'10.1016/0305-0483(86)90017-4':('historical comparator open','Cash-flow management is a same-task comparator; no technical rejection without text.'),
'10.1016/0148-6195(83)90012-7':('access-blocked lead','Historical financial planning survey; university PDF403 retained.'),
'10.1016/0148-6195(83)90013-9':('historical comparator open','Financial planning/forecasting overview potentially supplies omitted implementations.'),
'10.1007/978-3-030-91231-4_102':('edition comparison open','2022 simultaneous-equation chapter potentially overlaps2021 online chapter; inspect editions before counting separately.'),
'10.1007/978-3-030-73443-5_102-1':('edition comparison open','2021 simultaneous-equation chapter; probable edition relationship requires text comparison.'),
'10.1007/978-3-031-14283-3_20':('historical/current comparator open','Planning and forecasting chapter could connect historical methods to current implementations.'),
'10.1080/1540496x.2026.2636779':('technical follow-up open','Title directly combines dynamic corporate disclosure and ambiguity; cannot omit from coverage closure.'),
'10.1080/24725854.2026.2638452':('technical follow-up open','Multiple-priors MDP may change rectangularity/persistence assumptions; direct methods needed.'),
'10.1214/25-aap2266':('targeted technical reading','Definition4; Theorems4.1–4.2 and Section5.1 proof assembly inspected; dominated finite-action assumptions retained.'),
'10.1137/24m1711650':('targeted reading and code audit','Retained v1 policy-class statement needs repair;11 author-code blobs inspected; no training or published-edition equivalence.'),
'10.1214/25-aap2239':('technical follow-up open','Empirical martingale projections relevant if pricing-measure constraints are added.'),
'10.1016/j.spa.2026.105032':('targeted technical reading','Retained2024 lift/transfer proofs and AppendixA inspected; finite-state economy not inferred.'),
'10.3150/26-bej1985':('conditional extension open','Irregular SDEs relevant to continuous-time extension, not proof for current finite quotient.'),
'10.1016/j.insmatheco.2023.01.003':('sector extension open','Insurance and ambiguity are material to wider mission; not a current corporate core theorem.'),
'10.1007/s10589-015-9758-0':('technical follow-up open','Dynamic tree generation is a direct computational alternative.'),
'10.1016/j.compchemeng.2014.03.019':('technical follow-up open','Output-performance scenario reduction may supply query-dependent comparison; inspect information assumptions.'),
'10.1109/tpwrs.2019.2901545':('technical follow-up open','Clustering approach requires decision/information preservation review before transfer.'),
}
# Other records are individually retained as scoped metadata leads, never falsely rejected.
reasons={
'Existence, duality, and cyclical monotonicity for weak transport costs':'Foundational weak transport; current claims use inspected adapted-finance result, not this duality theorem.',
'Stability of martingale optimal transport and weak optimal transport':'Pricing-constrained transport extension; technical assumptions not yet compared.',
'Measuring association with Wasserstein distances':'Association measurement is adjacent, not a direct sequential-policy guarantee.',
'Applications of weak transport theory':'General mathematical extensions; retain for future proof-chain review.',
'Continuity of the martingale optimal transport problem on the real line':'Special martingale one-dimensional extension; not current hybrid company guarantee.',
'Existence of Bass martingales and the martingale Benamou–Brenier problem in Rd':'Continuous martingale transport; scoped later extension, no adopted claim.',
'Geodesic Execution Slippage: A Statistical Physics Framework for Cryptocurrency Liquidity Risk':'Asset-execution application; metadata only, not financial-forecast validation evidence.',
'Generalizing super/sub mot using weak ℓ1 transport':'Transport extension; relevant only after defining adopted martingale constraints.',
'Robustness of optimal controlled diffusions with near-Brownian noise via rough paths theory':'Continuous-time robustness extension; no transfer to discrete corporate defaults checked.',
'IQ and Stock Market Participation':'Household participation evidence does not itself identify company disclosure/financing policy.',
'Individual Preferences, Monetary Gambles, and Stock Market Participation: A Case for Narrow Framing':'Preference-model alternative; title-level relevance only.',
'Ambiguous Business Cycles':'Macro ambiguity may inform scenarios; not inspected for company-history inference.',
'Ambiguity and Asset Markets':'Survey lead for asset-pricing model comparison; technical screening remains.',
'Ambiguity and Nonparticipation: The Role of Regulation':'Market participation/regulation application; does not settle persistent company type.',
'Regulatory Learning or Precaution? Capital, Reporting, and Supervisory Architecture Under Ambiguity':'Recent directly related regulatory title; source authority and methods unverified.',
'A U‐Shaped Flow–Performance Sensitivity Across the Globe':'Fund flows are adjacent evidence, not current simulator identification.',
'Robust portfolio game under relative performance and state-dependent confidence sets':'Strategic robust-control extension; state-dependent ambiguity constraints need direct review.',
'Limited participation under ambiguity of correlation and drifts in continuous time':'Portfolio participation extension, not a checked company policy.',
'Entrepreneurship under ambiguity: extending Aghion and Howitt':'Entrepreneurial macro application; retained as adjacent unreviewed lead.',
'Model Uncertainty and the Pricing of Hurricane Risk in Florida':'Risk pricing application; useful sector follow-up, not current validation.',
'An educational framework for information technology in accounting and management education':'Educational design adjacent to historical planning, no superiority exclusion inferred.',
'Modeling the Budgeting Process: Enriching the Learning Environment Using Monte Carlo Simulations':'Simulation-teaching comparator; technical suitability not yet checked.',
'Modellgestützte Generierung von Planbilanzen mit PLASMA':'Historical projected-balance-sheet system; language/access reading remains needed.',
'Flexibility of Corporate Planning Models in the Case of Changing Objectives':'Historical adaptive planning comparator; technical full text open.',
'The Customer-Funded Business—A Conceptual Analysis':'Alternative financing conceptual lead, not checked contract algorithm.',
'Introduction':'Uninformative chapter title; parent-volume identity required before relevance judgment.',
'Modeling and predictive control of a cash concentration and disbursements system':'Direct cash-control comparator; text and model access needed.',
'Financial modelling and corporate governance: A feminist perspective using an optimization approach':'Governance/modeling perspective retained; no technical exclusion from title.',
'Strategische Unternehmensplanung und Operations Research':'Historical OR planning source; language and technical inspection remain.',
'A study on the structure of planning behaviour':'Behavioral planning comparator; empirical/technical scope unknown.',
'Mathematical models in capital investment appraisal':'Recent repository metadata may denote an older thesis; actual edition/date verification needed.',
'Multi-stage nonlinear model predictive control applied to a semi-batch polymerization reactor under uncertainty':'Engineering application; can inform algorithmic comparison, not financial applicability by itself.',
'Stochastic multi-objective optimization: a survey on non-scalarizing methods':'Broader objectives survey; not a missing direct proof for current single-query bound.',
'Robust stochastic optimal control via variance penalization: application to energy management systems':'Variance-penalized control changes objective; transfer requires exact target comparison.',
'The McCormick Martingale Optimal Transport':'Relaxation for martingale transport; exactness/approximation conditions unreviewed.'
}
forward={};appearances=0
for f in sorted((p/'sources').glob('*forward*.json')):
 j=json.loads(f.read_text())
 for r in j.get('results',[]):
  appearances+=1;doi=(r.get('doi') or '').lower().replace('https://doi.org/','');title=r.get('display_name','');key=doi or r.get('id') or title
  status,reason=decisions.get(doi,('scoped metadata lead',reasons.get(title,'Individual title/metadata retained; technical relevance not decided.')));date=r.get('publication_date')
  if date and date>'2026-10-26':status,reason='excluded from as-of screen','Publication date after cutoff; earlier online availability not established.'
  if key not in forward:forward[key]=dict(id=r.get('id'),doi=doi,title=title,publication_date=date,disposition=status,reason=reason,technical_acceptance=False,appearances=[])
  forward[key]['appearances'].append(f.name)
write('forward-snowball.json',dict(date='2026-10-26',scope='OpenAlex top8/recent8 citing records for five material seeds; not all citing works or all source families',index_warning='Epstein seed duplicated among citing records; DOI deduplication applied. Citation metadata are discovery evidence only.',raw_appearances=appearances,unique_records=len(forward),records=list(forward.values())))
back=[
('ProbabilisticView2024','HooverKeisler1984','adapted distribution','Foundational antecedent; current claims use checked later characterization; original full proof chain pending'),
('ProbabilisticView2024','Hoover1991','amalgamation','Later AppendixA gives a counterexample to a broad lemma; original/version comparison required before broader historical verdict'),
('TCVAE2024','EderPammer2022','adapted total variation','Lemma3.5 dependency for KL bound; no adoption until original assumptions inspected'),
('KernelTopology2025','KaraYuksel2020','robust MDP approximation','Retained original v7 read: Assumption1.1, Theorems4.2-4.4/full proofs, LemmaA.1 and AppendixA.5, Corollary5.1. All-state optimality and state-action coverage retained; continuous-company transfer remains unproved.'),
('HartMoore1991','AghionBolton1991','control rights','Important alternative contracting mechanism; primary comparison remains'),
('HartMoore1991','Diamond1991','maturity and liquidity risk','Alternative maturity mechanism must not be conflated with deterministic human-capital model'),
('HartMoore1991','HartMoore1989','stochastic default and renegotiation','Distinct earlier model with stochastic returns; not silently equivalent to1991 deterministic paper'),
('McCarthy1982','Sorter1969','events approach','Foundational comparator, primary technical reading pending'),
('McCarthy1982','McCarthy1979','ER accounting','Prior architectural version; edition/method comparison open'),
('McCarthy1982','Chen1976','entity relationship','Foundational schema paper; no new claim relies on unread content'),
('McCarthy1982','Ijiri1975','accounting measurement','Measurement scope beyond economic event representation'),
('McCarthy1982','Mattessich1964','analytical accounting','Historical analytical competitor, technical reading open'),
('McCarthy1982','EverestWeber1977','relational accounting','Same-task database comparator, full method open'),
('McCarthy1982','BenbasatDexter1979','value versus events experiment','Empirical comparison needs original design and outcomes'),
('Suijs2007','Dye1985','nonproprietary disclosure','JSTOR anti-bot HTML; local illustration is not attributed as reproduction'),
('Suijs2007','Verrecchia1983','discretionary disclosure','Alternative cost-driven selection model; primary text open'),
('Suijs2007','KornSchiller2003','disclosure equilibrium','Credibility/out-of-equilibrium behavior relevant; access unresolved'),
('Seaman2013','Rubin1976','inference and missing data','Original inaccessible; Seaman supplies independently inspected primary theorems'),
('Seaman2013','LuCopas2004','model completeness','Necessity conditions require completeness; no general necessity claimed'),
('Adapted2020','PflugPichler2012','nested distance','Inspected with convexity/regularity restriction'),
('SMC2','AndrieuDoucetHolenstein2010','particle MCMC','Foundational target proof chain; source SMC2 appendix checked, separate original/code audit pending'),
('Benzoni2023','DeMarzoHe2021','leverage dynamics without commitment','Strategic issuance benchmark; direct source/code comparison open'),
('Benzoni2023','Leland1994','debt/default boundary','Classical comparator; exact local positive-recovery relation derived independently'),
('Dewatripont2003','HermalinKatz1991','observable nonverifiable effort','Theory antecedent; source-specific assumptions need direct text'),
('HartMoore1991','BerglofVonThadden1994','multiple creditors','DOI10.2307/2118356; RERO timeout and Oxford403; cannot dismiss unread competitor'),
('RahimianMehrotra2022','PichlerShapiro','multistage DRO foundations','Primary arXiv v2 technical sections and conditional-risk proof read; scoped comparison and exact case added'),
('RahimianMehrotra2022','Shapiro2016','rectangular probability sets','Primary Definition2.1/Theorem2.1 proof, finite pasting and appendix read; changed ambiguity family explicitly documented'),
('RahimianMehrotra2022','XinGoldberg','time inconsistency','Primary model/definitions and Observations5–7 with proofs6.3–6.5 read; full dependent moment theorem chain and edition comparison remain')
]
write('backward-snowball.json',dict(date='2026-10-26',scope='Individual material references identified in inspected sections/reference lists, not exhaustive bibliography closure',records=[dict(seed=a,candidate=b,topic=c,disposition=d) for a,b,c,d in back]))
omissions=[
('O01','Francis–Rowell1978','access','JSTOR HTML/ResearchGate403; OpenAlex no OA; historical planning overview alternative403. Obtain legal full text before method comparison.'),
('O02','Gentry1979 and1974 appendix','version/access','Journal403; 1974 scan retained. Recover missing derivation and compare actual editions; no equivalence assertion.'),
('O03','Strebulaev–Whited risky-debt convention','edition/correction','Local algebra repaired; publisher403 and author link returns existing SSRN route. Original correction status remains unresolved.'),
('O04','ACTUS matched runtime','software access/correspondence','Historical spec/dictionary pinned; matching public core not recovered. Supply inspectable core/dependencies and execute conformance cases.'),
('O05','Duarte–Fonseca code','code linkage','Inspected author/NBER routes lack matched package; unrelated book repository excluded. Obtain authentic package and audit equations/gradients.'),
('O06','General mixed/discrete approximate compression','method transfer','Finite joint-kernel coupling method now derived and checked across64 policies per type, including integer actions/default. Scalable mixed-state implementation must establish its uniform bound premises.'),
('O07','Company likelihood and policy identification','empirical/data','Observation and preference assumptions not identified by accounts. evaluation-protocol.md specifies evidence; E3 remains deferred.'),
('O08','Multi-creditor bargaining and insolvency','source/method','Simple priority and creditor-veto examples do not solve bargaining. Berglof–vonThadden access blocked; actual rights and implementation needed.'),
('O09','Rubin1976, Dye1985, Korn–Schiller','source access','Original technical text unrecovered; Seaman/Suijs support their own scoped results, not complete historical priority.'),
('O10','Hart–Moore and new financing theorem chains','reading','Hart–Moore1991 all62 pages read and Example1 reproduced. Remaining financing theorem dependencies and1994 edition correspondence still need inspection.'),
('O11','Forward/backward coverage','coverage','Five-seed bounded screen leaves material recent and primary-reference follow-ups; three dynamic-ambiguity primary follow-ups now read. No worldwide or all-cases completion claim.'),
('O12','Human comprehension and independent review','acceptance','Author self-review and rendered inspection only. Provisional drafting allowed; no human/independent acceptance inferred.'),
('O13','General real-company implementation','engineering','Exact diagnostic scripts and fixture arithmetic are not the runtime. Integrate only after target-specific implementation/conformance work; preserve master controls.')
]
write('omissions.json',dict(date='2026-10-26',status='OPEN_RESIDUALS_EXPLICIT',records=[dict(id=i,subject=s,type=t,next_evidence=e) for i,s,t,e in omissions]))
print(json.dumps(dict(forward_appearances=appearances,forward_unique=len(forward),backward=len(back),omissions=len(omissions))))
