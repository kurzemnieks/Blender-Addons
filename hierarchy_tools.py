bl_info = {
    "name": "Hierarchy Tools",
    "author": "kurzemnieks",
    "version": (0, 1, 2),
    "blender": (2, 6, 0),
    "location": "View3D > Tool Shelf",
    "description": "Group selected objects under new empty. Reset childs inverse transform. Center parent to children. Snap parent to cursor.",
    "category": "Object"}

import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty
####################################################################################################################
def center_to_children(context):
    parent = context.active_object
    bpy.ops.object.select_all(action='DESELECT')
        
    for child in parent.children:
        child.select = True
    
    change_to_text = bpy.context.area.type == 'TEXT_EDITOR'

    if bpy.context.area.type is not 'VIEW_3D':    
        bpy.context.area.type = 'VIEW_3D' 

    old_cursor = bpy.context.scene.cursor_location.copy()
    bpy.ops.view3d.snap_cursor_to_selected()    
     
    child_objs = []
    for child in parent.children:
        context.scene.objects.active = child
        child_objs.append(child)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        child.select = False        
    
    parent.select = True
    bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
    parent.select = False
    
    for child in child_objs:
        child.select = True
        
    parent.select = True            
    bpy.context.scene.objects.active = parent
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    
    for child in child_objs:
        child.select = False

    bpy.context.scene.cursor_location = old_cursor
    
    if change_to_text:
        bpy.context.area.type = 'TEXT_EDITOR'
        
def parent_to_cursor(context):
    active = context.active_object
    parent = active.parent
    bpy.ops.object.select_all(action='DESELECT')
        
    change_to_text = bpy.context.area.type == 'TEXT_EDITOR'
    if bpy.context.area.type is not 'VIEW_3D':    
        bpy.context.area.type = 'VIEW_3D' 
     
    child_objs = []
    for child in parent.children:
        child.select = True 
        child_objs.append(child)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        child.select = False        
    
    parent.select = True
    bpy.context.scene.objects.active = parent
    bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)

    parent.select = False    
    for child in child_objs:
        child.select = True
        
    parent.select = True            
    bpy.context.scene.objects.active = parent
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    
    for child in child_objs:
        child.select = False
    parent.select = False
    
    active.select = True
    bpy.context.scene.objects.active = active

    if change_to_text:
        bpy.context.area.type = 'TEXT_EDITOR'
    

class CenterToChildrenOp(bpy.types.Operator):
    bl_idname = "object.center_to_children"
    bl_label = "Center object to children"    
    bl_description = 'Center selected object to its children without moving the children'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):        
        return context.active_object is not None and len(context.active_object.children) > 0

    def execute(self, context):
        center_to_children(context)
        return {'FINISHED'}
    
class MoveParentToCursorOp(bpy.types.Operator):
    bl_idname = "object.snap_sparent_to_cursor"
    bl_label = "Move parent to 3d cursor"
    bl_description = 'Move selected objects parent to 3d cursor'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):        
        return context.active_object is not None and context.active_object.parent is not None

    def execute(self, context):
        parent_to_cursor(context)
        return {'FINISHED'}
    
####################################################################################################################
#find top parent object that is not selected
def findActiveTopParent(act):
    p = act.parent
    while (p != None and p.select):
        p = p.parent
    return p

def clearParentInvertMatrix(act):
    old_cursor = bpy.context.scene.cursor_location.copy()
    bpy.ops.object.select_all(action='DESELECT')
    act.select = True
    bpy.ops.view3d.snap_cursor_to_selected()
    bpy.ops.object.location_clear()
    bpy.ops.object.origin_clear()
    bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
    bpy.context.scene.cursor_location = old_cursor
    act.select = False

class ParentStandardOp(bpy.types.Operator):
    bl_idname = 'object.parent_standard'
    bl_label = 'Parent Standard'
    bl_description = 'Parent selected to active without setting inverse correction matrix, but keeping offset'
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        objs = bpy.context.selected_objects
        if bpy.context.object is None:
            return False
        if (len(objs)==1 and objs[0]==bpy.context.object):
            return False
        return (len(objs) > 0)
    
    def execute(self,context):
        act = bpy.context.object
        sel = bpy.context.selected_objects
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        for c in sel:
            clearParentInvertMatrix(c)            
        for s in sel:
            s.select = True
        bpy.context.scene.objects.active = act
        return {'FINISHED'}

