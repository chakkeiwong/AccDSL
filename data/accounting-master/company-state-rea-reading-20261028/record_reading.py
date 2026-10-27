"""Record primary reading and bounded metadata; preserve prior survey ledgers."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
LEDGERS=ROOT/'docs/design/research/company-state-program-20261028'
NOTE='docs/design/research/company-state-program-20261028/rea-state-relationships.md'
SOURCE='data/accounting-master/simulation-literature-gaps-20261026/sources/mccarthy1982-author.pdf'
BACKWARD=[
 ('Chen1976, The Entity-Relationship Model—Toward a Unified View of Data','FOUNDATIONAL','Primary relationship and entity semantics; inspect technical model'),
 ('Chen1978, Applications of the Entity-Relationship Model','DIRECT_METHOD','View modeling and practical attribute specification; inspect next'),
 ('Ijiri1975, Theory of Accounting Measurement','FOUNDATIONAL','Resource/control and duality assumptions; inspect primary sections cited by McCarthy'),
 ('Mattessich1964, Accounting and Analytical Methods','FOUNDATIONAL','Alternative accounting formalization and duality; compare target scope'),
 ('Sorter1969, An Events Approach to Basic Accounting Theory','FOUNDATIONAL','Events accounting precursor; inspect underlying argument'),
 ('McCarthy1979, An Entity-Relationship View of Accounting Models','DIRECT_METHOD','Predecessor operational model and role declarations; inspect method'),
 ('McCarthy1980, Construction and Use of Integrated Accounting Systems with Entity-Relationship Modeling','DIRECT_METHOD','Operational design predecessor; inspect example'),
 ('McCarthy and Gal1981, Declarative and Procedural Features of a CODASYL Accounting System','IMPLEMENTATION_OR_SOFTWARE','Source points to a simple implemented enterprise; inspect before claiming reusable implementation'),
 ('Benbasat and Dexter1979, Value and Events Approaches to Accounting: An Experimental Evaluation','EMPIRICAL_EXAMPLE','Direct user-evaluation comparator; inspect design/results before any REA superiority claim'),
 ('Everest and Weber1977, A Relational Approach to Accounting Models','COMPETITOR','Alternative relational accounting model; inspect constraints and view semantics'),
 ('Haseman and Whinston1976, Design of a Multi-dimensional Accounting System','COMPETITOR','Alternative accounting representation; inspect technical scope'),
 ('Lieberman and Whinston1975, A Structuring of an Events-Accounting Information System','COMPETITOR','Events-accounting hierarchy; inspect technical structure'),
 ('Smith and Smith1977a/1977b, Database Abstractions: Aggregation / Aggregation and Generalization','FOUNDATIONAL','Generalization and aggregation machinery; two distinct papers, inspect separately before adoption'),
 ('Bubenko1977, The Temporal Dimension in Information Modeling','DIRECT_METHOD','Temporal materialization source; inspect exact event/time assumptions'),
 ('Wong and Mylopoulos1977, Two Views of Data Semantics','SURVEY_OR_TUTORIAL','Declarative/procedural distinction; orientation only until primary claims checked'),
 ('Weber1977, Implications of Data Base Management Systems for Auditing Research','BACKGROUND','Audit-evidence lead; no empirical or standards conclusion from citation'),
 ('Yu1976, The Structure of Accounting Theory','FOUNDATIONAL','Economic-event and periodicity arguments; inspect primary text'),
 ('Lum et al1979, New Orleans Data Base Design Workshop Report; Teorey and Fry1980, The Logical Record Access Approach to Database Design','BACKGROUND','Requirements/view integration background; defer detailed database implementation until needed'),
]


def main():
    names=['source-support.json','citation-venue.json','backward-snowball.json','forward-snowball.json','claim-support.json','omitted-paper-risk.json']
    backup=HERE/'ledgers-before';backup.mkdir(exist_ok=False)
    for n in names:shutil.copy2(LEDGERS/n,backup/n)
    loaded={n:json.loads((LEDGERS/n).read_text()) for n in names}
    crossref=json.loads((HERE/'crossref.json').read_text())['message']
    openalex=json.loads((HERE/'openalex.json').read_text())
    assert crossref['DOI'].lower()=='10.2308/tar-4487748'
    assert crossref['page']=='554-578' and crossref['volume']=='57' and crossref['issue']=='3'
    assert sha256((ROOT/SOURCE).read_bytes()).hexdigest()=='cb311ffc132154d59d9fc578f333711c8cb79a53dd309e5417540040691b6ce0'
    row=next(r for r in loaded['source-support.json']['sources'] if r['id']=='I-S1')
    row.setdefault('previous_scope',dict(inspected=row['inspected'],scope=row['scope']))
    row.update(title='McCarthy1982, The REA Accounting Model',doi='10.2308/tar-4487748',
        inspected='All25 scan pages/printed554–578 visually read, including Figures1–10, footnotes and complete references; technical design sections and qualifications examined.',
        scope='Conceptual schema, resource/event/agent relationships, procedural materialization and reported accounting interpretations; no general simulator or inference theorem.',
        allowed_claims='Explicit stock-flow/duality/control/responsibility roles; user-driven view integration; resource/claim choices; distinction between immediate/periodic updates and derived views; qualified temporal aggregation; declared implementation limits.',
        forbidden_claims='Automatic reconstruction from statements, behavioral simulation, complete company state, current accounting-standard validity, proven sufficiency of aggregation or empirical superiority.',
        publication_integrity='Crossref publication identity/page span matches scan; no update-to/updated-by relation; OpenAlex is_retracted=false; eight-result correction query reveals no relevant notice. Bounded checks, not exhaustive integrity certification.',
        official_code='No software artifact imported. Article identifies McCarthy/Gal1981 implementation lead; original implementation not inspected, so no software or performance adoption.',
        next_action='Inspect later policy/commitment REA and direct database/user-evaluation competitors; implement relationship dependencies separately from numeric state.',
        continuation_note=NOTE,reading_status='full primary article visually inspected')
    row=next(r for r in loaded['citation-venue.json']['rows'] if r['id']=='I-S1')
    row.update(citation_count=openalex['cited_by_count'],citation_source='OpenAlex W7136181339; raw current response retained',
        access_date='2026-10-28',venue='The Accounting Review57(3),554–578',
        note='This record reports13 citations and lacks older direct extensions in its bounded forward sample; possible record fragmentation. Not a reliable total impact count or coverage measure. Venue ranking not retrieved.')
    back=loaded['backward-snowball.json']['rows']
    for candidate,classification,action in BACKWARD:
        if any(r.get('seed')=='I-S1' and r.get('candidate')==candidate for r in back):continue
        back.append(dict(seed='I-S1',anchor='printed555–576; references577–578',candidate=candidate,
            classification=classification,action=action,reason='Relevant to explicit REA construction, alternative representations, temporal semantics or validation',status='lead_not_technical_support'))
    forward=loaded['forward-snowball.json']['rows']
    seen=set();screen=[]
    for name,order in [('forward-cited.json','cited_by_count:desc'),('forward-recent.json','publication_date:desc')]:
        raw=json.loads((HERE/name).read_text())
        for r in raw['results']:
            if r['id'] in seen:continue
            seen.add(r['id'])
            title=r['title'];lower=title.lower()
            if 'convergence' in lower or 'transformation of business' in lower or 'ontology as distributed' in lower:
                classification='COMPETITOR';action='inspect technical representation and interoperability; no claims adopted'
            elif 'duality' in lower:
                classification='DIRECT_METHOD';action='inspect duality definitions; ledger transparency is not company-state completeness'
            else:
                classification='BACKGROUND';action='defer until full-text relevance to state construction is established; no empirical claim adopted'
            entry=dict(seed='I-S1',source_file=str((HERE/name).relative_to(ROOT)),query_order=order,
                openalex_id=r['id'],title=title,date=r['publication_date'],citation_count=r['cited_by_count'],doi=r.get('doi'),
                classification=classification,disposition=action,screening_level='title/metadata only',version_status='not checked')
            screen.append(entry)
            if not any(x.get('seed')=='I-S1' and x.get('openalex_id')==r['id'] for x in forward):forward.append(entry)
    claims=loaded['claim-support.json']['rows']
    additions=[
        dict(id='REA-RELATIONSHIPS',claim='REA represents resource/event/agent relationships and separate procedural views; it is a conceptual construction method, not an inverse estimator.',support_class='PRIMARY_TECHNICAL_SUPPORT',anchor='McCarthy1982 pp556–566,Figures2–6',limits='No behavioral model, recovery theorem or current standards claim.'),
        dict(id='REA-PROCEDURES',claim='Immediate/periodic updates and views/derivations have different effects; periodic accounting choices remain unresolved by the framework itself.',support_class='PRIMARY_TECHNICAL_SUPPORT',anchor='McCarthy1982 pp567–574,Figures7–10',limits='No proof that any storage summary preserves all requested queries.'),
        dict(id='REA-LOCAL-DEPENDENCIES',claim='AccDSL needs relation/role/procedure dependencies in addition to numeric dependency closure; actual-source totals cannot identify missing counterparties or legal contracts.',support_class='PROJECT_DERIVATION',anchor=NOTE,limits='Design consequence; not yet a completed general relationship constructor.')]
    for row in additions:
        if not any(x['id']==row['id'] for x in claims):claims.append(row)
    risks=loaded['omitted-paper-risk.json']['rows']
    additions=[
        dict(id='OR-REA-EXTENSIONS',candidate='Geerts/McCarthy policy-level specifications2006; extended REA ontology/commitments; McCarthy/Geerts/Gal2019 monograph',reason='The1982 primary article predates explicit policy and commitment extensions; current design cannot claim coverage from that article alone.',disposition='requires technical comparison; author-hosted leads retained',task='S01',acceptable_for_final_survey=False),
        dict(id='OR-REA-EMPIRICAL',candidate='Benbasat/Dexter1979 and competing relational/hierarchical accounting models',reason='Source calls for user validation; no relative advantage is established by the conceptual paper or local exact checks.',disposition='requires primary design/result reading',task='S01',acceptable_for_final_survey=False),
        dict(id='OR-REA-INDEX',candidate='Older REA citing works omitted from OpenAlex W7136181339 forward sample',reason='Thirteen-citation record and seven unique bounded leads do not include known older author-page extensions; duplicate/index linkage unresolved.',disposition='reconcile alternate records and author bibliography; not complete forward coverage',task='S01',acceptable_for_final_survey=False)]
    for row in additions:
        if not any(x['id']==row['id'] for x in risks):risks.append(row)
    for n,d in loaded.items():(LEDGERS/n).write_text(json.dumps(d,indent=2)+chr(10))
    source=json.loads((HERE/'source.json').read_text());source['rendered']=list(range(1,26));source['visually_inspected']=list(range(1,26))
    source['print_page_rule']='physical+553';source['full_text_reading']='All pages, method, discussion, footnotes and references; no separate appendix.'
    (HERE/'source.json').write_text(json.dumps(source,indent=2)+chr(10))
    queries=[('crossref.json','https://api.crossref.org/works/10.2308%2Ftar-4487748'),
        ('openalex.json','https://api.openalex.org/works/https://doi.org/10.2308/tar-4487748'),
        ('corrections-query.json','https://api.crossref.org/works?query.title=The%20REA%20Accounting%20Model%20correction%20erratum&query.author=McCarthy&rows=8'),
        ('forward-cited.json','https://api.openalex.org/works?filter=cites:W7136181339&sort=cited_by_count:desc&per-page=5'),
        ('forward-recent.json','https://api.openalex.org/works?filter=cites:W7136181339&sort=publication_date:desc&per-page=5')]
    (HERE/'query-log.json').write_text(json.dumps(dict(date='2026-10-28',responses=[dict(file=n,url=u,http_status=200,sha256=sha256((HERE/n).read_bytes()).hexdigest()) for n,u in queries],web_calls='Two searches and one open returned empty tool bodies; not negative evidence.'),indent=2)+chr(10))
    (HERE/'forward-screen.json').write_text(json.dumps(screen,indent=2)+chr(10))
    paths=[ROOT/SOURCE,ROOT/NOTE,ROOT/'docs/plans/company-state-rea-reading-20261028.md',Path(__file__),*(HERE/n for n,u in queries)]
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],environment=sys.version,cpu_gpu='CPU-only Poppler rendering and manual primary reading; no accelerator imports',
        random_seeds='N/A documentary reading',wall_time='Manual reading; no benchmark timing claim',plan_file='docs/plans/company-state-rea-reading-20261028.md',
        result_file=str((HERE/'result.md').relative_to(ROOT)),utc=datetime.now(timezone.utc).isoformat(),
        source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths},
        ledger_changes={n:dict(before=sha256((backup/n).read_bytes()).hexdigest(),after=sha256((LEDGERS/n).read_bytes()).hexdigest()) for n in names})
    (HERE/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+chr(10))
    print(json.dumps(dict(pages_read=25,backward_leads_added=len(BACKWARD),unique_forward_screened=len(screen),claim_records_added=len(additions),ledgers_updated=len(names))))


if __name__=='__main__':main()
