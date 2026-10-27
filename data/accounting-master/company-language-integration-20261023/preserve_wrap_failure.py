from pathlib import Path
import json
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
dest=HERE/'before-wrap-repair'; assert not dest.exists(); dest.mkdir()
for name in ['build.json','build.log']:(HERE/name).rename(dest/name)
for name in ['accounting-product-proposal.pdf','accounting-product-proposal.log','sections/company-family-language.tex']:
    p=ROOT/'docs/design/proposal/manuscript-company-language-20261023'/name
    (dest/Path(name).name).write_bytes(p.read_bytes())
(dest/'failure.json').write_text(json.dumps({'classification':'rendering defect','overfull_points':40.13487,'source':'sections/company-family-language.tex:143-151','repair':'separate path list from explanatory paragraph','scientific_content_changed':False},indent=2)+'\n')
print(json.dumps({'preserved':str(dest)}))
