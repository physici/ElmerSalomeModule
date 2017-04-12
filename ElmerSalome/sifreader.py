# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 07:51:36 2017

@author: rainer.jacob

Sif reader class
"""


class SifReader():
    """SifReader"""

    def __init__(self, ewh):
        """Constructor

        Args:
        -----
        ewh: ElmerWindowHandler class
            current instane of the ElmerWindowHandler class containing all data
        """

        self._ewh = ewh
        self._solvIds = {}
        self._sifIds = {}

    def readSif(self, path):
        """Read a given sif-file and create data and objects in the main class
        of the module

        Args:
        -----
        path: str
            path to the sif-file
        """

        # read file and extract the blocks
        fs = open(path)
        data = fs.read()
        blocks = data.split(sep='End')
        blocks = [x.strip() for x in blocks]
        blocks.sort()

        # collect block types
        bodies = []
        boundaries = []
        equations = []
        general = []
        initial = []
        materials = []
        solvers = []
        bforces = []

        for block in blocks:
            if block.startswith('Body'):
                bodies.append(block)
            elif block.startswith('Boundary'):
                boundaries.append(block)
            elif block.startswith('Equation'):
                equations.append(block)
            elif block.startswith('Header'):
                general.append(block)
            elif block.startswith('Simulation'):
                general.append(block)
            elif block.startswith('Constants'):
                general.append(block)
            elif block.startswith('Material'):
                materials.append(block)
            elif block.startswith('Inital'):
                initial.append(block)
            elif block.startswith('Solver'):
                solvers.append(block)
            elif block.startswith('Body Force'):
                bforces.append(block)

        # apply general settings
        for block in general:
            self._general(block)
        # make a new equations window and change settings of first equation
        # also creates the default solvers
        self._ewh.showAddEquation(visible=False)
        # get all solvers by name and index
        for idx, element in enumerate(self._ewh.solverParameterEditor):
            self._solvIds.update({element.solverName: idx})

    def _changeSettings(self, parameter, value):
        """Change settings of hashed parameter in element.

        Args:
        -----
        parameter: obj
            obj of the parameter (e. g. the corresponding widget)
        value: str
            new value of the parameter
        """

        widgetType = parameter.elem.attribute('Widget', 'Edit')
        if widgetType == 'Edit':
            parameter.widget.setText(value)
        elif widgetType == 'TextEdit':
            sifValue = parameter.widget.toPlainText()
            sifValue = sifValue + value + '\n'
            parameter.widget.setText(sifValue)
        elif widgetType == 'Combo':
            idx = parameter.widget.findText(value)
            parameter.widget.setCurrentIndex(idx)
        elif widgetType == 'CheckBox':
            parameter.widget.setChecked(value == 'True')

    def _solvers(self, block):
        """Change settings of the solver.

        Args:
        -----
        block: str
            String containg the settings of the given equation
        """

        data = block.split('\n')

        # mapping of solver name and ID as in sif-file
        sifID = data.pop(0).split(' ')[1]
        name = data.pop(0).split('=')[1].strip()
        self._sifIds.update({name: sifID})

        # get the solver from the solver collection
        idx = self._solvIds[name]
        element = self._ewh.solverParameterEditor[idx]

        procedure = data.pop(0).split('=')[1].strip()
        variable = data.pop(0).split('=')[1].strip()

        while data:
            key, value = data.pop(0).split('=')
            if 'Exec' in key:
                if value == 'Always':
                    element.execAlways.setChecked(True)
                if value == 'Before Simulation':
                    element.execBeforeSimulation.setChecked(True)
                if value == 'After Simulation':
                    element.execAfterSimulation.setChecked(True)
                if value == 'Before Timestep':
                    element.execBeforeTimestep.setChecked(True)
                if value == 'After Timestep':
                    element.execAfterTimestep.setChecked(True)
                if value == 'Never':
                    element.execNever.setChecked(True)
                break
            key = '/{}/Solver/{}'.format(name, key)
            parameter = element.generalOptions.qhash[key]
            self._changeSettings(parameter, value)

        if len(data) == 0:
            return


    def _general(self, block):
        """Change settings in the general setup of the Elmer module

        Args:
        -----
        block: str
            String containing the settings of the general setup
        """

        # get the general setups window
        ui = self._ewh.gsWindow

        # split rows
        data = block.split('\n')

        title = data.pop(0)

        if title == 'Header':
            if 'CHECK KEYWORDS' in data[0]:
                ui.checkKeywordsWarn.setChecked(True)
                data.pop(0)
            else:
                ui.checkKeywordsWarn.setChecked(False)
                a, b = data.pop(0).strip().split(' ')[2:]
                ui.meshDBEdit1.setText(a)
                ui.meshDBEdit2.setText(b)
                a = data.pop(0).strip().split(' ')[2:]
                ui.includePathEdit.setText(a)
                a = data.pop(0).strip().split(' ')[2:]
                ui.resultsDirectoryEdit.setText(a)
                text = '\n'.join(data)
                ui.headerFreeTextEdit.setText(text)
        if title == 'Simulation':
            a = data.pop(0).split('=')[1].strip()
            idx = ui.maxOutputLevelCombo.findText(a)
            ui.maxOutputLevelCombo.setCurrentIndex(idx)
            a = data.pop(0).split('=')[1].strip()
            idx = ui.coordinateSystemCombo.findText(a)
            ui.coordinateSystemCombo.setCurrentIndex(idx)
            a = data.pop(0).split('=')[1].strip()
            ui.coordinateMappingEdit.setText(a)
            a = data.pop(0).split('=')[1].strip()
            idx = ui.simulationTypeCombo.findText(a)
            ui.simulationTypeCombo.setCurrentIndex(idx)
            a = data.pop(0).split('=')[1].strip()
            ui.steadyStateMaxIterEdit.setText(a)
            a = data.pop(0).split('=')[1].strip()
            ui.outputIntervalsEdit.setText(a)
            a = data.pop(0).split('=')[1].strip()
            idx = ui.timesteppingMethodCombo.findText(a)
            ui.timesteppingMethodCombo.setCurrentIndex(idx)
            a = data.pop(0).split('=')[1].strip()
            idx = ui.bdfOrderCombo.findText(a)
            ui.bdfOrderCombo.setCurrentIndex(idx)
            a = data.pop(0).split('=')[1].strip()
            ui.timeStepIntervalsEdit.setText(a)
            a = data.pop(0).split('=')[1].strip()
            ui.timestepSizesEdit.setText(a)
            a = data.pop(0).split('=')[1].strip()
            ui.solverInputFileEdit.setText(a)
            a = data.pop(0).split('=')[1].strip()
            ui.postFileEdit.setText(a)
            text = '\n'.join(data)
            ui.simulationFreeTextEdit.setText(text)
        if title == 'Constants':
            a = data.pop(0).split('=')[1].strip()
            idx = ui.gravityEdit.setText(a)
            a = data.pop(0).split('=')[1].strip()
            idx = ui.stefanBoltzmannEdit.setText(a)
            a = data.pop(0).split('=')[1].strip()
            idx = ui.vacuumPermittivityEdit.setText(a)
            a = data.pop(0).split('=')[1].strip()
            idx = ui.boltzmannEdit.setText(a)
            a = data.pop(0).split('=')[1].strip()
            idx = ui.unitChargeEdit.setText(a)
            text = '\n'.join(data)
            ui.constantsFreeTextEdit.setText(text)