from pathlib import Path
import re
H=Path(__file__).resolve().parent
s=(H.parent/'credit-claim-integration-20261027/integrate.py').read_text()
changes={
 'manuscript-coupon-resume-v548-20261027':'manuscript-credit-claim-v549-20261027',
 'manuscript-credit-claim-v549-20261027':'manuscript-credit-recovery-v550-20261027',
 'c91cfa88237b56a86ad59df541c3330ea7699489ce0e8ccc27a4a0603d249fa3':'c8dc8f87c72be812b91d3d73ca8e134041af6f8b924799b705d02a3418e8e26d',
 'aa39fdccc65342f3c0caae3e7828f4a77a09abe87ddd162f3e26104f66d6081c':'a151d669ee83be0f49afd7c95b0481a757a4f7bd6e53d13ca96cb76edd1a4072',
 '5.48':'5.49','5.49':'5.50',
 'credit-claim.tex':'credit-recovery.tex','simulation/credit-claim':'simulation/credit-recovery',
 'credit-claim-continuity-20261027':'credit-recovery-intake-20261027',
 'accounting-credit-claim-integration-20261027.md':'accounting-credit-recovery-integration-20261027.md',
}
s=re.sub('|'.join(re.escape(k) for k in sorted(changes,key=len,reverse=True)),lambda m:changes[m[0]],s)
s=s.replace("for folder in ['credit-recovery-intake-20261027']", "for folder in ['credit-recovery-scope-20261027','credit-recovery-intake-20261027']")
s=s.replace("['status']=='PASS'", "['status']=='PASS_UNRESOLVED_ONLY'",1)
a=s.index("[('credit-claim','Financial closure");b=s.index(']:',a)
s=s[:a]+"[('credit-recovery','A receipt after financial write-off raises a new accounting question.','them to match a later outcome.',['2019','50','unknown','derecognition','positive recovery'])]"+s[b+1:]
p=H/'integrate.py';assert not p.exists();p.write_text(s)
print('Prepared 5.50 source-boundary integration writer')
