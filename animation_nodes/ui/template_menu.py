import bpy

class TemplatesMenu(bpy.types.Menu):
    bl_idname = "an_templates_menu"
    bl_label = "Templates Menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("an.grid_arrange_objects_template")
        layout.operator("an.random_vertices_offset_template")
        layout.operator("an.network_from_particles_template")
        layout.operator("an.simple_sound_controller_template")
        layout.operator("an.sound_equalizer_template")
        layout.operator("an.distribute_instances_on_spline_template")
        layout.operator("an.simple_countdown_template")
        layout.operator("an.fcurve_animation_offset_template")
        layout.operator("an.simple_parent_template")
        layout.operator("an.grid_3d_template")
        layout.operator("an.animate_individual_letters_template")

class TemplatesMenuInHeader(bpy.types.Header):
    bl_idname = "an_templates_menu_in_header"
    bl_space_type = "NODE_EDITOR"

    def draw(self, context):
        if context.space_data.tree_type != "an_AnimationNodeTree": return

        layout = self.layout
        layout.separator()
        layout.menu("an_subprograms_menu", text = "Subprograms")
        layout.menu("an_templates_menu", text = "Templates")
