import bpy
import os
import math

# Clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Path to temp_pendant.obj
curr_dir = r"c:\KIRTSOY_CORE\AI_PROGRAMS\LOGO"
input_obj = os.path.join(curr_dir, "temp_pendant.obj")
output_obj = os.path.join(curr_dir, "assets", "kirtsoy_pendant_real_hole.obj")

print("Importing:", input_obj)
# In Blender 4/5, wm.obj_import is used
try:
    bpy.ops.wm.obj_import(filepath=input_obj)
except Exception:
    bpy.ops.import_scene.obj(filepath=input_obj)

pendant = bpy.context.selected_objects[0]
print("Imported pendant object:", pendant.name, "vertices:", len(pendant.data.vertices))

# Create boolean cutting cylinder along X axis
# Cylinder center: X = -5.535, Y = 19.39, Z = 0.0
# Radius = 1.6, depth = 20.0
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.65,
    depth=24.0,
    location=(-5.535, 19.39, 0.0),
    rotation=(0.0, math.radians(90.0), 0.0),
    vertices=32
)
cutter = bpy.context.selected_objects[0]
cutter.name = "BailHoleCutter"

# Add Boolean modifier to pendant
bool_mod = pendant.modifiers.new(name="BailHoleCut", type='BOOLEAN')
bool_mod.operation = 'DIFFERENCE'
bool_mod.object = cutter
bool_mod.solver = 'EXACT' # Exact solver in Blender 5.2

# Apply modifier
bpy.context.view_layer.objects.active = pendant
bpy.ops.object.modifier_apply(modifier="BailHoleCut")

# Remove cutter
bpy.data.objects.remove(cutter, do_unlink=True)

print("Boolean cut completed! Final vertices:", len(pendant.data.vertices), "faces:", len(pendant.data.polygons))

# Select pendant for export
pendant.select_set(True)
bpy.context.view_layer.objects.active = pendant

# Export result to assets/kirtsoy_pendant_real_hole.obj
try:
    bpy.ops.wm.obj_export(filepath=output_obj, export_selected_objects=True)
except Exception:
    bpy.ops.export_scene.obj(filepath=output_obj, use_selection=True)

print("Exported 100% real physical 3D mesh to:", output_obj)
