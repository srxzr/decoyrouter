__author__ = 'milad'

import myDB
import operator
import matplotlib.pyplot as plt
import random
import game

import cPickle as pickle
import math
import signal
import numpy as np


def handler(signal, frame):
    print 'signal'
    raise ArithmeticError()


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


def select_random(dests, country, cost, properties, min_cone, excludes):
    dec = []
    proten = []
    for i in dests:
        sel = i[0]
        if properties[str(sel)]['Country'] != country and int(
                str(properties[str(sel)]['#AS']).replace(',', '')) >= min_cone and not excludes.has_key(str(sel)):
            proten.append(sel)
    np.random.shuffle(proten)
    sel_cost = 0
    sels = []
    tryies = 1000
    for i in proten:
        i = str(i)
        i_cost = game.deployCostFucntion (properties[i], country)
        if i_cost + sel_cost <= cost:
            sels.append(i)
            sel_cost += i_cost
        if sel_cost > cost:
            tryies -= 1
            if tryies < 0:
                return sels
    return sels


def select_aggresive(dest, country, cost, properties, excludes):
    i = 0
    dec = []
    tries = 1000
    sel_cost = 0
    while i < len(dest):
        if properties[str(dest[i][0])]['Country'] != country and not excludes.has_key(str(dest[i][0])):
            q = str(dest[i][0])
            i_cost = game.deployCostFucntion(properties[q], country)
            if i_cost + sel_cost <= cost:
                dec.append(q)
                sel_cost += i_cost
            if sel_cost > cost:
                tries -= 1
                if tries < 0:
                    return dec

        i += 1
    return dec


def evalute_options(dests, sources, soc, properties):
    pass


def computeImportance(routes, sources, costs):
    contents = {}
    ASes = {}
    Revs = {}
    counts=0
    for i in sources:
        if not routes.has_key(i):
            continue
        dests = routes[i]
        for d in dests:
            if True:#costs[d]['Country'] == 'US':
                ASes.setdefault(d,{})

                if len(routes[i][d].selectedpath)<1:
                    continue
                for ass in routes[i][d].selectedpath[0]:
                    #print ass,routes[i][d].selectedpath
                    ASes[d].setdefault(ass, []).append(i)
                    Revs.setdefault(str(ass), {}).setdefault(str(d), []).append(str(i))
                '''for route in routes[i][d].alternativepaths:
                    for ass in route[0]:

                        ASes[d].setdefault(ass, []).append(i)
                        Revs.setdefault(str(ass), {}).setdefault(str(d), []).append(str(i))'''

    print len(Revs)
    return Revs


def decoyGameAction(routers, sources, country, properties, budget, excludes,denom):
    #dec= pickle.load(open('game_2e7.pickle'))
    #return dec

    imps=computeImportance(routers,sources,properties)

    print 'decoy: IMPS COMPUTED'
    dec=game.decoyResonse(imps.keys(),country,properties,budget,excludes,imps,denom)
    #pickle.dump(dec, open('ress/game_naughty2_%d.pickle'%budget,'wb'))
    print 'decoy: decoys deployed',dec
    return dec


def compute(dests, routes, ascountry, country, sources, percentage):
    results = {}
    sorted_dsts = dests
    selection_method_str = 'random'
    costs = pickle.load(open('../Datasets/AS_Cost.pickle', 'rb'))
    soc = int(len(sorted_dsts) * float(percentage) / 100.0)
    dec = select_random(sorted_dsts, country, soc, costs, 0)
    results['Decoys'] = dec

    rebuild = {}
    needrebuild = {}

    oks = {}
    print dec
    com = 0
    print 'start for %f percent with %d seleced' % (percentage, soc)
    lastDests = {}
    for i in sources:
        paths = routes.getRouteForSource(i)
        com += 1
        print 'computeing %d of %d' % (com, len(sources))
        # print len(paths)
        for k in paths:
            if k in sources:
                continue

            if lastDests.get(k, 0) == -2:
                # print 'escape'
                continue
            # print k
            route, type = routes.computeRAD(i, k, dec, sources)

            lastDests[k] = type

            if type >= 0:
                rebuild.setdefault(k, []).append(route)

                oks[k] = 1
            else:
                needrebuild.setdefault(i, []).append(k)

            # print route,type
            results.setdefault(i, {})[k] = {'route': route, 'type': type}

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
                results.setdefault(i, {})[k] = {'route': best, 'type': -1}

                continue
            best = best_paths[k]

            results.setdefault(i, {})[k] = {'route': best, 'type': -2}

    results['unreachable'] = float(len(oks)) / float(len(dests))

    pickle.dump(results, open('../results/results-%f-%s.pickle' % (percentage, selection_method_str), 'wb'))
    print 'done percentage %f' % percentage, float(len(oks)) / float(len(dests))
    return



