# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
THIS FILE IS PRESENTLY OWNED BY BRUCE -- please don't change it in any way,
however small, unless this is necessary to make Atom work properly for other developers.
[bruce 040921, 041015, ...]

$Id$

Extrude mode. Not yet finished (especially ring mode), as of 050107.

-- bruce 040924/041011/041015
"""

extrude_loop_debug = 0 # do not commit with 1, change back to 0

from modes import *


from handles import *
from debug import print_compact_traceback
import math #k needed?
from chunk import bond_at_singlets #k needed?
import platform
from widgets import FloatSpinBox, TogglePrefCheckBox

show_revolve_ui_features = 1 # for now

class BendData:
    """instances hold sets of attributes related to a single "bend value" (inter-unit rotation-quat, etc).
    
    This class (and concept) exists only to support Revolve, but it can also be used for bend-features in Extrude.
    We'll be set up to permit, in general, placing successive units around any spiral or screw
    (though the UI may or may not permit this level of generality to be used).
    """
    pass # not yet used or fully designed; see a notesfile    

MAX_NCOPIES = 360 # max number of extrude-unit copies. Should this be larger? Motivation is to avoid "hangs from slowness".

# bruce 040920: until MainWindow.ui does the following, I'll do it manually:
# (FYI: I will remove this, and the call to this, after MainWindowUI does the same stuff.
#  But first I will be editing this function a lot to get the dashboard contents that I need.)
def do_what_MainWindowUI_should_do(self):
    "self should be the main MWSemantics object -- at the moment this is a function, not a method"

    ### for now we must set up dashboards for both extrude and revolve. at first they are just the same one.
    # and when we show it we should patch the label...

    from qt import SIGNAL, QToolBar, QLabel, QLineEdit, QSpinBox

    # 2. make a toolbar to be our dashboard, similar to the cookieCutterToolbar
    # (based on the code for cookieCutterToolbar in MainWindowUI)

    self.extrudeDashboard = QToolBar(QString(""),self,Qt.DockBottom)
    ## self.extrudeToolbar = self.extrudeDashboard # bruce 041007 so I don't have to rename this in MWsemantics.py yet

    self.revolveDashboard = self.extrudeDashboard
    ### for now, let them be the same... should be ok unless we show new before hiding old

    self.extrudeDashboard.setGeometry(QRect(0,0,515,29)) ### will probably be wrong once we modify the contents
    self.extrudeDashboard.setBackgroundOrigin(QToolBar.WidgetOrigin)

    self.textLabel_extrude_toolbar = QLabel(self.extrudeDashboard,"textLabel_extrude_toolbar")
    # note: the string in the next line used to be "Extrude Mode", in two places in the file
    self.textLabel_extrude_toolbar.setText(self._MainWindow__tr("extrude or revolve 1")) # see note below about __tr

    self.extrudeDashboard.addSeparator()

    # make it convenient to revise nested vbox, hbox structures for the UI
    from widgets import widget_filler
    wf = widget_filler( self.extrudeDashboard, label_prefix = "extrude_label_", textfilter = self._MainWindow__tr )
    parent_now = wf.parent
    begin = wf.begin
    end = wf.end
    insertlabel = wf.label
    
    self.extrudeSpinBox_circle_n = None # if not set later
    
    if show_revolve_ui_features:
        w = self
        w.extrude_productTypeComboBox = QComboBox(0,parent_now(),"extrude_productTypeComboBox") ###k what is '0'?
        w.extrude_productTypeComboBox.clear() #k needed??
        w.extrude_productTypeComboBox.insertItem("rod") # these names are seen by user but not by our code
        w.extrude_productTypeComboBox.insertItem("ring")
        ## w.extrude_productTypeComboBox.insertItem("screw") ### remove this one, doesn't work yet
        #e add twist? (twisted rod)
        w.extrude_productTypeComboBox_ptypes = ["straight rod", "closed ring", "corkscrew"] # names used in the code, same order
         # # # # if you comment out items from combobox, you also have to remove them from this list unless they are at the end!!!

        if begin(QVBox):
            if begin(QHBox):
                insertlabel(" N ")
                self.extrudeSpinBox_n = QSpinBox(parent_now(), "extrudeSpinBox_n") # dup code to below
            end()
##            if begin(QHBox):
##                insertlabel("(m)")
##                self.extrudeSpinBox_circle_n = QSpinBox(parent_now(), "extrudeSpinBox_circle_n") # really for revolve
##            end()
        end()
    else:
        insertlabel(" N ")
        self.extrudeSpinBox_n = QSpinBox(parent_now(), "extrudeSpinBox_n") # dup code to above
        self.extrudeSpinBox_circle_n = None
    #
    
    self.extrudeSpinBox_n.setRange(1,MAX_NCOPIES)
    
    self.extrudeDashboard.addSeparator()

    if begin(QVBox):
        if begin(QHBox):
            insertlabel(" X ") # number of spaces is intentionally different on different labels
            self.extrudeSpinBox_x = FloatSpinBox(parent_now(), "extrudeSpinBox_x")
        end()
        if begin(QHBox):
            insertlabel(" Z ")
            self.extrudeSpinBox_z = FloatSpinBox(parent_now(), "extrudeSpinBox_z")
        end()
    end()
    if begin(QVBox):
        if begin(QHBox):
            insertlabel("      Y ")
            self.extrudeSpinBox_y = FloatSpinBox(parent_now(), "extrudeSpinBox_y")
        end()
        if begin(QHBox):
            insertlabel(" length ") # units?
            self.extrudeSpinBox_length = FloatSpinBox(parent_now(), "extrudeSpinBox_length", for_a_length = 1)
        end()
    end()

    self.extrudeDashboard.addSeparator()

    # == prefs things, don't work on reload if at end, don't know why

    if begin(QVBox):
        if begin(QHBox):
            insertlabel("show: ")
            # these have keyword args of sense (dflt True), in case you
            # rename them in a way which inverts meaning of True/False,
            # and default, to specify the initial value of the program
            # value (not nec. that of the checkbox, if sense = False!).
            self.extrudePref1 = TogglePrefCheckBox("whole model", parent_now(), "extrudePref1",
                                                   default = False, attr = 'show_whole_model', repaintQ = True )
            self.extrudePref2 = TogglePrefCheckBox("bond-offset spheres", parent_now(), "extrudePref2",
                                                   default = False,  attr = 'show_bond_offsets', repaintQ = True )
                #bruce 050218 don't show bond-offset spheres by default
        end()
        if begin(QHBox):
            insertlabel("when done: ")
            # these only affect what we do at the end -- no repaint needed.
            # History: when there were only two "when done" prefs, the names were "make bonds", "join into one part".
            # Other names tried and rejected (and the reasons):
            # - "bonds" (unclear), "make bonds" (good), "bond parts" (good);
            # - "merge parts" (unclear, but might be ok),
            #   "single part" (sounds like "set ncopies = 1"), "one part" (same), "all one part" (good? maybe unclear);
            #   "join parts" (sounds like "bond");
            # - "ring" (unclear), "make ring" (might be ok), "bend into ring" (too long?).
            self.extrudePref3 = TogglePrefCheckBox("make bonds", parent_now(), "extrudePref3", attr = 'whendone_make_bonds')
            self.extrudePref4 = TogglePrefCheckBox("merge parts", parent_now(), "extrudePref4", attr = 'whendone_all_one_part')
        end()
    end()

#e smaller font? how?
#e tooltips?
        
    self.extrudeDashboard.addSeparator()

    if begin(QVBox):
        global lambda_tol_nbonds
        lbl = insertlabel(lambda_tol_nbonds(1.0,-1)) # text changed later
        self.extrudeBondCriterionLabel = lbl
        self.extrudeBondCriterionLabel_lambda_tol_nbonds = lambda_tol_nbonds
        self.extrudeBondCriterionSlider_dflt = dflt = 100
        # int minValue, int maxValue, int pageStep, int value, orientation, parent, name:
        self.extrudeBondCriterionSlider = QSlider(0,300,5,dflt,Qt.Horizontal,parent_now()) # 100 = the built-in criterion
    end()
    ##lbl = insertlabel("<nnn>") # display of number of bonds, not editable
    ##self.extrudeBondCriterion_ResLabel = lbl

    self.extrudeDashboard.addSeparator()
    
    # == dashboard tools shared with other modes [did not test removing these wrt missing things at end bug, since exc caused]
    self.toolsBackUpAction.addTo(self.extrudeDashboard) #e want this??
    self.toolsStartOverAction.addTo(self.extrudeDashboard)
    self.toolsDoneAction.addTo(self.extrudeDashboard)
    self.toolsCancelAction.addTo(self.extrudeDashboard)

    # note: python name-mangling would turn __tr, within class MainWindow, into _MainWindow__tr (I think... seems to be right)
    self.extrudeDashboard.setLabel(self._MainWindow__tr("extrude or revolve 2"))

    # stuff *after* the dashboard... make it on the right? prefs settings. experimental.
    # QCheckBox::QCheckBox ( const QString & text, QWidget * parent, const char * name = 0 )

    ##print "extrude debug: do_what_MainWindowUI_should_do 3"

    # slider (& all else) failed to appear when it was created here, don't know why
    
    # fyi: caller hides the toolbar, we don't need to

    reinit_extrude_controls(self) # moved to end, will that fix the reload issues??
    
    return

def patch_modename_labels(win, modename):
    "call with Extrude or Revolve" # "Extrude Mode" was wider than I liked... space is tight
    self = win
    self.textLabel_extrude_toolbar.setText(self._MainWindow__tr(modename)) # i think this is the visible one...
    self.extrudeDashboard.setLabel(self._MainWindow__tr(modename)) # not sure whether this ever shows up
    
def lambda_tol_nbonds(tol, nbonds):
    if nbonds == -1:
        nbonds_str = "?"
    else:
        nbonds_str = "%d" % (nbonds,)
    tol_str = ("      %d" % int(tol*100.0))[-3:]
    # fixed-width (3 digits) but using initial spaces
    # (doesn't have all of desired effect, due to non-fixed-width font)
    tol_str = tol_str + "%"
    return "tolerance: %s => %s bonds" % (tol_str,nbonds_str)

def reinit_extrude_controls(win, glpane = None, length = None, attr_target = None):
    "reinitialize the extrude controls; used whenever we enter the mode; win should be the main window (MWSemantics object)"
    self = win

    #e refile these
    self.extrudeSpinBox_n_dflt_per_ptype = [3, 30] # default N depends on product type... not yet sure how to use this info
      ## in fact we can't use it while the bugs in changing N after going to a ring, remain...
    dflt_ncopies = self.extrudeSpinBox_n_dflt_per_ptype[0] #e 0 -> a named constant, it's also used far below
    
    self.extrudeSpinBox_n.setValue(dflt_ncopies)

    
    if self.extrudeSpinBox_circle_n:
        self.extrudeSpinBox_circle_n.setValue(0) #e for true Revolve the initial value would be small but positive...

    x,y,z = 5,5,5 # default dir in modelspace, to be used as a last resort
    if glpane:
        # use it to set direction
        try:
            right = glpane.right
            x,y,z = right # use default direction fixed in eyespace
            if not length:
                length = 7.0 #k needed?
        except:
            print "fyi (bug?): in extrude: x,y,z = glpane.right failed"
            pass
    if length:
        # adjust the length to what the caller desires
        #######, based on the extrude unit (if provided); we'll want to do this more sophisticatedly (??)
        ##length = 7.0 ######
        ll = math.sqrt(x*x + y*y + z*z) # should always be positive, due to above code
        rr = float(length) / ll
        x,y,z = (x * rr, y * rr, z * rr)
    set_extrude_controls_xyz(win, (x,y,z))

    self.extrude_pref_toggles = [self.extrudePref1, self.extrudePref2, self.extrudePref3, self.extrudePref4]
    for toggle in self.extrude_pref_toggles:
        if attr_target and toggle.attr: # do this first, so the attrs needed by the slot functions are there
            setattr(attr_target, toggle.attr, toggle.default) # this is the only place I initialize those attrs!
    for toggle in self.extrude_pref_toggles:
        ##toggle.setChecked(True) ##### stub; change to use its sense & default if it has one -- via a method on it
        toggle.initValue() # this might call the slot function!

    #e bonding-slider, and its label, showing tolerance, and # of bonds we'd make at current offset
    tol = self.extrudeBondCriterionSlider_dflt / 100.0
    set_bond_tolerance_and_number_display( win, tol)
    set_bond_tolerance_slider( win, tol)
    ### bug: at least after the reload menu item, reentering mode did not reinit slider to 100%. don't know why.

    self.extrude_productTypeComboBox.setCurrentItem(0)
    return

def set_bond_tolerance_and_number_display(win, tol, nbonds = -1): #e -1 indicates not yet known ###e '?' would look nicer
    self = win
    lambda_tol_nbonds = self.extrudeBondCriterionLabel_lambda_tol_nbonds
    self.extrudeBondCriterionLabel.setText(lambda_tol_nbonds(tol,nbonds))
    
def set_bond_tolerance_slider(win, tol):
    self = win
    self.extrudeBondCriterionSlider.setValue(int(tol * 100)) # this will send signals!
    
def get_bond_tolerance_slider_val(win):
    self = win
    ival = self.extrudeBondCriterionSlider.value()
    return ival / 100.0
    
def set_extrude_controls_xyz_nolength(win, (x,y,z) ):
    self = win
    self.extrudeSpinBox_x.setFloatValue(x)
    self.extrudeSpinBox_y.setFloatValue(y)
    self.extrudeSpinBox_z.setFloatValue(z)

def set_extrude_controls_xyz(win, (x,y,z) ):
    set_extrude_controls_xyz_nolength( win, (x,y,z) )
    update_length_control_from_xyz(win)

def get_extrude_controls_xyz(win):
    self = win
    x = self.extrudeSpinBox_x.floatValue()
    y = self.extrudeSpinBox_y.floatValue()
    z = self.extrudeSpinBox_z.floatValue()
    return (x,y,z)

suppress_valuechanged = 0

def call_while_suppressing_valuechanged(func):
    global suppress_valuechanged
    old_suppress_valuechanged = suppress_valuechanged
    suppress_valuechanged = 1
    try:
        res = func()
    finally:
        suppress_valuechanged = old_suppress_valuechanged
    return res

def update_length_control_from_xyz(win):
    x,y,z = get_extrude_controls_xyz(win)
    ll = math.sqrt(x*x + y*y + z*z)
    if ll < 0.1: # prevent ZeroDivisionError
        set_controls_minimal(win)
        return
    self = win
    call_while_suppressing_valuechanged( lambda: self.extrudeSpinBox_length.setFloatValue(ll) )
    
def update_xyz_controls_from_length(win):
    x,y,z = get_extrude_controls_xyz(win)
    ll = math.sqrt(x*x + y*y + z*z)
    if ll < 0.1: # prevent ZeroDivisionError
        set_controls_minimal(win)
        return
    self = win
    length = self.extrudeSpinBox_length.floatValue()
    rr = float(length) / ll
    call_while_suppressing_valuechanged( lambda: set_extrude_controls_xyz_nolength( win, (x * rr, y * rr, z * rr) ) )

def set_controls_minimal(win): #e would be better to try harder to preserve xyz ratio
    ll = 0.1 # kluge, but prevents ZeroDivisionError
    x = y = 0.0
    z = ll
    self = win
    call_while_suppressing_valuechanged( lambda: set_extrude_controls_xyz_nolength( win, (x, y, z) ) )
    call_while_suppressing_valuechanged( lambda: self.extrudeSpinBox_length.setFloatValue(ll) )
    ### obs comment?: this is not working as I expected, but it does seem to prevent that
    # ZeroDivisionError after user sets xyz each to 0 by typing in them

# ==

class extrudeMode(basicMode):

    # class constants
    is_revolve = 0
    backgroundColor = 199/255.0, 100/255.0, 100/255.0 # different than in cookieMode
    modename = 'EXTRUDE'
    default_mode_status_text = "Mode: Extrude"
    keeppicked = 0 # whether to keep the units all picked, or all unpicked, during the mode

    # default initial values
    ###

    # no __init__ method needed
    
    # methods related to entering this mode

    def connect_controls(self): ###@@@ josh has some disconnect code in cookieMode, now; should be imitated here
        "connect the dashboard controls to their slots in this method"
        #k i call this from Enter; depositMode calls the equivalent from init_gui -- which is better?
        
        ###e we'll need to disconnect these when we're done, but we don't do that yet
        # (predict this is a speed hit, but probably not a bug)

        
        ## from some other code:
        ## self.connect(self.NumFramesWidget,SIGNAL("valueChanged(int)"),self.NumFramesValueChanged)
        ## but we should destroy conn when we exit the mode... but i guess i can save that for later... since spinbox won't be shown then
        # and since redundant conns will not kill me for now.
        # self.w is a guess for where to put the conn, not sure it matters as long as its a Qt object
        self.w.connect(self.w.extrudeSpinBox_n,SIGNAL("valueChanged(int)"),self.spinbox_value_changed)
        self.w.connect(self.w.extrudeSpinBox_x,SIGNAL("valueChanged(int)"),self.spinbox_value_changed)
        self.w.connect(self.w.extrudeSpinBox_y,SIGNAL("valueChanged(int)"),self.spinbox_value_changed)
        self.w.connect(self.w.extrudeSpinBox_z,SIGNAL("valueChanged(int)"),self.spinbox_value_changed)
        self.w.connect(self.w.extrudeSpinBox_length,SIGNAL("valueChanged(int)"),self.length_value_changed) # needs its own slot

        for toggle in self.w.extrude_pref_toggles:
            self.w.connect(toggle, SIGNAL("stateChanged(int)"), self.toggle_value_changed)

        slider = self.w.extrudeBondCriterionSlider
        self.w.connect(slider, SIGNAL("valueChanged(int)"), self.slider_value_changed)

        if self.w.extrudeSpinBox_circle_n and self.is_revolve: ###k??
            self.w.connect(self.w.extrudeSpinBox_circle_n,SIGNAL("valueChanged(int)"),self.circle_n_value_changed)

        self.w.connect(self.w.extrude_productTypeComboBox,SIGNAL("activated(int)"), self.ptype_value_changed)
        return

    def ptype_value_changed(self, val):
        if not self.now_using_this_mode_object():
            return
        old = self.product_type
        new = self.w.extrude_productTypeComboBox_ptypes[val]
        if new != old:
            print "product_type = %r" % (new,) ####@@@Debug
            self.product_type = new
            ## i will remove those "not neededs" as soon as this is surely past the josh demo snapshot [041017 night]
            self.needs_repaint = 1 #k not needed since update_from_controls would do this too, i hope!
            self.update_from_controls()
            ## not yet effective, even if we did it: self.recompute_bonds()
            self.repaint_if_needed() #k not needed since done at end of update_from_controls
        return
    
    bond_tolerance = -1.0 # this initial value can't agree with value computed from slider
    
    def slider_value_changed(self):
        ######k why don't we check suppress_value_changed? maybe we never set its value with that set?
        if not self.now_using_this_mode_object():
            return
        old = self.bond_tolerance
        new = get_bond_tolerance_slider_val(self.w)
        if new != old:
            self.needs_repaint = 1 # almost certain, from bond-offset spheres and/or bondable singlet colors
            self.bond_tolerance = new
            # one of the hsets has a radius_multiplier which must be patched to self.bond_tolerance
            # (kluge? not compared to what I was doing a few minutes ago...)
            try:
                hset = self.nice_offsets_handleset
            except AttributeError:
                print "must be too early to patch self.nice_offsets_handleset -- could be a problem, it will miss this event" ###@@@
            else:
                hset.radius_multiplier = self.bond_tolerance
            set_bond_tolerance_and_number_display(self.w, self.bond_tolerance) # number of resulting bonds not yet known, will be set later
            self.recompute_bonds() # re-updates set_bond_tolerance_and_number_display when done
            self.repaint_if_needed() ##e merge with self.update_offset_bonds_display, call that instead?? no need for now.
        return
            
    def toggle_value_changed(self):
        if not self.now_using_this_mode_object():
            return
        self.needs_repaint = 0
        for toggle in self.w.extrude_pref_toggles:
            val = toggle.value()
            attr = toggle.attr
            repaintQ = toggle.repaintQ
            if attr:
                old = getattr(self,attr,val)
                if old != val:
                    setattr(self, attr, val)
                    if repaintQ:
                        self.needs_repaint = 1
            else:
                # bad but tolerable: a toggle with no attr, but repaintQ,
                # forces repaint even when some *other* toggle changes!
                # (since we don't bother to figure out whether it changed)
                if repaintQ:
                    self.needs_repaint = 1
                    print "shouldn't happen in current code - needless repaint"
            pass
        self.repaint_if_needed()
        ##print "self.w.extrudePref1.isChecked() = %r" % self.w.extrudePref1.isChecked()

    def refuseEnter(self, warn):
        "if we'd refuse to enter this mode, then (iff warn) tell user why, and (always) return true."
        ok, mol = assy_extrude_unit(self.o.assy, really_make_mol = 0)
        if not ok:
            whynot = mol
            if warn:
                self.warning("%s refused: %r" % (self.msg_modename, whynot,)) ###k format, in self.warning too ###@@@
            return 1
        else:
            # mol is nonsense, btw
            return 0
        pass
        
    def Enter(self):
        self.status_msg("preparing to enter %s..." % self.msg_modename)
          # this msg won't last long enough to be seen, if all goes well
        self.clear() ##e see comment there
        self.initial_down = self.o.down
        self.initial_out = self.o.out
        reinit_extrude_controls(self.w, self.o, length = 7.0, attr_target = self)
        basicMode.Enter(self)

        ###
        # find out what's selected, which if ok will be the repeating unit we will extrude... explore its atoms, bonds, externs...
        # what's selected should be its own molecule if it isn't already...
        # for now let's hope it is exactly one (was checked in refuseEnter, but not anymore).

        ok, mol = assy_extrude_unit(self.o.assy)
        if not ok:
            # after 041222 this should no longer happen, since checked in refuseEnter
            whynot = mol
            self.status_msg("%s refused: %r" % (self.msg_modename, whynot,))
            return 1 # refused!
        self.basemol = mol
        ## partly done new code [bruce 041222] ###@@@
        # temporarily break bonds between our base unit (mol) and the rest
        # of the model; record the pairs of singlets thus formed,
        # both for rebonding when we're done, and to rule out unit-unit bonds
        # incompatible with that rebonding.
        self.broken_externs = [] # pairs of singlets from breaking of externs
        self.broken_extern_s2s = {}
        for bon in list(mol.externs):
            s1, s2 = bon.bust() # these will be rebonded when we're done
            assert s1.is_singlet() and s2.is_singlet()
            # order them so that s2 is in mol, s1 not in it
            if s1.molecule == mol:
                (s1,s2) = (s2,s1)
                assert s1 != s2 # redundant with following, but more informative
            assert s2.molecule == mol
            assert s1.molecule != mol
            self.broken_externs.append((s1,s2))
            self.broken_extern_s2s[s2] = s1 # set of keys; values not used as of 041222
            # note that the atoms we unbonded (the neighbors of s1,s2)
            # might be neighbors of more than one singlet in this list.
        ####@@@ see paper notes - restore at end, also modify singlet-pairing alg

        # The following is necessary to work around a bug in this code, which is
        # its assumption (wrong, in general) that mol.copy().quat == mol.quat.
        # A better fix would be to stop using set_basecenter_and_quat, replacing
        # that with an equivalent use of mol.pivot.
        self.basemol.full_inval_and_update()
        mark_singlets(self.basemol, self.colorfunc) ###@@@ make this behave differently for broken_externs
        # now set up a consistent initial state, even though it will probably
        # be modified as soon as we look at the actual controls
        self.offset = V(15.0,16.0,17.0) # initial value doesn't matter
        self.ncopies = 1
        self.molcopies = [self.basemol]
            #e if we someday want to also display "potential new copies" dimly,
            # they are not in this list
            #e someday we might optimize by not creating separate molcopies,
            # only displaying the same mol in many places
            # (or, having many mols but making them share their display lists --
            #  could mol.copy do that for us??)

        try:
            self.recompute_for_new_unit() # recomputes whatever depends on self.basemol
        except:
            msg = "in Enter, exception in recompute_for_new_unit"
            print_compact_traceback(msg + ": ")
            self.status_msg("%s refused: %s" % (self.msg_modename, msg,))
            return 1 # refused!

        #e is this obs? or just nim?? [041017 night]
        self.recompute_for_new_bend() # ... and whatever depends on the bend from each repunit to the next (varies only in Revolve)

        self.connect_controls()
        ## i think this is safer *after* the first update_from_controls, not before it...
        # but i won't risk changing it right now (since tonight's bugfixes might go into josh's demo). [041017 night]
        
        try:
            self.update_from_controls()
        except:
            msg = "in Enter, exception in update_from_controls"
            print_compact_traceback(msg + ": ")
            self.status_msg("%s refused: %s" % (self.msg_modename, msg,))
            return 1

        # debugging code, safe to leave in indefinitely:
        import __main__
        __main__.mode = self
        if platform.atom_debug:
            print "fyi: extrude/revolve debug instructions: __main__.mode = this extrude mode obj; use debug window; has members assy, etc"
            ##print "also, use Menu1 entries to run debug code, like explore() to check out singlet pairs in self.basemol"

    singlet_color = {} # we also do this in clear()
    def colorfunc(self, atom): # uses a hack in chem.py atom.draw to use mol._colorfunc
        return self.singlet_color.get(atom.info) # ok if this is None

    def asserts(self):
        assert len(self.molcopies) == self.ncopies
        assert self.molcopies[0] == self.basemol

    circle_n = 0 # we also do this in clear()
    def circle_n_value_changed(self, val): # note: will not be used when first committed, but will be used later
        # see also "closed ring"
        ###### 041017 night: i suspect this will go away and the signal will just go to "update_from_controls".
        # at the moment, it is never called since the spinbox for it is never made or connected.
        # even if that changes, this routine looks harmless if update_from_controls is written to grab value
        # from spinbox directly, as long as update_from_controls overwrites self.circle_n again before anything can use it.
        val = "arg not used"
        global suppress_valuechanged
        if suppress_valuechanged:
            return
        if not self.now_using_this_mode_object():
            return
        assert self.is_revolve ###k for now
        spinbox = self.w.extrudeSpinBox_circle_n
        if not spinbox:
            #k should never happen??
            return #k?
        val = spinbox.value()
        old = self.circle_n
        if old != val:
            print "will use circle_n of %d (nim)" % val
            self.circle_n = val
            #e recompute... ###@@@ this is what needs doing... maybe also switch memoized data *right here*... this_bend thisbend
            self.update_from_controls() ###k guess -- this control is not even present as i write this line, tho it might be soon
            self.w.win_update() # or just repaint [this is redundant]
        return

    def spinbox_value_changed(self, val):
        "call this when any extrude spinbox value changed, except length."
        global suppress_valuechanged
        if suppress_valuechanged:
            return
        if not self.now_using_this_mode_object():
            #e we should be even more sure to disconnect the connections causing this to be called
            ##print "fyi: not now_using_this_mode_object" # this happens when you leave and reenter mode... need to break qt connections
            return
        update_length_control_from_xyz(self.w)
        self.update_from_controls()
            # use now-current value, not the one passed
            # (hoping something collapsed multiple signals into one event...)
            #e probably that won't happen unless we do something here to
            # generate an event.... probably doesn't matter anyway,
            #e unless code to adjust to one more or less copy is way to slow.

    def length_value_changed(self, val):
        "call this when the length spinbox changes"
        global suppress_valuechanged
        if suppress_valuechanged:
            return
        if not self.now_using_this_mode_object():
            ##print "fyi: not now_using_this_mode_object"
            return
        update_xyz_controls_from_length(self.w)
        self.update_from_controls()

    should_update_model_tree = 0 # avoid doing this when we don't need to (like during a drag)

    ## use_circle_n_from_ncopies_kluge = 1 # constant, until we add that back #e not in all places in code that it should be
    def want_center_and_quat(self, ii, ptype = None):
        offset = self.offset
        cn = self.circle_n ### does far-below code have bugs when ii >= cn?? that might explain some things i saw...
        basemol = self.basemol
        if not ptype:
            ptype = self.product_type
        #e the following should become the methods of product-type classes
        if ptype == "straight rod": # default for Extrude
            centerii = basemol.center + ii * offset
            # quatii = Q(1,0,0,0)
            quatii = basemol.quat
        elif ptype == "corkscrew": # not yet accessible?? # this code is wrong, anyway
            # stub, to extrude to right and then down -- axis is out of screen -- varies with pov!!!
            # Q(V(x,y,z), theta) = axis vector and angle
            
            quat1 = Q(self.o.out, 2 * pi / cn)
            quatii_rel = Q(self.o.out, 2 * pi * ii / cn)
            print quatii_rel
            # offset in plane of quat is tangent to circle; perp to it is preserved...
            axis = quat1.axis
            trans = dot(offset,axis) * axis
            tangent = offset - trans
            circumf = vlen(tangent) * cn
            radius = circumf / (2 * pi)
            radius_vec = cross(tangent, axis) * cn / (2 * pi)
              #####k I might have this negative... it should point from c_center to basemol.center
            check_floats_near(vlen(radius_vec),radius) ##### BUG -- these are not near!!! ###### ###@@@
            c_center = basemol.center - radius_vec
            centerii = c_center + trans * ii + quatii_rel.rot(radius_vec) ##### probably wrong...
            quatii = basemol.quat + quatii_rel
        elif ptype == "closed ring": # default for Revolve
            #e We store self.o.down (etc) when we enter the mode...
            # now we pick a circle in plane of that and current offset.
            # If this is ambiguous, we favor a circle in plane of initial down and out.
            down = self.initial_down ###implem
            out = self.initial_out
            tangent = norm(offset)
            axis = cross(down,tangent) # example, I think: left = cross(down,out)  ##k
            if vlen(axis) < 0.001: #k guess
                axis = cross(down,out)
                self.status_msg("error: offset too close to straight down, picking down/out circle")
                # worry: offset in this case won't quite be tangent to that circle. We'll have to make it so. ###NIM
            axis = norm(axis) # direction only
            # note: negating this direction makes the circle head up rather than down,
            # but doesn't change whether bonds are correct.
            
            # now all our quats (relative to basemol.quat) are around axis. Note: axis might be backwards, need to test this. ##k
            quat1 = Q(axis, 2 * pi / cn)
            quatii_rel = Q(axis, 2 * pi * ii / cn)
            if "try2 bugfix": ###@@@ why? could just be convention for theta the reverse of my guess
                quat1 = quat1 * -1.0
                quatii_rel = quatii_rel * -1.0 #k would -1 work too?
            quatii = basemol.quat + quatii_rel # (i think) this doesn't depend on where we are around the circle!
            towards_center = cross(offset,axis) # these are perp, axis is unit, so only cn is needed to make this correct length
            neg_radius_vec = towards_center * cn / (2 * pi)
            c_center = basemol.center + neg_radius_vec # circle center
            self.circle_center = c_center # be able to draw the axis
            self.axis_dir = axis
            radius_vec = - neg_radius_vec
            self.radius_vec = radius_vec # be able to draw "spokes", useful in case the axis is off-screen
            centerii = c_center + quatii_rel.rot( radius_vec ) # (as predicted, unrot is quite wrong!)
        else:
            self.status_msg("bug: unimplemented product type %r" % ptype)
            return self.want_center_and_quat(ii, "straight rod")
        if ii == 0:
            ###e we should warn if retvals are not same as basemol values; need a routine to "compare center and quat",
            # like our near test for floats; Numeric can help for center, but we need it for quat too
            check_posns_near( centerii, basemol.center )
            check_quats_near( quatii, basemol.quat )
            pass
        return centerii, quatii

    __old_ptype = None # hopefully not needed in clear(), but i'm not sure, so i added it
    def update_from_controls(self):
        """make the number and position of the copies of basemol what they should be, based on current control values.
        Never modify the control values! (That would infloop.)
        This should be called in Enter and whenever relevant controls might change.
        It's also called during a mousedrag event if the user is dragging one of the repeated units.

        We optimize by checking which controls changed and only recomputing what might depend on those.
        When that's not possible (e.g. when no record of prior value to compare to current value),
        we'd better check an invalid flag for some of what we compute,
        and/or a changed flag for some of the inputs we use.
        """        
        self.asserts()
        
        # get control values
        want_n = self.w.extrudeSpinBox_n.value()

        our_dashboard_has_extrudeSpinBox_circle_n = 0 # for now; later this is a class constant, until we split the dashboards
        if self.w.extrudeSpinBox_circle_n and our_dashboard_has_extrudeSpinBox_circle_n:
            want_cn = self.w.extrudeSpinBox_circle_n.value()
            #k redundant with the slot function for this?? yes, that will go away, see its comments [041017 night].
        else:
            want_cn = 0

        # limit N for safety
        ncopies_wanted = want_n
        ncopies_wanted = min(MAX_NCOPIES,ncopies_wanted) # upper limit (in theory, also enforced by the spinbox)
        ncopies_wanted = max(1,ncopies_wanted) # always at least one copy ###e fix spinbox's value too?? also think about it on exit...
        if ncopies_wanted != want_n:
            msg = "ncopies_wanted is limited to safer value %r, not your requested value %r" % (ncopies_wanted, want_n)
            self.status_msg(msg)

        want_n = ncopies_wanted # redundant -- sorry for this unclear code

        # figure out, and store, effective circle_n now (only matters in ring mode, but always done)
        if not want_cn:
            want_cn = want_n
            # otherwise the cn control overrides the "use N" behavior
        cn_changed = (self.circle_n != want_cn) #### if we again used the sep slot method for that spinbox, this might be wrong
        self.circle_n = want_cn
        
        # note that self.ncopies is not yet adjusted to the want_n value,
        # and (if want_n > self.ncopies) self.ncopies will only be adjusted gradually
        # as we create new copies! So it should not be relied on as giving the final number of copies.
        # But it's ok for that to be private to this code, since what other code needs to know is the
        # number of so-far-made copies (always equals self.ncopies) and the params that affect their
        # location (which never includes self.ncopies, only ptype, self.offset, self.circle_n and someday some more). [041017 night]

          ######@@@ to complete the bugfix:
        # + don't now have someone else store circle_n,
        # + or fail to use it!
        # + [mostly] check all uses of ncopies for not affecting unit pos/rot.
        # and later, rewrite code to keep that stuff in self.want.x and self.have.x,
        # and do all update from this routine (maybe even do that part now).
        # + check product_type or ptype compares.

        (want_x, want_y, want_z) = get_extrude_controls_xyz(self.w)

        offset_wanted = V(want_x, want_y, want_z) # (what are the offset units btw? i guess angstroms, but verify #k)

        # figure out whether product type might have changed -- affects pos/rot of molcopies
        ptype_changed = 0
        if self.__old_ptype != self.product_type:
            ptype_changed = 1
            self.__old_ptype = self.product_type

        # update the state:
        # first move the copies in common (between old and new states),
        # if anything changed which their location (pos/rot) might depend on.

        ncopies_common = min( ncopies_wanted, self.ncopies) # this many units already exist and will still exist
        #e rename to self.ncopies_have? no, just rename both of these to self.want.ncopies and self.have.ncopies.
        
        if offset_wanted != self.offset or cn_changed or ptype_changed: #e add more params if new ptypes use new params
            # invalidate all memoized data which is specific to these params
            self.have_offset_specific_data = 0 #misnamed
            self.offset = offset_wanted
            junk = self.want_center_and_quat(0) # this just asserts that the formulas don't want to move basemol
            for ii in range(1, ncopies_common):
                if 0: # this might accumulate position errors - don't do it:
                    motion = (offset_wanted - self.offset)*ii
                    self.molcopies[ii].move(motion) #k does this change picked state????
                else:
                    c, q = self.want_center_and_quat(ii)
                    self.molcopies[ii].set_basecenter_and_quat( c, q)
        # now delete or make copies as needed (but don't adjust view until the end)
        while self.ncopies > ncopies_wanted:
            # delete a copy we no longer want
            self.should_update_model_tree = 1
            ii = self.ncopies - 1
            self.ncopies = ii
            old = self.molcopies.pop(ii)
            old.unpick() # work around a bug in assy.killmol [041009] ##### that's fixed now -- verify, and remove this
            old.kill() # might be faster than self.o.assy.killmol(old)
            self.asserts()
        while self.ncopies < ncopies_wanted:
            # make a new copy we now want
            self.should_update_model_tree = 1
            #e the fact that it shows up immediately in model tree would permit user to change its color, etc;
            #e but we'll probably want to figure out a decent name for it, make a special group to put these in, etc
            ii = self.ncopies
            self.ncopies = ii + 1
            # pre-050216 code:
            ## newmols = assy_copy(self.o.assy, [self.basemol]) # fyi: offset is redundant with mol.set_basecenter_and_quat (below) 
            ## new = newmols[0]
            # new code 050216:
            new = self.basemol.copy(None) # None is the dad, and as of 050214 or so, passing any other dad is deprecated for now
            self.o.assy.addmol(new) #e addmol is inefficient when adding many mols at once, needs change to inval system
            # end 050216 changes
            if self.keeppicked:
                pass ## done later: self.basemol.pick()
            else:
                ## self.basemol.unpick()
                new.unpick() # undo side effect of assy_copy #k maybe no longer needed [long before 050216]
            self.molcopies.append(new)
            c, q = self.want_center_and_quat(ii)
            self.molcopies[ii].set_basecenter_and_quat( c, q)
            self.asserts()
        if self.keeppicked:
            self.basemol.pick() #041009 undo an unwanted side effect of assy_copy (probably won't matter, eventually)
                 #k maybe no longer needed [long before 050216]
        else:
            self.basemol.unpick() # do this even if no copies made (matters e.g. when entering the mode)
                 #k maybe no longer needed [long before 050216]
        
        ###@@@ now this looks like a general update function... hmm

        self.needs_repaint = 1 # assume this is always true, due to what calls us
        self.update_offset_bonds_display()

    def update_offset_bonds_display(self):
        # should be the last function called by some user event method (??)... not sure if it always is! some weird uses of it...
        "update whatever is needed of the offset_specific_data, the bonds, and the display itself"
        ###### now, if needed, recompute (or start recomputing) the offset-specific data
        #####e worry about whether to do this with every mousedrag event... or less often if it takes too long
        ##### but ideally we do it, so as to show bonding that would happen at current offset
        if not self.have_offset_specific_data:
            self.have_offset_specific_data = 1 # even if the following has an exception
            try:
                self.recompute_offset_specific_data()
            except:
                print_compact_traceback("error in recompute_offset_specific_data: ")
                return # no more updates #### should just raise, once callers cleaner
            pass
        #obs comment in this loc?
        #e now we'd adjust view, or make drawing show if stuff is out of view; make atom overlaps transparent or red; etc...

        # now update bonds (needed by most callers (not ncopies change!), so don't bother to have an invalid flag, for now...)
        if 1:
            self.recompute_bonds() # sets self.needs_repaint if bonds change; actually updates bond-specific ui displays
        
        # update model tree and/or glpane, as needed
        if self.should_update_model_tree:
            self.should_update_model_tree = 0 # reset first, so crashing calls are not redone
            self.needs_repaint = 0
            self.w.win_update() # update glpane and model tree
        elif self.needs_repaint: # merge with self.repaint_if_needed() ###@@@
            self.needs_repaint = 0
            self.o.gl_update() # just update glpane
        return

    # ==

    # These methods recompute things that depend on other things named in the methodname.
    # call them in the right order (this order) and at the right time.
    # If for some of them, we should only invalidate and not recompute until later (eg on buttonpress),
    # I did not yet decide how that will work.

    def recompute_for_new_unit(self):
        "recompute things which depend on the choice of rep unit (for now we use self.basemol to hold that)"
        # for now we use self.basemol,
        #e but later we might not split it from a larger mol, but have a separate mol for it

        # these are redundant, do we need them?
        self.have_offset_specific_data = 0
        self.bonds_for_current_offset_and_tol = (17,)
        
        self.show_bond_offsets_handlesets = [] # for now, assume no other function wants to keep things in this list
        hset = self.basemol_atoms_handleset = repunitHandleSet(target = self)
        for atom in self.basemol.atoms.values():
            # make a handle for it... to use in every copy we show
            pos = atom.posn() ###e make this relative?
            dispdef = self.basemol.get_dispdef(self.o)
            disp, radius = atom.howdraw(dispdef)
            info = None #####
            hset.addHandle(pos, radius, info)
        self.basemol_singlets = list(self.basemol.singlets) #bruce 041222 precaution: copy list
        hset = self.nice_offsets_handleset = niceoffsetsHandleSet(target = self)
        hset.radius_multiplier = abs(self.bond_tolerance) # kluge -- might be -1 or 1 initially! (sorry, i'm in a hurry)
          # note: hset is used to test offsets via self.nice_offsets_handleset,
          # but is drawn and click-tested due to being in self.show_bond_offsets_handlesets
        # make a handle just for dragging self.nice_offsets_handleset
        hset2 = self.nice_offsets_handle = draggableHandle_HandleSet( \
                    motion_callback = self.nice_offsets_handleset.move ,
                    statusmsg = "use purple center to drag the clickable suggested-offset display"
                )
        hset2.addHandle( V(0,0,0), 0.66, None)
        hset2.addHandle( self.offset, 0.17, None) # kluge: will be kept patched with current offset
        hset.special_pos = self.offset # ditto
        self.show_bond_offsets_handlesets.extend([hset,hset2])
           # (use of this list is conditioned on self.show_bond_offsets)
        ##e quadratic, slow alg; should worry about too many singlets
        # (rewritten from the obs functions explore, bondable_singlet_pairs_proto1)
        # note: this code will later be split out, and should not assume mol1 == mol2.
        # (but it does, see comments)
        mergeables = self.mergeables = {}
        sings1 = sings2 = self.basemol_singlets
        transient_id = (self, self.__class__.recompute_for_new_unit, "scanning all pairs")
        for i1 in range(len(sings1)):
            qApp.processEvents() # [bruce 050114, copied from movie.py]
                # Process queued events [enough to get statusbar msgs to show up]
                ###@@@ #e for safety we might want to pass the argument: QEventLoop::ExcludeUserInput;
                #e OTOH we'd rather have some way to let the user abort this if it takes too long!
                # (we don't yet have any known or safe way to abort it...)
            if i1 % 10 == 0 or i1 < 10:
                #bruce 050118 try only every 10th one, is it faster?
                #e should processEvents be in here too??
                ###e would be more sensible: compare real time passed...
                self.w.history.message("scanning open bond pairs... %d/%d done" % (i1, len(sings1)) ,
                             transient_id = transient_id
                            ) # this is our slowness warning
            ##e should correct that message for effect of i2 < i1 optim, by reporting better numbers...
            for i2 in range(len(sings2)):
                if i2 < i1:
                    continue # results are negative of swapped i1,i2, SINCE MOLS ARE THE SAME
                    # this order makes the slowness warning conservative... ie progress seems to speed up at the end
                    ### warning: this optim is only correct when mol1 == mol2
                    # and (i think) when there is no "bend" relating them.
                # (but for i1 == i2 we do the calc -- no guarantee mol1 is identical to mol2.)
                s1 = sings1[i1]
                s2 = sings2[i2]
                (ok, ideal, err) = mergeable_singlets_Q_and_offset(s1, s2)
                if extrude_loop_debug:
                    print "extrude loop %d, %d got %r" % (i1, i2, (ok, ideal, err))
                if ok:
                    mergeables[(i1,i2)] = (ideal, err)
        #e self.mergeables is in an obs format... but we still use it to look up (i1,i2) or their swapped form

        # final msg with same transient_id
        msg = "scanned %d open-bond pairs..." % ( len(sings1) * len(sings2) ,) # longer msg below
        self.w.history.message( msg, transient_id = transient_id, repaint = 1 )
        self.w.history.message("") # make it get into history right away
        del transient_id

        # make handles from mergeables.
        # Note added 041222: the handle (i1,i2) corresponds to the possibility
        # of bonding singlet number i1 in unit[k] to singlet number i2 in unit[k+1].
        # As of 041222 we have self.broken_externs, list of (s1,s2) where s1 is
        # something outside, and s2 is in the baseunit. We assume (without real
        # justification) that all this outside stuff should remain fixed and bound
        # to the baseunit; to avoid choosing unit-unit bonds which would prevent
        # that, we exclude (i1,i2) when singlet[i1] = s2 for some s2 in
        # self.broken_externs -- if we didn't, singlet[i1] in base unit would
        # need to bond to unit2 *and* to the outside stuff.
        excluded = 0
        for (i1,i2),(ideal,err) in mergeables.items():
            pos = ideal
            radius = err
            radius *= (1.1/0.77) * 1.0 # see a removed "bruce 041101" comment for why
            info = (i1,i2)
            if self.basemol_singlets[i1] not in self.broken_extern_s2s:
                hset.addHandle(pos, radius, info)
            else:
                excluded += 1
            if i2 != i1:
                # correct for optimization above
                pos = -pos
                info = (i2,i1)
                if self.basemol_singlets[i2] not in self.broken_extern_s2s:
                    hset.addHandle(pos, radius, info)
                else:
                    excluded += 1
            else:
                print "fyi: singlet %d is mergeable with itself (should never happen for extrude; ok for revolve)" % i1
            # handle has dual purposes: click to change the offset to the ideal,
            # or find (i1,i2) from an offset inside the (pos, radius) ball.
        msg = "scanned %d open-bond pairs; %d pairs could bond at some offset (as shown by bond-offset spheres)" % \
              ( len(sings1) * len(sings2) , len(hset.handles) )
        self.status_msg(msg)
        if excluded:
            print "fyi: %d pairs excluded due to external bonds to extruded unit" % excluded ###@@@
        return
    
    def recompute_for_new_bend(self):
        "recompute things which depend on the choice of bend between units (for revolve)"
        ##print "recompute_for_new_bend(): pass" ######
        pass

    have_offset_specific_data = 0 # we do this in clear() too

    def recompute_offset_specific_data(self):
        "recompute whatever depends on offset but not on tol or bonds -- nothing at the moment"
        pass
    
    def redo_look_of_bond_offset_spheres(self):
        # call to us moved from recompute_offset_specific_data to recompute_bonds
        "#doc; depends on offset and tol and len(bonds)"
        # kluge:
        try:
            # teensy purple ball usually shows position of offset rel to the white balls (it's also draggable btw)
            if len( self.bonds_for_current_offset_and_tol ) >= 1: ### worked with > 1, will it work with >= 1? ######@@@
                teensy_ball_pos = V(0,0,0) # ... but make it not visible if there are any bonds [#e or change color??]
                #e minor bug: it sometimes stays invisible even when there is only one bond again...
                # because we are not rerunning this when tol changes, but it depends on tol. Fix later. #######
            else:
                teensy_ball_pos = self.offset #k i think this is better than using self.offset_for_bonds
            hset2 = self.nice_offsets_handle
            hset2.handle_setpos( 1, teensy_ball_pos ) # positions the teensy purple ball
            hset = self.nice_offsets_handleset
            hset.special_pos = self.offset_for_bonds # tells the white balls who contain this offset to be slightly blue
        except:
            print "fyi: hset2/hset kluge failed"
        # don't call recompute_bonds, our callers do that if nec.
        return 

    bonds_for_current_offset_and_tol = (17,) # we do this in clear() too
    offset_for_bonds = None
    def recompute_bonds(self):
        "call this whenever offset or tol changes"

        ##k 041017 night: temporary workaround for the bonds being wrong for anything but a straight rod:
        # in other products, use the last offset we used to compute them for a rod, not the current offset.
        # even better might be to "or" the sets of bonds created for each offset tried... but we won't get
        # that fancy for now.
        if self.product_type == "straight rod":
            self.offset_for_bonds = self.offset
        else:
            if not self.offset_for_bonds:
                msg = "error: bond-offsets not yet computed, but computing them for %r is not yet implemented" % self.product_type
                self.w.history.message(msg, norepeat_id = msg)
                return
            else:
                msg = """warning: for %r, correct bond-offset computation is not yet implemented;\n""" \
                      """using bond-offsets computed for "rod", at last offset of the rod, not current offset""" % \
                      self.product_type
                self.w.history.message(msg, norepeat_id = msg)
            #e we could optim by returning if only offset but not tol changed, but we don't bother yet
        
        self.redo_look_of_bond_offset_spheres() # uses both self.offset and self.offset_for_bonds
        
        # recompute what singlets to show in diff color, what bonds to make...
        
        # basic idea: see which nice-offset-handles contain the offset, count them, and recolor singlets they come from.
        hset = self.nice_offsets_handleset #e revise this code if we cluster these, esp. if we change their radius
        hh = hset.findHandles_containing(self.offset_for_bonds)
            # semi-kluge: this takes into account self.bond_tolerance, since it was patched into hset.radius_multiplier
        # kluge for comparing it with prior value; depends on order stability of handleset, etc
        hh = tuple(hh)
        if hh != self.bonds_for_current_offset_and_tol:
            self.needs_repaint = 1 # usually true at this point
            ##msg = "new set of %d nice bonds: %r" % (len(hh), hh)
            ##print msg ## self.status_msg(msg) -- don't obscure the scan msg yet #######
            self.bonds_for_current_offset_and_tol = hh
            # change singlet color dict(??) for i1,i2 in ..., proc(i1, col1), proc(i2,col2)...
            self.singlet_color = {}
            for mol in self.molcopies:
                mol.changeapp(0)
                ##e if color should vary with bond closeness, we'd need changeapp for every offset change;
                # then for speed, we'd want to repeatedly draw one mol, not copies like now
                # (maybe we'd like to do that anyway).
            for (pos,radius,info) in hh:
                i1,i2 = info
                ####stub; we need to worry about repeated instances of the same one (as same of i1,i2 or not)
                def doit(ii, color):
                    basemol_singlet = self.basemol_singlets[ii]
                    mark = basemol_singlet.info
                    self.singlet_color[mark] = color # when we draw atoms, somehow they find self.singlet_color and use it...
                doit(i1, blue)
                doit(i2, green)
                ###e now how do we make that effect the look of the base and rep units? patch atom.draw?
                # but as we draw the atom, do we look up its key? is that the same in the mol.copy??
        nbonds = len(hh)
        set_bond_tolerance_and_number_display(self.w, self.bond_tolerance, nbonds)
        ###e ideally we'd color the word "bonds" funny, or so, to indicate that offset_for_bonds != offset or that ptype isn't rod...
        #e repaint, or let caller do that (perhaps aftermore changes)? latter - only repaint at end of highest event funcs.
        return

    def draw_bond_lines(self, unit1, unit2): #bruce 050203 experiment ####@@@@ PROBABLY NEEDS OPTIMIZATION
        "draw white lines showing the bonds we presently propose to make between the given adjacent units"
        # works now, but probably needs optim or memo of find_singlets before commit --
        # just store a mark->singlet table in the molcopies -- once when each one is made should be enough i think.
        hh = self.bonds_for_current_offset_and_tol
        self.prep_to_make_inter_unit_bonds() # needed for find_singlet; could be done just once each time bonds change, i think
        for (pos,radius,info) in hh:
            i1,i2 = info
            ## not so simple as this: p1 = unit1.singlets[i1].posn()
            p1 = self.find_singlet(unit1,i1).posn() # this is slow! need to optimize this (or make it optional)
            p2 = self.find_singlet(unit2,i2).posn()
            drawline(white, p1, p2)
        return
    
    # == this belongs higher up...
    
    def init_gui(self):
        ##print "hi my msg_modename is",self.msg_modename
        self.o.setCursor(QCursor(Qt.ArrowCursor)) #bruce 041011 copying a change from cookieMode, choice of cursor not reviewed ###
        
        # Disable some "File" action items while in Extrude mode - Mark 050114
        self.w.fileSaveAction.setEnabled(0) # Disable "File Save"
        self.w.fileSaveAsAction.setEnabled(0) # Disable "File Save As"
        self.w.fileOpenAction.setEnabled(0) # Disable "File Open"
        self.w.fileCloseAction.setEnabled(0) # Disable "File Close"
        self.w.fileInsertAction.setEnabled(0) # Disable "File Insert"
            # (bruce 050218 comment: would the following tools be ok to allow?
            #  No, because when they leave the mode and then reenter it, they make it
            #  lose all its state. If we had suspend/resume for modes, they'd be fine. ###e)
        self.w.zoomToolAction.setEnabled(0) # Disable "Zoom Tool"
        self.w.panToolAction.setEnabled(0) # Disable "Pan Tool"
        self.w.rotateToolAction.setEnabled(0) # Disable "Rotate Tool"
        
        if self.is_revolve:
            self.w.toolsRevolveAction.setOn(1)
            self.w.revolveDashboard.show()
            patch_modename_labels(self.w, "Revolve")
        else:
            self.w.toolsExtrudeAction.setOn(1) # make the Extrude tool icon look pressed (and the others not)
            self.w.extrudeDashboard.show()
            patch_modename_labels(self.w, "Extrude")
        return

    # methods related to exiting this mode [bruce 040922 made these from old Done and Flush methods]

    def haveNontrivialState(self):
        return self.ncopies != 1 # more or less...

    def StateDone(self):
        ## self.update_from_controls() #k 041017 night - will this help or hurt? since hard to know, not adding it now.
        # restore normal appearance
        for mol in self.molcopies:
            try:
                del mol._colorfunc
                mol.changeapp(0)
            except:
                pass
        self.finalize_product() # ... and emit status message about it
        return None

    def finalize_product(self):
        "if requested, make bonds and/or join units into one part"
        
        desc = " (N = %d)" % self.ncopies  #e later, also include circle_n if different and matters; and more for other product_types
        
        ##self.final_msg_accum = "extrude done: "
        self.final_msg_accum = "%s making %s%s: " % (self.msg_modename.split()[0], self.product_type, desc) # first word of modename
        
        msg0 = "leaving mode, finalizing product..." # if this lasts long enough to read, something went wrong
        self.status_msg(self.final_msg_accum + msg0)

        print "fyi: extrude params not mentioned in statusbar: offset = %r, tol = %r" % (self.offset, self.bond_tolerance)

        if self.whendone_make_bonds:
            # NIM - rebond base unit with its home molecule, if any [###@@@ see below]
            #  (but not if product is a closed ring, right? not sure, actually, deps on which singlets are involved)
            #e even the nim-warning msg is nim...
            #e (once we do this, maybe do it even when not self.whendone_make_bonds??)

            # unit-unit bonds:
            bonds = self.bonds_for_current_offset_and_tol
            if not bonds:
                bonds_msg = "no bonds to make"
            else:
                bonds_msg = "making %d bonds per unit..." % len(bonds)
            self.status_msg(self.final_msg_accum + bonds_msg)
            if bonds:
                self.prep_to_make_inter_unit_bonds()
                for ii in range(1, self.ncopies): # 1 thru n-1 (might be empty range, that's ok)
                    # bond unit ii with unit ii-1
                    self.make_inter_unit_bonds( self.molcopies[ii-1], self.molcopies[ii], bonds ) # uses self.basemol_singlets, etc
                if self.product_type == "closed ring":
                    # close the ring ###@@@ what about broken_externs? Need to modify bonding for ring, for this reason... ###@@@
                    self.make_inter_unit_bonds( self.molcopies[self.ncopies-1], self.molcopies[0], bonds )
                bonds_msg = "made %d bonds per unit" % len(bonds)
                self.status_msg(self.final_msg_accum + bonds_msg)
            self.final_msg_accum += bonds_msg
            # merge base back into its fragmented ancestral molecule...
            # but not until the end, for fear of messing up unit-unit bonding
            # (could be dealt with, but easier to skirt the issue).
            if not self.product_type == "closed ring":
                # 041222 finally implementing this...
                ###@@@ closed ring case has to be handled differently earlier...
                for s1,s2 in self.broken_externs:
                    bond_at_singlets(s1, s2, move = 0)
        
        if self.whendone_all_one_part:
            # rejoin base unit with its home molecule, if any -- NIM [even after 041222]
            #e even the nim-warning msg is nim...
            #e (once we do this, maybe do it even when not self.whendone_all_one_part??)

            # join all units into basemol
            self.final_msg_accum += "; "
            join_msg = "joining..." # this won't be shown for long, if no error
            self.status_msg(self.final_msg_accum + join_msg)
            product = self.basemol #e should use home mol, but that's nim
            for unit in self.molcopies[1:]: # all except basemol
                product.merge(unit) # also does unit.kill()
            self.product = product #e needed?
            if self.ncopies > 1:
                join_msg = "joined into one part"
            else:
                join_msg = "(one unit, nothing to join)"
            #e should we change ncopies and molcopies before another redraw could occur?
            self.final_msg_accum += join_msg
            self.status_msg(self.final_msg_accum)
        else:
            if self.ncopies > 1:
                self.final_msg_accum += " (left units as separate parts)"
            else:
                pass # what is there to say?
            self.status_msg(self.final_msg_accum)
        return

    def prep_to_make_inter_unit_bonds(self):
        self.i1_to_mark = {}
        #e keys are a range of ints, could have used an array -- but entire alg needs revision anyway
        for i1, s1 in zip(range(len(self.basemol_singlets)), self.basemol_singlets):
            self.i1_to_mark[i1] = s1.info # used by self.find_singlet
            #e find_singlet could just look directly in self.basemol_singlets *right now*,
            # but not after we start removing the singlets from basemol!
        return

    def make_inter_unit_bonds(self, unit1, unit2, bonds = ()):
        # you must first call prep_to_make_inter_unit_bonds, once
        #e this is quadratic in number of singlets, sorry; not hard to fix
        ##print "bonds are %r",bonds
        for (offset,permitted_error,(i1,i2)) in bonds:
            # ignore offset,permitted_error; i1,i2 are singlet indices
            # assume no singlet appears twice in this list!
            # [not yet justified, 041015 1207p]
            s1 = self.find_singlet(unit1,i1)
            s2 = self.find_singlet(unit2,i2)
            if s1 and s2:
                # replace two singlets (perhaps in different mols) by a bond between their atoms
                bond_at_singlets(s1, s2, move = 0)
            else:
                #e will be printed lots of times, oh well
                print "extrude warning: one or both of singlets %d,%d slated to bond in more than one way, not all bonds made" % (i1,i2)
        return

    def find_singlet(self, unit, i1):
        """Find the singlet #i1 in unit, and return it,
        or None if it's not there anymore
        (should someday never happen, but can for now)
        (arg called i1 could actually be i1 or i2 in bonds list)
        (all this singlet-numbering is specific to our current basemol)
        (only works if you first once called prep_to_make_inter_unit_bonds)
        """
        mark = self.i1_to_mark[i1] # mark is basemol key, but unrelated to other mols' keys
        for atm in unit.atoms.itervalues():
            try:
                if atm.info == mark:
                    return atm
            except:
                pass # not sure if singlets have .info
        print "extrude bug (trying to ignore it): singlet not found",unit,i1
        # can happen until we remove dup i1,i2 from bonds
        return None
        
    def StateCancel(self):
        self.w.extrudeSpinBox_n.setValue(1)
        self.update_from_controls()
        return self.StateDone() # closest we can come to cancelling
    
    def restore_gui(self):
        if self.is_revolve:
            self.w.revolveDashboard.hide()
        else:
            self.w.extrudeDashboard.hide()
        
        # Re-enable "File" action items - Mark 050114
        self.w.fileSaveAction.setEnabled(1) # Enable "File Save"
        self.w.fileSaveAsAction.setEnabled(1) # Enable "File Save"
        self.w.fileOpenAction.setEnabled(1) # Enable "File Open"
        self.w.fileCloseAction.setEnabled(1) # Enable "File Close"
        self.w.fileInsertAction.setEnabled(1) # Enable "File Insert"
        self.w.zoomToolAction.setEnabled(1) # Enable "Zoom Tool"
        self.w.panToolAction.setEnabled(1) # Enable "Pan Tool"
        self.w.rotateToolAction.setEnabled(1) # Enable "Rotate Tool"
        
        return

    # mouse events

    def leftDown(self, event):
        """Move the touched repunit object, or handle (if any), in the plane of
        the screen following the mouse, or in some other way appropriate to
        the object.
        """
        ####e Also highlight the object? (maybe even do that on mouseover ####) use bareMotion
        self.o.SaveMouse(event) # saves in self.o.MousePos, used in leftDrag
        thing = self.dragging_this = self.touchedThing(event)
        if thing:
            self.dragged_offset = self.offset
            # fyi: leftDrag directly changes only self.dragged_offset;
            # then recompute from controls (sp?) compares that to self.offset, changes that
            msg = thing.leftDown_status_msg()
            if not msg:
                msg = "touched %s" % (thing,)
            self.status_msg(msg)
            self.needs_repaint = 1 # for now, guess that this is always true (tho it's only usually true)
            thing.click() # click handle in appropriate way for its type (#e in future do only on some mouseups)
            self.repaint_if_needed() # (sometimes the click method already did the repaint, so this doesn't)
        return

    def status_msg(self, text): # bruce 050106 simplified this
        self.w.history.message(text)

    show_bond_offsets_handlesets = [] # (default value) the handlesets to be visible iff self.show_bond_offsets
    
    def touchedThing(self, event):
        "return None or the thing touched by this event"
        touchable_molecules = True
        if self.product_type != "straight rod":
            touchable_molecules = False
            # old comment:
            #  This function won't work properly in this case.
            # Be conservative until that bug is fixed. It's not even safe to permit
            # a click on a handle (which this code is correct in finding),
            # since it might be obscured on the screen
            # by some atom the user is intending to click on.
            #  The only safe thing to find in this case would be something purely draggable
            # with no hard-to-reverse effects, e.g. the "draggable purple handle",
            # or the base unit (useful only once we permit dragging the model using it).
            #  I might come back and make those exceptions here,
            # if I don't fix the overall bug soon enough. [bruce 041017]
            #
            # newer comment:
            #  Only disable dragging repunits, don't disable dragging or clicking bond-offset spheres
            # (even though they might be clicked by accident when visually behind a repunit of the ring).
            # [bruce 041019]
##            self.status_msg("(click or drag not yet implemented for product type %r; sorry)" % self.product_type)
##            return None
        p1, p2 = self.o.mousepoints(event) # (no side effect. p1 is just at near clipping plane; p2 in center of view plane)
        ##print "touchedthing for p1 = %r, p2 = %r" % (p1,p2)
        res = [] # (dist, handle) pairs, arb. order, but only the frontmost one from each handleset
        if self.show_bond_offsets:
            for hset in self.show_bond_offsets_handlesets:
                dh = hset.frontDistHandle(p1, p2) # dh = (dist, handle)  #######@@@ needs to use bond_tolerance, or get patched
                if dh:
                    res.append(dh)
        #e scan other handlesets here, if we have any
        if touchable_molecules:
            #e now try molecules (if we have not coded them as their own handlesets too) -- only the base and rep units for now
            hset = self.basemol_atoms_handleset
            for ii in range(self.ncopies):
                ##print "try touch",ii
                offset = self.offset * ii
                dh = hset.frontDistHandle(p1, p2, offset = offset, copy_id = ii)
                if dh:
                    res.append(dh) #e dh's handle contains copy_id, a code for which repunit
        if res:
            res.sort()
            dh = res[0]
            handle = dh[1]
            ##print "touched %r" % (handle,)
            return handle
        # nothing touched... need to warn?
        if not touchable_molecules:
            self.status_msg("(dragging of repeat units not yet implemented for product type %r; sorry)" % self.product_type)
        return None

    def leftDrag(self, event):
        """Move the touched objects as determined by leftDown(). ###doc
        """
        if self.dragging_this:
            self.doDrag(event, self.dragging_this)

    needs_repaint = 0
    def doDrag(self, event, thing):
        """drag thing, to new position in event.
        thing might be a handle (pos,radius,info) or something else... #doc
        """
        # determine motion to apply to thing being dragged. Current code is taken from modifyMode.
        # bruce question -- isn't this only right in central plane?
        # if so, we could fix it by using mousepoints() again.
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        move = self.o.quat.unrot(self.o.scale * deltaMouse/(h*0.5))
        
        self.o.SaveMouse(event) # sets MousePos, for next time

        self.needs_repaint = 1 # for now, guess that this is always true (tho it's only usually true)
        thing.move(move) # move handle in the appropriate way for its type
          #e this needs to set self.needs_repaint = 1 if it changes any visible thing!
          ##### how does it know?? ... so for now we always set it *before* calling;
          # that way a repaint during the call can reset the flag.
        ## was: self.o.assy.movesel(move)
        self.repaint_if_needed()
    
    def repaint_if_needed(self): # see also the end of update_offset_bonds_display -- we're inlined ######fix
        if self.needs_repaint:
            self.needs_repaint = 0
            self.o.gl_update()
        return
    
    def drag_repunit(self, copy_id, motion):
        "drag a repeat unit (copy_id > 0) or the base unit (id 0)"
        assert type(copy_id) == type(1) and copy_id >= 0
        if copy_id:
            # move repunit #copy_id by motion
            # compute desired motion for the offset which would give this motion to the repunit
            # bug note -- the code that supplies motion to us is wrong, for planes far from central plane -- fix later.
            motion = motion * (1.0 / copy_id)
            # store it, but not in self.offset, that's reserved for comparison with the last value from the controls
            self.dragged_offset = self.dragged_offset + motion
            #obs comment?? i forget what it meant: #e recompute_for_new_offset
            self.force_offset_and_update( self.dragged_offset)
        else:
            pass##print "dragging base unit moves entire model (not yet implemented)"
        return

    def force_offset_and_update(self, offset):
        "change the controls to reflect offset, then update from the controls"
        x,y,z = offset
        call_while_suppressing_valuechanged( lambda: set_extrude_controls_xyz( self.w, (x, y, z) ) )
        #e worry about too-low resolution of those spinbox numbers? at least not in self.dragged_offset...
        #e status bar msg? no, caller can do it if they want to.
        self.update_from_controls() # this does a repaint at the end (at least if the offset in the controls changed)
        
    def click_nice_offset_handle(self, handle):
        (pos,radius,info) = handle
        i1,i2 = info
        try:
            ideal, err = self.mergeables[(i1,i2)]
        except KeyError:
            ideal, err = self.mergeables[(i2,i1)]
            ideal = -1 * ideal
        self.force_offset_and_update( ideal)
    
    def leftUp(self, event):
        if self.dragging_this:
            ## self.doDrag(event, self.dragging_this) ## good idea? not sure. probably not.
            self.dragging_this = None
            #####e update, now that we know the final position of the dragged thing
            del self.dragged_offset
        return
    
    #==
    
    def leftShiftDown(self, event):
        pass##self.StartDraw(event, 0)

    def leftCntlDown(self, event):
        pass##self.StartDraw(event, 2)

    def leftShiftDrag(self, event):
        pass##self.ContinDraw(event)
    
    def leftCntlDrag(self, event):
        pass##self.ContinDraw(event)
    
    def leftShiftUp(self, event):
        pass##self.EndDraw(event)
    
    def leftCntlUp(self, event):
        pass##self.EndDraw(event)

    mergeables = {} # in case not yet initialized when we Draw (maybe not needed)
    moused_over = None

    def clear(self): ###e should modes.py also call this before calling Enter? until it does, call it in Enter ourselves
        self.mergeables = {}
        self.moused_over = None #k?
        self.dragdist = 0.0
        self.have_offset_specific_data = 0 #### also clear that data itself...
        self.bonds_for_current_offset_and_tol = (17,) # impossible value -- ok??
        self.offset_for_bonds = None
        if self.is_revolve:
            self.product_type = "closed ring"
            self.circle_n = 30 ###e should take this from the array [3,30] in some init function
            #e should vary default offset too
        else:
            self.product_type = "straight rod" #e someday have a combobox for this
            self.circle_n = 0
        self.__old_ptype = None
        self.singlet_color = {}
        #e lots more ivars too
        return

    def print_overrides(self):
        "[debugging method] print the class attributes overridden in this instance"
        #e generalize and split that into debug module and use for win, mtree, glpane, history
        # experiment: need to not do this for instance methods; will the im_func attr (same_method, modes.py) help?? #####
        instance1 = self
        class1 = self.__class__ # in general this might be a specific superclass instead
        # for extrude, the only ones this prints that are not in clear() are:
        # msg_modename, show_bond_offsets_handlesets
        # this part gets moved to a new func in debug...
        print "extrudeMode print_overrides..."
        import debug
        res = debug.overridden_attrs(class1, instance1) # a list of 0 or more attrnames
        print "  %r" % res
        return

    def print_overrides_win(self): #bruce 050109
        # this debug method belongs in MWsemantics.py but that doesn't really matter,
        # and the menu item for it could be anywhere, so for now i'll just put it here.
        print "overrides in main window... (this will include tons of slot methods, sorry)"
        # could exclude them by reporting overrides of Qt superclass of that which are not overridden in that ###doit 
        import debug
        from MainWindowUI import MainWindow
        print "  %r" % debug.overridden_attrs(MainWindow, self.w)

    def print_overrides_mt(self): #bruce 050109
        # this debug method probably belongs in modelTree.py or maybe MWsemantics.py,
        # but that doesn't really matter,
        # and the menu item for it could be anywhere, so for now i'll just put it here.
        print "overrides in model tree widget... [prints a lot, don't yet know why]"
        import debug
        from qt import QListView
        print "  %r" % debug.overridden_attrs(QListView, self.w.mt)

    def print_overrides_glpane(self): #bruce 050109
        # this debug method probably belongs in GLPane.py or maybe MWsemantics.py,
        # but that doesn't really matter,
        # and the menu item for it could be anywhere, so for now i'll just put it here.
        print "overrides in glpane widget... [prints a lot, don't yet know why]"
        import debug
        from qtgl import QGLWidget
        print "  %r" % debug.overridden_attrs(QGLWidget, self.o)
    
    def Draw(self):
        basicMode.Draw(self) # draw axes, if displayed
        if self.show_whole_model:
            self.o.assy.draw(self.o)
        else:
            for mol in self.molcopies:
                #e use per-repunit drawing styles...
                dispdef = mol.get_dispdef( self.o) # not needed, since...
                mol.draw(self.o, dispdef) # ...dispdef arg not used (041013)
        try: #bruce 050203 experiment
            for unit1,unit2 in zip(self.molcopies[:-1],self.molcopies[1:]):
                self.draw_bond_lines(unit1,unit2)
        except:
            print_compact_traceback("i tried: ") #####@@@@@
        if self.show_bond_offsets:
            for hset in self.show_bond_offsets_handlesets:
                try:
                    hset.draw(self.o)
                except:
                    print_compact_traceback("exc in some hset.draw(): ")
        return
   
    def makeMenus(self): ### mostly not yet reviewed for extrude or revolve mode
        
        self.Menu_spec = [
            ('Cancel', self.Cancel),
            ('Start Over', self.StartOver),
            ('Done', self.Done), #bruce 041217
         ]
        
        self.debug_Menu_spec = [
            ('debug: reload module', self.extrude_reload),
            ###e make these a submenu:
            ('debug: print overrides', self.print_overrides),
            ('debug: print overrides win', self.print_overrides_win),
            ('debug: print overrides mt', self.print_overrides_mt),
            ('debug: print overrides glpane', self.print_overrides_glpane),
         ]
        
        self.Menu_spec_control = [
            ('Invisible', self.w.dispInvis),
            None,
            ('Default', self.w.dispDefault),
            ('Lines', self.w.dispLines),
            ('CPK', self.w.dispCPK),
            ('Tubes', self.w.dispTubes),
            ('VdW', self.w.dispVdW),
            None,
            ('Color', self.w.dispObjectColor) ]
        
        return

    def extrude_reload(self):
        """for debugging: try to reload extrudeMode.py and patch your glpane
        to use it, so no need to restart Atom. Might not always work.
        [But it did work at least once!]
        """
        global extrudeMode, revolveMode
        print "extrude_reload: here goes...."
        try:
            self.w.extrudeSpinBox_n.setValue(1)
            self.update_from_controls()
            print "reset ncopies to 1, to avoid dialog from Abandon, and ease next use of the mode"
        except:
            print_compact_traceback("exc in resetting ncopies to 1 and updating, ignored: ")
        try:
            self.restore_gui()
        except:
            print_compact_traceback("exc in self.restore_gui(), ignored: ")
        for clas in [extrudeMode, revolveMode]:
            try:
                self.o.other_mode_classes.remove(clas) # was: self.__class__
            except ValueError:
                print "a mode class was not in modetab (normal if last reload of it had syntax error)"
        import handles
        reload(handles)
        import extrudeMode as _exm
        reload(_exm)
        from extrudeMode import extrudeMode, revolveMode, do_what_MainWindowUI_should_do
        try:
            do_what_MainWindowUI_should_do(self.w) # remake interface (dashboard), in case it's different [041014]
        except:
            print_compact_traceback("exc in new do_what_MainWindowUI_should_do(), ignored: ")
        ## self.o.modetab['EXTRUDE'] = extrudeMode
        self.o.other_mode_classes.append(extrudeMode)
        self.o.other_mode_classes.append(revolveMode)
        print "about to reinit modes"
        self.o._reinit_modes()
        print "done with reinit modes, now see if you can select the reloaded mode"
        return
    
    def copy(self):
        print 'NYI'

    def move(self):
        print 'NYI'

    pass # end of class extrudeMode

# ==

### should be a method in assembly (tho it also uses my local customizations to mol.copy and atom.copy)
##def assy_copy(assy, mols, offset = V(10.0, 10.0, 10.0)):
##    """in assy, copy the mols in the list of mols; return list of new mols.
##    The code is modified from pre-041007 assembly.copy [is that code used? correct? it doesn't do anything with nulist].
##    But then extended to handle post-041007 by bruce, 041007-08
##    Note, as a side effect (of molecule.copy), the new mols are picked and the old mols are unpicked. ####k [not anymore 041014]
##    """
##    self = assy
##    nulist = [] # moved out of loop; is that a bug in assy.copy too?? ###k
##    for mol in mols[:]: # copy the list in case it happens to be self.selmols (needed??)
##        self.changed() # only if loop runs
##        numol = mol.copy( mol.dad, offset)
##        nulist += [numol]
##        self.addmol(numol) ###k ###@@@ why was this not already done in mol.copy?? [bruce 041116 question]
##            # answer: because mol.copy makes mols meant for the clipboard, too! addmol for them is very wrong. [bruce 050202]
##        # what does it, when mol is actually copied by UI? 
##    return nulist

