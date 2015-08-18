# -*- coding: utf-8 -*-
"""
Created on Mon May 11 12:12:32 2015

@author: admin
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime,time
import os
import h5py
import readHdf5
  

#filename=r'D:\ISHTARmay\data_20150119_20150610.csv'
def convertGenerator(fileN,firstShot,lastShot,env):
    #filename=r'D:\DATA\IShTAR_Process\data_20150119_20150715.csv'
    filename=os.path.normpath(fileN)
    shotstart=firstShot
    shotend=lastShot
    included_cols=[1,2,3,11,12]
    
    df=pd.read_csv(filename,sep='\t',parse_dates=[0])
    print df.dtypes
    df.loc[df['ForwardPower[W]']!=0,'Run']=1
    #
    df['block']=(df.Run.shift(1)!=df.Run).astype(int).cumsum()
    df.reset_index().groupby(['Run','block'])['index'].apply(lambda x: np.array(x))
    df=df[df['Run']==1]
    nbr=np.max(df['block'])/2
    #print nbr
    liste=np.arange(shotstart,shotend)
    listefile=[]
    for x in liste:
        listefile.append(str(x).zfill(5)+'_Data')
        
    #print listefile
    j=2
    timediff=datetime.timedelta(minutes=1,seconds=0)
    timecorrection=datetime.timedelta(minutes=11,seconds=10)
    #path=r"D:"+os.sep+"DATA"+os.sep+"Acquired_data"
    path=env.path
    for x in listefile:
        #timei=datetime.datetime.strptime(time.ctime(os.path.getmtime(path+os.sep+x+'.h5')),"%a %b %d %H:%M:%S %Y")
        try:    
            timea=readHdf5.getAttr(x,'date',env)
            timei=datetime.datetime.strptime(timea,'%d.%m.%Y %H:%M:%S')
            #print x
            matched=False
            while not(matched):
                data0=df[df['block']==j]['Time'].values
                timef=datetime.datetime.utcfromtimestamp((data0[0]- np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's'))
                print timei,(timef+timecorrection),timef
                timef=timef+timecorrection        
                if timei>timef:        
                    deltat=timei-timef
                else:
                    deltat=timef-timei
                print deltat
                if (deltat<=timediff):
                    data=df[df['block']==j]['ForwardPower[W]'].values
                    data2=df[df['block']==j]['ReflectedPower[W]'].values
                    sampling=1/(float((data0[1]-data0[0]).item())*1e-9)
                    hdf5=h5py.File(path+os.sep+x+'.h5','a')
                    grouph=hdf5.create_group('Generator')
                    grouph.create_dataset('Fpower',data=data,compression="gzip")
                    grouph.create_dataset('Rpower',data=data2,compression="gzip")
                    grouph.attrs['sampling']=sampling
                    j=j+2
                    matched=True
                    print 'Generator for '+x
                    
                if (deltat>timediff) and (timei>timef) and (j<nbr):
                    j=j+2
                    print 'Power without discharge'
                if (deltat>timediff) and (timei>timef) and (j>=nbr):    
                    matched=True
                if (deltat>timediff) and (timei<timef):
                    matched=True
                    print 'No generator for '+x
        except:
         pass  

        #hdf5.close()
             
    
        
    #plt.plot(df[df['block']==4]['ForwardPower[W]'])
    
    #plt.show()