def censorGameAction(routes,sources,country,costs,decoys,sites,routemanager,denom):
    game.computeAllReroute(sources,routemanager,decoys)
    dic={}

    '''for s in routes:
        dic.setdefault(s,{})
        for d in routes[s]:
            dic[s][d]=[routes[s][d].radpath,routes[s][d].routetype]'''

    for source in routes:
        for dest in routes[source]:
            game.gameCensorDecide(source,dest,costs,sites,routemanager,denom)


def analysResult(routes,costs,dec,excludes,denom,sites):
    results={'NVF':[],'Unreachable':[],'Decoy':[],'Less Preferred':[],'Not changed':[],'Increased Path':[]}
    decoyutility=0
    censorutility=0
    tt={}
    newtransit=0
    increasedLength=0

    cenmetr=0.0
    total=0.0

    nroutes=0

    vv=0

    s_d= denom['s']

    decoys_util=0
    c1_util=0
    c2_util=0
    c3_util=0
    c4_util=0
    c5_util=0
    c6_util={}

    for s in routes:
        for d in routes[s] :
            #if d in excludes:
            #    continue
            nroutes+=1

            ssize=(float(str(costs[s].get('#IP','0')).replace(',','')) +1)*( float(str(costs[d].get('#IP','0')).replace(',',''))+1)


            if routes[s][d].isBGP:
                if routes[s][d].routetype!=0:
                    results['Decoy'].append((s,d))
                    cenmetr-=(float(str(costs[s].get('#IP','0')).replace(',','')) +1)*( float(str(costs[d].get('#IP','0')).replace(',',''))+1)
                    decoyutility+=( float(str(costs[s].get('#IP','0')).replace(',','')) )*( float(str(costs[d].get('#IP','0')).replace(',','')) )


                    decoys_util+=ssize
                else:
                    results['Not changed'].append((s,d))

            else:
                if routes[s][d].routetype==1:
                    results['Less Preferred'].append((s,d))
                    c5_util+=ssize

                    vv+=(float(str(costs[s].get('#IP','0')).replace(',','')) +1)*( float(str(costs[d].get('#IP','0')).replace(',',''))+1)
                if routes[s][d].routetype==2:
                    vv+=(float(str(costs[s].get('#IP','0')).replace(',','')) +1)*( float(str(costs[d].get('#IP','0')).replace(',',''))+1)
                    results['NVF'].append((s,d))
                    c4_util+=ssize
                    if  not 'Tr' in costs[str(routes[s][d].selectedpath[0][0])].get('Type',''):
                        newtransit+=1
                        tt[str(routes[s][d].selectedpath[0][0])]=1
                        c6_util[str(routes[s][d].selectedpath[0][0])]=1
                    if len(routes[s][d].selectedpath)>1 and  len(routes[s][d].selectedpath[0])==len(routes[s][d].bestpath[0]):
                        results['Increased Path'].append((s,d))
                        c3_util+=ssize


                if routes[s][d].routetype==-1:
                    results['Unreachable'].append((s,d))
                    c2_util+=(float( sites.get(str(d),1)))
                    c1_util+=ssize
                    total-=(float(str(costs[s].get('#IP','0')).replace(',','')) +1)*( float(str(costs[d].get('#IP','0')).replace(',',''))+1)
                    cenmetr-=(float(str(costs[s].get('#IP','0')).replace(',','')) +1)*( float(str(costs[d].get('#IP','0')).replace(',',''))+1)

                if len(routes[s][d].selectedpath)>1 and  len(routes[s][d].selectedpath[0])>len(routes[s][d].bestpath[0]):
                    results['Increased Path'].append((s,d))

                    increasedLength+=1
    colors=['yellowgreen','gold','lightskyblue','lightcoral','gray']
    #print results
    #plt.ioff()
    #plt.pie([len(results[i]) for i in results],labels=[i for i in results],colors=colors,shadow=True,startangle=90,explode=(0,0,0.1,0,0),autopct='%1.1f%%')
    #plt.show()

    x= {i:len(results[i]) for i in results}
    for i in results:
        x[i+'_frac']=float(len(results[i]))/float(nroutes)
    x['decoyutility']=decoyutility
    x['Transit']=newtransit
    x['ASTransit']=tt
    x['increasedLength']=increasedLength
    x['#decoys']=len(dec)

    x['c1']=float(c1_util)/s_d
    x['c2']=float(c2_util)/denom['sites']
    x['c3']=float(c3_util)/s_d
    x['c4']=float(c4_util)/s_d
    x['c5']=float(c5_util)/s_d
    x['c6']=float(len(c6_util))/denom['trans']
    x['decoy_ben']=float(decoys_util)/s_d
    print x

    return x



