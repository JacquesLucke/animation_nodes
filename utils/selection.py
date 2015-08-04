import bpy
from bpy.app.handlers import persistent

enableSelectionSorting = True
sortedSelectionNames = []

def getSortedSelectedObjects():
    objects = []
    for name in getSortedSelectedObjectNames():
        objects.append(bpy.data.objects.get(name))
    return objects
    
def getSortedSelectedObjectNames():
    return sortedSelectionNames

@persistent
def updateSelectionSorting(scene):
    global sortedSelectionNames

    selectedNames = getSelectedObjectNames()

    if enableSelectionSorting:
        newSortedSelection = []
        for name in sortedSelectionNames:
            if name in selectedNames:
                newSortedSelection.append(name)
        for name in selectedNames:
            if name not in newSortedSelection:
                newSortedSelection.append(name)
        sortedSelectionNames = newSortedSelection
    else:
        sortedSelectionNames = selectedNames

def getSelectedObjectNames():
    selectedNames = []
    for object in bpy.context.selected_objects:
        selectedNames.append(object.name)
    return selectedNames



# Register
##################################

def registerHandlers():
    bpy.app.handlers.scene_update_post.append(updateSelectionSorting)

def unregisterHandlers():
    bpy.app.handlers.scene_update_post.remove(updateSelectionSorting)
