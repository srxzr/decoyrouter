__author__ = 'milad'
import xmlrpclib
import operator

def findUnreachablePercentage(country,percentage,AS2CO):
    s = xmlrpclib.ServerProxy('http://localhost:8000')

    dests={}
    sources=AS2CO['Country2ASN'][country]
    for i in sources:
        paths=s.getRouteForSource(i)
        print len(paths)

        for k in paths:
            if not k in sources:


                dests.setdefault(k,[0])[0]+=1



    sorted_dsts = sorted(dests.items(), key=operator.itemgetter(1))
    sorted_dsts.reverse()
    soc=(len(sorted_dsts)*percentage/100)
    dec=[]

    i=0
    while len (dec)< soc:

        if not sorted_dsts[i] [0] in sources:
            dec.append(sorted_dsts[i][0])
        i+=1
    oks={}
    for i in sources:
        paths=s.getRouteForSource(i)
        #print len(paths)
        for k in paths:
            if k in sources:
                continue
            for a in paths[k]['alternativepaths']:
                add=True


                for q in dec:
                    if   q in a[0].split(' '):
                        add=False
                        break
                if add:
                    oks[k]=1
                    break
    #print oks

    return float(len(oks))/float(len(dests))



