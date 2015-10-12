def checkCurrentFile():
    updateSubprograms()

def updateSubprograms():
    from . nodes.system.subprogram_sockets import forceSubprogramUpdate
    forceSubprogramUpdate()
