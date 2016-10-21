__author__ = 'milad'
import math
import game
costofdeployment= 1000


def deployCostFucntion(properties,country):


    if properties['Country']==country or properties['Country']==country:
        #print 'hit'
        return 999999999999999999999999999999
    import_cost=  0.0  if properties.get('import_per','0%')==0  else float ( properties.get('import_per','0%')[:-1])
    export_cost= 0.0 if  properties.get('export_per','0%') == 0 else float ( properties.get('export_per','0%')[:-1])
    size_cost = math.floor( float(str(properties.get('#IP','0')).replace(',','')) +1)
    try:

        cost= max((import_cost+export_cost)*10,1) *((math.floor(size_cost))**1.0)
    except :
        print size_cost
        raise

    if 'Co' in properties.get('Type',''):
        cost=cost*100
        #print 'Co'
    elif 'En' in properties.get('Type',''):
        cost*=100
        #print 'En'
    '''else:
        print properties.get('Type','')'''

    return (cost+100.0)*2000.0


def whereHasDecoy(r,asn,decoys):


    index=0
    count=0
    decoy=-1
    flag=True
    more=False
    for i in r[0]:
        if asn==i:
            index=count


        if  decoys.has_key(i) and not flag:
            more=True

        if  decoys.has_key(i) and flag:
            decoy=count
            flag =False

        count+=1
    if index ==0 :
        print asn, r, decoys
        raise





    return decoy,index,more









def benefitDeploy(properties,country,gamma,decoys,routes,asn,sites,denoms,routermanager):
    addedFrac=7.0
    regben=0
    decben=0
    reg2=0.0
    for g in gamma:
        s,d,t,route=g
        stockben=regularbenefit(properties,country,s,d,decoys,routes)

        #route= routes[s][d].selectedpath
        decid,myid,moredecoy= whereHasDecoy(route,int(asn),decoys)
        decFrac=1.0+addedFrac
        #if t==1 and game.evaluetegameCensorDecide(s,d,properties,sites,routermanager,denoms,{asn:1}):
        #    decFrac=0.0
            #print 'U R Dead'


        if t==1:
            if decid < 0:
                decben+=stockben*decFrac
                regben+=stockben
                reg2+=stockben
            elif decid < myid:
                decben+=stockben
                regben+=stockben
                reg2+=stockben
            elif decid> myid:
                #print decid,myid,route,asn
                decben+=stockben*decFrac
                regben+=stockben
                reg2+=stockben*decFrac

            elif decid == myid and moredecoy:
                decben+=stockben*decFrac
                regben+=stockben
                reg2+=stockben*decFrac
            elif decid== myid and not moredecoy:
                decben+=stockben*decFrac
                regben+=stockben
                reg2+=stockben
            #regben+=stockben
            #decben+=stockben*decFrac
        else:

            if (decid== myid) and (not moredecoy) and (routes[s][d].routetype==-1):
                #print routes[s][d].routetype
                regben+=stockben


    #print regben, decben
    return regben,decben,reg2





def benefitDeploy_par(properties,country,gamma,decoys,routes,asn,sites,denoms,routermanager):
    addedFrac=10.0
    regben=0
    decben=0
    reg2=0.0
    for g in gamma:
        s,d,t,route=g
        stockben=regularbenefit(properties,country,s,d,decoys,False)

        #route= routes[s][d].selectedpath
        decid,myid,moredecoy= whereHasDecoy(route,int(asn),decoys)
        decFrac=1.0+addedFrac
        #if t==1 and game.evaluetegameCensorDecide(s,d,properties,sites,routermanager,denoms,{asn:1}):
        #    decFrac=0.0
            #print 'U R Dead'


        if t==1:
            if decid < 0:
                decben+=stockben*decFrac
                regben+=stockben
                reg2+=stockben
            elif decid < myid:
                decben+=stockben
                regben+=stockben
                reg2+=stockben
            elif decid> myid:
                #print decid,myid,route,asn
                decben+=stockben*decFrac
                regben+=stockben
                reg2+=stockben*decFrac

            elif decid == myid and moredecoy:
                decben+=stockben*decFrac
                regben+=stockben
                reg2+=stockben*decFrac
            elif decid== myid and not moredecoy:
                decben+=stockben*decFrac
                regben+=stockben
                reg2+=stockben
            #regben+=stockben
            #decben+=stockben*decFrac



    #print regben, decben
    return regben,decben,reg2










def regularbenefit(properties,country,s,d,decoys,routes):
    val=math.floor ((int(str(properties[d].get('#IP','0')).replace(',','')))+1)*math.floor ((int(str(properties[s].get('#IP','0')).replace(',','')))+1)
    return val