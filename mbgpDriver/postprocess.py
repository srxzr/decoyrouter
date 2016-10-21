__author__ = 'milad'


import cPickle as pickle
import  experiments
import operator
import game
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from cycler import  cycler
def postprocess():
    costs=pickle.load(open('../Datasets/AS_Cost.pickle','rb'))



def setAxLinesBW(ax):
    """
    Take each Line2D in the axes, ax, and convert the line style to be
    suitable for black and white viewing.
    """
    MARKERSIZE = 3

    COLORMAP = {
        'm': {'marker': None, 'dash': (None,None)},
        'c': {'marker': None, 'dash': [5,5]},
        'r': {'marker': None, 'dash': [5,3,1,3]},
        'b': {'marker': None, 'dash': [1,3]},
        'k': {'marker': None, 'dash': [5,2,5,2,5,10]},
        'y': {'marker': None, 'dash': [5,3,1,2,1,10]},
        'g': {'marker': 'o', 'dash': (None,None)} #[1,2,1,10]}
        }

    for line in ax.get_lines() + ax.get_legend().get_lines():
        origColor = line.get_color()
        line.set_color('black')
        line.set_dashes(COLORMAP[origColor]['dash'])
        line.set_marker(COLORMAP[origColor]['marker'])
        line.set_markersize(MARKERSIZE)

def setFigLinesBW(fig):
    """
    Take each axes in the figure, and for each line in the axes, make the
    line viewable in black and white.
    """
    for ax in fig.get_axes():
        setAxLinesBW(ax)






def rankCost():
    imps=pickle.load( open('/home/milad/revs_best_v3_us.pickle','r'))
    country='CN'
    costs=pickle.load(open('../Datasets/AS_Cost.pickle','rb'))

    f= open('../Datasets/ASN2Country.pickle','rb')
    ascountry=pickle.load(f)


    dests={}
    sources=[]
    for i in ascountry['ASN2Country']:
        if ascountry['ASN2Country'][i]=='CN':
            sources.append(i)
    fi= open('../Datasets/dests.pickle','r')

    dests=pickle.load(fi)
    fi.close()
    sorted_dsts = sorted(dests.items(), key=operator.itemgetter(1))
    sorted_dsts.reverse()

    rings=pickle.load(open('../Datasets/CN-rings.pickle'))

    def computeCosts_random(n,cost):
        total_costs_random_1=[]
        total_coverage=[]



        sels=experiments.select_random(sorted_dsts,'CN',cost,costs,n,rings)

        coverage=game.naiveCoverage(sels,imps)
        #coverage=0
        pickle.dump(sels,open('sorted_rnd%d.pickle'%n,'wb'))
        print 'Random %d Done'%n
        return coverage


    def computeCosts_sorted(cost):
        total_costs_random_1=[]
        total_coverage=[]


        sels=experiments.select_aggresive(sorted_dsts,'CN',cost,costs,rings)
        cost=0
        '''for i in sels:
            cost+=game.(costs[str(i)],country)'''
        coverage=game.naiveCoverage(sels,imps)
        pickle.dump(sels,open('sorted_sel.pickle','wb'))

        return coverage
    def computeCosts_game(cost):

        '''sels=experiments.(sorted_dsts,'CN',costs,20000000.0,rings)
        #sels=pickle.load(open( 'game_naughty_2e7.pickle','rb'))
        pickle.dump(sels, open('game_naughty_2e7.pickle','wb'))
        sel_cost=0
        total_costs_random_1=[]
        total_coverage=[]
        c_sels=[]
        for i in sels:
            sel_cost+=game.costFucntion(costs[str(i)],country)
            if sel_cost<cost:
                c_sels.append(i)
            else:
                break




        coverage= game.naiveCoverage(c_sels)
        print 'Game %d Done'%cost
        return coverage'''



    res={'Game':{},'Rnd1':{},'Rnd5':{},'Rnd10':{},'Sorted':{}}
    for i in [20000000]:
        #res['Game'][i]=computeCosts_game(i)
        res['Rnd1'][i]=computeCosts_random(1,i)
        res['Rnd5'][i]=computeCosts_random(5,i)
        res['Rnd10'][i]=computeCosts_random(10,i)
        res['Sorted'][i]=computeCosts_sorted(i)

    pickle.dump(res,open('res.pickle','wb'))
    #res=pickle.load(open('../Datasets/compare_greedy.pickle'))
    plt.rc('lines',linewidth=1)





    c=0
    fig= plt.figure()
    ax=fig.add_subplot(111)


    for i in res:
        if len(res[i])==0:
            continue

        ax.plot( np.arange(100000,20000000,100000),[res[i][j] for j in np.arange(100000,20000000,100000)],label=i)
        c+=1



    plt.legend(loc=2,prop={'size':12})
    plt.ylabel('Unreachable')
    plt.xlabel('Cost')
    setFigLinesBW(fig)



    plt.show()


def findInteresting():
    sels=pickle.load(open( 'game_2e7.pickle','rb'))
    costs=pickle.load(open('../Datasets/AS_Cost.pickle','rb'))

    print 'mm'





if __name__=='__main__':
    rankCost()