# should be a method in assembly (maybe there is one like this already??)
def assy_merge_mols(assy, mollist):
    "merge multiple mols in assy into one mol in assy, and return it"
    mollist = list(mollist) # be safe in case it's identical to assy.selmols,
        # which we might modify as we run
    assert len(mollist) >= 1
    ## mollist.sort() #k ok for mols? should be sorted by name, or by
    ## # position in model tree groups, I think...
    ## for now, don't sort, use selection order instead.
    res = mollist[0]
    for mol in mollist[1:]: # ok if no mols in this loop
        if platform.atom_debug:
            print "fyi (atom_debug): extrude merging a mol"
        res.merge(mol) ###k ###@@@ 041116 new feature, untested
        # note: this will unpick mol (modifying assy.selmols) and kill it
    return res

def assy_fix_selmol_bugs(assy):
    # 041116 new feature; as of 041222, runs but don't know if it catches bugs
    # (maybe they were all fixed).
    # Note that selected chunks might be in clipboard, and as of 041222
    # they are evidently also in assy.molecules, and extrude operates on them!
    # It even merges units from main model and clipboard... not sure that's good,
    # but ignore it until we figure out the correct model tree selection semantics
    # in general.
    "work around bugs in other code that prevent extrude from entering"
    for mol in list(assy.selmols):
        if (mol not in assy.molecules) or (not mol.dad) or (not mol.assy):
            try:
                it = " (%r) " % mol
            except:
                it = " (exception in its repr) "
            print "fyi: pruning bad mol %s left by prior bugs" % it
            try:
                mol.unpick()
            except:
                pass
            # but don't kill it (like i did before 041222)
            # in case it's in clipboard and user wants it still there
    #e worry about selatoms too?
    return

