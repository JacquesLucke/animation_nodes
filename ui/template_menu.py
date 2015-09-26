import bpy

class TemplatesMenu(bpy.types.Menu):
    bl_idname = "an_templates_menu"
    bl_label = "Templates Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("an.empty_subprogram_template")
        layout.operator("an.grid_arrange_objects_template")
        layout.operator("an.random_vertices_offset_template")
        layout.operator("an.network_from_particles_template")
        layout.operator("an.transform_individual_polygons_template")
        layout.operator("an.simple_sound_controler_template")
        layout.operator("an.sound_equalizer_template")
        layout.operator("an.distribute_instances_on_spline_template")
        layout.operator("an.simple_countdown_template")
        layout.operator("an.fcurve_animation_offset_template")

class TemplatesMenuInHeader(bpy.types.Header):
    bl_idname = "an_templates_menu_in_header"
    bl_space_type = "NODE_EDITOR"

    def draw(self, context):
        layout = self.layout
        layout.separator()
        layout.menu("an_templates_menu", text = "Templates")
