__author__ = 'milad'
import cPickle as pickle
def compute():
    print 'Init Begin'
    costs=pickle.load(open('../Datasets/AS_Cost.pickle','rb'))

    print 'Costs Loaded'

    contents={}
    for i in costs:
        if 'Co' in  costs[i]['Type']:
            contents[i]=1
    ASes={}
    Revs={}
    routes= open('../Datasets/all.txt','r')
    count=0
    mc=0
    sources={}
    for l in routes:
        sp= l.replace('\n','').split('\t')

        if len(sp)==1 and len(l)>1:
            source=sp[0]
            sources[source]=1

        elif len(sp)>1:
            pref=sp[2]
            isbest=sp[0][:2]=='*>'
            path=sp[4]
            dest=path.split(' ')[-1]
            if not isbest :
                continue
            if  costs[dest]['Country']=='US':
                ASes.setdefault(dest,{})
                if '21211' in path :
                    mc+=1

                for i in (source+' '+path).split(' '):
                    ASes[dest].setdefault(i,[]).append( source)
                    Revs.setdefault(i,{}).setdefault(dest,[]).append(source)








        count +=1
        if count%1000000==0:
            print count
    print len(ASes)
    routes.close()
    print mc
    pickle.dump(Revs,open('revs_best_v3_us.pickle','wb'))

    print len(sources)



if __name__=='__main__':
    compute()