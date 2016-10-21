__author__ = 'milad'
import cPickle as pickle
import logging
import copy
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )
class Route:
    def __init__(self,source,dest):
        self.source=source
        self.destination= dest
        self.bestpath=[]
        self.alternativepaths=[]
        self.radpath=[]
        self.selectedpath=[]
        self.routetype=0
        self.radpath=[]


    def setbestpath(self,path):
        self.bestpath=path
        self.selectedpath=self.bestpath












    def addpath(self,path):
        self.alternativepaths.append(path)
    def getallpathes(self):
        return self.alternativepaths
class RouteMananger:
    def __init__(self):
        self.routes={}
        self.asrels={}
        self.fillASrels()

    def fillASrels(self):
        asf= open('../Datasets/caida-m.txt','r')
        for l in asf:
            as1 ,  as2 =l.split(' ')[0:2]
            self.asrels.setdefault(as1,{})[as2]=int(l.split(' ')[2])
            self.asrels.setdefault(as2,{})[as1]=-int(l.split(' ')[2])
        asf.close()
    def addRoutes(self,source,dest,route):
        path=self.routes.setdefault(source,{}).setdefault(dest,Route(source,dest))
        path.addpath(route)
    def setBestRoute(self,source,dest,route):
        path=self.routes.setdefault(source,{}).setdefault(dest,Route(source,dest))
        path.setbestpath(route)
    def save(self,path):
        f=open(path,'wb')
        pickle.dump(self.routes,f)
        f.close()
    def getRoutes(self):
        return self.routes
    def getRouteForSource(self,src):
        res= self.routes.get(src,[])
        #logging.debug( str(len(res)))
        return res

    def hasDecoy(self,r,decoys):
        if len(r)<2:
            return False
        for i in r[0]:
            if  decoys.has_key(str(i)):
                return True
        return False
    def compareRAD(self,r1,r2):
        per1=int(r1[1])
        per2=int(r2[1])
        #LOCAL PRE
        if per2>per1:
            return r2
        elif per1>per2:
            return r1

        #SHORTEST
        if len(r2[0])>len(r1[0]):
            return r1
        if len(r2[0])<len(r1[0]):
            return r2
        if r1[0][0]<r2[0][0]:
            return  r1
        return r2









    def computeRAD(self,source,destination,decoys):
        if  not self.routes.has_key(source)  or not self.routes[source].has_key(destination):
            return  [],-1

        route=self.routes[source][destination]
        if not self.hasDecoy(route.bestpath,decoys):
            route.radpath=copy.deepcopy(route.bestpath)
            route.routetype=0
            return route.radpath, 0
        early_selection=[]
        for i in route.alternativepaths:
            if not self.hasDecoy(i,decoys):
                early_selection.append(i)
        if len(early_selection) == 0 :
            route.routetype=-1
            route.radpath=[]
            return [],-1
            best=[]
            for r in relays:
                if  not self.routes.has_key(r)  or not self.routes[r].has_key(destination):
                    continue
                rel= self.routes[r][destination]
                for ass in rel.alternativepaths:
                    if self.hasDecoy(ass,decoys):
                        continue

                    if best==[]:
                        best=ass
                    best= self.compareRAD(best,ass)
            if best == []:
                return [],-2
            return best,2

        best= early_selection[0]
        for i in early_selection:
            best=self.compareRAD(best,i)

        route.radpath=copy.deepcopy(best)
        route.routetype=1
        return best , 1

    def computeRAD_justcompute(self,source,destination,decoys):
        if  not self.routes.has_key(source)  or not self.routes[source].has_key(destination):
            return  [],-1

        route=self.routes[source][destination]
        if not self.hasDecoy(route.bestpath,decoys):
            return route.radpath, 0
        early_selection=[]
        for i in route.alternativepaths:
            if not self.hasDecoy(i,decoys):
                early_selection.append(i)
        if len(early_selection) == 0 :
            return [],-1
            best=[]
            for r in relays:
                if  not self.routes.has_key(r)  or not self.routes[r].has_key(destination):
                    continue
                rel= self.routes[r][destination]
                for ass in rel.alternativepaths:
                    if self.hasDecoy(ass,decoys):
                        continue

                    if best==[]:
                        best=ass
                    best= self.compareRAD(best,ass)
            if best == []:
                return [],-2
            return best,2

        best= early_selection[0]
        for i in early_selection:
            best=self.compareRAD(best,i)

        return best , 1






class RouteParser:
    def __init__(self,path):
        self.rm=RouteMananger()
        self.file= open(path,'r')


    def parseForDests(self,dests):
        source=''
        dest=''
        count=0
        for i in self.file :
            sp= i.replace('\n','').split('\t')

            if len(sp)==1 and len(i)>1:
                source=sp[0]

            elif len(sp)>1:
                pref=sp[2]
                isbest=sp[0][:2]=='*>'
                path=sp[4]
                dest=path.split(' ')[-1]
                if not dest  in dests:
                    continue

                self.rm.addRoutes(source,dest,([ int(ss) for ss in (source+' '+path).split(' ')],pref))

                if isbest:
                    self.rm.setBestRoute(source,dest,([ int(ss) for ss in (source+' '+path).split(' ')],pref))
            count +=1
            if count%1000000==0:
                print count



        self.file.close()
        self.check()

    def startParsing(self,sources,rings):
        source=''
        dest=''
        count=0
        for i in self.file :
            sp= i.replace('\n','').split('\t')

            if len(sp)==1 and len(i)>1:
                source=sp[0]

            elif len(sp)>1:
                pref=sp[2]
                isbest=sp[0][:2]=='*>'
                path=sp[4]
                dest=path.split(' ')[-1]
                if dest in sources or int(dest)  in rings or str(dest) in rings:
                    continue
                self.rm.addRoutes(source,dest,([ int(ss) for ss in (source+' '+path).split(' ')],pref))

                if isbest:
                    self.rm.setBestRoute(source,dest,([ int(ss) for ss in (source+' '+path).split(' ')],pref))
                    #break
            count +=1
            if count%1000000==0:
                #break
                print count



        self.file.close()
        self.check()
    def check(self):
        m=[]
        for i in self.rm.routes:
            m.append(len(self.rm.routes[i]))


        alt=[]
        for i in self.rm.routes:
            avg=0

            for j in self.rm.routes[i]:
                avg += len(self.rm.routes[i][j].alternativepaths)
            avg=float(avg)/float(len(self.rm.routes[i]))
            alt.append(avg)
        alt.sort()

        m.sort()
        print avg

    def saveRoutes(self,path):
        self.rm.save(path)
    def getRouteManager(self):
        return self.rm




import multiprocessing.managers
class MyManager(multiprocessing.managers.BaseManager):
    pass