# this can remain a local function
def assy_extrude_unit(assy, really_make_mol = 1):
    """If we can find a good extrude unit in assy,
       make it a molecule in there, and return (True, mol);
       else return (False, whynot).
       Note: we might modify assy even if we return False in the end!!!
       To mitigate that (for use in refuseEnter), caller can pass
       really_make_mol = 0, and then we will not change anything in assy
       (unless it has bugs caught by assy_fix_selmol_bugs),
       and return either (True, "not a mol") or (False, whynot).
    """
    # bruce 041222: adding really_make_mol flag.

    assy.unselect_clipboard_items() #bruce 050131 for Alpha

    assy_fix_selmol_bugs(assy)
    resmol = "not a mol"
    if assy.selmols:
        assert type(assy.selmols) == type([]) # assumed by this code; always true at the moment
        if really_make_mol:
            resmol = assy_merge_mols( assy, assy.selmols) # merge the selected mols into one
        return True, resmol
            #e in future, better to make them a group? or use them in parallel?
    elif assy.selatoms:
        if really_make_mol:
            res = []
            def new_old(new, old):
                # new = fragment of selected atoms, old = rest of their mol
                assert new.atoms
                res.append(new) #e someday we might use old too, eg for undo or for heuristics to help deal with neighbor-atoms...
            assy.modifySeparate(new_old_callback = new_old) # make the selected atoms into their own mols
                # note: that generates a status msg (as of 041222).
            assert res, "what happened to all those selected atoms???"
            resmol = assy_merge_mols( assy, res) # merge the newly made mol-fragments into one
                #e or for multiple mols, should we do several extrudes in parallel? hmm, might be useful...
        return True, resmol
    elif len(assy.molecules) == 1:
        # nothing selected, but exactly one molecule in all -- just use it
        if really_make_mol:
            resmol = assy.molecules[0]
        return True, resmol
    else:
        ## print 'assy.molecules is',`assy.molecules` #debug
        return False, "don't know what to extrude: nothing selected, and not exactly one chunk in all"
    pass

