# -*- coding: utf-8 -*-
"""
Created on 

@author: Matthias Zenker, Rainer Jacob

Start ElmerSolver class
"""
try:
    from PyQt4 import QtGui
    from PyQt4 import QtXml
    from PyQt4 import QtCore
except ImportError:
    from PyQt5 import QtWidgets as QtGui
    from PyQt5 import QtXml
    from PyQt5 import QtCore

from distutils import spawn
import subprocess
import os
import sys

class runElmerSolver():
    """runElmerSolver"""

    def __init__(self, ewh):
        # private
        self._ewh = ewh

    def expand(self,cmd):
        cmd_str = cmd
        cmd_str = cmd_str.replace('%n', str(self._ewh.psWindow.nofProcessorsSpinBox.value()))
        cmd_str = cmd_str.replace('%msh', self._ewh.meshDirectory)
        cmd_str = cmd_str.replace('%ep', str(self._ewh.gsWindow.postFileEdit.text()))
        return cmd_str
    

    # %% call to ElmerSolver
    def start_Solver(self):
        """Calls the ElmerSolver. Checks if a sif-file is present and whether
        multiprocessing is available and selected by the user.

        """
        #global subprocess
        
        # get sif-File and mesh-File
        sifFile = self._ewh.sifFile
        meshDirectory = self._ewh.meshDirectory
        # dummy values for testing
        #sifFile = "case.sif"
        #meshDirectory = "case"
        if sifFile == '' or meshDirectory == '':
            QtGui.QMessageBox.warning(None, "runElmerSolver",
                                      "No sif-file or mesh-file name present in memory. Write sif or create mesh.")
            return 0
        else:
            # check if ElmerSolver is known
            
            if spawn.find_executable('ElmerSolver') == None:
                QtGui.QMessageBox.warning(None, str("runElmerSolver"),
                                          "No ElmerSolver-executable found.")
                return 0
            else:
                from threading import Thread
                # do multiprocessing if set
                # (ParallelSettings class checks for mpi executable and availability of multiprocessing)
                if self._ewh.psWindow.parallelActiveCheckBox.isChecked():
                    if not self._ewh.psWindow.skipPartitioningCheckBox.isChecked():
                        # split mesh
                        # on Linux shell=True required,
                        # see http://stackoverflow.com/a/18962815/4141279
                        cmd = self.expand(str(self._ewh.psWindow.divideLineEdit.text()))
                        print(cmd)
                        subprocess.Popen(cmd, shell=True)
                    # change dir
                    path = os.path.dirname(sifFile)
                    os.chdir(path)
                    # create setup file
                    fs = open('ELMERSOLVER_STARTINFO', mode='w')
                    fileName = os.path.basename(sifFile)
                    fs.writelines([fileName, '\n', '1'])
                    fs.close()

                    #------------------------------------------------
                    # call ElmerSolver via mpiexec via a separate thread
                    def solve():
                        logfile = open(sifFile.replace('.sif','.log'), 'w')
                        cmd = self.expand(str(self._ewh.psWindow.parallelExecLineEdit.text()) + ' ' + str(self._ewh.psWindow.parallelArgsLineEdit.text()))
                        print(cmd)
                        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
                        # Poll process for new output until finished
                        while True:
                            nextline = proc.stdout.readline()
                            if nextline == '' and proc.poll() is not None:
                                break
                            sys.stdout.write(nextline)
                            sys.stdout.flush()
                            logfile.write(nextline)

                        output = proc.communicate()[0]
                        exitCode = proc.returncode
                        logfile.close()
                        if (not self._ewh.psWindow.skipPartitioningCheckBox.isChecked) and (os.path.splitext(str(self.gsWindow.postFileEdit.text()))[1] != ".ep"):
                            # merge mesh
                            cmd = self.expand(str(self._ewh.psWindow.mergeLineEdit.text()))
                            print(cmd)
                            subprocess.Popen(cmd, shell=True)
                        print 'Done'
                        #------------------------------------------------

                    print 'starting'
                    sys.stdout.flush()
                    t = Thread(target=solve)
                    t.start()
                    QtGui.QMessageBox.information(None, 'Solver', 'Solver is running. Check console and log file.')
                    return 1
                # single core operation
                else:
                    path = os.path.dirname(sifFile)
                    os.chdir(path)

                    #------------------------------------------------
                    # call ElmerSolver via a separate thread
                    def solve():
                        logfile = open(sifFile.replace('.sif','.log'), 'w')
                        proc = subprocess.Popen("ElmerSolver {}".format(sifFile),
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                universal_newlines=True, shell=True)
                        # Poll process for new output until finished
                        while True:
                            nextline = proc.stdout.readline()
                            if nextline == '' and proc.poll() is not None:
                                break
                            sys.stdout.write(nextline)
                            sys.stdout.flush()
                            logfile.write(nextline)

                        output = proc.communicate()[0]
                        exitCode = proc.returncode
                        logfile.close()
                        print 'Done'
                    #------------------------------------------------

                    print 'starting'
                    sys.stdout.flush()
                    t = Thread(target=solve)
                    t.start()
                    QtGui.QMessageBox.information(None, 'Solver', 'Solver is running. Check console and log file.')
                    # ...
                    #QtGui.QMessageBox.information(None, 'Solver', 'Solver has terminated.')
                    return 1

