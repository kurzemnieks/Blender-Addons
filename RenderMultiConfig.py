import bpy
from bpy.props import CollectionProperty
from bpy.props import StringProperty
from bpy.types import PropertyGroup

#define special types for passing parameters
class StringValue(bpy.types.PropertyGroup):
    value: StringProperty(name="Value")
    
class StringCollection(bpy.types.PropertyGroup):
    value: CollectionProperty(type=StringValue)

#define operator class
class Multi_Render(bpy.types.Operator):
    bl_idname = "render.everything"
    bl_label = "Render Everything!"

    #Operator input parameters
    
    #string - Base path to render to..
    basePath: StringProperty(name="Path")
    
    #List of cameras to render 
    camerasList: CollectionProperty(type=StringValue, name="Cameras") 
    
    #List of material configurations to render
    materialCfg: CollectionProperty(type=StringCollection, name="Materials") 
    
    #####################
    # internal variables
    cancelRender = None     #was render cancelled by user
    rendering = None        #is currently rendering
    renderQueue = None      #render queue 
    timerEvent = None       #timer

    #Rendering callback functions
    def pre_render(self, dummy):
        self.rendering = True    #mark rendering flag

    def post_render(self, dummy):
        self.renderQueue.pop(0) #remove finished item from render queue
        self.rendering = False  #clear rendering flag

    def on_render_cancel(self, dummy):
        self.cancelRender = True    #mark cancel render flag

    #Main operator function for user execution
    def execute(self, context):
        self.cancelRender = False   # clear cancel flag
        self.rendering = False      # clear rendering flag
                
        
        #fill renderQueue from input parameters with each camera rendering each material configuration
        self.renderQueue = []
        for mat in self.materialCfg:
            for cam in self.camerasList:
                self.renderQueue.append({"Camera":cam.value, "MatCfg":mat.value})
        
                      
        #Register callback functions
        bpy.app.handlers.render_pre.append(self.pre_render)
        bpy.app.handlers.render_post.append(self.post_render)
        bpy.app.handlers.render_cancel.append(self.on_render_cancel)

        #Create timer event that runs every second to check if render renderQueue needs to be updated
        self.timerEvent = context.window_manager.event_timer_add(1.0, window=context.window)
        
        #register this as running in background 
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    #modal callback when there is some event.. 
    def modal(self, context, event):

        #timer event every second        
        if event.type == 'TIMER':                                 

            # If cancelled or no items in queue to render, finish.
            if not self.renderQueue or self.cancelRender is True:
                
                #remove all render callbacks                
                bpy.app.handlers.render_pre.remove(self.pre_render)
                bpy.app.handlers.render_post.remove(self.post_render)
                bpy.app.handlers.render_cancel.remove(self.on_render_cancel)
                
                #remove timer
                context.window_manager.event_timer_remove(self.timerEvent)
                
                self.report({"INFO"},"RENDER QUEUE FINISHED")

                return {"FINISHED"} 

            #nothing is rendering and there are items in queue
            elif self.rendering is False: 
                                          
                sc = bpy.context.scene
                qitem = self.renderQueue[0] #first item in rendering queue
                
                #change scene active camera
                cameraName = qitem["Camera"]
                if cameraName in sc.objects:
                    sc.camera = bpy.data.objects[qitem["Camera"]]     
                else:
                    self.report({'ERROR_INVALID_INPUT'}, message="Can not find camera "+cameraName+" in scene!")
                    return {'CANCELLED'}
                    
                    
                matCfg = qitem["MatCfg"]
                # for simplcity we store special key __config_name along material assignments to store name for this material configuration
                configName = matCfg["__config_name"].value
                
                self.report({"INFO"}, "Rendering config: " + configName)

                #set output file path as base path + condig name + camera name
                sc.render.filepath = self.basePath + configName + "_" + sc.camera.name
                print("Out Path: " + sc.render.filepath)
                                
                #Go through and apply material configs
                for kc in matCfg:
                    if kc.name == "__config_name":
                        continue
                    
                    objName = kc.name
                    matName = kc.value
                    
                    obj = None
                    
                    if objName in sc.objects:
                        obj = bpy.data.objects[objName]
                    else:
                        self.report({'ERROR_INVALID_INPUT'}, message="Can not find object "+objName+" in scene!")
                        
                    if matName in bpy.data.materials and obj is not None:
                        mat = bpy.data.materials[matName]
                        obj.material_slots[0].material = mat #set as fist material .. will not work with multiple materials
                    else:
                        self.report({'ERROR_INVALID_INPUT'}, message="Can not find material "+matName+" in scene!")
                    
                #start new render                
                bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)

        return {"PASS_THROUGH"}

def register():
    bpy.utils.register_class(StringValue)
    bpy.utils.register_class(StringCollection)
    bpy.utils.register_class(Multi_Render)


def unregister():
    bpy.utils.unregister_class(Multi_Render)
    bpy.utils.unregister_class(StringValue)
    bpy.utils.unregister_class(StringCollection)



if __name__ == "__main__":
    register()
    
    # build input parameters like this:
    # Cameras:
    # [ 
    #   { "name":"x", "value":"camera_name" }, 
    #   { "name":"x", "value":"camera_name" }, 
    #   ...
    # ]
    #
    
    # TODO: Can we optimize this structure and passing logic, to be more reasonable regarding config_name??
    # Material:
    # [ 
    #   { "name":"x", "value": 
    #       [
    #           { "name":"__config_name", "value":"config name value" },
    #           { "name":"object_name", "value":"material_name" },
    #           { "name":"object_name", "value":"material_name" },
    #           ...
    #       ]
    #   },
    #   ...
    # ]
    #
    
    #c_cameras = bpy.data.collections['Cameras']
    #cameras = [ {"name":str(i), "value":o.name} for i,o in enumerate(c_cameras.objects) ]
    
    # Below is a code that builds input parameters and executes operator. You can do that from a separate script if 
    # operator is registered as addon. In that case remove all code below this comment. 
    
    cameras = [
                {"name":"1", "value":"Camera_0"},
                {"name":"2", "value":"Camera_1"}
            ]
        
    matConf = []
    
    cfg = { "name":"1", "value": 
            [ 
                {"name":"__config_name", "value":"Config_1"},
                {"name":"Cube_1", "value":"Mat_A"},
                {"name":"Cube_2", "value":"Mat_B"}                
            ]
        }
    matConf.append(cfg)
    
    cfg = { "name":"2", "value": 
            [ 
                {"name":"__config_name", "value":"Config_2"},
                {"name":"Cube_1", "value":"Mat_B"},
                {"name":"Cube_2", "value":"Mat_C"}                
            ]
        }
    matConf.append(cfg)
    
    cfg = { "name":"3", "value": 
            [ 
                {"name":"__config_name", "value":"Config_3"},
                {"name":"Cube_1", "value":"Mat_C"},
                {"name":"Cube_2", "value":"Mat_A"}                
            ]
        }
    matConf.append(cfg)

    #This is how you call the operator once it is registered!
    bpy.ops.render.everything(basePath = "//RenderAll/", camerasList=cameras, materialCfg=matConf)
    