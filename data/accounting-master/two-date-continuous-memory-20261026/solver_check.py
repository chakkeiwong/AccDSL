from model import A,H,Region,rect,F
import json
x,y=A(x=1),A(y=1);rows=[]
def ck(n,c):rows.append((n,bool(c)));assert c,n
r=rect(F(0),F(1),F(0),F(1));ck('open_rectangle',r.feasible() and len(r.vertices())==4)
ck('strict_diagonal_impossible',not r.add(H(x+y-2,False),H(2-x-y,False)).feasible())
q=r.add(H(x+y-1));ck('diagonal_triangle',q.feasible() and len(q.vertices())==3)
ck('sum_inf_unattained',q.bounds(x+y)=={'inf':0,'sup':1,'inf_attained':False,'sup_attained':True})
line=Region([H(-x),H(x-1),H(-y),H(y-1),H(x-y),H(y-x)])
ck('line_segment',line.feasible() and len(line.vertices())==2)
ck('line_strict_empty',not line.add(H(x-y,True)).feasible())
p=rect(F(1,3),F(1,3),F(2,3),F(2,3));ck('point',p.witness()==(F(1,3),F(2,3)))
ck('point_bounds',p.bounds(x+y)=={'inf':1,'sup':1,'inf_attained':True,'sup_attained':True})
ck('split_disjoint',not r.add(H(x+y-1),H(1-x-y,True)).feasible())
ck('all_sides_nonempty',all(v.feasible() for _,v in r.split(H(x+y-1))))
ck('outside_empty',not r.add(H(3-x-y)).feasible())
ck('equivalence',r.equal(Region(list(reversed(r.hs)))))
print(json.dumps({'status':'PASS','checks':rows}))
