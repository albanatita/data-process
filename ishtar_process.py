# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 11:25:21 2015

@author: admin
"""

from PyQt4 import QtGui, QtCore
import sys
import file_watcher
import readHdf5
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
#import sqlite3
import processActions
import inspect
import os
import numpy as np
import pickle
import readGenerator
import calculateBField


class genCreateDialog(QtGui.QDialog):
    def __init__(self,parent=None):
         super(genCreateDialog,self).__init__(parent)
         layout=QtGui.QVBoxLayout(self)
         label1=QtGui.QLabel('Generator file:')
         self.text1=QtGui.QLineEdit('')
         label2=QtGui.QLabel('First Shot:')
         self.text2=QtGui.QLineEdit('')
         label3=QtGui.QLabel('Last Shot:')
         self.text3=QtGui.QLineEdit('')
         readFile=QtGui.QPushButton("Open File")
         readFile.clicked.connect(self.openFile)
         layout.addWidget(label1)
         layout.addWidget(self.text1)
         layout.addWidget(readFile)
         layout.addWidget(label2)
         layout.addWidget(self.text2)
         layout.addWidget(label3)
         layout.addWidget(self.text3)         
         buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,QtCore.Qt.Horizontal, self)
         buttons.accepted.connect(self.accept)
         buttons.rejected.connect(self.reject)
         layout.addWidget(buttons)
    
    def openFile(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, 'Dialog Title', 'd:\\')
        if fileName:
            self.text1.setText(fileName)
    
    def getValues(self):
        name=self.text1.text()
        firstShot=int(self.text2.text())
        lastShot=int(self.text3.text())
        return name,firstShot,lastShot       
         
    @staticmethod     
    def getData(parent=None):
        dialog=genCreateDialog(parent)
        result=dialog.exec_()
        name,firstShot,lastShot=dialog.getValues()
        return (name,firstShot,lastShot,result==QtGui.QDialog.Accepted)

class gasCreateDialog(QtGui.QDialog):
    def __init__(self,parent=None):
         super(gasCreateDialog,self).__init__(parent)
         layout=QtGui.QVBoxLayout(self)
         self.listGas=QtGui.QComboBox()
         self.listGas.addItems(['Argon','Helium','Hydrogen'])
         label1=QtGui.QLabel('Type of Gas:')
         layout.addWidget(label1)
         layout.addWidget(self.listGas)
         buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,QtCore.Qt.Horizontal, self)
         buttons.accepted.connect(self.accept)
         buttons.rejected.connect(self.reject)
         layout.addWidget(buttons)
    
    def getValues(self):
        name=self.listGas.currentText()
        return name         
         
    @staticmethod     
    def getData(parent=None):
        dialog=gasCreateDialog(parent)
        result=dialog.exec_()
        name=dialog.getValues()
        return (name,result==QtGui.QDialog.Accepted)

class commentCreateDialog(QtGui.QDialog):
    def __init__(self,parent=None):
         super(commentCreateDialog,self).__init__(parent)
         layout=QtGui.QVBoxLayout(self)
         label1=QtGui.QLabel('Comment:')
         layout.addWidget(label1)
         self.text1=QtGui.QLineEdit('')
         layout.addWidget(self.text1)
         buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,QtCore.Qt.Horizontal, self)
         buttons.accepted.connect(self.accept)
         buttons.rejected.connect(self.reject)
         layout.addWidget(buttons)
    
    def getValues(self):
        name=self.text1.text()
        return name         
         
    @staticmethod     
    def getData(parent=None):
        dialog=commentCreateDialog(parent)
        result=dialog.exec_()
        name=dialog.getValues()
        return (name,result==QtGui.QDialog.Accepted)

class progCreateDialog(QtGui.QDialog):
    def __init__(self,parent=None):
         super(progCreateDialog,self).__init__(parent)
         self.text1=QtGui.QLineEdit('5.00')
         self.text2=QtGui.QTextEdit()
         layout=QtGui.QVBoxLayout(self)
         formbox=QtGui.QFormLayout()
         formbox.addRow('Program name : ',self.text1)
         formbox.addRow('Description : ',self.text2)
         self.setLayout(formbox)
         frame1=QtGui.QFrame()
         frame1.setLayout(formbox)
         buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,QtCore.Qt.Horizontal, self)
         buttons.accepted.connect(self.accept)
         buttons.rejected.connect(self.reject)
         layout.addWidget(frame1)         
         layout.addWidget(buttons)

    def getValues(self):
        name=self.text1.text()
        description=self.text2.toPlainText()
        return (name,description)         
         
    @staticmethod     
    def getData(parent=None):
        dialog=progCreateDialog(parent)
        result=dialog.exec_()
        name,description=dialog.getValues()
        return (name,description,result==QtGui.QDialog.Accepted)

class progSetDialog(QtGui.QDialog):
    def __init__(self,valuesi,parent=None):
         super(progSetDialog,self).__init__(parent)
         layout=QtGui.QVBoxLayout(self)
         self.valuesi=valuesi
         self.listProgs=QtGui.QComboBox()
         self.listProgs.addItems(self.valuesi.keys())
         self.listProgs.activated['QString'].connect(self.description)
         self.text=QtGui.QTextEdit()
         
         buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,QtCore.Qt.Horizontal, self)
         buttons.accepted.connect(self.accept)
         buttons.rejected.connect(self.reject)
         layout.addWidget(self.listProgs)         
         layout.addWidget(self.text)
         layout.addWidget(buttons)

    def description(self,item):
        self.text.setText(self.valuesi[item])
        
    def getValues(self):
        name=self.listProgs.currentText()
        return name

    @staticmethod     
    def getData(valuesi,parent=None):
        dialog=progSetDialog(valuesi,parent)
        result=dialog.exec_()
        name=dialog.getValues()
        return (name,result==QtGui.QDialog.Accepted)

class Environment():
    
    def __init__(self,process):
        self.path=r"F:"+os.sep+"DataIshtar"
        self.process=process
        self.mapdiag=dict()
        self.mapdiag[u'PXI M6251/IC_fwd']=['ICfwd']
        self.mapdiag[u'PXI M6251/IC_ref']=['ICref']
        self.mapdiag[u'PXI M6251/Lang_I']=['LangmuirI']
        self.mapdiag[u'PXI M6251/Lang_U']=['LangmuirU']
        self.mapdiag[u'PXI M6251/Phi_fast']=['Bdotphifast']
        self.mapdiag[u'PXI M6251/Phi_slow']=['Bdotphislow']
        self.mapdiag['PXI M6251/U_fast']=['BdotUfast']
        self.mapdiag[u'PXI M6251/U_slow']=['BdotUslow']
        self.mapdiag[u'S7/Big_coil_I [A]']=['Icoil']
        self.mapdiag[u'S7/vacuum [mbar]']=['Pneutral']
        self.mapdiag['Process/Langmuir_dens']=['Langmuirn']
        self.mapdiag['Process/Langmuir_temp']=['LangmuirT']
        self.mapdiag['Process/Langmuir_Vplasma']=['LangmuirVp']
        self.mapdiag['Process/Langmuir_Vfloat']=['LangmuirVf']
        self.mapdiag['Generator/Fpower']=['Hfwd']
        self.mapdiag['Generator/Rpower']=['Href']
        
    def getSignals(self):
        return self.mapdiag.iterkeys()
        
    def attr(self,item):
        return self.mapdiag[item][0]

class ishtarProcess(QtGui.QMainWindow):

    def __init__(self,parent=None):
        super(ishtarProcess,self).__init__(parent)

        self.listShots=QtGui.QTableWidget()

        self.listShots.setColumnCount(10)
        self.listShots.setHorizontalHeaderLabels(('Shot', 'FileName', 'Date', 'Program', 'Position','Gas','Density','Pressure','B','Comment'))
        self.listShots.cellClicked.connect(self.shotSelected)
        self.env=Environment(self)
        menuBar=self.menuBar()
        programMenu=menuBar.addMenu('&Program')
        toolsMenu=menuBar.addMenu('&Tools')
        physicsMenu=menuBar.addMenu('&Physics')
        createProgram=QtGui.QAction(QtGui.QIcon('exit.png'),'&Create',self)
        createProgram.triggered.connect(self.createProg)
        calculatePos=QtGui.QAction(QtGui.QIcon('exit.png'),'&Calculate Position',self)
        calculatePos.triggered.connect(self.calculatePosition)
        calculatePos2=QtGui.QAction(QtGui.QIcon('exit.png'),'&Calculate Position from V',self)
        calculatePos2.triggered.connect(self.calculateSpacefrompos)
        setParam=QtGui.QAction(QtGui.QIcon('exit.png'),'&Set Parameters',self)
        setParam.triggered.connect(self.shotParameters)
        setGas=QtGui.QAction(QtGui.QIcon('exit.png'),'&Set Gas',self)
        setGas.triggered.connect(self.setGas)
        addGenerator=QtGui.QAction(QtGui.QIcon('exit.png'),'&Add Generator File',self)
        addGenerator.triggered.connect(self.addGen)
        addComment=QtGui.QAction(QtGui.QIcon('exit.png'),'&Add Comment',self)
        addComment.triggered.connect(self.addCom)
        computeB=QtGui.QAction(QtGui.QIcon('exit.png'),'&Compute Magnetic Field',self)
        computeB.triggered.connect(self.calculateB)
        programMenu.addAction(createProgram)
        toolsMenu.addAction(calculatePos)
        toolsMenu.addAction(calculatePos2)
        toolsMenu.addAction(setParam)
        toolsMenu.addAction(setGas)
        toolsMenu.addAction(addGenerator)
        toolsMenu.addAction(addComment)
       
        physicsMenu.addAction(computeB)        
        applyProgram=QtGui.QAction(QtGui.QIcon('exit.png'),'&Apply',self)
        applyProgram.triggered.connect(self.applyProg)
        setProgram=QtGui.QAction(QtGui.QIcon('exit.png'),'&Set Current',self)
        setProgram.triggered.connect(self.setProg)
        programMenu.addAction(applyProgram)       
        programMenu.addAction(setProgram)
#        conn=sqlite3.connect('ishtar')
#        curs=conn.cursor()
#        curs.execute('select * from shots')
        listeFiles=[]
        for file in os.listdir(self.env.path):
            if file.endswith(".h5"):
                listeFiles.append(file[0:-3])
        shot=readHdf5.getSummaryData(listeFiles,self.env)            
        row=0
        self.idxmap=dict()
        for key in sorted(shot,reverse=True):
            self.listShots.insertRow(row)
            self.idxmap[str(shot[key][0])]=row
            self.listShots.setItem(row, 0, QtGui.QTableWidgetItem(str(key)))   
            self.listShots.setItem(row, 1, QtGui.QTableWidgetItem(str(shot[key][0])))
            
            self.listShots.setItem(row, 2, QtGui.QTableWidgetItem(str(shot[key][1])))
            self.listShots.setItem(row, 3, QtGui.QTableWidgetItem(str(shot[key][2])))
            self.listShots.setItem(row, 4, QtGui.QTableWidgetItem("%.3f"%shot[key][4]))
            self.listShots.setItem(row, 5, QtGui.QTableWidgetItem(str(shot[key][5])))
            try:
                self.listShots.setItem(row, 6, QtGui.QTableWidgetItem("%.3e"%shot[key][6][1]))
            except:
                self.listShots.setItem(row, 6, QtGui.QTableWidgetItem("%.3e"%shot[key][6]))
            self.listShots.setItem(row, 7, QtGui.QTableWidgetItem("%.3e"%shot[key][8]))
            self.listShots.setItem(row, 8, QtGui.QTableWidgetItem("%.1f"%shot[key][9]))
            self.listShots.setItem(row, 9, QtGui.QTableWidgetItem(str(shot[key][10])))
            row=row+1
        #print self.idxmap

               
        actions=QtGui.QFrame()
        label1=QtGui.QLabel("List of actions:")
        self.listActions=QtGui.QListWidget()
        
        
        listActi=[processActions.__dict__.get(a).__name__ for a in dir(processActions) if inspect.isclass(processActions.__dict__.get(a))]   
        self.listActions.addItems(listActi)
        #listActions.currentItemChanged.connect(self.startAction)
        
        startAction=QtGui.QPushButton("Start Action")
        startAction.clicked.connect(self.startAction)
        label2=QtGui.QLabel("Signal to display:")
        self.signalChoice=QtGui.QComboBox()
        self.signalChoice.activated['QString'].connect(self.plotOverview)
        self.plot=plt.Figure()
        self.ax=self.plot.add_subplot(111)
        self.ax.hold(False)
        self.canvas=FigureCanvas(self.plot)
        vbox=QtGui.QVBoxLayout()
        vbox.addWidget(label1)
        vbox.addWidget(self.listActions)
        vbox.addWidget(startAction)
        vbox.addWidget(label2)
        vbox.addWidget(self.signalChoice)
        vbox.addWidget(self.canvas)
        vbox.addStretch(1)
        actions.setLayout(vbox)        
        self.attrBox=QtGui.QTextEdit()
        self.attrBox.setReadOnly(True)         
        
        
        overview=QtGui.QFrame()
        hbox=QtGui.QHBoxLayout()        
        self.logBox=QtGui.QTextEdit()
        self.logBox.setReadOnly(True)        
        hbox.addWidget(self.logBox)
        hbox.addWidget(self.attrBox)
        hbox.addStretch(1)
        overview.setLayout(hbox)
        
        splitterH=QtGui.QSplitter(QtCore.Qt.Horizontal,self)
        splitterV=QtGui.QSplitter(QtCore.Qt.Vertical,self)
        splitterH.addWidget(self.listShots)
        splitterH.addWidget(actions)
        splitterV.addWidget(splitterH)
        splitterV.addWidget(overview)
        splitterH.setStretchFactor(0, 8)
        
        self.setCentralWidget(splitterV)
        #self.resize(1200,1000)
        self.showMaximized()
        self.watcher=file_watcher.fileWatcher(self.env,self.logBox)
        self.watcher.start()
        self.connect(self.watcher,QtCore.SIGNAL("update(QString)"), self.msg )
        self.connect(self.watcher,QtCore.SIGNAL("converted(QString)"), self.addFile )
        
    def msg(self,text):
        self.logBox.append(text)
        
    def addFile(self,fileName):
        row=self.listShots.rowCount()
        self.listShots.insertRow(row)
        #self.listShots.setItem(rowPosition,0,QtGui.QTableWidgetItem(fileName))
        #conn=sqlite3.connect('ishtar')
        #curs=conn.cursor()
        #lastid=curs.execute('select last_insert_rowid()')        
        #curs.execute('''SELECT * FROM shots ORDER BY shotnbr DESC LIMIT 1''')
        #element=curs.fetchone()
        #row=self.listShots.rowCount()-1
        #self.listShots.insertRow(row)
        fileList=[fileName]
        shot=readHdf5.getSummaryData(fileList,self.env)
        key=int(fileName[0:-5])
        self.listShots.setItem(row, 0, QtGui.QTableWidgetItem(str(key)))   
        self.listShots.setItem(row, 1, QtGui.QTableWidgetItem(str(shot[key][0])))
        self.listShots.setItem(row, 2, QtGui.QTableWidgetItem(str(shot[key][1])))
        self.listShots.setItem(row, 3, QtGui.QTableWidgetItem(str(shot[key][2])))
        self.listShots.setItem(row, 4, QtGui.QTableWidgetItem(str(shot[key][4])))
        self.listShots.setItem(row, 5, QtGui.QTableWidgetItem(str(shot[key][5])))
        self.listShots.setItem(row, 6, QtGui.QTableWidgetItem(str(shot[key][6])))
        self.listShots.setItem(row, 7, QtGui.QTableWidgetItem(str(shot[key][8])))
        self.listShots.setItem(row, 8, QtGui.QTableWidgetItem(str(shot[key][9])))       
        
        
    def shotSelected(self,row1,column):
        #item=self.listShots.item(row,1)
        self.fileName=[]
        for idx in self.listShots.selectedIndexes():
            self.fileName.append(self.listShots.item(idx.row(),1).text())
            
        #self.fileName=item.text()
        #print readHdf5.getSignals(fileName)
        self.signalChoice.clear()
        self.signalChoice.addItems(readHdf5.getSignals(self.fileName[0],self.env))
        self.attrBox.setText(readHdf5.getAttrlist(self.fileName[0],self.env))
#        self.signalChoice.addItems(readHdf5.getSignals(fileName))
        
    def plotOverview(self,item):
        time,data=readHdf5.getOverview(self.fileName[0],item,self.env)
        #print len(time)
        #print len(data)
        self.ax.plot(time,data)
        self.canvas.draw()
        
    def startAction(self):
        self.act=getattr(processActions,self.listActions.currentItem().text())(self.fileName,self.env)
  
    def createProg(self):
        name,description,ok=progCreateDialog.getData()
        try:
            listeProg=pickle.load(open("listeProg.txt","rb"))
        except:
            listeProg=dict()
        listeProg[name]=description
        print listeProg
        pickle.dump(listeProg,open("listeProg.txt","wb"))           
        
    def applyProg(self):
        listeProg=pickle.load(open("listeProg.txt","rb"))
        print listeProg
        name,ok=progSetDialog.getData(listeProg)  
        for idx in self.listShots.selectedIndexes():
            fileName=self.listShots.item(idx.row(),1).text()
            readHdf5.saveAttr(fileName,'program',name,self.env)
            readHdf5.saveAttr(fileName,'programdesc',listeProg[name],self.env)
            #self.listShots.setItem(idx.row(), 3, QtGui.QTableWidgetItem(str(name)))
            self.updateShot([fileName])
            #self.listShots.setItem(idx.row(), 6, QtGui.QTableWidgetItem(str(listeProg[name])))
        
        
    def setProg(self):
        print "toto"
        
    def calculatePosition(self):
        for idx in self.listShots.selectedIndexes():
            fileName=self.listShots.item(idx.row(),1).text()
            try:
                time,data,sampling=readHdf5.getData(fileName,'PXI M6251/manip_pos',self.env)
                positionARM=np.mean(np.array(data))
                readHdf5.saveAttr(fileName,'positionARM',positionARM,self.env)
                #positionARM=readHdf5.getAttr(fileName,'positionARM',self.env)[0]
                fit_fn = np.poly1d([386.80749619,  -34.6945666 ])
                positionSpace=fit_fn(positionARM)
                #slope=(76.-23.)/(400.-1400.)
                #positionSpace=(positionVoltage-400.)*slope+76.-33
                readHdf5.saveAttr(fileName,'positionSpace',positionSpace,self.env)
                self.listShots.setItem(idx.row(), 4, QtGui.QTableWidgetItem("%.3f"%positionSpace))
            except:
                pass
            
    def updateShot(self,fileName):
        shot=readHdf5.getSummaryData(fileName,self.env)            
        for key in sorted(shot,reverse=True):
            row=self.idxmap[str(shot[key][0])]
            self.listShots.setItem(row, 0, QtGui.QTableWidgetItem(str(key)))   
            self.listShots.setItem(row, 1, QtGui.QTableWidgetItem(str(shot[key][0])))
            self.idxmap[str(shot[key][0])]=row
            self.listShots.setItem(row, 2, QtGui.QTableWidgetItem(str(shot[key][1])))
            self.listShots.setItem(row, 3, QtGui.QTableWidgetItem(str(shot[key][2])))
            self.listShots.setItem(row, 4, QtGui.QTableWidgetItem("%.3f"%shot[key][4]))
            self.listShots.setItem(row, 5, QtGui.QTableWidgetItem(str(shot[key][5])))
            try:
                self.listShots.setItem(row, 6, QtGui.QTableWidgetItem("%.3e"%shot[key][6][1]))
            except:
                self.listShots.setItem(row, 6, QtGui.QTableWidgetItem("%.3e"%shot[key][6]))
            self.listShots.setItem(row, 7, QtGui.QTableWidgetItem("%.3e"%shot[key][8]))
            self.listShots.setItem(row, 8, QtGui.QTableWidgetItem("%.1f"%shot[key][9]))                
            self.listShots.setItem(row, 9, QtGui.QTableWidgetItem(str(shot[key][10])))
        
     
    def shotParameters(self)       :
        for idx in self.listShots.selectedIndexes():
            fileName=self.listShots.item(idx.row(),1).text()
            time,data,sampling=readHdf5.getData(fileName,'S7/vacuum [mbar]',self.env)
            readHdf5.saveAttr(fileName,'pressure',data[0],self.env)
            self.listShots.setItem(idx.row(), 7, QtGui.QTableWidgetItem("%.3e"%data[0]))
            time,data,sampling=readHdf5.getData(fileName,'S7/Big_coil_I [A]',self.env)
            readHdf5.saveAttr(fileName,'magnetic',max(data),self.env)
            self.listShots.setItem(idx.row(), 8, QtGui.QTableWidgetItem("%.1f"%max(data)))      
            
    def setGas(self)        :
        name,ok=gasCreateDialog.getData()
        for idx in self.listShots.selectedIndexes():
            fileName=self.listShots.item(idx.row(),1).text()
            readHdf5.saveAttr(fileName,'Gas',name,self.env)
            self.updateShot([fileName])
            
    def addGen(self):
        fileName,firstShot,lastShot,ok=genCreateDialog.getData()
        readGenerator.convertGenerator(fileName,firstShot,lastShot,self.env)
            
    def addCom(self):
        name,ok=commentCreateDialog.getData()
        for idx in self.listShots.selectedIndexes():
            fileName=self.listShots.item(idx.row(),1).text()
            readHdf5.saveAttr(fileName,'comment',name,self.env)
            self.updateShot([fileName])
            
    def calculateB(self):
        self.field=calculateBField.calculateBField(self.fileName,self.env)
        
    def calculateSpacefrompos(self):
        for idx in self.listShots.selectedIndexes():   
            fileName=self.listShots.item(idx.row(),1).text()
            try:
                position=readHdf5.getAttr(fileName,'position',self.env)
                slope=(23.-76.)/(1400.-400.)
                positionSpace=(position-400.)*slope+76.-33
                readHdf5.saveAttr(fileName,'positionSpace',positionSpace,self.env)
            except:
                pass
     
if __name__=='__main__':
    app=QtGui.QApplication(sys.argv)
    mainWindow=ishtarProcess()
    mainWindow.show()
    sys.exit(app.exec_())
    