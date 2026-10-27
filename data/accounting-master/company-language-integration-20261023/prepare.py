"""One-time protected manuscript successor preparation."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'docs/design/proposal/manuscript-company-authoring-20261023'
TARGET=ROOT/'docs/design/proposal/manuscript-company-language-20261023'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not TARGET.exists(),'successor already prepared'
 assert sha(SOURCE/'accounting-product-proposal.pdf')=='5bf364ae6c78bddcf833331d408c447ddd5f540aba1e47d4d28bc7e648c09893'
 hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
 baseline={'source_root':str(SOURCE.relative_to(ROOT)),'candidate_root':str(TARGET.relative_to(ROOT)),'source_hashes':hashes,'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')}
 (HERE/'baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
 confusion=[{'anchor':'Version 3.53 PDF page 98, language scope','finding':'Opening accurately stages debt to company path, but the broad expression/branching residual omits the newly checked bounded increments.','repair':'Name authored scenario families and pure policy expressions precisely, retaining general-language residuals.'},
 {'anchor':'PDF page 380, end of company path authoring','finding':'Reader moves directly from path information dates to another group profile; there is no explanation of joint authored scenarios, policy-expression dates or interrupted family work.','repair':'Insert one consecutive Northstar section before group composition, motivated by comparing the 90-percent rule and a slower-collection alternative.'},
 {'anchor':'PDF page 381, group continuation','finding':'Group method uses distinct companies and its own assumptions; new family prose must not imply these are Northstar branches.','repair':'Keep group section unchanged and retain a clear transition to its separate profile.'}]
 (HERE/'confusion-map.json').write_text(json.dumps({'baseline_pages_inspected':[97,98,380,381],'scope':'Bounded visual and boundary diagnosis, not whole-document reading','findings':confusion},indent=2)+'\n')
 for name in hashes:
  dest=TARGET/name; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes((SOURCE/name).read_bytes())
 replacements={
 'accounting-product-proposal.tex': [('Version 3.53 (proposal candidate)','Version 3.54 (proposal candidate)')],
 'chapters/06-language.tex': [('including named settlement allocations and incomplete paths. General policy\nexpressions, branching and broader accounting profiles remain language tasks.',
 'including named settlement allocations and incomplete paths.\nSection~\\ref{sec:company-family-language} adds named unweighted scenarios and\npure typed expressions for the declared collection policy. General functions,\nendogenous decisions, source admission and broader accounting profiles remain\nlanguage tasks.')],
 'chapters/07-execution.tex': [('explicit rule that regenerates it after a price change.',
 'explicit rule that regenerates it after a price change.\nSection~\\ref{sec:company-family-language} retains those outcomes together,\nthen distinguishes a partial financial year from suspended computation and\nchecks member-boundary recovery with exact retries.')],
 'sections/company-path-authoring.tex': [('branching, policy syntax and wider accounting profiles remain separate language\nrequirements.',
 'endogenous branching and wider accounting profiles remain separate language\nrequirements. The following extension supplies a bounded family wrapper and\npure expressions for the declared collection policy.'),
 ('evidence remain necessary for whole-company coverage. The following group\nprofile addresses composition and component migration under its own assumptions.',
 'evidence remain necessary for whole-company coverage. The next section keeps\nseveral authored choices together and makes their calculation recoverable.\n\n\\input{sections/company-family-language}\n\nThe following group profile addresses composition and component migration\nunder its own assumptions.')]
 }
 for name,pairs in replacements.items():
  p=TARGET/name; text=p.read_text()
  for old,new in pairs:
   assert text.count(old)==1,(name,old)
   text=text.replace(old,new)
  p.write_text(text)
 print(json.dumps({'source_count':len(hashes),'candidate':str(TARGET.relative_to(ROOT)),'baseline_unchanged':all(sha(SOURCE/n)==h for n,h in hashes.items())}))
if __name__=='__main__': main()
