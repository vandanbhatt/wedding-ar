import bpy
import bmesh
import math
import os
import shutil

def build_flawless_stage():
    print("=== BUILDING FLAWLESS 3D WEDDING STAGE MODEL ===")

    # 1. Reset Scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    base_dir = r"D:\Website\card"
    out_dir = os.path.join(base_dir, "output")
    tex_dir = os.path.join(out_dir, "textures")

    grass_tex_path = os.path.join(tex_dir, "ground_pure_grass.png")
    couple_tex_path = os.path.join(tex_dir, "foreground_cutout_ar.png")
    card_tex_path = os.path.join(tex_dir, "card_stage_backdrop.jpg")
    plaque_tex_path = os.path.join(tex_dir, "stage_gold_plaque.png")

    # ----------------------------------------------------
    # Dedicated, 100% Isolated Materials
    # ----------------------------------------------------
    # 1. Champagne Gold Metallic PBR
    gold_mat = bpy.data.materials.new(name="Mat_ChampagneGold")
    bsdf_gold = gold_mat.node_tree.nodes.get("Principled BSDF")
    bsdf_gold.inputs['Base Color'].default_value = (0.88, 0.76, 0.50, 1.0)
    bsdf_gold.inputs['Metallic'].default_value = 0.94
    bsdf_gold.inputs['Roughness'].default_value = 0.20

    # 2. Pure Green Grass Lawn Material (Single texture, single mesh)
    grass_mat = bpy.data.materials.new(name="Mat_PureGrassLawn")
    bsdf_grass = grass_mat.node_tree.nodes.get("Principled BSDF")
    img_grass = bpy.data.images.load(grass_tex_path)
    img_grass.name = "Texture_Grass_Pure"
    tex_grass = grass_mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_grass.image = img_grass
    grass_mat.node_tree.links.new(tex_grass.outputs['Color'], bsdf_grass.inputs['Base Color'])
    grass_mat.node_tree.links.new(tex_grass.outputs['Alpha'], bsdf_grass.inputs['Alpha'])
    bsdf_grass.inputs['Roughness'].default_value = 0.85
    grass_mat.blend_method = 'BLEND'

    # 3. Couple Cutout Material
    couple_mat = bpy.data.materials.new(name="Mat_CoupleCutout")
    bsdf_couple = couple_mat.node_tree.nodes.get("Principled BSDF")
    img_couple = bpy.data.images.load(couple_tex_path)
    img_couple.name = "Texture_Couple_AR"
    tex_couple = couple_mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_couple.image = img_couple
    couple_mat.node_tree.links.new(tex_couple.outputs['Color'], bsdf_couple.inputs['Base Color'])
    couple_mat.node_tree.links.new(tex_couple.outputs['Alpha'], bsdf_couple.inputs['Alpha'])
    bsdf_couple.inputs['Roughness'].default_value = 0.45
    bsdf_couple.inputs['Specular IOR Level'].default_value = 0.35
    couple_mat.blend_method = 'BLEND'

    # 4. Card Backdrop Material
    card_mat = bpy.data.materials.new(name="Mat_CardBackdrop")
    bsdf_card = card_mat.node_tree.nodes.get("Principled BSDF")
    img_card = bpy.data.images.load(card_tex_path)
    img_card.name = "Texture_Card_CleanArch"
    tex_card = card_mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_card.image = img_card
    card_mat.node_tree.links.new(tex_card.outputs['Color'], bsdf_card.inputs['Base Color'])
    bsdf_card.inputs['Roughness'].default_value = 0.40
    card_mat.blend_method = 'OPAQUE'

    # 5. Front Gold Plaque Material
    plaque_mat = bpy.data.materials.new(name="Mat_GoldPlaque")
    bsdf_plaque = plaque_mat.node_tree.nodes.get("Principled BSDF")
    img_plaque = bpy.data.images.load(plaque_tex_path)
    img_plaque.name = "Texture_Plaque_Text"
    tex_plaque = plaque_mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_plaque.image = img_plaque
    plaque_mat.node_tree.links.new(tex_plaque.outputs['Color'], bsdf_plaque.inputs['Base Color'])
    plaque_mat.node_tree.links.new(tex_plaque.outputs['Alpha'], bsdf_plaque.inputs['Alpha'])
    bsdf_plaque.inputs['Metallic'].default_value = 0.85
    bsdf_plaque.inputs['Roughness'].default_value = 0.22
    plaque_mat.blend_method = 'BLEND'

    # ----------------------------------------------------
    # Geometry 1A: Ground Lawn (Standalone Mesh for 100% Grass)
    # ----------------------------------------------------
    pedestal_rx = 0.65  # 1.30m wide
    pedestal_ry = 0.48  # 0.96m deep
    pedestal_h = 0.035  # 3.5cm thick base
    segments = 64

    bm_lawn = bmesh.new()
    verts_top = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = pedestal_rx * math.cos(angle)
        y = pedestal_ry * math.sin(angle)
        verts_top.append(bm_lawn.verts.new((x, y, pedestal_h + 0.001))) # slight offset above base

    top_face = bm_lawn.faces.new(verts_top)
    uv_lawn = bm_lawn.loops.layers.uv.new()
    for loop in top_face.loops:
        v = loop.vert
        u = (v.co.x / (pedestal_rx * 2)) + 0.5
        v_coord = (-v.co.y / (pedestal_ry * 2)) + 0.5
        loop[uv_lawn].uv = (u, v_coord)

    mesh_lawn = bpy.data.meshes.new("Lawn_Mesh")
    bm_lawn.to_mesh(mesh_lawn)
    bm_lawn.free()

    obj_lawn = bpy.data.objects.new("Ground_Lawn", mesh_lawn)
    bpy.context.collection.objects.link(obj_lawn)
    obj_lawn.data.materials.append(grass_mat)

    # ----------------------------------------------------
    # Geometry 1B: Ground Pedestal Gold Base (Standalone Solid Mesh)
    # ----------------------------------------------------
    bm_base = bmesh.new()
    vb_top = []
    vb_bot = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = pedestal_rx * math.cos(angle)
        y = pedestal_ry * math.sin(angle)
        vb_top.append(bm_base.verts.new((x, y, pedestal_h)))
        vb_bot.append(bm_base.verts.new((x, y, 0.0)))

    bm_base.faces.new(vb_top)
    bm_base.faces.new(reversed(vb_bot))
    for i in range(segments):
        next_i = (i + 1) % segments
        bm_base.faces.new([vb_bot[i], vb_bot[next_i], vb_top[next_i], vb_top[i]])

    mesh_base = bpy.data.meshes.new("Pedestal_Base_Mesh")
    bm_base.to_mesh(mesh_base)
    bm_base.free()

    obj_base = bpy.data.objects.new("Pedestal_Gold_Base", mesh_base)
    bpy.context.collection.objects.link(obj_base)
    obj_base.data.materials.append(gold_mat)

    # Gold Torus Rim
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
    # Geometry 2: Standing Couple (Facing -Y towards front camera)
    # ----------------------------------------------------
    couple_w = 0.88
    couple_h = 1.32
    couple_z_base = pedestal_h + 0.002
    couple_y_pos = -0.04

    bm_c = bmesh.new()
    vc_bl = bm_c.verts.new((-couple_w / 2, couple_y_pos, couple_z_base))
    vc_br = bm_c.verts.new((couple_w / 2, couple_y_pos, couple_z_base))
    vc_tr = bm_c.verts.new((couple_w / 2, couple_y_pos, couple_z_base + couple_h))
    vc_tl = bm_c.verts.new((-couple_w / 2, couple_y_pos, couple_z_base + couple_h))

    face_c = bm_c.faces.new([vc_bl, vc_br, vc_tr, vc_tl])
    uv_c = bm_c.loops.layers.uv.new()
    face_c.loops[0][uv_c].uv = (0.0, 0.0) # BL
    face_c.loops[1][uv_c].uv = (1.0, 0.0) # BR
    face_c.loops[2][uv_c].uv = (1.0, 1.0) # TR
    face_c.loops[3][uv_c].uv = (0.0, 1.0) # TL

    mesh_c = bpy.data.meshes.new("Couple_Mesh")
    bm_c.to_mesh(mesh_c)
    bm_c.free()

    obj_couple = bpy.data.objects.new("Standing_Couple", mesh_c)
    bpy.context.collection.objects.link(obj_couple)
    obj_couple.data.materials.append(couple_mat)

    # ----------------------------------------------------
    # Geometry 3: Floral Arch Backdrop (Facing -Y towards front camera)
    # ----------------------------------------------------
    arch_w = 1.08
    arch_h = 1.52
    arch_y_pos = 0.16
    arch_z_base = pedestal_h + 0.02

    bm_a = bmesh.new()
    va_bl = bm_a.verts.new((-arch_w / 2, arch_y_pos, arch_z_base))
    va_br = bm_a.verts.new((arch_w / 2, arch_y_pos, arch_z_base))
    va_tr = bm_a.verts.new((arch_w / 2, arch_y_pos, arch_z_base + arch_h))
    va_tl = bm_a.verts.new((-arch_w / 2, arch_y_pos, arch_z_base + arch_h))

    face_a = bm_a.faces.new([va_bl, va_br, va_tr, va_tl])
    uv_a = bm_a.loops.layers.uv.new()
    face_a.loops[0][uv_a].uv = (0.0, 0.0) # BL
    face_a.loops[1][uv_a].uv = (1.0, 0.0) # BR
    face_a.loops[2][uv_a].uv = (1.0, 1.0) # TR
    face_a.loops[3][uv_a].uv = (0.0, 1.0) # TL

    mesh_a = bpy.data.meshes.new("Card_Backdrop_Mesh")
    bm_a.to_mesh(mesh_a)
    bm_a.free()

    obj_arch = bpy.data.objects.new("Card_Backdrop", mesh_a)
    bpy.context.collection.objects.link(obj_arch)
    obj_arch.data.materials.append(card_mat)

    # Gold Backing for Arch Card
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0, arch_y_pos + 0.007, arch_z_base + arch_h / 2)
    )
    arch_backing = bpy.context.active_object
    arch_backing.name = "Arch_Gold_Backing"
    arch_backing.scale = (arch_w + 0.03, 0.010, arch_h + 0.03)
    arch_backing.data.materials.append(gold_mat)

    # ----------------------------------------------------
    # Geometry 4: 3D Champagne Gold Plaque on Front of Stage
    # ----------------------------------------------------
    plaque_w = 0.50
    plaque_h = 0.15
    plaque_y = -pedestal_ry * 0.90
    plaque_z = pedestal_h + 0.015
    plaque_tilt = math.radians(24)

    bm_p = bmesh.new()
    vp_bl = bm_p.verts.new((-plaque_w / 2, plaque_y, plaque_z))
    vp_br = bm_p.verts.new((plaque_w / 2, plaque_y, plaque_z))
    vp_tr = bm_p.verts.new((plaque_w / 2, plaque_y + plaque_h * math.sin(plaque_tilt), plaque_z + plaque_h * math.cos(plaque_tilt)))
    vp_tl = bm_p.verts.new((-plaque_w / 2, plaque_y + plaque_h * math.sin(plaque_tilt), plaque_z + plaque_h * math.cos(plaque_tilt)))

    face_p = bm_p.faces.new([vp_bl, vp_br, vp_tr, vp_tl])
    uv_p = bm_p.loops.layers.uv.new()
    face_p.loops[0][uv_p].uv = (0.0, 0.0) # BL
    face_p.loops[1][uv_p].uv = (1.0, 0.0) # BR
    face_p.loops[2][uv_p].uv = (1.0, 1.0) # TR
    face_p.loops[3][uv_p].uv = (0.0, 1.0) # TL

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
    for obj in [obj_lawn, obj_base, gold_rim, obj_couple, obj_arch, arch_backing, obj_plaque]:
        obj.location.z += center_offset_z

    # ----------------------------------------------------
    # Export GLB Model (Writing to BOTH filenames)
    # ----------------------------------------------------
    out_glb_v2 = os.path.join(out_dir, "vandan_riddhi_stage_v2.glb")
    out_glb_primary = os.path.join(out_dir, "vandan_riddhi_stage_3D_AR.glb")
    
    print(f"Exporting GLB to {out_glb_v2}...")
    bpy.ops.export_scene.gltf(
        filepath=out_glb_v2,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_materials='EXPORT',
        export_image_format='AUTO',
        export_cameras=False,
        export_lights=False
    )
    print(f"GLB exported! Size: {os.path.getsize(out_glb_v2):,} bytes")

    # Overwrite primary filename as well so both have the perfect fix!
    shutil.copyfile(out_glb_v2, out_glb_primary)
    print(f"Overwrote primary GLB at {out_glb_primary}")

    # Save Blend file
    out_blend = os.path.join(out_dir, "vandan_riddhi_stage_3D_AR.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print(f"Blend file saved to {out_blend}")

if __name__ == '__main__':
    build_flawless_stage()
