import bpy
import os
import math
import random

# ── Nettoyage scène ──────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ── Render Settings ──────────────────────────────────────────────
scene.render.engine                      = 'BLENDER_EEVEE'
scene.render.resolution_x               = 1280
scene.render.resolution_y               = 720
scene.render.resolution_percentage      = 100
scene.render.fps                        = 24
scene.frame_start                       = 1
scene.frame_end                         = 984   # 2s pour test — mettre 984 pour le vrai rendu

# Output PNG frames
os.makedirs("frames", exist_ok=True)
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath                   = os.path.abspath("frames/frame_")

# ── EEVEE Settings (5.1 — tout wrappé en try/except) ────────────
eevee = scene.eevee
eevee.taa_render_samples = 16
for attr, val in {
    'use_shadows':            True,
    'use_volumetric_shadows': True,
    'use_volumetric_lights':  True,
    'use_bloom':              True,
    'use_gtao':               True,
}.items():
    try:
        setattr(eevee, attr, val)
    except AttributeError:
        pass

# ── View settings (look cinématique) ────────────────────────────
try:
    scene.view_settings.look = 'AgX - Punchy'
except Exception:
    try:
        scene.view_settings.look = 'Filmic - High Contrast'
    except Exception:
        pass

# ── Freestyle (contours cel-shading) ────────────────────────────
scene.render.use_freestyle = True
try:
    vl = scene.view_layers[0]
    fs = vl.freestyle_settings
    # Crée un lineset si absent
    if len(fs.linesets) == 0:
        bpy.ops.scene.freestyle_lineset_add()
    ls = fs.linesets[0]
    # Crée un linestyle si absent
    if ls.linestyle is None:
        bpy.ops.scene.freestyle_linestyle_new()
    ls.linestyle.thickness = 2.2
    ls.linestyle.color = (0.0, 0.0, 0.0)
except Exception as e:
    print(f"[WARN] Freestyle non configuré : {e}")

# ── World (ciel nocturne) ────────────────────────────────────────
world = bpy.data.worlds.new("OlympusNight")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value    = (0.01, 0.01, 0.08, 1.0)
    bg.inputs['Strength'].default_value = 0.3

