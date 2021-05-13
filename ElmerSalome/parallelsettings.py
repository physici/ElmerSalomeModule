# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 22:00:00 2017

@author: Matthias Zenker

Parallel settings class
"""

try:
    from PyQt4 import QtGui
    from PyQt4 import uic
except ImportError:
    from PyQt5 import QtWidgets as QtGui
    from PyQt5 import uic
import shutil
import multiprocessing


class ParallelSettings(QtGui.QDialog):
    """Class that provides the Parallel settings dialog and its functionality"""

    def __init__(self, path_forms):
        """Constructor.

        Args:
        -----
        path_forms: str
            String containing the path to the ui-files defining the look of the
            window.
        """
        super(ParallelSettings, self).__init__()
        uic.loadUi(path_forms.joinpath("parallel.ui") , self)
        self.setDefaults()
        self.parallelActiveCheckBox.setChecked(False)
        self.parallelOnOff()
        self.parallelActiveCheckBox.clicked.connect(self.parallelOnOff)
        self.browseButton.clicked.connect(self.getParallelExec)
        self.defaultsButton.clicked.connect(self.setDefaults)
        self.okButton.clicked.connect(self.applyChanges)
        if multiprocessing.cpu_count() > 1:
            self.nofProcessorsSpinBox.setMaximum(multiprocessing.cpu_count())

    def setDefaults(self):
        self.nofProcessorsSpinBox.setValue(2)
        self.parallelExecLineEdit.setText("mpiexec")
        self.parallelArgsLineEdit.setText(" -n %n ElmerSolver_mpi")
        self.divideLineEdit.setText("ElmerGrid 2 2 %msh -metis %n")
        self.mergeLineEdit.setText("ElmerGrid 15 3 %ep -partjoin %n")
        self.label.setText("%n is the number of processes (spinbox above)")
        self.label_2.setText("%msh is the mesh directory")
        self.label_3.setText("%ep is the post file name (General settings)")
        self.skipPartitioningCheckBox.setChecked(False)

    def parallelOnOff(self):
        if (self.parallelActiveCheckBox.isChecked()) and (multiprocessing.cpu_count() < 2):
            QtGui.QMessageBox.warning(None, 'Warning', "No multiprocessing on single-core processor!")
            self.parallelActiveCheckBox.setChecked(False)
        self.nofProcessorsLabel.setEnabled(self.parallelActiveCheckBox.isChecked())
        self.nofProcessorsSpinBox.setEnabled(self.parallelActiveCheckBox.isChecked())
        self.parallelExecLineEdit.setEnabled(self.parallelActiveCheckBox.isChecked())
        self.browseButton.setEnabled(self.parallelActiveCheckBox.isChecked())
        self.parallelArgsLineEdit.setEnabled(self.parallelActiveCheckBox.isChecked())
        self.divideLineEdit.setEnabled(self.parallelActiveCheckBox.isChecked())
        self.mergeLineEdit.setEnabled(self.parallelActiveCheckBox.isChecked())
        self.skipPartitioningCheckBox.setEnabled(self.parallelActiveCheckBox.isChecked())

    def getParallelExec(self):
        filename = QtGui.QFileDialog.getOpenFileName(parent=None, caption="Select MPI executable")
        filename = str(filename)
        if filename != '':
            self.parallelExecLineEdit.setText(filename)

    def applyChanges(self):
        """Accept button hit"""
        # Check if MPI executable exists
        if self.parallelActiveCheckBox.isChecked() and (shutil.which(str(self.parallelExecLineEdit.text())) == None):
            QtGui.QMessageBox.warning(None, 'Error', "MPI executable not found.")
            self.parallelActiveCheckBox.setChecked(False)
            self.parallelOnOff()
        else:
            # Hide window, but keep contents in memory
            self.hide()
