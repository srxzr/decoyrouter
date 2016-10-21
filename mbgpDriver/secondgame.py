__author__ = 'milad'

import signal
import cPickle as pickle
import game
import experiments
import redis

import numpy as np
import ASgame
import math
import multiprocessing
from multiprocessing.managers import BaseManager
def handler(signal, frame):
    print 'signal'
    raise ArithmeticError()

def gameDecide(Gamma , properties,country,asnum,decoys,routes,prob,sites,denoms,routermanager,addedvalues):
    costdeploy=ASgame.deployCostFucntion(properties[asnum],country)
    utilitynotdeploy,benefitdeploy,un2= ASgame.benefitDeploy(properties,country,Gamma,decoys,routes,asnum,sites,denoms,routermanager)

    #costdeploy=1
    utilitynotdeploy+=addedvalues.get(str(asnum),0.0)
    utilitydeploy= benefitdeploy #- costdeploy




    if utilitydeploy> utilitynotdeploy:
        return True

    if np.random.random() < prob:
        return True

    return False



def gameDecide_par(Gamma , properties,country,asnum,decoys,routes,prob,sites,denoms,routermanager,addedvalues):
    Rad=redis.Redis()
    g=Rad.lrange(str(asnum),0,-1)
    gamma=[]
    for gp in g :
        gamma.append(pickle.loads(gp))
    Gamma=gamma
    costdeploy=ASgame.deployCostFucntion(properties[asnum],country)
    utilitynotdeploy,benefitdeploy,un2= ASgame.benefitDeploy(properties,country,Gamma,decoys,False,asnum,False,False,False)

    #costdeploy=1
    utilitynotdeploy+=addedvalues.get(str(asnum),0.0)
    utilitydeploy= benefitdeploy #- costdeploy




    if utilitydeploy> utilitynotdeploy:
        return True

    if np.random.random() < prob:
        return True

    return False







def computeGamma_inmemory(routes,sources,excludes,properties,country,decoys):
    Red= redis.Redis('localhost')

    contents = {}
    ASes = {}
    Gamma={}
    Revs = {}
    counts=0
    sourcemap={}
    addedValue={}


    for s in sources :
        sourcemap[int(s)]=1
    for i in sources:
        if not routes.has_key(i):
            continue
        dests = routes[i]
        for d in dests:




            if len(routes[i][d].selectedpath)<2:
                continue

            '''for ass in routes[i][d].selectedpath[0]:
                #print ass
                #print ass,routes[i][d].selectedpath
                if  sourcemap.has_key(ass )  or excludes.has_key(str(ass)):

                    continue

                Gamma.setdefault(str(ass), []).append((i,d))'''
            nobest=True
            for route in routes[i][d].alternativepaths:
                for ass in route[0]:
                    if d in excludes:
                        continue
                    if  sourcemap.has_key(ass )  or excludes.has_key(str(ass)):
                        continue
                    if route ==routes[i][d].selectedpath:
                        nobest=False

                        #Gamma.setdefault(str(ass), []).append((i,d,1,route))
                        Gamma[str(ass)]=1
                        Red.rpush(str(ass),pickle.dumps((i,d,1,route)))

                    else:
                        if  (routes[i][d].routetype==-1):
                            decid,myid,moredecoy=ASgame.whereHasDecoy(route,int(ass),decoys)
                            if (decid== myid) and (not moredecoy) and (routes[i][d].routetype==-1):
                                addedValue.setdefault(str(ass),0)
                                addedValue[str(ass)]+=ASgame.regularbenefit(properties,country,i,d,False,False)
                        #Gamma.setdefault(str(ass), []).append((i,d,2,route))

                    #ASes[d].setdefault(ass, []).append(i)
                    #Revs.setdefault(str(ass), {}).setdefault(str(d), []).append(str(i))
            if nobest:
                for ass in routes[i][d].selectedpath[0]:
                    #print ass
                    #print ass,routes[i][d].selectedpath
                    if  sourcemap.has_key(ass )  or excludes.has_key(str(ass)):

                        continue

                    #Gamma.setdefault(str(ass), []).append((i,d,1,routes[i][d].selectedpath))
                    Red.rpush(str(ass),pickle.dumps((i,d,1,routes[i][d].selectedpath)))
                    Gamma[str(ass)]=1

    print len(Gamma)
    return Gamma, addedValue











