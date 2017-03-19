#from operator import attrgetter

#import elmer_window_handler

#ewh = elmer_window_handler.elmerWindowHandler()

def write_sif(ewh):

    def writeToSif(str_val):
        print(str_val)

    def addSifLine(key, val):
        if val !='':
            writeToSif(key + val)

    def addSifLineBool(key, val):
        if val:
            writeToSif(key + 'True')
        else:
            writeToSif(key + 'False') 

    def makeSifEntry(parameter): 
        sifName = str(parameter.elem.firstChildElement('SifName').text()).strip()
        if sifName == '':
            sifName = str(parameter.elem.firstChildElement('Name').text()).strip()
        sifName = '  ' + sifName + ' = '
        widgetType = parameter.elem.attribute('Widget', 'Edit')
        if widgetType == 'Edit':
            sifValue = str(parameter.widget.text()).strip()
            addSifLine(sifName, sifValue)
        elif widgetType == 'TextEdit':
            sifValue = parameter.widget.toPlainText()
            addSifLine('', sifValue)
        elif widgetType == 'Combo':
            sifValue = str(parameter.widget.currentText()).strip()
            if sifValue != 'None':
                addSifLine(sifName, sifValue)
        elif widgetType == 'CheckBox':
            defaultValue = str(parameter.elem.firstChildElement('DefaultValue').text()).strip() == 'True'
            sifValue = parameter.widget.isChecked()
            if sifValue != defaultValue:
                addSifLineBool(sifName, sifValue)
        elif widgetType == 'Label':
            sifValue = ''
        else:
            print('WARNING: unknown widget type ' + widgetType)

    class SolverListItem:
        Name = ''
        Equations = []
        Priorities = []
        Number = 0

    print('write_sif')
    print('----------------------------------------')

    #general setup
    #-----------------

    ui = ewh._gsWindow

    #makeHeaderBlock()
    print('Header')
    if ui.checkKeywordsWarn.isChecked():
        print('  CHECK KEYWORDS Warn')
    print('  Mesh DB "' + str(ui.meshDBEdit1.text()).strip() + '" "' + str(ui.meshDBEdit2.text()).strip() + '"')
    print('  Include Path "' + str(ui.includePathEdit.text()).strip() + '"')
    print('  Results Directory "' + str(ui.resultsDirectoryEdit.text()).strip() + '"')
    FreeText = str(ui.headerFreeTextEdit.toPlainText()).splitlines()
    for line in FreeText:
        addSifLine('  ', line.strip())
    print('End')
    print('')
    
    #makeSimulationBlock()
    print('Simulation')
    addSifLine('  Max Output Level = ',  str(ui.maxOutputLevelCombo.currentText()).strip())
    addSifLine('  Coordinate System = ', str(ui.coordinateSystemCombo.currentText()).strip())
    addSifLine('  Coordinate Mapping(3) = ', str(ui.coordinateMappingEdit.text()).strip())
    addSifLine('  Simulation Type = ', str(ui.simulationTypeCombo.currentText()).strip())
    addSifLine('  Steady State Max Iterations = ', str(ui.steadyStateMaxIterEdit.text()).strip())
    addSifLine('  Output Intervals = ', str(ui.outputIntervalsEdit.text()).strip())
    addSifLine('  Timestepping Method = ', str(ui.timesteppingMethodCombo.currentText()).strip())
    addSifLine('  BDF Order = ', str(ui.bdfOrderCombo.currentText()).strip())
    addSifLine('  Timestep intervals = ', str(ui.timeStepIntervalsEdit.text()).strip())
    addSifLine('  Timestep Sizes = ', str(ui.timestepSizesEdit.text()).strip())
    addSifLine('  Solver Input File = ', str(ui.solverInputFileEdit.text()).strip())
    addSifLine('  Post File = ', str(ui.postFileEdit.text()).strip())
    FreeText = str(ui.simulationFreeTextEdit.toPlainText()).splitlines()
    for line in FreeText:
        addSifLine('  ', line.strip())
    print('End')
    print('')
    
    #makeConstantsBlock()
    print('Constants')
    addSifLine('  Gravity(4) = ', str(ui.gravityEdit.text()).strip())
    addSifLine('  Stefan Boltzmann = ', str(ui.stefanBoltzmannEdit.text()).strip())
    addSifLine('  Permittivity of Vacuum = ', str(ui.vacuumPermittivityEdit.text()).strip())
    addSifLine('  Boltzmann Constant = ', str(ui.boltzmannEdit.text()).strip())
    addSifLine('  Unit Charge = ', str(ui.unitChargeEdit.text()).strip())
    FreeText = str(ui.constantsFreeTextEdit.toPlainText()).splitlines()
    for line in FreeText:
        addSifLine('  ', line.strip())
    print('End')
    print('')

	#makeBodyBlocks()
    count = 0
    for objName in ewh._elementProperties:
        properties = ewh._elementProperties[objName]
        if properties.objectName() == 'bodyPropertyDialog':
            count += 1
            print('Body ' + str(count))
            print('  ! Target Bodies(1) = TODO')
            print('  Name = "' + objName + '"')
            addSifLine('  Equation = ', str(properties.equationCombo.currentIndex()).strip())
            addSifLine('  Material = ', str(properties.materialCombo.currentIndex()).strip())
            addSifLine('  Body Force = ', str(properties.bodyForceCombo.currentIndex()).strip())
            addSifLine('  Initial Condition = ', str(properties.initialConditionCombo.currentIndex()).strip())
            # use names instead of numbers
            #addSifLine('  Equation = ', '"'+str(properties.equation).strip()+'"')
            #addSifLine('  Material = ', '"'+str(properties.material).strip()+'"')
            #addSifLine('  Body Force = ', '"'+str(properties.force).strip()+'"')
            #addSifLine('  Initial Condition = ', '"'+str(properties.initial).strip()+'"')
            print('End')
            print('')

    #makeSolverBlocks
    i_solver = -1
    count_solver = 0
    SolverList = []
    for i_solver, element in enumerate(ewh._solverParameterEditor):
        newSolver = SolverListItem()
        newSolver.Name = str(element.solverName)
        # Remark: why do we need to initialize here (see class definition for SolverListItem)?
        newSolver.Equations = []
        newSolver.Priorities = []
        newSolver.Number = 0

        # find active solvers: loop over equations
        for eq in ewh._equationEditor:
            key = '/' + newSolver.Name + '/Equation/Active/' + str(eq.ID)
            if eq.qhash[key].widget.isChecked():
                newSolver.Equations.append(eq.ID+1) # Equation numbering starts with 1 in sif!
                prio = str(eq.qhash['/' + newSolver.Name + '/Equation/Priority/' + str(eq.ID)].widget.text()).strip()
                if prio != '':
                    prio_i = int(prio)
                else:
                    prio_i = 0 
                newSolver.Priorities.append(prio_i)

                #for key, value in eq.qhash.iteritems():
                #    if (newSolver.Name + '/Equation/Active' in key) and (eq.qhash[key].widget.isChecked()):

                # print(newSolver.Name + ' Equations: '+str(newSolver.Equations))
        if newSolver.Equations != []:
            # assign number to solver and append it to list only if active
            # may be changed in a future version
            count_solver += 1
            newSolver.Number = count_solver
            SolverList.append(newSolver)
            print('Solver ' + str(count_solver))
            print('  Equation = ' + element.solverName)
            #print(element.generalOptions.qhash)
            addSifLine('  Procedure = ', str(element.generalOptions.qhash[str('/'+element.solverName+'/Solver/Procedure/'+str(i_solver))].widget.text()).strip())
            key = str('/'+element.solverName+'/Solver/Variable/'+str(i_solver))
            if key in element.generalOptions.qhash:
                addSifLine('  Variable = ', str(element.generalOptions.qhash[key].widget.text()).strip())                    
                print('! ToDo: DOFs')
            for key in element.generalOptions.qhash.keys():
                value = element.generalOptions.qhash[key]
                if (str(element.solverName + '/Solver') in key) and not(any(s in key for s in ['Variable','Procedure'])): 
                    #print('  !' + key)
                    makeSifEntry(value)
                    #eq = ewh._equationEditor
                    #eq[0] -> Equation 1, eq[1] -> Equation 2
                    #str(eq[0].qhash['/Heat Equation/Equation/Active/0'].elem.attribute("Widget", "Edit")) -> 'CheckBox'
                    #eq[0].qhash['/Heat Equation/Equation/Active/0'].widget.isChecked() -> False

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
            addSifLine('  Exec Solver = ', str(val).strip())

            hasMatrix = True
            key = str('/'+element.solverName+'/Solver/No Matrix Equation/'+str(i_solver))
            if key in element.generalOptions.qhash:
                value = element.generalOptions.qhash[key]
                if (value.elem.attribute('Widget', 'Edit') == 'CheckBox') and value.widget.isChecked():
                    hasMatrix = False
            
            if hasMatrix:
                addSifLineBool('  Stabilize = ', element.stabilizeCheck.isChecked())
                addSifLineBool('  Bubbles = ', element.bubblesCheck.isChecked())
                addSifLineBool('  Lumped Mass Matrix = ', element.lumpedMassCheck.isChecked())
                addSifLineBool('  Optimize Bandwidth = ', element.optimizeBandwidthCheck.isChecked())
    
                # Steady State
                addSifLine('  Steady State Convergence Tolerance = ', str(element.steadyStateConvergenceToleranceEdit.text()).strip())
                if str(element.steadyStateConvergenceMeasureCombo.currentText()).strip() != "Norm":
                    addSifLine('  Steady State Convergence Measure = ', str(element.steadyStateConvergenceMeasureCombo.currentText()).strip())
    
                # Nonlinear System
                addSifLine('  Nonlinear System Convergence Tolerance = ', str(element.nonlinSystemConvergenceToleranceEdit.text()).strip())
                addSifLine('  Nonlinear System Max Iterations = ', str(element.nonlinSystemMaxIterationEdit.text()).strip())
                addSifLine('  Nonlinear System Relaxation Factor = ', str(element.nonlinSystemRelaxationFactorEdit.text()).strip())
                if str(element.nonlinSystemConvergenceMeasureCombo.currentText()).strip() != "Norm":
                    addSifLine('  Nonlinear System Convergence Measure = ', str(element.steadyStateConvergenceMeasureCombo.currentText()).strip())
                addSifLine('  Nonlinear System Newton After Iterations = ', str(element.nonlinSystemNewtonAfterIterEdit.text()).strip())
                addSifLine('  Nonlinear System Newton After Tolerance = ', str(element.nonlinSystemNewtonAfterTolEdit.text()).strip())
    
                # Linear System
                if element.linearSystemSolverDirect.isChecked():
                    addSifLine('  Linear System Solver = ', 'Direct')
                    addSifLine("  Linear System Direct Method = ", str(element.linearSystemDirectMethod.currentText()).strip())
                elif element.linearSystemSolverIterative.isChecked():
                    addSifLine('  Linear System Solver = ', 'Iterative');
                    addSifLine('  Linear System Iterative Method = ', str(element.linearSystemIterativeMethod.currentText()).strip())
                    addSifLine('  Linear System Max Iterations = ', str(element.linearSystemMaxIterationsEdit.text()).strip())
                    addSifLine('  Linear System Convergence Tolerance = ', str(element.linearSystemConvergenceToleranceEdit.text()).strip())
                    addSifLine('  BiCGstabl polynomial degree = ', str(element.linearSystemBiCGstablPolDeg.text()).strip())
                    if not (element.useHypre.isChecked()):
                        addSifLine('  Linear System Preconditioning = ', str(element.linearSystemPreconditioning.currentText()).strip())
                    addSifLine('  Linear System ILUT Tolerance = ', str(element.linearSystemILUTToleranceEdit.text()).strip())
                    addSifLineBool("  Linear System Abort Not Converged = ", element.linearSystemAbortWhenNotConvergedCheck.isChecked())
                    addSifLine('  Linear System Residual Output = ', str(element.linearSystemResiduaOutputEdit.text()).strip())
                    addSifLine('  Linear System Precondition Recompute = ', str(element.linearSystemPreconditionRecomputeEdit.text()).strip())
                elif element.linearSystemSolverMultigrid.isChecked():
                    addSifLine('  Linear System Solver = ', 'Multigrid');
                addSifLine('  ! ToDo: Add missing parameters!!', '')
    
                # Parallel
                if element.useHypre.isChecked():
                    addSifLine("  Linear System Use HYPRE = ", "True");
                    if element.useParasails.isChecked():
                        addSifLine('  Linear System Preconditioning = ', 'ParaSails');
                        addSifLine('  ParaSails Threshold = ', str(element.thresholdEdit.text()).strip())
                        addSifLine('  ParaSails Filter = ', str(element.filterEdit.text()).strip())
                        addSifLine('  ParaSails MaxLevel = ', str(element.maxLevelEdit.text()).strip())
                        addSifLine('  ParaSails Symmetry = ', str(element.symmetryEdit.text()).strip())
                    if(element.useBoomerAMG.isChecked()):
                        addSifLine('  Linear System Preconditioning = ', 'BoomerAMG');
                        addSifLine('  BoomerAMG Relax Type = ', str(element.boomerRelaxation.currentIndex()).strip())
                        addSifLine('  BoomerAMG Coarsen Type = ', str(element.boomerCoarsening.currentIndex()).strip())
                        addSifLine('  BoomerAMG Num Sweeps = ', str(element.boomerSweeps.text()).strip())
                        addSifLine('  BoomerAMG Max Levels = ', str(element.boomerMaxLevels.text()).strip())
                        addSifLine('  BoomerAMG Interpolation = ', str(element.boomerInterpolation.currentIndex()))
                        addSifLine('  BoomerAMG Smooth Type = ', str(element.boomerSmoother.currentIndex()));
                        addSifLine('  BoomerAMG Cycle Type = ', str(element.boomerCycle.currentIndex()))
    
                #Adaptive
                if element.adaptiveMeshRefinementCheck.isChecked():
                    addSifLineBool('  Adaptive Mesh Refinement = ', element.adaptiveMeshRefinementCheck.isChecked())
                    addSifLine('  Adaptive Mesh Name = ', str(element.adaptiveMeshNameEdit.text()).strip())
                    addSifLineBool('  Adaptive Remesh = ', element.adaptiveReMeshCheck.isChecked())
                    addSifLineBool('  Adaptive Save Mesh = ', element.adaptiveSaveMeshCheck.isChecked())
                    addSifLineBool('  Adaptive Coarsening = ', element.adaptiveCoarseningCheck.isChecked())
                    addSifLine('  Adaptive Error Limit = ', str(element.adaptiveErrorLimitEdit.text()).strip())
                    addSifLine('  Adaptive Min H = ', str(element.adaptiveMinHEdit.text()).strip())
                    addSifLine('  Adaptive Max H = ', str(element.adaptiveMaxHEdit.text()).strip())
                    addSifLine('  Adaptive Max Change = ', str(element.adaptiveMaxChangeEdit.text()).strip())
    
                addSifLine('  ! Multigrid: ', 'TODO')
                
            writeToSif('End')
            writeToSif('')
	
	#makeEquationBlocks
    idx = 0
    for element in ewh._equationEditor:
        idx += 1
        writeToSif('Equation ' + str(idx))
        writeToSif('  Name = "' + str(element.nameEdit.text()).strip() + '"')
        activeSolvers = []
        N_activeSolvers = 0
        for sol in SolverList:
            # print('Solver '+str(sol.Number)+': '+sol.Name+' Equations'+str(sol.Equations))
            if idx in sol.Equations:
                activeSolvers.append([sol.Priorities[sol.Equations.index(idx)],sol.Number]) 
                # = activeSolvers + ' ' + str(sol.Number)
                N_activeSolvers += 1
        activeSolvers = sorted(activeSolvers, reverse=True) # higher priority first
        #print('+++ active Solvers '+str(activeSolvers))
        actSolStr = ''
        for s_num in [x[1] for x in activeSolvers]:
            actSolStr += str(s_num) + ' '
        writeToSif('  Active Solvers(' + str(N_activeSolvers) + ') = ' +  actSolStr.strip())
        writeToSif('End')
        writeToSif('')
           	

    #Materials
    for mat in ewh._materialEditor:
        addSifLine('Material ', str(mat.ID+1))
        addSifLine('  Name = ', '"'+str(mat.nameEdit.text()).strip()+'"')
        for key, value in mat.qhash.iteritems(): 
            makeSifEntry(value)
        writeToSif('End')
        writeToSif('')

    #Body Forces
    for bf in ewh._bodyForceEditor:
        addSifLine('Body Force ', str(bf.ID+1))
        addSifLine('  Name = ', '"'+str(bf.nameEdit.text()).strip()+'"')
        for key, value in bf.qhash.iteritems(): 
            makeSifEntry(value)
        writeToSif('End')
        writeToSif('')

    #Boundary Conditions
    for bc in ewh._boundaryConditionEditor:
        TargetBoundaries = []
        TargetBoundaryNumbers = []
        for objName in ewh._elementProperties:
            properties = ewh._elementProperties[objName]
            if (properties.objectName() == 'boundaryPropertyDialog') and (properties.boundaryConditionCombo.currentIndex() == bc.ID+1):
                TargetBoundaries.append(objName)
                #TargetBoundaryNumbers.append()
        if len(TargetBoundaries) > 0:
            bcStr = ''
            #for s_num in TargetBoundaryNumbers:
            #    bcStr += str(s_num) + ' '
            for x in TargetBoundaries:
                bcStr += x + ' '   
            addSifLine('BoundaryCondition ', str(bc.ID+1))
            writeToSif('  Target Boundaries('+str(len(TargetBoundaries))+') = ' + bcStr )
            writeToSif('  Name = ' + '"'+str(bc.nameEdit.text()).strip()+'"')
            for key, value in bc.qhash.iteritems(): 
                makeSifEntry(value)
            writeToSif('! ToDo: Periodic BCs')
            writeToSif('End')
            writeToSif('')
    
    
    #Initial Conditions
    for ic in ewh._initialConditionEditor:
        addSifLine('Initial Condition ', str(ic.ID+1))
        addSifLine('  Name = ', '"'+str(ic.nameEdit.text()).strip()+'"')
        for key, value in ic.qhash.iteritems(): 
            makeSifEntry(value)
        writeToSif('End')
        writeToSif('')
    print('----------------------------------------')

