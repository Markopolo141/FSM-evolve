from copy import deepcopy as copy
import math


class SVG(object):
    xmin = None
    xmax = None
    ymin = None
    ymax = None
    rects = None
    circs = None
    lines = None
    bg=None
    appends=None
    def __init__(self):
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self.rects = []
        self.circs = []
        self.lines = []
        self.bg="white"
        self.appends = []
    def setBG(self,bg):
        self.bg=bg
    def addAppend(self,append):
        self.appends.append(append)
    def addRect(self,x,y,w,h,c):
        self.rects.append({"x":x,"y":y,"w":w,"h":h,"c":c})
        self.xmin = min(self.xmin,x) if self.xmin is not None else x
        self.ymin = min(self.ymin,y) if self.ymin is not None else y
        self.xmax = max(self.xmax,x+w) if self.xmax is not None else x+w
        self.ymax = max(self.ymax,y+h) if self.ymax is not None else y+h
    def addCirc(self,x,y,r,c):
        self.circs.append({"x":x,"y":y,"r":r,"c":c})
        self.xmin = min(self.xmin,x-r) if self.xmin is not None else x-r
        self.ymin = min(self.ymin,y-r) if self.ymin is not None else y-r
        self.xmax = max(self.xmax,x+r) if self.xmax is not None else x+r
        self.ymax = max(self.ymax,y+r) if self.ymax is not None else y+r
    def addLine(self,x1,y1,x2,y2,t,c,extra=None):
        if extra is None:
            extra = ""
        self.lines.append({"x1":x1,"y1":y1,"x2":x2,"y2":y2,"t":t,"c":c,"extra":extra})
        self.xmin = min(self.xmin,min(x1,x2)) if self.xmin is not None else min(x1,x2)
        self.ymin = min(self.ymin,min(y1,y2)) if self.ymin is not None else min(y1,y2)
        self.xmax = max(self.xmax,max(x1,x2)) if self.xmax is not None else max(x1,x2)
        self.ymax = max(self.ymax,max(y1,y2)) if self.ymax is not None else max(y1,y2)
    def flatten(self):
        s= '<svg width="{0}" height="{1}"><rect x="0" y="0" width="{0}" height="{1}" fill="{2}"></rect><g transform="translate({3} {4})">\n'.format(self.xmax-self.xmin,self.ymax-self.ymin,self.bg,-self.xmin,-self.ymin)
        for r in self.rects:
            s+='<rect x="{}" y="{}" width="{}" height="{}" fill="{}"></rect>\n'.format(r['x'],r['y'],r['w'],r['h'],r['c'])
        for r in self.circs:
            s+='<circle cx="{}" cy="{}" r="{}" fill="{}"></circle>\n'.format(r['x'],r['y'],r['r'],r['c'])
        for r in self.lines:
            s+='<line x1="{}" y1="{}" x2="{}" y2="{}" stroke-width="{}" stroke="{}" stroke-linecap="round" {}/>'.format(r['x1'],r['y1'],r['x2'],r['y2'],r['t'],r['c'],r['extra'])
        s+="</g>"
        for a in self.appends:
            s+=a+"\n"
        s+="</svg>"
        return s


def runTrack(p,a,b,dt,ts,skewR=1,skewP=1,skewS=1): #replicator
    p = copy(p)
    ps = []
    ps.append(copy(p))
    for i in range(ts):
        p[0] = p[0]+dt*p[0]*(         0*p[0]+skewP*(-b)*p[1]+   skewS*a*p[2])
        p[1] = p[1]+dt*p[1]*(   skewR*a*p[0]+         0*p[1]+skewS*(-b)*p[2])
        p[2] = p[2]+dt*p[2]*(skewR*(-b)*p[0]+   skewP*a*p[1]+         0*p[2])
        sump = p[0]+p[1]+p[2]
        p[0] = p[0]/sump
        p[1] = p[1]/sump
        p[2] = p[2]/sump

        if p[0]<=0:
            break
        if p[1]<=0:
            break
        if p[2]<=0:
            break
        ps.append(copy(p))
    return ps