# ==

#e between two molecules, find overlapping atoms/bonds ("bad") or singlets ("good") -- as a function of all possible offsets
# (in future, some cases of overlapping atoms might be ok, since those atoms could be merged into one)

# (for now, we notice only bondable singlets, nothing about overlapping atoms or bonds)

cosine_of_permitted_noncollinearity = 0.5 #e we might want to adjust this parameter

def mergeable_singlets_Q_and_offset(s1, s2, offset2 = None):
    """figure out whether singlets s1 and s2, presumed to be in different
    molecules (or in different copies, if now in the same molecule), could
    reasonably be merged (replaced with one actual bond), if s2.molecule was
    moved by approximately offset2 (or considering all possible offset2's
     if this arg is not supplied); and if so, what would be the ideal offset
    (slightly different from offset2) after this merging.
    Return (False, None, None) or (True, ideal_offset2, error_offset2),
    where error_offset2 gives the radius of a sphere of reasonable offset2
    values, centered around ideal_offset2.
    """
    ###e if anyone ever passes offset2, we should take a tolerance arg to
    ###e multiply the error offset, i suppose [bruce 041109]
    #e someday we might move this to a more general file
    #e once this works, we might need to optimize it,
    # since it redoes a lot of the same work
    # when called repeatedly for the same extrudable unit.
    res_bad = (False, None, None)
    a1 = singlet_atom(s1)
    a2 = singlet_atom(s2)
    e1 = a1.element
    e2 = a2.element
    r1 = e1.rcovalent
    r2 = e2.rcovalent
    dir1 = norm(s1.posn()-a1.posn())
    dir2 = norm(s2.posn()-a2.posn())
    # the open bond directions (from their atoms) should point approximately
    # opposite to each other -- per Josh suggestion, require them to be
    # within 60 deg. of collinear.
    closeness = - dot(dir1, dir2) # ideal is 1.0, terrible is -1.0
    if closeness < cosine_of_permitted_noncollinearity:
        if extrude_loop_debug and closeness >= 0.0:
            print "rejected nonneg closeness of %r since less than %r" % (closeness, cosine_of_permitted_noncollinearity)
        return res_bad
    # ok, we'll merge. Just figure out the offset. At the end, compare to offset2.
    # For now, we'll just bend the half-bonds by the same angle to make them
    # point at each other, ignoring other bonds on their atoms.
    new_dir1 = norm( (dir1 - dir2) / 2 )
    new_dir2 = - new_dir1 #e needed?
    a1_a2_offset = (r1 + r2) * new_dir1 # ideal offset, just between the atoms
    a1_a2_offset_now = a2.posn() - a1.posn() # present offset between atoms
    ideal_offset2 = a1_a2_offset - a1_a2_offset_now # required shift of a2
    error_offset2 = (r1 + r2) / 2.0 # josh's guess (replaces 1.0 from the initial tests)
    if offset2:
        if vlen(offset2 - ideal_offset2) > error_offset2:
            return res_bad
    return (True, ideal_offset2, error_offset2)

