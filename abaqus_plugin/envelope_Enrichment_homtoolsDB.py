from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class Envelope_Enrichment_homtoolsDB(AFXDataDialog):
    [
        ID_MODEL,
        ID_FILEPATH
    ] = range(AFXToolsetGui.ID_LAST, AFXToolsetGui.ID_LAST+2)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, 'Envelope Enrichment - plugin',
            self.OK|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
            

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('Compute')
        
            
        fileHandler = Envelope_Enrichment_homtoolsDBFileHandler(form, 'filePath', 'All files (*)')
        fileTextHf = FXHorizontalFrame(p=self, opts=0, x=0, y=0, w=0, h=0,
            pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        # Note: Set the selector to indicate that this widget should not be
        #       colored differently from its parent when the 'Color layout managers'
        #       button is checked in the RSG Dialog Builder dialog.
        fileTextHf.setSelector(99)
        
        
        AFXTextField(p=fileTextHf, ncols=12, labelText='File name:', tgt=form.filePathKw, sel=0,
            opts=AFXTEXTFIELD_STRING|LAYOUT_CENTER_Y)
        icon = afxGetIcon('fileOpen', AFX_ICON_SMALL )
        FXButton(p=fileTextHf, text='	Select File\nFrom Dialog', ic=icon, tgt=fileHandler, sel=AFXMode.ID_ACTIVATE,
            opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=1, pr=1, pt=1, pb=1)
        
        import_handler = import_buttonHandler(form)
        import_button = FXHorizontalFrame(p=self, opts=0, x=0, y=0, w=0, h=0,
                                          pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        
        FXButton(p=import_button, text='Import Model', tgt=import_handler, sel=AFXMode.ID_ACTIVATE,
                 opts=BUTTON_NORMAL|LAYOUT_CENTER_Y, x=0, y=0, w=0, h=0, pl=1, pr=1, pt=1, pb=1)
        
        spinner = AFXSpinner(self, 6, 'Iteration', form.iterationKw, 0)
        spinner.setRange(2, 10)
        spinner.setIncrement(1)
        

###########################################################################
# Class definition
###########################################################################

class Envelope_Enrichment_homtoolsDBFileHandler(FXObject):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form, keyword, patterns='*'):

        self.form = form
        self.patterns = patterns
        self.patternTgt = AFXIntTarget(0)
        exec('self.filePathKw = form.%sKw' % keyword)
        self.readOnlyKw = AFXBoolKeyword(None, 'readOnly', AFXBoolKeyword.TRUE_FALSE)
        FXObject.__init__(self)
        FXMAPFUNC(self, SEL_COMMAND, AFXMode.ID_ACTIVATE, Envelope_Enrichment_homtoolsDBFileHandler.activate)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def activate(self, sender, sel, ptr):

        fileDb = AFXFileSelectorDialog(getAFXApp().getAFXMainWindow(), 'Select a File',
            self.filePathKw, self.readOnlyKw,
            AFXSELECTFILE_ANY, self.patterns, self.patternTgt)
        fileDb.setReadOnlyPatterns('*.odb')
        fileDb.create()
        fileDb.showModal()
        
        
class import_buttonHandler(FXObject):
    def __init__(self, form):
        self.form = form
        exec('self.filePathKw = form.filePathKw')
        FXObject.__init__(self)
        FXMAPFUNC(self, SEL_COMMAND, AFXMode.ID_ACTIVATE, import_buttonHandler.activate)
        
    def activate(self, sender, sel, ptr):
        if self.filePathKw != '':
            cmd = 'print \'%s\'' %(self.filePathKw.getValue())
            sendCommand(cmd)
            file = os.path.basename(self.filePathKw.getValue())
            name, ext = os.path.splitext(file)
            cmd = 'mdb.ModelFromInputFile(name=\'%s\', inputFileName=\'%s\')' % (name[0:-6], self.filePathKw.getValue())
            sendCommand(cmd)
            
            