def runTrack2(p,a,b,dt,ts,skewR=1,skewP=1,skewS=1,epsilon=1): #smoothed logit
    p = copy(p)
    ps = []
    ps.append(copy(p))
    for i in range(ts):
        d0 = math.exp((         0*p[0]+skewP*(-b)*p[1]+   skewS*a*p[2])/epsilon)
        d1 = math.exp((   skewR*a*p[0]+         0*p[1]+skewS*(-b)*p[2])/epsilon)
        d2 = math.exp((skewR*(-b)*p[0]+   skewP*a*p[1]+         0*p[2])/epsilon)
        ds = d0+d1+d2
        p[0] = p[0]+dt*(d0/ds)
        p[1] = p[1]+dt*(d1/ds)
        p[2] = p[2]+dt*(d2/ds)
        sump = p[0]+p[1]+p[2]
        p[0] = p[0]/sump
        p[1] = p[1]/sump
        p[2] = p[2]/sump
        if p[0]<=0:
            break
        if p[1]<=0:
            break
        if p[2]<=0:
            break
        ps.append(copy(p))
    return ps

def runTrack3(p,a,b,dt,ts,skewR=1,skewP=1,skewS=1): #best response
    p = copy(p)
    ps = []
    ps.append(copy(p))
    for i in range(ts):
        d0 = (         0*p[0]+skewP*(-b)*p[1]+   skewS*a*p[2])
        d1 = (   skewR*a*p[0]+         0*p[1]+skewS*(-b)*p[2])
        d2 = (skewR*(-b)*p[0]+   skewP*a*p[1]+         0*p[2])
        ds = max(max(d0,d1),d2)
        d0 = 1 if d0==ds else 0
        d1 = 1 if d1==ds else 0
        d2 = 1 if d2==ds else 0
        p[0] = p[0]+dt*(d0)
        p[1] = p[1]+dt*(d1)
        p[2] = p[2]+dt*(d2)
        sump = p[0]+p[1]+p[2]
        p[0] = p[0]/sump
        p[1] = p[1]/sump
        p[2] = p[2]/sump
        if p[0]<=0:
            break
        if p[1]<=0:
            break
        if p[2]<=0:
            break
        ps.append(copy(p))
    return ps

def runTrack4(p,a,b,dt,ts,skewR=1,skewP=1,skewS=1): #best response with function time-step
    p = copy(p)
    ps = []
    ps.append(copy(p))
    for i in range(ts):
        d0 = (         0*p[0]+skewP*(-b)*p[1]+   skewS*a*p[2])
        d1 = (   skewR*a*p[0]+         0*p[1]+skewS*(-b)*p[2])
        d2 = (skewR*(-b)*p[0]+   skewP*a*p[1]+         0*p[2])
        ds = max(max(d0,d1),d2)
        d0 = 1 if d0==ds else 0
        d1 = 1 if d1==ds else 0
        d2 = 1 if d2==ds else 0
        p[0] = p[0]+dt(i)*(d0)
        p[1] = p[1]+dt(i)*(d1)
        p[2] = p[2]+dt(i)*(d2)
        sump = p[0]+p[1]+p[2]
        p[0] = p[0]/sump
        p[1] = p[1]/sump
        p[2] = p[2]/sump
        if p[0]<=0:
            break
        if p[1]<=0:
            break
        if p[2]<=0:
            break
        ps.append(copy(p))
    return ps


def transformCoords(p,v):
    return v*(p[2]+0.5*p[0]),-0.866*v*p[0]

S = SVG()

v=300

coordR = transformCoords([1,0,0],v)
coordP = transformCoords([0,1,0],v)
coordS = transformCoords([0,0,1],v)
S.addLine(
    coordR[0],
    coordR[1],
    coordP[0],
    coordP[1],
    1,"black")
S.addLine(
    coordP[0],
    coordP[1],
    coordS[0],
    coordS[1],
    1,"black")
S.addLine(
    coordS[0],
    coordS[1],
    coordR[0],
    coordR[1],
    1,"black")
S.addCirc(coordR[0],coordR[1],2,"black")
S.addCirc(coordP[0],coordP[1],2,"black")
S.addCirc(coordS[0],coordS[1],2,"black")
S.addAppend('<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto" markerUnits="strokeWidth" viewBox="0 0 13 13"><path d="M0,0 L0,6 L9,3 z" fill="#000" /></marker></defs>')
S.addAppend('<text x="170" y="15" font-family="Verdana" text-anchor="middle" alignment-baseline="central" font-size="15">R</text>')
S.addAppend('<text x="15" y="295" font-family="Verdana" text-anchor="middle" alignment-baseline="central" font-size="15">P</text>')
S.addAppend('<text x="325" y="295" font-family="Verdana" text-anchor="middle" alignment-baseline="central" font-size="15">S</text>')
S.addCirc(-20,20,0,"blue")
S.addCirc(300+20,-260-20,0,"blue")


