from pathlib import Path
p=Path(__file__).with_name('funding-control-authority.tex')
s=p.read_text()
edits={'price60':'price 60','pays60':'pays 60','cash22':'cash 22','the5':'the 5',
 'face80':'face 80','gives$':'gives $','obtain$':'obtain $','accreting$':'accreting $','at5':'at 5',
 'AASB132':'AASB~132','AASB127':'AASB~127','AASB128':'AASB~128','AASB18':'AASB~18',
 'AASB10':'AASB~10','AASB9':'AASB~9','AASB3':'AASB~3','amount$':'amount $','that120':'that 120',
 'paragraph25':'paragraph 25','paragraph26':'paragraph 26','paragraphs28':'paragraphs 28',
 "fixture's2028":"fixture's 2028",'its2029':'its 2029',"owner's25":"owner's 25",'a75':'a 75',
 'of100':'of 100','starting1':'starting 1','January2027':'January 2027','complete2027':'complete 2027',
 'from30':'from 30','to31':'to 31','from31':'from 31','to1 January':'to 1 January',
 'financial meaning unchanged':'control conclusions unchanged'}
for a,b in edits.items():s=s.replace(a,b)
p.write_text(s)
