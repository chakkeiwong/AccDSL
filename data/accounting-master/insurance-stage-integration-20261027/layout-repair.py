from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;R=H.parents[2]
lock=json.loads((H/'source-preservation.json').read_text());T=R/lock['target']
out=H/'layout-repair';out.mkdir(exist_ok=False)
names=['insurance-stage.tex','integrate.py']
for n in names:(out/n).write_bytes((H/n).read_bytes())
(out/'source-preservation.json').write_bytes((H/'source-preservation.json').read_bytes())
old=(H/'insurance-stage.tex').read_text()
new=old.replace('\\section{Separate issued and held results before choosing a calendar}',
                '\\clearpage\n\\section{Issued and held results before dated reporting}')
assert new!=old
(H/'insurance-stage.tex').write_text(new);(T/'simulation/insurance-stage.tex').write_text(new)
lock['added']['simulation/insurance-stage.tex']=sha256(new.encode()).hexdigest()
lock['integration_inputs']['insurance-stage.tex']=sha256(new.encode()).hexdigest()
(H/'source-preservation-v2.json').write_text(json.dumps(lock,indent=2)+'\n')
s=(H/'integrate.py').read_text()
s=s.replace("assert not (H/'verification.json').exists();lock=json.loads((H/'source-preservation.json').read_text());checks=[];docs=[]",
            "assert sys.argv[2]=='02' and not (H/'verification-02.json').exists();lock=json.loads((H/'source-preservation-v2.json').read_text());checks=[];docs=[]")
s=s.replace("H/('render-'+name)","H/('render-02-'+name)")
s=s.replace("name+'-additions.txt'","name+'-additions-02.txt'")
s=s.replace("save('document-checks.json'","save('document-checks-02.json'")
s=s.replace("save('verification.json'","save('verification-02.json'")
(H/'integrate-layout.py').write_text(s)
(out/'reason.md').write_text('Build 01 was mathematically intact but split the long heading and opening example across pages. Shorten only the heading and start the section on a fresh page; retain every equation, sentence and source limit. Preserve first-build checks. Build/verify 02 uses the explicit successor preservation manifest.\n')
print('Prepared focused layout repair; original build and verification preserved')
