"""Apply the seven diagnosed documentary repairs to a new protected successor."""
from pathlib import Path
import hashlib
import json
import shutil
import difflib

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'docs/design/proposal/manuscript-origin-matched-cessation-20261017'
NEXT = ROOT / 'docs/design/proposal/manuscript-readability-20261017'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def replace(path, before, after):
    text = path.read_text()
    assert text.count(before) == 1, (path, before[:100])
    path.write_text(text.replace(before, after))

def main():
    ledger = json.loads((ROOT/'data/accounting-master/continuous-reading-20261017/structure-ledger.json').read_text())
    assert ledger['diagnosis_status'] == 'author_diagnosis_complete'
    assert sha(BASE/'accounting-product-proposal.pdf') == ledger['pdf_sha256']
    assert not NEXT.exists(), 'Never overwrite a manuscript successor'
    NEXT.mkdir()
    rows = []
    for row in ledger['sources']:
        source = ROOT/row['path']
        assert sha(source) == row['sha256']
        rel = source.relative_to(BASE)
        dest = NEXT/rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source,dest)
        rows.append(dict(path=str(rel),baseline_sha256=row['sha256']))
    for suffix in ('.png','.jpg','.jpeg','.pdf','.sty','.cls','.bst','.lark'):
        for source in BASE.rglob('*'+suffix):
            if source == BASE/'accounting-product-proposal.pdf':
                continue
            dest = NEXT/source.relative_to(BASE)
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,dest)
    replace(NEXT/'accounting-product-proposal.tex','Version 3.41 (proposal candidate)','Version 3.42 (proposal candidate)')
    replace(NEXT/'chapters/13-reference-company.tex',
        "opening and closing working-capital balances, while the collection and purchase\ntotals are hidden. Under Northstar's explicit no-write-off, no-acquisition and\nno-currency-effect scope, the three bridges are",
        "opening and closing working-capital balances, while the collection and purchase\ntotals are hidden. Receivables rise from 20 to 35, inventory falls from 30 to\n20, and trade payables rise from 20 to 30. Let $C$ denote collections, $P$\npurchases and $S$ supplier payments, all in currency units over the same year.\nUnder Northstar's explicit no-write-off, no-acquisition and no-currency-effect\nscope, the three bridges are")
    replace(NEXT/'chapters/13-reference-company.tex',
        'Here $C$ denotes collections, $P$ purchases and $S$ supplier payments, all in\ncurrency units over the same year. Substitution gives',
        'Substitution gives')
    replace(NEXT/'sections/sector-company-composition.tex',"Of I's cash,20","Of I's cash, 20")
    replace(NEXT/'sections/sector-company-composition.tex','Its changes,3 and','Its changes, 3 and')

    # Move complete cost/PPE teaching blocks before their richer applications.
    path = NEXT/'sections/corporate-methods.tex'
    text = path.read_text()
    start = text.index('\\subsection{Inventory and assets retain their cost histories}')
    end = text.index('\\input{sections/error-estimate}',start)
    foundation = text[start:end]
    text = text[:start]+text[end:]
    anchor = '\\input{sections/production-cost}'
    assert text.count(anchor)==1
    bridge = ('The customer cases separate earned revenue from billing and cash.\n'
              'The cost side requires a second history: which goods and asset components\n'
              'remain, what they cost, and which losses or revaluations they have already\n'
              'absorbed. Ordinary cost and replacement cases establish that history\n'
              'before production and changed obligations make it more complex.\n\n')
    later = ('\\input{sections/corporate-benefit-impairment-foundations}\n\n'
             'These cost, benefit and obligation measurements supply the starting states\n'
             'for the following changes. Production first asks which costs the output\n'
             'can carry; later examples change estimates, rights and obligations while\n'
             'retaining their earlier measurement histories.\n\n')
    text = text.replace(anchor,bridge+foundation+later+anchor)
    path.write_text(text)

    # Preserve the EU foundation bodies and their labels,with real nested parents.
    path = NEXT/'sections/corporate-extensions.tex'
    text = path.read_text()
    split = text.index('\\hypertarget{share-based-compensation}')
    foundation, late = text[:split], text[split:]
    foundation = foundation.replace('\\section{','\\subsection{')
    foundation = foundation.replace('\\subsection{Recognising a separate obligation}',
                                    '\\subsubsection{Recognising a separate obligation}')
    foundation = foundation.replace('The additional methods below use',
        'The employee-benefit, impairment, provision, award and valuation methods use')
    (NEXT/'sections/corporate-benefit-impairment-foundations.tex').write_text(foundation)
    path.write_text(late)
    path = NEXT/'sections/impairment-floors.tex'
    path.write_text(path.read_text().replace('\\subsection{','\\subsubsection{'))
    replace(NEXT/'sections/corporate-extensions.tex',
        'AwardState distinguishes equity versus cash settlement,',
        'Ordinary employee benefits and impairment have established how service and\n'
        'past measurements remain in state. Share awards add settlement choices and\n'
        'vesting conditions; the valuation and capitalization methods that follow\n'
        'address the inputs and costs those cases require. These extensions retain\n'
        'the historical EU source scope stated with the earlier foundations.\n\n'
        'AwardState distinguishes equity versus cash settlement,')

    bank = NEXT/'chapters/15-banking.tex'
    for anchor,title,label in [
        ('Note~33 makes the funding distinction measurable for 2025.', 'Parent income, cash and conditional transfers','sec:bank-parent-funding'),
        ("For a future cash dividend, the model needs the bank's declaration", 'Dividend declarations and payout restrictions','sec:bank-payout-restrictions'),
        ("Replacing the example's supplied leverage-buffer standard", 'Systemic indicators and the applicable surcharge','sec:bank-systemic-surcharge'),
        ('Debt amounts add a second distinction.', 'Debt measurement, payment rights and succession','sec:bank-debt-rights'),
        ('Loan origination can debit loans', 'Loan creation, commitments and expected credit losses','sec:bank-loans-commitments'),
        ('Regulatory capital is computed in a separate prudential layer', 'Reconciling accounting equity to regulatory capital','sec:bank-capital-reconciliation')
    ]:
        heading = '\\subsection{'+title+'}\n\\label{'+label+'}\n\n'
        replace(bank,anchor,heading+anchor)
    replace(bank,'Debt amounts add a second distinction.',
            'The payout rules constrain cash leaving the bank. Debt contracts determine\n'
            'a different set of claims on the group: who owes a payment, when it falls\n'
            'due, and what a holder can require after a breach. Debt amounts therefore\n'
            'need their own measurement and contractual histories.')
    replace(NEXT/'sections/bank-funding-settlement.tex',
            'automatically satisfy the distinct US prudential profile considered next.',
            'automatically satisfy the distinct US prudential profile in\n'
            'Section~\\ref{sec:bank-prudential-connection}.')
    replace(NEXT/'sections/insurance-methods.tex',
            '\\clearpage\nThe acquisition-cost row appears within',
            'The acquisition-cost row appears within')

    diffs=[]
    for row in rows:
        rel=row['path']; before=(BASE/rel).read_text(); after=(NEXT/rel).read_text()
        row['candidate_sha256']=sha(NEXT/rel)
        row['changed']=before!=after
        if before!=after:
            diffs.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='3.41/'+rel,tofile='3.42/'+rel))
    new=NEXT/'sections/corporate-benefit-impairment-foundations.tex'
    diffs.extend(difflib.unified_diff([],new.read_text().splitlines(True),fromfile='/dev/null',tofile='3.42/'+str(new.relative_to(NEXT))))
    (OUT/'body-delta.patch').write_text(''.join(diffs))
    (OUT/'source-lock.json').write_text(json.dumps(dict(baseline=str(BASE.relative_to(ROOT)),
        candidate=str(NEXT.relative_to(ROOT)),baseline_pdf_sha256=ledger['pdf_sha256'],
        files=rows,new_files=[dict(path=str(new.relative_to(NEXT)),sha256=sha(new))]),indent=2)+'\n')
    print(json.dumps(dict(candidate=str(NEXT),changed=[r['path'] for r in rows if r['changed']],new_file=str(new.relative_to(NEXT)))))

if __name__=='__main__':
    main()
