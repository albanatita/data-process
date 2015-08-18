# -*- coding: utf-8 -*-
"""
Created on Wed May 20 11:42:42 2015

@author: admin
"""

import h5py
import os
import numpy as np



def getSignals(fileName,env):
    path=env.path
    hdf5=h5py.File(os.path.join(path,fileName+'.h5'),'r')
    #channel=tdms_file.object('PXI M6251','Lang_U')
    liste=[]    
    hdf5.visit(liste.append)
    liste2=[x for x in liste if isinstance(hdf5[x],h5py.Dataset)]
    print liste2
    hdf5.close()
    return liste2
    
def getAttributes(fileName,env):
    path=env.path
    hdf5=h5py.File(os.path.join(path,fileName+'.h5'),'r')
    #channel=tdms_file.object('PXI M6251','Lang_U')
    liste=[]    
    hdf5.visit(liste.append)
    liste2=[hdf5[x].attrs.keys() for x in liste if isinstance(hdf5[x],h5py.Group)]
    hdf5.close()
    return liste2    
    
def getOverview(fileName,item,env):
    path=env.path
    hdf5=h5py.File(os.path.join(path,fileName+'.h5'),'r')
    if hdf5[item].parent.name=='/S7':
        data=np.array(hdf5[item])[-100:-1]
        time=np.array(hdf5['S7/Time'])[-100:-1]/1000
        sampling=1/(time[1]-time[0])
        
    else:
        data=hdf5[item]
        sampling=hdf5[item].parent.attrs['sampling']
        time=np.linspace(0,len(data)-1,num=len(data))/(sampling)

    return time,data
    hdf5.close()


def getData(fileName,item,env):
    path=env.path
    hdf5=h5py.File(os.path.join(path,fileName+'.h5'),'r')
    par=hdf5[item].parent.name
    if par=='/S7':
        data=np.array(hdf5[item])[-100:-1]
        time=np.array(hdf5[par[1:]+'/Time'])[-100:-1]/1000
        sampling=1/(time[1]-time[0])
    elif par=='/Process':
        data=np.array(hdf5[item])
        time=np.array(hdf5[par[1:]+'/Time'])
        sampling=1/(time[1]-time[0])        
    else:
        data=np.array(hdf5[item])
        sampling=np.abs(hdf5[item].parent.attrs['sampling'])
        time=np.linspace(0,len(data)-1,num=len(data))/(sampling)
    hdf5.close()
    return time,data,sampling

def saveData(fileName,item,data,env):
     path=env.path
     hdf5=h5py.File(os.path.join(path,fileName+'.h5'),'a')   
     group=hdf5['Process']
     try:
         del group[item]
     except:
         pass
     group.create_dataset(item,data=data,compression="gzip")
     hdf5.close()
     return
    
def getDataProcess(fileName,item,env):
     path=env.path
     hdf5=h5py.File(os.path.join(path,fileName+'.h5'),'r')   
 #    group=hdf5['Process']
     
     a=np.array(hdf5[item])
     hdf5.close()
     return a
    

def saveAttr(fileName,attributName,data,env):
     path=env.path
     hdf5=h5py.File(os.path.join(path,fileName+'.h5'),'a')
     group=hdf5['Process']
     group.attrs[attributName]=data
     hdf5.close()
     
def getAttr(fileName,attributName,env):
     path=env.path
     hdf5=h5py.File(os.path.join(path,fileName+'.h5'),'r')
     group=hdf5['Process']
     aa=group.attrs[attributName]
     hdf5.close()
     return aa

def getAttrlist(fileName,env):
     path=env.path
     hdf5=h5py.File(os.path.join(path,fileName+'.h5'),'r')
     group=hdf5['Process']
     string=''
     for x,y in zip(group.attrs.iterkeys(),group.attrs.itervalues()):
         string=string+str(x)+' : '+str(y)+'\n'
     hdf5.close()
     return string
    
         
         
    
def getMultiData(fileName,item1,item2,env):
    path=env.path
    hdf5=h5py.File(os.path.join(path,fileName+'.h5'),'r')
    data1=hdf5[item1]
    data2=hdf5[item2]
    sampling=np.abs(hdf5[item1].parent.attrs['sampling'])
    time=np.linspace(0,len(data1)-1,num=len(data1))/(sampling)
    return data1,data2,time,sampling
    hdf5.close()

def getSummaryData(fileList,env):
    path=env.path
    shot=dict()
    for fileName in fileList:
        shotnumber=int(fileName[0:-5])        
        shot[shotnumber]=[fileName]
        print os.path.join(path,fileName+'.h5')
        hdf5=h5py.File(os.path.join(path,fileName+'.h5'),'r')
        group=hdf5['Process']
        try:
            shot[shotnumber].append(group.attrs['date'])
        except:
            shot[shotnumber].append('')
        try:
            shot[shotnumber].append(group.attrs['program'])
        except:
            shot[shotnumber].append('')

        try:
            shot[shotnumber].append(group.attrs['programdesc'])
        except:
            shot[shotnumber].append('')
        try:            
            shot[shotnumber].append(group.attrs['positionSpace'])
        except:
            shot[shotnumber].append(0.)
        try:                        
            shot[shotnumber].append(group.attrs['Gas'])
        except:
            shot[shotnumber].append('')
        try:            
            shot[shotnumber].append(group.attrs['densityHP'])
        except:
            shot[shotnumber].append(0.)
        try:            
            shot[shotnumber].append(group.attrs['densityLP'])
        except:
            shot[shotnumber].append(0.)    
        try:            
            shot[shotnumber].append(group.attrs['pressure'])
        except:
            shot[shotnumber].append(0.)         
        try:            
            shot[shotnumber].append(group.attrs['magnetic'])
        except:
            shot[shotnumber].append(0.)    
        try:            
            shot[shotnumber].append(group.attrs['comment'])
        except:
            shot[shotnumber].append('')         
        hdf5.close()
    return shot
    
    
#def name_dataset(name,obj):
#    if isinstance(obj,h5py.Dataset):
#        return obj
    
#    for name in hdf5:
#        return [hdf5[name].items() for name in hdf5]
         

