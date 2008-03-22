# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
CntSegment_EditCommand provides a way to edit an existing CntSegment. 

To edit a segment, first enter BuildCnt_EditCommand (accessed using Build > Cnt) 
then, select an axis chunk of an existing CntSegment  within the CntGroup you
are editing. When you select the axis chunk, it enters CntSegment_Editcommand
and shows the property manager with its widgets showing the properties of 
selected segment. 

While in this command, user can 
(a) Highlight and then left drag the resize handles located at the 
    two 'axis endpoints' of thje segment to change its length.  
(b) Highlight and then left drag any axis atom (except the two end axis atoms)
    to translate the  whole segment along the axis
(c) Highlight and then left drag any strand atom to rotate the segment around 
    its axis. 

    Note that implementation b and c may change slightly if we implement special
    handles to do these oprations. 
    See also: CntSegment_GraphicsMode .. the default graphics mode for this 
    command


@author: Ninad, Mark
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$

History:
Mark 2008-03-10: Created from copy of DnaSegment_EditCommand.py
"""
from command_support.EditCommand import EditCommand 
from cnt.model.CntSegment import CntSegment
from cnt.commands.CntSegment.CntSegment_GraphicsMode import CntSegment_GraphicsMode
from cnt.commands.CntSegment.CntSegment_GraphicsMode import CntSegment_DragHandles_GraphicsMode
from command_support.GraphicsMode_API import GraphicsMode_API
from cnt.model.Cnt_Constants import getCntRise, getNumberOfCellsFromCntLength

from utilities.Log  import redmsg

from geometry.VQT import V, Veq, vlen
from geometry.VQT import cross, norm

from cnt.commands.InsertCnt.Nanotube import Cnt

from command_support.GeneratorBaseClass import PluginBug, UserError

from utilities.constants import gensym

from cnt.model.Cnt_Constants import getCntLength
from prototype.test_connectWithState import State_preMixin

from utilities.constants import noop
from exprs.attr_decl_macros import Instance, State

from exprs.__Symbols__ import _self
from exprs.Exprs import call_Expr
from exprs.Exprs import norm_Expr
from widgets.prefs_widgets import ObjAttr_StateRef
from exprs.ExprsConstants import Width, Point

from model.chunk import Chunk
from model.chem import Atom
from model.bonds import Bond


from cnt.commands.CntSegment.CntSegment_ResizeHandle import CntSegment_ResizeHandle
from graphics.drawables.RotationHandle import RotationHandle

CYLINDER_WIDTH_DEFAULT_VALUE = 0.0
HANDLE_RADIUS_DEFAULT_VALUE = 1.2
ORIGIN = V(0,0,0)

#Flag that appends rotation handles to the self.handles (thus enabling their 
#display and computation while in CntSegment_EditCommand
DEBUG_ROTATION_HANDLES = False


class CntSegment_EditCommand(State_preMixin, EditCommand):
    """
    Command to edit a CntSegment object. 
    To edit a segment, first enter BuildCnt_EditCommand (accessed using Build > Cnt) 
    then, select an axis chunk of an existing CntSegment  within the CntGroup you
    are editing. When you select the axis chunk, it enters CntSegment_Editcommand
    and shows the property manager with its widgets showing the properties of 
    selected segment.
    """
    cmd              =  'Cnt Segment'
    sponsor_keyword  =  'CNT'
    prefix           =  'Segment '   # used for gensym
    cmdname          = "CNT_SEGMENT"
    commandName       = 'CNT_SEGMENT'
    featurename       = 'Edit Cnt Segment'


    command_should_resume_prevMode = True
    command_has_its_own_gui = True
    command_can_be_suspended = False

    # Generators for DNA, nanotubes and graphene have their MT name 
    # generated (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix  =  True 

    call_makeMenus_for_each_event = True 

    #Graphics Mode 
    GraphicsMode_class = CntSegment_GraphicsMode

    #This is set to BuildCnt_EditCommand.flyoutToolbar (as of 2008-01-14, 
    #it only uses 
    flyoutToolbar = None

    _parentCntGroup = None    

    handlePoint1 = State( Point, ORIGIN)
    handlePoint2 = State( Point, ORIGIN)

    rotationHandleBasePoint1 = State( Point, ORIGIN)
    rotationHandleBasePoint2 = State( Point, ORIGIN)

    #See self._determine_hresize_handle_radius where this gets changed. 
    #also see CntSegment_ResizeHandle to see how its implemented. 
    handleSphereRadius1 = State(Width, HANDLE_RADIUS_DEFAULT_VALUE)
    handleSphereRadius2 = State(Width, HANDLE_RADIUS_DEFAULT_VALUE)

    cylinderWidth = State(Width, CYLINDER_WIDTH_DEFAULT_VALUE) 
    cylinderWidth2 = State(Width, CYLINDER_WIDTH_DEFAULT_VALUE) 
    #@TODO: modify the 'State params for rotation_distance 
    rotation_distance1 = State(Width, CYLINDER_WIDTH_DEFAULT_VALUE)
    rotation_distance2 = State(Width, CYLINDER_WIDTH_DEFAULT_VALUE)

    cntRise =  getCntRise()  #@ FIX THIS.

    leftHandle = Instance(         
        CntSegment_ResizeHandle(    
            command = _self,
            height_ref = call_Expr( ObjAttr_StateRef, _self, 'cylinderWidth'),
            origin = handlePoint1,
            fixedEndOfStructure = handlePoint2,
            direction = norm_Expr(handlePoint1 - handlePoint2),
            sphereRadius = handleSphereRadius1, 
                               
                           ))

    rightHandle = Instance( 
        CntSegment_ResizeHandle(
            command = _self,
            height_ref = call_Expr( ObjAttr_StateRef, _self, 'cylinderWidth2'),
            origin = handlePoint2,
            fixedEndOfStructure = handlePoint1,
            direction = norm_Expr(handlePoint2 - handlePoint1),
            sphereRadius = handleSphereRadius2
                           ))

    rotationHandle1 = Instance(         
        RotationHandle(    
            command = _self,
            rotationDistanceRef = call_Expr( ObjAttr_StateRef,
                                             _self, 
                                             'rotation_distance1'),
            center = handlePoint1,
            axis = norm_Expr(handlePoint1 - handlePoint2),
            origin = rotationHandleBasePoint1,
            radiusVector = norm_Expr(rotationHandleBasePoint1 - handlePoint1)

        ))

    rotationHandle2 = Instance(         
        RotationHandle(    
            command = _self,
            rotationDistanceRef = call_Expr( ObjAttr_StateRef,
                                             _self, 
                                             'rotation_distance2'),
            center = handlePoint2,
            axis = norm_Expr(handlePoint2 - handlePoint1),
            origin = rotationHandleBasePoint2,
            radiusVector = norm_Expr(rotationHandleBasePoint2 - handlePoint2)

        ))


    def __init__(self, commandSequencer, struct = None):
        """
        Constructor for InsertCnt_EditCommand
        """

        glpane = commandSequencer
        State_preMixin.__init__(self, glpane)        
        EditCommand.__init__(self, commandSequencer)
        self.struct = struct

        #Graphics handles for editing the structure . 
        self.handles = []        
        self.grabbedHandle = None

    def init_gui(self):
        """
        Initialize gui. 
        """

        #Note that CntSegment_EditCommand only act as an edit command for an 
        #existing structure. The call to self.propMgr.show() is done only during
        #the call to self.editStructure ..i .e. only after self.struct is 
        #updated. This is done because of the following reason:
        # - self.init_gui is called immediately after entering the command. 
        # - self.init_gui in turn, initialized propMgr object and may also 
        #  show the property manager. The self.propMgr.show routine calls 
        #  an update widget method just before the show. This update method 
        #  updates the widgets based on the parameters from the existing 
        #  structure of the command (self.editCommand.struct)
        #  Although, it checks whether this structure exists, the editCommand
        #  could still have a self.struct attr from a previous run. (Note that 
        #  EditCommand API was written before the command sequencer API and 
        #  it has some loose ends like this. ) -- Ninad 2008-01-22
        self.create_and_or_show_PM_if_wanted(showPropMgr = False)

    def editStructure(self, struct = None):
        EditCommand.editStructure(self, struct)        
        if self.struct:
            #@@@TEMPORARY CODE -- might be revised once cnt data model is in
            #place           
            assert isinstance(self.struct, CntSegment)
            #When the structure (segment) is finalized (afterthe  modifications)
            #it will be added to the original CntGroup to which it belonged 
            #before we began editing (modifying) it. 
            self._parentCntGroup = self.struct.get_CntGroup() 
            #Set the duplex rise and number of bases
            self.propMgr.setParameters(self.struct.getProps())
            #Store the previous parameters. Important to set it after you 
            #set cntRise and basesPerTurn attrs in the propMgr. 
            #self.previousParams is used in self._previewStructure and 
            #self._finalizeStructure to check if self.stuct changed.
            self.previousParams = self._gatherParameters()
            self._updateHandleList()
            self.updateHandlePositions()
            
    def keep_empty_group(self, group):
        """
        Returns True if the empty group should not be automatically deleted. 
        otherwise returns False. The default implementation always returns 
        False. Subclasses should override this method if it needs to keep the
        empty group for some reasons. Note that this method will only get called
        when a group has a class constant autdelete_when_empty set to True. 
        (and as of 2008-03-06, it is proposed that cnt_updater calls this method
        when needed. 
        @see: Command.keep_empty_group() which is overridden here. 
        @see: BreakStrands_Command.keep_empty_group
        @see: Group.autodelete_when_empty.. a class constant used by the 
              cnt_updater (the cnt updater then decides whether to call this 
              method to see which empty groups need to be deleted)
        """
        
        bool_keep = EditCommand.keep_empty_group(self, group)
        
        if not bool_keep:     
            if self.hasValidStructure():                
                if group is self.struct:
                    bool_keep = True
                elif group is self.struct.parent_node_of_class(self.assy.CntGroup):
                    bool_keep = True
            #If this command doesn't have a valid structure, as a fall back, 
            #lets instruct it to keep ALL the CntGroup objects even when empty
            #Reason? ..see explanation in BreakStrands_Command.keep_empty_group
            elif isinstance(group, self.assy.CntGroup):
                bool_keep = True
        
        return bool_keep
    

    def hasValidStructure(self):
        """
        Tells the caller if this edit command has a valid structure. 
        Overrides EditCommand.hasValidStructure()
        """
        #(By Bruce 2008-02-13)

        isValid = EditCommand.hasValidStructure(self)

        if not isValid:
            return isValid

        if not isinstance(self.struct, CntSegment): 
            return False    

        # would like to check here whether it's empty of axis chunks;
        # instead, this will do for now (probably too slow, though):
        p1, p2 = self.struct.getAxisEndPoints()
        return (p1 is not None)

    def _updateHandleList(self):
        """        
        Updates the list of handles (self.handles) 
        @see: self.editStructure
        @see: CntSegment_GraphicsMode._drawHandles()
        """   
        # note: if handlePoint1 and/or handlePoint2 can change more often than this 
        # runs, we'll need to rerun the two assignments above whenever they 
        # change and before the handle is drawn. An easy way would be to rerun
        # these assignments in the draw method of our GM. [bruce 080128]
        self.handles = [] # guess, but seems like a good idea [bruce 080128]
        self.handles.append(self.leftHandle)
        self.handles.append(self.rightHandle)
        if DEBUG_ROTATION_HANDLES:
            self.handles.append(self.rotationHandle1)
            self.handles.append(self.rotationHandle2)

    def updateHandlePositions(self):
        """
        Update handle positions
        """        

        self.cylinderWidth = CYLINDER_WIDTH_DEFAULT_VALUE
        self.cylinderWidth2 = CYLINDER_WIDTH_DEFAULT_VALUE
        
        print "***before, self.handlesphereRadius1 =", self.handleSphereRadius1
        

        self._determine_resize_handle_radius()
        
        print "***after, self.handlesphereRadius1 =", self.handleSphereRadius1
        print "~~~~~~~~~~~"

        handlePoint1, handlePoint2 = self.struct.getAxisEndPoints()


        if handlePoint1 is not None:
            # (that condition is bugfix for deleted axis segment, bruce 080213)

            self.handlePoint1, self.handlePoint2 = handlePoint1, handlePoint2

            if DEBUG_ROTATION_HANDLES:
                self.rotation_distance1 = CYLINDER_WIDTH_DEFAULT_VALUE
                self.rotation_distance2 = CYLINDER_WIDTH_DEFAULT_VALUE
                #Following computes the base points for rotation handles. 
                #to be revised -- Ninad 2008-02-13

                unitVectorAlongAxis = norm(self.handlePoint1 - self.handlePoint2)

                v  = cross(self.glpane.lineOfSight, unitVectorAlongAxis)

                self.rotationHandleBasePoint1 = self.handlePoint1 + norm(v) * 4.0  
                self.rotationHandleBasePoint2 = self.handlePoint2 + norm(v) * 4.0 

    def _determine_resize_handle_radius(self):
        """
        Finds out the sphere radius to use for the resize handles, based on 
        atom /chunk or glpane display (whichever decides the display of the end 
        atoms.  The default  value is 1.2.


        @see: self.updateHandlePositions()
        @see: B{Atom.drawing_radius()}
        """
        atm1 , atm2 = self.struct.getAxisEndAtoms()                  
        if atm1 is not None:
            self.handleSphereRadius1 = max(1.005*atm1.drawing_radius(), 
                                           1.005*HANDLE_RADIUS_DEFAULT_VALUE)
        if atm2 is not None: 
            self.handleSphereRadius2 =  max(1.005*atm2.drawing_radius(), 
                                           1.005*HANDLE_RADIUS_DEFAULT_VALUE)

    def _createPropMgrObject(self):
        """
        Creates a property manager object (that defines UI things) for this 
        editCommand. 
        """
        assert not self.propMgr
        propMgr = self.win.createCntSegmentPropMgr_if_needed(self)
        return propMgr

    def _gatherParameters(self):
        """
        Return the parameters from the property manager UI.

        @return: All the parameters (get those from the property manager):
                 - numberOfCells
                 - cntType
                 - basesPerTurn
                 - endPoint1
                 - endPoint2
        @rtype:  tuple
        """     
        return self.propMgr.getParameters()


    def _createStructure(self):
        """
        Creates and returns the structure (in this case a L{Group} object that 
        contains the CNT strand and axis chunks. 
        @return : group containing that contains the CNT axis chunks.
        @rtype: L{Group}  
        @note: This needs to return a DNA object once that model is implemented        
        """

        params = self._gatherParameters()
        

        # No error checking in build_struct, do all your error
        # checking in gather_parameters
        numberOfCells, \
                     cntType, \
                     cntModel, \
                     basesPerTurn, \
                     cntRise, \
                     endPoint1, \
                     endPoint2 = params

        #If user enters the number of basepairs and hits preview i.e. endPoint1
        #and endPoint2 are not entered by the user and thus have default value 
        #of V(0, 0, 0), then enter the endPoint1 as V(0, 0, 0) and compute
        #endPoint2 using the duplex length. 
        #Do not use '==' equality check on vectors! its a bug. Use same_vals 
        # or Veq instead. 
        if Veq(endPoint1 , endPoint2) and Veq(endPoint1, V(0, 0, 0)):
            endPoint2 = endPoint1 + \
                      self.win.glpane.right*getCntLength('Carbon', 
                                                            numberOfCells)


        if numberOfCells < 1:
            msg = redmsg("Cannot to preview/insert a CNT with 0 cells.")
            self.propMgr.updateMessage(msg)
            self.cnt = None # Fixes bug 2530. Mark 2007-09-02
            return None

        cnt = Cnt()

        self.cnt  =  cnt  # needed for done msg

        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix) # (in _build_struct)
            self._gensym_data_for_reusing_name = (self.prefix, name)
        else:
            # use externally created name
            self._gensym_data_for_reusing_name = None
                # (can't reuse name in this case -- not sure what prefix it was
                #  made with)
            name = self.name


        # Create the model tree group node. 
        # Make sure that the 'topnode'  of this part is a Group (under which the
        # DNa group will be placed), if the topnode is not a group, make it a
        # a 'Group' (applicable to Clipboard parts).See part.py
        # --Part.ensure_toplevel_group method. This is an important line
        # and it fixes bug 2585
        self.win.assy.part.ensure_toplevel_group()
        cntSegment = CntSegment(self.name, 
                                self.win.assy,
                                self.win.assy.part.topnode,
                                editCommand = self  )
        try:
            # Make the DNA duplex. <cntGroup> will contain one chunk:
            #  - Axis (Segment)

            cnt.make(cntSegment, 
                     numberOfCells, 
                     basesPerTurn, 
                     cntRise,
                     endPoint1,
                     endPoint2)
            
            #set some properties such as cntRise and number of bases per turn
            #This information will be stored on the CntSegment object so that
            #it can be retrieved while editing this object. 
            #This works with or without cnt_updater. Now the question is 
            #should these props be assigned to the CntSegment in 
            #Nanotube.make() itself ? This needs to be answered while modifying
            #make() method to fit in the cnt data model. --Ninad 2008-03-05
            
            #WARNING 2008-03-05: Since self._modifyStructure calls 
            #self._createStructure() 
            #If in the near future, we actually permit modifying a
            #structure (such as cnt) without actually recreating the whole 
            #structre, then the following properties must be set in 
            #self._modifyStructure as well. Needs more thought.
            props = (cntRise, basesPerTurn)            
            cntSegment.setProps(props)
            
            return cntSegment

        except (PluginBug, UserError):
            # Why do we need UserError here? Mark 2007-08-28
            cntSegment.kill()
            raise PluginBug("Internal error while trying to create DNA duplex.")


    def _modifyStructure(self, params):
        """
        Modify the structure based on the parameters specified. 
        Overrides EditCommand._modifystructure. This method removes the old 
        structure and creates a new one using self._createStructure. This 
        was needed for the structures like this (Dna, Nanotube etc) . .
        See more comments in the method.
        """    
        assert self.struct
        # parameters have changed, update existing structure
        self._revertNumber()


        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix) # (in _build_struct)
            self._gensym_data_for_reusing_name = (self.prefix, name)
        else:
            # use externally created name
            self._gensym_data_for_reusing_name = None
                # (can't reuse name in this case -- not sure what prefix it was
                #  made with)
            name = self.name

        #@NOTE: Unlike editcommands such as Plane_EditCommand, this 
        #editCommand actually removes the structure and creates a new one 
        #when its modified. We don't yet know if the DNA object model 
        # will solve this problem. (i.e. reusing the object and just modifying
        #its attributes.  Till that time, we'll continue to use 
        #what the old GeneratorBaseClass use to do ..i.e. remove the item and 
        # create a new one  -- Ninad 2007-10-24

        self._removeStructure()

        self.previousParams = params

        self.struct = self._createStructure()
        # Now append the new structure in self._segmentList (this list of 
        # segments will be provided to the previous command 
        # (BuildCnt_EditCommand)
        # TODO: Should self._createStructure does the job of appending the 
        # structure to the list of segments? This fixes bug 2599 
        # (see also BuildCnt_PropertyManager.Ok 

        if self._parentCntGroup is not None:
            #Should this be an assertion? (assert self._parentCntGroup is not 
            #None. For now lets just print a warning if parentCntGroup is None 
            self._parentCntGroup.addSegment(self.struct)
        return  

    def getStructureName(self):
        """
        Returns the name string of self.struct if there is a valid structure. 
        Otherwise returns None. This information is used by the name edit field 
        of  this command's PM when we call self.propMgr.show()
        @see: CntSegment_PropertyManager.show()
        @see: self.setStructureName
        """
        if self.hasValidStructure():
            return self.struct.name
        else:
            return None

    def setStructureName(self, name):
        """
        Sets the name of self.struct to param <name> (if there is a valid 
        structure. 
        The PM of this command callss this method while closing itself 
        @param name: name of the structure to be set.
        @type name: string
        @see: CntSegment_PropertyManager.close()
        @see: self.getStructureName()

        """
        #@BUG: We call this method in self.propMgr.close(). But propMgr.close() 
                #is called even when the command is 'cancelled'. That means the 
                #structure will get changed even when user hits cancel button or
                #exits the command by clicking on empty space. 
                #This should really be done in self._finalizeStructure but that 
                #method doesn't get called when you click on empty space to exit 
                #the command. See CntSegment_GraphicsMode.leftUp for a detailed 
                #comment. 

        if self.hasValidStructure():
            self.struct.name = name

    def getCursorText(self):
        """
        This is used as a callback method in CntLine mode 
        @see: CntLineMode.setParams, CntLineMode_GM.Draw
        """
        if self.grabbedHandle is None:
            return

        text = ""

        currentPosition = self.grabbedHandle.currentPosition
        fixedEndOfStructure = self.grabbedHandle.fixedEndOfStructure

        cntLength = vlen( currentPosition - fixedEndOfStructure )
        numberOfCells = getNumberOfCellsFromCntLength(cntLength, 'Carbon')
        cntLengthString = str(round(cntLength, 3))
        text =  str(numberOfCells)+ "c, "+ cntLengthString 

        #@TODO: The following updates the PM as the cursor moves. 
        #Need to rename this method so that you that it also does more things 
        #than just to return a textString -- Ninad 2007-12-20
        #@self.propMgr.numberOfCellsSpinBox.setValue(numberOfCells)

        return text


    def modifyStructure(self):
        """
        Called when a resize handle is dragged to change the length of the 
        segment. (Called upon leftUp) . This method assigns the new parameters 
        for the segment after it is resized and calls 
        preview_or_finalize_structure which does the rest of the job. 
        Note that Client should call this public method and should never call
        the private method self._modifyStructure. self._modifyStructure is 
        called only by self.preview_or_finalize_structure

        @see: B{CntSegment_ResizeHandle.on_release} (the caller)
        @see: B{SelectChunks_GraphicsMode.leftUp} (which calls the 
              the relevent method in DragHandler API. )
        @see: B{exprs.DraggableHandle_AlongLine}, B{exprs.DragBehavior}
        @see: B{self.preview_or_finalize_structure }
        @see: B{self._modifyStructure}        

        As of 2008-02-01 it recreates the structure
        @see: a note in self._createStructure() about use of cntSegment.setProps 
        """
        if self.grabbedHandle is None:
            return        

        self.propMgr.endPoint1 = self.grabbedHandle.fixedEndOfStructure
        self.propMgr.endPoint2 = self.grabbedHandle.currentPosition
        length = vlen(self.propMgr.endPoint1 - self.propMgr.endPoint2 )
        numberOfCells = getNumberOfCellsFromCntLength(cntLength, 'Carbon')
        #self.propMgr.numberOfCellsSpinBox.setValue(numberOfCells)       

        self.preview_or_finalize_structure(previewing = True)  

        self.updateHandlePositions()
        self.glpane.gl_update()

    def makeMenus(self): 
        """
        Create context menu for this command. (Build Cnt mode)
        """
        if not hasattr(self, 'graphicsMode'):
            return

        selobj = self.glpane.selobj

        if selobj is None:
            return

        self.Menu_spec = []

        highlightedChunk = None
        if isinstance(selobj, Chunk):
            highlightedChunk = selobj
        if isinstance(selobj, Atom):
            highlightedChunk = selobj.molecule
        elif isinstance(selobj, Bond):
            chunk1 = selobj.atom1.molecule
            chunk2 = selobj.atom2.molecule
            if chunk1 is chunk2 and chunk1 is not None:
                highlightedChunk = chunk1
        
        if highlightedChunk is None:
            return

        if self.hasValidStructure():        
             
            cntGroup = self.struct.parent_node_of_class(self.assy.CntGroup)
            if cntGroup is None:
                return
            #following should be self.struct.get_CntGroup or self.struct.getCntGroup
            #need to formalize method name and then make change.
            if not cntGroup is highlightedChunk.parent_node_of_class(self.assy.CntGroup):
                item = ("Edit unavailable: Member of a different CntGroup",
                        noop, 'disabled')
                self.Menu_spec.append(item)
                return
        
        highlightedChunk.make_glpane_context_menu_items(self.Menu_spec,
                                                 command = self)


    #START- EXPERIMENTAL CODE Not called anywhere ==============================

    #Using an alternate graphics mode to draw DNA line? 
    #Example: leftDown on a handle enters CntLine graphics mode (but you are in 
    #the same command' now you do the dragging, a cnt rubber band line is drawn 
    #and upon left up, it again enters the default graphics mode. This poses 
    #some challenges -- may be we need to save the event and explicitely 
    #call the CntLine_GM.leftDown, passing this event as an argument. 
    #Other issues include -- We need to specify certain attrs/ methods on the 
    #CntSegment_EditCommand so that CntLineMode_GM works. In general, 
    #for this to work , we need to refactor CntLine_GM at some point 
    #(it was originally designed to work as a temporary mode which returns to 
    #the previous mode after certain mouse clicks.) -- Ninad 2008-02-01

    ##Following is needed by CntLine_GM -- Declare it in class definition
    ##when using CntLine_GM
    ##mouseClickPoints = []

    def EXPERIMENTALswitchGraphicsModeTo(self, newGraphicsMode = 'DEFAULT'):
        """
       EXPERIMENTALswitchGraphicsModeTo -- Not called anywhere. While
       testing feasibility of using CntLine_GM, rename this method to 
       witchGraphicsModeTo and make other modifications as necessary.

       Switch graphics mode of self to the one specified 
       by the client. 
       Changing graphics mode while remaining in the same command has certain 
       advantages and it also bypasses some code related to entering a new 
       command. 
       @param newGraphicsMode: specifies the new graphics mode to switch to
       @type  newGraphicsMode: string
       @see: B{MovePropertyManager.activate_translateGroupBox} 
       """
        #TODO: Make this a general API method if need arises - Ninad 2008-01-25
        assert newGraphicsMode in ['DEFAULT', 'DRAG_HANDLES']

        if newGraphicsMode == 'DEFAULT':
            if self.graphicsMode is self.default_graphicsMode:
                return
            self.graphicsMode = self.default_graphicsMode
            self.graphicsMode.Enter_GraphicsMode()
            self.glpane.update_after_new_graphicsMode()
        elif newGraphicsMode == 'DRAG_HANDLES':
            if self.graphicsMode is self.drag_handles_graphicsMode:
                return 
            self.graphicsMode = self.drag_handles_graphicsMode
            self.graphicsMode.Enter_GraphicsMode()
            self.glpane.update_after_new_graphicsMode()

    def EXPERIMENTAL_create_GraphicsMode(self):
        """
        EXPERIMENTAL_create_GraphicsMode -- Not called anywhere. While
        testing feasibility of using CntLine_GM, rename this method to 
        _create_GraphicsMode and make other modifications as necessary.
        """
        GM_class = self.GraphicsMode_class
        assert issubclass(GM_class, GraphicsMode_API)
        args = [self] 
        kws = {} 


        self.default_graphicsMode = GM_class(*args, **kws)
        self.drag_handles_graphicsMode  = \
            CntSegment_DragHandles_GraphicsMode(*args, **kws)

        self.graphicsMode = self.default_graphicsMode


    def EXPERIMENTAL_setParamsForCntLineGraphicsMode(self):
        """
        Things needed for CntLine_GraphicsMode (CntLine_GM)==================
        EXPERIMENTAL -- call this method in self.init_gui() while experimenting 
        use of CntLine_GM. (or better refactor CntLine_GM for a general use)
        Rename it as "_setParamsForCntLineGraphicsMode"
        Needed for CntLine_GraphicsMode (CntLine_GM). The method names need to
        be revised (e.g. callback_xxx. The prefix callback_ was for the earlier 
        implementation of CntLine mode where it just used to supply some 
        parameters to the previous mode using the callbacks from the 
        previousmode. 
        """
        self.mouseClickLimit = 1
        self.cntRise =  getCntRise('Carbon')

        self.callbackMethodForCursorTextString = \
            self.EXPERIMENTALgetCursorTextForTemporaryMode

        self.callbackForSnapEnabled = self.EXPERIMENTALisRubberbandLineSnapEnabled

        self.callback_rubberbandLineDisplay = \
            self.EXPERIMENTALgetDisplayStyleForRubberbandLine

    def EXPERIMENTALgetCursorTextForTemporaryMode(self, endPoint1, endPoint2):
        """
        EXPERIMENTAL method. rename it to getCursorTextForTemporaryMode while 
        trying out CntLine_GM
        This is used as a callback method in CntLine mode 
        @see: CntLineMode.setParams, CntLineMode_GM.Draw
        """
        cntLength = vlen(endPoint2 - endPoint1)
        numberOfCells = getNumberOfCellsFromCntLength(cntLength, 'Carbon')
        cntLengthString = str(round(cntLength, 3))
        text =  str(numberOfCells)+ "b, "+ cntLengthString 

        #@TODO: The following updates the PM as the cursor moves. 
        #Need to rename this method so that you that it also does more things 
        #than just to return a textString -- Ninad 2007-12-20
        #self.propMgrnumberOfCellssSpinBox.setValue(numberOfCells)

        return ""

    def EXPERIMENTALgetDisplayStyleForRubberbandLine(self):
        """
        EXPERIMENTAL: rename it to: getDisplayStyleForRubberbandLine while 
        experimenting CntLine_GM
        This is used as a callback method in CntLine mode . 
        @return: The current display style for the rubberband line. 
        @rtype: string
        @see: CntLineMode.setParams, CntLineMode_GM.Draw
        """
        return "Ribbons"

    def EXPERIMENTALprovideParamsForTemporaryMode(self, temporaryModeName):
        """
        EXPERIMENTAL: rename it to: provideParamsForTemporaryMode while 
        experimenting CntLine_GM. Also change the calls to various methods 
        in this method (e.g. allback_snapEnabled = 
        self.EXPERIMENTALisRubberbandLineSnapEnabled etc)
        NOTE: This needs to be a general API method. There are situations when 
	user enters a temporary mode , does something there and returns back to
	the previous mode he was in. He also needs to send some data from 
	previous mode to the temporary mode .	 
	@see: B{CntLineMode}
	@see: self.acceptParamsFromTemporaryMode 
        """

        assert temporaryModeName == 'CNT_LINE_MODE'

        mouseClickLimit = None
        cntRise =  getCntRise('Carbon')
        endPoint1 = V(0, 0, 0)

        callback_cursorText = self.EXPERIMENTALgetCursorTextForTemporaryMode
        callback_snapEnabled = self.EXPERIMENTALisRubberbandLineSnapEnabled
        callback_rubberbandLineDisplay = self.EXPERIMENTALgetDisplayStyleForRubberbandLine
        return (mouseClickLimit, 
                cntRise, 
                callback_cursorText, 
                callback_snapEnabled, 
                callback_rubberbandLineDisplay,
                endPoint1
            )   

    def EXPERIMENTALisRubberbandLineSnapEnabled(self):
        """
        rubbernad snap enabled?
        """
        return True

    #END- EXPERIMENTAL CODE Not called anywhere ================================

