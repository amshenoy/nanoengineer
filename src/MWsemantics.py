# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
import qt
from qt import QMainWindow, QPixmap, QWidget, QFrame, QPushButton
from qt import QGroupBox, QComboBox, QAction, QMenuBar, QPopupMenu
from qt import SIGNAL, SLOT, QListView, QListViewItem, QFileDialog
from GLPane import *
import os
import help
from runSim import runSim
from modelTree import *

from constants import *
from elementSelector import *
from fileIO import *

from MainWindowUI import MainWindow
helpwindow = None
elementwindow = None
windowList = []

eCCBtab1 = [1,2, 5,6,7,8,9,10, 13,14,15,16,17,18, 32,33,34,35,36, 51,52,53,54]

eCCBtab2 = {}
for i,elno in zip(range(len(eCCBtab1)), eCCBtab1):
    eCCBtab2[elno] = i

def fileparse(name):
    """breaks name into directory, main name, and extension in a tuple.
    fileparse('~/foo/bar/gorp.xam') ==> ('~/foo/bar/', 'gorp', '.xam')
    """
    m=re.match("(.*\/)*([^\.]+)(\..*)?",name)
    return ((m.group(1) or "./"), m.group(2), (m.group(3) or ""))

class MWsemantics(MainWindow):
    def __init__(self,parent = None, name = None, fl = 0):
	
        global windowList
        MainWindow.__init__(self, parent, name, fl)

        # bruce 040920: until MainWindow.ui does the following, I'll do it manually:
        import extrudeMode as _extrudeMode
        _extrudeMode.do_what_MainWindowUI_should_do(self)
        
        windowList += [self]
        if name == None:
            self.setName("Atom")

	# start with empty window
        self.assy = assembly(self, "Empty")

        splitter = QSplitter(Qt.Horizontal, self, "ContentsWindow")

        self.modelTreeView = modelTree(splitter, self)
        self.modelTreeView.setMinimumSize(150, 0)
        
        
        self.glpane = GLPane(self.assy, splitter, "glpane", self)

        splitter.setResizeMode(self.modelTreeView, QSplitter.KeepSize)       
        splitter.setOpaqueResize(True)
        
        self.setCentralWidget(splitter)
        
        # do here to avoid a circular dependency
        self.assy.o = self.glpane

        self.setFocusPolicy(QWidget.StrongFocus)

        self.cookieCutterToolbar.hide() # (bruce note: this is the cookie mode dashboard)
        self.extrudeToolbar.hide() # (... and this is the extrude mode dashboard)
        self.sketchAtomToolbar.hide()

        # Mark - Set up primary (left) message bar in status bar area.
        self.msgbarLabel = QLabel(self, "msgbarLabel")
        self.msgbarLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
        self.msgbarLabel.setText( " " )
        
        self.statusBar().addWidget(self.msgbarLabel,1,1)

        # Mark - Set up mode bar (right) in status bar area.        
        self.modebarLabel = QLabel(self, "modebarLabel")
        self.modebarLabel.setFrameStyle( QFrame.Panel | QFrame.Sunken )
        self.modebarLabel.setText( "Mode: Select Molecules" )
        
        self.statusBar().addWidget(self.modebarLabel,0,1)

        # start with Carbon
        self.Element = 6
        self.setElement(6)
       
    ###################################
    # functions from the "File" menu
    ###################################

    def fileNew(self):
        """If this window is empty (has no assembly), do nothing.
        Else create a new empty one.
        """
        foo = MWsemantics()
        foo.show()

    def fileInsert(self):
        wd = globalParms['WorkingDirectory']
        fn = QFileDialog.getOpenFileName(wd, "Molecular machine parts (*.mmp);;Molecules (*.pdb);;Molecular parts assemblies (*.mpa);; All of the above (*.pdb *.mmp *.mpa)",
                                         self )
        fn = str(fn)
        if not os.path.exists(fn): return
        assy = assembly(self, "Empty")
        if fn[-3:] == "pdb":
            readpdb(assy,fn)
        if fn[-3:] == "mmp":
            readmmp(assy,fn)

        dir, fil, ext = fileparse(fn)
        assy.name = fil
        assy.filename = fn

        self.setCaption(self.trUtf8("Atom: " + assy.name))

	#update the model tree
        self.modelTreeView.updateModelTree()

        self.glpane.scale=self.assy.bbox.scale()
        self.glpane.paintGL()


    def fileOpen(self):
        self.__clear()
        
        wd = globalParms['WorkingDirectory']
        fn = QFileDialog.getOpenFileName(wd, "Molecular machine parts (*.mmp);;Molecules (*.pdb);;Molecular parts assemblies (*.mpa);; All of the above (*.pdb *.mmp *.mpa)",
                                         self )
        fn = str(fn)
        if not os.path.exists(fn): return
        if fn[-3:] == "pdb":
            readpdb(self.assy,fn)
        if fn[-3:] == "mmp":
            readmmp(self.assy,fn)

        dir, fil, ext = fileparse(fn)
        self.assy.name = fil
        self.assy.filename = fn

        self.setCaption(self.trUtf8("Atom: " + self.assy.name))

	#update the model tree
        self.modelTreeView.updateModelTree()

        self.glpane.scale=self.assy.bbox.scale()
        self.glpane.paintGL()


    def fileSave(self):
        if self.assy:
            if self.assy.filename:
                fn = str(self.assy.filename)
                dir, fil, ext = fileparse(fn)
                writemmp(self.assy, dir + fil + ".mmp")
            else: self.fileSaveAs()

    def fileSaveAs(self):
        if self.assy:
            if self.assy.filename:
                dir, fil, ext = fileparse(self.assy.filename)
            else: dir, fil = "./", self.assy.name
            
	    fileDialog = QFileDialog(dir, "Molecular machine parts (*.mmp);;Molecules (*.pdb);;POV-Ray (*.pov)", self, "Save File As", 1)
            if self.assy.filename:
                fileDialog.setSelection(fil)

            fileDialog.setMode(QFileDialog.AnyFile)
	    fn = None
            if fileDialog.exec_loop() == QDialog.Accepted:
            	fn = fileDialog.selectedFile()
            
            if fn:
                fn = str(fn)
                dir, fil, ext = fileparse(fn)
                ext = fileDialog.selectedFilter()
                ext = str(ext)
                if ext[-4:-1] == "mmp":
                    writemmp(self.assy, dir + fil + ".mmp")
                    self.assy.filename = dir + fil + ".mmp"
                    self.assy.modified = 0
                elif ext[-4:-1] == "pdb":
                    writepdb(self.assy, dir + fil + ".pdb")
                    self.assy.filename = dir + fil + ".pdb"
                    self.assy.modified = 0
                elif ext[-4:-1] == "pov":
                    w = self.glpane.width
                    h = self.glpane.height
                    self.glpane.povwrite(dir + fil + ".pov", w, h)

    def fileImage(self):
        if self.assy:
            if self.assy.filename:
                fn = str(self.assy.filename)
                dir, fil, ext = fileparse(fn)
            else: dir, fil, ext = "./", "Picture", "jpg"
        fn = QFileDialog.getSaveFileName(dir + fil + ".jpg",
                                         "JPEG images (*.jpg *.jpeg",
                                         self )
        fn = str(fn)
        self.glpane.image(fn)

    def fileExit(self):
        pass

    def fileClear(self):
        self.__clear()
        self.modelTreeView.updateModelTree()
        self.glpane.paintGL()


    def fileClose(self):
        if self.assy.modified: self.fileSave()
        self.__clear()

    def fileSetWorkDir(self):
	""" Sets working directory (need dialogue window) """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def __clear(self):
        global assyList
        del assyList[:]
        self.assy = assembly(self, "Empty")
        self.glpane.setAssy(self.assy)


    ###################################
    # functions from the "Edit" menu
    ###################################

    def editUndo(self):
        print "MWsemantics.editUndo(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editRedo(self):
        print "MWsemantics.editRedo(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editCut(self):
        print "MWsemantics.editCut(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editCopy(self):
        print "MWsemantics.editCopy(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editPaste(self):
        print "MWsemantics.editPaste(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editFind(self):
        print "MWsemantics.editFind(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    ###################################
    # functions from the "View" menu
    ###################################

    # GLPane.ortho is checked in GLPane.paintGL
    def setViewOrtho(self):
        self.glpane.ortho = 1
        self.glpane.paintGL()

    def setViewPerspec(self):
        self.glpane.ortho = 0
        self.glpane.paintGL()

    def setViewBack(self):
        self.glpane.quat = Q(V(0,1,0),pi)
        self.glpane.paintGL()

    def setViewBottom(self):
        self.glpane.quat = Q(V(1,0,0),-pi/2)
        self.glpane.paintGL()

    def setViewFront(self):
        self.glpane.quat = Q(1,0,0,0)
        self.glpane.paintGL()

    def setViewHome(self):
        self.glpane.quat = Q(1,0,0,0)
        self.glpane.paintGL()

    def setViewLeft(self):
        self.glpane.quat = Q(V(0,1,0),-pi/2)
        self.glpane.paintGL()

    def setViewRight(self):
        self.glpane.quat = Q(V(0,1,0),pi/2)
        self.glpane.paintGL()

    def setViewTop(self):
        self.glpane.quat = Q(V(1,0,0),pi/2)
        self.glpane.paintGL()

    # set display formats in whatever is selected,
    # or the GLPane global default if nothing is
    def dispDefault(self):
        self.setDisplay(diDEFAULT)

    def dispInvis(self):
        self.setDisplay(diINVISIBLE)

    def dispVdW(self):
        self.setDisplay(diVDW)

    def dispTubes(self):
        self.setDisplay(diTUBES)

    def dispCPK(self):
        self.setDisplay(diCPK)

    def dispLines(self):
        self.setDisplay(diLINES)

    def setDisplay(self, form):
        if self.assy and self.assy.selatoms:
            for ob in self.assy.selatoms.itervalues():
                ob.setDisplay(form)
        elif self.assy and self.assy.selmols:
            for ob in self.assy.selmols:
                ob.setDisplay(form)
        else:
            if self.glpane.display == form: return
            self.glpane.setDisplay(form)
        self.glpane.paintGL()

    def setdisplay(self, a0):
        print 'setdisplay', a0


    # set the color of the selected part(s) (molecule)
    # or the background color if no part is selected.
    # atom colors cannot be changed singly
    def dispObjectColor(self):
        c = self.colorchoose()
        for ob in self.assy.selmols:
            ob.setcolor(c)
        self.glpane.paintGL()


    def dispBGColor(self):
        c = self.colorchoose()
        self.glpane.backgroundColor = c
        self.glpane.paintGL()

    def dispGrid(self):
        print "MWsemantics.dispGrid(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
        

    def gridGraphite(self):
        print "MWsemantics.gridGraphite(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    #######################################
    # functions from the "Orientation" menu
    #######################################

    # points of view corresponding to the three crystal
    # surfaces of diamond

    # along one axis
    def orient100(self):
        self.glpane.snapquat100()

    # halfway between two axes
    def orient110(self):
        self.glpane.snapquat110()

    # equidistant from three axes
    def orient111(self):
        self.glpane.snapquat111()

    # lots of things ???
    def orientView(self, a0=None):
        print "MainWindow.orientView(string):", a0
        self.glpane.quat = Q(1,0,0,0)
        self.glpane.pov = V(0,0,0)
        self.glpane.paintGL()

    ###############################################################
    # functions from the "Select" menu
    ###############################################################

    def selectAtoms(self):
        self.modebarLabel.setText( "Mode: Select Atoms" )
        self.assy.selectAtoms()

    def selectParts(self):
        self.modebarLabel.setText( "Mode: Select Molecules" )
        self.assy.selectParts()
    
    def selectAll(self):
        """Select all parts if nothing selected.
        If some parts are selected, select all atoms in those parts.
        If some atoms are selected, select all atoms in the parts
        in which some atoms are selected.
        """
        self.assy.selectAll()

    def selectNone(self):
        self.assy.selectNone()

    def selectInvert(self):
        """If some parts are selected, select the other parts instead.
        If some atoms are selected, select all currently unselected
        atoms in parts in which there are currently some selected atoms.
        (And unselect all currently selected atoms.)
        """
        self.assy.selectInvert()

    def selectConnected(self):
        """Select any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        """
        self.assy.selectConnected()


    def selectDoubly(self):
        """Select any atom that can be reached from any currently
        selected atom through two or more non-overlapping sequences of
        bonds. Also select atoms that are connected to this group by
        one bond and have no other bonds.
        """
        self.assy.selectDoubly()

    ###################################
    # Functions from the "Make" menu
    ###################################

    # these functions (do or will) create small structures that
    # describe records to send to the simulator
    # they don't do much in Atom itself
    def makeGround(self):
        self.assy.makeground()
        self.glpane.paintGL()

    def makeHandle(self):
        print "MWsemantics.makeHandle(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def makeMotor(self):
        self.assy.makemotor(self.glpane.lineOfSight)
        self.glpane.paintGL()

    def makeLinearMotor(self):
        self.assy.makeLinearMotor(self.glpane.lineOfSight)
        self.glpane.paintGL()


    def makeBearing(self):
        QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def makeSpring(self):
        QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
    def makeDyno(self):
        print "MWsemantics.makeDyno(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def makeHeatsink(self):
        print "MWsemantics.makeHeatsink(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    ###################################
    # functions from the "Modify" menu
    ###################################

    # change surface atom types to eliminate dangling bonds
    # a kludgey hack
    def modifyPassivate(self):
        self.assy.modifyPassivate()

    # add hydrogen atoms to each dangling bond
    def modifyHydrogenate(self):
        self.assy.modifyHydrogenate()

    # form a new part (molecule) with whatever atoms are selected
    def modifySeparate(self):
        self.assy.modifySeparate()

    ###################################
    # Functions from the "Help" menu
    ###################################

    def helpContents(self):
        global helpwindow
        if not helpwindow: helpwindow = help.Help()
        helpwindow.show()

    def helpIndex(self):
        print "MWsemantics.helpIndex(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
    def helpAbout(self):
        QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")


    ######################################################
    # functions for toggling (hiding/unhiding) toolbars  #
    ######################################################

    def toggleFileTbar(self):
        if self.fileToolbar.isVisible():
            self.fileToolbar.hide()
        else:
            self.fileToolbar.show()

    def toggleEditTbar(self):
        if self.editToolbar.isVisible():
            self.editToolbar.hide()
        else:
            self.editToolbar.show()

    def toggleViewTbar(self):
        if self.viewToolbar.isVisible():
            self.viewToolbar.hide()
        else:
            self.viewToolbar.show()

    def toggleGridTbar(self):
        if self.gridToolbar.isVisible():
            self.gridToolbar.hide()
        else:
            self.gridToolbar.show()

    def toggleModelDispTbar(self):
        if self.modelDispToolbar.isVisible():
            self.modelDispToolbar.hide()
        else:
            self.modelDispToolbar.show()

    def toggleSelectTbar(self):
        if self.selectToolbar.isVisible():
            self.selectToolbar.hide()
        else:
            self.selectToolbar.show()

    def toggleModifyTbar(self):
        if self.modifyToolbar.isVisible():
            self.modifyToolbar.hide()
        else:
            self.modifyToolbar.show()

    def toggleToolsTbar(self):
        if self.toolsToolbar.isVisible():
            self.toolsToolbar.hide()
        else:
            self.toolsToolbar.show()

    def toggleDatumDispTbar(self):
        if self.datumDispToolbar.isVisible():
            self.datumDispToolbar.hide()
        else:
            self.datumDispToolbar.show()

    def toggleSketchAtomTbar(self):
        if self.sketchAtomToolbar.isVisible():
            self.sketchAtomToolbar.hide()
        else:
            self.sketchAtomToolbar.show()

