import bpy
import bmesh
import math
import os

def build_card_matched_ar():
    print("=== BUILDING CARD-MATCHED 3D AR MODEL ===")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 12
    scene.cycles.max_bounces = 3
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 960
    scene.render.resolution_y = 1354  # 726:1024 ratio
    scene.render.film_transparent = True
    scene.view_settings.view_transform = 'Standard'

    base_dir = os.path.abspath(".")
    tex_dir = os.path.join(base_dir, "output", "textures")
    card_img_path = os.path.join(tex_dir, "card_front_ar.jpg")
    couple_img_path = os.path.join(tex_dir, "couple_card_aligned.png")

    assert os.path.exists(card_img_path)
    assert os.path.exists(couple_img_path)

    # Dimensions: 726 x 1024
    # Standard card height: 1.411m, width: 1.0m (or height = 1.5m, width = 1.5 * (726/1024) = 1.063m)
    card_h = 1.500
    card_w = card_h * (726.0 / 1024.0)  # 1.0635m
    hw = card_w / 2.0
    hh = card_h / 2.0

    # 1. Gold Material for subtle card bevel/edge
    gold_mat = bpy.data.materials.new(name="Gold_Edge_Mat")
    gold_mat.use_nodes = True
    g_bsdf = gold_mat.node_tree.nodes.get("Principled BSDF")
    if not g_bsdf:
        g_bsdf = gold_mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    g_bsdf.inputs["Base Color"].default_value = (0.88, 0.78, 0.58, 1.0)
    g_bsdf.inputs["Metallic"].default_value = 0.92
    g_bsdf.inputs["Roughness"].default_value = 0.28

    # 2. Card Front Material
    mat_card = bpy.data.materials.new(name="Card_Front_Mat")
    mat_card.use_nodes = True
    nodes_c = mat_card.node_tree.nodes
    nodes_c.clear()
    c_out = nodes_c.new("ShaderNodeOutputMaterial")
    c_bsdf = nodes_c.new("ShaderNodeBsdfPrincipled")
    c_bsdf.inputs["Roughness"].default_value = 0.35
    c_tex = nodes_c.new("ShaderNodeTexImage")
    c_tex.image = bpy.data.images.load(card_img_path)
    mat_card.node_tree.links.new(c_tex.outputs["Color"], c_bsdf.inputs["Base Color"])
    mat_card.node_tree.links.new(c_bsdf.outputs["BSDF"], c_out.inputs["Surface"])

    # 3. Couple Pop-Out Material (Alpha Blended)
    mat_couple = bpy.data.materials.new(name="Couple_Popout_Mat")
    mat_couple.use_nodes = True
    nodes_cp = mat_couple.node_tree.nodes
    nodes_cp.clear()
    cp_out = nodes_cp.new("ShaderNodeOutputMaterial")
    cp_bsdf = nodes_cp.new("ShaderNodeBsdfPrincipled")
    cp_bsdf.inputs["Roughness"].default_value = 0.30
    cp_tex = nodes_cp.new("ShaderNodeTexImage")
    cp_tex.image = bpy.data.images.load(couple_img_path)
    mat_couple.node_tree.links.new(cp_tex.outputs["Color"], cp_bsdf.inputs["Base Color"])
    mat_couple.node_tree.links.new(cp_tex.outputs["Alpha"], cp_bsdf.inputs["Alpha"])
    mat_couple.node_tree.links.new(cp_bsdf.outputs["BSDF"], cp_out.inputs["Surface"])
    if hasattr(mat_couple, "blend_method"):
        mat_couple.blend_method = 'BLEND'

    # Plane Creation Helper
    def create_card_plane(name, y_offset, material):
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

        uv_layer = mesh.uv_layers.new(name="UVMap")
        uvs = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        for i, loop in enumerate(mesh.loops):
            uv_layer.data[loop.index].uv = uvs[i]

        obj.data.materials.append(material)
        return obj

    # Layer 1: Base Card (Printed Canva Front)
    card_obj = create_card_plane("Layer1_Canva_Card_Base", y_offset=0.000, material=mat_card)

    # Layer 2: 3D Holographic Couple popping forward by 3.5 cm
    couple_obj = create_card_plane("Layer2_Couple_PopOut", y_offset=-0.035, material=mat_couple)

    # Layer 3: Subtle Gold Beveled Backing Base
    mesh_back = bpy.data.meshes.new("Card_Backing_mesh")
    back_obj = bpy.data.objects.new("Layer3_Card_Backing", mesh_back)
    bpy.context.collection.objects.link(back_obj)

    bm_card = bmesh.new()
    bmesh.ops.create_cube(bm_card, size=1.0)
    card_thick = 0.008
    bmesh.ops.scale(bm_card, vec=(card_w + 0.015, card_thick, card_h + 0.015), verts=bm_card.verts)
    bmesh.ops.translate(bm_card, vec=(0.0, 0.005, 0.0), verts=bm_card.verts)
    # Bevel 4 corner edges parallel to Y for rounded PVC card corners
    corner_edges = [
        e for e in bm_card.edges
        if abs(e.verts[0].co.x - e.verts[1].co.x) < 1e-4 and abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-4
    ]
    bmesh.ops.bevel(bm_card, geom=corner_edges, offset=0.030, segments=5, affect='EDGES')
    bmesh.ops.recalc_face_normals(bm_card, faces=bm_card.faces)
    bm_card.to_mesh(mesh_back)
    bm_card.free()
    mesh_back.update()
    back_obj.data.materials.append(gold_mat)

    # Lighting & Camera
    key = bpy.data.lights.new("KeyLight", 'AREA')
    key.energy = 80.0
    key.size = 1.5
    key_o = bpy.data.objects.new("KeyLight", key)
    key_o.location = (1.2, -2.4, 1.4)
    bpy.context.collection.objects.link(key_o)

    fill = bpy.data.lights.new("FillLight", 'AREA')
    fill.energy = 40.0
    fill.size = 2.0
    fill_o = bpy.data.objects.new("FillLight", fill)
    fill_o.location = (-1.4, -2.0, 0.6)
    bpy.context.collection.objects.link(fill_o)

    cam_front = bpy.data.cameras.new("Cam_Front")
    cam_front.lens = 50.0
    cam_front_o = bpy.data.objects.new("Cam_Front", cam_front)
    cam_front_o.location = (0.0, -2.55, 0.0)
    cam_front_o.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.collection.objects.link(cam_front_o)

    cam_angle = bpy.data.cameras.new("Cam_Angle")
    cam_angle.lens = 48.0
    cam_angle_o = bpy.data.objects.new("Cam_Angle", cam_angle)
    cam_angle_o.location = (1.1, -2.3, 0.45)
    cam_angle_o.rotation_euler = (math.radians(78), math.radians(8), math.radians(28))
    bpy.context.collection.objects.link(cam_angle_o)

    # Export Card-Matched GLB
    glb_out = os.path.join(base_dir, "output", "vandan_riddhi_card_3D_AR.glb")
    print(f"Exporting card-matched WebAR GLB to {glb_out}...")
    for o in bpy.context.scene.objects:
        o.select_set(o.type == 'MESH')

    bpy.ops.export_scene.gltf(
        filepath=glb_out,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_image_format='AUTO',
        export_materials='EXPORT',
        export_cameras=False,
        export_lights=False
    )
    print(f"Card-matched GLB exported! Size: {os.path.getsize(glb_out):,} bytes")

    # Render Preview of Card-Matched AR
    scene.camera = cam_angle_o
    render_out = os.path.join(base_dir, "output", "vandan_riddhi_card_render_3d_angle.png")
    scene.render.filepath = render_out
    bpy.ops.render.render(write_still=True)
    print(f"Angle render of card-matched model saved to {render_out}!")

    blend_out = os.path.join(base_dir, "output", "vandan_riddhi_card_3D_AR.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"Blend file saved to {blend_out}!")

if __name__ == "__main__":
    build_card_matched_ar()
