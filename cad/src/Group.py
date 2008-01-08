# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Group.py -- Class (or superclass) for all non-leaf nodes in the
internal model tree of Nodes. (See also class Block.)

@author: Josh
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Originally by Josh; gradually has been greatly extended by Bruce,
but the basic structure of Nodes and Groups has not been changed.

Bruce 071110 split Group.py out of Utility.py. (And may soon
split out Node and/or LeafNode as well.)
"""

from debug import print_compact_stack, print_compact_traceback
import platform
import env
from state_constants import S_CHILDREN

from GroupProp import GroupProp
from icon_utilities import imagename_to_pixmap

from Utility import Node

# ==

class Group(Node):
    """
    A kind of Node which groups other nodes (its .members,
    informally called its "kids") in the model tree, for drawing,
    and for selection.

    Its members can be various other kinds of Groups (subtrees of nodes)
    or non-Group Nodes (e.g. Jigs, Chunks).

    Group is used as both a concrete and abstract class.
    (I.e. it's instantiated directly, but also has subclasses.)
    """
    featurename = "" # (redundant with Node)
        # It's intentional that we don't provide this for Group itself, so a selected Group in the MT
        # doesn't bother you by offering wiki help on Group. Maybe we'll leave it off of Chunk as well...
        # but maybe a better system would be to let user turn it off for specific classes they're familiar with,
        # or to relegate it to a help submenu rather than MT context menu, or in some other way make it less visible...
        # [bruce 051201]

    _s_attr_members = S_CHILDREN # this declares group.members for Undo
        # note: group.members are informally called its "kids",
        # but need not be identical to the output of group.MT_kids(),
        # which gives the list of nodes to show as its children in the Model Tree.

    def __init__(self, name, assy, dad, members = (), editCommand = None): ###@@@ review inconsistent arg order
        self.members = [] # must come before Node.__init__ [bruce 050316]
        self.__cmfuncs = [] # funcs to call right after the next time self.members is changed
        Node.__init__(self, assy, name, dad)
        self.open = True
        for ob in members:
            self.addchild(ob)

        #@WARNING: Following (self.editCommand) is a temporary code that 
        # allows editing of DNA Duplex which is, at the moment, same as a 
        # group in the MT. Once we have a DNA object model ready, 
        # the following should be removed/ revised . 
        # See also self.edit where this is being used. -- Ninad 2007-10-26
        self.editCommand = editCommand

        return

    def _um_initargs(self): #bruce 051013 [in class Group]
        # [as of 060209 this is probably well-defined and correct (for most subclasses), but not presently used]
        """
        [Overrides Node._um_initargs; see its docstring.]
        """
        return (self.name, self.assy), {} # note reversed arg order from Node version
            # dad and members (like most inter-object links) are best handled separately

    def _undo_update(self): # in class Group [bruce 060306]
        self.changed_members() # part of fix for bug 1617; fixing it will also require separate changes in MMKit by Mark.
            ###k is this safe to do in arbitrary order vs. other Undo-related updates,
            # or do we need to only do it at the end, and/or in some order when several Groups changed??
            # I don't know, so for now I'll wait and see if we notice bugs from doing it in arbitrary order. [bruce 060306]
        Node._undo_update(self)
        return

    def is_group(self):
        """
        [overrides Node method; see its docstring]
        """
        return True

    open_specified_by_mmp_file = False
    def readmmp_info_opengroup_setitem( self, key, val, interp ): #bruce 050421, to read group open state from mmp file
        """
        This is called when reading an mmp file, for each "info opengroup" record
        which occurs right after this node's "group" record is read and no other node
        (or "group" record) has been read.
           Key is a list of words, val a string; the entire record format
        is presently [050421] "info opengroup <key> = <val>".
        Interp is an object to help us translate references in <val>
        into other objects read from the same mmp file or referred to by it.
        See the calls of this method from files_mmp for the doc of interp methods.
           If key is recognized, set the attribute or property
        it refers to to val; otherwise do nothing (or for subclasses of Group
        which handle certain keys specially, call the same method in the superclass
        for other keys).
           (An unrecognized key, even if longer than any recognized key,
        is not an error. Someday it would be ok to warn about an mmp file
        containing unrecognized info records or keys, but not too verbosely
        (at most once per file per type of info).)
        """
        if key == ['open']:
            # val should be "True" or "False" (unrecognized vals are ignored)
            if val == 'True':
                self.open = True
                self.open_specified_by_mmp_file = True # so code to close the clipboard won't override it
            elif val == 'False':
                self.open = False
                self.open_specified_by_mmp_file = True
            elif platform.atom_debug:
                print "atom_debug: maybe not an error: \"info opengroup open\" ignoring unrecognized val %r" % (val,)
        else:
            if platform.atom_debug:
                print "atom_debug: fyi: info opengroup (in Group) with unrecognized key %r (not an error)" % (key,)
        return

    def drag_move_ok(self):
        return True # same as for Node

    def drag_copy_ok(self):
        return True # for my testing... maybe make it False for Alpha though ###e ####@@@@ 050201

    def is_selection_group_container(self): #bruce 050131 for Alpha
        """
        Whether this group causes each of its direct members to be treated
        as a "selection group" (see another docstring for what that means,
        but note that it can be true of leaf nodes too, in spite of the name).
        [Intended to be overridden only by the Clipboard.]
        """
        return False # for most groups

    def haspicked(self): # bruce 050126
        """
        Whether node's subtree has any picked members.
        [See comments in Node.haspicked docstring.]
        """
        if self.picked:
            return True
        for m in self.members:
            if m.haspicked():
                return True
        return False

    def changed_members(self): #bruce 050121 new feature, now needed by depositMode
        """
        Whenever something changes self.members in any way (insert, delete, reorder),
        it MUST call this method to inform us (but only *after* it makes the change);
        we'll inform other interested parties, if any.
        (To tell us you're an interested party, use call_after_next_changed_members.)
           Notes: This need not be called after changes in membership *within* our members,
        only after direct changes to our members list. Our members list is public, but
        whether it's incrementally changed (the same mutable list object) or replaced is
        not defined (and for whatever wants to change it, either one is acceptable).
        It is deprecated for anything other than a Group (or subclass) method to directly
        change self.members, but if it does, calling this immediately afterwards is required.
        [As of 050121 I don't know for sure if all code yet follows this rule, but I think it does. ##k]
        """
        if self.part:
            self.part.changed() # does assy.changed too
        elif self.assy:
            # [bruce 050429 comment: I'm suspicious this is needed or good if we have no part (re bug 413),
            #  but it's too dangerous to change it just before a release, so bug 413 needs a different fix
            #  (and anyway this is not the only source of assy.changed() from opening a file -- at least
            #   chunk.setDisplay also does it). For Undo we might let .changed() propogate only into direct
            #   parents, and then those assy.changed() would not happen and bug 413 might be fixable differently.]
            self.assy.changed()
            # it is ok for something in part.changed() or assy.changed() to modify self.__cmfuncs
        cm = self.__cmfuncs
        if cm:
            self.__cmfuncs = [] # must do this first in case func appends to it
            for func in cm:
                try:
                    func(self)
                        # pass self, in case it's different from the object
                        # they subscribed to (due to kluge_change_class)
                except:
                    print_compact_traceback("error in some cmfunc, ignored by %r: " % self)
        return

    def call_after_next_changed_members(self, func, only_if_new = False):
        """
        Call func once, right after the next time anything changes self.members.
        At that time, pass it one argument, self; ignore its retval; print error message
        (in debug version only) if it has exceptions.
           If our members are taken over by another Group instance (see kluge_change_class),
        then it, not us, will call func and be the argument passed to func.
           Typically, func should be an "invalidation function", recording the need to
        update something; when that update later occurs, it uses self.members and again
        supplies a func to this method. (If every call of func did an update and gave us
        a new func to record, this might be inefficient when self.members is changed many
        times in a row; nevertheless this is explicitly permitted, which means that we
        explicitly permit func, when called from our code, to itself call this method,
        supplying either the same func or a new one.)
        """
        if only_if_new and (func in self.__cmfuncs):
            return
        self.__cmfuncs.append( func) # might occur during use of same func!

    def openable(self): # overrides Node.openable()
        """
        whether tree widgets should permit the user to open/close their view of this node
        """
        # if we decide this depends on the tree widget or on something about it,
        # we'll have to pass in some args... don't do that unless/until we need to.
        return True

    # methods before this are by bruce 050108 and should be reviewed when my rewrite is done ###@@@

    def kluge_change_class(self, subclass):
        #bruce 050109 ###@@@ temporary [until files_mmp & assy make this kind of assy.root, shelf, tree on their own]
        """
        Return a new Group with this one's members but of the specified subclass
        (and otherwise just like this Group, which must be in class Group itself,
        not a subclass). This won't be needed once class assembly is fixed to make
        the proper subclasses directly.
        """
        assert self.__class__ is Group
        new = subclass(self.name, self.assy, self.dad) # no members yet
        assert isinstance(new, Group) # (but usually it's also some subclass of Group, unlike self)
        if self.dad:
            # don't use addmember, it tells the assy it changed
            # (and doesn't add new in right place either) --
            # just directly patch dad's members list to replace self with new
            ind = self.dad.members.index(self)
            self.dad.members[ind] = new
                # don't tell dad its members changed, until new is finished (below)
            self.dad = None # still available in new.dad if we need it
        new.members = self.members # let new steal our members directly
        new.__cmfuncs = self.__cmfuncs # and take responsibility for our members changing...
        self.__cmfuncs = []
        # self should no longer be used; enforce this
        self.members = 333 # not a sequence
        self.node_icon = "<bug if this is called>"
        for mem in new.members:
            mem.dad = new
            # bruce 050205:
            # should we now call mem.changed_dad()? reasons yes: new's new class might differ in rules for selgroup or space
            # (e.g. be the top of a selgroup) and change_dad might be noticing and responding to that change,
            # so this might turn out to be required if something has cached that info in mem already.
            # reasons no: ... some vague uneasiness. Oh, it might falsely tell assy it changed, but I think our caller
            # handles that. So yes wins, unless bugs show up!
            # BUT: don't do this until we're all done (so new is entirely valid).
            ## mem.changed_dad()
        for attr in ['open', 'hidden', 'picked']:
            # not name, assy, dad (done in init or above), selgroup, space (done in changed_dad)
            try:
                val = getattr(self, attr)
            except AttributeError:
                pass # .open will go away soon;
                # others are probably always defined but I'm not sure
                # (and should not care here, as long as I get them all)
            else:
                setattr(new, attr, val)
        for mem in new.members:
            mem.changed_dad() # reason is explained above [bruce 050205]
        new.dad.changed_members() # since new class is different from self.class, this might be needed ###@@@ is it ok?
        return new

    # bruce 050113 deprecated addmember and confined it to Node; see its docstring.
    # bruce 071110 split def addmember between Node and Group,
    # so Node needn't import Group now that they're in different modules.
    def addmember(self, node, before_or_top = False):
        """
        [Deprecated public method]
        [overrides Node implem; different behavior;
         see Node implem docstring for documentation of both implems]
        """
        self.addchild( node, top = before_or_top)
        return

    def addchild(self, newchild, _guard_ = 050201, top = False, after = None, before = None): # [renamed from addmember - bruce 050113]
        """
        Add the given node, newchild, to the end (aka. bottom) of this Group's members list,
        or to the specified place (top aka. beginning, or after some child or index,
        or before some child or index) if one of the named arguments is given.
        Ok even if newchild is already a member of self, in same or different
        location than requested (it will be moved), or a member of some other Group
        (it will be removed). (Behavior with more than one named argument is undefined.)
           Note: the existence of this method (as an attribute) might be used as a check
        for whether a Node can be treated like a Group [as of 050201].
           Special case: legal and no effect if newchild is None or 0 (or anything false);
        this turns out to be needed by assy.copy_sel/Group.copy or Jig.copy! [050131 comment]
        [Warning (from when this was called addmember):
         semantics (place of insertion, and optional arg name/meaning)
         are not consistent with Node.addmember; see my comments in its docstring.
         -- bruce 050110]
        [note, 050315: during low-level node-tree methods like addchild and delmember,
         and also during pick and unpick methods,
         there is no guarantee that the Part structure of our assy's node tree is correct,
         so checkparts should not be called, and assy.part should not be asked for;
         in general, these methods might need to know that each node has a part (perhaps None),
         but they should treat the mapping from nodes to parts as completely arbitrary,
         except for calling inherit_part to help maintain it.]
        """
        #bruce 050110/050206 updated docstring based on current code
        # Note: Lots of changes implemented at home 050201-050202 but not committed until
        # 050206 (after Alpha out); most dates 050201-050202 below are date of change at home.
        #bruce 050201 added _guard_, after, before
        assert _guard_ == 050201
        if newchild is None:
            #bruce 050201 comment: sometimes newchild was the number 0,
            # since Group.copy returned that as a failure code!!!
            # Or it can be None (Jig.copy, or Group.copy after I changed it).
            return

        #bruce 050205:
        # adding several safety checks (and related new feature of auto-delmember)
        # for help with MT DND; they're a good idea anyway.
        # See also today's changes to changed_dad().
        if newchild.dad and not (newchild in newchild.dad.members):
            # This is really a bug or a very deprecated behavior, but we tolerate it for now.
            # Details: some node-creating methods like molecule.copy and/or Group.copy
            # have the unpleasant habit of setting dad in the newly made node
            # without telling the dad! This almost certainly means the other
            # dad-related aspects of the node are wrong... probably best to just pretend
            # those methods never did that. Soon after Alpha we should fix them all and then
            # make this a detected error and no longer tolerate it.
            if platform.atom_debug:
                msg = "atom_debug: addchild setting newchild.dad to None " \
                    "since newchild not in dad's members: %s, %s" % (self, newchild)
                print_compact_stack(msg)
            newchild.dad = None
        if newchild.is_ascendant(self):
            #bruce 050205 adding this for safety (should prevent DND-move cycles as a last resort, tho might lose moved nodes)
            if platform.atom_debug:
                # this msg covers newchild is self too since that's a length-1 cycle
                print "atom_debug: addchild refusing to form a cycle, " \
                      "doing nothing; this indicates a bug in the caller:", self, newchild
            return
        if newchild.dad:
            # first cleanly remove newchild from its prior home.
            # (Callers not liking this can set newchild.dad = None before calling us.
            #  But doing so (or not liking this) is deprecated.)
            if newchild.dad is self:
                # this might be wanted (as a way of moving a node within self.members)
                # (and a caller might request it by accident when moving a node from a general position,
                #  so we want to cooperate), but the general-case code won't work
                # if the before or after options were used, whether as nodes (if the node used as a marker is newchild itself)
                # or as indices (since removal of newchild will change indices of subsequent nodes).
                # So instead, if those options were used, we fix them to work.
                # We print a debug msg just as fyi; that can be removed once this is stable and tested.
                if platform.atom_debug and 0:
                    # i'll remove this msg soon after i first see it.
                    print "atom_debug: fyi: addchild asked to move newchild " \
                          "within self.members, might need special cases", self, newchild
                    print "...options: top = %r, after = %r, before = %r" % (top , after , before)
                if type(before) is type(1):
                        # indices will change, use real nodes instead
                        # (ok even if real node is 'newchild'! we detect that below)
                    before = self.members[before]
                if type(after) is type(1):
                    after = self.members[after]
                if before is newchild or after is newchild:
                    # this is a noop, and it's basically a valid request, so just do it now (i.e. return immediately);
                    # note that general-case code would fail since these desired-position-markers
                    # would be gone once we remove newchild from self.members.
                    return
                # otherwise (after our fixes above) the general-case code should be ok.
                # Fall thru to removing newchild from prior home (in this case, self),
                # before re-adding it in a new place.
            # remove newchild from its prior home (which may or may not be self):
            newchild.dad.delmember(newchild) # this sets newchild.dad to None, but doesn't mess with its .part, .assy, etc
        # Only now will we actually insert newchild into self.
        # [end of this part of bruce 050205 changes]

        ## self.assy.changed() # now done by changed_members below
            #e (and what about informing the model tree, if it's displaying us?
            #   probably we need some subscription-to-changes or modtime system...)
        if top:
            self.members.insert(0, newchild) # Insert newchild at the very top
        elif after is not None: # 0 has different meaning than None!
            if type(after) is not type(0):
                after = self.members.index(after) # raises ValueError if not found, that's fine
            if after == -1:
                self.members += [newchild] # Add newchild to the bottom (.insert at -1+1 doesn't do what we want for this case)
            else:
                self.members.insert(after+1, newchild) # Insert newchild after the given position #k does this work for negative indices?
        elif before is not None:
            if type(before) is not type(0):
                before = self.members.index(before) # raises ValueError if not found, that's fine
            self.members.insert(before, newchild) # Insert newchild before the given position #k does this work for negative indices?
        else:
            self.members.append(newchild) # Add newchild to the bottom, i.e. end (default case)
        newchild.dad = self
        newchild.changed_dad()
        newchild.dad.changed_members() # must be done *after* they change and *after* changed_dad has made them acceptable for new dad
        # note: if we moved newchild from one place to another in self,
        # changed_members is called twice, once after deletion and once after re-insertion.
        # probably ok, but I should #doc this in the related subscriber funcs
        # so callers are aware of it. [bruce 050205]
        return

    def delmember(self, obj):
        if obj.dad is not self: # bruce 050205 new feature -- check for this (but do nothing about it)
            if platform.atom_debug:
                print_compact_stack( "atom_debug: fyi: delmember finds obj.dad is not self: ") #k does this ever happen?
        obj.unpick() #bruce 041029 fix bug 145 [callers should not depend on this happening! see below]
            #k [bruce 050202 comment, added 050205]: review this unpick again sometime, esp re DND drag_move
            # (it might be more relevant for addchild than for here; more likely it should be made not needed by callers)
            # [bruce 050203 review: still needed, to keep killed obj out of selmols,
            #  unless we revise things enough to let us invalidate selmols here, or the like;
            #  and [050206] we should, since this side effect is sometimes bad
            #  (though I forget which recent case of it bugged me a lot).]
        ## self.assy.changed() # now done by changed_members below
        try:
            self.members.remove(obj)
        except:
            # relying on this being permitted is deprecated [bruce 050121]
            if platform.atom_debug:
                print_compact_stack( "atom_debug: fyi: delmember finds obj not in members list: ") #k does this ever happen?
            return
        obj.dad = None # bruce 050205 new feature
        self.changed_members() # must be done *after* they change
        return

    def steal_members(self): #bruce 050526
        """
        Remove all of this group's members (like delmember would do)
        and return them as a list. Assume self doesn't yet have a dad and no members are picked.

        [Private method, for copy -- not reviewed for general use!]
        """
        res = self.members
        self.members = []
        for obj in res:
            if obj.dad is not self: # error, debug-reported but ignored
                if platform.atom_debug:
                    print_compact_stack( "atom_debug: fyi: steal_members finds obj.dad is not self: ") #k does this ever happen?
            obj.dad = None
        ## assume not needed for our private purpose, though it would be needed in general: self.changed_members()
        return res

    def pick(self):
        """
        select the Group -- and all its members! [see also pick_top]

        [overrides Node.pick]
        """
        Node.pick(self)
            # bruce 050131 comment: important for speed to do Node.pick first,
            # so ob.pick() sees it's picked when its subr scans up the tree
        for ob in self.members:
            ob.pick()
        from debug_prefs import debug_pref_History_print_every_selected_object
        if debug_pref_History_print_every_selected_object(): #bruce 070504 added this condition
            # bruce 050131 comment:
            # I'm very skeptical of doing this history.message
            # recursively, but I'm not changing it for Alpha
            msg = self.description_for_history() # bruce 050121 let subclass decide on this
            env.history.message( msg )
        return

    def description_for_history(self):
        """
        Return something to print in the history whenever we are selected

        [some subclasses should override this]
        """
        return "Group Name: [" + self.name +"]"

    def unpick(self):
        """
        unselect the Group -- and all its members! [see also unpick_top]
        """
        Node.unpick(self)
        for ob in self.members:
            ob.unpick()

    def unpick_top(self): #bruce 050131 for Alpha: bugfix
        """
        [Group implem -- go up but don't go down]
        """
        #redoc, and clean it all up
        Node.unpick(self)

    def unpick_all_members_except(self, node): #bruce 050131 for Alpha
        """
        [private method; #doc; overrides Node method]
        """
        #e should probably inline into unpick_all_except and split that for Node/Group
        res = False
        for ob in self.members:
            res1 = ob.unpick_all_except( node)
            res = res or res1
            # note: the above is *not* equivalent (in side effects)
            # to res = res or ob.unpick_all_except( node)!
        return res

    def inherit_part(self, part): # Group method; bruce 050308
        """
        Self (a Group) is inheriting part from its dad.
        Set this part in self and all partless kids
        (assuming those are all at the top of the nodetree under self).
        [overrides Node method]
        """
        Node.inherit_part(self, part)
        for m in self.members:
            if m.part is None:
                m.inherit_part(part)
        return

    def hide(self):
        for ob in self.members:
            ob.hide()

    def unhide(self):
        for ob in self.members:
            ob.unhide()

    def apply2all(self, fn):
        """
        Apply fn to self and (as overridden here in Group) all its members.
        It's safe for fn to modify self.members list (since we scan a copy),
        but if members of not-yet-scanned nodes are modified, that will affect
        what nodes are reached by our scan, since each nodes' members list is
        copied only when we reach it. For example, if fn moves a node to a later
        subtree, then the same apply2all scan will reach the same node again
        in its new position.
        """
        fn(self)
        for ob in self.members[:]:
            ob.apply2all(fn)

    def apply2tree(self, fn): #e rename?
        """
        Like apply2all, but only applies fn to all Group nodes (at or under self).
        """
        fn(self)
        for ob in self.members[:]:
            ob.apply2tree(fn)

    def apply2picked(self, fn):
        """
        Apply fn to the topmost picked nodes under (or equal to) self.
        That is, scan the tree of self and its members (to all levels including leaf nodes),
        applying fn to all picked nodes seen, but not scanning into the members of picked nodes.
        Thus, for any node, fn is never applied to both that node and any of its ancestors.
        For effect of fn modifying a members list, see comments in apply2all docstring.
        [An example of (i hope) a safe way of modifying it, as of 050121, is in Group.ungroup.]
        """
        if self.picked:
            fn(self)
        else:
            for ob in self.members[:]:
                ob.apply2picked(fn)

    def hindmost(self): ###@@@ should rename
        """
        [docstring is meant for both Node and Group methods taken together:]
        Thinking of nodes as subtrees of the model tree, return the smallest
        subtree of self which contains all picked nodes in this subtree, or None
        if there are no picked nodes in this subtree. Note that the result does
        not depend on the order of traversal of the members of a Group.
        """
        if self.picked:
            return self
        node = None
        for x in self.members:
            h = x.hindmost()
            if node and h:
                return self
            node = node or h
        return node

    def permits_ungrouping(self):
        """
        Should the user interface permit users to dissolve this Group
        using self.ungroup?
        [Some subclasses should override this.]
        """
        return True # yes, for normal groups.

    def ungroup(self):
        """
        If this Node is a Group, dissolve it, letting its members
        join its dad, if this is possible and if it's permitted as a
        user-requested operation. [bruce 050121 thinks this should be
        split into whether this is permitted, and doing it whether or
        not it's permitted; the present method is really a UI operation
        rather than a structural primitive.]
        [overrides Node.ungroup]
        """
        #bruce 050121 revised: use permits_ungrouping;
        # add kids in place of self within dad (rather than at end)
        if self.dad and self.permits_ungrouping():
            ## if self.name == self.assy.name: return
            ## (that's now covered by permits_ungrouping)
            for x in self.members[:]:
                ## x.moveto(self.dad) #e should probably put them before self in there
                self.delmember(x)
                self.addsibling(x, before = True)
                    # put them before self, to preserve order [bruce 050126]
            self.kill()

    # == Group copy methods [revised/added by bruce 050524-050526]

    def will_copy_if_selected(self, sel, realCopy): # wware 060329 added realCopy arg
        if realCopy:
            # [bruce 060329 comment on wware code:]
            # This recursion is just to print warnings.
            # It's safe for now, since this function is apparently not itself called recursively
            # while copying Group members, but that might change, and if it does this will also need to change.
            # It also appears to be incorrect, at least in some cases, e.g. a Measure Distance jig in a Group
            # gets copied even if only one atom does (in spite of having printed this message),
            # though the produced object gives a traceback when displayed.
            # And the easiest fix for that might be for copying to do a recursive call of this,
            # which is exactly what would make this method's own recursion unneeded and unsafe
            # (it would become exponential in number of nested Groups, in runtime and number of redundant warnings).
            for x in self.members:
                x.will_copy_if_selected(sel, True)
        return True

    def copy_full_in_mapping(self, mapping): # Group method [bruce 050526]
        """
        #doc; overrides Node method; copies any subclass of Group as if it was a plain Group
        [subclasses can override or extend that behavior if desired]
        """
        new = Group(self.name, mapping.assy, None)
        self.copy_copyable_attrs_to(new)
            # redundantly copies .name; also copies .open
            # (This might be wrong for some Group subclasses! Not an issue for now, but someday
            #  it might be better to use attrlist from target, or intersection of their attrlists...)
        mapping.record_copy(self, new) # asserts it was not already copied
        for mem in self.members:
            memcopy = mem.copy_full_in_mapping(mapping) # can be None, if mem refused to be copied
            if memcopy is not None:
                new.addchild(memcopy)
        return new

    # ==

    def kill(self): # in class Group
        #bruce 050214: called Node.kill instead of inlining it; enhanced Node.kill;
        # and fixed bug 381 by killing all members first.
        self._prekill() # this has to be done before killing the members, even though Node.kill might do it too [bruce 060327]
        for m in self.members[:]:
            m.kill()
        Node.kill(self)

    def _set_will_kill(self, val): #bruce 060327 in Group
        """
        [private helper method for _prekill; see its docstring for details;
        subclasses with owned objects should extend this]
        """
        Node._set_will_kill( self, val)
        for m in self.members:
            m._set_will_kill( val)
        return

    def reset_subtree_part_assy(self): #bruce 051227
        """
        [overrides Node method]
        """
        for m in self.members[:]:
            m.reset_subtree_part_assy()
        Node.reset_subtree_part_assy(self)
        return

    def is_ascendant(self, node):
        """
        [overrides Node.is_ascendant, which is a very special case of the same semantics]
        Returns True iff self is an ascendant of node,
        i.e. if the subtree of nodes headed by self contains node.
        (node must be a Node or None (for None we return False);
         thus it's legal to call this for node being any node's dad.)
        """
            #e rename nodetree_contains? is_ancestor? (tho true of self too)
            #e or just contains? (no, not obvious arg is a node)
        while node is not None:
            if node is self:
                return True
            node = node.dad
        return False

    def nodespicked(self):
        """
        Return the number of nodes currently selected in this subtree.
        [Overrides Node.nodespicked()]
        Warning (about current implementation [050113]):
        scans the entire tree... calling this on every node in the tree
        might be slow (every node scanned as many times as it is deep in the tree).
        """
        npick = Node.nodespicked(self)
            # bruce 050126 bugfix: was 0 (as if this was called leavespicked)
        for ob in self.members: 
            npick += ob.nodespicked()
        return npick

    def node_icon(self, display_prefs):
        open = display_prefs.get('open', False)
        if open:
            return imagename_to_pixmap("modeltree/group-expanded.png")
        else:
            return imagename_to_pixmap("modeltree/group-collapsed.png")

    def kids(self, display_prefs): #bruce 050109 [#k is this used?] #080108 not used; soon to be renamed MT_kids
        """
        [Overrides Node.kids(); is overridden in our subclass Block]
        
        Return the ordered list of our kids which should be displayed in a model
        tree widget which is using (for this node itself) the given display prefs
        (which might include the boolean pref 'open', default False, telling us
         whether the tree widget plans to show our kids or not).
        (Don't include inter-kid gaps for drag&drop explicitly; see another method
         for that. ###nim)
        Subclasses can override this; this version is valid for any Group whose .members
        don't need filtering or updating, or augmenting (like PartGroup does as of 050109).
         [Note that it is (probably) perfectly ok for subclasses to have a set of kids which is
        not related to their members, provided callers (tree widgets) never assume node.dad
        corresponds to the parent relation in their own tree of display items. I don't know
        how well the existing caller (modelTree.py) follows this so far. -- bruce 050113]
        """
        if not self.openable() or not display_prefs.get('open', False):
            ###@@@ I suspect this check should always be done in the tree widget,
            # so we don't have to do it in Group methods. [bruce 050113]
            return []
        # Historical note: self.members used to be stored in reversed order, but
        # Mark fixed that some time ago. Some callers in modelTree needed reversed
        # members list, after that, not because it was stored in reverse order as
        # it had been, but because modeltree methods added tree items in reverse
        # order (which I fixed yesterday).
        # [bruce 050110 inference from addmember implems/usage]
        return list(self.members)

    def edit(self):
        """
        [this is overridden in some subclasses of Group]
        """
        if self.editCommand:
            commandSequencer = self.assy.w.commandSequencer
            commandSequencer.userEnterCommand('DNA_DUPLEX')
            currentCommand = commandSequencer.currentCommand
            assert currentCommand.commandName == 'DNA_DUPLEX'
            currentCommand.editStructure(self)
        else:
            cntl = GroupProp(self) # Normal group prop
            cntl.exec_()
            self.assy.mt.mt_update()

    def getProps(self):
        """
	Temporary method to support Dna duplex editing. see Group.__init__ for 
	a comment
	"""
        if self.editCommand:
            props = ()
            return props

    def setProps(self, props):
        """
	Temporary method to support Dna duplex editing. see Group.__init__ for 
	a comment
	"""
        pass

    def dumptree(self, depth = 0):
        print depth * "...", self.name
        for x in self.members:
            if x.dad is not self:
                print "bad thread:", x, self, x.dad
            x.dumptree(depth + 1)
        return

    def draw(self, glpane, dispdef): #bruce 050615, 071026 revised this
        if self.hidden:
            #k does this ever happen? This state might only be stored on the kids... [bruce 050615 question]
            return
        self.draw_begin(glpane, dispdef)    
        try:
            for ob in self.members: ## [:]:
                if not ob.draw_later_due_to_translucency:
                    #Exclude any ESP image drawing here because of its translucency. [Huaicai 9/28/05]
                    # (They will be drawn later when GraphicsMode.Draw_after_highlighting calls
                    #  the misnamed self._drawESPImage. [bruce 071026 comment])
                    ob.draw(glpane, dispdef)
            #k Do they actually use dispdef? I know some of them sometimes circumvent it (i.e. look directly at outermost one).
            #e I might like to get them to honor it, and generalize dispdef into "drawing preferences".
            # Or it might be easier for drawing prefs to be separately pushed and popped in the glpane itself...
            # we have to worry about things which are drawn before or after main drawing loop --
            # they might need to figure out their dispdef (and coords) specially, or store them during first pass
            # (like renderpass.py egcode does when it stores modelview matrix for transparent objects).
            # [bruce 050615 comments]
        except:
            print_compact_traceback("exception in drawing some Group member; skipping to end: ")
        self.draw_end(glpane, dispdef)
        return

    def draw_begin(self, glpane, dispdef): #bruce 050615
        """
        Subclasses can override this to change how their child nodes are drawn.
        """
        pass

    def draw_end(self, glpane, dispdef): #bruce 050615
        """
        Subclasses which override draw_begin should also override draw_end
        to undo whatever changes were made by draw_begin
        (preferably by popping stacks, rather than by doing inverse transformations,
         which only work if nothing was messed up by child nodes or exceptions from them,
         and which might be subject to numerical errors).
        """
        pass

    def getstatistics(self, stats):
        """
        add group to part stats
        """
        stats.ngroups += 1
        for ob in self.members:
            ob.getstatistics(stats)

    def writemmp(self, mapping): #bruce 050322 revised interface
        mapping.write("group (" + mapping.encode_name(self.name) + ")\n")
        mapping.write("info opengroup open = %s\n" % (self.open and "True" or "False")) #bruce 050421
            # All "info opengroup" records should be written before we write any of our members.
            # If Group subclasses override this method (and don't call it), they'll need to behave similarly.
        # [bruce 050422: this is where we'd write out "jigs moved forward" if they should come at start of this group...]
        for xx in mapping.pop_forwarded_nodes_after_opengroup(self):
            mapping.write_forwarded_node_for_real(xx)
        for x in self.members:
            x.writemmp(mapping)
            # [bruce 050422: ... and this is where we'd write them, to put them after some member leaf or group.]
            for xx in mapping.pop_forwarded_nodes_after_child(x):
                mapping.write_forwarded_node_for_real(xx)
        mapping.write("egroup (" + mapping.encode_name(self.name) + ")\n")

    def writepov(self, f, dispdef):
        if self.hidden:
            return
        for x in self.members:
            x.writepov(f, dispdef)

    def writemdl(self, alist, f, dispdef):
        if self.hidden:
            return
        for x in self.members:
            x.writemdl(alist, f, dispdef)

    def __str__(self):
        return "<group " + self.name +">"

    def move(self, offset): # in Group [bruce 070501 added this to Node API]
        """
        [overrides Node.move]
        """
        for m in self.members:
            m.move(offset)
        return

    def pickatoms(self): # in Group [bruce 070501 added this to Node API]
        """
        [overrides Node method]
        """
        npicked = 0
        for m in self.members:
            npicked += m.pickatoms()
        return npicked

    pass # end of class Group

# end
