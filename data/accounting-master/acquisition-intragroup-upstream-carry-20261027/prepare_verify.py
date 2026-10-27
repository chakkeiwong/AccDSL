from pathlib import Path
H=Path(__file__).resolve().parent;p=H/'verify.py';assert not p.exists()
s=(H.parent/'acquisition-intragroup-carry-20261027/verify.py').read_text()
replacements=[
('accounting-intragroup-carry-20261027','accounting-intragroup-upstream-carry-20261027'),
("def run(earlier,settled,fraction,tax='known'):","def run(earlier,settled,fraction,tax='recognised',continuation='known'):"),
("fraction,tax]);b=f.fixture(earlier,settled,fraction,tax)","fraction,tax,continuation]);b=f.fixture(earlier,settled,fraction,tax,continuation)"),
("'tax_method_required' if tax=='unresolved' else", "'tax_method_required' if tax=='unresolved' or continuation=='unresolved' else"),
("if tax=='unresolved':", "if tax=='unresolved' or continuation=='unresolved':"),
("f.prior(earlier,settled)['result']", "f.prior(earlier,settled,tax)['result']"),
("f.expected(earlier,settled,fraction).items()", "f.expected(earlier,settled,fraction,tax).items()"),
("if (earlier,settled,fraction)==('0/1',False,'1/1'):","if (earlier,settled,fraction,tax)==('0/1',False,'1/1','recognised'):"),
("cash='310/1',assets='1627/4',liabilities='57/2',equity='1513/4'","cash='290/1',assets='1547/4',liabilities='57/2',equity='1433/4'"),
("b['payload']['opening_legal']['P.retained_post']='0/1'", "b['payload']['opening_legal']['S.retained_post']='0/1'"),
]
for old,new in replacements:assert old in s,old;s=s.replace(old,new)
start=s.index("        run('0/1',False,'0/1')")
end=s.index("        b=f.fixture();b['payload']['sale']['receipts']",start)
s=s[:start]+'''        for tax in ['recognised','unrecognised']:
            for earlier in ['0/1','1/2']:
                for settled in [False,True]:
                    for fraction in ['0/1','1/2','1/1']:run(earlier,settled,fraction,tax)
        for earlier in ['0/1','1/2']:
            for settled in [False,True]:
                run(earlier,settled,'1/1','unresolved')
                run(earlier,settled,'1/1','recognised','unresolved')
                run(earlier,settled,'1/2','unrecognised','unresolved')
        unrec=next(x['result']['report'] for x in cases if x['id']=='0/1/credit/1/1/unrecognised/known')
        for k,v in dict(profit='1/2',owners_profit='9/4',nci_profit='-7/4',assets='1547/4',liabilities='57/2',equity='1433/4').items():ck('unrecognised_absolute/'+k,unrec[k],v)
        rec=next(x['result']['report'] for x in cases if x['id']=='0/1/credit/1/1/recognised/known')
        for k in ['assets','liabilities','equity','owners_equity','nci','cash']:ck('fully_realised_same_closing/'+k,rec[k],unrec[k])
''' +s[end:]
# Check the complete adjusted earnings by entity against reported NCI.
anchor="            ck(name+'/no_reacquisition',not any(x['id']=='acquisition' for x in r['group_journals']))"
assert anchor in s
s=s.replace(anchor,anchor+'''
            sub=-sum(F(v) for k,v in r['closing_adjusted'].items() if k.split('.')[0] in ['S','group'] and k.split('.')[1] in m.INCOME)
            ck(name+'/account_nci',sub/4,F(r['report']['nci_profit']))
            for entry in r['group_journals'][1:]:
                ck(name+'/subsidiary_attribution/'+entry['id'],entry['profit_attribution'],'subsidiary_ordinary_rights')''')
compile(s,str(p),'exec');p.write_text(s);print('Prepared complete upstream carry verifier.')