def computeGamma(routes,sources,excludes,properties,country,decoys):
    contents = {}
    ASes = {}
    Gamma={}
    Revs = {}
    counts=0
    sourcemap={}
    addedValue={}


    for s in sources :
        sourcemap[int(s)]=1
    for i in sources:
        if not routes.has_key(i):
            continue
        dests = routes[i]
        for d in dests:




            if len(routes[i][d].selectedpath)<2:
                continue

            '''for ass in routes[i][d].selectedpath[0]:
                #print ass
                #print ass,routes[i][d].selectedpath
                if  sourcemap.has_key(ass )  or excludes.has_key(str(ass)):

                    continue

                Gamma.setdefault(str(ass), []).append((i,d))'''
            nobest=True
            for route in routes[i][d].alternativepaths:
                for ass in route[0]:
                    if d in excludes:
                        continue
                    if  sourcemap.has_key(ass )  or excludes.has_key(str(ass)):
                        continue
                    if route ==routes[i][d].selectedpath:
                        nobest=False

                        Gamma.setdefault(str(ass), []).append((i,d,1,route))

                    else:
                        if  (routes[i][d].routetype==-1):
                            decid,myid,moredecoy=ASgame.whereHasDecoy(route,int(ass),decoys)
                            if (decid== myid) and (not moredecoy) and (routes[i][d].routetype==-1):
                                addedValue.setdefault(str(ass),0)
                                addedValue[str(ass)]+=ASgame.regularbenefit(properties,country,i,d,False,False)
                        #Gamma.setdefault(str(ass), []).append((i,d,2,route))

                    #ASes[d].setdefault(ass, []).append(i)
                    #Revs.setdefault(str(ass), {}).setdefault(str(d), []).append(str(i))
            if nobest:
                for ass in routes[i][d].selectedpath[0]:
                    #print ass
                    #print ass,routes[i][d].selectedpath
                    if  sourcemap.has_key(ass )  or excludes.has_key(str(ass)):

                        continue

                    Gamma.setdefault(str(ass), []).append((i,d,1,routes[i][d].selectedpath))

    print len(Gamma)
    return Gamma, addedValue


def computeGamma2(routes,sources,excludes):
    contents = {}
    ASes = {}
    Gamma={}
    Revs = {}
    counts=0
    sourcemap={}


    for s in sources :
        sourcemap[int(s)]=1
    for i in sources:
        if not routes.has_key(i):
            continue
        dests = routes[i]
        for d in dests:



            if len(routes[i][d].selectedpath)<2:
                continue

            for ass in routes[i][d].selectedpath[0]:
                #print ass
                #print ass,routes[i][d].selectedpath
                if  sourcemap.has_key(ass )  or excludes.has_key(str(ass)):

                    continue

                Gamma.setdefault(str(ass), []).append((i,d))
            '''for route in routes[i][d].alternativepaths:
                for ass in route[0]:

                    ASes[d].setdefault(ass, []).append(i)
                    Revs.setdefault(str(ass), {}).setdefault(str(d), []).append(str(i))'''

    print len(Gamma)
    return Gamma


def computeGammaStar(routes,sources,excludes):
    contents = {}
    ASes = {}
    Gamma={}
    Revs = {}
    counts=0
    sourcemap={}
    for s in sources :
        sourcemap[int(s)]=1
    for i in sources:
        if not routes.has_key(i):
            continue
        dests = routes[i]
        for d in dests:


            for path in  routes[i][d].alternativepaths:

                for ass in path[0]:
                    #print ass,routes[i][d].selectedpath
                    if  sourcemap.has_key(ass )  or excludes.has_key(ass):

                        continue

                    Gamma.setdefault(str(ass), []).append((i,d))
                '''for route in routes[i][d].alternativepaths:
                    for ass in route[0]:

                        ASes[d].setdefault(ass, []).append(i)
                        Revs.setdefault(str(ass), {}).setdefault(str(d), []).append(str(i))'''

    print 'len Gamma: ',len(Gamma)
    return Gamma


import copy




def runAgents_par(properties,routes,routemanager,excludes,sources,country,decoys,Gammas,prob,sites,denoms,addedvalues):

    decs=copy.deepcopy(decoys)
    mp=multiprocessing.Pool(8)

    asn=0.0
    procs={}
    for ass in Gammas:
        procs[ass]=mp.apply_async(gameDecide_par,args=(Gammas[ass],properties,country,ass,decs,False,prob,False,False,False,addedvalues))
    print 'process created'


    for ass in Gammas:

        if procs[ass].get():

            decs[int(ass)]=1

        elif decs.has_key(int(ass)):
            del decs[int(ass)]
        asn+=1.0
        if int (asn) %10000==0:
            print asn/float(len(Gammas))


    return decs





def runAgents(properties,routes,routemanager,excludes,sources,country,decoys,Gammas,prob,sites,denoms,addedvalues):

    decs=copy.deepcopy(decoys)

    asn=0.0
    for ass in Gammas:

        if gameDecide(Gammas[ass],properties,country,ass,decs,routes,prob,sites,denoms,routemanager,addedvalues):

            decs[int(ass)]=1

        elif decs.has_key(int(ass)):
            del decs[int(ass)]
        asn+=1.0
        if int (asn) %10000==0:
            print asn/float(len(Gammas))


    return decs


