__author__ = 'milad'
import cPickle as pickle
import math

import myDB


def compareRAD(r1, r2):
    per1 = int(r1[1])
    per2 = int(r2[1])
    # LOCAL PRE
    if per2 > per1:
        return r2
    elif per1 > per2:
        return r1

    # SHORTEST
    if len(r2[0]) > len(r1[0]):
        return r1
    if len(r2[0]) < len(r1[0]):
        return r2
    if r1[0][0] < r2[0][0]:
        return r1
    return r2

def deployCostFucntion(properties,country):


    if properties['Country']==country:
        #print 'hit'
        return 9999999999999999999999
    import_cost=  0.0  if properties.get('import_per','0%')==0  else float ( properties.get('import_per','0%')[:-1])
    export_cost= 0.0 if  properties.get('export_per','0%') == 0 else float ( properties.get('export_per','0%')[:-1])
    size_cost =( float(str(properties.get('#IP','0')).replace(',','')) +1)
    cost= max((import_cost+export_cost)*10,1) *((size_cost)**0.5)
    '''if 'Co' in properties.get('Type',''):
        cost=cost**2
        #print 'Co'
    elif 'En' in properties.get('Type',''):
        cost*=10
        #print 'En'
    else:
        print properties.get('Type','')'''

    return cost+100
import copy
import heapq

def decoyResonse(routers,country,properties,budget,excludes,importance ,denom):
    reachs={}
    dec=[]
    mdec={}
    used_budget=0
    count=0
    print len(routers), len(importance)
    AS_val={}
    sorted_ASs=[]
    if len (routers)==0:
        return mdec


    for ass in routers:

        val=0
        i=(ass)
        if excludes.has_key(i):
            continue
        if mdec.has_key(i):
            continue
        if properties.get(i,{'Country':''})['Country']==country:
            continue

        for dest in importance.get(i,[]):
            for source in importance[i][dest]:
                if reachs.get(source,{}).get(dest)==None :


                    val+= ((int(str(properties[dest].get('#IP','0')).replace(',','')))+1)* ((int(str(properties[source].get('#IP','0')).replace(',','')))+1)


        val2= float(val) / float( deployCostFucntion(properties[i],country))
        AS_val[i]=val2
        heapq.heappush(sorted_ASs,(-val2,i))


    print 'Sorted'



    while used_budget<budget:
        best=''
        bestval=-999999999999999
        count1=0
        count2=0

        while True:

            val=0
            ass=heapq.heappop(sorted_ASs)[1]


            i=(ass)
            if excludes.has_key(i):
                continue
            if mdec.has_key(i):
                continue
            if properties.get(i,{'Country':''})['Country']==country:
                continue




            for dest in importance.get(i,[]):
                for source in importance[i][dest]:
                    if reachs.get(source,{}).get(dest)==None :


                        val+= ((int(str(properties[dest].get('#IP','0')).replace(',','')))+1)* ((int(str(properties[source].get('#IP','0')).replace(',','')))+1)


            val2= float(val) / float( deployCostFucntion(properties[i],country))
            nextone=heapq.nsmallest(1,sorted_ASs)[0]


            sval=-nextone[0]

            if sval<=val2:
                bestval=val2
                best=i
                break
            else:
                #print 'Nextone'
                heapq.heappush(sorted_ASs,(-val2,i))
                #print i , val ,val2 , val2-val



        dec.append(best)
        mdec[best]=1
        used_budget+=deployCostFucntion(properties[best],country)
        #print used_budget, 'selected: ', best, 'len: ',len(dec) , properties[best]

        for dest in importance.get(best,[]):
            for source in importance[best][dest]:
                #print 'setting',source,dest
                reachs.setdefault(source,{}).setdefault(dest,1)
                count2+=1
        #print count1, count2
        count+=1
        if count%10000==0:
            naiveCoverage(dec,importance)

    print 'used:', used_budget, budget

    ddec={}
    for d in  dec:
        ddec[d]=1

    print dec
    return  ddec

def computeAllReroute(sources,routermanager,decoys):
    results = {}
    rebuild = {}
    needrebuild = {}

    oks = {}

    com = 0
    print 'Computing RAD'
    mdec={}
    for i in decoys:
        mdec[str(i)]=1


    lastDests = {}
    for i in routermanager.routes:
        paths = routermanager.getRouteForSource(i)
        com += 1
        # print len(paths)
        for k in paths:
            if k in sources:
                continue

            if lastDests.get(k, 0) == -2:
                print 'escape'
                continue
            # print k
            route, type = routermanager.computeRAD(i, k, mdec)
            routermanager.routes[i][k].routetype=type

            lastDests[k] = type

            if type >= 0:
                rebuild.setdefault(k, []).append(route)

                oks[k] = 1
            else:
                needrebuild.setdefault(i, []).append(k)

            # print route,type


    # print oks
    best_paths = {}

    for k in rebuild:
        best = rebuild[k][0]
        for p in rebuild[k]:
            best = compareRAD(best, p)
        best_paths[k] = best

    for i in needrebuild:
        for k in needrebuild[i]:
            if not rebuild.has_key(k):



                continue
            best = best_paths[k]
            routermanager.routes[i][k].routetype=2
            routermanager.routes[i][k].radpath=copy.deepcopy(best)









    print 'Censor: RAD COMPUTED'

def getLatency(route):
    return 1.0

