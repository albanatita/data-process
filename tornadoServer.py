# -*- coding: utf-8 -*-
"""
Created on Tue Jul 07 12:44:35 2015

@author: admin
"""

import tornado.ioloop
import tornado.web
import sqlite3
from tornado.escape import json_encode
import readHdf5
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html
import os
import numpy as np

class Environment():
    
    def __init__(self):
        self.path=r"D:"+os.sep+"DATA"+os.sep+'Acquired_data'

class MainHandler(tornado.web.RequestHandler):
    def get(self):
#        self.write('List of discharges\n')        
#        
#        conn=sqlite3.connect('ishtar')
#        curs=conn.cursor()
#        curs.execute('select * from shots')
#        for row,form in enumerate(curs):
#            for column, item in enumerate(form):
#                #print str(item)
#                self.write(str(item)+'\n')
        env=Environment()
        time,data,sampling=readHdf5.getData('00857_Data','Generator/Fpower',env)
        #print time[100],data[100]
        plot = figure()
        plot.line(np.array(time), np.array(data))

        html = file_html(plot, CDN, "my plot") 
        self.write(html)
        #print len(time),len(data)
        #self.ax.plot(time,data)
        #self.canvas.draw()   

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()