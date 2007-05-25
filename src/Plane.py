# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from ReferenceGeometry import ReferenceGeometry 
from shape import fill
from drawer import drawLineLoop, drawPlane
from constants import black, gray, orange, yellow, darkgreen
from VQT import V,Q, cross, dot, A
from OpenGL.GL import *
from math import pi
from debug import print_compact_traceback
import env
from OpenGL.GLU import gluProject, gluUnProject

#draw handle inside or outside of push-pop matrix that draws the Plane geometry
#default is True (handle drawn inside) 
DEBUG_DRAW_HANDLE_INSIDE = False

class Plane(ReferenceGeometry):    
    sym = "Plane"    
    is_movable = True 
    mutable_attrs = ('center', 'quat')
    icon_names = ["modeltree/plane.png", "modeltree/plane-hide.png"]
    
    copyable_attrs = ReferenceGeometry.copyable_attrs + mutable_attrs
    
    def __init__(self, win, lst = None, READ_FROM_MMP = False):
        ''' 
        @param: win: MainWindow object
        @param: lst: List of atoms or points'''
        ReferenceGeometry.__init__(self, win)        
        self.width = 16
        self.height = 16                    
        self.normcolor = black
        self.fill_color = gray
        
        self.opacity = 0.3
        
        self.handles = []        
        
        #This is used to notify drawing code if it's just for picking purpose
        #copied from jig_planes.ESPImage
        self.pickCheckOnly=False 
        
        if not READ_FROM_MMP:
            self.__init_quat_center(lst)
    
    def __getattr__(self, name): # in class RectGadget
        if name == 'planeNorm':
            return self.quat.rot(V(0.0, 0.0, 1.0))
        else:
            raise AttributeError, 'Plane has no "%s"' % name 
        
    
    def draw(self, glpane, dispdef):
        try:
            glPushName(self.glname)
            self._draw(glpane, dispdef)
        except:
            glPopName()
            print_compact_traceback("ignoring exception when drawing Plane %r: " % self)
        else:
            glPopName()
                   
    def _draw_geometry(self, glpane, color, highlighted=False):
        '''Draw a Plane.'''
        
        # Reference planes don't support textures so set this property to False 
        # in the drawer.drawPlane method        
        textureReady = False
        glPushMatrix()

        glTranslatef( self.center[0], self.center[1], self.center[2])
        q = self.quat
    
        glRotatef( q.angle*180.0/pi, q.x, q.y, q.z)

        hw = self.width/2.0; hh = self.height/2.0
        
        bottom_left = V(- hw,- hh, 0.0)                       
        bottom_right = V(+ hw,- hh, 0.0)        
        top_right = V(+ hw, + hh, 0.0)
        top_left = V(- hw, + hh, 0.0)
        
        
        corners_pos = [bottom_left, bottom_right, 
                       top_right, top_left]          
                
                
        drawPlane(self.fill_color, 
                  self.width, 
                  self.height, 
                  textureReady,
                  self.opacity, 
                  SOLID=True, 
                  pickCheckOnly=self.pickCheckOnly)
        
        if self.picked:
            drawLineLoop(self.color, corners_pos)  
            #See comment near line 138 below -- Ninad 20070525 
            if DEBUG_DRAW_HANDLE_INSIDE:
                self._draw_handles(corners_pos)               
        else:
            if highlighted:
                drawLineLoop(yellow, corners_pos, width=2)
            else:  
                #Following draws the border of the plane in orange color 
                #for it's front side (side that was in front 
                #when the plane was created and a gray border for the back side. 
                if dot(self.getaxis(), glpane.lineOfSight) < 0:
                    bordercolor = gray #backside
                else:
                    bordercolor = color #frontside
                drawLineLoop(bordercolor, corners_pos)                  
        glPopMatrix()
        if not DEBUG_DRAW_HANDLE_INSIDE:            
            #We need to compute the corner positions to draw 
            #the handles. The list 'corners_pos' can't be used for this 
            #purpose as it computes the corners in a translation matrix 
            #whose center is always at the center of the geometry. 
            # Then why not use the above translation matrix for handles?
            #-- we can't do this because then the handles are not drawn parallel
            #to the screen in some orientations (i.e. user doesn't see them as 
            #squares in some orientations) -- ninad 20070518
          
            bottom_left = V(self.center[0] - hw,
                            self.center[1] - hh,
                            self.center[2])
            bottom_right = V(self.center[0] + hw,
                            self.center[1] - hh,
                            self.center[2])
            
            top_right = V(self.center[0] + hw,
                            self.center[1] + hh,
                            self.center[2])
            top_left = V(self.center[0] - hw,
                            self.center[1] + hh,
                            self.center[2])
            
        
            cornerHandleCenters =  [bottom_left,bottom_right,
                                    top_right,top_left]       
                          
            # Draw the handles when selected. 
            if self.picked:
                #[A] Following line draws the handles outside of the 
                # push-pop matrix that draws the plane. But this is wrong. 
                # it works only in front plane. When plane is created in other
                #orientations, the handle geometry is still created in front plane. 
                # This is happening because the 'cornerHandleCenters' computation
                #done above is not correct. 
                #[B] If called inside of the push-pop matrix that does the plane
                #drawing, it uses the correct handle centers, but then there
                #is a problem in correct computation of quaternion that draws the 
                #Handle geometry. The handle geometry should always be drawn 
                #parallel to the screen. 
                #This is not (yet) acheived by doing [B] described above. Need 
                #some more work.  -- Ninad 20070525
                self._draw_handles(cornerHandleCenters)
              
                if highlighted:
                    glPushMatrix()
                    glTranslatef( self.center[0], self.center[1], self.center[2])
                    q = self.quat
                    glRotatef( q.angle*180.0/pi, q.x, q.y, q.z)
                    drawLineLoop(yellow, corners_pos, width=2)
                    glPopMatrix()        
           
        return
           
    def __init_quat_center(self, lst = None):
        if lst:    
            self.atomPos =[]
            for a in lst:
                self.atomPos += [a.posn()]    
            planeNorm = self._getPlaneOrientation(self.atomPos)
            self.center = add.reduce(self.atomPos)/len(self.atomPos)
        else:            
            planeNorm = self.glpane.lineOfSight
            self.center = [0.0,0.0,0.0]        
        self.quat = Q(V(0.0, 0.0, 1.0), planeNorm)
    
    def setWidth(self, newwidth):
        self.width = newwidth
    
    def setHeight(self, newheight):
        self.height = newheight
    
    def getWidth(self):
        return self.width
    
    def getHeight(self):
        return self.height
        
    def getaxis(self):
        return self.planeNorm
        
    def move(self, offset):
        '''Move the plane by <offset>, which is a 'V' object.'''
        self.center += offset
        #Following makes sure that handles move as the geometry moves. 
        #@@ do not call Plane.move method during the Plane resizing. 
        #call recomputeCenter method instead. -- ninad 20070522
        if len(self.handles) == 8:
            for hdl in self.handles:
                assert isinstance(hdl, Handle)
                hdl.move(offset)
            
        
    def rot(self, q):
        self.quat += q
        
    def _getPlaneOrientation(self, atomPos):
        assert len(atomPos) >= 3
        v1 = atomPos[-2] - atomPos[-1]
        v2 = atomPos[-3] - atomPos[-1]
        
        return cross(v1, v2)
    
    def _draw_handles(self, cornerPoints):
        '''' Draw the handles that permit the geometry resizing. 
        Example: For a plane, there will be 8 small squares along the 
        border...4 at plane corners and remaining in the middle 
        of each side of the plane. The handles will be displayed only when the 
        geometry is selected
        @param: cornerPoints : List of corner points. The handles will be
        drawn at these corners PLUS in the middle of each side of tthe Plane'''
        
        handleCenters = list(cornerPoints)
       
        cornerHandleCenters = list(cornerPoints) 
        
        midBtm = (handleCenters[0] + handleCenters[1])/2      
        midRt = (handleCenters[1] + handleCenters[2])/2
        midTop = (handleCenters[2] + handleCenters[3])/2
        midLft = (handleCenters[3] + handleCenters[0])/2
        
       
        for midpt in [midBtm,midRt,midTop, midLft]:
            handleCenters.append(midpt)
        
        if len(self.handles)==8:   
            assert len(self.handles) == len(handleCenters)
            i = 0
            for i in range(len(self.handles)):
                self.handles[i].draw(hCenter = handleCenters[i])
        else:   
            hdlIndex = 0
            for hCenter in handleCenters: 
                handle = Handle(self, self.glpane, hCenter)
                handle.draw() 
                if handle not in self.handles:
                    self.handles.append(handle)
                #handleIndex = 0, 1, 2, 3 -->
                #--> bottomLeft, bottomRight, topRight, topLeft corners respt
                #handleIndex = 4, 5, 6, 7 -->
                #-->midBottom, midRight, midTop, midLeft Handles respt.
                if hdlIndex == 5 or hdlIndex == 7: 
                    handle.setType('X-Handle')
                elif hdlIndex == 4 or hdlIndex == 6:
                    handle.setType('Y-Handle')
                else:
                    handle.setType('Corner')
                
                hdlIndex +=1
                                            
    def recomputeCenter(self, handleOffset):
        ''' Recompute the center of the Plane based on the handleOffset
        This is needed during resizing'''
        
        ##self.move(handleOffset/2.0) 
        self.center += handleOffset/2.0
      
    def resizeGeometry(self, movedHandle, offset):
        
        handleOffset = offset
                            
        new_center = self.center + handleOffset/2.0
        moved_handle_center = movedHandle.center + handleOffset
        
        if movedHandle.getType() == 'X-Handle':
            hw = abs(new_center[0] - moved_handle_center[0])
            self.setWidth(hw*2.0) 
            xOffset = handleOffset
            xOffset[1] -= handleOffset[1]
            xOffset[2] -= handleOffset[2]
            self.recomputeCenter(xOffset)
        elif movedHandle.getType() == 'Y-Handle':
            hh = abs(new_center[1] - moved_handle_center[1]) 
            self.setHeight(hh*2.0)
            yOffset = handleOffset
            yOffset[0] -= handleOffset[0]
            yOffset[2] -= handleOffset[2]
            self.recomputeCenter(yOffset)
        elif movedHandle.getType() == 'Corner':
            hw = abs(new_center[0] - moved_handle_center[0])
            hh = abs(new_center[1] - moved_handle_center[1]) 
            self.setWidth(hw*2.0)
            self.setHeight(hh*2.0)
            cornerOffset = handleOffset
            cornerOffset[2] -= handleOffset[2]
            self.recomputeCenter(cornerOffset)
  
        
