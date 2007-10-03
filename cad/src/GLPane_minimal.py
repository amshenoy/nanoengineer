# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
GLPane_minimal.py -- common superclass for GLPane-like widgets.

$Id$

History:

bruce 070914 made this to remind us that GLPane and ThumbView
need a common superclass (and have common code that needs merging).
It needs to be in its own file to avoid import loop problems.
"""

from OpenGL.GL import glDepthRange

from PyQt4.Qt import QGLFormat
from PyQt4.Qt import QGLWidget

from debug_prefs import Choice
from debug_prefs import debug_pref

DEPTH_TWEAK_UNITS = (2.0)**(-32)
DEPTH_TWEAK_VALUE = 100000
    # For bond cylinders subject to shorten_tubes:
    # on my iMac G5, 300 is enough to prevent "patchy highlighting" problems
    # except sometimes at the edges. 5000 even fixes the edges and causes no
    # known harm, so we'd use that value if only that platform mattered.
    #
    # But, on Windows XP (Ninad & Tom), much higher values are needed.
    # By experiment, 100000 is enough on those platforms, and doesn't seem to
    # be too large on them or on my iMac, so we'll go with that for now,
    # but leave it in as a debug_pref. (We made no attempt to get a precise
    # estimate of the required value -- we only know that 10000 is not enough.)
    #
    # We don't know why a higher value is needed on Windows. Could the
    # depth buffer bit depth be different?? This value works out to a bit
    # more than one resolution unit for a 16-bit depth buffer, so that might
    # be a plausible cause. But due to our limited testing, the true difference
    # in required values on these platforms might be much smaller.
    #
    # [bruce 070926]

DEPTH_TWEAK = DEPTH_TWEAK_UNITS * DEPTH_TWEAK_VALUE
    # changed by setDepthRange_setup_from_debug_pref

DEPTH_TWEAK_CHOICE = \
    Choice( [0,1,3,10,
             100,200,300,400,500,600,700,800,900,1000,
             2000,3000,4000,5000,
             10000, 100000, 10**6, 10**7, 10**8],
            defaultValue = DEPTH_TWEAK_VALUE )

class GLPane_minimal(QGLWidget): #bruce 070914
    """
    Mostly a stub superclass, just so GLPane and ThumbView can have a common
    superclass.

    TODO:
    They share a lot of code, which ought to be merged into this superclass.
    Once that happens, it might as well get renamed.
    """

    def __init__(self, parent, shareWidget, useStencilBuffer):
        """
        If shareWidget is specified, useStencilBuffer is ignored: set it in the widget you're sharing with.
        """
        
        if shareWidget:
            self.shareWidget = shareWidget #bruce 051212
            glformat = shareWidget.format()
            QGLWidget.__init__(self, glformat, parent, shareWidget)
            if not self.isSharing():
                print "Request of display list sharing is failed."
                return
        else:
            glformat = QGLFormat()
            if (useStencilBuffer):
                glformat.setStencil(True)
            QGLWidget.__init__(self, glformat, parent)
    
    def should_draw_valence_errors(self):
        """
        Return a boolean to indicate whether valence error
        indicators (of any kind) should ever be drawn in self.
        (Each specific kind may also be controlled by a prefs
        setting, checked independently by the caller. As of 070914
        there is only one kind, drawn by class Atom.)
        """
        return False

    def setDepthRange_setup_from_debug_pref(self):
        global DEPTH_TWEAK
        DEPTH_TWEAK = DEPTH_TWEAK_UNITS * \
                      debug_pref("GLPane: depth tweak", DEPTH_TWEAK_CHOICE)
        return

    def setDepthRange_Normal(self):
        glDepthRange(0.0 + DEPTH_TWEAK, 1.0) # args are near, far
        return

    def setDepthRange_Highlighting(self):
        glDepthRange(0.0, 1.0 - DEPTH_TWEAK)
        return
    pass

# end
