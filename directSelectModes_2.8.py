bl_info = {
	"name": "Direct Selection Modes",
	"author": "kurzemnieks",
	"version": (1, 0),
	"blender": (2, 80, 0),
	"location": "",
	"description": "Allows entering edit submode directly",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Selection"}
	
import bpy

def active_has_edit_mode():
	if bpy.context.active_object is None:
		return False
	if bpy.context.active_object.type == "LAMP":
		return False
	if bpy.context.active_object.type == "CAMERA":
		return False
	if bpy.context.active_object.type == "SPEAKER":
		return False
	if bpy.context.active_object.type == "EMPTY":
		return False
	return True

class OBJECT_OT_enter_edit_submode(bpy.types.Operator):
	bl_idname = "object.enter_edit_submode"
	bl_label = "Enter edit submode"

	smode : bpy.props.EnumProperty(
		name="Submode", 
		description="Submode to enter directly", 
		items=(
			("VERTEX", "Vertex mode", ""),
			("EDGE", "Edge mode", ""),
			("FACE", "Face mode", ""),
			)
		)
	@classmethod
	def poll(cls, context):
		return context.active_object is not None
		
	def execute(self, context):
		if bpy.context.mode == "OBJECT" and active_has_edit_mode() == True:
			bpy.ops.object.mode_set(mode="EDIT")
			if bpy.context.mode == "EDIT_MESH":
				if self.smode == "VERTEX":
					bpy.ops.mesh.select_mode(type='VERT')
				elif self.smode == "EDGE":
					bpy.ops.mesh.select_mode(type='EDGE')
				elif self.smode == "FACE":
					bpy.ops.mesh.select_mode(type='FACE')

		return {"FINISHED"}

def register():
	bpy.utils.register_class(OBJECT_OT_enter_edit_submode)

def unregister():
	bpy.utils.unregister_class(OBJECT_OT_enter_edit_submode)

if __name__ == "__main__":
	register()