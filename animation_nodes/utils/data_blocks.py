import bpy

collectionNameByType = {
    "MESH" : "meshes",
    "CAMERA" : "cameras",
    "FONT" : "curves",
    "CURVE" : "curves",
    "SURFACE" : "curves",
    "META" : "metaballs",
    "ARMATURE" : "armatures",
    "LATTICE" : "lattices",
    "LIGHT" : "lights",
    "SPEAKER" : "speakers"
}

def removeNotUsedDataBlock(data, type):
    getattr(bpy.data, collectionNameByType[type]).remove(data)