def gameCensorDecide(source,dest,costs,sites,routermanager,denom):
    bgputil=0
    s_d=float( denom['s'])
    site_d=max(float(denom['sites']),1.0)
    trans_d=max(float(denom['trans']),1.0)
    sizefactor=( float(str(costs[source].get('#IP','0')).replace(',','')) +1)*( float(str(costs[dest].get('#IP','0')).replace(',','')) +1)/s_d
    rbgputil=sizefactor
    bgputil=sizefactor

    alpha=1.0
    rbgputil*=alpha
    bgputil*=alpha
    b1=100.0
    b2=100.0
    b3=100.0 #len
    b4=0.0 # NVF $
    b5=0.0 # pref $
    b6=0.0 # trans $


    c1=sizefactor
    c2=(float( sites.get(str(dest),0)))/float(site_d)




    if routermanager.routes[source][dest].routetype!=0:
        bgputil*=0.0

    if routermanager.routes[source][dest].routetype==-1:
        rbgputil-= b1*c1 + b2*c2



    if routermanager.routes[source][dest].routetype>0:

        rad=routermanager.routes[source][dest].radpath
        bgp=routermanager.routes[source][dest].bestpath
        nvf =0.0
        pathlen= 1 if len(rad[0]) > (len(bgp[0])) else 0

        pref= 1 if  float(bgp[1]) > float(rad[1]) else 0
        trans=0.0



        if routermanager.routes[source][dest].routetype==2:
            nvf=1.0

            pathlen= 1 if (len(rad[0])+1) > (len(bgp[0])) else 0
            if not 'Tr' in costs[str(rad[0][0])].get('Type',''):
                trans=1.0 / trans_d









        #print size , getLatency(rad)/getLatency(bgp) , (float(rad[1])/float(bgp[1])),nvf,float (sites.get(str(dest),1))

        #rbgputil+=  sizefactor*(-1.0*( (  b4*pathlen + b5*nvf +b6*pref +   b7*trans )))
        rbgputil-= sizefactor*( b3* pathlen +  b4*nvf +b5*pref ) + (b6 * trans)



    if bgputil> rbgputil:
        routermanager.routes[source][dest].selectedpath=copy.deepcopy(routermanager.routes[source][dest].bestpath)
        routermanager.routes[source][dest].isBGP=True
    else :

        routermanager.routes[source][dest].selectedpath=copy.deepcopy(routermanager.routes[source][dest].radpath)
        routermanager.routes[source][dest].isBGP=False

def evaluetegameCensorDecide(source,dest,costs,sites,routermanager,denom,decs):
    bgputil=0
    s_d=float( denom['s'])
    site_d=max(float(denom['sites']),1.0)
    trans_d=max(float(denom['trans']),1.0)
    sizefactor=( float(str(costs[source].get('#IP','0')).replace(',','')) +1)*( float(str(costs[dest].get('#IP','0')).replace(',','')) +1)/s_d
    rbgputil=sizefactor
    bgputil=sizefactor

    rad,type=routermanager.computeRAD_justcompute(source, dest, decs)

    alpha=50.0
    rbgputil*=alpha
    bgputil*=alpha
    b1=0.0
    b2=0.0
    b3=0.0 #len
    b4=100.0 # NVF $
    b5=100.0 # pref $
    b6=100.0 # trans $


    c1=sizefactor
    c2=(float( sites.get(str(dest),1)))/float(site_d)



    if type!=0:
        bgputil*=0.0

    if type==-1:
        rbgputil-= b1*c1 + b2*c2



    if type>0:

        bgp=routermanager.routes[source][dest].bestpath
        nvf =0.0
        pathlen= 1 if len(rad[0]) > (len(bgp[0])) else 0

        pref= 1 if  float(bgp[1]) > float(rad[1]) else 0
        trans=0.0



        '''if routermanager.routes[source][dest].routetype==2:
            nvf=1.0

            pathlen= 1 if (len(rad[0])+1) > (len(bgp[0])) else 0
            if not 'Tr' in costs[str(rad[0][0])].get('Type',''):
                trans=1.0 / trans_d'''









        #print size , getLatency(rad)/getLatency(bgp) , (float(rad[1])/float(bgp[1])),nvf,float (sites.get(str(dest),1))

        #rbgputil+=  sizefactor*(-1.0*( (  b4*pathlen + b5*nvf +b6*pref +   b7*trans )))
        rbgputil-= sizefactor*( b3* pathlen +  b4*nvf +b5*pref ) + (b6 * trans)


    #print rbgputil,bgputil



    if bgputil> rbgputil:
        return False
    else :
        return True












class Statics:
    imps=[]#pickle.load( open('/home/milad/revs_best_v3_us.pickle','r'))


def naiveCoverage(dec,imps):
    pairs={}
    mdec={}

    for d in dec :
        mdec[str(d)]=1
    for ass in imps:
        for dest in imps[ass]:
            for source in imps[ass][dest]:
                pairs.setdefault (dest,{}).setdefault(source,1)

                if mdec.has_key(ass):
                    pairs[dest][source]=0
    countUnreach=0
    print 'Cover Done'
    for dest in pairs:
        reachable=False
        for source  in pairs[dest]:
            if pairs[dest][source]==1:
                reachable=True
                break
        if reachable==False:
            countUnreach+=1
    print 'Coverage: %f' % (float(countUnreach)/float(len(pairs)))
    return float(countUnreach)/float(len(pairs))


def censorCost(dec,routes):
    imps=Statics.imps






import time
if __name__=='__main__':
    for i in range(1000):
        t1=time.time()
        imps=Statics.imps
        print time.time()-t1