class Handle:
    '''@@@EXPERIMENTAL -- ninad 20070517 
    - unreleated with things in handles.py
    - soon it will be moved to handles.py (with added docstrings)-ninad20070521'''
    def __init__(self, parent, glpane, handleCenter):
        self.parent = parent
        #this could be parent.glpane , but pass glpane object explicitely
        #for creating  a handle to avoid any errors
        self.glpane = glpane
        self.center = handleCenter
        # No texture in handles (drawn Handle object). 
        # Ideally the following value in the drawer.drawPlane method 
        #should be False by default.
        self.textureReady = False
        self.pickCheckOnly = False        
        self.glname = env.alloc_my_glselect_name(self)        
        self.type = None      
    
    def draw(self, hCenter = None):
        try:
            glPushName(self.glname)
            if hCenter:
                self._draw(hCenter)    
            else:
                self._draw()
        except:
            glPopName()
            print_compact_traceback("ignoring exception when drawing handle %r: " % self)
        else:
            glPopName()
    
    def _draw(self, hCenter = None, highlighted = False):
        ''' Draw the handle object '''        
        
        if hCenter:
            if self.center != hCenter:
                self.center = hCenter    
        
        if not DEBUG_DRAW_HANDLE_INSIDE:
            #Always draw the handle geometry facing the line of sight. So that 
            #the handles are visible in any orientation of the plane.
            handleNorm = self.glpane.lineOfSight 
            #@@@ ninad20070523 bug when the plane is created after rotating the glpane          
            self.quat = Q(V(0.0, 0.0, 1.0), handleNorm)
        
        #Use glpane's scale for drawing the handle. This makes sure that
        # the handle is non-zoomable. 
        side = self.glpane.scale*0.05                
        glPushMatrix()           
            
        
        #Translate to the center of the handle
        glTranslatef(self.center[0], 
                     self.center[1], 
                     self.center[2])   
        
        if DEBUG_DRAW_HANDLE_INSIDE:
            #Bruce suggested undoing the glpane.quat rotation and plane quat rotation 
            #before drawing the handle geometry. -- ninad 20070525
            parent_q = self.parent.quat        
            glpane_q = self.glpane.quat 
            glRotatef(-parent_q.angle*180.0/pi, parent_q.x, parent_q.y, parent_q.z)          
            glRotatef(-glpane_q.angle*180.0/pi, glpane_q.x, glpane_q.y, glpane_q.z)        
        else:
            q = self.quat     
            glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)
                
        drawPlane(darkgreen, 
              side, 
              side, 
              self.textureReady,
              0.9, 
              SOLID=True, 
              pickCheckOnly=self.pickCheckOnly)         
        
        handle_hw = side/2.0 #handle's half width
        handle_hh = side/2.0 #handle's half height        
        handle_corner = [V(-handle_hw, handle_hh, 0.0), 
               V(-handle_hw, -handle_hh, 0.0), 
               V(handle_hw, -handle_hh, 0.0), 
               V(handle_hw, handle_hh, 0.0)]   
        
        if highlighted:    
            drawLineLoop(orange, handle_corner, width=6)
        else:
            drawLineLoop(black, handle_corner, width=2)                
        glPopMatrix()
        
    def draw_in_abs_coords(self, glpane, color):
        ''' Draw the handle as a highlighted object'''
        if DEBUG_DRAW_HANDLE_INSIDE:            
            q = self.parent.quat  
            glPushMatrix()
            glTranslatef( self.parent.center[0],
                          self.parent.center[1], 
                          self.parent.center[2])
            glRotatef( q.angle*180.0/pi, q.x, q.y, q.z)            
        self._draw(highlighted = True)
        if DEBUG_DRAW_HANDLE_INSIDE:   
            glPopMatrix()
        
    def move(self, offset):
        '''Move the handle by <offset>, which is a 'V' object.'''
        self.center += offset
    
    def setType(self, handleType):
        ''' @param: handleType: returns the '''
        assert handleType in [ 'X-Handle' , 'Y-Handle' , 'Corner']
        self.type = handleType
       
        
    def getType(self):
        '''@return: string self.type that tells whether its a X or Y 
        or a corner handle '''
        assert self.type is not None
        return self.type