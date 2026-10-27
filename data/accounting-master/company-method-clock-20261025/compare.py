from copy import deepcopy
from examples import binder,payment,sale,rehash


def compare():
    rows=[]
    for name,make in [('alpha',lambda:payment('alpha')),('beta',lambda:payment('beta')),('sale',sale)]:
        book,call,request=make();original=deepcopy((book,call));expected=binder.transition.propose(book,request)
        result=binder.propose(book,call);applied=binder.apply(book,call,result)
        checks={'explicit_request':result['materialized_request']==request,'entire_transition':result['transition']==expected,
                'entire_application':applied['transition']==binder.transition.apply(book,request,expected),
                'input_preserved':(book,call)==original,'flags_false':all(result[k] is False for k in binder.FLAGS)}
        rows.append({'case':name,'book':book,'call':call,'expected_request':request,'result':result,'applied':applied,'checks':checks})
    for name,value,status in [('unknown',{'status':'unknown','reason':'unobserved'},'unresolved'),('false',{'status':'known','value':False},'unsupported')]:
        book,call,request=payment();call['event']['inputs']['approved']['value']=value;request['event']['inputs']['approved']['value']=value
        result=binder.propose(book,call);expected=binder.transition.propose(book,request)
        rows.append({'case':name,'book':book,'call':call,'result':result,'checks':{
            'status':result['status']==status,'complete_refusal':result['transition']==expected,'no_applied_state':'after' not in result['transition']}})
    return {'cases':rows,'checks':[{'name':row['case']+':'+k,'passed':bool(v)} for row in rows for k,v in row['checks'].items()]}
