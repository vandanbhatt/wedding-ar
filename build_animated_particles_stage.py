import bpy
import bmesh
import math
import os
import shutil
import numpy as np

def build_animated_stage():
    print("=== BUILDING 3D WEDDING STAGE WITH ANIMATED FALLING PETALS & FAIRY DUST ===")

    # 1. Reset Scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 120
    scene.render.fps = 30

    base_dir = r"D:\Website\card"
    out_dir = os.path.join(base_dir, "output")
    tex_dir = os.path.join(out_dir, "textures")

    grass_tex_path = os.path.join(tex_dir, "ground_pure_grass.png")
    couple_tex_path = os.path.join(tex_dir, "foreground_cutout_ar.png")
    card_tex_path = os.path.join(tex_dir, "card_stage_backdrop.jpg")
    plaque_tex_path = os.path.join(tex_dir, "stage_gold_plaque.png")
    petal_tex_path = os.path.join(tex_dir, "rose_petal.png")
    sparkle_tex_path = os.path.join(tex_dir, "sparkle_star.png")

    # ----------------------------------------------------
    # Dedicated Materials
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

    # 6. Blush Pink Rose Petal Material
    petal_mat = bpy.data.materials.new(name="Mat_RosePetal")
    bsdf_petal = petal_mat.node_tree.nodes.get("Principled BSDF")
    img_petal = bpy.data.images.load(petal_tex_path)
    img_petal.name = "Texture_Petal_Rose"
    tex_petal = petal_mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_petal.image = img_petal
    petal_mat.node_tree.links.new(tex_petal.outputs['Color'], bsdf_petal.inputs['Base Color'])
    petal_mat.node_tree.links.new(tex_petal.outputs['Alpha'], bsdf_petal.inputs['Alpha'])
    bsdf_petal.inputs['Roughness'].default_value = 0.60
    petal_mat.blend_method = 'BLEND'

    # 7. Fairy Dust Sparkle Material (Glowing Gold)
    sparkle_mat = bpy.data.materials.new(name="Mat_FairySparkle")
    bsdf_sparkle = sparkle_mat.node_tree.nodes.get("Principled BSDF")
    img_sparkle = bpy.data.images.load(sparkle_tex_path)
    img_sparkle.name = "Texture_Sparkle_Star"
    tex_sparkle = sparkle_mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_sparkle.image = img_sparkle
    sparkle_mat.node_tree.links.new(tex_sparkle.outputs['Color'], bsdf_sparkle.inputs['Base Color'])
    sparkle_mat.node_tree.links.new(tex_sparkle.outputs['Alpha'], bsdf_sparkle.inputs['Alpha'])
    sparkle_mat.node_tree.links.new(tex_sparkle.outputs['Color'], bsdf_sparkle.inputs['Emission Color'])
    bsdf_sparkle.inputs['Emission Strength'].default_value = 2.0
    sparkle_mat.blend_method = 'BLEND'

    # ----------------------------------------------------
    # Geometry 1A: Ground Lawn (100% Grass Mesh)
    # ----------------------------------------------------
    pedestal_rx = 0.65
    pedestal_ry = 0.48
    pedestal_h = 0.035
    segments = 64

    bm_lawn = bmesh.new()
    verts_top = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = pedestal_rx * math.cos(angle)
        y = pedestal_ry * math.sin(angle)
        verts_top.append(bm_lawn.verts.new((x, y, pedestal_h + 0.001)))

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
    # Geometry 1B: Ground Pedestal Gold Base
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
    # Geometry 2: Standing Couple
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
    face_c.loops[0][uv_c].uv = (0.0, 0.0)
    face_c.loops[1][uv_c].uv = (1.0, 0.0)
    face_c.loops[2][uv_c].uv = (1.0, 1.0)
    face_c.loops[3][uv_c].uv = (0.0, 1.0)

    mesh_c = bpy.data.meshes.new("Couple_Mesh")
    bm_c.to_mesh(mesh_c)
    bm_c.free()

    obj_couple = bpy.data.objects.new("Standing_Couple", mesh_c)
    bpy.context.collection.objects.link(obj_couple)
    obj_couple.data.materials.append(couple_mat)

    # ----------------------------------------------------
    # Geometry 3: Floral Arch Backdrop
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
    face_a.loops[0][uv_a].uv = (0.0, 0.0)
    face_a.loops[1][uv_a].uv = (1.0, 0.0)
    face_a.loops[2][uv_a].uv = (1.0, 1.0)
    face_a.loops[3][uv_a].uv = (0.0, 1.0)

    mesh_a = bpy.data.meshes.new("Card_Backdrop_Mesh")
    bm_a.to_mesh(mesh_a)
    bm_a.free()

    obj_arch = bpy.data.objects.new("Card_Backdrop", mesh_a)
    bpy.context.collection.objects.link(obj_arch)
    obj_arch.data.materials.append(card_mat)

    # Gold Backing
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
    face_p.loops[0][uv_p].uv = (0.0, 0.0)
    face_p.loops[1][uv_p].uv = (1.0, 0.0)
    face_p.loops[2][uv_p].uv = (1.0, 1.0)
    face_p.loops[3][uv_p].uv = (0.0, 1.0)

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
    # PARTICLE SYSTEM A: 18 Animated Falling Rose Petals
    # ----------------------------------------------------
    print("Generating 18 animated falling rose petals...")
    np.random.seed(888)
    num_petals = 18
    petal_size = 0.065 # 6.5 cm delicate rose petals

    # Helper to create curved petal mesh
    def create_single_petal_mesh(name):
        bm = bmesh.new()
        pw = petal_size
        ph = petal_size * 1.15
        # 4 vertices slightly curved
        v0 = bm.verts.new((-pw/2, 0, 0))
        v1 = bm.verts.new((pw/2, 0, 0))
        v2 = bm.verts.new((pw/2, -0.012, ph)) # curved profile
        v3 = bm.verts.new((-pw/2, -0.012, ph))
        f = bm.faces.new([v0, v1, v2, v3])
        uv = bm.loops.layers.uv.new()
        f.loops[0][uv].uv = (0.0, 0.0)
        f.loops[1][uv].uv = (1.0, 0.0)
        f.loops[2][uv].uv = (1.0, 1.0)
        f.loops[3][uv].uv = (0.0, 1.0)
        m = bpy.data.meshes.new(name)
        bm.to_mesh(m)
        bm.free()
        return m

    petal_base_mesh = create_single_petal_mesh("Petal_Mesh_Data")

    # Spawn and animate each petal over 120 frames
    for i in range(num_petals):
        p_obj = bpy.data.objects.new(f"Falling_Petal_{i+1:02d}", petal_base_mesh)
        bpy.context.collection.objects.link(p_obj)
        p_obj.data.materials.append(petal_mat)

        # Randomized flight path parameters
        x_center = np.random.uniform(-0.52, 0.52)
        y_center = np.random.uniform(-0.25, 0.12)
        sway_amp_x = np.random.uniform(0.04, 0.09)
        sway_amp_y = np.random.uniform(0.02, 0.06)
        sway_freq = np.random.uniform(1.5, 2.5)
        phase = np.random.uniform(0, 2 * math.pi)

        # Height range: from top of card (z ~ +0.9) down to ground (z ~ -0.6)
        z_start = 0.95 + np.random.uniform(-0.1, 0.2)
        z_end = -0.58
        total_drop = z_start - z_end

        # Initial time phase offset so petals are staggered across the air
        t_offset = (i / num_petals)

        # Create keyframes at frames 1, 30, 60, 90, 120
        key_frames = [1, 30, 60, 90, 120]
        for f in key_frames:
            scene.frame_set(f)
            t = ((f - 1) / 120.0 + t_offset) % 1.0  # normalized time in [0, 1]

            # Current position
            cur_z = z_start - t * total_drop
            cur_x = x_center + sway_amp_x * math.sin(t * sway_freq * 2 * math.pi + phase)
            cur_y = y_center + sway_amp_y * math.cos(t * sway_freq * 2 * math.pi + phase)
            p_obj.location = (cur_x, cur_y, cur_z)

            # Rotation (tumbling and fluttering in breeze)
            rot_x = math.radians(20 * math.sin(t * 4 * math.pi + phase) + 15)
            rot_y = math.radians(25 * math.cos(t * 3 * math.pi + phase))
            rot_z = math.radians(180 * t * (1 if i % 2 == 0 else -1) + phase)
            p_obj.rotation_euler = (rot_x, rot_y, rot_z)

            # Scale (subtle breathing / distance fade)
            base_s = np.random.uniform(0.85, 1.15)
            # Fade out smoothly as it hits ground
            if t > 0.92:
                s_factor = max(0.01, (1.0 - t) / 0.08)
            elif t < 0.08:
                s_factor = max(0.01, t / 0.08)
            else:
                s_factor = 1.0
            p_obj.scale = (base_s * s_factor, base_s * s_factor, base_s * s_factor)

            p_obj.keyframe_insert(data_path="location", frame=f)
            p_obj.keyframe_insert(data_path="rotation_euler", frame=f)
            p_obj.keyframe_insert(data_path="scale", frame=f)

    # ----------------------------------------------------
    # PARTICLE SYSTEM B: 12 Animated Twinkling Fairy Dust Sparkles
    # ----------------------------------------------------
    print("Generating 12 twinkling champagne-gold fairy dust sparkles...")
    num_sparkles = 12
    sparkle_size = 0.045

    def create_sparkle_mesh(name):
        bm = bmesh.new()
        sw = sparkle_size
        v0 = bm.verts.new((-sw/2, 0, -sw/2))
        v1 = bm.verts.new((sw/2, 0, -sw/2))
        v2 = bm.verts.new((sw/2, 0, sw/2))
        v3 = bm.verts.new((-sw/2, 0, sw/2))
        f = bm.faces.new([v0, v1, v2, v3])
        uv = bm.loops.layers.uv.new()
        f.loops[0][uv].uv = (0.0, 0.0)
        f.loops[1][uv].uv = (1.0, 0.0)
        f.loops[2][uv].uv = (1.0, 1.0)
        f.loops[3][uv].uv = (0.0, 1.0)
        m = bpy.data.meshes.new(name)
        bm.to_mesh(m)
        bm.free()
        return m

    sparkle_base_mesh = create_sparkle_mesh("Sparkle_Mesh_Data")

    # Positions around the floral arch
    for j in range(num_sparkles):
        s_obj = bpy.data.objects.new(f"Fairy_Sparkle_{j+1:02d}", sparkle_base_mesh)
        bpy.context.collection.objects.link(s_obj)
        s_obj.data.materials.append(sparkle_mat)

        # Distribute around arch perimeter
        arch_angle = math.pi * (j + 1) / (num_sparkles + 1) # semi-circle
        arch_rad = 0.52 + np.random.uniform(-0.06, 0.06)
        base_x = arch_rad * math.cos(arch_angle)
        base_z = 0.15 + arch_rad * math.sin(arch_angle)
        base_y = np.random.uniform(-0.08, 0.10)

        phase_s = np.random.uniform(0, 2 * math.pi)
        scale_max = np.random.uniform(1.2, 1.6)

        key_frames_s = [1, 30, 60, 90, 120]
        for f in key_frames_s:
            scene.frame_set(f)
            t = (f - 1) / 120.0
            # Gentle vertical float
            cur_z = base_z + 0.025 * math.sin(t * 4 * math.pi + phase_s)
            cur_x = base_x + 0.015 * math.cos(t * 2 * math.pi + phase_s)
            s_obj.location = (cur_x, base_y, cur_z)

            # Twinkling pulsing scale
            pulse = 0.5 + 0.5 * math.sin(t * 6 * math.pi + phase_s)
            s_val = max(0.1, pulse * scale_max)
            s_obj.scale = (s_val, s_val, s_val)

            # Slow rotation
            s_obj.rotation_euler = (0, math.radians(t * 180 + j * 30), 0)

            s_obj.keyframe_insert(data_path="location", frame=f)
            s_obj.keyframe_insert(data_path="rotation_euler", frame=f)
            s_obj.keyframe_insert(data_path="scale", frame=f)

    # ----------------------------------------------------
    # Export GLB Model with Animations (Writing to ALL paths)
    # ----------------------------------------------------
    scene.frame_set(1)
    out_glb_particles = os.path.join(out_dir, "vandan_riddhi_stage_particles.glb")
    out_glb_v2 = os.path.join(out_dir, "vandan_riddhi_stage_v2.glb")
    out_glb_primary = os.path.join(out_dir, "vandan_riddhi_stage_3D_AR.glb")

    print(f"Exporting Animated GLB to {out_glb_particles}...")
    bpy.ops.export_scene.gltf(
        filepath=out_glb_particles,
        export_format='GLB',
        use_selection=False,
        export_apply=False, # keep animation tracks intact!
        export_animations=True,
        export_frame_range=True,
        export_frame_step=1,
        export_materials='EXPORT',
        export_image_format='AUTO',
        export_cameras=False,
        export_lights=False
    )
    print(f"Animated GLB exported! Size: {os.path.getsize(out_glb_particles):,} bytes")

    # Overwrite v2 and primary as well
    shutil.copyfile(out_glb_particles, out_glb_v2)
    shutil.copyfile(out_glb_particles, out_glb_primary)
    print("Updated vandan_riddhi_stage_v2.glb and vandan_riddhi_stage_3D_AR.glb!")

    # Save Blend file
    out_blend = os.path.join(out_dir, "vandan_riddhi_stage_3D_AR.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print(f"Blend file saved to {out_blend}")

if __name__ == '__main__':
    build_animated_stage()
