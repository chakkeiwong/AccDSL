"""Create a protected successor for native conditional sequences."""
from hashlib import sha256
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-typed-attachment-20261024'
TARGET=ROOT/'docs/design/proposal/manuscript-native-sequence-20261024'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def main():
    assert not TARGET.exists(),'successor already exists'
    assert sha(SOURCE/'accounting-product-proposal.pdf')=='aeaf1edc2a0cbcb176ad52e89850b7e5d43f41d3a0e45aca2b9d3ba0c6a46006'
    edits={
      'accounting-product-proposal.tex':[('Version 3.68 (proposal candidate)','Version 3.69 (proposal candidate)')],
      'chapters/06-language.tex':[('amounts to selected method prerequisites without choosing a single history.',
       'amounts to selected method prerequisites without choosing a single history.\nSection~\\ref{sec:native-conditional-sequence} carries every retained return\nbranch through settlement and sale, preserving funding and intermediate observations.')],
      'sections/conditional-method-families.tex':[(
       'The intersection strengthens a\nconditional method family without selecting one history. Applying such methods\nthrough a complete economic history, recovering actual legal and operational\nstate, admitting source interpretations, integer lots and broader nonlinear\nmethods remain substantive simulator work.',
       'The intersection strengthens a\nconditional method family without selecting one history. The next section\nconnects this method to one fixed complete opening and an ordered settlement\nand sale. General economic histories, actual legal and operational state,\nsource interpretation admission, integer lots and broader nonlinear methods\nremain substantive simulator work.\n\n\\input{sections/native-conditional-sequence}')]}
    changed={}
    for name,pairs in edits.items():
        value=(SOURCE/name).read_text()
        for old,new in pairs:
            old=old.replace('\\n','\n');new=new.replace('\\n','\n').replace('\\\\','\\')
            assert value.count(old)==1,(name,old)
            value=value.replace(old,new)
        changed[name]=value
    hashes={str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.rglob('*')
            if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    (HERE/'baseline.json').write_text(json.dumps({'source_root':str(SOURCE.relative_to(ROOT)),
       'candidate_root':str(TARGET.relative_to(ROOT)),'source_hashes':hashes,
       'pdf_sha256':sha(SOURCE/'accounting-product-proposal.pdf')},indent=2)+'\n')
    for name in hashes:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((SOURCE/name).read_bytes())
    for name,value in changed.items():(TARGET/name).write_text(value)
    print(json.dumps({'protected_sources':len(hashes),'changed_files':list(changed)}))
if __name__=='__main__':main()