def simulateAgents(properties,routes,routemanager,excludes,sources,country,sites,denoms,decoys):

    converged=False
    count=0
    Gammas,addedvalues= computeGamma(routes,sources,excludes,properties,country,decoys)
    print 'Gamma Computed'

    decs={}
    prob=0.0
    common={}

    while not converged:

        newdecs=runAgents(properties,routes,routemanager,excludes,sources,country,decs,Gammas,prob,sites,denoms,addedvalues)
        cou=0
        for d in newdecs:

            if not decs.has_key(d):
                cou+=1
        for d in decs:
            if not newdecs.has_key(d):
                cou+=1
        try:
            print 'Not Matched %f'%(float(cou)/float(len(newdecs)))
        except:
            pass
        prob*=0.5

        if cou==0:
            converged=True
        if count==4:
            common=copy.deepcopy(newdecs)
        kk=common.keys()
        for i in kk:
            if not newdecs.has_key(i):
                del common[i]



        decs=newdecs
        print  'rounde %d num dec %d '%(count,len(decs))
        print 'common %d'%(len(common))
        if count>10:
            return common

        #print decs.keys()



        count+=1
        if count>50:
            converged=True
    return decs



















def experiment(routes,dests, sources,country, excludes,costs,sites):
    sources=sources['Country2ASN'][country]
    decoy_max_costs=20000000
    exmap={}
    reload(ASgame)
    reload(game)
    for i in excludes:
        exmap[str(i)]=1
    roundcount=0
    dec={}
    decs=pickle.load(open('decs_reasonable.pickle'))
    dec=pickle.load(open('decs_reasonable.pickle'))
    converged=False
    check =False
    denom=experiments.computeTheDenoms(routes.routes,costs,sites,sources,excludes)

    base={}
    if check:
        base= pickle.load(open('../t1_common_sa.pickle'))
        dec=base
        experiments.censorGameAction(routes.routes,sources,country,costs,base,sites,routes,denom)
        experiments.analysResult(routes.routes,costs,dec,excludes,denom,sites)

    histroy=[]




    print decs
    while not converged:
        signal.signal(signal.SIGINT, handler)

        newdecs = simulateAgents(costs,routes.routes,routes,exmap,sources,country,sites,denom,dec)


        cou=0
        for d in newdecs:

            if not dec.has_key(d):
                cou+=1
        '''for d in base:
            if not newdecs.has_key(d):
                cou+=1'''
                #print 'Theit'
        try:

            print 'Not Matched %f, %d'%(float(cou)/float(len(newdecs)),cou)
        except:
            pass



        con='n' # raw_input('Conv?')
        if newdecs in histroy or roundcount>0 or float(cou)/float(len(newdecs))<0.5 or con=='y':
            print 'Converged Step1'
            converged=True
            inter={}
            for d in newdecs:
                if dec.has_key(d):
                    inter[d]=1
            newdecs=step3(inter,routes,dests,sources,country,excludes,costs,sites,denom)

            print 'COnvergeeeeeed, Yaaay'
        dec=newdecs
        histroy.append(copy.deepcopy(dec))



        #f=open('decoys-asgame-run-fair-f2-%d.pickle'%roundcount,'wb')
        #pickle.dump(dec,f,-1)
        #dec=pickle.load(f)
        #f.close()
        roundcount+=1
        print newdecs
        print 'Decoy: Computed'
        experiments.censorGameAction(routes.routes,sources,country,costs,dec,sites,routes,denom)
        print 'Censor: Computed'

        experiments.analysResult(routes.routes,costs,dec,excludes,denom,sites)






def step3(intersection,routes,dests, sources,country, excludes,costs,sites,denom):
    dec= intersection
    history=[copy.deepcopy(dec)]

    exmap={}
    reload(ASgame)
    reload(game)
    for i in excludes:
        exmap[str(i)]=1

    experiments.censorGameAction(routes.routes,sources,country,costs,dec,sites,routes,denom)
    while True:
        newdcs =simulateAgents(costs,routes.routes,routes,exmap,sources,country,sites,denom,dec)
        if newdcs in history:
            return dec
        repdec={}
        fl=False
        for d in dec :
            if newdcs.has_key(d):
                repdec[d]=1
            else:
                fl=True
                print 'Shiiit'
        if fl:
            history=[copy.deepcopy(repdec)]
            newdcs=repdec
        else:
            history.append(copy.deepcopy(newdcs))
        print history
        dec=repdec



        experiments.censorGameAction(routes.routes,sources,country,costs,newdcs,sites,routes,denom)



