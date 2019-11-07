import bpy
from .. utils.names import getPossibleNodeName

mainObjectContainerName = "Animation Nodes Object Container"
helperMaterialName = "Helper Material for Animation Nodes"


def getMainObjectContainer(scene):
    objectContainer = bpy.data.collections.get(mainObjectContainerName)
    if objectContainer is None:
        objectContainer = bpy.data.collections.new(mainObjectContainerName)
    if objectContainer.name not in scene.collection.children:
        scene.collection.children.link(objectContainer)
    return objectContainer

def getHelperMaterial():
    helperMaterial = bpy.data.materials.get(helperMaterialName)
    if helperMaterial is None:
        helperMaterial = newHelperMaterial()
    return helperMaterial

def newHelperMaterial():
    material = bpy.data.materials.new(helperMaterialName)
    material.use_nodes = True
    material.use_fake_user = True
    return material
