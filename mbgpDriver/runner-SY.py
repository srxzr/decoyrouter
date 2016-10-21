__author__ = 'milad'

import myDB
import operator
import matplotlib.pyplot as plt
import secondgame
import random
import   importlib
import cPickle as pickle
import experiments

import traceback

def  loadInits():

    print 'Init Begin'
    CNsites={}
    cnsf=open('../Datasets/nonSYas.sites')
    for l in cnsf:
        ass,num= l.split(',')
        CNsites[ass]=int(num)
    print 'sites Loaded'
    country='SY'

    destCountry='US'
    p=myDB.RouteParser('../Datasets/routes/SY/all.txt')

    #p.saveRoutes('../Datasets/routes/CN/all.pickle')



    f= open('../Datasets/ASN2Country.pickle','rb')

    ascountry=pickle.load(f)



    rings=pickle.load(open('../Datasets/SY-rings.pickle'))

    print 'Rings Loaded' , len(rings)


    costs= pickle.load(open('../Datasets/AS_Cost.pickle'))

    print 'Costs Loaded'
    us_dest={}
    all_dest={}
    for  c in costs:
        if costs[c]['Country']==destCountry:
            us_dest[c]=1
        all_dest[c]=1
    tdest={'24137':1}
    #p.startParsingDests(us_dest)
    #p.parseForDests(us_dest)
    #p.parseForDests(tdest)
    sources=ascountry['Country2ASN'][country]
    p.startParsing(sources,rings=rings)
    r=p.getRouteManager()


    print 'Routes Loaded'

    dests={}

    '''toremove=[]
    for i in sources:
        paths=r.getRouteForSource(i)
        #print len(paths)
        #if len(paths)<10000:
        #    print 'route not found'
        #    toremove.append(i)
        #    continue

        for k in paths:
            if not k in sources:
                for j in paths[k].bestpath[0]:
                    if not j in sources:



                        dests.setdefault(j,[0])[0]+=1
    fi= open('../Datasets/routes/CN/dests.pickle','w')

    dests=pickle.dump(dests,fi,-1)
    fi.close()
    '''

    print 'Dests are seted num Dests',len(us_dest)

    return all_dest,r,ascountry,country,rings,costs,CNsites




def run():
    flag= True
    dests,routes,ascountry,country,rings,costs,sites=loadInits()
    #pickle.dump((dests,routes,ascountry,country,rings,costs,sites),open('ff','w'))
    #dests,routes,ascountry,country,rings,costs,sites=pickle.load(open('ff'))
    #raise
    #dests,routes,ascountry,country,rings,costs,sites=pickle.load(open('ff'))
    while flag:
        try:
            reload (experiments)
            reload (secondgame)
            reload(myDB)
            #secondgame.experiment(routes,dests,ascountry,country,rings,costs,sites)
            #experiments.experiment(routes,dests,ascountry,country,rings,costs,sites)
            experiments.experiment_rand(routes,dests,ascountry,country,rings,costs,sites,10,20)
        except Exception as E:
            print E
            print E.message
            traceback.print_exc()


        y=raw_input('Rerun?')
        if y!='y':
            flag=False






if __name__=='__main__':
    run()