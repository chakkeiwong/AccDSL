from pathlib import Path
H=Path(__file__).resolve().parent;assert not (H/'integrate.py').exists()
s=(H.parent/'debt-exchange-integration-20261027/integrate.py').read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep("S=R/'docs/design/proposal/manuscript-prior-equity-v536-20261027'","S=R/'docs/design/proposal/manuscript-debt-exchange-v537-20261027'")
rep("T=R/'docs/design/proposal/manuscript-debt-exchange-v537-20261027'","T=R/'docs/design/proposal/manuscript-prospective-policy-v538-20261027'")
rep('221a556f22a7fcb845487a096770d8abac73775b712dc598547bfa9d83fd3920','6ca03da58896b0def9388114460aa1076d1c918342d5982bf253e19a5c281927')
rep('50dc57a63853c78d5b5580057958b1b1cc423e93805c580a156038a5822a7db0','6e1fd02cf3b454fb0cdb3590a8e3df17850d7b57fae467b32c8501a2ffbf11d6')
rep('Version 5.37','__NEW__');rep('Version 5.36','Version 5.37');rep('__NEW__','Version 5.38');rep("startswith('5.36;')","startswith('5.37;')")
rep("ADDED={'simulation/debt-exchange.tex':'debt-exchange.tex'}","ADDED={'simulation/prospective-policy.tex':'prospective-policy.tex','simulation/conversion-partition.tex':'conversion-partition.tex'}")
rep("'simulation/26-finite-finance.tex','references.bib'","'simulation/26-finite-finance.tex','simulation/17-continuous-methods.tex'")
start=s.index("    if n=='simulation/26-finite-finance.tex':");end=s.index('    return t',start)
s=s[:start]+"    if n=='simulation/26-finite-finance.tex':return t+'\\n\\\\input{simulation/conversion-partition}\\n'\n    if n=='simulation/17-continuous-methods.tex':return t+'\\n\\\\input{simulation/prospective-policy}\\n'\n"+s[end:]
rep("['acquisition-debt-relationship-20261027','debtor-conversion-worksheet-20261027','creditor-conversion-worksheet-20261027']","['prospective-policy-domain-20261027','prospective-partial-policy-20261027','conversion-control-transaction-20261027']")
rep("not {'inputs','__pycache__'}&set(p.parts)","not {'inputs','__pycache__','control-before'}&set(p.parts)")
rep("for folder,attempt in [(x,'attempt-01') for x in ['prospective-policy-domain-20261027','prospective-partial-policy-20261027','conversion-control-transaction-20261027']]:","for folder,attempt in [('prospective-policy-domain-20261027','attempt-03'),('prospective-partial-policy-20261027','attempt-01'),('conversion-control-transaction-20261027','attempt-01')]:")
rep("['debt-exchange.tex','reader-plan.md','bibliography-addition.bib']","['prospective-policy.tex','conversion-partition.tex','reader-plan.md']")
rep("attempt in ['01','02']","attempt in ['01','02','03']");rep('timeout=240','timeout=120')
rep('accounting-debt-exchange-integration-20261027.md','accounting-prospective-policy-integration-20261027.md')
start=s.index("            title='One debt exchange");end=s.index('            clipped=',start)
s=s[:start]+'''            ranges=[]
            for label,opening,ending,words in [
                ('policy','A manager who may pay an obligation or draw on a facility','broader observation languages still require their own comparisons.',['pending','unresolved','declaration','512','4,096']),
                ('partition','Obtaining control through a debt exchange raises a question','before constructing goodwill and acquired-basis statements.',['108','80','settlement','supplied','unresolved'])]:
                starts=[i+1 for i,t in enumerate(texts) if opening in t];ends=[i+1 for i,t in enumerate(texts) if ending in t]
                ck(name+'/'+label+'/section',bool(starts) and bool(ends));first,last=starts[-1],ends[-1];ck(name+'/'+label+'/order',first<=last)
                text=' '.join(texts[first-1:last]);ck(name+'/'+label+'/complete_argument',all(x in text for x in words));ranges.append([first,last])
''' + s[end:]
rep("pages=[1]+list(range(first,last+1));folder=", "pages=[1]+sorted({i for first,last in ranges for i in range(first,last+1)});folder=")
rep('addition_pages=[first,last]','addition_pages=ranges')
(H/'integrate.py').write_text(s)
for n in ['prospective-policy.tex','conversion-partition.tex']:
 p=H/n;t=p.read_text()
 for a,b in [('the25','the 25'),('retains15','retains 15'),('The512','The 512'),('most12','most 12'),('most4,096','most 4,096'),('produces12','produces 12'),('requires18','requires 18'),('its10','its 10'),('checks12','checks 12'),('at110','at 110'),('and31','and 31'),('of80','of 80'),('consideration,20','consideration, 20'),('settlement,5','settlement, 5'),('costs and3','costs and 3'),('to108','to 108'),('only80','only 80'),('the20','the 20'),('inquiry,33','inquiry, 33'),('all24','all 24'),('components,21','components, 21'),('and351','and 351')]:t=t.replace(a,b)
 p.write_text(t)
print('Created guarded v5.38 writer and repaired number spacing.')

