# -*- coding: utf-8 -*-
"""
Created on Thu Aug 06 10:11:13 2015

@author: admin
"""
from subprocess import call
from PyQt4 import QtGui,QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt
import readHdf5
import numpy as np
import os

class calculateBField(QtGui.QMainWindow):
        def __init__(self,filename,env,parent=None):
             super(calculateBField,self).__init__(parent)
#             pg.setConfigOption('background', 'w')
#             pg.setConfigOption('foreground', 'k')
             plt.ioff()
             self.fileName=filename[0]
             self.setWindowTitle("B Field Map - "+self.fileName )
             self.resize(1000,600)
             self.env=env
             #self.p0=pg.ImageView()
             self.figure=plt.figure()
             self.canvas=FigureCanvas(self.figure)
             self.toolbar = NavigationToolbar(self.canvas, self)
             #self.p0.setLabel('left', 'Y Axis")
             #self.p0.setLabel('bottom', "X Axis")
             button0=QtGui.QPushButton('Start calculation')
             button0.clicked.connect(self.start)
             button2=QtGui.QPushButton('Display data')
             button2.clicked.connect(self.display)
             button1=QtGui.QPushButton('Save data')
             button1.clicked.connect(self.save)
             self.bigC=QtGui.QLineEdit('auto')
             self.smallC=QtGui.QLineEdit('1000')
             self.addC=QtGui.QLineEdit('0')             
             formbox=QtGui.QFormLayout()
             formbox.addRow('Current Big coil (A): ',self.bigC)
             formbox.addRow('Current small coil (A): ',self.smallC)
             formbox.addRow('Current additional coil (A): ',self.addC)        
             form=QtGui.QFrame()
             form.setLayout(formbox)
             vbox2=QtGui.QVBoxLayout()         
             #vbox2.addStretch(1)
             vbox2.addWidget(form)
             vbox2.addWidget(button0)
             vbox2.addWidget(button2)
             vbox2.addWidget(button1)
             vbox1=QtGui.QVBoxLayout()         
             #vbox1.addStretch(1)
             vbox1.addWidget(self.canvas)  
             vbox1.addWidget(self.toolbar)
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
            smallcoils=float(self.smallC.text())
            addcoil=float(self.addC.text())
            text=self.bigC.text()
            if text=='auto':
                try:
                    bigcoil=readHdf5.getAttr(self.fileName,'magnetic',self.env)
                except:
                    text='2000'
                    self.smallC.setText('2000')
            if not(text=='auto'):
                bigcoil=float(text)
            file = open('2015_07_22_MFC_003_adBcoil.FEM', 'r')
            i=1
            for line in file:
                if i==55:
                    line=line.split('=')[0]+'='+str(smallcoils)+'\n'
                if i==61:
                    line=line.split('=')[0]+'='+str(-smallcoils)+'\n'
                if i==67:
                    line=line.split('=')[0]+'='+str(bigcoil)+'\n'
                if i==73:
                    line=line.split('=')[0]+'='+str(-bigcoil)+'\n'
                if i==79:
                    line=line.split('=')[0]+'='+str(addcoil)+'\n'
                if i==85:
                    line=line.split('=')[0]+'='+str(-addcoil)+'\n'
                i=i+1
            command="C:"+os.sep+"femm42"+os.sep+"bin"+os.sep+"femm.exe"
            path=r"D:"+os.sep+"DATA"+os.sep+"IShTAR_Process"            
            script1="-lua-script="+path+os.sep+"LUA_code_003.lua"
            script2=" -windowhide"
            command=command+' '+script1+' '+script2
            print command
            print script1,script2
            call(command,shell=True)
            
        def display(self):  
            path=r"D:"+os.sep+"DATA"+os.sep+"IShTAR_Process" 
            fileX='LuaBz_axis.mag'            
            result=np.loadtxt(path+os.sep+fileX)
            result=np.concatenate((result,result[::-1,:]),axis=0)
            x_1d = np.linspace(-50,50,100)
            y_1d = np.linspace(1,200,200)
            self.ax=self.figure.add_subplot(111)
            pol=plt.pcolormesh(y_1d,x_1d,result)
            plt.colorbar()
            plt.contour(y_1d, x_1d, result,colors="k")
            self.ax.add_collection(pol)
            self.canvas.draw()
            #ax=self.figure.add
            

            
        def save(self):
            print "toto"
                        

    
        