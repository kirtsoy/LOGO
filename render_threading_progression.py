import bpy
import os
import math
import mathutils

def render_threading_steps():
    curr_dir = r"c:\KIRTSOY_CORE\AI_PROGRAMS\LOGO"
    obj_path = os.path.join(curr_dir, "assets", "kirtsoy_pendant_real_hole.obj")

    # Three key moments to demonstrate:
    # 1. Approach: Tip flies in from top-left towards 't'
    # 2. Piercing: Tip threads straight through the hole in 't'
    # 3. Settled: Full chain threaded and locked in
    steps = [
        {"name": "step1_approach.png", "progress": 0.35, "desc": "1. Конец цепи подлетает к 't'"},
        {"name": "step2_piercing_hole.png", "progress": 0.65, "desc": "2. Конец цепи просовывается сквозь дырку в 't'"},
        {"name": "step3_settled_full.png", "progress": 1.00, "desc": "3. Цепь полностью продета и зафиксирована"}
    ]

    for step in steps:
        bpy.ops.wm.read_factory_settings(use_empty=True)

        world = bpy.data.worlds.new('World')
        bpy.context.scene.world = world

        # 1. Import baked upright pendant
        bpy.ops.wm.obj_import(filepath=obj_path)
        pendant = bpy.context.selected_objects[0]
        pendant.name = "Pendant"

        for poly in pendant.data.polygons:
            poly.use_smooth = True

        # Gold material
        mat_gold = bpy.data.materials.new(name="Gold")
        bsdf = mat_gold.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.95, 0.78, 0.3, 1.0)
            bsdf.inputs['Metallic'].default_value = 1.0
            bsdf.inputs['Roughness'].default_value = 0.12

        pendant.data.materials.clear()
        pendant.data.materials.append(mat_gold)

        # 2. Build 11-point path
        hole_x = -5.74
        hole_z = 18.51

        points_data = [
            (-145.74, -50.0, hole_z + 110.0),
            (-80.74, -26.0, hole_z + 55.0),
            (-43.74, -12.0, hole_z + 22.0),
            (-21.29, -2.0, hole_z + 2.5),
            (-11.29, 0.0, hole_z),
            (hole_x, 0.0, hole_z),
            (-0.19, 0.0, hole_z),
            (9.81, -2.0, hole_z + 2.5),
            (32.26, -12.0, hole_z + 22.0),
            (69.26, -26.0, hole_z + 55.0),
            (134.26, -50.0, hole_z + 110.0)
        ]

        # Calculate curve & points for this progress level
        p = step['progress']
        # Total points in spline proportional to progress
        # At p=0.35: starts at pt 1 down to pt 3
        # At p=0.65: starts at pt 1 down through pt 4, 5, 6, 7
        # At p=1.00: spans pt 1 to pt 9
        t_settled_start_idx = 1
        t_settled_end_idx = 9

        # Fractional points
        start_idx = max(0, int(round(1 + (1.0 - p) * 1.5)))
        # Head index advances from 2 to 9
        head_idx = min(len(points_data) - 1, int(round(3 + p * 6)))

        active_pts = points_data[start_idx : head_idx + 1]
        if len(active_pts) < 2:
            active_pts = points_data[1:3]

        curve_data = bpy.data.curves.new('ChainPath', type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.resolution_u = 32
        curve_data.bevel_depth = 1.35
        curve_data.bevel_resolution = 8

        polyline = curve_data.splines.new('BEZIER')
        polyline.bezier_points.add(len(active_pts) - 1)
        for i, pt in enumerate(active_pts):
            bp = polyline.bezier_points[i]
            bp.co = pt
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'

        chain_obj = bpy.data.objects.new('NecklaceChain', curve_data)
        bpy.context.collection.objects.link(chain_obj)
        chain_obj.data.materials.append(mat_gold)

        # 3. Lighting
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

        # Camera
        cam_data = bpy.data.cameras.new('MainCamera')
        cam = bpy.data.objects.new('MainCamera', cam_data)
        bpy.context.collection.objects.link(cam)
        cam.location = (0.0, -210.0, 18.0)
        direction = mathutils.Vector((0, 0, 5.0)) - cam.location
        cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        bpy.context.scene.camera = cam

        # Render
        out_file = os.path.join(curr_dir, step['name'])
        bpy.context.scene.render.resolution_x = 1280
        bpy.context.scene.render.resolution_y = 720
        bpy.context.scene.render.filepath = out_file
        bpy.context.scene.render.image_settings.file_format = 'PNG'

        bpy.ops.render.render(write_still=True)
        print("Rendered:", out_file)

if __name__ == "__main__":
    render_threading_steps()
