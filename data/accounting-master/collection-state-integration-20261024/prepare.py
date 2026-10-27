"""Protect the predecessor and copy only sources for a bounded successor."""
from hashlib import sha256
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-requirement-successors-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-collection-state-20261024'
def sha(p): return sha256(p.read_bytes()).hexdigest()
def main():
    assert not TARGET.exists(),'candidate exists'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='20d5b624c20fdd956a7ce5c1fd62b04df4ab0cb9cdd29f77779217573c5b5102'
    edits={'accounting-product-proposal.tex': [('Version 3.60 (proposal candidate)', 'Version 3.61 (proposal candidate)')], 'chapters/06-language.tex': [('dimensional products and guarded applicability, with explicit version selection.', 'dimensional products and guarded applicability, with explicit version selection.\nSection~\\ref{sec:collection-state-requirements} adds explicit collection coverage,\nidentity order, signed totals and state-domain findings before monetary effects.')], 'chapters/17-portable-reference.tex': [('\\input{sections/requirement-successors}', '\\input{sections/requirement-successors}\n\n\\input{sections/collection-state-requirements}')], 'sections/requirement-successors.tex': [('Collection membership and reference order,\nshared-book invariants, state effects, replay and reporting still need their\nown complete method semantics. Selected requirements can explain why an input\nis usable or why work must wait; they do not authorize the omitted transitions.', 'Collection membership, identity order and selected shared-book conditions are\nmade explicit in the following section. State effects, replay and reporting\nstill require complete method semantics. Selected requirements can explain why\nan input is usable or why work must wait; they do not authorize those transitions.')]}
    changed={}
    for name,pairs in edits.items():
        content=(SOURCE/name).read_text()
        for old,new in pairs:
            assert content.count(old)==1,(name,old)
            content=content.replace(old,new)
        changed[name]=content
    hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*')
            if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    (HERE/'baseline.json').write_text(json.dumps({'source_root':str(SOURCE.relative_to(ROOT)),
        'candidate_root':str(TARGET.relative_to(ROOT)),'source_hashes':hashes,
        'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')},indent=2)+'\n')
    for name in hashes:
        target=TARGET/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((SOURCE/name).read_bytes())
    for name,content in changed.items():
        (TARGET/name).write_text(content)
    print(json.dumps({'protected_sources':len(hashes),'changed_files':list(changed)}))
if __name__=='__main__': main()
