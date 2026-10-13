import bpy, os, json, math, mathutils

curr_dir = r"c:\KIRTSOY_CORE\AI_PROGRAMS\LOGO"
input_obj = os.path.join(curr_dir, "temp_upright_interlocking.obj")
output_obj = os.path.join(curr_dir, "assets", "kirtsoy_pendant_real_hole.obj")

with open(os.path.join(curr_dir, "hole_coords.json"), 'r') as f:
    hole_info = json.load(f)

bpy.ops.wm.read_factory_settings(use_empty=True)

# Import upright interlocking mesh
bpy.ops.wm.obj_import(filepath=input_obj)
pendant = bpy.context.selected_objects[0]
pendant.name = 'Pendant'

# Blender's obj_import applies a rotation_euler=(1.5708, 0, 0) to convert Y-up to Z-up
# So world coordinates: X is width, Y is -depth, Z is height!
# Let's inspect pendant world matrix:
mat = pendant.matrix_world

# In Three.js coordinates:
# X = hole_info['xCenter'] (-6.66)
# Y = hole_info['yBail'] (18.51, height)
# Z = 0 (depth center)
three_hole = mathutils.Vector((hole_info['xCenter'], hole_info['yBail'], 0.0))

# Transform Three.js point to Blender world space:
# In Three.js: (X, Y, Z) where Y is up.
# When imported with rotation (90 around X):
# Blender World: X = Three.X, Y = -Three.Z, Z = Three.Y!
blender_hole_loc = mathutils.Vector((three_hole.x, -three_hole.z, three_hole.y))

print(f"Drilling hole at Blender world location: {blender_hole_loc}")

# Cylinder along X-axis (width):
# In Blender, cylinder axis is along Z by default.
# Rotate around Y by 90 deg to align along X-axis!
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.85,
    depth=35.0,
    location=blender_hole_loc,
    rotation=(0.0, math.radians(90.0), 0.0),
    vertices=32
)
cutter = bpy.context.selected_objects[0]
cutter.name = "HoleCutter"

# Boolean difference
mod = pendant.modifiers.new(name="ChainHoleCut", type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = cutter
mod.solver = 'EXACT'

bpy.context.view_layer.objects.active = pendant
bpy.ops.object.modifier_apply(modifier="ChainHoleCut")
bpy.data.objects.remove(cutter, do_unlink=True)

bpy.ops.object.shade_smooth()

# Export back to assets/kirtsoy_pendant_real_hole.obj
# wm.obj_export converts back from Blender Z-up to Three.js Y-up!
pendant.select_set(True)
bpy.context.view_layer.objects.active = pendant
bpy.ops.wm.obj_export(filepath=output_obj, export_selected_objects=True)
print("Successfully exported real-hole upright interlocking pendant to:", output_obj)
