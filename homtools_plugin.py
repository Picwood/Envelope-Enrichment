from abaqusGui import *
from abaqusConstants import ALL
import osutils, os
import homtoolsDB

###########################################################################
# Class definition
###########################################################################

class Homtools_plugin(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        self.next_step = 0
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='import_model',
            objectName='periodicBoundary_env', registerQuery=False)
        pickedDefault = ''
        self.workdirKw = AFXStringKeyword(self.cmd, 'workdir', True, '')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_next_dialog(self):
        if self.next_step == 0:
            return self.getFirstDialog()
        else:
            return self.getSecondDialog()
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def getFirstDialog(self):

        return homtoolsDB.HomtoolsDB(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getSecondDialog(self):

        return homtoolsDB.HomtoolsDBIte(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def doCustomChecks(self):
        self.next_step = self.next_step + 1
        #fileinputed = self.workdirKw()
        #if fileinputed != '':
        #    self.next_step = 1
        if self.next_step == 2:
            self.cmd = AFXGuiCommand(mode=self, method='main',
                                     objectName='periodicBoundary_env', registerQuery=False)
            self.workdirKw = AFXStringKeyword(self.cmd, 'workdir', True, '')
            self.iterationKw = AFXIntKeyword(self.cmd, 'iteration', True, 5)
        return True
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def okToCancel(self):

        # No need to close the dialog when a file operation (such
        # as New or Open) or model change is executed.
        #
        return False
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Register the plug-in
#
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Envelope Enrichment', 
    object=Homtools_plugin(toolset),
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    kernelInitString='import periodicBoundary_env',
    applicableModules=ALL,
    version='N/A',
    author='N/A',
    description='N/A',
    helpUrl='N/A'
)
