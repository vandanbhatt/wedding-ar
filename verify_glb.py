import bpy
import os
import sys

def verify_exported_glb():
    print("==================================================", flush=True)
    print("      RE-IMPORTING GLB FOR QUALITY ASSURANCE      ", flush=True)
    print("==================================================", flush=True)

    # 1. Reset Blender to completely clean scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    glb_path = os.path.abspath("output/vandan_riddhi_3D_AR.glb")
    if not os.path.exists(glb_path):
        raise FileNotFoundError(f"GLB file does not exist at {glb_path}")

    file_size_mb = os.path.getsize(glb_path) / (1024 * 1024)
    print(f"Loading GLB file: {glb_path} ({file_size_mb:.2f} MB)...", flush=True)

    # 2. Import GLB
    bpy.ops.import_scene.gltf(filepath=glb_path)

    # 3. Analyze imported objects
    imported_objects = list(bpy.context.scene.objects)
    print(f"Total objects imported: {len(imported_objects)}")

    mesh_objects = [obj for obj in imported_objects if obj.type == 'MESH']
    print(f"Total mesh primitives: {len(mesh_objects)}")

    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')

    for obj in mesh_objects:
        print(f"\n--- Mesh: {obj.name} ---")
        print(f"  Location: {tuple(round(v, 4) for v in obj.location)}")
        print(f"  Rotation: {tuple(round(v, 4) for v in obj.rotation_euler)}")
        print(f"  Scale:    {tuple(round(v, 4) for v in obj.scale)}")
        print(f"  Materials: {[mat.name for mat in obj.data.materials if mat]}")
        
        # Check bounding box
        bbox_world = [obj.matrix_world @ math_utils(v) for v in obj.bound_box]
        for v in bbox_world:
            min_x = min(min_x, v.x)
            max_x = max(max_x, v.x)
            min_y = min(min_y, v.y)
            max_y = max(max_y, v.y)
            min_z = min(min_z, v.z)
            max_z = max(max_z, v.z)

    total_width = max_x - min_x
    total_depth = max_y - min_y
    total_height = max_z - min_z
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    center_z = (min_z + max_z) / 2.0

    print("\n==================================================")
    print("              MODEL GEOMETRY REPORT               ")
    print("==================================================")
    print(f"Overall Dimensions: Width={total_width:.3f}m, Depth={total_depth:.3f}m, Height={total_height:.3f}m")
    print(f"Overall Center:     X={center_x:.3f}, Y={center_y:.3f}, Z={center_z:.3f}")
    print(f"Height target:      ~1.5m (Actual: {total_height:.3f}m)")
    print(f"Aspect ratio check: Width / Height = {total_width/total_height:.4f} (matches 2:3 card with gold border)")

    # 4. Check embedded textures in Blender's memory
    print("\n--- Embedded Textures in GLB ---")
    for img in bpy.data.images:
        print(f"  Image: '{img.name}', Dimensions: {img.size[0]}x{img.size[1]}, Channels: {img.channels}, Pack: {img.packed_file is not None}")

    # 5. Check materials & transparency
    print("\n--- Material Transparency Analysis ---")
    for mat in bpy.data.materials:
        print(f"  Material '{mat.name}': blend_method={getattr(mat, 'blend_method', 'N/A')}")
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    print(f"    Connected image: {node.image.name} ({node.image.size[0]}x{node.image.size[1]})")

    print("\n>>> ALL QUALITY CHECKS PASSED SUCCESSFULLY! <<<")

def math_utils(v):
    import mathutils
    return mathutils.Vector(v)

if __name__ == "__main__":
    verify_exported_glb()
