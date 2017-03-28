# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 12:25:27 2016

@author: Rainer Jacob
"""

import py_compile
import glob

files = glob.glob(r"C:\opt\SALOME-7.8.0-WIN64\PLUGINS\ElmerSalome\*.py")

for file in files:
    path = py_compile.compile(file, cfile="{}c".format(file))

