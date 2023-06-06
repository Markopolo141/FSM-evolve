from numpy.linalg import eig
from numpy import matrix

from sympy import symbols,Matrix,diff

YP = symbols("YP")
YY = symbols("YY")
YO = symbols("YO")

A = Matrix([
[ 3.0e-5, YP/3 + YY/3 + 3.0e-5, 0.666696666666667, 0.666696666666667, 3.0e-5],
[1.00003, 3.0e-5, 3.0e-5, 3.0e-5, 3.0e-5],
[ 3.0e-5, 0.0333333333333333*YO + 0.0333333333333333*YP + 0.0333333333333333*YY + 3.0e-5,  3.0e-5,  3.0e-5, 3.0e-5],
[ 3.0e-5, -YO/3 - YP/3 - YY/3 + 1.00003, 3.0e-5, 3.0e-5, 3.0e-5],
[ 3.0e-5, YO/3 + 3.0e-5, 0.333363333333333, 0.333363333333333, 3.0e-5]])

A = A.subs(YP,1)
A = A.subs(YY,1)

dA = diff(A,YO)


lams = []
vecs = []
v = []
As = []

dyo = 0.000001

for yo in [0.0,dyo,1.0-dyo,1.0]:
    A_x = A.subs(YO,yo)
    A_x = matrix(A_x.tolist()).astype(float)
    E = eig(A_x)
    lam = max(E[0])
#    print(lam)
    lams.append(lam.real)
    vec = E[1].transpose()[E[0].tolist().index(lam)].transpose().real
#    print((A_x*vec)[0]/vec[0])
    v.append(vec)
    As.append(A_x)
    vecs.append((vec.transpose()*dA*vec)[0,0])

print(lams)
print(vecs)
print("manual dL at 0:",(lams[1]-lams[0])/dyo)
print("manual dL at 1:",(lams[3]-lams[2])/dyo)
print("automated dl at 0:",vecs[0])
print("automated dl at 1:",vecs[-1])

print("anomoly term at 0:",v[0].transpose()*As[0]*((v[1]-v[0])*1.0/dyo))
print("orthogonality tesst at 0:", v[0].transpose()*((v[1]-v[0])*1.0/dyo))

print("diff manual-automatic at 0:",vecs[0]-(lams[1]-lams[0])/dyo)

#import pdb
#pdb.set_trace()
