# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:49:02 2015

@author: admin
"""

import os, datetime, time
import ConvertFiles
import sqlite3
import readHdf5

def massConversion():
    path=r"D:"+os.sep+"DATA"+os.sep+"Acquired_data"
#    listFiles=['00823_Data']
    
    iteration=range(10,46)
    listeFiles=['01078_Data']
   # for i in iteration:
  #      listeFiles.append('010'+str(i)+'_Data')
#    for file in os.listdir(path):
#        if file.endswith(".tdms"):
#            listeFiles.append(file[0:-5])



    #conn=sqlite3.connect('ishtar')
    #curs=conn.cursor()
    #tblcmd='create table shots (shotnbr int(6),file char(40))'
    #curs.execute(tblcmd)
    #conn.commit()
   
    for x in listeFiles:
        print x
        ConvertFiles.convert_tdms(path,x,False)
#
#    for x in listFiles2:
   
class Environment():
    
    def __init__(self):
        self.path=r"D:"+os.sep+"DATA"+os.sep+"Acquired_data"   

def addDate():
    path=r"D:"+os.sep+"DATA"+os.sep+"Acquired_data"
    env=Environment()
    listeFiles=[]    
    for file in os.listdir(path):
        if file.endswith(".h5"):
            listeFiles.append(file[0:-3])
    for file in listeFiles:
            try:
                timei=time.ctime(os.path.getmtime(path+os.sep+file+'.tdms'))
                readHdf5.saveAttr(file,'date',timei,env)
            except:
                print file+'.tdms not found'

def addMagneticField():
    path=r"D:"+os.sep+"DATA"+os.sep+"Acquired_data"
    env=Environment()
    listeFiles=[]    
    for file in os.listdir(path):
        if file.endswith(".h5"):
            listeFiles.append(file[0:-3])
    for file in listeFiles:
            try:
                readHdf5.saveAttr(file,'date',timei,env)
            except:
                print file+'.tdms not found'

def addWincc():
    path=r"D:"+os.sep+"DATA"+os.sep+"Acquired_data"
    env=Environment()
    listeFiles=[]    
    for file in os.listdir(path):
        #print file[0:2]
        if file.endswith(".csv") and file[0:2]=='Is':
            #listeFiles.append(file[0:-3])
            inputfile=open(path+os.sep+file)
            #inputfile.next()
            print inputfile.readline()
            #timei=datetime.datetime.strptime(inputfile.readline()[13:-1],'%d.%m.%Y %H:%M:%S')
            timei=inputfile.readline()[13:-1]        
            print timei
            h5file='0'+file[7:-4]+'_Data'
            print h5file
            readHdf5.saveAttr(h5file,'date',timei,env)
        
        
if __name__=='__main__':
    #massConversion()
    #addMagneticField()
    #addWincc()