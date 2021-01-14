def importDataStructures():
    from . color import Color
    from . struct import ANStruct

    from . lists.clist import CList
    from . meshes.mesh_data import Mesh
    from . gpencils.gp_layer_data import GPLayer
    from . gpencils.gp_frame_data import GPFrame
    from . gpencils.gp_stroke_data import GPStroke
    from . lists.polygon_indices_list import PolygonIndicesList
    from . lists.base_lists import (
        Vector3DList, Vector2DList, Matrix4x4List, EdgeIndicesList, EulerList, ColorList,
        BooleanList, FloatList, DoubleList, LongList, IntegerList, UShortList, CharList,
        QuaternionList, UIntegerList, ShortList, UShortList
    )

    from . virtual_list.virtual_list import VirtualList, VirtualPyList
    from . virtual_list.virtual_clists import (
        VirtualVector3DList, VirtualMatrix4x4List, VirtualEulerList, VirtualBooleanList,
        VirtualFloatList, VirtualDoubleList, VirtualLongList, VirtualColorList,
        VirtualVector2DList, VirtualQuaternionList
    )

    from . splines.base_spline import Spline
    from . splines.poly_spline import PolySpline
    from . splines.bezier_spline import BezierSpline
    from . default_lists.c_default_list import CDefaultList
    from . interpolation import Interpolation
    from . falloffs.falloff_base import Falloff, BaseFalloff, CompoundFalloff

    from . sounds.sound import Sound
    from . sounds.sound_data import SoundData
    from . sounds.sound_sequence import SoundSequence

    from . midi.midi_note import MIDINote
    from . midi.midi_track import MIDITrack

    from . action import (
        Action, ActionEvaluator, ActionChannel,
        PathActionChannel, PathIndexActionChannel,
        BoundedAction, UnboundedAction,
        BoundedActionEvaluator, UnboundedActionEvaluator,
        SimpleBoundedAction, SimpleUnboundedAction,
        DelayAction
    )

    return locals()

dataStructures = importDataStructures()
__all__ = list(dataStructures.keys())
globals().update(dataStructures)
