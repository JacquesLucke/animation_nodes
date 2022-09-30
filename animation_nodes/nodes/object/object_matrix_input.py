import bpy
from ... base_types import AnimationNode, VectorizedSocket

class ObjectMatrixInputNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_ObjectMatrixInputNode"
    bl_label = "Object Matrix Input"
    codeEffects = [VectorizedSocket.CodeEffect]

    useObjectList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Objects", "objects")))

        self.newOutput(VectorizedSocket("Matrix", "useObjectList",
            ("World", "world"), ("Worlds", "worlds")))

        self.newOutput(VectorizedSocket("Matrix", "useObjectList",
            ("Basis", "basis", dict(hide = True)),
            ("Bases", "bases", dict(hide = True))))

        self.newOutput(VectorizedSocket("Matrix", "useObjectList",
            ("Local", "local", dict(hide = True)),
            ("Locals", "locals", dict(hide = True))))

        self.newOutput(VectorizedSocket("Matrix", "useObjectList",
            ("Parent Inverse", "parentInverse", dict(hide = True)), 
            ("Parent Inverses", "parentInverses", dict(hide = True))))

    def getExecutionCode(self, required):
        if len(required) == 0:
            return

        yield "if object is None:"
        if "world" in required:         yield "    world = Matrix.Identity(4)"
        if "basis" in required:         yield "    basis = Matrix.Identity(4)"
        if "local" in required:         yield "    local = Matrix.Identity(4)"
        if "parentInverse" in required: yield "    parentInverse = Matrix.Identity(4)"
        yield "else:"
        yield "    evaluatedObject = AN.utils.depsgraph.getEvaluatedID(object)"
        if "world" in required:         yield "    world = evaluatedObject.matrix_world"
        if "basis" in required:         yield "    basis = evaluatedObject.matrix_basis"
        if "local" in required:         yield "    local = evaluatedObject.matrix_local"
        if "parentInverse" in required: yield "    parentInverse = evaluatedObject.matrix_parent_inverse"