## bruce 040920 -- toggleCookieCutterTbar seems to be obsolete, so I zapped it:
##    def toggleCookieCutterTbar(self):
##        print "\n * * * * fyi: toggleCookieCutterTbar() called -- tell bruce since he thinks this will never happen * * * * \n" ####
##        if self.cookieCutterToolbar.isVisible():
##            self.cookieCutterToolbar.hide()
##        else:
##            self.cookieCutterToolbar.show()


    ###############################################################
    # functions from the buttons down the right side of the display
    ###############################################################

    # get into cookiecutter mode
    def toolsCookieCut(self):
        self.modebarLabel.setText( "Mode: Cookie Cutter" )
        self.glpane.setMode('COOKIE')

    # get into Extrude mode
    def toolsExtrude(self):
        self.modebarLabel.setText( "Mode: Extrude" )
        self.glpane.setMode('EXTRUDE')

    # "push down" one nanometer to cut out the next layer
    def toolsCCAddLayer(self):
        if self.glpane.shape:
            self.glpane.pov -= self.glpane.shape.pushdown()
            self.glpane.paintGL()

    # fill the shape created in the cookiecutter with actual
    # carbon atoms in a diamond lattice (including bonds)
    # this works for all modes, not just add atom
    def toolsDone(self):
        self.glpane.mode.Done()

    def toolsStartOver(self):
        self.glpane.mode.Restart()

    def toolsBackUp(self):
        self.glpane.mode.Backup()

    def toolsCancel(self):
        self.glpane.mode.Flush()

    # turn on and off an "add atom with a mouse click" mode
    def addAtomStart(self):
        self.modebarLabel.setText( "Mode: Sketch Atoms" )
        self.glpane.setMode('DEPOSIT')

    def toolsAtomStart(self):
        self.modebarLabel.setText( "Mode: Sektch Atoms" )
        self.glpane.setMode('DEPOSIT')

    # pop up set element box
    def modifySetElement(self):
        print self.Element    
        global elementwindow
        if not elementwindow:
            elementwindow = elementSelector(self)
        elementwindow.setDisplay(self.Element)
        elementwindow.show()

    def elemChange(self, a0):
        self.Element = eCCBtab1[a0]
        global elementwindow
        if not elementwindow.isHidden():
           elementwindow.setDisplay(self.Element)     
           elementwindow.show()
          
         
    # this routine sets the displays to reflect elt
    def setElement(self, elt):
        # element specified as element number
        global elementwindow
        self.Element = elt
        if elementwindow: elementwindow.setDisplay(elt)
        line = eCCBtab2[elt]
        self.elemChangeComboBox.setCurrentItem(line)

    def setCarbon(self):
        self.setElement(6)

    def setHydrogen(self):
        self.setElement(1)
    
    def setOxygen(self):
        self.setElement(8)

    def setNitrogen(self):
        self.setElement(7)

    # Play a movie from the simulator
    def toolsMovie(self):
        dir, fil, ext = fileparse(self.assy.filename)
        self.glpane.startmovie(dir + fil + ".dpb")

    
    ###################################
    # some unimplemented buttons:
    ###################################

    # bring molecules together and bond unbonded sites
    def modifyWeldMolecule(self):
        print "MWsemantics.modifyWeldMolecule(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
 

    
    # create bonds where reasonable between selected and unselected
    def modifyEdgeBond(self):
        print "MWsemantics.modifyEdgeBond(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
        
    # create bonds where reasonable between selected and unselected
    def modifyAddBond(self):
        print "MWsemantics.modifyAddBond(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    # Turn on or off the axis icon
    def dispTrihedron(self):
        self.glpane.drawAxisIcon = not self.glpane.drawAxisIcon
        self.glpane.paintGL()

    def dispCsys(self):
        """ Toggle on/off center coordinate axes """
        self.glpane.cSysToggleButton = not self.glpane.cSysToggleButton
        self.glpane.paintGL()

    # break bonds between selected and unselected atoms
    def modifyDeleteBond(self):
        print "MWsemantics.modifyDeleteBond(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    # Make a copy of the selected part (molecule)
    # cannot copy individual atoms
    def copyDo(self):
        self.assy.copy()
        self.glpane.paintGL()

    # 2BDone: make a copy of the selected part, move it, and bondEdge it,
    # having unselected the original and selected the copy.
    # the motion is to be the same relative motion done to a part
    # between copying and bondEdging it.
    def modifyCopyBond(self):
        print "MWsemantics.modifyCopyBond(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    # delete selected parts or atoms
    def killDo(self):
        self.assy.kill()
        self.glpane.paintGL()

    # utility functions

    def colorchoose(self):
        c = QColorDialog.getColor(QColor(100,100,100), self, "choose")
        return c.red()/256.0, c.green()/256.0, c.blue()/256.0


    def keyPressEvent(self, e):
        self.glpane.mode.keyPress(e.key())

    ##############################################################
    # Some future slot functions for the UI                      #
    ##############################################################

    def dispDatumLines(self):
        """ Toggle on/off datum lines """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def dispDatumPlanes(self):
        """ Toggle on/off datum planes """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def dispOpenBonds(self):
        """ Toggle on/off open bonds """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editPrefs(self):
        """ Edit square grid line distances(dx, dy, dz) in nm/angtroms """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
 
    def elemChangePTable(self):
        """ Future: element change via periodic table
        (only elements we support) """

    def modifyMinimize(self):
        """ Minimize the current assembly """
	self.glpane.minimize()

    def toolsSimulator(self):
        self.simCntl = runSim(self.assy)
        self.simCntl.show()

    def setViewFitToWindow(self):
        """ Fit to Window """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
        
    def setViewRecenter(self):
        """ Fit to Window """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")