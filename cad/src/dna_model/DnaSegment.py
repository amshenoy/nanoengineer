# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaSegment.py - ... 

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
from dna_model.DnaStrandOrSegment import DnaStrandOrSegment
from debug import print_compact_stack
from chunk import Chunk


class DnaSegment(DnaStrandOrSegment):
    """
    Model object which represents a Dna Segment inside a Dna Group.

    Internally, this is just a specialized Group containing various
    subobjects, described in the superclass docstring.

    Among its (self's) Group.members are its DnaAxisChunks and its
    DnaSegmentMarkers, including exactly one controlling marker.
    These occur in undefined order (??). Note that its DnaStrand
    atoms are not inside it; they are easily found from the DnaAxisChunks.

    [Note: we might decide to put the DnaStrandChunks inside the
     DnaSegment whose axis they attach to, instead; for more info,
     see docstring of class DnaStrand. bruce comment 080111]

    Note that this object will never show up directly in the Model Tree
    once the DNA Data Model is fully implemented, since it will always
    occur inside a DnaGroup (and since it's not a Block).
    """

    # This should be a tuple of classifications that appear in
    # files_mmp._GROUP_CLASSIFICATIONS, most general first.
    # See comment in class Group for more info. [bruce 080115]
    _mmp_group_classifications = ('DnaSegment',)
    
    def edit(self):
        """
        Edit this DnaSegment. 
        @see: DnaSegment_EditCommand
        """
        commandSequencer = self.assy.w.commandSequencer
        if commandSequencer.currentCommand.commandName != "DNA_SEGMENT":
            commandSequencer.userEnterTemporaryCommand('DNA_SEGMENT')
            
        assert commandSequencer.currentCommand.commandName == 'DNA_SEGMENT'
        commandSequencer.currentCommand.editStructure(self)

    #Following methods are NOT IMPLEMENTED YET =================================
    
    def getAxisEndPoints(self):
        """
        Derives and returns the two axis end points based on the atom positions
        of the segment. 
        
        @return: a list containing the two endPoints of the Axis.
        @rtype: list 
        """
        #Temporary implementation that uses chunk class to distinguish an 
        #axis chunk from an ordinary chunk. This method can be revised after
        #Full dna data model implementation -- Ninad 2008-01-21
        endPointList = []
        for m in self.members:
            if isinstance(m, Chunk) and m.isAxisChunk():
                for atm in m.atoms.itervalues():
                    if atm.element.symbol == 'Ae3':                        
                        endPointList.append(atm.posn())
        if len(endPointList) == 2:
            return endPointList[0], endPointList[1]
        elif len(endPointList) > 2:
            print_compact_stack("bug:The axis chunk has more than 2 'Ae' atoms")
        else:
            return None, None
                    
    

# end
