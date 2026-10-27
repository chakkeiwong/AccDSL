"""Exact strict difference constraints. Certificates contain original edge indices."""
from fractions import Fraction as Q

def solve(variables,edges):
 names=sorted(set(variables)|{'zero'});d={x:(Q(0),0) for x in names};pred={};last=None
 for _ in names:
  last=None
  for i,e in enumerate(edges):
   u,v=e['u'],e['v'];w=(Q(e['bound']),-int(e['strict']));candidate=(d[u][0]+w[0],d[u][1]+w[1])
   if candidate<d[v]:d[v]=candidate;pred[v]=i;last=v
  if last is None:break
 if last is not None:
  x=last
  for _ in names:x=edges[pred[x]]['u']
  start=x;cycle=[]
  while True:
   i=pred[x];cycle.append(i);x=edges[i]['u']
   if x==start:break
  return {'kind':'empty','cycle':cycle}
 eps=Q(1)
 for e in edges:
  a=d[e['v']][0]-d[e['u']][0];b=d[e['v']][1]-d[e['u']][1];slack=Q(e['bound'])-a
  if slack>0:eps=min(eps,slack/(abs(b)+1)/2)
 values={k:a+b*eps for k,(a,b) in d.items()};z=values['zero']
 return {'kind':'nonempty','values':{k:str(values[k]-z) for k in names}}

def opposite(e):return {'u':e['v'],'v':e['u'],'bound':str(-Q(e['bound'])),'strict':not e['strict']}