def printTrack(ps,v,S,circs=False,linearrows=0):
    if circs:
        for z in ps:
            c = transformCoords(z,v)
            S.addCirc(c[0],c[1],2,"black")
    for i in range(len(ps)-1):
        c0 = transformCoords(ps[i],v)
        c1 = transformCoords(ps[i+1],v)
        if linearrows > 0 and i%linearrows==linearrows-1:
            S.addLine(c0[0],c0[1],c1[0],c1[1],0.7,"black", 'marker-end="url(#arrow)"')
        else:
            S.addLine(c0[0],c0[1],c1[0],c1[1],0.7,"black")



########################################################
#starting_points = [[1,1,1.5+i] for i in range(5)]
#for i in range(len(starting_points)):
#    point_sum = sum(starting_points[i])
#    starting_points[i][0] = starting_points[i][0]/point_sum
#    starting_points[i][1] = starting_points[i][1]/point_sum
#    starting_points[i][2] = starting_points[i][2]/point_sum
#a=0.5
#b=0.5
#dt = 0.02
#
#for point in starting_points:
#    printTrack(runTrack(point,a,b,dt,1400),v,S,False,300)
#    pass
#
#f = open("z.svg","w")
#f.write(S.flatten())
#f.close()
#########################################################


#########################################################
#point = [0.25,0.5,0.25]
#a=0.5
#b=0.66
#
#printTrack(runTrack(point,a,b,0.3,1400,skewP=0.4),v,S,False,100)
##printTrack(runTrack(point,a,b,2.13,100,skewR=1.5),v,S,True,0)
#
#f = open("z2.svg","w")
#f.write(S.flatten())
#f.close()
#########################################################


#########################################################
#point = [0.8,0.1,0.1]
#skewP=0.3
#
#a=0.5
#b=0.1
#printTrack(runTrack2(point,a,b,0.01,900,skewP=skewP,epsilon=0.01),v,S,False,0)
#printTrack(runTrack2(point,a,b,0.01,900,skewP=skewP,epsilon=0.05),v,S,False,0)
#printTrack(runTrack2(point,a,b,0.01,900,skewP=skewP,epsilon=0.10),v,S,False,0)
#printTrack(runTrack2(point,a,b,0.01,900,skewP=skewP,epsilon=0.15),v,S,False,0)
#printTrack(runTrack2(point,a,b,0.01,900,skewP=skewP,epsilon=0.20),v,S,False,0)
#printTrack(runTrack2(point,a,b,0.01,900,skewP=skewP,epsilon=0.25),v,S,False,0)
#printTrack(runTrack3(point,a,b,0.001,3000,skewP=skewP),v,S,False,0)
#
#point = [0.6,0.2,0.2]
#a=0.5
#b=0.48
#printTrack(runTrack(point,a,b,0.1,2000),v,S,False,0)
#printTrack(runTrack(point,a,b,2.1,2000),v,S,True,0)
#
#f = open("z2.svg","w")
#f.write(S.flatten())
#f.close()
#########################################################


#########################################################
#
#a=0.5
#b=0.1
#point = [0.6,0.2,0.2]
#printTrack(runTrack2(point,a,b,0.001,3000,epsilon=0.05),v,S,False,0)
#point = [0.58,0.21,0.21]
#printTrack(runTrack2(point,a,b,0.2,50,epsilon=0.05),v,S,False,0)
#point = [0.56,0.22,0.22]
#printTrack(runTrack(point,a,b,0.2,50),v,S,False,0)
#
#
#f = open("z2.svg","w")
#f.write(S.flatten())
#f.close()
##########################################################


#########################################################

a=0.5
b=0.1
point = [0.6,0.2,0.2]
printTrack(runTrack3(point,a,b,0.4,50),v,S,False,0)
point = [0.58,0.21,0.21]
printTrack(runTrack4(point,a,b,lambda x:0.4/(x+2),50),v,S,False,0)


f = open("z2.svg","w")
f.write(S.flatten())
f.close()
#########################################################



