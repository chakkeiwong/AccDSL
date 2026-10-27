# Bounded P18 argument integration review

You are an independent read-only reviewer. No tools, files, commands, edits or further reviewers. Review only this self-contained packet, not the whole proposal.

Check the manuscript argument, requirements and acceptance exposition for unearned readiness claims, wrong corpus counts, poor source boundaries, obsolete normative assertions or a disconnected implementation sequence. General reference detail in appendices is allowed when body teaches its premises. No human readability certification.

Accepted P16 architecture and P17 scoped methods are comparison baselines, not proof of full readiness. The candidate builds (122 pages, zero serious LaTeX warnings); render inspection is separate. Current ASC, whole real-company semantics, insurance transition/full VFA, actual regulatory/actuarial data, and human acceptance remain open. Do not label those honestly retained gaps a new P18 transcription failure. Source provenance is frozen; no new literature search is claimed.

Budget the review to finish in one response. Give at most 6 concrete findings, each with exact file/section and necessary repair, plus a brief reason for the verdict. Focus first on material mismatches; do not perform or narrate an exhaustive re-derivation of every case. Limit your final answer to 1000 words. End with exactly VERDICT: AGREE or VERDICT: REVISE. AGREE accepts only this packet's integration scope, with any minor nonblocking findings explicitly labelled.


## FILE docs/design/proposal/manuscript/accounting-product-proposal.tex

\documentclass[11pt,a4paper]{report}
\usepackage[margin=26mm,headheight=15pt]{geometry}
\usepackage{fontspec}
\setmainfont{Latin Modern Roman}
\setsansfont{Latin Modern Sans}
\setmonofont{Latin Modern Mono}[Scale=0.88]
\usepackage{amsmath,amssymb,mathtools,booktabs,longtable,array,tabularx,calc}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\usepackage{graphicx,xcolor,enumitem,listings,microtype}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning}
\usepackage[round,authoryear]{natbib}
\usepackage[hidelinks,bookmarksnumbered]{hyperref}
\usepackage{bookmark}
\definecolor{ink}{HTML}{17354A}
\definecolor{papergray}{HTML}{F4F6F7}
\hypersetup{pdftitle={AccDSL: Company Histories, Accounting Interpretations, and Scenario Simulation},pdfauthor={AccDSL design study}}
\pagestyle{headings}
\setlength{\parskip}{5pt}\setlength{\parindent}{0pt}
\setlength{\emergencystretch}{2em}
\setcounter{tocdepth}{1}
\setlist{itemsep=3pt,topsep=5pt}
\lstset{basicstyle=\small\ttfamily,backgroundcolor=\color{papergray},frame=single,
  rulecolor=\color{black!15},breaklines=true,columns=fullflexible,keepspaces=true,
  showstringspaces=false,tabsize=2,xleftmargin=5pt,xrightmargin=5pt}
