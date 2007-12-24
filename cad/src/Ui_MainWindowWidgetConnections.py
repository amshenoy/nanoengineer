# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Ui_MainWindowWidgetConnects.py

Creates all connects for all Main Window widgets used in menus and toolbars.

@author: Mark
@version: $Id:$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

History:

2007-12-23: Moved all connect() calls from MWsemantics to here.
"""

from PyQt4 import QtCore
from PyQt4.Qt import SIGNAL

def setupUi(win):
    """
    Create all connects for all Main Window widgets used in menus and toolbars.

    @param win: NE1's mainwindow object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """

    win.connect(win.changeBackgroundColorAction,SIGNAL("triggered()"),win.changeBackgroundColor)
    win.connect(win.dispBallAction,SIGNAL("triggered()"),win.dispBall)
    win.connect(win.dispDefaultAction,SIGNAL("triggered()"),win.dispDefault)
    win.connect(win.dispElementColorSettingsAction,SIGNAL("triggered()"),win.dispElementColorSettings)
    win.connect(win.dispInvisAction,SIGNAL("triggered()"),win.dispInvis)
    win.connect(win.dispLightingAction,SIGNAL("triggered()"),win.dispLighting)
    win.connect(win.dispLinesAction,SIGNAL("triggered()"),win.dispLines)
    win.connect(win.dispObjectColorAction,SIGNAL("triggered()"),win.dispObjectColor)
    win.connect(win.dispResetAtomsDisplayAction,SIGNAL("triggered()"),win.dispResetAtomsDisplay)
    win.connect(win.dispResetChunkColorAction,SIGNAL("triggered()"),win.dispResetChunkColor)
    win.connect(win.dispShowInvisAtomsAction,SIGNAL("triggered()"),win.dispShowInvisAtoms)
    win.connect(win.dispTubesAction,SIGNAL("triggered()"),win.dispTubes)
    win.connect(win.dispCPKAction,SIGNAL("triggered()"),win.dispCPK)
    win.connect(win.dispHybridAction,SIGNAL("triggered()"),win.dispHybrid)

    win.connect(win.editAutoCheckpointingAction,SIGNAL("toggled(bool)"),win.editAutoCheckpointing)
    win.connect(win.editClearUndoStackAction,SIGNAL("triggered()"),win.editClearUndoStack)
    win.connect(win.editCopyAction,SIGNAL("triggered()"),win.editCopy)
    win.connect(win.editCutAction,SIGNAL("triggered()"),win.editCut)
    win.connect(win.editDeleteAction,SIGNAL("triggered()"),win.killDo)
    win.connect(win.editMakeCheckpointAction,SIGNAL("triggered()"),win.editMakeCheckpoint)
    win.connect(win.editPasteAction,SIGNAL("triggered()"),win.editPaste)
    win.connect(win.pasteFromClipboardAction, 
                 SIGNAL("triggered()"),
                 win.editPasteFromClipboard )

    win.connect(win.partLibAction, 
                 SIGNAL("triggered()"),
                 win.insertPartFromPartLib)

    win.connect(win.viewFullScreenAction, 
                 SIGNAL("toggled(bool)"), 
                 win.setViewFullScreen)
    win.connect(win.viewSemiFullScreenAction, 
                 SIGNAL("toggled(bool)"), 
                 win.setViewSemiFullScreen)

    win.connect(win.editPrefsAction,SIGNAL("triggered()"),win.editPrefs)
    win.connect(win.editRedoAction,SIGNAL("triggered()"),win.editRedo)
    win.connect(win.editUndoAction,SIGNAL("triggered()"),win.editUndo)
    win.connect(win.fileCloseAction,SIGNAL("triggered()"),win.fileClose)
    win.connect(win.fileExitAction,SIGNAL("triggered()"), win.close)
    win.connect(win.fileInsertAction,SIGNAL("triggered()"),win.fileInsert)
    win.connect(win.fileOpenAction,SIGNAL("triggered()"),win.fileOpen)
    win.connect(win.fileSaveAction,SIGNAL("triggered()"),win.fileSave)
    win.connect(win.fileSaveAsAction,SIGNAL("triggered()"),win.fileSaveAs)
    win.connect(win.fileSaveSelectionAction,SIGNAL("triggered()"),win.fileSaveSelection)
    win.connect(win.fileSetWorkDirAction,SIGNAL("triggered()"),win.fileSetWorkDir)
    win.connect(win.helpAboutAction,SIGNAL("triggered()"),win.helpAbout)
    win.connect(win.helpGraphicsCardAction,SIGNAL("triggered()"),win.helpGraphicsCard)
    win.connect(win.helpKeyboardShortcutsAction,SIGNAL("triggered()"),win.helpKeyboardShortcuts)
    win.connect(win.helpMouseControlsAction,SIGNAL("triggered()"),win.helpMouseControls)
    win.connect(win.helpWhatsThisAction,SIGNAL("triggered()"),win.helpWhatsThis)
    #win.connect(win.buildDnaAction,SIGNAL("triggered()"),win.insertDna)
    win.connect(win.buildDnaAction,SIGNAL("triggered()"),win.activateDnaTool)
    win.connect(win.insertCommentAction,SIGNAL("triggered()"),win.insertComment)
    win.connect(win.insertNanotubeAction,SIGNAL("triggered()"),win.insertNanotube)
    win.connect(win.insertGrapheneAction,SIGNAL("triggered()"),win.insertGraphene)

    win.connect(win.jigsAnchorAction,SIGNAL("triggered()"),win.makeAnchor)
    win.connect(win.jigsAngleAction,SIGNAL("triggered()"),win.makeMeasureAngle)
    win.connect(win.jigsAtomSetAction,SIGNAL("triggered()"),win.makeAtomSet)
    win.connect(win.jigsDihedralAction,SIGNAL("triggered()"),win.makeMeasureDihedral)
    win.connect(win.jigsDistanceAction,SIGNAL("triggered()"),win.makeMeasureDistance)
    win.connect(win.jigsESPImageAction,SIGNAL("triggered()"),win.makeESPImage)
    win.connect(win.jigsGamessAction,SIGNAL("triggered()"),win.makeGamess)
    win.connect(win.jigsGridPlaneAction,SIGNAL("triggered()"),win.makeGridPlane)

    win.connect(win.referencePlaneAction,SIGNAL("triggered()"),
                 win.createPlane)
    win.connect(win.referenceLineAction,SIGNAL("triggered()"),
                 win.createPolyLine)

    win.connect(win.jigsLinearMotorAction,
                 SIGNAL("triggered()"),
                 win.makeLinearMotor)

    win.connect(win.jigsMotorAction,
                 SIGNAL("triggered()"),
                 win.makeRotaryMotor)

    win.connect(win.jigsStatAction,SIGNAL("triggered()"),win.makeStat)
    win.connect(win.jigsThermoAction,SIGNAL("triggered()"),win.makeThermo)
    win.connect(win.modifyAlignCommonAxisAction,SIGNAL("triggered()"),win.modifyAlignCommonAxis)
    win.connect(win.modifyCenterCommonAxisAction,SIGNAL("triggered()"),win.modifyCenterCommonAxis)
    win.connect(win.modifyDehydrogenateAction,SIGNAL("triggered()"),win.modifyDehydrogenate)
    win.connect(win.modifyDeleteBondsAction,SIGNAL("triggered()"),win.modifyDeleteBonds)
    win.connect(win.modifyHydrogenateAction,SIGNAL("triggered()"),win.modifyHydrogenate)
    win.connect(win.modifyInvertAction,SIGNAL("triggered()"),win.modifyInvert)
    win.connect(win.modifyMergeAction,SIGNAL("triggered()"),win.modifyMerge)
    win.connect(win.makeChunkFromSelectedAtomsAction,
                 SIGNAL("triggered()"),win.makeChunkFromAtom)
    win.connect(win.modifyAdjustAllAction,SIGNAL("triggered()"),win.modifyAdjustAll)
    win.connect(win.modifyAdjustSelAction,SIGNAL("triggered()"),win.modifyAdjustSel)
    win.connect(win.modifyPassivateAction,SIGNAL("triggered()"),win.modifyPassivate)
    win.connect(win.modifySeparateAction,SIGNAL("triggered()"),win.modifySeparate)
    win.connect(win.modifyStretchAction,SIGNAL("triggered()"),win.modifyStretch)
    win.connect(win.panToolAction,SIGNAL("toggled(bool)"),win.panTool)
    win.connect(win.rotateToolAction,SIGNAL("toggled(bool)"),win.rotateTool)
    win.connect(win.saveNamedViewAction,SIGNAL("triggered()"),win.saveNamedView)
    win.connect(win.selectAllAction,SIGNAL("triggered()"),win.selectAll)
    win.connect(win.selectConnectedAction,SIGNAL("triggered()"),win.selectConnected)
    win.connect(win.selectContractAction,SIGNAL("triggered()"),win.selectContract)
    win.connect(win.selectDoublyAction,SIGNAL("triggered()"),win.selectDoubly)
    win.connect(win.selectExpandAction,SIGNAL("triggered()"),win.selectExpand)
    win.connect(win.selectInvertAction,SIGNAL("triggered()"),win.selectInvert)
    win.connect(win.selectNoneAction,SIGNAL("triggered()"),win.selectNone)

    win.connect(win.viewOrientationAction,SIGNAL("triggered()"),win.showOrientationWindow) #ninad061114

    ##When Standard Views button is clicked, show its QMenu.-- By default, nothing happens if you click on the 
    ##toolbutton with submenus. The menus are displayed only when you click on the small downward arrow 
    ## of the tool button. Therefore the following slot is added. Also QWidgetAction is used 
    ## for it to add this feature (see Ui_ViewToolBar for details) ninad 070109 
    win.connect(win.standardViews_btn,SIGNAL("pressed()"),win.showStandardViewsMenu)

    win.connect(win.viewBackAction,SIGNAL("triggered()"),win.viewBack)
    win.connect(win.viewBottomAction,SIGNAL("triggered()"),win.viewBottom)
    win.connect(win.setViewFitToWindowAction,SIGNAL("triggered()"),win.setViewFitToWindow)
    win.connect(win.viewFrontAction,SIGNAL("triggered()"),win.viewFront)
    win.connect(win.setViewHomeAction,SIGNAL("triggered()"),win.setViewHome)
    win.connect(win.setViewHomeToCurrentAction,SIGNAL("triggered()"),win.setViewHomeToCurrent)
    win.connect(win.viewLeftAction,SIGNAL("triggered()"),win.viewLeft)
    win.connect(win.viewRotateMinus90Action,SIGNAL("triggered()"),win.viewRotateMinus90)
    win.connect(win.viewNormalToAction,SIGNAL("triggered()"),win.viewNormalTo)
    win.connect(win.viewRotate180Action,SIGNAL("triggered()"),win.viewRotate180)
    win.connect(win.setViewOrthoAction,SIGNAL("triggered()"),win.setViewOrtho)
    win.connect(win.viewParallelToAction,SIGNAL("triggered()"),win.viewParallelTo)
    win.connect(win.setViewPerspecAction,SIGNAL("triggered()"),win.setViewPerspec)
    win.connect(win.viewRotatePlus90Action,SIGNAL("triggered()"),win.viewRotatePlus90)
    win.connect(win.setViewRecenterAction,SIGNAL("triggered()"),win.setViewRecenter)
    win.connect(win.viewRightAction,SIGNAL("triggered()"),win.viewRight)
    win.connect(win.viewTopAction,SIGNAL("triggered()"),win.viewTop)
    win.connect(win.simMoviePlayerAction,SIGNAL("triggered()"),win.simMoviePlayer)
    win.connect(win.simNanoHiveAction,SIGNAL("triggered()"),win.simNanoHive)
    win.connect(win.simPlotToolAction,SIGNAL("triggered()"),win.simPlot)
    win.connect(win.simSetupAction,SIGNAL("triggered()"),win.simSetup)
    win.connect(win.toolsCookieCutAction,SIGNAL("triggered()"),win.toolsCookieCut)

    win.connect(win.toolsDepositAtomAction,
                 SIGNAL("triggered()"),
                 win.toolsBuildAtoms)

    win.connect(win.toolsDoneAction,SIGNAL("triggered()"),win.toolsDone)
    win.connect(win.toolsExtrudeAction,SIGNAL("triggered()"),win.toolsExtrude)
    win.connect(win.toolsFuseChunksAction,SIGNAL("triggered()"),win.toolsFuseChunks)
    
    #Move and Rotate Components mode
    win.connect(win.toolsMoveMoleculeAction,SIGNAL("triggered()"),win.toolsMoveMolecule)
    win.connect(win.rotateComponentsAction,SIGNAL("triggered()"),win.toolsRotateComponents)

    win.connect(win.toolsSelectMoleculesAction,SIGNAL("triggered()"),win.toolsSelectMolecules)
    win.connect(win.zoomToolAction,SIGNAL("toggled(bool)"),win.zoomTool)
    win.connect(win.viewZoomAboutScreenCenterAction,SIGNAL("toggled(bool)"),
                 win.changeZoomBehavior)
    win.connect(win.viewQuteMolAction,SIGNAL("triggered()"),win.viewQuteMol)
    win.connect(win.viewRaytraceSceneAction,SIGNAL("triggered()"),win.viewRaytraceScene)
    win.connect(win.insertPovraySceneAction,SIGNAL("triggered()"),win.insertPovrayScene)
    win.connect(win.dispSurfaceAction,SIGNAL("triggered()"),win.dispSurface)
    win.connect(win.dispCylinderAction,SIGNAL("triggered()"),win.dispCylinder)
    win.connect(win.simMinimizeEnergyAction,SIGNAL("triggered()"),win.simMinimizeEnergy)
    win.connect(win.fileImportAction,SIGNAL("triggered()"),win.fileImport)
    win.connect(win.fileExportAction,SIGNAL("triggered()"),win.fileExport)
    win.connect(win.viewIsometricAction,SIGNAL("triggered()"),win.viewIsometric)
    win.connect(win.modifyMirrorAction,SIGNAL("triggered()"),win.modifyMirror)
    win.connect(win.setViewZoomtoSelectionAction,SIGNAL("triggered()"),win.setViewZoomToSelection)

    # Atom Generator example for developers. Mark and Jeff. 2007-06-13
    #@ Jeff - add a link to the public wiki page when ready. Mark 2007-06-13.
    win.connect(win.insertAtomAction,SIGNAL("triggered()"),win.insertAtom)

    QtCore.QObject.connect(win.fileExitAction,
                           QtCore.SIGNAL("activated()"),
                           win.close)