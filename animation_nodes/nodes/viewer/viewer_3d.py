import os
import bpy
from bpy.props import *
from ... draw_handler import drawHandler
from ... base_types import AnimationNode
from ... tree_info import getNodesByType
from ... utils.blender_ui import redrawAll

from mathutils import Vector, Matrix
from ... nodes.vector.c_utils import convert_Vector2DList_to_Vector3DList
from ... data_structures import Vector3DList, Vector2DList, Matrix4x4List, Spline, BezierSpline

import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from ... graphics.import_shader import getShader
from ... graphics.c_utils import getMatricesVBOandIBO

dataByIdentifier = {}

class DrawData:
    def __init__(self, data, drawFunction):
        self.data = data
        self.drawFunction = drawFunction

drawableDataTypes = (Vector3DList, Vector2DList, Matrix4x4List, Vector, Matrix, Spline)

class Viewer3DNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_Viewer3DNode"
    bl_label = "3D Viewer"

    def drawPropertyChanged(self, context):
        self.execute(self.getCurrentData())
        self.redrawViewport(context)

    def redrawViewport(self, context):
        redrawAll()

    enabled: BoolProperty(name = "Enabled", default = True, update = redrawViewport)

    width: IntProperty(name = "Size", default = 2, min = 1, update = drawPropertyChanged)

    matrixScale: FloatProperty(name = "Scale", default = 1, update = drawPropertyChanged)

    drawColor: FloatVectorProperty(name = "Draw Color",
        default = [0.9, 0.9, 0.9], subtype = "COLOR",
        soft_min = 0.0, soft_max = 1.0,
        update = drawPropertyChanged)

    pointAmount: IntProperty(name = "Amount", default = 50, update = drawPropertyChanged)

    def create(self):
        self.newInput("Generic", "Data", "data")

    def draw(self, layout):
        data = self.getCurrentData()
        if data is None:
            return

        col = layout.column()
        row = col.row(align = True)
        row.prop(self, "width", text = "Width")
        icon = "LAYER_ACTIVE" if self.enabled else "LAYER_USED"
        row.prop(self, "enabled", text = "", icon = icon)

        if isinstance(data, (Vector, Vector3DList)):
            col.prop(self, "drawColor", text = "")
        elif isinstance(data, (Matrix, Matrix4x4List)):
            col.prop(self, "matrixScale", text = "Scale")
        elif isinstance(data, Spline):
            if isinstance(data, BezierSpline):
                col.prop(self, "pointAmount")
            col.prop(self, "drawColor", text = "")

    def execute(self, data):
        self.freeDrawingData()
        if not isinstance(data, drawableDataTypes):
            return
        if isinstance(data, Vector3DList):
            dataByIdentifier[self.identifier] = DrawData(data, self.drawVectors)
        if isinstance(data, Vector2DList):
            vectors = convert_Vector2DList_to_Vector3DList(data)
            dataByIdentifier[self.identifier] = DrawData(vectors, self.drawVectors)
        elif isinstance(data, Vector) and len(data) in (2, 3):
            vector = data.to_3d()
            dataByIdentifier[self.identifier] = DrawData(Vector3DList.fromValues([vector]), self.drawVectors)
        elif isinstance(data, Matrix4x4List):
            dataByIdentifier[self.identifier] = DrawData(data, self.drawMatrices)
        elif isinstance(data, Matrix):
            dataByIdentifier[self.identifier] = DrawData(Matrix4x4List.fromValues([data]), self.drawMatrices)
        elif isinstance(data, Spline):
            dataByIdentifier[self.identifier] = DrawData(data, self.drawSpline)

    def drawVectors(self, vectors):
        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'POINTS', {"pos": vectors.asNumpyArray().reshape(-1, 3)})

        shader.bind()
        shader.uniform_float("color", (*self.drawColor, 1))

        glPointSize(self.width)
        batch.draw(shader)

    def drawMatrices(self, matrices):
        shader = getShader(os.path.join(os.path.dirname(__file__), "matrix_shader.glsl"))
        vbo, ibo = getMatricesVBOandIBO(matrices, self.matrixScale)
        batch = batch_for_shader(shader, 'LINES',
            {"pos": vbo.asNumpyArray().reshape(-1, 3)},
            indices = ibo.asNumpyArray().reshape(-1, 2))

        shader.bind()
        viewMatrix = bpy.context.region_data.perspective_matrix
        shader.uniform_float("u_ViewProjectionMatrix", viewMatrix)
        shader.uniform_int("u_Count", len(matrices))

        glLineWidth(self.width)
        batch.draw(shader)

    def drawSpline(self, spline):
        vectors = spline.points
        if spline.isEvaluable() and isinstance(spline, BezierSpline):
            vectors = spline.getDistributedPoints(self.pointAmount, 0, 1, 'RESOLUTION')
        lineType = 'LINE_LOOP' if spline.cyclic else 'LINE_STRIP'

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, lineType, {"pos": vectors.asNumpyArray().reshape(-1, 3)})

        shader.bind()
        shader.uniform_float("color", (*self.drawColor, 1))

        glLineWidth(self.width)
        batch.draw(shader)

    def delete(self):
        self.freeDrawingData()

    def freeDrawingData(self):
        if self.identifier in dataByIdentifier:
            del dataByIdentifier[self.identifier]

    def getCurrentData(self):
        if self.identifier in dataByIdentifier:
            return dataByIdentifier[self.identifier].data

@drawHandler("SpaceView3D", "WINDOW", "POST_VIEW")
def draw():
    for node in getNodesByType("an_Viewer3DNode"):
        if node.enabled and node.identifier in dataByIdentifier:
            drawData = dataByIdentifier[node.identifier]
            drawData.drawFunction(drawData.data)