def hasDecoy(r,decoys,debug=False):
        for i in r[0]:
            if decoys.has_key(str(i)):
                if debug:
                    print i,
                return True
        return False


def computeGame():
    pass
def computeDecoyUtility(routes,decoys,costs,debug,rm):
    utility =0
    for s in routes:
        for d in routes[s] :
            if len(routes[s][d].selectedpath)<2:
                continue
            if hasDecoy( routes[s][d].selectedpath,decoys):
                if routes[s][d].routetype==0 and debug:
                    print routes[s][d].selectedpath ,routes[s][d].routetype , routes[s][d].isBGP,( float(str(costs[s].get('#IP','0')).replace(',','')) )*( float(str(costs[d].get('#IP','0')).replace(',','')) )
                    hasDecoy(routes[s][d].selectedpath,decoys,True)
                    print rm.computeRAD(s, d, decoys)
                    print rm.hasDecoy(routes[s][d].selectedpath,decoys)
                    print hasDecoy(routes[s][d].bestpath,decoys,True)

                utility+=( float(str(costs[s].get('#IP','0')).replace(',','')) )*( float(str(costs[d].get('#IP','0')).replace(',','')) )
    return utility


def computeTheDenoms(routes,costs,sites,sources,rings):
    s_d=0
    ring_d=0
    sites_d=0

    for s in routes :
        for i in sites:
            sites_d+=sites[i]
        for d in routes[s]:
            if d in rings:
                ring_d+=( float(str(costs[s].get('#IP','0')).replace(',','')) )*( float(str(costs[d].get('#IP','0')).replace(',','')) )
            s_d+=( float(str(costs[s].get('#IP','0')).replace(',','')) )*( float(str(costs[d].get('#IP','0')).replace(',','')) )


    trans=0
    for s in sources:
        if   'Tr' in costs.get(str(s),{}).get('Type',''):
            trans+=1


    denoms = {'sites':sites_d,'s':s_d,'trans':trans}
    print denoms
    print 'denoms computerd'
    print float(ring_d)/float(s_d)

    return denoms



