from . mn_execution import nodePropertyChanged, nodeTreeChanged

def propertyChanged(self = None, context = None):
    nodePropertyChanged()
    
def treeChanged(self = None, context = None):
    nodeTreeChanged()
    
def executionCodeChanged(self = None, context = None):
    nodeTreeChanged()    