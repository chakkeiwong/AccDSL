from pathlib import Path
from hashlib import sha256
import json,shutil
import integrate as i
HERE=i.HERE;archive=HERE/'attempt-01'
assert not archive.exists()
verification=i.read(HERE/'verification.json')
assert verification['pdf_sha256']=='1a37cc338d388f20f19c5fa4099d332bbe4ebbc0d0c71a89f7a89ecb4c8c07f5'
assert len(verification['new_warnings'])==2
source=HERE/'nested-term-invariants.tex';old=source.read_text();new=old
before='Event membership uses the existing collection-reference evaluator through'+chr(10)+i.BS+'code{ProjectedStateCollections/1}. It binds complete term rows and the book\'s'
after='Event membership uses '+i.BS+'code{ProjectedStateCollections/1} to connect nested'+chr(10)+'rows to the existing collection-reference evaluator. It binds complete term'+chr(10)+'rows and the book\'s'
assert new.count(before)==1;new=new.replace(before,after)
before='Join the semantic checks and preserve the admission boundary.'
assert new.count(before)==1;new=new.replace(before,'Join the six semantic checks.')
assert (i.TARGET/i.NEW).read_text()==old
archive.mkdir()
for path in (source,HERE/'integrate.py',HERE/'build.json',HERE/'verification.json',HERE/'source-preservation.json',
             HERE/'build.log',i.TARGET/'accounting-product-proposal.pdf',i.TARGET/'accounting-product-proposal.log'):
    shutil.copy2(path,archive/path.name)
source.write_text(new);(i.TARGET/i.NEW).write_text(new)
preservation=i.read(HERE/'source-preservation.json');preservation['added_source_sha256']=i.sha(source)
i.dump('source-preservation.json',preservation)
# The successful build has a recorded layout veto. Archive its marker before rebuilding.
(HERE/'build.json').unlink()
i.dump('layout-repair.json',dict(old_source_sha256=sha256(old.encode()).hexdigest(),new_source_sha256=i.sha(source),
  edits=['Move long collection profile name earlier in sentence','Shorten run-in paragraph heading'],
  substantive_deletion=False,old_pdf_sha256=verification['pdf_sha256']))
print(json.dumps(dict(archived='attempt-01',layout_edits=2)))
