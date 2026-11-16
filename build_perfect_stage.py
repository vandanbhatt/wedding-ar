import bpy
import bmesh
import math
import os

def build_perfect_stage():
    print("=== BUILDING PERFECT 3D WEDDING STAGE WITH PURE GRASS & CLEAR DATE ===")

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

    # Texture paths
    grass_tex_path = os.path.join(tex_dir, "ground_pure_grass.png")
    couple_tex_path = os.path.join(tex_dir, "foreground_cutout_ar.png")
    card_tex_path = os.path.join(tex_dir, "card_stage_backdrop.jpg")
    plaque_tex_path = os.path.join(tex_dir, "stage_gold_plaque.png")

    # ----------------------------------------------------
    # Dedicated Materials with UNIQUE image data-blocks
    # ----------------------------------------------------
    # 1. Champagne Gold Metallic PBR
    gold_mat = bpy.data.materials.new(name="Mat_ChampagneGold")
    bsdf_gold = gold_mat.node_tree.nodes.get("Principled BSDF")
    bsdf_gold.inputs['Base Color'].default_value = (0.88, 0.76, 0.50, 1.0)
    bsdf_gold.inputs['Metallic'].default_value = 0.94
    bsdf_gold.inputs['Roughness'].default_value = 0.20

    # 2. Pure Green Grass Lawn Material
    grass_mat = bpy.data.materials.new(name="Mat_PureGrassLawn")
    bsdf_grass = grass_mat.node_tree.nodes.get("Principled BSDF")
    img_grass = bpy.data.images.load(grass_tex_path)
    img_grass.name = "Texture_PureGrass_Lawn"
    tex_grass = grass_mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_grass.image = img_grass
    grass_mat.node_tree.links.new(tex_grass.outputs['Color'], bsdf_grass.inputs['Base Color'])
    grass_mat.node_tree.links.new(tex_grass.outputs['Alpha'], bsdf_grass.inputs['Alpha'])
    bsdf_grass.inputs['Roughness'].default_value = 0.85
    grass_mat.blend_method = 'BLEND'

    # 3. Couple Cutout Material (100% original face & outfit pixels)
    couple_mat = bpy.data.materials.new(name="Mat_CoupleCutout")
    bsdf_couple = couple_mat.node_tree.nodes.get("Principled BSDF")
    img_couple = bpy.data.images.load(couple_tex_path)
    img_couple.name = "Texture_Couple_Cutout_AR"
    tex_couple = couple_mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_couple.image = img_couple
    couple_mat.node_tree.links.new(tex_couple.outputs['Color'], bsdf_couple.inputs['Base Color'])
    couple_mat.node_tree.links.new(tex_couple.outputs['Alpha'], bsdf_couple.inputs['Alpha'])
    bsdf_couple.inputs['Roughness'].default_value = 0.45
    bsdf_couple.inputs['Specular IOR Level'].default_value = 0.35
    couple_mat.blend_method = 'BLEND'

    # 4. Card Backdrop Material (Unmirrored, clean garden arch, clear wedding date)
    card_mat = bpy.data.materials.new(name="Mat_CardBackdrop")
    bsdf_card = card_mat.node_tree.nodes.get("Principled BSDF")
    img_card = bpy.data.images.load(card_tex_path)
    img_card.name = "Texture_Card_Backdrop_Clean"
    tex_card = card_mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_card.image = img_card
    card_mat.node_tree.links.new(tex_card.outputs['Color'], bsdf_card.inputs['Base Color'])
    bsdf_card.inputs['Roughness'].default_value = 0.40
    card_mat.blend_method = 'OPAQUE'

    # 5. Front Gold Plaque Material (Names & Date engraved)
    plaque_mat = bpy.data.materials.new(name="Mat_GoldPlaque")
    bsdf_plaque = plaque_mat.node_tree.nodes.get("Principled BSDF")
    img_plaque = bpy.data.images.load(plaque_tex_path)
    img_plaque.name = "Texture_Gold_Plaque"
    tex_plaque = plaque_mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_plaque.image = img_plaque
    plaque_mat.node_tree.links.new(tex_plaque.outputs['Color'], bsdf_plaque.inputs['Base Color'])
    plaque_mat.node_tree.links.new(tex_plaque.outputs['Alpha'], bsdf_plaque.inputs['Alpha'])
    bsdf_plaque.inputs['Metallic'].default_value = 0.75
    bsdf_plaque.inputs['Roughness'].default_value = 0.28
    plaque_mat.blend_method = 'BLEND'

    # ----------------------------------------------------
    # Geometry 1: Ground Pedestal Base (Horizontal Oval)
    # ----------------------------------------------------
    pedestal_rx = 0.65  # 1.30m wide
    pedestal_ry = 0.48  # 0.96m deep
    pedestal_h = 0.035  # 3.5cm thick base
    segments = 48

    bm_ground = bmesh.new()
    verts_top = []
    verts_bottom = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = pedestal_rx * math.cos(angle)
        y = pedestal_ry * math.sin(angle)
        verts_top.append(bm_ground.verts.new((x, y, pedestal_h)))
        verts_bottom.append(bm_ground.verts.new((x, y, 0.0)))

    # Top lawn face
    top_face = bm_ground.faces.new(verts_top)
    # Bottom face
    bottom_face = bm_ground.faces.new(reversed(verts_bottom))

    # Side walls
    side_faces = []
    for i in range(segments):
        next_i = (i + 1) % segments
        sf = bm_ground.faces.new([
            verts_bottom[i],
            verts_bottom[next_i],
            verts_top[next_i],
            verts_top[i]
        ])
        side_faces.append(sf)

    # UV Mapping for top grass face
    uv_layer_g = bm_ground.loops.layers.uv.new()
    for loop in top_face.loops:
        v = loop.vert
        u = (v.co.x / (pedestal_rx * 2)) + 0.5
        v_coord = (v.co.y / (pedestal_ry * 2)) + 0.5
        loop[uv_layer_g].uv = (u, v_coord)

    # Assign material slot 0 (Grass) to top face, material slot 1 (Gold) to sides/bottom
    top_face.material_index = 0
    bottom_face.material_index = 1
    for sf in side_faces:
        sf.material_index = 1

    mesh_ground = bpy.data.meshes.new("Ground_Pedestal_Mesh")
    bm_ground.to_mesh(mesh_ground)
    bm_ground.free()

    obj_ground = bpy.data.objects.new("Ground_Pedestal", mesh_ground)
    bpy.context.collection.objects.link(obj_ground)
    obj_ground.data.materials.append(grass_mat) # Slot 0: Grass
    obj_ground.data.materials.append(gold_mat)  # Slot 1: Gold rim

    # Champagne Gold Outer Ring around pedestal
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
    # Geometry 2: Upright Couple Standing on the Lawn
    # ----------------------------------------------------
    couple_w = 0.88
    couple_h = 1.32
    couple_z_base = pedestal_h
    couple_y_pos = 0.04

    bm_c = bmesh.new()
    # Correct winding order so normal points +Y (towards camera)
    # When viewed from +Y looking at -Y: Left is -X, Right is +X, Bottom is Z, Top is Z+H
    # Counter-clockwise from front: BR -> BL -> TL -> TR
    vc_br = bm_c.verts.new((couple_w / 2, couple_y_pos, couple_z_base))
    vc_bl = bm_c.verts.new((-couple_w / 2, couple_y_pos, couple_z_base))
    vc_tl = bm_c.verts.new((-couple_w / 2, couple_y_pos, couple_z_base + couple_h))
    vc_tr = bm_c.verts.new((couple_w / 2, couple_y_pos, couple_z_base + couple_h))

    face_c = bm_c.faces.new([vc_br, vc_bl, vc_tl, vc_tr])
    uv_c = bm_c.loops.layers.uv.new()
    face_c.loops[0][uv_c].uv = (1.0, 0.0) # BR
    face_c.loops[1][uv_c].uv = (0.0, 0.0) # BL
    face_c.loops[2][uv_c].uv = (0.0, 1.0) # TL
    face_c.loops[3][uv_c].uv = (1.0, 1.0) # TR

    mesh_c = bpy.data.meshes.new("Couple_Mesh")
    bm_c.to_mesh(mesh_c)
    bm_c.free()

    obj_couple = bpy.data.objects.new("Standing_Couple", mesh_c)
    bpy.context.collection.objects.link(obj_couple)
    obj_couple.data.materials.append(couple_mat)

    # ----------------------------------------------------
    # Geometry 3: Floral Arch Backdrop (100% UNMIRRORED)
    # ----------------------------------------------------
    # Card aspect ratio: 726 x 1024 -> 1.08m wide x 1.52m tall
    arch_w = 1.08
    arch_h = 1.52
    arch_y_pos = -0.16
    arch_z_base = pedestal_h + 0.02

    bm_a = bmesh.new()
    # Counter-clockwise from front: BR -> BL -> TL -> TR
    va_br = bm_a.verts.new((arch_w / 2, arch_y_pos, arch_z_base))
    va_bl = bm_a.verts.new((-arch_w / 2, arch_y_pos, arch_z_base))
    va_tl = bm_a.verts.new((-arch_w / 2, arch_y_pos, arch_z_base + arch_h))
    va_tr = bm_a.verts.new((arch_w / 2, arch_y_pos, arch_z_base + arch_h))

    face_a = bm_a.faces.new([va_br, va_bl, va_tl, va_tr])
    uv_a = bm_a.loops.layers.uv.new()
    face_a.loops[0][uv_a].uv = (1.0, 0.0) # BR
    face_a.loops[1][uv_a].uv = (0.0, 0.0) # BL
    face_a.loops[2][uv_a].uv = (0.0, 1.0) # TL
    face_a.loops[3][uv_a].uv = (1.0, 1.0) # TR

    mesh_a = bpy.data.meshes.new("Card_Backdrop_Mesh")
    bm_a.to_mesh(mesh_a)
    bm_a.free()

    obj_arch = bpy.data.objects.new("Card_Backdrop", mesh_a)
    bpy.context.collection.objects.link(obj_arch)
    obj_arch.data.materials.append(card_mat)

    # Gold Backing for Arch Card
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0, arch_y_pos - 0.007, arch_z_base + arch_h / 2)
    )
    arch_backing = bpy.context.active_object
    arch_backing.name = "Arch_Gold_Backing"
    arch_backing.scale = (arch_w + 0.03, 0.010, arch_h + 0.03)
    arch_backing.data.materials.append(gold_mat)

    # ----------------------------------------------------
    # Geometry 4: 3D Champagne Gold Plaque on Front of Pedestal
    # (Shows "Vandan & Riddhi" and "29 . 12 . 2027" in full view)
    # ----------------------------------------------------
    plaque_w = 0.48
    plaque_h = 0.15
    plaque_y = pedestal_ry * 0.92  # near front edge of pedestal
    plaque_z = pedestal_h + 0.02
    plaque_tilt = math.radians(22) # tilted 22 deg for perfect camera reading

    bm_p = bmesh.new()
    # Build inclined quad
    vp_br = bm_p.verts.new((plaque_w / 2, plaque_y, plaque_z))
    vp_bl = bm_p.verts.new((-plaque_w / 2, plaque_y, plaque_z))
    vp_tl = bm_p.verts.new((-plaque_w / 2, plaque_y - plaque_h * math.sin(plaque_tilt), plaque_z + plaque_h * math.cos(plaque_tilt)))
    vp_tr = bm_p.verts.new((plaque_w / 2, plaque_y - plaque_h * math.sin(plaque_tilt), plaque_z + plaque_h * math.cos(plaque_tilt)))

    face_p = bm_p.faces.new([vp_br, vp_bl, vp_tl, vp_tr])
    uv_p = bm_p.loops.layers.uv.new()
    face_p.loops[0][uv_p].uv = (1.0, 0.0) # BR
    face_p.loops[1][uv_p].uv = (0.0, 0.0) # BL
    face_p.loops[2][uv_p].uv = (0.0, 1.0) # TL
    face_p.loops[3][uv_p].uv = (1.0, 1.0) # TR

    mesh_p = bpy.data.meshes.new("Gold_Plaque_Mesh")
    bm_p.to_mesh(mesh_p)
    bm_p.free()

    obj_plaque = bpy.data.objects.new("Front_Gold_Plaque", mesh_p)
    bpy.context.collection.objects.link(obj_plaque)
    obj_plaque.data.materials.append(plaque_mat)

    # ----------------------------------------------------
    # Center Scene Origin
    # ----------------------------------------------------
    center_offset_z = -(pedestal_h + couple_h * 0.45)
    for obj in [obj_ground, gold_rim, obj_couple, obj_arch, arch_backing, obj_plaque]:
        obj.location.z += center_offset_z

    # ----------------------------------------------------
    # Studio Lighting Setup
    # ----------------------------------------------------
    light_key = bpy.data.lights.new(name="Light_SunKey", type='POINT')
    light_key.energy = 450
    light_key.color = (1.0, 0.96, 0.90)
    light_key.shadow_soft_size = 0.25
    obj_lkey = bpy.data.objects.new("Light_Key", light_key)
    obj_lkey.location = (1.4, 2.0, 1.5)
    bpy.context.collection.objects.link(obj_lkey)

    light_fill = bpy.data.lights.new(name="Light_Fill", type='POINT')
    light_fill.energy = 250
    light_fill.color = (0.92, 0.95, 1.0)
    light_fill.shadow_soft_size = 0.4
    obj_lfill = bpy.data.objects.new("Light_Fill", light_fill)
    obj_lfill.location = (-1.5, 1.6, 1.0)
    bpy.context.collection.objects.link(obj_lfill)

    light_rim = bpy.data.lights.new(name="Light_Rim", type='POINT')
    light_rim.energy = 320
    light_rim.color = (1.0, 0.88, 0.70)
    obj_lrim = bpy.data.objects.new("Light_Rim", light_rim)
    obj_lrim.location = (0.0, -1.8, 1.2)
    bpy.context.collection.objects.link(obj_lrim)

    # ----------------------------------------------------
    # Perspective Camera for Render
    # ----------------------------------------------------
    cam_data = bpy.data.cameras.new("Cam_Preview")
    cam_data.lens = 48
    cam_obj = bpy.data.objects.new("Camera_Preview", cam_data)
    cam_obj.location = (0.8, 2.4, 0.5)
    cam_obj.rotation_euler = (math.radians(78), math.radians(0), math.radians(18))
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # ----------------------------------------------------
    # Export glTF / GLB with AUTO format (preserves PNG alpha)
    # ----------------------------------------------------
    out_glb = os.path.join(out_dir, "vandan_riddhi_stage_3D_AR.glb")
    print(f"Exporting GLB to {out_glb}...")
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_materials='EXPORT',
        export_image_format='AUTO',
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
    build_perfect_stage()
