bl_info = {
	"name": "Python Toolbar",
	"author": "kurzemnieks",
	"version": (0, 3 ),
	"blender": (2, 80, 0),
	"location": "",
	"description": "Execute python from 3d view",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "System"}

import bpy

from bpy.types import (
    Operator,
    Menu,
    Panel,
    UIList,
    PropertyGroup
)

from bpy.props import (
    StringProperty,
    IntProperty,
    PointerProperty,
    EnumProperty
)

class PythonPanelUIParams(PropertyGroup):
    code_line : StringProperty(description="Python command")
    text_name : StringProperty(name="source", description="Python source")

class PythonExec(bpy.types.Operator):
    """Execute python scripts from 3D view"""
    bl_idname = "system.exec_python"
    bl_label = "Execute Python"
    bl_options = {'REGISTER', 'UNDO'}

    set_mode : EnumProperty(name="Execution mode",
                            items=[
                                ('line', "Line", "Execute text line"),
                                ('text', "Text", "Execute text file")
                            ],
                            description="Execution mode", options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):                
        ui_params = bpy.context.window_manager.python_panel
        code = ""
        if self.set_mode == 'text':
            if ui_params.text_name in bpy.data.texts:
                text = bpy.data.texts[ui_params.text_name]
                code = text.as_string()
        elif self.set_mode =='line':
            code = ui_params.code_line

        if len(code) > 0:
            exec(code)
        return {'FINISHED'}

def HeaderPanel(self, context):
    layout = self.layout
    ui_params = bpy.context.window_manager.python_panel
    row = layout.row(align=True)
    row.scale_x = 3.0
    row.alignment = 'EXPAND'
    row.prop(ui_params,"code_line", text="")
    row = layout.row(align=True)
    row.operator('system.exec_python', text="Run Line").set_mode = "line"
    
    row = layout.row(align=True)    
    row.scale_x = 1.3    
    row.prop_search(ui_params, "text_name", bpy.data,"texts", text="")    
    row = layout.row(align=True)
    row.operator('system.exec_python',text="Run Script").set_mode = "text"

class Panel3DViewPython(bpy.types.Panel):
    bl_label = 'Python'
    bl_idname = "VIEW3D_PT_python_panel"
    bl_space_type = 'VIEW_3D'    
    bl_region_type = 'UI'
    bl_category = 'Scripting'
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout

        #ui_params = bpy.context.area.python_panel
        ui_params = bpy.context.window_manager.python_panel
        
        col = layout.column()
        row = col.row(align=True)        
        row.prop(ui_params, "code_line", text="Code")        
        row = col.row(align=True)
        row.operator('system.exec_python', text="Run Line").set_mode = "line"

        col.separator()

        row = col.row(align=True)
        row = row.split(factor=0.8)
        row.prop_search(ui_params, "text_name", bpy.data, "texts", text="Script:")
        row.operator('system.exec_python', text = "Run Script").set_mode = "text"


addon_keymaps = []

def register():
    bpy.utils.register_class(PythonPanelUIParams)
    bpy.utils.register_class(PythonExec)
    #bpy.types.VIEW3D_HT_header.append(HeaderPanel)
    bpy.utils.register_class(Panel3DViewPython)
    bpy.types.WindowManager.python_panel = PointerProperty(
        type=PythonPanelUIParams, name="Python Panel contents")

    
    kcfg = bpy.context.window_manager.keyconfigs.addon
    if kcfg:
        km = kcfg.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("system.exec_python", 'X', 'PRESS', shift=True, alt=True)
        setattr(kmi.properties, 'set_mode', 'line')
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("system.exec_python", 'X', 'PRESS', ctrl=True, alt=True)
        setattr(kmi.properties, 'set_mode', 'text')
        addon_keymaps.append((km, kmi))
    

def unregister():

    # remove keymap entry
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    bpy.utils.unregister_class(PythonPanelUIParams)
    bpy.utils.unregister_class(PythonExec)
    bpy.utils.unregister_class(Panel3DViewPython)
    #bpy.types.VIEW3D_HT_header.remove(HeaderPanel)
    del bpy.types.WindowManager.python_panel

if __name__ == "__main__":
    register()
