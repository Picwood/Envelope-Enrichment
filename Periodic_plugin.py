#-----------------------------------------------------------------------
#     Plugin for periodic condition on the boundary
#-----------------------------------------------------------------------
#     Authors: Stephane Lejeunes,  Stephane Bourgeois
#     Institute: LMA UPR7051, CNRS
#     Date: 24/02/10
#
#-----------------------------------------------------------------------
from abaqusGui import *
from kernelAccess import mdb, session
import i18n
from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog

########################################################################
# Class definition
########################################################################
class PeriodicForm(AFXForm):
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):

        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
                
        # Command
        #
        self.cmd = AFXGuiCommand(self, 'mainopo', 'periodicBoundary_env')
        self.is_smallstrain=AFXBoolKeyword(self.cmd, 'is_smallstrain', AFXBoolKeyword.TRUE_FALSE, True,True)
        self.dim=AFXIntKeyword(self.cmd, 'dim',3)
        self.folderNameKw = AFXStringKeyword(self.cmd, 'folderName', True, '')
        self.iteKw = AFXIntKeyword(self.cmd, 'ite', True, 5)
        
        
        
        self.owner=owner
        self.setS1=None
        self.setS2=None
        self.setS3=None
        self.setM3=None
        self.setM2=None
        self.setM1=None
        self.select_wd=None
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):
        vpName = session.currentViewportName
        modelName = session.sessionState[vpName]['modelName']
        m=mdb.models[modelName]
        a = m.rootAssembly
        self.dim.setValue(3)
        if(a.getMassProperties()['volume']==None): 
           self.dim.setValue(2)
        db = PeriodicDB(self,self.dim)
        return db

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class PeriodicDB(AFXDataDialog):
    [
        ID_M1,
        ID_M2,
        ID_M3,
        ID_S1,
        ID_S2,
        ID_S3,
        select_wd,
        homo
    ] = range(AFXDataDialog.ID_LAST, AFXDataDialog.ID_LAST+8)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form,  dim):
        #self.cmd = sendCommand("periodicBoundary_env.__init__()")
        form.setS1=None
        form.setS2=None
        form.setS3=None

        self.step2=None
        AFXDataDialog.__init__(self, form, 'Periodic conditions on the boundary', self.OK|self.CANCEL)
                      
        vf = FXVerticalFrame(self,  LAYOUT_FILL_Y|LAYOUT_FILL_X)
        form.is_smallstrain.setValue(True)

        #gb3 = FXGroupBox(vf, 'Envelope Homogenization', LAYOUT_FILL_X|FRAME_GROOVE)
        #self.dim=dim.getValue()
        #
        #hf3 = FXMatrix(gb3, 2,opts=MATRIX_BY_COLUMNS|LAYOUT_FILL_X|LAYOUT_FILL_Y)        
        #self.label1 = FXLabel(hf3,'Working directory',opts=JUSTIFY_LEFT|LAYOUT_FILL_X|LAYOUT_FILL_COLUMN)
        #FXButton(hf3, 'Select...',None,self,self.select_wd,opts=LAYOUT_RIGHT|BUTTON_NORMAL)
        #self.label2 = FXLabel(hf3, 'Homogenize',opts=JUSTIFY_LEFT|LAYOUT_FILL_X|LAYOUT_FILL_COLUMN)
        #FXButton(hf3, 'Go',None,self,self.homo,opts=LAYOUT_RIGHT|BUTTON_NORMAL)
        
        #RsgFileTextField(p='GroupBox_1', ncols=12, labelText='File name:', keyword='folderName', default='')
        
        
        AFXDataDialog.__init__(self, form, 'homtools',
                               self.OK|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)


        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('OK')
        GroupBox_1 = FXGroupBox(p=self, text='Envelope Homogenization', opts=FRAME_GROOVE|LAYOUT_FILL_X)
        fileHandler = _rsgTmp001_DBFileHandler(form, 'fileName', 'All files (*)')
        fileTextHf = FXHorizontalFrame(p=GroupBox_1, opts=0, x=0, y=0, w=0, h=0,
                                       pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        fileTextHf.setSelector(99)
        AFXTextField(p=fileTextHf, ncols=12, labelText='Working directory', tgt=form.folderNameKw, sel=0,
                     opts=AFXTEXTFIELD_STRING|LAYOUT_CENTER_Y)
        icon = afxGetIcon('fileOpen', AFX_ICON_SMALL )
        FXButton(p=fileTextHf, text='	Select File\nFrom Dialog', ic=icon, tgt=fileHandler, sel=AFXMode.ID_ACTIVATE,
                 opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=1, pr=1, pt=1, pb=1)
        spinner = AFXSpinner(GroupBox_1, 6, 'Iteration', form.iteKw, 0)
        spinner.setRange(1, 15)
        spinner.setIncrement(1)
        if isinstance(GroupBox_1, FXHorizontalFrame):
            FXVerticalSeparator(p=GroupBox_1, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=2, pb=2)
        else:
            FXHorizontalSeparator(p=GroupBox_1, x=0, y=0, w=0, h=0, pl=2, pr=2, pt=2, pb=2)
        
        self.form=form
        self.Refpoint=False
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #def processUpdates(self):
    #    self.label1.setText('Working directory')
    #    self.label2.setText('Homogenize')
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCmdSelect(self,sender,sel,ptr):
         self.step2=_rsgTmp001_DBFileHandler(self.form.owner)
         self.step2.activate()
         return 1
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCmdHomo(self,sender,sel,ptr):
         self.step2=createRVE(self.form.owner)
         self.step2.activate()
         return 1

#class selectWD(AFXProcedure):
class _rsgTmp001_DBFileHandler(FXObject):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form, keyword, patterns='*'):

        self.form = form
        self.patterns = patterns
        self.patternTgt = AFXIntTarget(0)
        exec('self.fileNameKw = form.%sKw' % keyword)
        self.readOnlyKw = AFXBoolKeyword(None, 'readOnly', AFXBoolKeyword.TRUE_FALSE)
        FXObject.__init__(self)
        FXMAPFUNC(self, SEL_COMMAND, AFXMode.ID_ACTIVATE, _rsgTmp001_DBFileHandler.activate)
        
        self.cmd = AFXGuiCommand(self, 'setWorkingDir', 'periodicBoundary_env.py')
        self.workdir = AFXObjectKeyword(self.cmd, 'workdir', TRUE)
    

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def activate(self, sender, sel, ptr):

        fileDb = AFXFileSelectorDialog(getAFXApp().getAFXMainWindow(), 'Select a File',
                                       self.fileNameKw, self.readOnlyKw,
                                       AFXSELECTFILE_ANY, self.patterns, self.patternTgt)
        fileDb.setReadOnlyPatterns('*.odb')
        fileDb.create()
        fileDb.showModal()



import os
absPath = os.path.abspath(__file__)
absDir  = os.path.dirname(absPath)
helpUrl = os.path.join(absDir, 'www.lma.cnrs-mrs.fr')

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()

# Register a GUI plug-in in the Plug-ins menu.
#
toolset.registerGuiMenuButton(
    object=PeriodicForm(toolset), buttonText='Homtools|Periodic Bounday Conditions',
    kernelInitString='import periodicBoundary_env; periodicBoundary_env=periodicBoundary_env.MainFrame()',
    version='1.1', author='S. Lejeunes & S. Bourgeois (LMA-CNRS UPR7051)',
    applicableModules = ['Part','Interaction'],
    description='A simple Gui to define periodic Boundary Conditions '
                "This plug-in's files may be copied from " + absDir,
    helpUrl=helpUrl
)

