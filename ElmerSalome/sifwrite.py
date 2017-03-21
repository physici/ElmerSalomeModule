class SolverListItem:
    Name = ''
    Equations = []
    Priorities = []
    Number = 0


class SifWriter():

    def __init__(self, ewh):
        # public
        self.file = None

        # private
        self._ewh = ewh
        self._fObject = None

    def _writeToSif(self, str_val):
        if not self._fObject:
            print(str_val)
        else:
            self._fObject.write('{}\n'.format(str_val))

    def _addSifLine(self, key, val):
        if val != '':
            self._writeToSif(key + val)

    def _addSifLineBool(self, key, val):
        if val:
            self._writeToSif(key + 'True')
        else:
            self._writeToSif(key + 'False')

    def _makeSifEntry(self, parameter):
        sifName = str(parameter.elem.firstChildElement('SifName').text()).strip()
        if sifName == '':
            sifName = str(parameter.elem.firstChildElement('Name').text()).strip()
        sifName = '  ' + sifName + ' = '
        widgetType = parameter.elem.attribute('Widget', 'Edit')
        if widgetType == 'Edit':
            sifValue = str(parameter.widget.text()).strip()
            self._addSifLine(sifName, sifValue)
        elif widgetType == 'TextEdit':
            sifValue = parameter.widget.toPlainText()
            self._addSifLine('', sifValue)
        elif widgetType == 'Combo':
            sifValue = str(parameter.widget.currentText()).strip()
            if sifValue != 'None':
                self._addSifLine(sifName, sifValue)
        elif widgetType == 'CheckBox':
            defaultValue = str(parameter.elem.firstChildElement('DefaultValue').text()).strip() == 'True'
            sifValue = parameter.widget.isChecked()
            if sifValue != defaultValue:
                self._addSifLineBool(sifName, sifValue)
        elif widgetType == 'Label':
            sifValue = ''
        else:
            print('WARNING: unknown widget type ' + widgetType)


    def writeSif(self):
        print('write_sif')
        print('----------------------------------------')

        ui = self._ewh._gsWindow

        if self.file:
            obj = open(self.file, 'w')
            self._fObject = obj

        # makeHeaderBlock()
        self._writeToSif('Header')
        if ui.checkKeywordsWarn.isChecked():
            self._writeToSif('  CHECK KEYWORDS Warn')
        self._writeToSif('  Mesh DB "' + str(ui.meshDBEdit1.text()).strip() + '" "' + str(ui.meshDBEdit2.text()).strip() + '"')
        self._writeToSif('  Include Path "' + str(ui.includePathEdit.text()).strip() + '"')
        self._writeToSif('  Results Directory "' + str(ui.resultsDirectoryEdit.text()).strip() + '"')
        FreeText = str(ui.headerFreeTextEdit.toPlainText()).splitlines()
        for line in FreeText:
            self._addSifLine('  ', line.strip())
        self._writeToSif('End')
        self._writeToSif('')

        # makeSimulationBlock()
        self._writeToSif('Simulation')
        self._addSifLine('  Max Output Level = ',  str(ui.maxOutputLevelCombo.currentText()).strip())
        self._addSifLine('  Coordinate System = ', str(ui.coordinateSystemCombo.currentText()).strip())
        self._addSifLine('  Coordinate Mapping(3) = ', str(ui.coordinateMappingEdit.text()).strip())
        self._addSifLine('  Simulation Type = ', str(ui.simulationTypeCombo.currentText()).strip())
        self._addSifLine('  Steady State Max Iterations = ', str(ui.steadyStateMaxIterEdit.text()).strip())
        self._addSifLine('  Output Intervals = ', str(ui.outputIntervalsEdit.text()).strip())
        self._addSifLine('  Timestepping Method = ', str(ui.timesteppingMethodCombo.currentText()).strip())
        self._addSifLine('  BDF Order = ', str(ui.bdfOrderCombo.currentText()).strip())
        self._addSifLine('  Timestep intervals = ', str(ui.timeStepIntervalsEdit.text()).strip())
        self._addSifLine('  Timestep Sizes = ', str(ui.timestepSizesEdit.text()).strip())
        self._addSifLine('  Solver Input File = ', str(ui.solverInputFileEdit.text()).strip())
        self._addSifLine('  Post File = ', str(ui.postFileEdit.text()).strip())
        self._writeToSif('  Use Mesh Names = Logical True')
        FreeText = str(ui.simulationFreeTextEdit.toPlainText()).splitlines()
        for line in FreeText:
            self._addSifLine('  ', line.strip())
        self._writeToSif('End')
        self._writeToSif('')

        # makeConstantsBlock()
        self._writeToSif('Constants')
        self._addSifLine('  Gravity(4) = ', str(ui.gravityEdit.text()).strip())
        self._addSifLine('  Stefan Boltzmann = ', str(ui.stefanBoltzmannEdit.text()).strip())
        self._addSifLine('  Permittivity of Vacuum = ', str(ui.vacuumPermittivityEdit.text()).strip())
        self._addSifLine('  Boltzmann Constant = ', str(ui.boltzmannEdit.text()).strip())
        self._addSifLine('  Unit Charge = ', str(ui.unitChargeEdit.text()).strip())
        FreeText = str(ui.constantsFreeTextEdit.toPlainText()).splitlines()
        for line in FreeText:
            self._addSifLine('  ', line.strip())
        self._writeToSif('End')
        self._writeToSif('')

        # makeBodyBlocks()
        count = 0
        for objName in self._ewh._elementProperties:
            properties = self._ewh._elementProperties[objName]
            if properties.objectName() == 'bodyPropertyDialog':
                count += 1
                self._writeToSif('Body ' + str(count))
                self._writeToSif('  ! Target Bodies(1) = TODO')
                self._writeToSif('  Name = "' + objName + '"')
                self._addSifLine('  Equation = ', str(properties.equationCombo.currentIndex()).strip())
                self._addSifLine('  Material = ', str(properties.materialCombo.currentIndex()).strip())
                self._addSifLine('  Body Force = ', str(properties.bodyForceCombo.currentIndex()).strip())
                self._addSifLine('  Initial Condition = ', str(properties.initialConditionCombo.currentIndex()).strip())
                # use names instead of numbers
                #_addSifLine('  Equation = ', '"'+str(properties.equation).strip()+'"')
                #_addSifLine('  Material = ', '"'+str(properties.material).strip()+'"')
                #_addSifLine('  Body Force = ', '"'+str(properties.force).strip()+'"')
                #_addSifLine('  Initial Condition = ', '"'+str(properties.initial).strip()+'"')
                self._writeToSif('End')
                self._writeToSif('')

        # makeSolverBlocks
        i_solver = -1
        count_solver = 0
        SolverList = []
        for i_solver, element in enumerate(self._ewh._solverParameterEditor):
            newSolver = SolverListItem()
            newSolver.Name = str(element.solverName)
            # Remark: why do we need to initialize here (see class definition for SolverListItem)?
            newSolver.Equations = []
            newSolver.Priorities = []
            newSolver.Number = 0

            # find active solvers: loop over equations
            for eq in self._ewh._equationEditor:
                key = '/' + newSolver.Name + '/Equation/Active/' + str(eq.ID)
                if eq.qhash[key].widget.isChecked():
                    newSolver.Equations.append(eq.ID+1) # Equation numbering starts with 1 in sif!
                    prio = str(eq.qhash['/' + newSolver.Name + '/Equation/Priority/' + str(eq.ID)].widget.text()).strip()
                    if prio != '':
                        prio_i = int(prio)
                    else:
                        prio_i = 0
                    newSolver.Priorities.append(prio_i)

            if newSolver.Equations != []:
                # assign number to solver and append it to list only if active
                # may be changed in a future version
                count_solver += 1
                newSolver.Number = count_solver
                SolverList.append(newSolver)
                self._writeToSif('Solver ' + str(count_solver))
                self._writeToSif('  Equation = ' + element.solverName)
                self._addSifLine('  Procedure = ', str(element.generalOptions.qhash[str('/'+element.solverName+'/Solver/Procedure/'+str(i_solver))].widget.text()).strip())
                key = str('/'+element.solverName+'/Solver/Variable/'+str(i_solver))
                if key in element.generalOptions.qhash:
                    self._addSifLine('  Variable = ', str(element.generalOptions.qhash[key].widget.text()).strip())
                    self._writeToSif('! ToDo: DOFs')
                for key in element.generalOptions.qhash.keys():
                    value = element.generalOptions.qhash[key]
                    if (str(element.solverName + '/Solver') in key) and not(any(s in key for s in ['Variable','Procedure'])):
                        self._makeSifEntry(value)
    
                # General
                val = ''
                if element.execAlways.isChecked():
                    val = 'Always'
                if element.execBeforeSimulation.isChecked():
                    val = 'Before Simulation'
                if element.execAfterSimulation.isChecked():
                    val = 'After Simulation'
                if element.execBeforeTimestep.isChecked():
                    val = 'Before Timestep'
                if element.execAfterTimestep.isChecked():
                    val = 'After Timestep'
                if element.execNever.isChecked():
                    val = 'Never'
                self._addSifLine('  Exec Solver = ', str(val).strip())

                hasMatrix = True
                key = str('/'+element.solverName+'/Solver/No Matrix Equation/'+str(i_solver))
                if key in element.generalOptions.qhash:
                    value = element.generalOptions.qhash[key]
                    if (value.elem.attribute('Widget', 'Edit') == 'CheckBox') and value.widget.isChecked():
                        hasMatrix = False

                if hasMatrix:
                    self. _addSifLineBool('  Stabilize = ', element.stabilizeCheck.isChecked())
                    self. _addSifLineBool('  Bubbles = ', element.bubblesCheck.isChecked())
                    self. _addSifLineBool('  Lumped Mass Matrix = ', element.lumpedMassCheck.isChecked())
                    self. _addSifLineBool('  Optimize Bandwidth = ', element.optimizeBandwidthCheck.isChecked())

                    # Steady State
                    self. _addSifLine('  Steady State Convergence Tolerance = ', str(element.steadyStateConvergenceToleranceEdit.text()).strip())
                    if str(element.steadyStateConvergenceMeasureCombo.currentText()).strip() != "Norm":
                        self._addSifLine('  Steady State Convergence Measure = ', str(element.steadyStateConvergenceMeasureCombo.currentText()).strip())

                    # Nonlinear System
                    self._addSifLine('  Nonlinear System Convergence Tolerance = ', str(element.nonlinSystemConvergenceToleranceEdit.text()).strip())
                    self._addSifLine('  Nonlinear System Max Iterations = ', str(element.nonlinSystemMaxIterationEdit.text()).strip())
                    self._addSifLine('  Nonlinear System Relaxation Factor = ', str(element.nonlinSystemRelaxationFactorEdit.text()).strip())
                    if str(element.nonlinSystemConvergenceMeasureCombo.currentText()).strip() != "Norm":
                        self._addSifLine('  Nonlinear System Convergence Measure = ', str(element.steadyStateConvergenceMeasureCombo.currentText()).strip())
                    self._addSifLine('  Nonlinear System Newton After Iterations = ', str(element.nonlinSystemNewtonAfterIterEdit.text()).strip())
                    self._addSifLine('  Nonlinear System Newton After Tolerance = ', str(element.nonlinSystemNewtonAfterTolEdit.text()).strip())

                    # Linear System
                    if element.linearSystemSolverDirect.isChecked():
                        self._addSifLine('  Linear System Solver = ', 'Direct')
                        self._addSifLine("  Linear System Direct Method = ", str(element.linearSystemDirectMethod.currentText()).strip())
                    elif element.linearSystemSolverIterative.isChecked():
                        self._addSifLine('  Linear System Solver = ', 'Iterative');
                        self._addSifLine('  Linear System Iterative Method = ', str(element.linearSystemIterativeMethod.currentText()).strip())
                        self._addSifLine('  Linear System Max Iterations = ', str(element.linearSystemMaxIterationsEdit.text()).strip())
                        self._addSifLine('  Linear System Convergence Tolerance = ', str(element.linearSystemConvergenceToleranceEdit.text()).strip())
                        self._addSifLine('  BiCGstabl polynomial degree = ', str(element.linearSystemBiCGstablPolDeg.text()).strip())
                        if not (element.useHypre.isChecked()):
                            self._addSifLine('  Linear System Preconditioning = ', str(element.linearSystemPreconditioning.currentText()).strip())
                        self._addSifLine('  Linear System ILUT Tolerance = ', str(element.linearSystemILUTToleranceEdit.text()).strip())
                        self._addSifLineBool("  Linear System Abort Not Converged = ", element.linearSystemAbortWhenNotConvergedCheck.isChecked())
                        self._addSifLine('  Linear System Residual Output = ', str(element.linearSystemResiduaOutputEdit.text()).strip())
                        self._addSifLine('  Linear System Precondition Recompute = ', str(element.linearSystemPreconditionRecomputeEdit.text()).strip())
                    elif element.linearSystemSolverMultigrid.isChecked():
                        self._addSifLine('  Linear System Solver = ', 'Multigrid');
                    self._addSifLine('  ! ToDo: Add missing parameters!!', '')

                    # Parallel
                    if element.useHypre.isChecked():
                        self._addSifLine("  Linear System Use HYPRE = ", "True");
                        if element.useParasails.isChecked():
                            self._addSifLine('  Linear System Preconditioning = ', 'ParaSails');
                            self._addSifLine('  ParaSails Threshold = ', str(element.thresholdEdit.text()).strip())
                            self._addSifLine('  ParaSails Filter = ', str(element.filterEdit.text()).strip())
                            self._addSifLine('  ParaSails MaxLevel = ', str(element.maxLevelEdit.text()).strip())
                            self._addSifLine('  ParaSails Symmetry = ', str(element.symmetryEdit.text()).strip())
                        if(element.useBoomerAMG.isChecked()):
                            self._addSifLine('  Linear System Preconditioning = ', 'BoomerAMG');
                            self._addSifLine('  BoomerAMG Relax Type = ', str(element.boomerRelaxation.currentIndex()).strip())
                            self._addSifLine('  BoomerAMG Coarsen Type = ', str(element.boomerCoarsening.currentIndex()).strip())
                            self._addSifLine('  BoomerAMG Num Sweeps = ', str(element.boomerSweeps.text()).strip())
                            self._addSifLine('  BoomerAMG Max Levels = ', str(element.boomerMaxLevels.text()).strip())
                            self._addSifLine('  BoomerAMG Interpolation = ', str(element.boomerInterpolation.currentIndex()))
                            self._addSifLine('  BoomerAMG Smooth Type = ', str(element.boomerSmoother.currentIndex()));
                            self._addSifLine('  BoomerAMG Cycle Type = ', str(element.boomerCycle.currentIndex()))

                    # Adaptive
                    if element.adaptiveMeshRefinementCheck.isChecked():
                        self._addSifLineBool('  Adaptive Mesh Refinement = ', element.adaptiveMeshRefinementCheck.isChecked())
                        self._addSifLine('  Adaptive Mesh Name = ', str(element.adaptiveMeshNameEdit.text()).strip())
                        self._addSifLineBool('  Adaptive Remesh = ', element.adaptiveReMeshCheck.isChecked())
                        self._addSifLineBool('  Adaptive Save Mesh = ', element.adaptiveSaveMeshCheck.isChecked())
                        self._addSifLineBool('  Adaptive Coarsening = ', element.adaptiveCoarseningCheck.isChecked())
                        self._addSifLine('  Adaptive Error Limit = ', str(element.adaptiveErrorLimitEdit.text()).strip())
                        self._addSifLine('  Adaptive Min H = ', str(element.adaptiveMinHEdit.text()).strip())
                        self._addSifLine('  Adaptive Max H = ', str(element.adaptiveMaxHEdit.text()).strip())
                        self._addSifLine('  Adaptive Max Change = ', str(element.adaptiveMaxChangeEdit.text()).strip())

                    self._addSifLine('  ! Multigrid: ', 'TODO')

                self._writeToSif('End')
                self._writeToSif('')

    	# makeEquationBlocks
        idx = 0
        for element in self._ewh._equationEditor:
            idx += 1
            self._writeToSif('Equation ' + str(idx))
            self._writeToSif('  Name = "' + str(element.nameEdit.text()).strip() + '"')
            activeSolvers = []
            N_activeSolvers = 0
            for sol in SolverList:
                if idx in sol.Equations:
                    activeSolvers.append([sol.Priorities[sol.Equations.index(idx)],sol.Number])
                    N_activeSolvers += 1
            activeSolvers = sorted(activeSolvers, reverse=True) # higher priority first
            actSolStr = ''
            for s_num in [x[1] for x in activeSolvers]:
                actSolStr += str(s_num) + ' '
            self._writeToSif('  Active Solvers(' + str(N_activeSolvers) + ') = ' +  actSolStr.strip())
            self._writeToSif('End')
            self._writeToSif('')

        # Materials
        for mat in self._ewh._materialEditor:
            self._addSifLine('Material ', str(mat.ID+1))
            self._addSifLine('  Name = ', '"'+str(mat.nameEdit.text()).strip()+'"')
            for key, value in mat.qhash.iteritems():
                self._makeSifEntry(value)
            self._writeToSif('End')
            self._writeToSif('')

        # Body Forces
        for bf in self._ewh._bodyForceEditor:
            self._addSifLine('Body Force ', str(bf.ID+1))
            self._addSifLine('  Name = ', '"'+str(bf.nameEdit.text()).strip()+'"')
            for key, value in bf.qhash.iteritems():
                self._makeSifEntry(value)
            self._writeToSif('End')
            self._writeToSif('')

        # Boundary Conditions
        x = 1
        for bc in self._ewh._boundaryConditionEditor:
            TargetBoundaries = []
            TargetBoundaryNumbers = []
            for objName in self._ewh._elementProperties:
                properties = self._ewh._elementProperties[objName]
                if (properties.objectName() == 'boundaryPropertyDialog') and (properties.boundaryConditionCombo.currentIndex() == bc.ID+1):
                    TargetBoundaries.append(objName)
            if len(TargetBoundaries) > 0:
                for name in TargetBoundaries:
                    self._addSifLine('BoundaryCondition ', str(x))
    #                self._writeToSif('  Target Boundaries('+str(len(TargetBoundaries))+') = ' + bcStr )
    #                self._writeToSif('  Name = ' + '"'+str(bc.nameEdit.text()).strip()+'"')
                    self._writeToSif('  Name = ' + '"'+str(name).strip()+'"')
                    for key, value in bc.qhash.iteritems():
                        self._makeSifEntry(value)
                    self._writeToSif('! ToDo: Periodic BCs')
                    self._writeToSif('End')
                    self._writeToSif('')
                    x += 1

        # Initial Conditions
        for ic in self._ewh._initialConditionEditor:
            self._addSifLine('Initial Condition ', str(ic.ID+1))
            self._addSifLine('  Name = ', '"'+str(ic.nameEdit.text()).strip()+'"')
            for key, value in ic.qhash.iteritems():
                self._makeSifEntry(value)
            self._writeToSif('End')
            self._writeToSif('')

        print('----------------------------------------')

        if self._fObject:
            self._fObject.close()