\newcommand{\code}[1]{\texttt{#1}}
\newcommand{\E}{\mathbb{E}}
\newcommand{\Prob}{\mathbb{P}}
\newcommand{\Hist}{\mathcal{H}}
\newcommand{\req}[1]{\textsf{\textbf{#1}}}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\begin{document}
\hypersetup{pageanchor=false}
\begin{titlepage}
\vspace*{20mm}
{\sffamily\color{ink}\Huge AccDSL\par}
\vspace{7mm}
{\LARGE Company Histories,\par Accounting Interpretations,\par and Scenario Simulation\par}
\vspace{12mm}
{\Large Product and method proposal\par}
\vspace{5mm}
Version 2.0 (proposal candidate) \quad 6 October 2026
\vfill
This document specifies a system that translates company disclosures into
traceable evidence, represents several compatible economic and accounting
histories, and simulates their future journals and financial statements under
explicit economic scenarios.

The proposed data contracts, methods and acceptance cases specify the intended
implementation. Current source and domain limitations remain explicit; this
candidate is not a completed product or a claim of full proposal readiness. Proposed libraries can be replaced while preserving those
contracts. Sector rule packages require their own accounting review before
they can be described as compliant with a reporting standard.

\vspace{8mm}
Research materials, source qualifications and review records accompany this
document in \code{docs/design/research} and \code{docs/design/review}.
\end{titlepage}
\pagenumbering{roman}
\hypersetup{pageanchor=true}
\tableofcontents
\clearpage\pagenumbering{arabic}
\input{chapters/01-purpose}
\input{chapters/13-reference-company}
\input{chapters/02-history}
\input{chapters/03-literature}
\input{chapters/04-architecture}
\input{chapters/05-mathematics}
\input{chapters/06-language}
\input{chapters/07-execution}
\input{chapters/08-modules}
\input{chapters/14-financing-groups}
\input{chapters/15-banking}
\input{chapters/16-insurance}
\input{chapters/09-implementation}
\input{chapters/10-validation}
\appendix
\input{chapters/17-portable-reference}
\input{chapters/11-contracts}
\input{chapters/12-research}
\bibliographystyle{plainnat}
\begingroup\raggedright
\bibliography{references}
\endgroup
\end{document}


## FILE docs/design/proposal/manuscript/chapters/01-purpose.tex

\chapter{The product decision}
\label{ch:purpose}

A company's accounts describe the financial consequences of its activities,
but they leave much of the activity itself unobserved. Revenue combines many
sales, a borrowing balance combines contracts with different terms, and a
provision combines estimates about uncertain future payments. Aggregation is
necessary for reporting. It also makes the inverse task---recovering economic
history from published reports---fundamentally different from entering known
transactions into a ledger.

AccDSL will preserve this distinction. Its first product is an evidence-backed
representation of a company's historical record. Its second is a set of
compatible histories and current economic states. Its third is a collection of
conditional simulations, each explaining how a particular history, accounting
treatment and business response produces future journals and reports. These
products share identifiers and provenance, so an analyst can move from a
forecast balance to the assumption or disclosure responsible for it.

The recommended design is a small, typed accounting language over a shared
intermediate representation, combined with an evidence database, contract
calculators and replaceable inference engines. A language earns its place by
making recurring accounting decisions explicit and checkable: which entity and
period an amount belongs to, whether it is known or assumed, which rule applies,
and how an event changes a balanced ledger. The language does not supply missing
facts or determine a company's future behaviour.

\section{Why journals are necessary but insufficient}

Consider a company with a borrowing of 100 currency units and annual interest
expense of 5. Assume that the entire principal was outstanding throughout the
year, interest was paid at year-end, and there were no fees, defaults, hedges or
foreign-exchange effects. Both a fixed-rate loan at 5\% and a floating-rate loan
whose rate happened to be 5\% generate the same entries:
\begin{center}
\begin{tabular}{lrr}
\toprule Account & Debit & Credit\\\midrule
Cash, on initial borrowing &100&\\
Borrowing liability &&100\\\midrule
Interest expense, at year-end &5&\\
Cash &&5\\\bottomrule
\end{tabular}
\end{center}
Even the full historical journal would not distinguish these two contracts.
Now impose a scenario in which the floating rate resets immediately to 7\%
for the whole next year. The fixed loan produces interest of 5; the floating
loan produces interest of 7. If the disclosure is also compatible with any
fixed-rate fraction $\alpha\in[0,1]$, future interest is
\begin{equation}\label{eq:running}
 I(\alpha)=100[0.05\alpha+0.07(1-\alpha)]=7-2\alpha.
\end{equation}
The historical accounts are compatible with the whole interval $[5,7]$ of
future interest. This is a range of feasible amounts. It becomes a probability
distribution only when a distribution for $\alpha$ is supplied. Neither the
number of generated interpretations nor a language model's confidence provides
that distribution.

Journals remain essential because simulated economic events must have coherent
accounting consequences. However, the simulated state must also contain
contract terms, maturities, customer or borrower cohorts, collateral,
unrecognised commitments, and management decisions. These determine what the
journals will be under a changed economy. Reconstructing every historical
transaction is unnecessary when a smaller state preserves the responses needed
for the intended scenarios. Establishing that smaller state is an explicit
modelling task, examined in Chapter~\ref{ch:math}.

The analogy with competing legal interpretations is useful at the level of
representation. Several readings may survive the evidence and require separate
reasoning. In accounting, some alternatives concern the meaning of a disclosure;
others concern undisclosed facts or future behaviour. The system must identify
which kind of uncertainty is involved. A known contractual term must not become
an arbitrary interpretive choice merely because another choice is convenient
for a simulation.

\section{Users, questions and deliverables}

An accounting analyst needs to inspect a number in its original table, verify
its entity, currency and period, and see how it reconciles with the notes. A
financial modeller needs to distinguish a reported balance from assumptions
about its composition. A language engineer needs deterministic semantics and
tests. A researcher needs to compare explanations under the same scenario,
including explanations that fit history equally well.

The first release must answer the following complete workflow. An analyst
loads a set of reports and specifies an information cutoff. AccDSL preserves
the original documents and extracts source-linked observations. It identifies
reconciliation failures and constructs an explicitly bounded family of
compatible histories. The analyst declares additional assumptions where
simulation requires them. The system executes each requested scenario and
returns statements, journal traces, explanation-specific distributions or
bounds, and unresolved limitations. When a later filing arrives, the analyst
can compare the revised interpretation with the earlier information set.

\begin{longtable}{L{34mm}L{102mm}}
\toprule Requirement & Required behaviour\\\midrule\endhead
\req{R1 Evidence} & Every observed amount or narrative assertion retains its
document version, location, extraction method and original representation.\\
\req{R2 History} & Queries distinguish economic time, reporting period,
publication time and database ingestion time; restatements remain recoverable.\\
\req{R3 Meaning} & Entity, perimeter, dimensions, currency, measurement basis,
standard version and accounting concept accompany values.\\
\req{R4 Ambiguity} & Discrete alternatives and continuous unknowns retain their
joint constraints across accounts and periods. Missing values never mean zero.\\
\req{R5 Accounting} & All committed journals balance in the book's functional
currency, and balances reconcile to explicitly classified movements.\\
\req{R6 Economics} & Contracts, exposures and behavioural assumptions drive
events. Accounting identities alone never determine scenario responses.\\
\req{R7 Results} & Conditional results survive by interpretation and scenario.
Weighted results require declared, normalised probability measures.\\
\req{R8 Explanation} & A report cell can be traced to journals, events, rules,
assumptions and evidence, including consolidation adjustments.\\
\req{R9 Extensibility} & Standard, industry and company packages extend shared
types through versioned interfaces, with explicit unsupported cases.\\
\req{R10 Reproduction} & A saved run records source versions, model versions,
parameters, calendars, seeds and numerical conventions.\\\bottomrule
\end{longtable}

These are acceptance requirements. Python, SQL storage, a particular parser,
and a particular constraint solver are implementation choices. Initial support
will cover a non-financial company with cash, receivables, payables, inventory,
fixed assets, ordinary debt and ordinary equity. Banks and insurers must be
representable in the core data model from the outset, but their executable
measurement and behavioural packages follow dedicated milestones. Until a
package supports an instrument, the result is explicitly incomplete.

\section{What constitutes a useful first implementation}

The first demonstrator should reconstruct three reporting dates and the
intervening annual and interim flows for one company, including at least one
restatement or revised comparative. It must preserve a borrowing-composition
ambiguity and execute the fixed/floating example through both journals and all
affected statement lines. A synthetic company supplies known hidden history;
a public company supplies realistic disclosure and extraction problems. Their
roles differ: the synthetic case tests preservation and rejection of known
alternatives, while the public case tests traceability and practical coverage.

Success is a reproducible chain of evidence and computation, with identified
gaps. A convincing-looking complete ledger reconstructed from incomplete
disclosures would fail this product contract if its assumptions were hidden.
Forecast accuracy requires a later evaluation with historical information
cutoffs and suitable baselines; it is not established by the first demonstrator.


## FILE docs/design/proposal/manuscript/chapters/03-literature.tex

\chapter{What the literature contributes}
\label{ch:literature}

The research problem crosses accounting, databases, programming languages,
econometrics and document understanding. Each field resolves part of it. The
review below distinguishes results that can be adopted directly, engineering
ideas that need adaptation, and evidence that does not establish the intended
product capability. Source versions and technical anchors are recorded in the
accompanying research ledgers. The search includes work outside the original
collection, with public-index searches and backward and forward citation
searches through 2 October 2026. It is a scoped design survey, rather than a
claim to enumerate every paper in these fields.

\section{Accounting structure and company dynamics}

\citet{nehmer1997}, especially Sections 2--5, supplies a useful algebraic
starting point: balances occupy a structured state space, transactions change
that state, and aggregation relates detailed accounts to reports. This supports
a distinction between conservation constraints and permitted transactions.
An entry can conserve the accounting total and still be an inadmissible
transaction. AccDSL adopts that distinction in its posting validator. Its
particular event vocabulary, evidence model and inverse-history semantics are
new design decisions, not results established by the algebraic paper.

\citet{doshi2024} develops an accounting DSL with time, transaction logs and
correction mechanisms. The relevant material is in Chapters 4 and 7--9 of the
2024 thesis; the original collection's filename misleadingly suggests 2026.
It demonstrates why corrections and dates belong in the language rather than
in informal comments. The thesis does not establish recovery of an entire
company history from public reports or inference over economically distinct
histories. \citet{babcinetchi2022}, pp.~342--345, offers a much smaller accounting
language and grammar proposal. It is useful as a syntax precedent, but it
provides insufficient semantics or evaluation to govern AccDSL by itself.

\citet{shahnazarian2004} connects accounting dynamics with behavioural and
econometric equations. Sections 2.3--2.8 describe the accounting relationships;
the optimisation and econometric discussion in Chapter 3 and the data and
evaluation material in Chapters 4 and 8 show how the model is used with
standardised Swedish corporate data. This is an important precedent for
simulating companies under changed conditions. Its standardised tax-data
starting point differs from heterogeneous public-report extraction, and its
working-capital funds formulation should not be imported as a general modern
cash-flow statement implementation. The transferable idea is the explicit
separation of accounting evolution and behavioural assumptions.

\citet{pierson2020}, Sections 3--4 and the reporting structures, makes that
separation operational in system dynamics. Receivables, payables and wages
accumulate differences between accrual and payment flows; reporting-period
accumulators turn instantaneous flows into statements. AccDSL can use these
structures as examples of coherent movement schedules. The model's payment
delays, inventory approximations and simplified equity treatment remain
modelling choices. They are not universal defaults for companies or evidence
that an aggregate state is sufficient for all shocks.

Bank models demonstrate why journal generation needs economic state.
\citet{halaj2016}, Section 3, combines funding shocks, fire sales, loans,
securities and risk constraints. The homogeneous portfolios and specified
funding process make the model tractable, but limit instrument-level
interpretation. \citet{behn2019}, Section 2, makes managers' choices over asset
growth, debt, risk and payouts depend on capital and liquidity constraints.
These models motivate interfaces for management policy and regulatory
calculations. Their parameterisations must be calibrated and evaluated for
the target application; passing their accounting identities would not validate
an AccDSL forecast.

Two important neighbouring traditions remain explicit coverage qualifications.
McCarthy's 1982 REA model is a foundational candidate for the relation between
resources, events and agents; Caiani and co-authors' stock-flow-consistent
agent-based benchmark is a candidate for simulation across interacting sectors.
Verified primary PDFs could not be obtained in this retrieval campaign after
institutional and publisher attempts. Their records are retained in the omission
register, and no technical result from either is used to justify the design.
AccDSL's event and counterparty records are specified and justified directly
below. A later multi-company equilibrium engine would require expansion of
the stock-flow-consistent literature before implementation.

\section{Incomplete information and provenance}

Financial disclosures are incomplete databases in a substantive sense.
Multiple underlying records can yield the same published observations.
\citet{libkin2014}, Sections 2--5, explains the semantics of incomplete
databases, labelled nulls, conditional tables and certain answers. Repeated
occurrences of the same unknown must share a value. Conditional tables can
represent dependence between alternatives that independent missing cells
cannot express. This is directly relevant to a debt note and a cash-flow table
that refer to the same unknown repayment.

AccDSL adopts shared symbolic unknowns and conditions. It extends the database
idea with accounting constraints, continuous amounts, temporal transitions and
economic event models. A ``certain'' answer means a statement that holds for
every history in the declared feasible family. The family itself may omit
unknown mechanisms; certainty is therefore always relative to a model scope.
Imieliński and Lipski's original 1984 paper is a foundational backward lead
whose publisher copy was inaccessible in this campaign. The inspected Libkin
paper supplies the technical discussion actually used here.

\citet{green2007}, Definitions 3.1--3.2 and Section 4, treats provenance as
annotations that compose through relational operations. Combining sources
and alternative derivations can therefore have formal semantics, rather than
being a list of unrelated citations. This is useful for report aggregation and
explanation queries. Positive relational operations covered by provenance
semirings do not by themselves specify every operation AccDSL needs: negation,
nonlinear valuation, optimisation and probabilistic conditioning require their
own derivation records. Accordingly, the implementation starts with a typed
dependency graph and may use semiring annotations for supported relational
subqueries. A dependency edge is not a posterior probability.

\citet{snodgrass1986} distinguishes historical validity from the time facts
are stored. The archived paper is \emph{Temporal Databases}, by Snodgrass and
Ahn, not the later Jensen--Snodgrass paper initially returned by a search.
Its snapshot, rollback, historical and temporal examples support the need to
recover both old business facts and old database beliefs. AccDSL adds public
availability time because a database insertion date cannot establish whether
a historical investor could have seen a filing.

\section{Inverse problems, identification and probability}

\citet{stuart2010}, Section 2.2, starts from an observation equation
$y=G(u)$ and distinguishes inversion, regularisation and Bayesian inference.
The discussion makes explicit that a regularising norm or prior is an
additional assumption. AccDSL has a similar observation problem, although
its unknowns include discrete accounting interpretations and event structures
as well as continuous parameters. The infinite-dimensional well-posedness
theorems in that paper are not automatically applicable to this mixed,
potentially discontinuous model.

The relevant issue is often identification rather than computation alone.
\citet{giacomini2021}, Sections 2.1--2.6 and Theorem 1 of the archived 2020
working version, shows how a class of priors can preserve uncertainty within
an identified set. A likelihood that is flat over the unresolved part does
not learn the conditional prior over that part. Posterior lower and upper
probabilities summarise a class of posterior beliefs. The paper's regularity
conditions and application to structural vector autoregressions do not prove
that an arbitrary accounting program admits the same algorithms or guarantees.
The design borrows the distinction between learnable quantities and
assumption-dependent distributions; the simple accounting bounds in
Chapter~\ref{ch:math} are derived directly.

\citet{hoeting1999}, equations (1)--(3), gives Bayesian model averaging as a
weighted sum of model-conditional distributions, with weights determined by
model priors and marginal likelihoods. Sections 3 and 5 discuss computation
and prior specification. This supports an optional weighted mode, provided
AccDSL specifies the likelihood, priors and candidate model space. It does
not justify giving equal mass to every syntactically different journal
reconstruction. Two encodings of the same economic history must not gain extra
weight by duplication. Model averaging also remains conditional on the
considered model family, rather than repairing missing mechanisms.

Scenario semantics need similar care. \citet{pearl2009}, Section 3.2.1 and
equations (5)--(6), distinguishes an intervention that replaces a structural
equation from ordinary conditioning. AccDSL will distinguish a supplied
exogenous path, an observational conditional forecast and an intervention.
A rise in rates imposed by a stress test is not automatically distributed as
the collection of historical periods in which rates happened to be high.
Identifying a causal effect requires assumptions beyond reproducing accounts.

\section{Languages for rules and contracts}

\citet{vandeursen2000} surveys DSL benefits, risks and implementation options.
\citet{mernik2005}, Sections 1.1 and 2.2--2.5 of the archived CWI report,
treats application libraries as serious competitors and distinguishes deciding,
analysing, designing and implementing a DSL. Its implementation decision tree
explicitly includes embedding in a host language. The literature therefore
supports a conditional design decision: a DSL is attractive when domain
constraints and repeated notation justify it, but an ordinary typed library
may be cheaper and equally expressive. AccDSL will implement one shared
representation accessible from both a Python API and a textual language, so
syntax does not become a prerequisite for testing the accounting model.

\citet{merigoux2021}, Sections 3--4 and Figures 8--9, provides Catala's scopes,
exceptions, default calculus and translation into a conventional functional
target. Its explicit empty and conflict outcomes are valuable precedents for
accounting rules with exceptions. They are different from probabilistic
uncertainty. AccDSL will preserve this distinction: conflicting applicable
rules produce a diagnostic, while an evidence-supported alternative reading
produces a conditional model branch. The paper's compiler correctness results
do not establish correctness of our accounting rules or of an automatic
translation from disclosures.

The inspected LegalMath code offers reusable ideas in its shared typed
interpretation, partial observations, source references and validity/knowledge
times. Its ordinary frontend execution selects a reading. AccDSL needs an
additional execution mode that retains a family of readings, continuous
unknowns and economic state. A bounded candidate generator is useful for
search, but its candidate limit does not prove completeness.

\citet{jones2000}, Sections 3--5, builds complex financial contracts from
combinators and separates their compositional meaning from a chosen valuation
model. The ACTUS technical specification similarly separates contract states,
scheduled events, state transitions and payoffs, with risk factors supplied
through an interface \citep{actus}. These are strong reasons to represent
contractual obligations independently of accounting classifications. Neither
contract cash flows nor a derivative price determine the recognition,
measurement and presentation rules of a complete IFRS or US GAAP book.

\section{Extraction and financial reasoning}

The document literature supports a staged ingestion process. PubTables-1M
\citep{smock2022}, in its canonicalisation procedure and evaluation section,
distinguishes table detection, structure recognition and functional analysis.
Its GriTS evaluation compares reconstructed table structure. TableBank
\citep{li2020}, Sections 3--4, uses document structure to obtain weak supervision
for table detection and recognition. GTE and FinTabNet \citep{zheng2021},
Sections 3--5, provide a financial-document setting and company-level dataset
splits. These sources help select extraction components and evaluation units.
Their table scores do not establish that a debt note has been interpreted
correctly across years or that every off-balance-sheet exposure has been found.

The Docling report \citep{nassar2024}, Section 3, describes PDF parsing, page
layout analysis and table structure recognition within a document-conversion
pipeline. The locally archived version lists Christoph Auer first; this
version difference is recorded in the catalogue. Docling is an ingestion
candidate whose output must retain source locations and undergo accounting
validation. Its code and model licences must be considered separately when
packaging a deployment.

FinQA \citep{chen2021}, Sections 3--6, provides questions with executable
reasoning programs and supporting evidence. TAT-QA \citep{zhu2021}, Sections
2--4, combines table cells and text spans with aggregation operations, and
explicitly treats numerical signs in evaluation. DocFinQA \citep{reddy2024}
extends financial questions to long documents and evaluates retrieval/context
choices. FinBen \citep{xie2024} broadens the collection of financial tasks and
model evaluations. These benchmarks can test retrieval and local numerical
reasoning. Their question-answer format does not require a complete
multi-period company representation, joint alternative histories or
scenario-dependent journal generation.

A directly relevant recent competitor is the auditable RAG architecture of
\citet{cosentino2026}. Sections 3.1--3.2 describe persistent extraction,
enrichment, retrieval and provenance records; Section 4.6 checks citation
resolvability and failure recovery. Section 5 limits the interpretation of
those results to the evaluated document-intelligence tasks. AccDSL should
reuse the idea of persistent evidence and recoverable processing, while adding
executable accounting and economic semantics. No performance comparison with
that architecture has been run here.

\section{Solvers and probabilistic execution}

\citet{damoura2008}, Sections 2--3, describes Z3's interfaces and theory-solving
architecture. It supports choosing an SMT solver for logical choices and
arithmetic constraints, but does not make arbitrary nonlinear simulation
tractable. The first solver fragment is deliberately bounded: finite choices,
exact linear arithmetic and selected calendar relations. Unsupported formulas
remain in the representation with a solver diagnostic.

\citet{vandeMeent2018} develops probabilistic programs through sampling,
observations and inference; the inspected material includes the first-order
language and weighted sampling discussion. Stan \citep{carpenter2017}, its
model language and sampler-output discussion, and Pyro \citep{bingham2019},
Sections 2--3, show different ways to separate a probabilistic model from
inference machinery. They are candidates for optional inference over an
already-defined economic model. Exact accounting identities and discrete rule
selection should not be turned into nearly satisfied likelihood penalties
merely to fit an inference library. Nor should successful sampler execution
be described as evidence that all interpretations were explored.

\section{The remaining design problem}

The combined literature provides algebra for journals, semantics for missing
information, temporal storage, provenance, contract languages, rule languages,
inference methods and extraction tools. The unresolved integration problem is
to retain their distinctions while connecting them: a disclosure constrains
economic histories; a history supplies contract and behavioural state; a
scenario drives events; accounting rules produce journals; reporting rules
render statements; and every step remains explainable.

The design is therefore an integration proposal with several local
mathematical constructions. Its originality and empirical advantage have not
been established by this survey. Its practical merit will depend on the
acceptance cases, accounting review and comparative implementation work in
Chapter~\ref{ch:validation}.


## FILE docs/design/proposal/manuscript/chapters/04-architecture.tex

\chapter{Architecture and reuse}
\label{ch:architecture}

\section{One representation, several authoring methods}

The architectural centre is a typed intermediate representation (IR), not a
text parser. A document extractor, a human editor, a Python library and the
AccDSL compiler all create the same records. This allows a modeller to begin
with a reviewed structured file and later add convenient notation. It also
allows source extraction to improve without changing accounting semantics.

\begin{figure}[ht]
\centering
\begin{tikzpicture}[node distance=7mm,>=Latex,
 box/.style={draw=ink,rounded corners,align=center,text width=112mm,
 minimum height=10mm,font=\small,fill=papergray}]
\node[box] (e) {Documents and tagged filings\\immutable evidence, source spans and reporting contexts};
\node[box,below=of e] (h) {Typed historical representation\\observations, entities, contracts, mappings and constraints};
\node[box,below=of h] (i) {Compatible histories and declared assumptions\\discrete alternatives, continuous families, optional weights};
\node[box,below=of i] (s) {Scenario execution\\economic events, accounting rules and balanced journal batches};
\node[box,below=of s] (r) {Reports and conditional results\\statements, movement schedules, bounds and explanations};
\draw[->] (e)--(h);\draw[->] (h)--(i);\draw[->] (i)--(s);\draw[->] (s)--(r);
\end{tikzpicture}
\caption{The simulation path. Every transformation records its inputs and
assumptions; the source record remains available throughout.}
\label{fig:architecture}
\end{figure}

Evidence storage and economic modelling must remain separate. If a company
reports 100 of borrowing, a model can assume two loans of 60 and 40 without
creating a new reported fact that the company disclosed those loans. The
contract library consumes the assumed terms, the accounting module consumes
the resulting events, and the explanation graph records the assumption at
each affected result.

\section{Why a DSL, and when another approach is better}

The strongest baseline is a typed schema, SQL storage and ordinary Python
code. That combination can implement the whole product. Its disadvantage is
that repeated accounting requirements can become conventions scattered across
functions: implicit currency conversion, missing period checks, hidden default
values and duplicated rule selection. A bounded language makes these
requirements part of typing and compilation. Its costs are language
maintenance, diagnostics, migration and training.

\begin{longtable}{L{29mm}L{51mm}L{56mm}}
\toprule Approach & Useful role & Limitation for this product\\\midrule\endhead
Typed schema and Python & Reference executor, flexible economic models,
initial authoring API & Domain restrictions require disciplined APIs or a
validator; arbitrary code complicates static analysis and provenance.\\
XBRL and OIM & Tagged evidence, contexts, dimensions, taxonomies and exchange &
Reported facts and reporting relationships do not recover hidden economic
histories or specify scenario behaviour.\\
Ledger languages & Recording known transactions, balance checks, export and
differential testing & Alternatives, source interpretation and contract
exposure need additional semantics.\\
Knowledge graph / SQL & Relationships, lineage, temporal queries and evidence
navigation & A graph or schema alone does not define event execution or the
probability meaning of alternatives.\\
Rules / Catala & Dated policy logic, defaults, exceptions, traceable rule
evaluation & Ledger state, event scheduling and ensembles require an enclosing
runtime.\\
Probabilistic program & Priors, likelihoods and inference over model parameters &
Needs declared probability measures; cannot turn unspecified ambiguity into
probability or supply accounting rules.\\
Spreadsheets & Familiar review and small transparent financial models &
Versioned evidence, shared unknowns and branching histories are difficult to
govern as the model grows.\\
AccDSL over shared IR & Common domain checks, reusable templates, explicit
alternatives and deterministic posting semantics & Requires implementation and
evaluation; broad notation without stable semantics would add cost.\\
\bottomrule
\end{longtable}

The decision is to implement the IR, validators and Python reference API first,
then the textual frontend. The same conformance cases must pass through both
frontends. If the DSL fails to reduce ambiguity in representative authoring
tasks, the IR and library remain useful. This is a reversible product decision,
not a claim that a new language is inherently better than a library.

\section{Open-source components}

The following survey uses official repository descriptions, licence files and
selected source interfaces archived on 2 October 2026. It is a source
inspection, not an executed integration or performance evaluation. The
machine-readable tool ledger records retrieval paths and available version
metadata. Dependencies must be pinned when implementation begins; a branch
name observed during this survey is not a release requirement.

\begin{longtable}{L{26mm}L{71mm}L{39mm}}
\toprule Component & Proposed use and checked boundary & Licence / decision\\\midrule\endhead
Arelle & Parse and validate XBRL/iXBRL. Inspected \code{ModelFact}, context and
unit accessors. Preserve taxonomy extensions and full contexts when importing.
& Apache-2.0 core; first-choice adapter.\\
Docling & PDF layout, text and table conversion. Inspected converter interface;
retain page coordinates and extraction settings. & MIT code; assess model
licences separately. Candidate.\\
Table Transformer & Table extraction baseline associated with PubTables-1M;
check finance-domain performance before selection. & MIT; repository marked
archived in inspected metadata. Baseline, not a maintenance default.\\
Beancount & Posting and transaction data types; export selected concrete
branches and compare balances. & GPL-2.0 project metadata; integration and
redistribution choice needed. Optional adapter.\\
Ledger & Known-journal reference and export. Inspected transaction balancing
code and manual date/assertion behaviour. & BSD-style licence; optional
reference tool.\\
hledger & Alternative ledger import/export and accounting checks. Repository
documentation inspected. & GPL-3.0 project metadata; optional process adapter.\\
Catala & Potential backend for deterministic policy modules; defaults and
exceptions have useful semantics. & Apache-2.0; prototype only after core
execution semantics stabilise.\\
ACTUS & Contract schedules, payoffs and transitions; external risk-factor
interface. Verify event schedules against ACTUS tests. & Service Apache-2.0;
technical specification CC-BY-SA-4.0. Candidate contract adapter.\\
QuantLib & Calendars, cash flows and valuation. Floating coupon source separates
fixing dates and pricing. Accounting treatment remains external. & Modified
BSD-style licence; candidate valuation adapter.\\
OpenFisca & Versioned tax-benefit formulas as a rule-system reference; inspected
variable/formula metadata. Corporate-tax coverage must be supplied. & AGPL-3.0;
optional, not the core runtime.\\
Z3 & Finite alternatives, logical compatibility, linear constraints and conflict
explanations. & MIT licence text; first solver candidate.\\
DuckDB & Local analytical queries over extracted facts and results. & MIT;
candidate alongside SQLite transactional storage.\\
Stan & Continuous probabilistic models and diagnostics with an explicit target.
Inspected model interface and paper. & BSD-3-Clause; optional inference backend.\\
Pyro / PyMC & Alternative probabilistic backends for model-specific inference.
Pyro design paper and project descriptions inspected. & Apache-2.0 / Apache-2.0
licence texts; optional, no default selection.\\
\bottomrule
\end{longtable}

The licence entries identify the inspected projects, not a legal conclusion
about every combination of code, models and datasets. The default product
architecture can communicate with optional tools through explicit adapters.
This does not, by itself, settle redistribution obligations. That question is
resolved when a concrete dependency and distribution method are selected.

XBRL's Open Information Model supplies standardised facts with concepts,
entities, periods, units and dimensions \citep{xbrloim}. Those facts are an
excellent ingestion source. AccDSL retains their original contexts and
decimals rather than flattening them immediately into a company-by-year table.
Calculation relationships can help validate reporting totals, but are not a
general description of the transactions that generated those totals.

\section{Responsibilities that AccDSL must implement}

AccDSL owns the evidence and temporal model, typed accounting concepts, shared
unknowns and alternatives, rule-package selection, journal validation,
consolidation provenance and report explanations. It also owns the distinction
between feasible sets and distributions. These responsibilities cannot be
delegated implicitly to whichever parser or solver is convenient.

External components receive narrow requests and return typed responses.
A contract adapter returns scheduled events, cash-flow quantities, state
changes and source/model references; it does not directly mutate the ledger.
A valuation adapter returns a measure, currency, date, method and numerical
status; the accounting package decides whether and where to recognise the
change. A solver returns feasibility or bounds with scope and completeness
status. A language model proposes source-linked mappings or interpretations;
it cannot commit an unsupported assertion as fact.

The architecture consequently permits deterministic reference execution,
alternative solvers and later acceleration without changing the meaning of a
historical observation or a journal entry. Performance work begins only after
the same semantic cases pass through these interfaces.


## FILE docs/design/proposal/manuscript/chapters/10-validation.tex

\chapter{Acceptance and implementation sequence}
\label{ch:validation}

The reference cases now make several of the acceptance obligations executable
as design checks. Northstar provides full statements and a known compatible
history; Apple supplies real source contexts and a bounded marginal stress;
bank, insurance, consolidation and inventory fixtures test the core's broader
state requirements. They do not constitute a production implementation.

\section{Three different questions require different evidence}

Engineering correctness asks whether the implementation follows the specified
types, transitions and arithmetic. Accounting validity asks whether the
selected rules faithfully implement the applicable standards and disclosed
policies. Scientific validity asks whether the economic assumptions and
uncertainty representation support the intended forecasts or comparisons.
A balanced journal answers only part of the first question.

The implementation must therefore maintain separate validation results.
Compilation and deterministic examples cannot establish forecasting quality.
Agreement with a public report cannot identify an undisclosed contract term.
A lower extraction error on a document benchmark cannot establish that the
engine preserved every materially different scenario response.

\section{Core conformance cases}

\begin{longtable}{L{16mm}L{73mm}L{47mm}}
\toprule Test & Required case & Pass condition\\\midrule\endhead
T01 & Exact debit/credit batches, including reversals and period closing &
Every committed book conserves signed balances; imbalance rejected atomically.\\
T02 & Money, quantities, currencies, instants and interval flows &
Invalid additions and context combinations rejected; explicit conversions traced.\\
T03 & Original filing, later correction and as-known cutoff &
Earlier query reproduces the original evidence view; later view shows revision.\\
T04 & Annual and interim cumulative flows with revised comparatives &
Quarter derivation only across compatible contexts and vintages.\\
T05 & Fixed/floating borrowing with identical historical postings &
Both explanations survive; next-year expense is 5 and 7 under the stated shock.\\
T06 & Continuous fixed share $\alpha\in[0,1]$ &
Exact model returns $I=7-2\alpha$ and extrema 5, 7 without assigning probabilities.\\
T07 & Duplicated encoding of one history &
Canonical duplicates preserve results and declared weights; no extra
probability mass from an additional encoding.\\
T08 & Linked interpretation across debt classification and payment treatment &
Impossible combinations rejected through shared constraints.\\
T09 & Rounded totals, duplicate facts and contradictory notes &
Correct interval compatibility; no automatic zero or balancing plug.\\
T10 & Infeasible or unsupported constraint problem &
Conflicting sources exposed; timeout/unsupported case reported as unknown.\\
T11 & Zero-coupon bond and ordinary equity examples &
Carrying amounts, payments, share quantities and report mappings match derivations.\\
T12 & Foreign-currency asset, translation and cash movement &
No mixed-unit balance test; translation effects separated from cash flows.\\
T13 & Acquisition and intragroup balance elimination &
Perimeter and adjustment book reproduce group totals without inventing capex.\\
T14 & Conflicting recognition rules and unknown guards &
Explicit conflict or symbolic partition; file order has no effect.\\
T15 & Insufficient cash with constrained funding &
Funding failure/default retained as an outcome; no hidden borrowing.\\
T16 & Expected-loss measurement before future default is realised &
Measurement uses only information allowed at that date.\\
T17 & Repeated/reordered independent events and interrupted execution &
Idempotent replay; branch isolation; identical committed outputs.\\
T18 & Conditional distributions and optional weighted mixture &
Branch distributions retained; mixture agrees with declared weights and total
probability; unweighted family never labelled probabilistic.\\
\bottomrule
\end{longtable}

For synthetic cases, expected histories, excluded histories and scenario
consequences are known by construction. Tests should include counterexamples
that balance but have the wrong economic effect, such as treating a
non-cash acquisition movement as operating cash. Such tests discriminate
between arithmetic validity and the intended semantics.

Differential tests against an existing ledger check only the shared supported
subset. ACTUS schedule comparisons check contractual events, and QuantLib
comparisons check selected valuation calculations under matched conventions.
Disagreements must be classified as different conventions, unsupported cases
or implementation errors before one tool is treated as an oracle.

\section{Extraction and reconstruction evaluation}

A company corpus must include different standards, industries, languages,
filing formats, extensions, interim calendars and restatements. Company and
time splits are required so repeated report templates or revised versions do
not leak into evaluation. Public benchmark tables are useful development
material, while acceptance uses complete disclosure packages that include
notes and their relationships.

Reviewers annotate source facts, contexts, mappings, required relationships,
known ambiguities and unsupported assertions. Relevant measures include
correct source-linked values and contexts, unresolved extraction volume,
coverage of note obligations, reconciliation failures and invented facts.
Report each separately. A single overall score can hide a serious error in a
small but consequential financing note.

Historical reconstruction should test whether the known synthetic history
remains feasible, whether known incompatible histories are rejected, and
whether economically distinct alternatives are preserved. On real companies,
public data generally cannot establish the true journal. Review instead
assesses evidential compatibility, unsupported commitments and conditional
economic consequences. Later disclosures may provide discriminating evidence
for previously ambiguous terms.

No universal numerical threshold for semantic coverage or extraction accuracy
is fixed in this document. Before a release evaluation, an accounting-reviewed
test corpus and task-specific acceptance thresholds must be recorded in an
evidence contract. Hard conformance failures, fabricated citations, silent
discarding of valid alternatives and undocumented accounting adjustments veto
acceptance regardless of an aggregate score.

\section{Evaluate the DSL against the strongest practical baseline}

The comparison uses the same IR, accounting examples and tasks. One group of
models is authored through the typed Python API; another through the DSL.
Both receive equivalent documentation and examples. Tasks include encoding a
movement schedule, adding an alternative interpretation, changing an effective
date and tracing a simulated amount. Measure correctness, material omissions,
time to a reviewed result, ease of explaining a change and maintenance effort.

This comparison tests whether the notation and compiler help users; it is not
a comparison between careful DSL code and unstructured spreadsheets. If the
DSL offers little advantage, retain the shared IR and library and narrow the
textual language. Small pilots nominate improvements. A claim of superiority
requires a predeclared comparison and uncertainty evidence, not a few favourable
demonstrations.

\section{Forecasting evaluation comes later}

The proposed experiment asks whether a conditional company method adds
out-of-time predictive information while preserving statement coherence and
unresolved exposure. The comparator ladder uses the same available sources and
targets: last-observation and seasonal naive forecasts; contractual runoff and
accounting-identity forecasts; tuned classical statistical forecasts; then the
plain structural model and declared extensions. Tuning stays within training
windows. Test issuers or time blocks remain untouched, and unavailable
predictions stay in the reported denominator.

For probabilities, predeclare proper scores, calibration, interval coverage,
sharpness and dependence-sensitive joint checks. Unweighted feasible sets have
coverage and width under a stated set interpretation, not probability intervals.
Promotion needs a declared score difference with uncertainty evidence on matched
eligible targets and no accounting or information-time veto. Issuer and time
dependence require a justified paired resampling or equivalent inference design;
overlapping reports are not independent replications. Runtime, a few losses and
small-seed tail differences remain descriptive without that support. No such
forecast experiment has been run for this proposal.

Look-ahead, broken conservation, a changed target or missing scope can invalidate
an experiment. A valid comparison in which the proposed predictor performs
poorly instead rejects that candidate and motivates its stated repair. The two
outcomes must not be conflated when choosing the next experiment.

Forecast evaluation uses historical information cutoffs, fixed data vintages,
declared economic scenarios and proper separation of training and testing
periods. Baselines should include a naive persistence or ratio model, a tuned
conventional financial model, the structural model with a single selected
interpretation, and the same model preserving alternatives. This identifies
whether any benefit comes from better economics, more information or the
representation of ambiguity.

Construct the inexpensive comparators before choosing a complex forecasting
method. A no-growth operating forecast with scheduled contractual financing
tests whether the model adds value beyond existing obligations. A constant
margin and turnover model tests whether detailed operations improve on familiar
financial ratios. A trailing-average growth model tests whether fitted dynamics
improve on recent experience. A fixed-exposure contractual stress model tests
whether estimated management responses help beyond repricing the existing
book. Each comparator must generate coherent accounts through the same reporting
rules and use the same historical information. In synthetic cases, the known
hidden state also supplies an oracle conditional on the stipulated scenario.

Evaluate these comparisons separately under stable conditions, large rate
resets, refinancing pressure, credit deterioration and changes in reporting
perimeter. A pooled average can conceal failure in the situation the product
is intended to explain. Supported underperformance against a cheap comparator
in a declared critical situation vetoes promotion of the complex forecasting
method and must lead the result discussion. These checks are falsification
tests, not training targets or evidence of superiority when merely passed.

Evaluate point forecasts where they are a stated target, distributional
calibration when probabilities are justified, and decision-relevant robustness
when only feasible sets are available. A wide feasible set is not automatically
a good prediction, and an unweighted set cannot be assessed as if it were a
95\% predictive interval. In multi-scenario stress tests, scenario severity and
probability remain separate inputs.

Any serious numerical comparison must follow the repository's research plan,
assumption audit, baseline, veto, uncertainty and result-record policies. The
present document runs only deterministic checks of its own examples. It
neither selects a scientific forecasting default nor reports comparative
performance.

\section{Capability contracts for sector packages}

\begin{longtable}{L{26mm}L{55mm}L{55mm}}
\toprule Package & Required state and operations & Minimum acceptance evidence\\\midrule\endhead
Core corporate & Working-capital bridges, lots/assets, ordinary debt and equity,
period closing and cash-flow mappings & Exact synthetic cases, reviewed public
filing reconstruction, all statement reconciliations.\\
Financial instruments & Terms, calendars, resets, options, measurement
categories, modifications and hedges & Contract schedule comparisons, valuation
checks, paragraph-based posting cases and transition cases.\\
Banking & Credit cohorts, deposits, collateral, liquidity, regulatory capital,
management actions & Allowance roll-forwards, repricing and runoff stresses,
capital reconciliation and default/funding-failure cases.\\
Insurance & Policy groups, future cash flows, service and finance components,
reinsurance and asset interaction & Cohort movement reconciliation, assumption
change cases, service recognition and reviewed actuarial calculations.\\
Multi-basis reporting & Versioned IFRS/US GAAP/ASBE rules, entity elections and
transition treatment & Matched economic-event cases with explained basis
differences and independent accounting review.\\\bottomrule
\end{longtable}

Every package declares capabilities at operation level. ``Supports bonds'' is
too vague; ``supports fixed-rate, single-currency, non-callable amortised-cost
issuance and redemption under this reviewed rule set'' is implementable and
testable. Unimplemented operations retain their source and contract
representation while producing an explicit capability error when execution
requires them.

\section{Implementation milestones and dependency order}

\begin{longtable}{L{16mm}L{76mm}L{44mm}}
\toprule Stage & Concrete implementation deliverable & Exit evidence\\\midrule\endhead
P0 & Evidence registry, contextual types, versioned IR and exact posting engine;
Python constructors for the running cases & T01--T04, T09 and T17; source
inspection and replay.\\
P1 & Finite choices, shared symbols, linear solver adapter, historical bridges,
conditional simulation and report explanations & T05--T10, T14 and T18;
synthetic family preserved.\\
P2 & Textual Core 0 frontend with identical IR; initial corporate package;
document/XBRL import adapters & Parser/API equivalence; T11--T13; reviewed
three-date public-company case.\\
P3 & Contract and valuation adapters, dated standard packages, richer financing
and tax/funding policies & Contract/valuation differential cases; accounting
review; T15 and transition cases.\\
P4 & Bank package, allowance models, regulatory reconciliation and management
response alternatives & T16; banking-specific reviewed histories and stresses.\\
P5 & Insurance cohort package, reinsurance and actuarial measurement adapters &
Reviewed cohort roll-forwards, information-date and service/finance tests.\\
P6 & Optional probabilistic inference, model-weight sensitivity and broader
scenario research & Explicit targets, sampler/numerical validity, prior
sensitivity and downstream evaluation.\\\bottomrule
\end{longtable}

These stages specify dependency order, not dates or staffing estimates.
Banking and insurance representation requirements influence P0 types, although
their measurement engines arrive later. Probability weighting is optional;
P1 already produces useful conditional cases and bounds. A failure of a chosen
extractor or inference algorithm triggers a local replacement or repair,
rather than abandoning the product's representation requirements.

\section{Decisions and replaceable assumptions}

The requirements fixed by this design are preservation of evidence and
alternatives, explicit time and basis, balanced and admissible posting, economic
state beyond journals, and distinct set/probability semantics. Replaceable
choices include the storage engines, parser generator, solver, numerical
libraries, aggregation resolution and user interface. Every scientifically
material aggregation, behavioural parameter, prior or truncation rule must
record provenance, purpose, failure mode and a diagnostic before it becomes a
default.

The immediate work is to finish and review the governing proposal, including
its real-source, authority, domain and research obligations. Product
implementation follows completion of that work and explicit implementation
authorization. The proposed dependency order begins with portable records,
review/time selection and durable receipts, then typed authoring, admitted
history templates and connected corporate methods. The implementation stages
below are a design sequence, not an already running product campaign.

\section{Concrete conformance and corpus protocol}

The fixture directory contains independently entered inputs and expected
outputs for Northstar, rounded borrowing, evidence views and sector cases.
\code{check\_repair\_conformance.py} recomputes exact journals and statements,
constructs the joint linear bridges in Z3, checks strict bounds, and exercises
replay, atomic rejection, finite Bayes updating and funding failure.
\code{check\_core\_contract.py} checks grammar/schema examples, canonical
identities, stable streams, information restrictions and source inventory.
These scripts are reference oracles for portions of the design. They do not
test an unimplemented full DSL compiler, all adapters or standards compliance.

Every conformance case must specify input files, the operation requested,
expected values or typed errors, comparison convention and supported scope.
Exact money, finite probabilities, linear witnesses and example journals
compare as rationals. Approximate valuations require an error bound or a
justified tolerance tied to the valuation scale. A missing expected result
cannot become a passing test simply because the operation returned something.
An implementation release must pass all applicable positive and negative
fixtures and preserve unresolved operations; the arithmetic oracle alone
does not release it.

The retained panel now contains all 192 target annual/interim reports for
2018--2025 across nine issuers and three evidenced accounting families, with
eight consecutive complete years per issuer. This is source acquisition, not
semantic closure or a representative random sample. The 244 retained original
versions include historical alternatives to the active panel. Apple remains
a detailed development package, with Caterpillar supplying a contrasting
inventory policy; bank, insurer, IFRS and ASBE reports are also retained.

Publication dates remain unverified for 136 of the 192 accepted reports; 56 have
filing-date metadata. A historical forecasting population needs the actual
byte-availability evidence described in Section~\ref{sec:time-admission},
not imputed publication dates. The 31 provisional annotations across four
reports are exposed development material, not heldout answers. Policies, note
links, incorporated documents, changed comparatives and adjudicated meanings
still require task-specific preparation. Synthetic revisions provide controlled
cases without substituting for a required real conflict. The corpus protocol
and active panel preserve their distinct populations and versions.

Annotators first record literal/context readings without seeing the model's
predictions, then mark source conflicts, mapping relationships, narrative
qualifications and admissible alternatives. A second accounting-aware reviewer
adjudicates material disagreements while preserving both initial annotations.
Reports from the same issuer family and duplicated tables cannot be split
between development and heldout evaluation. Forecast tests freeze the actual
publication cutoff; later revisions are separately labelled outcomes and may
not enter predictor inputs. Extractor upgrades rerun the same frozen corpus.

For the initial supported release, loss of a source span, wrong entity/unit/
period/basis, invented evidence, hidden financing, dropped feasible branch,
incorrect cash reconciliation or unreported unsupported treatment blocks
acceptance. All selected critical facts and operations must have exact
reviewed answers or the expected unresolved response. These zero-tolerance
conditions follow from the product's meaning-preservation requirements.
Non-critical extraction quality is reported by stratum and error category;
no arbitrary overall accuracy threshold certifies whole-report understanding.
An extraction benchmark needs its own sample size and uncertainty protocol
before making statistical accuracy claims.

The DSL and typed-library comparison uses identical packages, evidence,
schemas and runtime. Users perform the same tasks: correct a context, add a
shared uncertainty, represent a restatement, add a supported event and explain
a forecast difference. Task order is counterbalanced and experience recorded.
Both frontends receive the same validation and error messages. Measure
successful completion, material semantic errors, time and maintenance effort
with uncertainty appropriate to the participants; report no winner from the
current syntax checks. A textual language earns its maintenance cost only if
that comparison supports its use.

\section{Workload limits and release evidence}

The first integration workload is one local company package, up to 10,000
observations, 100 declared aggregate event slots per period, 64 materialised
finite-choice cells and a 30-second budget per solver operation. These are
provisional engineering limits for bounded failure behaviour, not measured
capacity or scientific defaults. They must be configurable and recorded.
Reaching a limit yields partial coverage with the unvisited formula/cells,
never an exhaustive-history claim. Peak memory and latency are measured only
after an implementation exists; a slower but semantically correct result
does not become a scientific failure.

Engineering release needs compiler/API equivalence, transactional replay and
adapter subset checks. Accounting release additionally needs paragraph-level
authority, dated applicability, exact fixtures and independent domain review
for every promoted operation. Forecast promotion additionally needs preserved
information sets, the stated baseline ladder, statistical uncertainty and
critical-regime vetoes. Human comprehension review remains separate from all
three. The present repair supplies a richer design candidate and reference
checks while preserving these outstanding acceptance decisions.


## FILE docs/design/proposal/manuscript/chapters/12-research.tex

\chapter{Research basis and outstanding review}
\label{app:research}

\section{Source collection and reading scope}

The companion library contains 32 verified paper PDFs: 25 retrieved from
external sources and seven preserved copies from the original collection.
Filenames use the title, first author's surname and year. Publication years
are used where an archived working version underlies a later publication;
the catalogue identifies the actual version read. The original collection
has not been renamed or modified. Standards pages, contract specifications,
software source snapshots and metadata are stored separately from papers.

The survey considered accounting algebra and DSLs, corporate and bank
simulation, incomplete and temporal databases, provenance, inverse problems,
partial identification, model averaging, causal scenarios, contract languages,
probabilistic programming, document extraction and financial reasoning.
OpenAlex and Crossref supplied dated metadata, while primary publisher,
institutional and author copies supplied technical support. Public-index
results were checked against the downloaded title pages; HTTP success alone
was not accepted as a valid paper download.

Technical reading was targeted to the mechanisms used in this design.
The full PDF is archived even where only specified sections support the
argument. No claim is made that every theorem, appendix or empirical result
in every archived paper was independently replicated. Representative support
anchors are listed below; the source-support ledger contains the per-source
scope and qualifications.

\begin{longtable}{L{33mm}L{57mm}L{46mm}}
\toprule Source & Inspected technical support & Design use\\\midrule\endhead
Nehmer and Robinson & Sections 2--5: account states, transactions and aggregation &
Conservation plus admissibility.\\
Doshi & Chapters 4, 7--9 of the 2024 thesis & Dates, logs, corrections and DSL scope.\\
Shahnazarian & Sections 2.3--2.8; relevant Chapter 3 equations; data and evaluation
sections; Appendix B & Accounting/behaviour separation; limits of data transfer.\\
Pierson & Sections 3--4 and reporting structures; supplementary Vensim equations &
Accrual/payment bridges and reporting accumulators.\\
Libkin & Sections 2--5: incomplete states, conditions and certain answers &
Shared unknowns and joint alternatives.\\
Green et al. & Definitions 3.1--3.2; Section 4 & Composable relational provenance;
limits outside positive operations.\\
Stuart & Section 2.2, observation equation and prior/regularisation discussion &
Inverse-problem formulation, not imported convergence guarantees.\\
Giacomini and Kitagawa & Sections 2.1--2.6 and Theorem 1 in CWP12/20 &
Prior sensitivity and classes of posterior beliefs.\\
Hoeting et al. & Equations (1)--(3); prior and predictive-evaluation discussion &
Optional model-weighted predictions.\\
Merigoux et al. & Sections 3--4, default calculus and translation figures &
Scopes, exceptions, empty/conflict outcomes.\\
Peyton Jones et al. & Sections 3--5, combinators and valuation semantics &
Contract composition separate from valuation assumptions.\\
FinQA / TAT-QA & Dataset operations, annotation, model and evaluation sections;
FinQA evaluation source & Evidence-linked local arithmetic; benchmark boundaries.\\
DocFinQA / FinBen & Context/retrieval and financial-task evaluations &
Long-document difficulty and task coverage.\\
PubTables / GTE & Canonicalisation, dataset construction, methods and evaluation &
Table structure and financial-domain extraction.\\
Cosentino et al. & Sections 3.1--3.2, 4.6 and 5 & Persistent RAG provenance;
scope of auditability evidence.\\\bottomrule
\end{longtable}

\section{Version and access qualifications}

Several discrepancies mattered. Doshi's thesis is dated 2024 despite the
original filename. The archived Mernik text is the 2003 CWI report underlying
the 2005 article. Giacomini and Kitagawa's copy is the April 2020 working paper
underlying the 2021 article. The Docling v5 copy lists Auer as first author.
The probabilistic-programming tutorial is an arXiv version revised in 2021,
first submitted in 2018; a merged index DOI was not used. The Libkin author
PDF has a footer DOI that resolves to another paper; title/author metadata
from the indexes resolves the cited work to DOI
\code{10.1145/2594538.2594561}. These discrepancies remain documented rather
than being hidden by a cleaned bibliography.

McCarthy (1982), Imieliński and Lipski (1984), Tamer (2010), and Caiani and
co-authors (2016) are retained as important blocked candidates. Access failures
and rejected wrong-content downloads are recorded. The design does not use
their uninspected technical claims. More specialised work on accounting
measurement, process mining, multi-company equilibrium, actuarial inference
and learned forecasting is recorded as expansion work for the corresponding
implementation stage. The survey supports the core architecture without
pretending that those later modules have a complete literature or rule base.

OpenAlex retraction flags and available Crossref correction/version relations
were inspected alongside local versions. No reviewed source was excluded for
a discovered retraction. Missing correction metadata is marked unavailable;
absence of a discovered notice does not certify that no notice exists.
Citation counts are dated index metadata, and venue rankings were not available
in this campaign. Neither is used as evidence of correctness.

\section{Companion records and status}

The six research ledgers are \code{source-support.json},
\code{citation-venue.json}, \code{backward-snowball.json},
\code{forward-snowball.json}, \code{claim-support.json}, and
\code{omissions.json}. They record technical anchors, metadata sources,
considered leads, omitted or blocked candidates and the distinction between
source claims and this document's derivations. Citation leads with checked
seed references are distinguished from cross-survey additions and topic
expansion leads. Forward searches retain the most-cited and most-recent
results returned by the recorded bounded queries; they do not establish
exhaustive citation coverage. The separate \code{tools.json}
records software evidence. Raw retrievals and text extracts permit a later
reviewer to revisit the decisions.

The repair adds Mack's reserving paper, with its conditional-mean/variance
assumptions, proofs, aggregate-error dependence and numerical comparisons
inspected. It also archives official AASB texts incorporating IAS~2, IAS~32
and IFRS~17, distinguishing their Australian additions and applicable editions.
The corporate filings are evidence of reported amounts and policies, rather
than substitutes for every underlying standard. The ASBE~1 reproduction has
not been verified against an accessible official current text, and official
FASB/ASC access remains incomplete. These limitations are recorded at the
specific operations they affect.

Every one of the 179 unique candidates in the acquired forward-query files
now has an individual title/metadata relevance decision. This includes
previously omitted discovery files associated with inaccessible seed papers.
The generation script requires an explicit decision and stops on an unseen
candidate. Screening is still distinct from technical reading: deferred
provenance, temporal-query, bank-optimisation, extraction and actuarial
follow-ups remain identified expansion risks. An omitted-paper reason does
not make that paper technically reviewed or make the survey exhaustive.

This document specifies the product; it does not report a completed engine.
The companion review records cover deterministic example arithmetic,
bibliography/build checks, rendered-page inspection and author review. Human
comprehension review, independent accounting review and implementation
conformance remain separate future evidence. They are not replaced by a clean
LaTeX build or by the quantity of literature collected.
