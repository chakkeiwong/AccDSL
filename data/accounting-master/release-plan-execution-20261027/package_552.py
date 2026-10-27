from pathlib import Path
import hashlib,json,platform,sys
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;T=R/'docs/design/proposal/manuscript-release-prep-v552r1-20261027'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
readme=T/'README.md';s=readme.read_text().replace('protected 5.51 directory','protected 5.52 directory');s += '''
Package verification (no third-party Python dependency):

    python3 -I -B verify_package.py

package-manifest.json lists the included sources, normative companions, fixtures,
component files and two built PDFs. It excludes generated caches and TeX
intermediates. Its identity is fixed in the external execution record; a hash
manifest proves integrity relative to that record, not authenticity by itself.
Source relocation was checked page by page against the included PDFs. TeX/font
installation files are recorded separately, not included or installed here.
DEPENDENCIES.md distinguishes the reproducible subset from remaining evidence
and distribution work. This package is for internal review; no licence grant
or public redistribution clearance is inferred.
''';readme.write_text(s)
(T/'DEPENDENCIES.md').write_text('''# Included dependencies and remaining release closure

The two document roots use local chapter, section, simulation, bibliography and
grammar files. Fresh builds use the recorded TeX Live 2026, LuaHBTeX 1.24.0,
latexmk 4.88 and BibTeX 0.99e environment. Build-environment.json records the
actual commands. Absolute cache directories are local to each copied package.
The external execution record retains hashes of every observed TeX/font input.
This establishes reproduction on the retained system toolchain, not a clean
installation on every operating system or byte-identical PDF metadata.

companions/historical-core0 and companions/selected-term contain exact copies
of the independently relocated bounded components. Their bundle manifests
record Python and installed-distribution versions. The modern component's
audit hook precedes project imports; the historical component installs its
hook later. These are dependency diagnostics, not security sandboxes.
The historical command requires an explicit output path inside its bundle when
called from another working directory. Use new output names.

The manuscript refers to additional repository evidence under data/, docs/ and
scripts/. Those references are not all bundled. The 201 failure targets, full
real-company source network, accounting authority and literature reading records
remain required external repository evidence. Exact routes are in the current
release execution index; complete transitive evidence closure is outstanding.
Do not infer that two runnable components reproduce all manuscript results.

No retained paper, accounting standard, issuer source archive, credential or
external service is copied into this package. Source-access and redistribution
dispositions for a recipient remain open. Local inspection and source identity
do not grant rights. No publication or external transmission is performed.
''')
verifier='''from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parent
manifest=json.loads((root/'package-manifest.json').read_text())
seen=set();bad=[]
for row in manifest['files']:
 rel=Path(row['path'])
 if rel.is_absolute() or '..' in rel.parts or row['path'] in seen:
  bad.append({'path':str(rel),'error':'invalid_or_duplicate_path'});continue
 seen.add(row['path']);p=root/rel
 if not p.is_file() or any((root/Path(*rel.parts[:i])).is_symlink() for i in range(1,len(rel.parts)+1)):
  bad.append({'path':str(rel),'error':'missing_or_symlink'});continue
 if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256'] or p.stat().st_size!=row['bytes']:
  bad.append({'path':str(rel),'error':'content_mismatch'})
print(json.dumps({'pass':not bad,'checked_files':len(seen),'failures':bad,'scope':'Declared package bytes only; external manifest trust, source validity and release acceptance are separate.'}))
sys.exit(1 if bad else 0)
'''
(T/'verify_package.py').write_text(verifier)
files=[];omitted=[]
for p in sorted(T.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(T)
 if any(x.startswith('.') or x.startswith('output-') or x=='__pycache__' for x in rel.parts) or p.suffix in {'.aux','.log','.fls','.fdb_latexmk','.toc','.bbl','.blg','.pyc'} or rel.name=='package-manifest.json':
  omitted.append(str(rel));continue
 assert not p.is_symlink()
 role='component' if rel.parts[0]=='companions' else 'pdf' if p.suffix=='.pdf' else 'manuscript_source' if p.suffix in {'.tex','.bib','.lark'} else 'package_reference'
 files.append({'path':str(rel),'sha256':sha(p),'bytes':p.stat().st_size,'role':role,'redistribution':'unreviewed_internal_only'})
m={'profile':'AccDSLReleasePreparationBundle/1','candidate':'5.52-R1;not_ready','date':'2026-10-27','files':files,'excluded_patterns':['.* cache directories','output-*','__pycache__','.aux','.log','.fls','.fdb_latexmk','.toc','.bbl','.blg','.pyc'],'manifest_self_hash':'Stored outside this package in release-plan-execution-20261027/v552r1/package-record.json','full_evidence_closure':False,'external_dependencies':'DEPENDENCIES.md','rights':'Internal preparation only; no public redistribution clearance','acceptance':'No broad requirement, product or empirical promotion'}
(T/'package-manifest.json').write_text(json.dumps(m,indent=2)+chr(10))
record={'path':str(T.relative_to(R)),'manifest_sha256':sha(T/'package-manifest.json'),'files':len(files),'bytes':sum(x['bytes'] for x in files),'excluded_file_count':len(omitted),'python':sys.version,'platform':platform.platform(),'inputs':{'main_pdf':sha(T/'accounting-product-proposal.pdf'),'simulation_pdf':sha(T/'simulation-foundations.pdf')},'limitations':m['rights']+'; full evidence closure remains open'}
(H/'v552r1/package-record.json').write_text(json.dumps(record,indent=2)+chr(10));print(json.dumps(record,indent=2))
