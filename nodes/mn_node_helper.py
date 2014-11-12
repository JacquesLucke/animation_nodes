import bpy
from mn_node_utils import *

mainObjectContainerName = "Animation Nodes Object Container"
helperMaterialName = "Helper Material for Animation Nodes"

def getMainObjectContainer():
	objectContainer = bpy.context.scene.objects.get(mainObjectContainerName)
	if objectContainer is None:
		objectContainer = newMainObjectContainer()
	return objectContainer
def newMainObjectContainer():
	objectContainer = bpy.data.objects.new(mainObjectContainerName, None)
	objectContainer.hide = True
	objectContainer.hide_render = True
	objectContainer.hide_select = True
	bpy.context.scene.objects.link(objectContainer)
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
def getNotUsedMaterialNodeName():
	return getPossibleNodeName(getHelperMaterial().node_tree)