def experiment(routes,dests, sources,country, excludes,costs,sites,rounds,budget):
    reload(game)
    signal.signal(signal.SIGINT, handler)
    sources=sources['Country2ASN'][country]
    decoy_max_costs=budget
    roundcount=0
    decutility=[]
    ress={}
    r=0

    denom=computeTheDenoms(routes.routes,costs,sites,sources,rings=excludes)
    while r<rounds:
        r+=1

        signal.signal(signal.SIGINT, handler)


        if roundcount>-1:
            dec=decoyGameAction(routes.routes,sources,country,costs,decoy_max_costs,excludes,denom)
            f=open('ress/decoys-game-t2-c1e8-%s-%d.pickle'%(country,roundcount),'wb')
            pickle.dump(dec,f)
        else:
            f=open('ress/decoys-game-%s-%d.pickle'%(country,roundcount),'rb')

            dec=pickle.load(f)
        f.close()

        roundcount+=1
        print 'Decoy: Computed '
        #ut=computeDecoyUtility(routes.routes,dec,costs,False,routes)
        #decutility.append(ut)
        #print 'Decoy: Computed DECOY utility= ',ut
        censorGameAction(routes.routes,sources,country,costs,dec,sites,routes,denom)
        #ut=computeDecoyUtility(routes.routes,dec,costs,False,routes)
        #decutility.append(ut)
        #print 'Censor: Computed decoy utility= ',ut

        rez=analysResult(routes.routes,costs,dec,excludes,denom,sites)
        ress.setdefault(decoy_max_costs,[]).append(rez)
        print decutility


        print ress
    return ress






import heapq
import copy

def experiment_sorted(routes,dests, sources,country, excludes,costs,sites,rounds,budget):
    reload(game)
    signal.signal(signal.SIGINT, handler)
    sources=sources['Country2ASN'][country]
    decoy_max_costs=budget
    roundcount=0
    decutility=[]
    ress={}
    r=0
    denom=computeTheDenoms(routes.routes,costs,sites,sources,rings=excludes)

    back=computeImportance(routes.routes,sources,costs)
    for b in [10000000,20000000,40000000,80000000,100000000,200000000]:
        importance=copy.deepcopy(back)
        sorted_ASs=[]
        for ass in importance.keys():

            val=0
            i=(ass)
            if excludes.has_key(i):
                continue
            if costs.get(i,{'Country':''})['Country']==country:
                continue

            for dest in importance.get(i,[]):
                for source in importance[i][dest]:
                    val+= 1




            heapq.heappush(sorted_ASs,(-val,i))
        u=0
        AD={}
        while u < b :
            ass=heapq.heappop(sorted_ASs)[1]
            AD[ass]=1
            u+=game.deployCostFucntion(costs[ass],country)
        censorGameAction(routes.routes,sources,country,costs,AD,sites,routes,denom)


        rez=analysResult(routes.routes,costs,AD,excludes,denom,sites)
        ress.setdefault(b,[]).append(rez)
    return ress




def randselection(costs,dests,min_cone,excludes,country):
    proten = []
    for i in dests:
        sel = i
        if costs[str(sel)]['Country'] != country and int(
                str(costs[str(sel)]['#AS']).replace(',', '')) >= min_cone and not excludes.has_key(str(sel)):
            proten.append(sel)
    print  'Cands:',len(proten)
    print proten
    return proten




def experiment_rand(routes,dests, sources,country, excludes,costs,sites,rounds,budget):
    reload(game)
    signal.signal(signal.SIGINT, handler)
    sources=sources['Country2ASN'][country]
    decoy_max_costs=budget
    roundcount=0
    decutility=[]
    ress={}
    r=0
    denom=computeTheDenoms(routes.routes,costs,sites,sources,rings=excludes)

    back=randselection(costs,dests,10,excludes,country)
    for b in [10000000,20000000,40000000,80000000,100000000,200000000]:
        importance=copy.deepcopy(back)
        pot=importance
        np.random.shuffle(pot)

        u=0
        AD={}
        s=0
        while u < b and s< len(pot) :
            ass=pot[s]
            s+=1
            AD[ass]=1
            #print s, u ,b ,ass
            u+=game.deployCostFucntion(costs[ass],country)

        censorGameAction(routes.routes,sources,country,costs,AD,sites,routes,denom)


        rez=analysResult(routes.routes,costs,AD,excludes,denom,sites)
        ress.setdefault(b,[]).append(rez)
    return ress











if __name__ == '__main__':
    experiment()
