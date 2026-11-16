import bpy
import bmesh
import math
import os

def run():
    print("=== BUILDING 3D WEDDING STAGE MODEL WITH GROUND LAWN ===")

    # 1. Reset Scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 16
    scene.cycles.max_bounces = 3
    scene.cycles.transparent_max_bounces = 4
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200

    base_dir = r"D:\Website\card"
    out_dir = os.path.join(base_dir, "output")
    tex_dir = os.path.join(out_dir, "textures")

    # Path to textures
    ground_tex_path = os.path.join(tex_dir, "ground_lawn.png")
    couple_tex_path = os.path.join(tex_dir, "foreground_cutout_ar.png")
    card_tex_path = os.path.join(tex_dir, "card_front_ar.jpg")

    # ----------------------------------------------------
    # Materials
    # ----------------------------------------------------
    # 1. Champagne Gold Metallic Material
    gold_mat = bpy.data.materials.new(name="ChampagneGold_PBR")
    gold_mat.use_nodes = True
    bsdf_gold = gold_mat.node_tree.nodes.get("Principled BSDF")
    bsdf_gold.inputs['Base Color'].default_value = (0.87, 0.74, 0.48, 1.0)
    bsdf_gold.inputs['Metallic'].default_value = 0.92
    bsdf_gold.inputs['Roughness'].default_value = 0.22

    # 2. Ground Lawn Material (Textured with contact shadow & rose petals)
    ground_mat = bpy.data.materials.new(name="GroundLawn_PBR")
    ground_mat.use_nodes = True
    bsdf_ground = ground_mat.node_tree.nodes.get("Principled BSDF")
    nodes_g = ground_mat.node_tree.nodes
    links_g = ground_mat.node_tree.links

    tex_node_g = nodes_g.new('ShaderNodeTexImage')
    tex_node_g.image = bpy.data.images.load(ground_tex_path)
    links_g.new(tex_node_g.outputs['Color'], bsdf_ground.inputs['Base Color'])
    links_g.new(tex_node_g.outputs['Alpha'], bsdf_ground.inputs['Alpha'])
    bsdf_ground.inputs['Roughness'].default_value = 0.85
    ground_mat.blend_method = 'BLEND'

    # 3. Upright Couple Cutout Material
    couple_mat = bpy.data.materials.new(name="CoupleCutout_PBR")
    couple_mat.use_nodes = True
    bsdf_couple = couple_mat.node_tree.nodes.get("Principled BSDF")
    nodes_c = couple_mat.node_tree.nodes
    links_c = couple_mat.node_tree.links

    tex_node_c = nodes_c.new('ShaderNodeTexImage')
    tex_node_c.image = bpy.data.images.load(couple_tex_path)
    links_c.new(tex_node_c.outputs['Color'], bsdf_couple.inputs['Base Color'])
    links_c.new(tex_node_c.outputs['Alpha'], bsdf_couple.inputs['Alpha'])
    bsdf_couple.inputs['Roughness'].default_value = 0.45
    bsdf_couple.inputs['Specular IOR Level'].default_value = 0.35
    couple_mat.blend_method = 'BLEND'

    # 4. Arch Backdrop Material
    arch_mat = bpy.data.materials.new(name="ArchBackdrop_PBR")
    arch_mat.use_nodes = True
    bsdf_arch = arch_mat.node_tree.nodes.get("Principled BSDF")
    nodes_a = arch_mat.node_tree.nodes
    links_a = arch_mat.node_tree.links

    tex_node_a = nodes_a.new('ShaderNodeTexImage')
    tex_node_a.image = bpy.data.images.load(card_tex_path)
    links_a.new(tex_node_a.outputs['Color'], bsdf_arch.inputs['Base Color'])
    bsdf_arch.inputs['Roughness'].default_value = 0.4
    arch_mat.blend_method = 'OPAQUE'

    # ----------------------------------------------------
    # Geometry 1: Ground Pedestal Base (Horizontal Oval in X-Y plane, Z=0)
    # ----------------------------------------------------
    # In Blender: Z is UP, X is RIGHT, Y is FORWARD
    pedestal_rx = 0.65  # 1.3m wide
    pedestal_ry = 0.45  # 0.9m deep
    pedestal_h = 0.035  # 3.5cm thick base
    segments = 48

    # Create top circular lawn plane
    bm_ground = bmesh.new()
    # Create oval vertices
    verts_top = []
    verts_bottom = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = pedestal_rx * math.cos(angle)
        y = pedestal_ry * math.sin(angle)
        verts_top.append(bm_ground.verts.new((x, y, pedestal_h)))
        verts_bottom.append(bm_ground.verts.new((x, y, 0.0)))

    # Face for top
    top_face = bm_ground.faces.new(verts_top)
    bottom_face = bm_ground.faces.new(reversed(verts_bottom))

    # Side walls
    for i in range(segments):
        next_i = (i + 1) % segments
        bm_ground.faces.new([
            verts_bottom[i],
            verts_bottom[next_i],
            verts_top[next_i],
            verts_top[i]
        ])

    # Assign UVs to top face
    uv_layer = bm_ground.loops.layers.uv.new()
    for loop in top_face.loops:
        v = loop.vert
        # Map x, y to [0, 1]
        u = (v.co.x / (pedestal_rx * 2)) + 0.5
        v_coord = (v.co.y / (pedestal_ry * 2)) + 0.5
        loop[uv_layer].uv = (u, v_coord)

    mesh_ground = bpy.data.meshes.new("Ground_Pedestal_Mesh")
    bm_ground.to_mesh(mesh_ground)
    bm_ground.free()

    obj_ground = bpy.data.objects.new("Ground_Pedestal", mesh_ground)
    bpy.context.collection.objects.link(obj_ground)
    obj_ground.data.materials.append(ground_mat)

    # Gold rim ring around the pedestal
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.55,
        minor_radius=0.018,
        major_segments=48,
        minor_segments=12,
        location=(0, 0, pedestal_h)
    )
    gold_rim = bpy.context.active_object
    gold_rim.name = "Gold_Pedestal_Rim"
    gold_rim.scale = (pedestal_rx / 0.55, pedestal_ry / 0.55, 1.0)
    gold_rim.data.materials.append(gold_mat)

    # ----------------------------------------------------
    # Geometry 2: Upright Couple Standing ON the Ground (Z = pedestal_h)
    # ----------------------------------------------------
    # Height of couple: 1.35m, aspect ratio ~ 2:3 -> width ~ 0.90m
    couple_w = 0.90
    couple_h = 1.35
    couple_z_base = pedestal_h
    couple_y_pos = 0.05  # slightly forward on the pedestal

    bm_couple = bmesh.new()
    # 4 vertices for upright standing plane
    v_bl = bm_couple.verts.new((-couple_w / 2, couple_y_pos, couple_z_base))
    v_br = bm_couple.verts.new((couple_w / 2, couple_y_pos, couple_z_base))
    v_tr = bm_couple.verts.new((couple_w / 2, couple_y_pos, couple_z_base + couple_h))
    v_tl = bm_couple.verts.new((-couple_w / 2, couple_y_pos, couple_z_base + couple_h))

    face_couple = bm_couple.faces.new([v_bl, v_br, v_tr, v_tl])

    uv_layer_c = bm_couple.loops.layers.uv.new()
    # Map full image
    face_couple.loops[0][uv_layer_c].uv = (0.0, 0.0)
    face_couple.loops[1][uv_layer_c].uv = (1.0, 0.0)
    face_couple.loops[2][uv_layer_c].uv = (1.0, 1.0)
    face_couple.loops[3][uv_layer_c].uv = (0.0, 1.0)

    mesh_couple = bpy.data.meshes.new("Standing_Couple_Mesh")
    bm_couple.to_mesh(mesh_couple)
    bm_couple.free()

    obj_couple = bpy.data.objects.new("Standing_Couple_3D", mesh_couple)
    bpy.context.collection.objects.link(obj_couple)
    obj_couple.data.materials.append(couple_mat)

    # ----------------------------------------------------
    # Geometry 3: Floral Arch Backdrop Standing Behind Couple
    # ----------------------------------------------------
    # Placed at Y = -0.18m (18cm behind the couple)
    arch_w = 1.05
    arch_h = 1.48
    arch_y_pos = -0.18
    arch_z_base = pedestal_h

    bm_arch = bmesh.new()
    va_bl = bm_arch.verts.new((-arch_w / 2, arch_y_pos, arch_z_base))
    va_br = bm_arch.verts.new((arch_w / 2, arch_y_pos, arch_z_base))
    va_tr = bm_arch.verts.new((arch_w / 2, arch_y_pos, arch_z_base + arch_h))
    va_tl = bm_arch.verts.new((-arch_w / 2, arch_y_pos, arch_z_base + arch_h))

    face_arch = bm_arch.faces.new([va_bl, va_br, va_tr, va_tl])
    uv_layer_a = bm_arch.loops.layers.uv.new()
    face_arch.loops[0][uv_layer_a].uv = (0.0, 0.0)
    face_arch.loops[1][uv_layer_a].uv = (1.0, 0.0)
    face_arch.loops[2][uv_layer_a].uv = (1.0, 1.0)
    face_arch.loops[3][uv_layer_a].uv = (0.0, 1.0)

    mesh_arch = bpy.data.meshes.new("Arch_Backdrop_Mesh")
    bm_arch.to_mesh(mesh_arch)
    bm_arch.free()

    obj_arch = bpy.data.objects.new("Floral_Arch_Backdrop", mesh_arch)
    bpy.context.collection.objects.link(obj_arch)
    obj_arch.data.materials.append(arch_mat)

    # Gold frame border for the arch backdrop
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0, arch_y_pos - 0.008, arch_z_base + arch_h / 2)
    )
    arch_backing = bpy.context.active_object
    arch_backing.name = "Arch_Gold_Backing"
    arch_backing.scale = (arch_w + 0.04, 0.012, arch_h + 0.04)
    arch_backing.data.materials.append(gold_mat)

    # ----------------------------------------------------
    # Center Scene Origin
    # ----------------------------------------------------
    # Shift scene so the center of gravity / eye-level is at world origin
    center_offset_z = -(pedestal_h + couple_h * 0.45)
    for obj in [obj_ground, gold_rim, obj_couple, obj_arch, arch_backing]:
        obj.location.z += center_offset_z

    # ----------------------------------------------------
    # Studio Lighting Setup
    # ----------------------------------------------------
    # Key Light (Warm soft sunlight)
    light_key = bpy.data.lights.new(name="Light_SunKey", type='POINT')
    light_key.energy = 450
    light_key.color = (1.0, 0.96, 0.90)
    light_key.shadow_soft_size = 0.25
    obj_lkey = bpy.data.objects.new("Light_Key", light_key)
    obj_lkey.location = (1.4, 1.8, 1.5)
    bpy.context.collection.objects.link(obj_lkey)

    # Fill Light (Cool ambient soft garden light)
    light_fill = bpy.data.lights.new(name="Light_Fill", type='POINT')
    light_fill.energy = 220
    light_fill.color = (0.92, 0.95, 1.0)
    light_fill.shadow_soft_size = 0.4
    obj_lfill = bpy.data.objects.new("Light_Fill", light_fill)
    obj_lfill.location = (-1.5, 1.5, 1.0)
    bpy.context.collection.objects.link(obj_lfill)

    # Rim Light (Champagne gold rim highlight)
    light_rim = bpy.data.lights.new(name="Light_Rim", type='POINT')
    light_rim.energy = 300
    light_rim.color = (1.0, 0.88, 0.70)
    obj_lrim = bpy.data.objects.new("Light_Rim", light_rim)
    obj_lrim.location = (0.0, -1.8, 1.2)
    bpy.context.collection.objects.link(obj_lrim)

    # ----------------------------------------------------
    # Camera Setup & Render
    # ----------------------------------------------------
    # 3D Perspective Angle Camera (shows the ground, depth, and pop-out)
    cam_angle_data = bpy.data.cameras.new("Cam_3D_Angle")
    cam_angle_data.lens = 48
    cam_angle_obj = bpy.data.objects.new("Camera_3D_Angle", cam_angle_data)
    # Position camera looking down at 25 degrees from a 30-degree azimuth
    cam_angle_obj.location = (1.2, 2.2, 0.6)
    # Point at (0, 0, 0)
    cam_angle_obj.rotation_euler = (math.radians(75), math.radians(0), math.radians(28))
    bpy.context.collection.objects.link(cam_angle_obj)

    scene.camera = cam_angle_obj

    # ----------------------------------------------------
    # Export GLB Model
    # ----------------------------------------------------
    out_glb = os.path.join(out_dir, "vandan_riddhi_stage_3D_AR.glb")
    print(f"Exporting 3D Ground Stage GLB to {out_glb}...")
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_materials='EXPORT',
        export_image_format='JPEG',
        export_jpeg_quality=92,
        export_cameras=False,
        export_lights=False
    )
    print(f"GLB exported! Size: {os.path.getsize(out_glb):,} bytes")

    # Save Blend file
    out_blend = os.path.join(out_dir, "vandan_riddhi_stage_3D_AR.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print(f"Blend file saved to {out_blend}")

    # Render Preview
    render_out = os.path.join(out_dir, "vandan_riddhi_stage_render_angle.png")
    scene.render.filepath = render_out
    bpy.ops.render.render(write_still=True)
    print(f"Render saved to {render_out}")

if __name__ == '__main__':
    run()
