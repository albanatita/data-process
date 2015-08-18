# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 11:45:30 2015

@author: admin
"""

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import readHdf5
import numpy as np
import scipy.fftpack
from scipy.signal import argrelextrema
from scipy.interpolate import interp1d,splrep,splev
import pickle
import traceback

class matchDialog(QtGui.QDialog):
    def __init__(self,parent=None):
         super(matchDialog,self).__init__(parent)
         self.text1=QtGui.QLineEdit('5.00')
         self.text2=QtGui.QLineEdit('11.70')
         formbox=QtGui.QFormLayout()
         layout=QtGui.QVBoxLayout(self)
         formbox.addRow('ICRF Frequency (MHz) : ',self.text1)
         formbox.addRow('Helicon Frequency (MHz) : ',self.text2)
         frame1=QtGui.QFrame()
         frame1.setLayout(formbox)
         buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,QtCore.Qt.Horizontal, self)
         buttons.accepted.connect(self.accept)
         buttons.rejected.connect(self.reject)
         layout.addWidget(frame1)         
         layout.addWidget(buttons)
    
    def getFreq(self):
        freq1=float(self.text1.text())*1.e6
        freq2=float(self.text2.text())*1.e6
        return (freq1,freq2)        
    
    @staticmethod     
    def getData(parent=None):
        dialog=matchDialog(parent)
        result=dialog.exec_()
        freq1,freq2=dialog.getFreq()
        return (freq1,freq2,result==QtGui.QDialog.Accepted)
         

class plotSignal(QtGui.QMainWindow):
    
    def __init__(self,filename,env,parent=None):
         super(plotSignal,self).__init__(parent)
         pg.setConfigOption('background', 'w')
         pg.setConfigOption('foreground', 'k')
         self.fileName=filename
         self.setWindowTitle("Plotting signal")
         self.resize(1000,600)
         self.env=env
         self.signalChoice=QtGui.QComboBox()
         self.signals=readHdf5.getSignals(self.fileName[0],self.env)
         self.signalChoice.addItems(self.signals)
         self.signalChoice.activated['QString'].connect(self.plotSignal)
         
         self.p1=pg.PlotWidget()
         #self.p1.resize(500,300)
         self.p2=pg.PlotWidget()
         self.p3=pg.PlotWidget()
         button2=QtGui.QPushButton('FFT')
         button2.clicked.connect(self.calculatefft)
         
         vbox=QtGui.QVBoxLayout()
         vbox.addWidget(self.signalChoice)
         vbox.addWidget(self.p1)
         vbox.addWidget(self.p2)
         vbox.addStretch(1)
         
         vbox2=QtGui.QVBoxLayout()         
         vbox2.addStretch(1)
         
         draw=QtGui.QFrame()
         label1=QtGui.QLabel('Properties')
         button3=QtGui.QPushButton('Match frequencies')
         button3.clicked.connect(self.matchFreq)
         button1=QtGui.QPushButton('calculate')
         self.frqlabel=QtGui.QLabel('Sampling rate:')
         
         button1.clicked.connect(self.calculate)
         self.textResult=QtGui.QTextEdit()
         self.textResult.setReadOnly(True)
         self.attribut=QtGui.QLineEdit()
#         self.save=QtGui.QPushButton('Save data')
#         self.save.clicked.connect(self.saveData)
         
         process=QtGui.QFrame()
         vbox2.addWidget(self.frqlabel)
         vbox2.addWidget(self.p3)
         vbox2.addWidget(button3)
         vbox2.addWidget(button2)
         vbox2.addWidget(label1)
         vbox2.addWidget(button1)
         vbox2.addWidget(self.textResult)
         vbox2.addWidget(self.attribut)
#         vbox2.addWidget(self.save)
         process.setLayout(vbox2)
         draw.setLayout(vbox)
         splitterH=QtGui.QSplitter(QtCore.Qt.Horizontal,self)
         splitterH.addWidget(draw)
         splitterH.addWidget(process)
         self.setCentralWidget(splitterH)
         
         try:
             [self.left,self.right,saveName,self.signalName]=pickle.load( open( "User.dat", "rb" ) )
             self.existingData=True
             self.signalChoice.setCurrentIndex(self.signals.index(self.signalName))
             self.plotSignal(self.signalName)
             self.updatePlot()
             self.attribut.setText(saveName)
         except Exception,e:
             print str(e)
             self.existingData=False  
         if len(self.fileName)>1:
             self.existingData=False
         self.existingData=False    
         self.show()


    def plotSignal(self,item):
        indexColor=0
        self.p1.clear()
        self.p2.clear()
        for fileName in self.fileName:
            print fileName
            self.Back=False
            self.signalName=item
            time,data,self.sampling=readHdf5.getData(fileName,item,self.env)
            self.time=np.array(time)
            self.data=np.array(data)
            self.frqlabel.setText('sampling rate: '+str(self.sampling))
            pencil=pg.mkPen(color=pg.intColor(indexColor))
            self.p1.plot(self.time,self.data,pen=pencil)
            self.p2.plot(self.time,self.data,pen=pencil)
            indexColor=indexColor+1
            
        if self.existingData:
            self.lr=pg.LinearRegionItem([self.left,self.right])
        else:
            self.lr=pg.LinearRegionItem([self.time[0],self.time[-1]])
            self.left=self.time[0]
            self.right=self.time[-1]
        self.lr.setZValue(-10)
        self.p1.addItem(self.lr)
        self.lr.sigRegionChanged.connect(self.updatePlot)
        
    def updatePlot(self):
        self.p2.setXRange(*self.lr.getRegion(),padding=0)
        [self.left,self.right]=self.lr.getRegion()
    


    def calculate(self):
        self.results=dict()        
        #item=self.signalChoice.currentText()
        for file in self.fileName:

            for item in self.env.getSignals():
                try:
                    print item
                    time,data,self.sampling=readHdf5.getData(file,item,self.env) 
                    rang=self.p2.getPlotItem().getViewBox().viewRange()
                    rang2=rang[0]
                    average=np.mean(data[(time>=rang2[0]) & (time<=rang2[1])])
                    maxi=np.max(data[(time>=rang2[0]) & (time<=rang2[1])])
                    mini=np.min(data[(time>=rang2[0]) & (time<=rang2[1])])
               #     self.results[file]=[average,maxi,mini]
                #    self.textResult.append(file+':\n'+'Mean: '+str(average)+'\n'+'Max: '+str(maxi)+'\n'+'Min: '+str(mini)+'\n')
                    nameAttr=self.env.attr(item)+self.attribut.text()
                    readHdf5.saveAttr(file,nameAttr,np.array([average,maxi,mini]),self.env)
                except:
                    pass
        pickle.dump([self.left,self.right,self.attribut.text(),self.signalChoice.currentText()], open( "User.dat", "wb" ) )       

       
    def calculatefft(self):
        indexColor=0
        self.p3.clear()
        self.p3.addLegend()
        for fileName in self.fileName:
            time,data,self.sampling=readHdf5.getData(fileName,self.signalName,self.env)
            self.time=np.array(time)
            self.data=np.array(data)
            rang=self.p2.getPlotItem().getViewBox().viewRange()
            rang2=rang[0]
            # Number of samplepoints
            dataslice=self.data[(self.time>=rang2[0]) & (self.time<=rang2[1])]
            N=len(dataslice)
            # sample spacing
            T = 1.0 / self.sampling
            yf = scipy.fftpack.fft(dataslice)
            xf = np.linspace(0.0, 1.0/(2.0*T), N/2)
            pencil=pg.mkPen(color=pg.intColor(indexColor))
            self.p3.plot(xf, 2.0/N * np.abs(yf[0:N/2]),pen=pencil,name=fileName[0:-5])
            indexColor=indexColor+1
        self.p3.setLabel('left', "Spectral power (SI)")
        self.p3.setLabel('bottom', "Frequency (Hz)")
        
    def matchFreq(self):
        freq1,freq2,ok=matchDialog.getData()
        pencil1=pg.mkPen(color=pg.intColor(1))
        pencil2=pg.mkPen(color=pg.intColor(20))        
        pencil3=pg.mkPen(color=pg.intColor(30))
        for k in range(1,4):
            self.p3.plot([k*freq1,k*freq1],[0,1.],pen=pencil1)
            self.p3.plot([k*freq2,k*freq2],[0,1.],pen=pencil2)
            for l in range(1,3):
                self.p3.plot([k*freq2-l*freq1,k*freq2-l*freq1],[0,.5],pen=pencil3)            
                self.p3.plot([k*freq2+l*freq1,k*freq2+l*freq1],[0,.5],pen=pencil3)            
        self.p3.addItem(pg.PlotDataItem(pen=pencil1,name='ICRF'))
        self.p3.addItem(pg.PlotDataItem(pen=pencil2,name='Helicon'))
        self.p3.addItem(pg.PlotDataItem(pen=pencil3,name='Beat'))
        

class langmuirSingle(QtGui.QMainWindow):
    
    def __init__(self,filename,env,parent=None):
         super(langmuirSingle,self).__init__(parent)
         pg.setConfigOption('background', 'w')
         pg.setConfigOption('foreground', 'k')
         self.fileName=filename[0]
         self.setWindowTitle("Plotting signal")
         self.resize(1000,600)
         self.env=env
         self.Back=False
         self.signalChoice1=QtGui.QComboBox()
         self.signalChoice2=QtGui.QComboBox()
         self.signals=readHdf5.getSignals(self.fileName,self.env)
         self.signalChoice1.addItems(self.signals)
         self.signalChoice2.addItems(self.signals)         
         self.p1=pg.PlotWidget()
         self.p2=pg.PlotWidget()
         self.p3=pg.PlotWidget()
         self.p4=pg.PlotWidget()


         button1=QtGui.QPushButton('Select I and V signals')
         button1.clicked.connect(self.chooseSignals)
         button2=QtGui.QPushButton('Select window')
         button2.clicked.connect(self.displayIV)
         button3=QtGui.QPushButton('Select current correction')
         button3.clicked.connect(self.currentCorrection)
         button4=QtGui.QPushButton('Select temperature zone')
         button4.clicked.connect(self.temperature)
         self.textResult=QtGui.QTextEdit()
         self.textResult.setReadOnly(True)
       
         self.text1=QtGui.QLineEdit('100')
         self.gas=QtGui.QComboBox()
         self.gas.addItems(['Argon','Helium'])
         self.tempChoice=QtGui.QCheckBox('Calculate temp')
         self.temp=QtGui.QLineEdit()
         
         formbox=QtGui.QFormLayout()
         formbox.addRow('Probe rate : ',self.text1)
         formbox.addRow('Type of gas : ',self.gas)
         formbox.addRow('Use Temperature : ',self.tempChoice)
         formbox.addRow('Temperature : ',self.temp)
         form=QtGui.QFrame()
         form.setLayout(formbox)
         
         button5=QtGui.QPushButton('Save background')
         button5.clicked.connect(self.saveBack)
         
         self.saveL=QtGui.QLineEdit()
         button6=QtGui.QPushButton('Save attribute')
         button6.clicked.connect(self.saveAttr)

         vbox2=QtGui.QVBoxLayout()         
         vbox2.addStretch(1)
         vbox2.addWidget(form)
         vbox2.addWidget(button5)
         vbox2.addWidget(self.p3)
         vbox2.addWidget(button3)
         vbox2.addWidget(self.p4)         
         vbox2.addWidget(button4)         
         vbox2.addWidget(self.textResult)
         vbox2.addWidget(self.saveL)
         vbox2.addWidget(button6)
         vbox1=QtGui.QVBoxLayout()         
         vbox1.addStretch(1)
         vbox1.addWidget(self.signalChoice1)
         vbox1.addWidget(self.signalChoice2)
         vbox1.addWidget(button1)
         vbox1.addWidget(self.p1)
         vbox1.addWidget(self.p2)
         vbox1.addWidget(button2)
         dataWin=QtGui.QFrame()
         dataWin.setLayout(vbox1)
         
         processWin=QtGui.QFrame()
         processWin.setLayout(vbox2)
         splitterH=QtGui.QSplitter(QtCore.Qt.Horizontal,self)
         splitterH.addWidget(dataWin)
         splitterH.addWidget(processWin)
         self.setCentralWidget(splitterH)

       
         try: 
             [sig1,sig2,self.l1,self.r1,self.l2,self.r2,self.l3,self.r3,lsample,gasindex,calculate,temp]=pickle.load( open( "UserLangmuir.dat", "rb" ) )
             self.signalChoice1.setCurrentIndex(self.signals.index(sig1))   
             self.signalChoice2.setCurrentIndex(self.signals.index(sig2))
             self.text1.setText(lsample)
             self.gas.setCurrentIndex(gasindex)
             self.temp.setText(temp)
             self.tempChoice.setCheckState(calculate)
             self.chooseSignals()
             self.updatePlot()
             self.displayIV()
             self.currentCorrection()
             self.temperature()
             
         except Exception,e:
            print str(e)
            self.l1=0.
            self.r1=2.
            self.l2=0.
            self.r2=0.
            self.l3=0.
            self.r3=0.
            print 'toto'
         self.showMaximized()
         self.show()
         
    def chooseSignals(self):
        Usignal=self.signalChoice1.currentText()
        Isignal=self.signalChoice2.currentText()
        Udata,Idata,time,self.sampling=readHdf5.getMultiData(self.fileName,Usignal,Isignal,self.env)
        self.Udata=np.array(Udata)
        self.Idata=np.array(Idata)
        self.time=np.array(time)
        self.Udata=self.Udata*20.
        self.Idata=-self.Idata*0.01
        self.p1.clear()
        self.p2.clear()
        self.p3.clear()
        self.p4.clear() 
        self.lr=pg.LinearRegionItem([self.l1,self.r1])
        self.lr.setZValue(-10)
        self.p1.addItem(self.lr)    
        self.lr.sigRegionChanged.connect(self.updatePlot)
        self.p1.plot(self.time,self.Idata)
        self.p2.plot(self.time,self.Idata)        


        
    def updatePlot(self):
        self.p2.setXRange(*self.lr.getRegion(),padding=0)
    
    def displayIV(self):
        [self.l1,self.r1]=self.lr.getRegion()
        rang=self.p2.getPlotItem().getViewBox().viewRange()
        rang2=rang[0]
        Udataslice=self.Udata[(self.time>=rang2[0]) & (self.time<=rang2[1])]
        Idataslice=self.Idata[(self.time>=rang2[0]) & (self.time<=rang2[1])]
#        nsweep1=int(self.sampling/100)
        langsampl=float(self.text1.text())
        nsweep=int(self.sampling/langsampl/2)        
        maxi=argrelextrema(Udataslice, np.greater,order=nsweep)
        mini=argrelextrema(Udataslice, np.less,order=nsweep)
        indx=np.sort(np.hstack((maxi,mini)))[0]
        temp=np.split(Udataslice,indx)
        Udatadown=np.concatenate(temp[::2])
        Idatadown=np.concatenate(np.split(Idataslice,indx)[::2])
        self.p3.clear()
        self.p4.clear()
        self.p3.plot(Udatadown,Idatadown,pen=None,symbol='o',symbolSize=1)
        idxsorted=np.argsort(Udatadown)
        Udatadown=Udatadown[idxsorted]
        Idatadown=Idatadown[idxsorted]   
        Udatadown=self.movingaverage(Udatadown,int(1/langsampl/2*self.sampling/2))
        self.Udatauniq=np.unique(Udatadown)
        self.Idatauniq=np.zeros(len(self.Udatauniq))
        #print 1/langsampl/2*self.sampling/2
        i=0
        while i<len(self.Udatauniq):
            self.Idatauniq[i]=np.mean(Idatadown[Udatadown==self.Udatauniq[i]])
            i=i+1

        #self.Udatauniq=self.movingaverage(self.Udatauniq,100)
        self.Idatauniq=self.movingaverage(self.Idatauniq,int(1/langsampl/2*self.sampling/2))

        if self.Back:
            backi=interp1d(self.UBack,self.IBack)(self.Udatauniq)
            self.Idatauniq=np.subtract(self.Idatauniq,backi)
        self.p3.plot(self.Udatauniq,self.Idatauniq)
        self.lr2=pg.LinearRegionItem([self.l2,self.r2])
        self.lr2.setZValue(-10)
        self.p3.addItem(self.lr2)  

        
    def currentCorrection(self):
        [self.l2,self.r2]=self.lr2.getRegion()
        rangea=self.lr2.getRegion()
        Ufit=self.Udatauniq[(self.Udatauniq>=rangea[0])&(self.Udatauniq<=rangea[1])]
        Ifit=self.Idatauniq[(self.Udatauniq>=rangea[0])&(self.Udatauniq<=rangea[1])]
        fit = np.polyfit(Ufit,Ifit,1)
        fit_fn = np.poly1d(fit)
        
        self.p3.plot(self.Udatauniq,fit_fn(self.Udatauniq),pen=(0,255,0))
        self.Ifitcorr=np.subtract(self.Idatauniq,fit_fn(self.Udatauniq))
        self.indexsat=np.where(self.Idatauniq<=0)[0][-1]
        self.Vfloat=self.Udatauniq[self.indexsat]
        self.Isat=fit_fn(self.Udatauniq)[self.indexsat]
        self.p3.plot(self.Udatauniq,self.Ifitcorr,pen=(255,0,0))
        self.p4.clear()
        self.p4.plot(self.Udatauniq,np.log(self.Ifitcorr))
        self.lr3=pg.LinearRegionItem([self.l3,self.r3])
        self.lr3.setZValue(-10)
        self.p4.addItem(self.lr3)
        
    def temperature(self):
        [self.l3,self.r3]=self.lr3.getRegion()
        if self.tempChoice.isChecked():
            diffI=np.diff(self.movingaverage(self.Ifitcorr[self.indexsat:-10],300))
            diffU=np.diff(self.Udatauniq[self.indexsat:-10])
            idxmax=np.argmax(diffI/diffU)
            self.Vplasma=(self.Udatauniq[self.indexsat:-10])[idxmax-1]
            self.lineal=pg.InfiniteLine(pos=self.Vplasma,angle=90,movable=True)
            # self.p3.clear()
            #self.p3.plot(self.Udatauniq[self.indexsat:-11],diffI/diffU)
            self.p4.addItem(self.lineal)
            rangea=self.lr3.getRegion()
            Ufit=self.Udatauniq[(self.Udatauniq>=rangea[0])&(self.Udatauniq<=rangea[1])]
            #print self.Ifitcorr[(self.Udatauniq>=rangea[0])&(self.Udatauniq<=rangea[1])]
            
            Ilogfit=np.log(self.Ifitcorr[(self.Udatauniq>=rangea[0])&(self.Udatauniq<=rangea[1])])
            #print Ilogfit            
            fit = np.polyfit(Ufit,Ilogfit,1)
            fit_fn = np.poly1d(fit)
            self.p4.plot(Ufit,fit_fn(Ufit),pen=(0,0,255))
            self.T=1/fit[0]
        else:
            self.T=float(self.temp.text())
        e_electron=1.6022e-19
        if self.gas.currentText()=='Argon':
            Mi = 40*1.6726e-27
        if self.gas.currentText()=='Helium': 
            Mi = 4*1.6726e-27
        k_b = 1.3807e-23
        area=2*np.pi*1e-3*10e-3+np.pi*(1e-3)**2
            
        self.dens = -self.Isat * np.sqrt(Mi)/(0.6 * e_electron * area * np.sqrt(k_b*self.T*11604))        
        self.textResult.append('Temperature : '+str(self.T)+'\n Density : '+str(self.dens)+'\n Vfloat : '+str(self.Vfloat)+'\n Vplasma : '+str(self.Vplasma))       
        
    def movingaverage(self,interval, window_size):
        window = np.ones(int(window_size))/float(window_size)
        return np.convolve(interval, window, 'same')
        
    def saveBack(self):
        self.Uback=self.Udatauniq
        self.Iback=self.Idatauniq
        self.back=True
        
    def saveAttr(self):
        attr=self.saveL.text()
        readHdf5.saveAttr(self.fileName,attr,np.array([self.T,self.dens,self.Vfloat,self.Vplasma]),self.env)

        sig1=self.signalChoice1.currentText()
        sig2=self.signalChoice2.currentText()
        lsample=self.text1.text()
        gasindex=self.gas.currentIndex()
        temp=self.temp.text()
        calculate=self.tempChoice.isChecked()
        pickle.dump([sig1,sig2,self.l1,self.r1,self.l2,self.r2,self.l3,self.r3,lsample,gasindex,calculate,temp]    , open( "UserLangmuir.dat", "wb" ) )    
        self.env.process.updateShot([self.fileName])
        
#class powerScaling(QtGui.QMainWindow):
#    
#    def __init__(self,filename,env,parent=None):
#         super(plotSignal,self).__init__(parent)
#         pg.setConfigOption('background', 'w')
#         pg.setConfigOption('foreground', 'k')
#         self.fileName=filename[0]
#         self.setWindowTitle("Plotting signal")
#         self.resize(1000,600)
#         self.env=env
#         
#         
#         self.show()
         
class profiles(QtGui.QMainWindow):
    
    def __init__(self,filename,env,parent=None):
         super(profiles,self).__init__(parent)
         pg.setConfigOption('background', 'w')
         pg.setConfigOption('foreground', 'k')
         self.fileName=filename
         self.setWindowTitle("Profiles")
         self.resize(1000,600)
         self.env=env
         self.p0=pg.PlotWidget()        
         self.p1=pg.PlotWidget()        
         self.p2=pg.PlotWidget()        
         self.p3=pg.PlotWidget()        
         self.l1=QtGui.QLineEdit('densityHP')
         self.l2=QtGui.QLineEdit('fastHP')             
         self.l3=QtGui.QLineEdit('slowHP')             
         self.l4=QtGui.QLineEdit('Vplasma')         
         formbox=QtGui.QFormLayout()
         formbox.addRow('Plot 1: ',self.l1)
         formbox.addRow('Plot 2: ',self.l2)
         formbox.addRow('Plot 3: ',self.l3)
         formbox.addRow('Plot 4: ',self.l4)         
         form=QtGui.QFrame()
         button0=QtGui.QPushButton('Plot data')
         button0.clicked.connect(self.start)
         form.setLayout(formbox)
         vbox2=QtGui.QVBoxLayout()         
         vbox2.addStretch(1)
         vbox2.addWidget(form)
         vbox2.addWidget(button0)

         vbox1=QtGui.QVBoxLayout()         
         vbox1.addStretch(1)
         vbox1.addWidget(self.p0)
         vbox1.addWidget(self.p1)
         vbox1.addWidget(self.p2)
         vbox1.addWidget(self.p3)         
         frame1=QtGui.QFrame()
         frame1.setLayout(vbox1)
         frame2=QtGui.QFrame()
         frame2.setLayout(vbox2)
         splitterH=QtGui.QSplitter(QtCore.Qt.Horizontal,self)
         splitterH.addWidget(frame1)
         splitterH.addWidget(frame2)
         self.setCentralWidget(splitterH)
         self.show()  
         
         
    def start(self):
         def calibr(x):
             slope=(76.-23.)/(400.-1400.)
             return (x-400.)*slope+76.-33     
             
         def calibr2(x):
             return 10**(((x-0.02- 2.2503)/0.0520+10)/10)
         pos=[]           
         data1=[]
         data2=[]
         data3=[]
         data4=[]
         data1max=[]
         data2max=[]
         data3max=[]
         data4max=[]
         data1min=[]
         data2min=[]
         data3min=[]
         data4min=[]
         for x in self.fileName:
            try:
                pos.append(readHdf5.getAttr(x,'positionSpace',self.env))
            except:
                continue
            try:
                attr=self.l1.text()
                print attr
                if attr=='':
                    data1.append(0.)
                    data1min.append(0.) 
                    data1max.append(0.) 
                else:
#                    attr2=attr
#                    if attr=='VplasmaHP' or attr=='VplasmaLP':
#                        attr2='density'+attr[-1:-2]
#                    if attr=='VfloatHP' or attr=='VfloatLP':
#                        
#                        attr2='density'+attr[-1:-2]
#                    if attr=='tempHP' or attr=='tempLP':
#                        attr2='density'+attr[-1:-2]                   
#                    data=readHdf5.getAttr(x,attr2,self.env)
#                    attr=attr2
                    data=readHdf5.getAttr(x,attr,self.env)
#                    if (attr=='fastHP' or attr=='fastLP' or attr=='slowLP' or attr=='slowHP'):
#                        data=calibr2(data[0])
#                    if attr=='densityHP' or attr=='densityLP':
#                        data=data[1]
#                    if attr=='vplasmaHP' or attr=='vplasmaLP':
#                        data=data[3]
#                    if attr=='vfloatHP' or attr=='vfloatLP':
#                        
#                        data=data[2]
#                    if attr=='tempHP' or attr=='tempLP':
#                        data=data[0]                        
                        
                    data1.append(data[0]) 
                    data1max.append(data[1])
                    data1min.append(data[2])                             
            except:
                 pass
            try:
                attr=self.l2.text()
                if attr=='':
                    data2.append(0.)    
                    data2min.append(0.)  
                    data2max.append(0.)  
                else:
                    data=readHdf5.getAttr(x,attr,self.env)
                    data2.append(data[0]) 
                    data2max.append(data[1])
                    data2min.append(data[2])                             
            except:
                 pass
            try:
                attr=self.l3.text()
                if attr=='':
                    data3.append(0.)    
                    data3min.append(0.)  
                    data3max.append(0.)  
                else:
                    data=readHdf5.getAttr(x,attr,self.env)
                    data3.append(data[0]) 
                    data3max.append(data[1])
                    data3min.append(data[2])                             
            except:
                 pass
            try:
                attr=self.l4.text()
                if attr=='':
                    data4.append(0.)    
                    data4min.append(0.)  
                    data4max.append(0.)  
                else:
                    data=readHdf5.getAttr(x,attr,self.env)
                    data4.append(data[0]) 
                    data4max.append(data[1])
                    data4min.append(data[2])                             
            except:
                 pass
   
         #self.p1.plot(title='Fast Wave profile High Power')
         self.p0.clear()
         self.p0.plot(pos,data1,pen=None,symbolPen='w')
         self.p0.setLabel('bottom', "Position/Center (cm)")
         self.p1.clear()
         self.p1.plot(pos,data2,pen=None,symbolPen='w')
         self.p1.setLabel('bottom', "Position/Center (cm)")
         self.p2.clear()
         self.p2.plot(pos,data3,pen=None,symbolPen='w')
         self.p2.setLabel('bottom', "Position/Center (cm)")
         self.p3.clear()
         self.p3.plot(pos,data4,pen=None,symbolPen='w')
         self.p3.setLabel('bottom', "Position/Center (cm)")
         self.p1.setXLink(self.p0)
         self.p2.setXLink(self.p0)
         self.p3.setXLink(self.p0)
         err = pg.ErrorBarItem(x=np.array(pos), y=np.array(data1), top=np.array(data1max), bottom=np.array(data1min), beam=0.5)
         self.p0.addItem(err)
         err = pg.ErrorBarItem(x=np.array(pos), y=np.array(data2), top=np.array(data2max), bottom=np.array(data2min), beam=0.5)
         self.p1.addItem(err)
         err = pg.ErrorBarItem(x=np.array(pos), y=np.array(data3), top=np.array(data3max), bottom=np.array(data3min), beam=0.5)
         self.p2.addItem(err)
         err = pg.ErrorBarItem(x=np.array(pos), y=np.array(data4), top=np.array(data4max), bottom=np.array(data4min), beam=0.5)
         self.p3.addItem(err)
         
#         indices = np.argsort(pos)
#         pos=np.array(pos)[indices]
#         pos,idx=np.unique(pos,return_index=True)
#         fast=np.array(fast)[indices]
#         fast=fast[idx]
#         tck = splrep(pos,fast,s=100 )
#         x2 = np.linspace(pos[0], pos[-1], 200)
#         y2 = splev(x2, tck)
#         p1.plot(x2,y2,pen=(255,0,0))
         self.show()


class correlateData(pg.GraphicsWindow):
    
    def __init__(self,filename,env,parent=None):
         super(correlateData,self).__init__(parent)
         pg.setConfigOption('background', 'w')
         pg.setConfigOption('foreground', 'k')
         self.fileName=filename
         self.setWindowTitle("Correlate data")
         self.resize(1000,1000)
         self.env=env
         self.correlation={}
         self.signalChoice1=QtGui.QComboBox()
         self.signalChoice2=QtGui.QComboBox()
         self.signals=readHdf5.getSignals(self.fileName[0],self.env)
         self.signalChoice1.addItems(self.signals)
         self.signalChoice2.addItems(self.signals) 
                
         self.p1=pg.PlotWidget()
         self.p2=pg.PlotWidget()
         self.p3=pg.PlotWidget()
         
         self.listShots=QtGui.QListWidget()
         self.listShots.addItems(self.fileName)
         self.listShots.itemClicked.connect(self.display)
         button1=QtGui.QPushButton('Calculate correlation')
         button1.clicked.connect(self.calculate)
         button2= QtGui.QPushButton('Remove correlation')
         button2.clicked.connect(self.delCorr)
         self.corrName=QtGui.QLineEdit()
         button3= QtGui.QPushButton('Save correlation')
         button3.clicked.connect(self.saveCorr)
         
         vbox1=QtGui.QVBoxLayout()         
         vbox1.addStretch(1)
         
         vbox2=QtGui.QVBoxLayout()         
         vbox2.addStretch(1)
         hbox1=QtGui.QHBoxLayout()
         hbox1.addStretch(1)
         #dataWin=QtGui.QFrame()
         #dataWin.setLayout(hbox1)
         vbox1.addWidget(self.signalChoice1)
         vbox1.addWidget(self.signalChoice2)
         vbox1.addWidget(self.p1)
         vbox1.addWidget(self.p2)
         vbox2.addWidget(self.listShots)
         vbox2.addWidget(button1)
         vbox2.addWidget(self.p3)
         vbox2.addWidget(self.corrName)
         vbox2.addWidget(button2)
         win2=QtGui.QFrame()
         win2.setLayout(vbox1)
         win3=QtGui.QFrame()
         win3.setLayout(vbox2)
         
         hbox1.addWidget(win2)
         hbox1.addWidget(win3)
         #self.setCentralWidget(dataWin)
         self.setLayout(hbox1)
         self.show()
         
         
    def display(self,item):
        self.currentFile=self.listShots.currentItem().text()
        signal1=self.signalChoice1.currentText()
        signal2=self.signalChoice2.currentText()
        time1,data1,sampling1=readHdf5.getData(self.currentFile,signal1,self.env)
        time2,data2,sampling2=readHdf5.getData(self.currentFile,signal2,self.env)
        if sampling2>=sampling1:
             self.data2=interp1d(time2,data2)(time1)
             self.timei=time1
             self.data1=data1
        else:
             self.data1=interp1d(time1,data1)(time2)
             self.timei=time2
             self.data2=data2
        self.p1.clear()
        self.p1.plot(self.timei,data1)
        self.p2.clear()
        self.p2.plot(self.timei,self.data2)
        #self.p2.linkXAxis(self.p1)
        self.lr1=pg.LinearRegionItem([self.timei[0],self.timei[-1]])
        self.lr1.setZValue(-10)
        self.lr2=pg.LinearRegionItem([self.timei[0],self.timei[-1]])
        self.lr2.setZValue(-10)
        self.p1.addItem(self.lr1)
        self.p2.addItem(self.lr2)
        self.lr1.sigRegionChanged.connect(self.updatePlot1)
        self.lr2.sigRegionChanged.connect(self.updatePlot2)
        
    def updatePlot1(self):
            self.lr2.setRegion(self.lr1.getRegion())
    def updatePlot2(self):
            self.lr1.setRegion(self.lr2.getRegion())
        
    def calculate(self):
        rangea=self.lr1.getRegion()
        data1corr=self.data1[(self.timei>=rangea[0])&(self.timei<=rangea[1])]
        data2corr=self.data2[(self.timei>=rangea[0])&(self.timei<=rangea[1])]
        self.correlation[self.currentFile]=np.vstack((data1corr,data2corr))
        print np.concatenate((data1corr,data2corr),axis=0).shape        
        self.updateCorr()        
        
    def updateCorr(self):
        self.p3.clear()
        for key in self.correlation:

            self.p3.plot(self.correlation[key][0],self.correlation[key][1],pen=None,symbol='o')

    def delCorr(self):
            del self.correlation[self.currentFile]
            self.updateCorr()
        
    def saveCorr(self):
        print 'toto'
        
class correlateAttributes(pg.GraphicsWindow):
    
   def __init__(self,filename,env,parent=None):
     super(correlateAttributes,self).__init__(parent)
     pg.setConfigOption('background', 'w')
     pg.setConfigOption('foreground', 'k')
     self.fileName=filename
     self.setWindowTitle("Correlate attributes")
     self.resize(1000,1000)
     self.env=env
     self.attr1=QtGui.QLineEdit()
     self.attr2=QtGui.QLineEdit()
     formbox=QtGui.QFormLayout()
     formbox.addRow('Name of attribute 1 : ',self.attr1)
     formbox.addRow('Name of attribute 2 : ',self.attr2)
     form=QtGui.QFrame()
     form.setLayout(formbox)
     self.p1=pg.PlotWidget()
     button1=QtGui.QPushButton('Calculate correlation')
     button1.clicked.connect(self.calculate)
     vbox1=QtGui.QVBoxLayout()
     vbox1.addStretch(1)
     vbox1.addWidget(form)
     vbox1.addWidget(button1)
     vbox1.addWidget(self.p1)
     self.setLayout(vbox1)
     self.show()
     
   def calculate(self):
        attr1=[]
        attr2=[]
        
        for fileName in self.fileName:
            error=False
            try:
                value1=readHdf5.getAttr(fileName,self.attr1.text(),self.env)
                if isinstance(value1,float) or isinstance(value1,int):                    
                    attr1.append(value1)
                else:
                    attr1.append(value1[0])
                error=True
                value2=readHdf5.getAttr(fileName,self.attr2.text(),self.env)
                if isinstance(value2,float)  or isinstance(value2,int):
                    print value2                    
                    attr2.append(value2)
                else:
                    attr2.append(value2[0])
            except:
                if error:
                    attr2.append(0.0)
                continue
            #print attr1,attr2[0]
        #print attr1,attr2
        self.p1.plot(attr1,attr2,pen=None,symbol='o')
        fit = np.polyfit(attr1,attr2,1)
        xx=np.linspace(min(attr1),max(attr1),200)
        self.p1.plot(xx,np.poly1d(fit)(xx))
        print fit
        #fit_fn = np.poly1d(fit)
            
class positionARM(pg.GraphicsWindow):
    
   def __init__(self,filename,env,parent=None):
     super(positionARM,self).__init__(parent)
     pg.setConfigOption('background', 'w')
     pg.setConfigOption('foreground', 'k')
     self.fileName=filename[0]
     self.setWindowTitle("Correlate attributes")
     #self.resize(1000,1000)
     self.env=env       
     view=pg.PlotWidget()
     item='PXI M6251/manip_pos'
     time,data,self.sampling=readHdf5.getData(self.fileName,item,self.env)
     data=self.movingaverage(data,5000)
     view.plot(time,data)
     vbox1=QtGui.QVBoxLayout()
     vbox1.addStretch(1)
     vbox1.addWidget(view)
     self.setLayout(vbox1)
     self.show()
     
     
   def movingaverage(self,interval, window_size):
     window = np.ones(int(window_size))/float(window_size)
     return np.convolve(interval, window, 'same')
     
class overview(pg.GraphicsWindow):
    
    def __init__(self,filename,env,parent=None):
         super(overview,self).__init__(parent)
         pg.setConfigOption('background', 'w')
         pg.setConfigOption('foreground', 'k')
         self.fileName=filename
         self.setWindowTitle("Overview Signal")
         self.showMaximized()
         self.env=env
         p1=self.addPlot(title='Current Big coils')
         self.nextRow()
         p2=self.addPlot(title='Pressure')
         self.nextRow()
         p3=self.addPlot(title='Helicon power')         
         self.nextRow()
         p4=self.addPlot(title='ICRF power')      
         self.nextRow()
         p5=self.addPlot(title='Density Langmuir probe')         
         self.nextRow()
         p6=self.addPlot(title='Amplitude B-dot probes')         
         self.nextRow()
         p7=self.addPlot(title='Phase B-dot probes')         
         indexColor=0
         for x in self.fileName:
             try:
                 timeCoils,dataCoils,sampling=readHdf5.getData(x,'S7/Big_coil_I [A]',env)
             except:
                 pass

             try:
                 timeP,dataP,sampling=readHdf5.getData(x,'S7/vacuum [mbar]',env)
             except: 
                 pass
             try:
                 timeHF,dataHF,sampling=readHdf5.getData(x,'Generator/Fpower',env)
             except: 
                 pass
             try:
                 timeHR,dataHR,sampling=readHdf5.getData(x,'Generator/Rpower',env)
             except: 
                 pass
             try:
                 timeIF,dataIF,sampling=readHdf5.getData(x,'PXI M6251/IC_fwd',env)
             except: 
                 pass
             try:
                 timeIR,dataIR,sampling=readHdf5.getData(x,'PXI M6251/IC_ref',env)
             except: 
                 pass
             try:
                 dataL=np.array(readHdf5.getDataProcess(x,'Process/Langmuir_dens',env))
                 timeL=np.array(readHdf5.getDataProcess(x,'Process/Langmuir_time',env))
             except: 
                 pass
             try:
                 timeFW,dataFW,sampling=readHdf5.getData(x,'PXI M6251/U_fast',env)
             except: 
                 pass
             try:
                 timeSW,dataSW,sampling=readHdf5.getData(x,'PXI M6251/U_slow',env)
             except: 
                 pass
             try:
                 timePhase1,dataPhase1,sampling=readHdf5.getData(x,'PXI M6251/Phi_fast',env)
             except: 
                 pass
             try:
                 timePhase2,dataPhase2,sampling=readHdf5.getData(x,'PXI M6251/Phi_slow',env)
             except: 
                 pass
             
             pencil=pg.mkPen(color=pg.intColor(indexColor)) 
             try:
                 p1.plot(timeCoils,dataCoils,pen=pencil)
             except:    
                 pass
             try:
                p2.plot(timeP,dataP,pen=pencil)
             except:    
                pass
             try:
                p3.plot(timeHF,dataHF,pen=pencil)
                p3.plot(timeHR,dataHR,pen=pencil)
             except:    
                pass
             try:
                p4.plot(timeIF,dataIF,pen=pencil)
                p4.plot(timeIR,dataIR,pen=pencil)
             except:    
                pass
             try:
                p5.plot(timeL,dataL,pen=pencil)
             except:    
                pass
             try:
                p6.plot(timeFW,dataFW,pen=pencil)
                p6.plot(timeSW,dataSW,pen=pencil)
             except:    
                pass
             try:
                p7.plot(timePhase1,dataPhase1-dataPhase2,pen=pencil)

             except:
                 pass
             indexColor=indexColor+1
             
         p7.setXLink(p1)
         p6.setXLink(p1)
         p5.setXLink(p1)        
         p4.setXLink(p1)         
         p3.setXLink(p1)         
         p2.setXLink(p1)         
         
class langmuirTime(QtGui.QMainWindow):
        def __init__(self,filename,env,parent=None):
             super(langmuirTime,self).__init__(parent)
             pg.setConfigOption('background', 'w')
             pg.setConfigOption('foreground', 'k')
             self.fileName=filename[0]
             self.setWindowTitle("langmuir time evolution")
             self.resize(1000,600)
             self.env=env
             self.p0=pg.PlotWidget()
             self.p0.setLabel('left', "Langmuir current (A)")
             self.p0.setLabel('bottom', "Time (s)")
             self.lr=pg.LinearRegionItem([2.,3.])
             self.lr.setZValue(-10)
             self.p0.addItem(self.lr)  
             self.Udata,self.Idata,self.time,self.sampling=readHdf5.getMultiData(self.fileName,'PXI M6251/Lang_I','PXI M6251/Lang_U',self.env)
             self.Udata=np.array(self.Udata)
             self.Idata=np.array(self.Idata)
             self.time=np.array(self.time)
             self.Udata=self.Udata*20.
             self.Idata=-self.Idata*0.01
             self.p0.plot(self.time,self.Idata)
             self.p1=pg.PlotWidget()
             self.p1.setLabel('left', "Plasma density (m^-3)")
             self.p1.setLabel('bottom', "Time (s)")     
             self.p2=pg.PlotWidget()
             self.p2.setLabel('left', "Plasma temperature (eV)")
             self.p2.setLabel('bottom', "Time (s)")  
             self.p3=pg.PlotWidget()
             self.p3.setLabel('left', "Potenials (V)")
             self.p3.setLabel('bottom', "Time (s)")  
             button0=QtGui.QPushButton('Start calculation')
             button0.clicked.connect(self.start)
             button1=QtGui.QPushButton('Save data')
             button1.clicked.connect(self.save)
             self.ramps=QtGui.QLineEdit('10')
             self.slots=QtGui.QLineEdit('50')
             self.gas=QtGui.QLineEdit('Helium')             
             self.tempT=QtGui.QLineEdit('')             
             self.freq=QtGui.QLineEdit('1000')
             formbox=QtGui.QFormLayout()
             formbox.addRow('Number of ramps : ',self.ramps)
             formbox.addRow('Number of time slots : ',self.slots)
             formbox.addRow('Gas : ',self.gas)
             formbox.addRow('Temperature (auto if empty): ',self.tempT)
             formbox.addRow('Sweep frequency: ',self.freq)
             form=QtGui.QFrame()
             form.setLayout(formbox)
             vbox2=QtGui.QVBoxLayout()         
             vbox2.addStretch(1)
             vbox2.addWidget(form)
             vbox2.addWidget(button0)
             vbox2.addWidget(button1)
             vbox1=QtGui.QVBoxLayout()         
             vbox1.addStretch(1)
             vbox1.addWidget(self.p0)
             vbox1.addWidget(self.p1)
             vbox1.addWidget(self.p2)
             vbox1.addWidget(self.p3)         
             frame1=QtGui.QFrame()
             frame1.setLayout(vbox1)
             frame2=QtGui.QFrame()
             frame2.setLayout(vbox2)
             splitterH=QtGui.QSplitter(QtCore.Qt.Horizontal,self)
             splitterH.addWidget(frame1)
             splitterH.addWidget(frame2)
             self.setCentralWidget(splitterH)
             self.show()
             
        def start(self):
        
            rangeal=self.lr.getRegion()
            sweepperiod=float(self.freq.text())
            nbrramps=float(self.ramps.text())
            deltatime0=nbrramps/sweepperiod
            print deltatime0
            nbrslots=int(self.slots.text())
            deltatime=(rangeal[1]-rangeal[0])/nbrslots
            self.dens=np.zeros(nbrslots)
            self.timedata=np.zeros(nbrslots)
            self.temp=np.zeros(nbrslots)
            self.Vplasma=np.zeros(nbrslots)
            self.Vfloat=np.zeros(nbrslots)
            for j in range(0,nbrslots):
                print j
                tstart=rangeal[0]+j*deltatime
                tend=tstart+deltatime0
                Udataslice=self.Udata[(self.time>=tstart) & (self.time<=tend)]
                Idataslice=self.Idata[(self.time>=tstart) & (self.time<=tend)]
                nsweep=int(self.sampling/sweepperiod/2)
                maxi=argrelextrema(Udataslice, np.greater,order=nsweep)
                mini=argrelextrema(Udataslice, np.less,order=nsweep)
                indx=np.sort(np.hstack((maxi,mini)))[0]
                temp=np.split(Udataslice,indx)
                Udatadown=np.concatenate(temp[::2])
                Idatadown=np.concatenate(np.split(Idataslice,indx)[::2])
                idxsorted=np.argsort(Udatadown)
                Udatadown=Udatadown[idxsorted]
                Idatadown=Idatadown[idxsorted]   
                Udatadown=self.movingaverage(Udatadown,int(1/sweepperiod/2*self.sampling/2))
                Udatauniq=np.unique(Udatadown)
                Idatauniq=np.zeros(len(Udatauniq))
                i=0
                
                while i<len(Udatauniq):
                    Idatauniq[i]=np.mean(Idatadown[Udatadown==Udatauniq[i]])
                    i=i+1
                Idatauniq=self.movingaverage(Idatauniq,int(1/sweepperiod/2*self.sampling/2))
                try:
                    
                    indexsat=np.where(Idatauniq<=0)[0][-1]
                    Vfloat=Udatauniq[indexsat]
                    print indexsat, Vfloat
                    
                    deltarange=(Vfloat-Udatauniq[0])
                    rangea=[Vfloat-deltarange/2,Vfloat-deltarange/4]
                    Ufit=Udatauniq[(Udatauniq>=rangea[0])&(Udatauniq<=rangea[1])]
                    Ifit=Idatauniq[(Udatauniq>=rangea[0])&(Udatauniq<=rangea[1])]
                    fit = np.polyfit(Ufit,Ifit,1)
                    fit_fn = np.poly1d(fit)         
                    Ifitcorr=np.subtract(Idatauniq,fit_fn(Udatauniq))
                    Isat=fit_fn(Udatauniq)[indexsat]
                    print "calculating temp"
                    if self.tempT.text()=='':
                        #print indexsat,len(Ifitcorr),len(Udatauniq)
                        #print Udatauniq
                        diffI=np.diff(self.movingaverage(Ifitcorr[indexsat:-10],30))
                        diffU=np.diff(Udatauniq[indexsat:-10])
                        idxmax=np.argmax(diffI/diffU)
                        Vplasma=(Udatauniq[indexsat:-10])[idxmax-1]
                        print Vplasma
                        print Vfloat
                        Vdelta=Vplasma-Vfloat
                        rangea=[Vfloat+Vdelta/4,Vfloat+Vdelta/2]
                        Ufit=Udatauniq[(Udatauniq>=rangea[0])&(Udatauniq<=rangea[1])]
                        Ilogfit=np.log(Ifitcorr[(Udatauniq>=rangea[0])&(Udatauniq<=rangea[1])])
                        fit = np.polyfit(Ufit,Ilogfit,1)
                        fit_fn = np.poly1d(fit)
                        T=1/fit[0]
                    else:
                        Vplasma=Udatauniq[-1]
                        self.T=float(self.temp.text())
                    e_electron=1.6022e-19
                    if self.gas.text()=='Argon':
                        Mi = 40*1.6726e-27
                    if self.gas.text()=='Helium': 
                        Mi = 4*1.6726e-27
                    k_b = 1.3807e-23
                    area=2*np.pi*1e-3*10e-3+np.pi*(1e-3)**2            
                    dens = -Isat * np.sqrt(Mi)/(0.6 * e_electron * area * np.sqrt(k_b*T*11604))
                    self.dens[j]=dens
                    self.temp[j]=T
                    self.Vplasma[j]=Vplasma
                    self.Vfloat[j]=Vfloat
                    self.timedata[j]=tstart
                except Exception:
                    print(traceback.format_exc())
                    self.dens[j]=0
                    self.temp[j]=0
                    self.Vplasma[j]=0
                    self.Vfloat[j]=0
                    self.timedata[j]=tstart
            
            #self.p0.plot(self.time[0:-1:10],self.Idata[0:-1:10])
            self.p1.clear()            
            self.p2.clear()
            self.p3.clear()
            self.p1.plot(self.timedata,self.dens)
            self.p2.plot(self.timedata,self.temp)
            self.p3.addLegend()
            self.p3.plot(self.timedata,self.Vfloat,pen=pg.mkPen('r'),name='Vfloat')
            self.p3.plot(self.timedata,self.Vplasma,pen=pg.mkPen('b'),name='Vplasma')

            self.p3.setXLink(self.p0)         
            self.p2.setXLink(self.p0)    
            self.p1.setXLink(self.p0)


        def save(self):
            readHdf5.saveData(self.fileName,'Langmuir_dens',self.dens,self.env)
            readHdf5.saveData(self.fileName,'Langmuir_temp',self.temp,self.env)
            readHdf5.saveData(self.fileName,'Langmuir_Vplasma',self.Vplasma,self.env)
            readHdf5.saveData(self.fileName,'Langmuir_Vfloat',self.Vfloat,self.env)
            readHdf5.saveData(self.fileName,'Time',self.timedata,self.env)
            
        def movingaverage(self,interval, window_size):
            window = np.ones(int(window_size))/float(window_size)
            return np.convolve(interval, window, 'same')