class ResetInverseMatrix(bpy.types.Operator):
    bl_idname = 'object.reset_inverse_transform'
    bl_label = 'Reset Invert'
    bl_description = 'Reset child objects invert matrix.'
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        objs = bpy.context.selected_objects
        return (len(objs) > 0)
    def execute(self,context):
        act = bpy.context.object
        sel = bpy.context.selected_objects
        for c in sel:
            clearParentInvertMatrix(c)
            
        for s in sel:
            s.select = True
        bpy.context.scene.objects.active = act
        return {'FINISHED'}
    

class GroupEmpty(bpy.types.Operator):
    bl_idname = 'object.group_in_empty'
    bl_label = 'Group in Empty'
    bl_description = 'Group selected objects under new empty.'
    bl_options = {'REGISTER', 'UNDO'}

    name = StringProperty(name='', default='Group', description='Group name')
    group = bpy.props.BoolProperty(name='Create Group', default=False, description='Also add objects to a group')
    pos = bpy.props.EnumProperty(name='', items=[('CURSOR','Cursor','Cursor'),('ACTIVE','Active','Active'),
    ('CENTER','Center','Selection Center')],description='Empty location', default='CENTER')

    @classmethod
    def poll(cls, context):
        objs = bpy.context.selected_objects
        return (len(objs) > 0)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'name')
        column = layout.column(align=True)
        column.prop(self,'pos')
        column.prop(self,'group')

    def execute(self, context):        
        objs = bpy.context.selected_objects
        act = bpy.context.object        
        if not act:
            act = objs[0]
            bpy.context.scene.objects.active = act

        pnt = findActiveTopParent(act)
                        
        try: bpy.ops.object.mode_set()
        except: pass
            
        bpy.ops.object.add(type='EMPTY')
        new_empty = bpy.context.object
        bpy.context.object.name = self.name
        bpy.context.object.show_name = False
        bpy.context.object.show_x_ray = False
        bpy.context.object.empty_draw_size = 0.1
        
        if pnt is not None:                        
            new_empty.select = True
            bpy.context.scene.objects.active = pnt
            #parent empty to top parent without inverse matrix
            bpy.ops.object.parent_no_inverse_set()

        old_cursor = bpy.context.scene.cursor_location.copy()        
        bpy.ops.object.select_all(action='DESELECT')
        
        #temporarily move 3d cursor to active object or center on all selected
        if self.pos == 'ACTIVE':
            act.select = True
            bpy.ops.view3d.snap_cursor_to_selected()
        elif self.pos == 'CURSOR':
            pass
        else:
            for o in objs:
                o.select = True
            bpy.ops.view3d.snap_cursor_to_selected()
        
        bpy.ops.object.select_all(action='DESELECT')
        new_empty.select = True
                        
        #move new empty to 3d cursor
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)            
        
        #restore cursor pos
        bpy.context.scene.cursor_location = old_cursor                    
                
                        
        #create and add to group if needed
        if self.group:
            bpy.context.scene.objects.active = new_empty
            bpy.ops.group.create(name=self.name)
            bpy.ops.group.objects_add_active()
                             
        for o in objs:            
            #get only top level selected (objects who has no parent among selected)
            if not (o.parent and o.parent in objs):                              
                o.select = True
                bpy.context.scene.objects.active = new_empty
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                o.select = False
                bpy.context.scene.objects.active = None
                
            clearParentInvertMatrix(o)                

            if self.group:
                o.select = True
                bpy.context.scene.objects.active = new_empty
                bpy.ops.group.objects_add_active()
                o.select = False
                            
        new_empty.select = True
        bpy.context.scene.objects.active = new_empty
                                    
        return {'FINISHED'}

####################################################################################################################


class PanelGroupHTools(bpy.types.Panel):
    bl_label = 'Hierarchy Tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Relations'

    def draw(self, context):
        layout = self.layout
        layout.operator('object.group_in_empty')
        layout.operator('object.parent_standard')
        layout.operator('object.reset_inverse_transform')
        layout.operator('object.center_to_children')
        layout.operator('object.snap_sparent_to_cursor')

def register():
    bpy.utils.register_class(GroupEmpty)
    bpy.utils.register_class(ResetInverseMatrix)
    bpy.utils.register_class(CenterToChildrenOp)
    bpy.utils.register_class(MoveParentToCursorOp)
    bpy.utils.register_class(ParentStandardOp)    
    bpy.utils.register_class(PanelGroupHTools)

def unregister():
    bpy.utils.unregister_class(GroupEmpty)
    bpy.utils.unregister_class(ResetInverseMatrix)
    bpy.utils.unregister_class(CenterToChildrenOp)
    bpy.utils.unregister_class(MoveParentToCursorOp)
    bpy.utils.unregister_class(ParentStandardOp)
    bpy.utils.unregister_class(PanelGroupHTools)

if __name__ == '__main__':
    register()