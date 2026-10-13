import bpy
import os
import math
import mathutils

def render_showcase():
    curr_dir = r"c:\KIRTSOY_CORE\AI_PROGRAMS\LOGO"
    obj_path = os.path.join(curr_dir, "assets", "kirtsoy_pendant_real_hole.obj")
    output_png = os.path.join(curr_dir, "pendant_upright_chain_showcase.png")

    bpy.ops.wm.read_factory_settings(use_empty=True)

    world = bpy.data.worlds.new('World')
    bpy.context.scene.world = world

    # 1. Import baked upright pendant
    bpy.ops.wm.obj_import(filepath=obj_path)
    pendant = bpy.context.selected_objects[0]
    pendant.name = "Pendant"

    # Smooth shading
    for poly in pendant.data.polygons:
        poly.use_smooth = True

    # 2. Luxury Gold Material
    mat_gold = bpy.data.materials.new(name="Gold")
    bsdf = mat_gold.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.95, 0.78, 0.3, 1.0)
        bsdf.inputs['Metallic'].default_value = 1.0
        bsdf.inputs['Roughness'].default_value = 0.12

    pendant.data.materials.clear()
    pendant.data.materials.append(mat_gold)

    # 3. Create Chain threading through the lateral tunnel in 't'
    # Coordinates in Blender world:
    # Crossbar hole center: X = -5.74, Y = 0, Z = 18.51
    hole_x = -5.74
    hole_z = 18.51

    curve_data = bpy.data.curves.new('ChainPath', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 32
    curve_data.bevel_depth = 1.35
    curve_data.bevel_resolution = 8

    polyline = curve_data.splines.new('BEZIER')
    points_data = [
        (-80.0, -30.0, hole_z + 40.0),
        (-42.0, -15.0, hole_z + 18.0),
        (-20.0, -5.0, hole_z + 3.0),
        (-11.29, 0.0, hole_z),       # Enters left side of crossbar
        (hole_x, 0.0, hole_z),       # Inside hole in 't'
        (-0.19, 0.0, hole_z),        # Exits right side of crossbar
        (15.0, -5.0, hole_z + 3.0),
        (38.0, -15.0, hole_z + 18.0),
        (75.0, -30.0, hole_z + 40.0)
    ]

    polyline.bezier_points.add(len(points_data) - 1)
    for i, pt in enumerate(points_data):
        bp = polyline.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'

    chain_obj = bpy.data.objects.new('NecklaceChain', curve_data)
    bpy.context.collection.objects.link(chain_obj)
    chain_obj.data.materials.append(mat_gold)

    # 4. Sun & Fill Lighting
    key_light_data = bpy.data.lights.new('KeySun', type='SUN')
    key_light_data.energy = 4.5
    key_obj = bpy.data.objects.new('KeySun', key_light_data)
    bpy.context.collection.objects.link(key_obj)
    key_obj.location = (20.0, -50.0, 40.0)
    key_obj.rotation_euler = (0.6, 0.3, 0.2)

    rim_light_data = bpy.data.lights.new('RimSun', type='SUN')
    rim_light_data.energy = 2.5
    rim_obj = bpy.data.objects.new('RimSun', rim_light_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (-40.0, 50.0, 30.0)
    rim_obj.rotation_euler = (-0.7, -0.2, 2.5)

    # 5. Camera (Slight angle to see the chain looping through the hole)
    cam_data = bpy.data.cameras.new('MainCamera')
    cam = bpy.data.objects.new('MainCamera', cam_data)
    bpy.context.collection.objects.link(cam)
    # Camera placed at slight perspective angle
    cam.location = (0.0, -210.0, 18.0)
    direction = mathutils.Vector((0, 0, 5.0)) - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam

    # 6. Render Settings
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.filepath = output_png
    bpy.context.scene.render.image_settings.file_format = 'PNG'

    print("Rendering...")
    bpy.ops.render.render(write_still=True)
    print("Showcase rendered to:", output_png)

if __name__ == "__main__":
    render_showcase()
