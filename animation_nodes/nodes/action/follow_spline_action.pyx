import bpy
from ... base_types import AnimationNode
from ... math cimport Vector3, Euler3, Matrix4, matrixToEuler
from ... algorithms.rotations.rotation_and_direction cimport directionToMatrix_LowLevel

from ... data_structures cimport (
    Spline,
    PathIndexActionChannel,
    SimpleBoundedAction
)

class FollowSplineActionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FollowSplineActionNode"
    bl_label = "Follow Spline Action"

    def create(self):
        self.newInput("Spline", "Spline", "spline", defaultDrawType = "PROPERTY_ONLY", dataIsModified = True)
        self.newInput("Float", "Duration", "duration", value = 100)
        self.newOutput("Action", "Action", "action")

    def execute(self, spline, duration):
        if not spline.isEvaluable():
            return None

        return FollowSplineAction(spline, duration)


locationChannels = PathIndexActionChannel.forArray("location", 3)
rotationChannels = PathIndexActionChannel.forArray("rotation_euler", 3)
scaleChannels = PathIndexActionChannel.forArray("scale", 3)

cdef class FollowSplineAction(SimpleBoundedAction):
    cdef Spline spline
    cdef float duration

    def __cinit__(self, Spline spline, float duration):
        self.spline = spline
        self.duration = max(duration, 0.001)

    cdef list getEvaluateFunctions(self):
        cdef list functions = []
        functions.append(self.newFunction(<void*>self.evaluateLocation, locationChannels))
        functions.append(self.newFunction(<void*>self.evaluateRotation, rotationChannels))
        functions.append(self.newFunction(<void*>self.evaluateScale, scaleChannels))
        return functions

    cdef void evaluateLocation(self, float frame, Py_ssize_t index, float *target):
        cdef float t = min(max(frame / self.duration, 0), 1)
        self.spline.evaluatePoint_LowLevel(t, <Vector3*>target)

    cdef void evaluateRotation(self, float frame, Py_ssize_t index, float *target):
        cdef float t = min(max(frame / self.duration, 0), 1)
        cdef Vector3 tangent
        self.spline.evaluateTangent_LowLevel(t, &tangent)
        cdef Matrix4 matrix
        cdef Vector3 guide = Vector3(0, 0, 1)
        directionToMatrix_LowLevel(&matrix, &tangent, &guide, "Z", "X")
        cdef Euler3 rotation
        matrixToEuler(&rotation, &matrix)
        target[0] = rotation.x
        target[1] = rotation.y
        target[2] = rotation.z

    cdef void evaluateScale(self, float frame, Py_ssize_t index, float *target):
        target[0] = 1
        target[1] = 1
        target[2] = 1

    cdef float getStart(self, Py_ssize_t index):
        return 0

    cdef float getEnd(self, Py_ssize_t index):
        return self.duration

    cdef float getLength(self, Py_ssize_t index):
        return self.duration
