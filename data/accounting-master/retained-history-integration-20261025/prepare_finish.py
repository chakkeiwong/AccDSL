"""Prepare the successor control refresh without touching frozen evidence."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
text=(ROOT/'data/accounting-master/credit-linked-book-integration-20261025/finish.py').read_text()
changes=[
 ('accounting-simulator-post-sector-reassessment-20261025.md','accounting-retained-statement-history-20261025.md'),
 ('credit-linked-integration-20261025/coverage.json','credit-linked-book-integration-20261025/coverage.json'),
 ('integrate_v2.py','integrate.py'),('pages = [1, 409, 410, 411, 412]','pages = [1, 389, 390, 391]'),
 ("'4.32'","'4.33'"),('Version 4.32','Version 4.33'),('in4.32','in4.33'),('4.32;528 pages','4.33;529 pages'),
 ('Optional exact credit book integrated','Retained source histories integrated'),
 ('Optional exact credit book projection and reporting limits integrated','Selected source-bound conditional history composition integrated'),
 ('17 focused tests,72 regressions,36 book exchanges and11 refusals replay.','15 focused tests,65 regressions and11 complete exchanges replay.'),
 ('3186 identities and124 rational host validations pass across252 journals and228 observations.','Full256-observation/143-relation reports and both source/history constraint systems remain preserved.'),
 ('The optional single-root projection preserves context, native order and complements; admission remains false.','Separate source bases and unresolved actual-company facts remain explicit; admission stays false.'),
 ('Cover and PDF409–412 were viewed; first heading spacing repaired, no new warnings, five inherited underfull notices.','Cover and PDF389–391 were viewed; no new warnings, five inherited underfull notices.'),
 ('which remaining simulator dependency is now ready after exact sector composition?','can selected cash histories also satisfy retained balance-sheet constraints?'),
 ("['credit-linked-book-20261025',HERE.name]","['retained-source-history-20261025',HERE.name]"),
 ('Reassess the whole simulator backlog and select the next ready mission dependency','Constrain selected cash histories with explicit retained balance-sheet evidence'),
 ('accounting-credit-linked-book-integration-20261025.md','accounting-retained-history-integration-20261025.md'),
 ('Version4.31 plus accepted exact credit book exchanges','Version4.32 plus accepted retained-source/history exchanges'),
 ('build-v2','build'),
 ("sum(json.loads((HERE/n).read_text())['wall_seconds'] for n in ['build.json','build.json'])","json.loads((HERE/'build.json').read_text())['wall_seconds']")
 ]
for old,new in changes:
    assert old in text,old;text=text.replace(old,new)
a=text.index('advanced = ');b=text.index('coverage = ',a)
text=text[:a]+"advanced = {'MC01','MC04','MC05','MC09','MC10','MC24','MC28','MC32','MC33','MC34','MC35'}\n"+text[b:]
a=text.index('artifacts = ');b=text.index("dump(HERE / 'run-manifest.json'",a)
text=text[:a]+"artifacts = ['integration-baseline.json','integration-verification.json','source-lock.json','build.json','build.log','audit.md','review.md','result.md','coverage.json','render-review.json','replay-observation.json','control-refresh.json','integrate.py','setup.py','integration-code-lock.json','prepare_finish.py','finish.py']\n"+text[b:]
text=text.replace('python3 -B integrate.py prepare/build; repair_layout.py; integrate.py build/verify; finish.py',
                  'python3 -B setup.py; integrate.py prepare/build/verify; finish.py')
compile(text,'finish.py','exec');assert not (HERE/'finish.py').exists();(HERE/'finish.py').write_text(text)
print('Prepared Version4.33 control refresh')
