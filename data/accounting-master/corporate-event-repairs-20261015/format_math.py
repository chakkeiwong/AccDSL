from pathlib import Path
import re,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
p=ROOT/'docs/design/proposal/manuscript-corporate-events-20261015/sections/corporate-events.tex'
s=p.read_text();old=s
# Introduced equations only; no historical section or source citation is rewritten.
replacements={
 'qA':r'\(qA\)', 'qL':r'\(qL\)', 'q(L−A)':r'\(q(L-A)\)',
 'D−P':r'\(D-P\)', 'max(P−D−C,0)':r'\(\max(P-D-C,0)\)',
 'A=80 and L=100':r'\(A=80\) and \(L=100\)',
 'A=60 and L=75':r'\(A=60\) and \(L=75\)',
 'D=1,000/P=900':r'\(D=1{,}000\), \(P=900\)',
 'D=1,100/P=920':r'\(D=1{,}100\), \(P=920\)',
 'D=798.75/P=768.75':r'\(D=798.75\), \(P=768.75\)',
}
done=[]
for a,b in replacements.items():
 if a in s:s=s.replace(a,b);done.append(a)
s=re.sub(r'(?<=[A-Za-z])(?=\d)', ' ',s)
# Restore deliberate source keys after presentation spacing.
s=s.replace('eu 20231803','eu20231803')
p.write_text(s)
(OUT/'math-format.json').write_text(json.dumps({'explicit_math':done,'changed':s!=old},indent=2)+'\n')
print(json.dumps({'explicit_math':len(done),'changed':s!=old}))
