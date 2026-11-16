import bpy
import bmesh
import math
import os
import sys

def build_wedding_ar_scene():
    print("=== STARTING WEDDING 3D AR SCENE GENERATION ===", flush=True)

    # 1. Reset scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES' if 'CYCLES' in [e.id_name for e in bpy.types.RenderEngine.__subclasses__()] else 'BLENDER_EEVEE_NEXT'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 64
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2400
    scene.render.film_transparent = True

    # Color management for vibrant natural photograph reproduction
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'

    # Paths
    base_dir = os.path.abspath(".")
    tex_dir = os.path.join(base_dir, "output", "textures")
    bg_img_path = os.path.join(tex_dir, "background_ar.jpg")
    fg_img_path = os.path.join(tex_dir, "foreground_cutout_ar.png")
    shadow_img_path = os.path.join(tex_dir, "couple_shadow.png")

    assert os.path.exists(bg_img_path), f"Missing {bg_img_path}"
    assert os.path.exists(fg_img_path), f"Missing {fg_img_path}"
    assert os.path.exists(shadow_img_path), f"Missing {shadow_img_path}"

    # Aspect ratio & dimensions
    # Original image: 3712 x 5568 -> aspect ratio = 2/3 = 0.666667
    height = 1.5
    width = 1.0  # 1.5 * (2/3) = 1.0 exactly
    hw = width / 2.0
    hh = height / 2.0

    print(f"Card dimensions: width={width:.4f}m, height={height:.4f}m (Aspect ratio: 2:3)", flush=True)

    # --- MATERIALS ---
    def create_gold_material():
        mat = bpy.data.materials.new(name="Champagne_Gold_Metallic")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        out_node = nodes.new("ShaderNodeOutputMaterial")
        out_node.location = (300, 0)

        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (0, 0)
        # Champagne Gold color (warm, elegant, non-brassy)
        bsdf.inputs["Base Color"].default_value = (0.86, 0.76, 0.56, 1.0)
        bsdf.inputs["Metallic"].default_value = 0.92
        bsdf.inputs["Roughness"].default_value = 0.28
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.8
        elif "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = 0.8

        links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
        return mat

    def create_image_material(name, img_path, is_transparent=False, roughness=0.35):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        out_node = nodes.new("ShaderNodeOutputMaterial")
        out_node.location = (300, 0)

        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (0, 0)
        bsdf.inputs["Roughness"].default_value = roughness
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.5
        elif "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = 0.5

        tex_node = nodes.new("ShaderNodeTexImage")
        tex_node.location = (-350, 0)
        img = bpy.data.images.load(img_path)
        tex_node.image = img

        links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

        if is_transparent:
            links.new(tex_node.outputs["Alpha"], bsdf.inputs["Alpha"])
            if hasattr(mat, "blend_method"):
                mat.blend_method = 'BLEND'
            if hasattr(mat, "surface_render_method"):
                mat.surface_render_method = 'BLENDED'
            if hasattr(mat, "shadow_method"):
                mat.shadow_method = 'NONE'

        return mat

    gold_mat = create_gold_material()
    bg_mat = create_image_material("Background_Photo_Mat", bg_img_path, is_transparent=False, roughness=0.38)
    shadow_mat = create_image_material("Ambient_Shadow_Mat", shadow_img_path, is_transparent=True, roughness=1.0)
    fg_mat = create_image_material("Foreground_Couple_Mat", fg_img_path, is_transparent=True, roughness=0.32)

    # --- HELPER: CREATE TEXTURED PLANE ---
    def create_plane(name, y_offset, material):
        mesh = bpy.data.meshes.new(name + "_mesh")
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)

        # Vertices facing front (-Y)
        # 0: bottom-left, 1: bottom-right, 2: top-right, 3: top-left
        verts = [
            (-hw, y_offset, -hh),
            ( hw, y_offset, -hh),
            ( hw, y_offset,  hh),
            (-hw, y_offset,  hh)
        ]
        faces = [[0, 1, 2, 3]]
        mesh.from_pydata(verts, [], faces)
        mesh.update()

        # UV Coordinates
        uv_layer = mesh.uv_layers.new(name="UVMap")
        uv_data = uv_layer.data
        uv_coords = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        for i, loop in enumerate(mesh.loops):
            uv_data[loop.index].uv = uv_coords[i]

        obj.data.materials.append(material)
        return obj

    # --- LAYER 1: BACKGROUND PHOTOGRAPH ---
    print("Building Layer 1: Background Photograph...", flush=True)
    bg_obj = create_plane("Layer1_Background_Photo", y_offset=0.000, material=bg_mat)

    # --- LAYER 3A: AMBIENT CONTACT SHADOW ---
    print("Building Layer 3A: Ambient Shadow...", flush=True)
    shadow_obj = create_plane("Layer3_Ambient_Shadow", y_offset=-0.003, material=shadow_mat)

    # --- LAYER 2: FOREGROUND COUPLE CUTOUT ---
    print("Building Layer 2: Foreground Couple Cutout...", flush=True)
    # Popping out 4.0 cm in front of background
    fg_obj = create_plane("Layer2_Foreground_Couple", y_offset=-0.038, material=fg_mat)

    # --- LAYER 3B: CHAMPAGNE GOLD BACKING CARD ---
    print("Building Layer 3B: Champagne Gold Backing Card...", flush=True)
    # Backing card with bevelled edges behind the photo
    card_margin = 0.020
    card_thickness = 0.010
    card_w = width + card_margin * 2
    card_h = height + card_margin * 2

    mesh_back = bpy.data.meshes.new("Backing_Card_mesh")
    back_obj = bpy.data.objects.new("Layer3_Backing_Card", mesh_back)
    bpy.context.collection.objects.link(back_obj)

    # Create box mesh with bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    # Scale cube to card dimensions
    bmesh.ops.scale(bm, vec=(card_w, card_thickness, card_h), verts=bm.verts)
    # Position backplate centered just behind the photo (Y center at +0.006 + card_thickness/2)
    bmesh.ops.translate(bm, vec=(0.0, 0.001 + card_thickness / 2.0, 0.0), verts=bm.verts)
    
    # Bevel the edges for smooth luxury feel
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=0.006, segments=3, profile=0.7, affect='EDGES')
    
    bm.to_mesh(mesh_back)
    bm.free()
    mesh_back.update()
    back_obj.data.materials.append(gold_mat)

    # --- LAYER 4: CHAMPAGNE GOLD DECORATIVE FRAME ---
    print("Building Layer 4: Champagne Gold Decorative Frame...", flush=True)
    # A thin, elegant border framing the photo with rounded beveled edges
    frame_mesh = bpy.data.meshes.new("Decorative_Frame_mesh")
    frame_obj = bpy.data.objects.new("Layer4_Decorative_Gold_Frame", frame_mesh)
    bpy.context.collection.objects.link(frame_obj)

    frame_bm = bmesh.new()
    # Outer rectangle: slightly larger than photo
    outer_hw = hw + 0.015
    outer_hh = hh + 0.015
    # Inner opening: slightly reveals photo edge cleanly without clipping couple
    inner_hw = hw - 0.005
    inner_hh = hh - 0.005
    frame_depth = 0.008
    frame_y = -0.006  # slightly in front of photo plane

    # Vertices for front face of frame
    # Outer quad (0..3)
    o0 = frame_bm.verts.new((-outer_hw, frame_y - frame_depth, -outer_hh))
    o1 = frame_bm.verts.new(( outer_hw, frame_y - frame_depth, -outer_hh))
    o2 = frame_bm.verts.new(( outer_hw, frame_y - frame_depth,  outer_hh))
    o3 = frame_bm.verts.new((-outer_hw, frame_y - frame_depth,  outer_hh))

    # Inner quad (4..7)
    i0 = frame_bm.verts.new((-inner_hw, frame_y - frame_depth, -inner_hh))
    i1 = frame_bm.verts.new(( inner_hw, frame_y - frame_depth, -inner_hh))
    i2 = frame_bm.verts.new(( inner_hw, frame_y - frame_depth,  inner_hh))
    i3 = frame_bm.verts.new((-inner_hw, frame_y - frame_depth,  inner_hh))

    # Back outer quad (8..11)
    bo0 = frame_bm.verts.new((-outer_hw, frame_y, -outer_hh))
    bo1 = frame_bm.verts.new(( outer_hw, frame_y, -outer_hh))
    bo2 = frame_bm.verts.new(( outer_hw, frame_y,  outer_hh))
    bo3 = frame_bm.verts.new((-outer_hw, frame_y,  outer_hh))

    # Front frame faces (4 borders around opening)
    frame_bm.faces.new([o0, o1, i1, i0])  # Bottom
    frame_bm.faces.new([o1, o2, i2, i1])  # Right
    frame_bm.faces.new([o2, o3, i3, i2])  # Top
    frame_bm.faces.new([o3, o0, i0, i3])  # Left

    # Outer side walls
    frame_bm.faces.new([o0, bo0, bo1, o1])
    frame_bm.faces.new([o1, bo1, bo2, o2])
    frame_bm.faces.new([o2, bo2, bo3, o3])
    frame_bm.faces.new([o3, bo3, bo0, o0])

    # Inner bevel / rim
    frame_bm.faces.new([i0, i1, o1, o0]) # inner wall back to photo

    # Bevel the front outer edges for elegant luxury reflection
    bmesh.ops.bevel(frame_bm, geom=frame_bm.edges[:], offset=0.003, segments=2, affect='EDGES')

    frame_bm.to_mesh(frame_mesh)
    frame_bm.free()
    frame_mesh.update()
    frame_obj.data.materials.append(gold_mat)

    # --- STUDIO LIGHTING ---
    print("Setting up Studio Lighting...", flush=True)
    light_data_key = bpy.data.lights.new(name="Key_Light", type='AREA')
    light_data_key.energy = 85.0
    light_data_key.size = 1.2
    light_data_key.color = (1.0, 0.97, 0.92)  # Warm bridal tone
    key_obj = bpy.data.objects.new("Key_Light", light_data_key)
    key_obj.location = (1.2, -2.4, 1.4)
    key_obj.rotation_euler = (math.radians(35), math.radians(20), math.radians(-30))
    bpy.context.collection.objects.link(key_obj)

    light_data_fill = bpy.data.lights.new(name="Fill_Light", type='AREA')
    light_data_fill.energy = 45.0
    light_data_fill.size = 1.5
    light_data_fill.color = (0.94, 0.96, 1.0)  # Soft fill
    fill_obj = bpy.data.objects.new("Fill_Light", light_data_fill)
    fill_obj.location = (-1.4, -2.0, 0.6)
    fill_obj.rotation_euler = (math.radians(20), math.radians(-25), math.radians(35))
    bpy.context.collection.objects.link(fill_obj)

    light_data_rim = bpy.data.lights.new(name="Rim_Gold_Light", type='POINT')
    light_data_rim.energy = 60.0
    light_data_rim.color = (1.0, 0.88, 0.70)  # Gold accent rim
    rim_obj = bpy.data.objects.new("Rim_Gold_Light", light_data_rim)
    rim_obj.location = (0.0, 1.2, 1.8)
    bpy.context.collection.objects.link(rim_obj)

    # --- CAMERAS ---
    print("Configuring Cameras...", flush=True)
    # 1. Front Camera (Straight-on AR view)
    cam_front_data = bpy.data.cameras.new("Front_Camera")
    cam_front_data.lens = 55.0  # Portrait lens
    cam_front_obj = bpy.data.objects.new("Front_Camera", cam_front_data)
    cam_front_obj.location = (0.0, -2.55, 0.0)
    cam_front_obj.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.collection.objects.link(cam_front_obj)

    # 2. Angled Perspective Camera (to showcase 3D depth pop-out)
    cam_angle_data = bpy.data.cameras.new("Angle_3D_Camera")
    cam_angle_data.lens = 50.0
    cam_angle_obj = bpy.data.objects.new("Angle_3D_Camera", cam_angle_data)
    cam_angle_obj.location = (1.1, -2.3, 0.5)
    cam_angle_obj.rotation_euler = (math.radians(78), math.radians(6), math.radians(26))
    bpy.context.collection.objects.link(cam_angle_obj)

    scene.camera = cam_front_obj

    # --- SAVE BLENDER FILE ---
    blend_path = os.path.join(base_dir, "output", "vandan_riddhi_3D_AR.blend")
    print(f"Saving editable Blender scene to {blend_path}...", flush=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    # --- EXPORT GLB FOR WEBAR ---
    glb_path = os.path.join(base_dir, "output", "vandan_riddhi_3D_AR.glb")
    print(f"Exporting WebAR GLB to {glb_path}...", flush=True)
    
    # Select only the mesh objects for AR export
    for obj in bpy.context.scene.objects:
        obj.select_set(obj.type == 'MESH')

    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_image_format='AUTO',
        export_materials='EXPORT',
        export_colors=True,
        export_cameras=False,
        export_lights=False
    )
    print(f"GLB exported! Size: {os.path.getsize(glb_path):,} bytes", flush=True)

    # --- RENDER PREVIEWS ---
    print("Rendering Front Preview...", flush=True)
    scene.camera = cam_front_obj
    front_render_path = os.path.join(base_dir, "output", "vandan_riddhi_render_front.png")
    scene.render.filepath = front_render_path
    bpy.ops.render.render(write_still=True)
    print(f"Front preview rendered to {front_render_path}!", flush=True)

    print("Rendering 3D Angle Preview (showing pop-out depth)...", flush=True)
    scene.camera = cam_angle_obj
    angle_render_path = os.path.join(base_dir, "output", "vandan_riddhi_render_3d_angle.png")
    scene.render.filepath = angle_render_path
    bpy.ops.render.render(write_still=True)
    print(f"3D angle preview rendered to {angle_render_path}!", flush=True)

    print("=== SCENE GENERATION COMPLETE ===", flush=True)

if __name__ == "__main__":
    build_wedding_ar_scene()