# ==

# detect reloading
try:
    _already_loaded
except:
    _already_loaded = 1
else:
    print "reloading extrudeMode.py"
pass

def mark_singlets(basemol, colorfunc):
    for a in basemol.atoms.itervalues():
        a.info = a.key
    basemol._colorfunc = colorfunc # maps atoms to colors (due to a hack i will add)
    return


#end of extrude
 # + remember to unpatch _colorfunc from the mols when i'm done
# and info from the atoms? not needed but might as well [nah]

# not done:

# for (i1,i2) in bonds:
            # assume no singlet appears twice in this list!
# this is not yet justified, and if false will crash it when it makes bonds


class revolveMode(extrudeMode):
    "revolve, a slightly different version of Extrude, someday with a different dashboard"

    # class constants
    backgroundColor = 150/255.0, 200/255.0, 100/255.0 # different than in extrudeMode
    modename = 'REVOLVE'
    msg_modename = "revolve mode" #e need to fix up anything else?
    default_mode_status_text = "Mode: Revolve"
    is_revolve = 1

    pass


# more customized should-be mol methods
    
def floats_near(f1,f2):
    return abs( f1-f2 ) <= 0.0000001 # just for use in sanity-check assertions

def check_floats_near(f1,f2,msg = ""):
    if floats_near(f1,f2):
        return True # means good (they were near)
    if msg:
        fmt = "not near (%s):" % msg
    else:
        fmt = "not near:"
    # fmt is not a format but a prefix
    print fmt,f1,f2 # printing a lot...
    return False # means bad

def check_posns_near(p1,p2,msg=""):
    res = False
    for i in [0,1,2]:
        res = res and check_floats_near(p1[i],p2[i],msg+"[%d]"%i)
    return res

def check_quats_near(q1,q2,msg=""):
    res = False
    for i in [0,1,2,3]:
        res = res and check_floats_near(q1[i],q2[i],msg+"[%d]"%i)
    return res

# see above, slightly, for a list of a few unfinished things or bugs in the code
# end
