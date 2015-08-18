# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 14:55:55 2015

@author: ekaterina
"""

import readHdf5
import sys
import os

listeShots=[844, 845, 846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900,901,902,903]
listePosition=[1350, 1300, 1300, 1300, 1350, 1400, 1450, 1430, 1410, 1390, 1390, 1370, 1350, 1350, 1310, 1290, 1290, 1270, 1250, 1250, 1230, 1210, 1190, 1170, 1120, 1070, 1020, 970, 970, 1292, 1292, 1310, 1330, 1350, 1370, 1390, 1410, 1430, 1450, 1290, 1270, 1250, 1230, 1230, 1230, 1210, 1190, 1170, 1150, 1290, 1290, 1290, 1290, 1290]

#listeShots=[925,926,927,928,929,930, 931,932,933,934,935,936,937,938,939,940,941,942,943,944,945,946,947,948,949,950,951,952,953,954,955,983,984,985,986,987,988,989,990,991,992,993,994,995,996,997,998,999]
#listePosition=[1406,1416,1396,1386,1386,1386,1376,1366,1355,1345,1335,1325,1315,1305,1295,1285,1275,1265,1255,1235,1215,1195,1145,1095,1045,995,895,795,695,595,495,1315,1330,1340,1350,1360,1370,1305,1295,1285,1275,1265,1255,1245,1235,1225,1215,1380]

print len(listeShots),len(listePosition)


class Environment():
    
    def __init__(self):
        self.path=r"D:"+os.sep+"ISHTARmay"

def calibr(x):
    slope=(76.-23.)/(400.-1400.)
    return (x-400.)*slope+76.-33
    
listePositionspace=[]
for x in  listePosition:
    listePositionspace.append(calibr(x))

i=0
env=Environment()
while i<len(listeShots):
    fileName='00'+str(listeShots[i])+'_Data'
    print listeShots[i]
    Attrname='position'
    value=listePosition[i]

    readHdf5.saveAttr(fileName,Attrname,value,env)
    Attrname='positionspace'
    value=listePositionspace[i]
    i=i+1

    
    
    