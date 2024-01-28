from abaqusGui import *
from abaqusConstants import ALL
import osutils, os


###########################################################################
# Class definition
###########################################################################

class Envelope_Enrichment_homtools_plugin(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}
        self.step = 0
        self.cmd = AFXGuiCommand(mode=self, method='main',
            objectName='periodicBoundary_env', registerQuery=False)
        pickedDefault = ''
        self.ID_MODEL = 0
        self.filePathKw = AFXStringKeyword(self.cmd, 'filePath', True, '')
        self.modelnameKw = AFXStringKeyword(self.cmd, 'modelname', True)
        self.iterationKw = AFXIntKeyword(self.cmd, 'iteration', True, 4)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import envelope_Enrichment_homtoolsDB
        return envelope_Enrichment_homtoolsDB.Envelope_Enrichment_homtoolsDB(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def doCustomChecks(self):
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def okToCancel(self):

        # No need to close the dialog when a file operation (such
        # as New or Open) or model change is executed.
        #
        return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Utility method to issues a command to the kernel
def issue_command(cmd):
    sendCommandString(cmd.getCommandString())
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Register the plug-in
#
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='EE_plugin', 
    object=Envelope_Enrichment_homtools_plugin(toolset),
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    kernelInitString='import periodicBoundary_env',
    applicableModules=ALL,
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
