from pathlib import Path
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