# ── Helpers ──────────────────────────────────────────────────────
def new_mat(name, color, metallic=0.0, roughness=0.8, toon=False, emit=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    if toon:
        try:
            shader = nodes.new('ShaderNodeBsdfToon')
            shader.inputs['Color'].default_value = color
            shader.inputs['Size'].default_value  = 0.6
        except Exception:
            # Fallback si Toon BSDF absent
            shader = nodes.new('ShaderNodeBsdfPrincipled')
            shader.inputs['Base Color'].default_value = color
    else:
        shader = nodes.new('ShaderNodeBsdfPrincipled')
        shader.inputs['Base Color'].default_value = color
        try:
            shader.inputs['Metallic'].default_value   = metallic
            shader.inputs['Roughness'].default_value  = roughness
        except Exception:
            pass
    if emit > 0:
        em  = nodes.new('ShaderNodeEmission')
        em.inputs['Color'].default_value    = color
        em.inputs['Strength'].default_value = emit
        mix = nodes.new('ShaderNodeMixShader')
        mix.inputs['Fac'].default_value = 0.4
        links.new(shader.outputs[0], mix.inputs[1])
        links.new(em.outputs[0],     mix.inputs[2])
        links.new(mix.outputs[0],    out.inputs['Surface'])
    else:
        links.new(shader.outputs[0], out.inputs['Surface'])
    return mat

def add_obj(type_, name, loc, scale, mat):
    if type_ == 'CUBE':
        bpy.ops.mesh.primitive_cube_add(location=loc)
    elif type_ == 'CYLINDER':
        bpy.ops.mesh.primitive_cylinder_add(location=loc)
    elif type_ == 'SPHERE':
        bpy.ops.mesh.primitive_uv_sphere_add(location=loc)
    elif type_ == 'CONE':
        bpy.ops.mesh.primitive_cone_add(location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if mat:
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat
    return obj

def keyframe_loc(obj, frame, loc):
    obj.location = loc
    obj.keyframe_insert('location', frame=frame)

def keyframe_rot(obj, frame, rot):
    obj.rotation_euler = rot
    obj.keyframe_insert('rotation_euler', frame=frame)

# ── Matériaux ────────────────────────────────────────────────────
mat_wood   = new_mat("Wood",   (0.45, 0.28, 0.12, 1), roughness=0.9,  toon=True)
mat_cloth  = new_mat("Cloth",  (0.15, 0.25, 0.55, 1), roughness=0.95, toon=True)
mat_skin   = new_mat("Skin",   (0.9,  0.72, 0.58, 1), roughness=0.7,  toon=True)
mat_divine = new_mat("Divine", (0.95, 0.85, 0.3,  1), metallic=0.8,   roughness=0.2, emit=1.5)
mat_marble = new_mat("Marble", (0.88, 0.86, 0.82, 1), roughness=0.3)
mat_string = new_mat("String", (0.8,  0.8,  0.8,  1), roughness=1.0)
mat_aura   = new_mat("Aura",   (0.5,  0.7,  1.0,  1), emit=2.0)
mat_star   = new_mat("Star",   (1.0,  1.0,  0.9,  1), emit=3.0)
mat_eye    = new_mat("Eye",    (0.05, 0.05, 0.4,  1), toon=True)

# ── Sol ──────────────────────────────────────────────────────────
add_obj('CUBE', "Floor", (0, 0, -0.1), (8, 5, 0.1), mat_marble)

# ── Colonnes grecques ────────────────────────────────────────────
for i, (cx, cy) in enumerate([(-5,-3),(-5,3),(5,-3),(5,3)]):
    add_obj('CYLINDER', f"Col_{i}_shaft", (cx, cy, 1.5),  (0.25, 0.25, 1.5),  mat_marble)
    add_obj('CUBE',     f"Col_{i}_cap",   (cx, cy, 3.1),  (0.35, 0.35, 0.15), mat_marble)
    add_obj('CUBE',     f"Col_{i}_base",  (cx, cy, 0.1),  (0.35, 0.35, 0.1),  mat_marble)

# ── Étoiles ──────────────────────────────────────────────────────
random.seed(42)
for i in range(60):
    x = random.uniform(-12, 12)
    y = random.uniform(3, 10)
    z = random.uniform(3, 9)
    s = random.uniform(0.03, 0.09)
    add_obj('SPHERE', f"Star_{i}", (x, y, z), (s, s, s), mat_star)

# ── Marionnette Odysseus ─────────────────────────────────────────
ody_torso = add_obj('CUBE',     "Ody_torso", (-2,    0, 1.2),  (0.28, 0.18, 0.35), mat_wood)
ody_head  = add_obj('SPHERE',   "Ody_head",  (-2,    0, 1.9),  (0.2,  0.2,  0.2),  mat_skin)
ody_larm  = add_obj('CYLINDER', "Ody_larm",  (-2.45, 0, 1.35), (0.07, 0.07, 0.28), mat_wood)
ody_rarm  = add_obj('CYLINDER', "Ody_rarm",  (-1.55, 0, 1.35), (0.07, 0.07, 0.28), mat_wood)
add_obj('CYLINDER', "Ody_lleg", (-2.15, 0, 0.65), (0.08, 0.08, 0.3), mat_wood)
add_obj('CYLINDER', "Ody_rleg", (-1.85, 0, 0.65), (0.08, 0.08, 0.3), mat_wood)
for pos in [(-2.45,0,1.55),(-1.55,0,1.55),(-2.15,0,0.9),(-1.85,0,0.9)]:
    add_obj('SPHERE', "Joint", pos, (0.07,0.07,0.07), mat_wood)
for pos in [(-2,0,2.1),(-2.45,0,1.6),(-1.55,0,1.6)]:
    add_obj('CYLINDER', "String", pos, (0.01,0.01,0.25), mat_string)

# ── Marionnette Penelope ─────────────────────────────────────────
pen_torso = add_obj('CUBE',     "Pen_torso", (2,    0, 1.2),  (0.26, 0.16, 0.38), mat_cloth)
pen_head  = add_obj('SPHERE',   "Pen_head",  (2,    0, 1.95), (0.19, 0.19, 0.19), mat_skin)
pen_larm  = add_obj('CYLINDER', "Pen_larm",  (1.6,  0, 1.35), (0.06, 0.06, 0.26), mat_cloth)
pen_rarm  = add_obj('CYLINDER', "Pen_rarm",  (2.4,  0, 1.35), (0.06, 0.06, 0.26), mat_cloth)
add_obj('CYLINDER', "Pen_lleg", (1.85, 0, 0.65), (0.07, 0.07, 0.3), mat_cloth)
add_obj('CYLINDER', "Pen_rleg", (2.15, 0, 0.65), (0.07, 0.07, 0.3), mat_cloth)
for pos in [(1.6,0,1.55),(2.4,0,1.55),(1.85,0,0.9),(2.15,0,0.9)]:
    add_obj('SPHERE', "Joint", pos, (0.06,0.06,0.06), mat_cloth)
for pos in [(2,0,2.15),(1.6,0,1.6),(2.4,0,1.6)]:
    add_obj('CYLINDER', "String", pos, (0.01,0.01,0.25), mat_string)

# ── Athena (déesse) ──────────────────────────────────────────────
ath_torso = add_obj('CUBE',     "Ath_torso",  (0,     0, 1.3),  (0.3,  0.2,  0.45), mat_divine)
ath_head  = add_obj('SPHERE',   "Ath_head",   (0,     0, 2.1),  (0.22, 0.22, 0.22), mat_skin)
add_obj('CYLINDER', "Ath_larm", (-0.45, 0, 1.4), (0.07, 0.07, 0.32), mat_divine)
add_obj('CYLINDER', "Ath_rarm", ( 0.45, 0, 1.4), (0.07, 0.07, 0.32), mat_divine)
add_obj('CYLINDER', "Ath_lleg", (-0.15, 0, 0.6), (0.09, 0.09, 0.35), mat_divine)
add_obj('CYLINDER', "Ath_rleg", ( 0.15, 0, 0.6), (0.09, 0.09, 0.35), mat_divine)
add_obj('SPHERE', "Ath_eye_l", (-0.08, -0.2, 2.12), (0.04,0.04,0.04), mat_eye)
add_obj('SPHERE', "Ath_eye_r", ( 0.08, -0.2, 2.12), (0.04,0.04,0.04), mat_eye)
aura = add_obj('SPHERE',   "Aura", (0, 0, 1.3),  (0.9,  0.9,  1.2),  mat_aura)
aura.display_type = 'WIRE'
halo = add_obj('CYLINDER', "Halo", (0, 0, 2.45), (0.35, 0.35, 0.03), mat_divine)

# ── Animation marionnettes (saccadée) ───────────────────────────
for frame in range(1, 49, 4):
    swing = 0.15 * math.sin(frame * 0.4)
    keyframe_rot(ody_larm, frame, (swing,    0, 0))
    keyframe_rot(ody_rarm, frame, (-swing,   0, 0))
    keyframe_rot(pen_larm, frame, (-swing*0.8, 0, 0))
    keyframe_rot(pen_rarm, frame, ( swing*0.8, 0, 0))

# ── Animation Athena (descend du ciel) ──────────────────────────
keyframe_loc(ath_torso, 1,  (0, 0, 5.0))
keyframe_loc(ath_torso, 24, (0, 0, 1.3))
keyframe_loc(ath_head,  1,  (0, 0, 5.8))
keyframe_loc(ath_head,  24, (0, 0, 2.1))

# Halo rotation continue
for f in range(1, 49, 6):
    keyframe_rot(halo, f, (0, 0, math.radians(f * 15)))

# ── Lumières ─────────────────────────────────────────────────────
bpy.ops.object.light_add(type='SUN', location=(5, -5, 8))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.data.color  = (1.0, 0.92, 0.75)
sun.rotation_euler = (math.radians(45), 0, math.radians(-30))

bpy.ops.object.light_add(type='AREA', location=(-4, 4, 5))
fill = bpy.context.active_object
fill.data.energy = 200
fill.data.color  = (0.4, 0.6, 1.0)
fill.data.size   = 3.0

bpy.ops.object.light_add(type='POINT', location=(0, -1, 3))
divine_light = bpy.context.active_object
divine_light.data.color = (1.0, 0.9, 0.4)
for f in [1, 12, 24, 36, 48]:
    divine_light.data.energy = 300 + 150 * math.sin(f * 0.3)
    divine_light.data.keyframe_insert('energy', frame=f)

# ── Caméra ───────────────────────────────────────────────────────
bpy.ops.object.camera_add(location=(0, -7, 2))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(80), 0, 0)
scene.camera = cam

for frame, loc, rot in [
    (1,  (0,  -7,  2),   (math.radians(80), 0, 0)),
    (12, (-2, -6,  2.5), (math.radians(78), 0, math.radians(-10))),
    (24, (0,  -5,  3),   (math.radians(75), 0, 0)),
    (36, (0,  -4,  2.5), (math.radians(80), 0, 0)),
    (48, (0,  -8,  4),   (math.radians(70), 0, 0)),
]:
    keyframe_loc(cam, frame, loc)
    keyframe_rot(cam, frame, rot)

# ── Sauvegarde .blend ────────────────────────────────────────────
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath("epic_scene.blend"))
print("✅ Scène sauvegardée : epic_scene.blend")

# ── Rendu ────────────────────────────────────────────────────────
print(f"🎬 Rendu frames {scene.frame_start}–{scene.frame_end}...")
bpy.ops.render.render(animation=True)
print("✅ Frames rendues dans : frames/")
print()
print("📦 Assembler avec ffmpeg :")
print("   ffmpeg -framerate 24 -i frames/frame_%04d.png \\")
print("          -c:v libx264 -crf 18 -pix_fmt yuv420p epic_animation.mp4")
