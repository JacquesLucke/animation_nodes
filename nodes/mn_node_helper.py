import bpy

mainObjectContainerName = "Animation Nodes Object Container"

def getMainObjectContainer():
	objectContainer = bpy.data.objects.get(mainObjectContainerName)
	if objectContainer is None:
		objectContainer = bpy.data.objects.new(mainObjectContainerName, None)
		objectContainer.hide = True
		objectContainer.hide_render = True
		objectContainer.hide_select = True
		bpy.context.scene.objects.link(objectContainer)
	return objectContainer