"""Find a Boolean assignment or explicit contradictory implication paths."""
from collections import deque

def edges(terms):
    result={}
    for term,source in terms:
        if len(term)==1:
            i,a=term[0];result.setdefault((2*i+a,2*i+1-a),source)
        elif len(term)==2:
            (i,a),(j,b)=term
            result.setdefault((2*i+a,2*j+1-b),source)
            result.setdefault((2*j+b,2*i+1-a),source)
        else:raise ValueError('only unary/binary refusals supported')
    return result

def solve(n,terms):
    es=edges(terms);graph=[[] for _ in range(2*n)];reverse=[[] for _ in range(2*n)]
    for a,z in es:graph[a].append(z);reverse[z].append(a)
    seen=set();order=[]
    for start in range(2*n):
        if start in seen:continue
        stack=[(start,False)]
        while stack:
            v,done=stack.pop()
            if done:order.append(v);continue
            if v in seen:continue
            seen.add(v);stack.append((v,True))
            for z in reversed(graph[v]):
                if z not in seen:stack.append((z,False))
    component={};index=0
    for start in reversed(order):
        if start in component:continue
        stack=[start];component[start]=index
        while stack:
            v=stack.pop()
            for z in reverse[v]:
                if z not in component:component[z]=index;stack.append(z)
        index+=1
    def path(a,z):
        previous={a:None};queue=deque([a])
        while z not in previous:
            v=queue.popleft()
            for nxt in graph[v]:
                if nxt not in previous:previous[nxt]=v;queue.append(nxt)
        out=[];v=z
        while v!=a:
            prior=previous[v];out.append(dict(start=prior,end=v,row=es[(prior,v)]));v=prior
        return list(reversed(out))
    for i in range(n):
        if component[2*i]==component[2*i+1]:
            return dict(kind='contradiction',variable=i,forward=path(2*i,2*i+1),backward=path(2*i+1,2*i))
    return dict(kind='assignment',rule=[int(component[2*i+1]>component[2*i]) for i in range(n)])

def verify(n,terms,certificate):
    assert type(certificate) is dict
    if certificate.get('kind')=='assignment':
        assert set(certificate)=={'kind','rule'}
        rule=certificate['rule'];assert type(rule) is list and len(rule)==n and all(type(v) is int and v in (0,1) for v in rule)
        assert not any(all(rule[i]==bit for i,bit in term) for term,source in terms)
    else:
        assert set(certificate)=={'kind','variable','forward','backward'} and certificate['kind']=='contradiction'
        i=certificate['variable'];assert type(i) is int and 0<=i<n
        bysource={source:term for term,source in terms}
        for name,a,z in [('forward',2*i,2*i+1),('backward',2*i+1,2*i)]:
            path=certificate[name];assert type(path) is list and 0<len(path)<=2*n;current=a
            for edge in path:
                assert set(edge)=={'start','end','row'} and edge['start']==current
                u,v=edge['start'],edge['end'];assert type(u) is int and type(v) is int and 0<=u<2*n and 0<=v<2*n
                term=bysource[edge['row']]
                # The row is violated when u is true and v is false. This
                # directly justifies u=>v without calling the graph builder.
                condition={(u//2,u%2),(v//2,1-v%2)}
                assert set(term)==condition or len(term)==1 and u//2==v//2 and u%2!=v%2 and set(term)=={(u//2,u%2)}
                current=v
            assert current==z
    return True
