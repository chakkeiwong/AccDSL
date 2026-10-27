"""Build additive pylcs source/Unicode records once."""
import hashlib
import json
from pathlib import Path
import re
import shlex
from compare import calculate

UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]
BASE=UNIT.parent


def bind(path):return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def write(name,value):
    with (UNIT/name).open('x') as handle:json.dump(value,handle,indent=2);handle.write('\n')


def main():
    assert not (UNIT/'source-ledger.json').exists(),'one-time construction'
    acquisitions=[]
    for stem in ('01-package','02-repository','03-tree','04-source','05-source','06-source'):
        rpath=UNIT/'sources'/(stem+'.receipt.json');r=json.loads(rpath.read_text())
        ipath=UNIT/'sources'/(stem+'.invocation.json');inv=json.loads(ipath.read_text())
        acquisitions.append({'url':r['url'],'status':r['http_code'],'bytes':r['size_download'],'curl_seconds':r['time_total'],
            'command':shlex.join(inv['argv']),'body':bind(ROOT/r['filename_effective']),
            'headers':bind(UNIT/'sources'/(stem+'.headers')),'receipt':bind(rpath),'invocation':bind(ipath)})
    native=UNIT/'sources/04-source.body';init=UNIT/'sources/05-source.body';setup=UNIT/'sources/06-source.body'
    current=BASE/'r04-pubtablesv2-20261019/sources/05-metric.py'
    needles={native:[
        ('splitter','vector<string> utf8_split(const string &str)'),
        ('byte-length-int','int len = str.length();'),
        ('continuation-test','if (right >= len || ((str[right] & 0xc0) != 0x80))'),
        ('token-slice','string s = str.substr(left, right - left);'),
        ('lcs-signature','int lcs_sequence_length(const string &str1, const string &str2)'),
        ('empty-input','if (str1 == "" || str2 == "")'),
        ('string-to-tokens','vector<string> s1 = utf8_split(str1);'),
        ('matrix-storage','vector<vector<int>> dp(m + 1, vector<int>(n + 1));'),
        ('matching-token','if (s1[i - 1] == s2[j - 1])'),
        ('diagonal-recurrence','dp[i][j] = dp[i - 1][j - 1] + 1;'),
        ('max-recurrence','if (dp[i - 1][j] >= dp[i][j - 1])'),
        ('return-optimum','return dp[m][n];'),
        ('native-module','PYBIND11_MODULE(_pylcs, m)'),
        ('export-exact-symbol','m.def("lcs_sequence_length", &lcs_sequence_length'),
        ('separate-substring','m.def("lcs_string_length", &lcs_string_length')],
        init:[('python-export','from _pylcs import *')],
        setup:[('extension-name',"'_pylcs'"),('build-source',"['src/main.cpp']"),
            ('cpp-language',"language='c++'"),('recipe-version',"version='0.1.1'"),
            ('binding-range',"install_requires=['pybind11>=2.2']")],
        current:[('wrapper-equality','if string1 == string2:'),
            ('wrapper-call','lcs_length = pylcs.lcs_sequence_length(string1, string2)'),
            ('wrapper-denominator','return 2 * lcs_length / (len(string1) + len(string2))')],
    }
    passages=[]
    for path,rows in needles.items():
        lines=path.read_text().splitlines()
        for identifier,quote in rows:
            hits=[i for i,line in enumerate(lines,1) if quote in line];assert hits,(identifier,quote)
            passages.append({'id':identifier,'path':str(path.relative_to(ROOT)),'line':hits[0],'quote':quote})
    package=json.loads((UNIT/'sources/01-package.body').read_text())
    head=re.findall(r'"currentOid":"([0-9a-f]{40})"',(UNIT/'sources/02-repository.body').read_text())[0]
    witness=calculate()
    write('source-ledger.json',{'date_local':'2026-10-20','package':'pylcs','pypi_version':package['info']['version'],
        'repository':package['info']['home_page'],'commit':head,'acquisitions':acquisitions,'passages':passages,
        'reading':{'native':'lines1-61 and328-365 only; intervening functions uninspected',
            'initializer':'entire file','setup':'entire file','package_description':'entire metadata description'},
        'release_files':[{'filename':r['filename'],'sha256':r['digests']['sha256'],'uploaded':r['upload_time_iso_8601'],'yanked':r['yanked']} for r in package['releases']['0.1.1']],
        'distribution_downloaded':False,'release_source_equivalence':False})
    write('witnesses.json',witness)
    write('source-support-ledger.json',{'title':'pylcs selected native LCS and binding declarations','classification':'IMPLEMENTATION_OR_SOFTWARE',
        'authors':'kuangkzh transfer repository; metadata identifies Meteorix predecessor','version':'PyPI0.1.1 versus current source commit'+head,
        'local_native':bind(native),'publication_status':'Software metadata and pinned source; no distribution installed or acquired',
        'retraction_quarantine':'All eight0.1.1 files unyanked in acquired metadata; no independent vulnerability/correction survey',
        'inspected_sections':['utf8_split','lcs_sequence_length','PYBIND11_MODULE exports','Python initializer','setup recipe'],
        'equations':'Local prefix-DP recurrence proof in execution-audit.md; no imported theorem',
        'allowed':['selected-source exact token-LCS recurrence','conditional valid-UTF8/codepoint relation','explicit source limits'],
        'forbidden':['installed validity','release-source equality','pybind11 conversion checked','normalization/grapheme equivalence','performance ranking']})
    write('citation-venue-ledger.json',{'date':'2026-10-20','citation_count':'not available','citation_source':'No academic citation query for dependency',
        'venue':'PyPI/repository source','venue_metric':'not available','caveat':'Package popularity and super-fast description are not performance evidence.'})
    write('backward-snowball-ledger.json',{'scope':'Dependency and source chain, not new paper bibliography','entries':[
        {'target':'Meteorix/pylcs','classification':'IMPLEMENTATION_OR_SOFTWARE','action':'Predecessor identified in metadata; original history not audited'},
        {'target':'pybind11>=2.2','classification':'IMPLEMENTATION_OR_SOFTWARE','action':'Next exact string-conversion source inquiry; build headers uninspected'},
        {'target':'Wikipedia LCS/substring/edit-distance links','classification':'BACKGROUND','action':'Not used as theorem support; local recurrence proof supplied'},
        {'target':'GriTS paper and current wrapper','classification':'DIRECT_METHOD','action':'Completed original/theory units retained; no reread for completion credit'}]})
    write('forward-snowball-ledger.json',{'new_query':'None in bounded dependency inquiry','retained_consumer':'Kensho GriTS pylcs call at pinned commit',
        'status':'One concrete inspected consumer; no comprehensive forward coverage claim'})
    write('claim-support-ledger.json',{'candidate':'3.44','manuscript_changed':False,'entries':[
        {'claim':'Selected C++ recurrence computes exact LCS over supplied tokens','class':'PROJECT_DERIVATION','support':'prefix induction in execution-audit.md plus code anchors',
         'limit':'dimensions fit ints, allocation succeeds; no compiled execution'},
        {'claim':'UTF8 groups equal codepoints','class':'PROJECT_DERIVATION','support':'valid-scalar UTF8 boundary argument and15 finite strings',
         'limit':'Binding conversion and malformed input acceptance are unchecked'},
        {'claim':'Codepoint normalization or grapheme equivalence','class':'SOURCE_GAP_BLOCKER','support':'Not performed in selected source; illustrative canonical/emoji pairs show distinction'},
        {'claim':'PyPI0.1.1 equals inspected repository head','class':'SOURCE_GAP_BLOCKER','support':'Version labels agree, exact distribution-source binding absent'}]})
    write('omission-risk-ledger.json',{'entries':[
        {'gap':'pybind11 Unicode conversion','status':'inspect next','risk':'Source std::string token contract is conditional until binding conversion is inspected'},
        {'gap':'Release/distribution/head correspondence','status':'open','risk':'Equal version string is not equal bytes'},
        {'gap':'Malformed UTF8/surrogate inputs and resource bounds','status':'open','risk':'Splitter is not a validator; int dimensions and quadratic storage need runtime constraints'},
        {'gap':'Historical/current empirical performance','status':'held','risk':'No benchmark or package execution authorised'}],
        'survey_status':'Additive dependency evidence only; no whole-row closure'})
    print(json.dumps({'constructed':True,'anchors':len(passages),'pairs':[{k:v for k,v in x.items() if k in ('name','lcs_codepoints','wrapper_reward','nfc_reward_explanatory_only')} for x in witness['examples']],
        'boundary_strings':15,'malformed':2}))


if __name__=='__main__':main()
