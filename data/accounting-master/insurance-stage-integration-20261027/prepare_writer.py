from pathlib import Path
import re
H=Path(__file__).resolve().parent
s=(H.parent/'credit-recovery-integration-20261027/integrate.py').read_text()
changes={
 'manuscript-credit-claim-v549-20261027':'manuscript-credit-recovery-v550-20261027',
 'manuscript-credit-recovery-v550-20261027':'manuscript-insurance-stage-v551-20261027',
 'c8dc8f87c72be812b91d3d73ca8e134041af6f8b924799b705d02a3418e8e26d':'fe85d4723605e5bdf1fb1602ffa957bf9bdc9f02a3bfa9f45f8719cd6111f795',
 'a151d669ee83be0f49afd7c95b0481a757a4f7bd6e53d13ca96cb76edd1a4072':'63fa2a2dc33c272ec31d0a842685cd3a52136977afd87a41592ca2ea261edee7',
 '5.49':'5.50','5.50':'5.51',
 'credit-recovery.tex':'insurance-stage.tex','simulation/credit-recovery':'simulation/insurance-stage',
 'credit-recovery-intake-20261027':'insurance-recovery-stage-book-20261027',
 'credit-recovery-scope-20261027':'insurance-shared-group-audit-20261027',
 'accounting-credit-recovery-integration-20261027.md':'accounting-insurance-stage-integration-20261027.md',
 'PASS_UNRESOLVED_ONLY':'PASS_STAGE_ONLY',
}
s=re.sub('|'.join(re.escape(k) for k in sorted(changes,key=len,reverse=True)),lambda m:changes[m[0]],s)
a=s.index("[('credit-recovery','A receipt");b=s.index(']:',a)
s=s[:a]+"[('insurance-stage','An insurance calculation can preserve the right total while losing the relation','opening before these stages can become a company-book execution.',['issued','held','22','unknown','fiscal'])]"+s[b+1:]
p=H/'integrate.py';assert not p.exists();p.write_text(s)
print('Prepared insurance stage integration writer')
