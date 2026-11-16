import bpy
import bmesh
import math
import os
import sys

def build_scene():
    print("==================================================", flush=True)
    print("   VANDAN & RIDDHI - 3D WEDDING AR MODEL BUILDER   ", flush=True)
    print("==================================================", flush=True)

    # 1. Reset scene to pristine state
    bpy.ops.wm.read_factory_settings(use_empty=True)

    scene = bpy.context.scene
    # Configure Cycles CPU with optimized bounces and OIDN Denoising for ultra-fast, clean renders
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 12
    scene.cycles.max_bounces = 3
    scene.cycles.transparent_max_bounces = 4
    scene.cycles.diffuse_bounces = 1
    scene.cycles.glossy_bounces = 2
    scene.cycles.transmission_bounces = 1
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 960
    scene.render.resolution_y = 1440
    scene.render.film_transparent = True
    scene.view_settings.view_transform = 'Standard'

    base_dir = os.path.abspath(".")
    tex_dir = os.path.join(base_dir, "output", "textures")
    bg_img_path = os.path.join(tex_dir, "background_ar.jpg")
    fg_img_path = os.path.join(tex_dir, "foreground_cutout_ar.png")
    shadow_img_path = os.path.join(tex_dir, "couple_shadow.png")

    for path, name in [(bg_img_path, "Background"), (fg_img_path, "Foreground cutout"), (shadow_img_path, "Shadow")]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"{name} texture not found at {path}")

    # Model Dimensions:
    # Photographic Aspect Ratio: 3712 / 5568 = 2/3 (0.666667)
    # Target height = 1.5 Blender units (1.5 meters)
    # Width = 1.5 * (2/3) = 1.0 Blender unit (1.0 meter)
    card_height = 1.5
    card_width = 1.0
    hw = card_width / 2.0
    hh = card_height / 2.0

    print(f"Dimensions: Width={card_width:.3f}m, Height={card_height:.3f}m (2:3 aspect ratio)")

    # ----------------------------------------------------
    # MATERIALS
    # ----------------------------------------------------
    # 1. Champagne Gold Metallic Material
    gold_mat = bpy.data.materials.new(name="Champagne_Gold_Metallic")
    gold_mat.use_nodes = True
    gnodes = gold_mat.node_tree.nodes
    glinks = gold_mat.node_tree.links
    gnodes.clear()
    g_out = gnodes.new("ShaderNodeOutputMaterial")
    g_bsdf = gnodes.new("ShaderNodeBsdfPrincipled")
    # Refined champagne gold color: warm, delicate, non-brassy
    g_bsdf.inputs["Base Color"].default_value = (0.88, 0.78, 0.58, 1.0)
    g_bsdf.inputs["Metallic"].default_value = 0.94
    g_bsdf.inputs["Roughness"].default_value = 0.25
    if "Specular IOR Level" in g_bsdf.inputs:
        g_bsdf.inputs["Specular IOR Level"].default_value = 0.8
    elif "Specular" in g_bsdf.inputs:
        g_bsdf.inputs["Specular"].default_value = 0.8
    glinks.new(g_bsdf.outputs["BSDF"], g_out.inputs["Surface"])

    # 2. Image Texture Material Helper
    def create_image_mat(name, img_path, is_transparent=False, roughness=0.38):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        out_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Roughness"].default_value = roughness
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.5
        elif "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = 0.5

        tex_node = nodes.new("ShaderNodeTexImage")
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

    bg_mat = create_image_mat("Background_Photo_Material", bg_img_path, is_transparent=False, roughness=0.36)
    shadow_mat = create_image_mat("Ambient_Shadow_Material", shadow_img_path, is_transparent=True, roughness=1.0)
    fg_mat = create_image_mat("Foreground_Couple_Material", fg_img_path, is_transparent=True, roughness=0.32)

    # ----------------------------------------------------
    # MESH CREATION HELPERS
    # ----------------------------------------------------
    def create_quad_plane(name, y_offset, material):
        mesh = bpy.data.meshes.new(name + "_mesh")
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)

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

    # ----------------------------------------------------
    # LAYER 3B: LUXURY CHAMPAGNE GOLD BACKING CARD
    # ----------------------------------------------------
    print("Building Layer 3B: Champagne Gold Backing Card...", flush=True)
    card_margin = 0.025
    card_w = card_width + card_margin * 2  # 1.05m
    card_h = card_height + card_margin * 2  # 1.55m
    card_thick = 0.010
    card_y = 0.006

    mesh_back = bpy.data.meshes.new("Backing_Card_mesh")
    back_obj = bpy.data.objects.new("Layer3_Champagne_Gold_Backing", mesh_back)
    bpy.context.collection.objects.link(back_obj)

    bm_card = bmesh.new()
    bmesh.ops.create_cube(bm_card, size=1.0)
    bmesh.ops.scale(bm_card, vec=(card_w, card_thick, card_h), verts=bm_card.verts)
    bmesh.ops.translate(bm_card, vec=(0.0, card_y, 0.0), verts=bm_card.verts)

    # Bevel 4 corner edges parallel to Y for elegant rounded corners
    corner_edges = [
        e for e in bm_card.edges
        if abs(e.verts[0].co.x - e.verts[1].co.x) < 1e-4 and abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-4
    ]
    bmesh.ops.bevel(bm_card, geom=corner_edges, offset=0.035, segments=6, affect='EDGES')

    # Bevel front & back perimeter rim edges
    rim_edges = [e for e in bm_card.edges if abs(e.verts[0].co.y - e.verts[1].co.y) < 1e-4]
    bmesh.ops.bevel(bm_card, geom=rim_edges, offset=0.002, segments=2, affect='EDGES')

    bmesh.ops.recalc_face_normals(bm_card, faces=bm_card.faces)
    bm_card.to_mesh(mesh_back)
    bm_card.free()
    mesh_back.update()
    back_obj.data.materials.append(gold_mat)

    # ----------------------------------------------------
    # LAYER 1: ORIGINAL GARDEN PHOTOGRAPH BACKGROUND
    # ----------------------------------------------------
    print("Building Layer 1: Background Photograph...", flush=True)
    bg_obj = create_quad_plane("Layer1_Background_Photograph", y_offset=0.000, material=bg_mat)

    # ----------------------------------------------------
    # LAYER 3A: AMBIENT CONTACT SHADOW PLANE
    # ----------------------------------------------------
    print("Building Layer 3A: Ambient Depth Shadow...", flush=True)
    shadow_obj = create_quad_plane("Layer3_Ambient_Shadow", y_offset=-0.003, material=shadow_mat)

    # ----------------------------------------------------
    # LAYER 4: CHAMPAGNE GOLD DECORATIVE FRAME
    # ----------------------------------------------------
    print("Building Layer 4: Champagne Gold Decorative Frame...", flush=True)
    frame_mesh = bpy.data.meshes.new("Decorative_Frame_mesh")
    frame_obj = bpy.data.objects.new("Layer4_Decorative_Gold_Frame", frame_mesh)
    bpy.context.collection.objects.link(frame_obj)

    bm_frame = bmesh.new()
    ow, oh = hw + 0.015, hh + 0.015
    iw, ih = hw - 0.004, hh - 0.004
    y_front = -0.012
    y_back = -0.002

    # 4 Outer front verts
    fo = [
        bm_frame.verts.new((-ow, y_front, -oh)),
        bm_frame.verts.new(( ow, y_front, -oh)),
        bm_frame.verts.new(( ow, y_front,  oh)),
        bm_frame.verts.new((-ow, y_front,  oh))
    ]
    # 4 Inner front verts
    fi = [
        bm_frame.verts.new((-iw, y_front, -ih)),
        bm_frame.verts.new(( iw, y_front, -ih)),
        bm_frame.verts.new(( iw, y_front,  ih)),
        bm_frame.verts.new((-iw, y_front,  ih))
    ]
    # 4 Outer back verts
    bo = [
        bm_frame.verts.new((-ow, y_back, -oh)),
        bm_frame.verts.new(( ow, y_back, -oh)),
        bm_frame.verts.new(( ow, y_back,  oh)),
        bm_frame.verts.new((-ow, y_back,  oh))
    ]
    # 4 Inner back verts
    bi = [
        bm_frame.verts.new((-iw, y_back, -ih)),
        bm_frame.verts.new(( iw, y_back, -ih)),
        bm_frame.verts.new(( iw, y_back,  ih)),
        bm_frame.verts.new((-iw, y_back,  ih))
    ]

    # Front face border
    for i in range(4):
        nxt = (i + 1) % 4
        bm_frame.faces.new([fo[i], fo[nxt], fi[nxt], fi[i]])
    # Outer side walls
    for i in range(4):
        nxt = (i + 1) % 4
        bm_frame.faces.new([fo[nxt], fo[i], bo[i], bo[nxt]])
    # Inner side walls
    for i in range(4):
        nxt = (i + 1) % 4
        bm_frame.faces.new([fi[i], fi[nxt], bi[nxt], bi[i]])
    # Back face
    for i in range(4):
        nxt = (i + 1) % 4
        bm_frame.faces.new([bi[i], bi[nxt], bo[nxt], bo[i]])

    # Bevel corner edges
    f_corner_edges = [
        e for e in bm_frame.edges
        if abs(e.verts[0].co.x - e.verts[1].co.x) < 1e-4 and abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-4
    ]
    bmesh.ops.bevel(bm_frame, geom=f_corner_edges, offset=0.030, segments=5, affect='EDGES')

    # Front bevel for jewelry-grade reflection
    front_edges = [
        e for e in bm_frame.edges
        if abs(e.verts[0].co.y - y_front) < 1e-4 and abs(e.verts[1].co.y - y_front) < 1e-4
    ]
    bmesh.ops.bevel(bm_frame, geom=front_edges, offset=0.002, segments=2, affect='EDGES')

    bmesh.ops.recalc_face_normals(bm_frame, faces=bm_frame.faces)
    bm_frame.to_mesh(frame_mesh)
    bm_frame.free()
    frame_mesh.update()
    frame_obj.data.materials.append(gold_mat)

    # ----------------------------------------------------
    # LAYER 2: FOREGROUND COUPLE CUTOUT (POP-OUT)
    # ----------------------------------------------------
    print("Building Layer 2: Foreground Couple Cutout...", flush=True)
    # Exactly aligned with background photo, popped forward by 3.8 cm (-0.038m)
    fg_obj = create_quad_plane("Layer2_Foreground_Couple", y_offset=-0.038, material=fg_mat)

    # ----------------------------------------------------
    # LIGHTING SETUP (Studio 3-Point + Gold Accents)
    # ----------------------------------------------------
    print("Configuring Studio Lighting...", flush=True)
    # Key Light (Area)
    key_light = bpy.data.lights.new("Key_Area_Light", 'AREA')
    key_light.energy = 90.0
    key_light.size = 1.5
    key_light.color = (1.0, 0.98, 0.93)
    key_obj = bpy.data.objects.new("Key_Area_Light", key_light)
    key_obj.location = (1.2, -2.5, 1.4)
    key_obj.rotation_euler = (math.radians(35), math.radians(18), math.radians(-32))
    bpy.context.collection.objects.link(key_obj)

    # Fill Light (Area)
    fill_light = bpy.data.lights.new("Fill_Area_Light", 'AREA')
    fill_light.energy = 45.0
    fill_light.size = 2.0
    fill_light.color = (0.93, 0.96, 1.0)
    fill_obj = bpy.data.objects.new("Fill_Area_Light", fill_light)
    fill_obj.location = (-1.5, -2.2, 0.5)
    fill_obj.rotation_euler = (math.radians(20), math.radians(-25), math.radians(35))
    bpy.context.collection.objects.link(fill_obj)

    # Gold Accent Rim Light
    rim_light = bpy.data.lights.new("Rim_Gold_Light", 'POINT')
    rim_light.energy = 75.0
    rim_light.color = (1.0, 0.88, 0.68)
    rim_obj = bpy.data.objects.new("Rim_Gold_Light", rim_light)
    rim_obj.location = (0.0, 1.0, 1.6)
    bpy.context.collection.objects.link(rim_obj)

    # Soft ambient fill
    scene.world = bpy.data.worlds.new("StudioWorld")
    scene.world.use_nodes = True
    bg_node = scene.world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.95, 0.95, 0.95, 1.0)
        bg_node.inputs["Strength"].default_value = 0.25

    # ----------------------------------------------------
    # CAMERAS
    # ----------------------------------------------------
    print("Configuring Cameras...", flush=True)
    # Front-facing Camera (orthographic portrait perspective)
    cam_front = bpy.data.cameras.new("Camera_Front")
    cam_front.lens = 52.0
    cam_front_obj = bpy.data.objects.new("Camera_Front", cam_front)
    cam_front_obj.location = (0.0, -2.55, 0.0)
    cam_front_obj.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.collection.objects.link(cam_front_obj)

    # 3D Angle Camera (showing the distinct pop-out parallax depth & gold frame)
    cam_angle = bpy.data.cameras.new("Camera_3D_Angle")
    cam_angle.lens = 48.0
    cam_angle_obj = bpy.data.objects.new("Camera_3D_Angle", cam_angle)
    cam_angle_obj.location = (1.15, -2.35, 0.45)
    cam_angle_obj.rotation_euler = (math.radians(78), math.radians(8), math.radians(28))
    bpy.context.collection.objects.link(cam_angle_obj)

    # ----------------------------------------------------
    # SAVE .BLEND FILE
    # ----------------------------------------------------
    out_dir = os.path.join(base_dir, "output")
    blend_path = os.path.join(out_dir, "vandan_riddhi_3D_AR.blend")
    print(f"Saving editable Blender file: {blend_path}...", flush=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    # ----------------------------------------------------
    # EXPORT GLB FOR WEBAR
    # ----------------------------------------------------
    glb_path = os.path.join(out_dir, "vandan_riddhi_3D_AR.glb")
    print(f"Exporting WebAR GLB model: {glb_path}...", flush=True)

    # Select only the 5 mesh objects for GLB export
    mesh_names = [
        "Layer1_Background_Photograph",
        "Layer2_Foreground_Couple",
        "Layer3_Ambient_Shadow",
        "Layer3_Champagne_Gold_Backing",
        "Layer4_Decorative_Gold_Frame"
    ]
    for obj in bpy.context.scene.objects:
        obj.select_set(obj.name in mesh_names)

    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_image_format='AUTO',
        export_materials='EXPORT',
        export_cameras=False,
        export_lights=False
    )
    print(f"WebAR GLB Exported Successfully! Size: {os.path.getsize(glb_path):,} bytes", flush=True)

    # ----------------------------------------------------
    # RENDER PREVIEWS
    # ----------------------------------------------------
    # 1. Front-facing render preview
    print("Rendering Front-Facing Studio Preview...", flush=True)
    scene.camera = cam_front_obj
    front_path = os.path.join(out_dir, "vandan_riddhi_render_front.png")
    scene.render.filepath = front_path
    bpy.ops.render.render(write_still=True)
    print(f"Front preview rendered to {front_path} ({os.path.getsize(front_path):,} bytes)")

    # 2. 3D Angle render preview (showcasing depth pop-out and gold bevels)
    print("Rendering 3D Angle Pop-Out Preview...", flush=True)
    scene.camera = cam_angle_obj
    angle_path = os.path.join(out_dir, "vandan_riddhi_render_3d_angle.png")
    scene.render.filepath = angle_path
    bpy.ops.render.render(write_still=True)
    print(f"3D angle preview rendered to {angle_path} ({os.path.getsize(angle_path):,} bytes)")

    print("==================================================", flush=True)
    print("   ALL OPERATIONS COMPLETED SUCCESSFULLY!        ", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    build_scene()
