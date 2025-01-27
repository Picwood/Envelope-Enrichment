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
        
            
        # Main vertical frame
        mainFrame = FXVerticalFrame(self, LAYOUT_FILL_X|LAYOUT_FILL_Y)
        
        # File selection frame
        fileFrame = FXHorizontalFrame(mainFrame, LAYOUT_FILL_X)
        fileHandler = Envelope_Enrichment_homtoolsDBFileHandler(form, 'filePath', 'All files (*)')
        AFXTextField(p=fileFrame, ncols=12, labelText='File name:', 
                    tgt=form.filePathKw, sel=0,
                    opts=AFXTEXTFIELD_STRING|LAYOUT_CENTER_Y)
        icon = afxGetIcon('fileOpen', AFX_ICON_SMALL)
        FXButton(p=fileFrame, text='Select File\nFrom Dialog', ic=icon, 
                tgt=fileHandler, sel=AFXMode.ID_ACTIVATE,
                opts=BUTTON_NORMAL|LAYOUT_CENTER_Y)

        # Model type group box
        modelTypeBox = FXGroupBox(mainFrame, 'Model Configuration', 
                                LAYOUT_FILL_X|FRAME_GROOVE)
        
        # Dimension radio buttons
        dimFrame = FXHorizontalFrame(modelTypeBox)
        FXLabel(dimFrame, 'Dimension:')
        FXRadioButton(dimFrame, '2D', form.dimensionKw, 2,
                     RADIOBUTTON_NORMAL|LAYOUT_CENTER_Y)
        FXRadioButton(dimFrame, '3D', form.dimensionKw, 3,
                     RADIOBUTTON_NORMAL|LAYOUT_CENTER_Y, True)

        # Mesh type radio buttons in a group
        dimFrame2 = FXHorizontalFrame(modelTypeBox)
        FXLabel(dimFrame2, 'Mesh type:')
        FXRadioButton(dimFrame2, 'Embedded', form.meshTypeKw, 4,
                     RADIOBUTTON_NORMAL|LAYOUT_CENTER_Y)
        FXRadioButton(dimFrame2, 'Conform', form.meshTypeKw, 5,
                     RADIOBUTTON_NORMAL|LAYOUT_CENTER_Y)

        # Iteration spinner
        spinnerFrame = FXHorizontalFrame(mainFrame)
        spinner = AFXSpinner(spinnerFrame, 6, 'Iteration:', 
                           form.iterationKw, 0)
        spinner.setRange(2, 10)
        spinner.setIncrement(1)

        # Import button
        import_handler = import_buttonHandler(form)
        FXButton(mainFrame, 'Import Model', tgt=import_handler, 
                sel=AFXMode.ID_ACTIVATE,
                opts=BUTTON_NORMAL|LAYOUT_CENTER_X)

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