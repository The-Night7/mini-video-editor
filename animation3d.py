import moderngl
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import AudioFileClip, ImageSequenceClip
import os
import math

# ─── CONFIG ─────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 720
FPS = 30
DURATION = 41
TOTAL_FRAMES = FPS * DURATION
OUTPUT_DIR = "frames_epic"
OUTPUT_VIDEO = "epic_animation.mp4"
MUSIC_FILE = "epic_music.mp3"  # yt-dlp -x --audio-format mp3 ...

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── COULEURS ───────────────────────────────────────────────────────
BG_COLOR      = (10, 5, 25)
PUPPET_COLOR  = (139, 90, 43)
PUPPET_JOINT  = (80, 50, 20)
GOD_GLOW      = (255, 220, 80)
GOD_SKIN      = (255, 200, 120)
GOD_ROBE = (180, 100, 255) 
ATHENA_ROBE   = (100, 160, 255)   # Bleu sagesse
PENELOPE_ROBE = (200, 120, 160)   # Rose doux

# ─── UTILITAIRES ────────────────────────────────────────────────────
def lerp(a, b, t):      return a + (b - a) * t
def ease_in_out(t):     return t * t * (3 - 2 * t)
def clamp(v, lo, hi):   return max(lo, min(hi, v))
def pulse(t, freq=1.0): return 0.5 + 0.5 * math.sin(t * freq * 2 * math.pi)

# ─── FOND ───────────────────────────────────────────────────────────
def draw_background(draw, frame):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(lerp(10, 30, ratio))
        g = int(lerp(5, 15, ratio))
        b = int(lerp(40, 70, ratio))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Étoiles
    rng = np.random.RandomState(42)
    for i in range(100):
        x = int(rng.uniform(0, WIDTH))
        y = int(rng.uniform(0, HEIGHT * 0.65))
        twinkle = 0.5 + 0.5 * math.sin(frame * 0.04 + i * 1.3)
        b2 = int(140 + 115 * twinkle)
        draw.ellipse([x-1, y-1, x+1, y+1], fill=(b2, b2, int(b2*0.9)))

    # Sol
    ground_y = int(HEIGHT * 0.76)
    for y in range(ground_y, HEIGHT):
        ratio = (y - ground_y) / (HEIGHT - ground_y)
        c = int(lerp(45, 22, ratio))
        draw.line([(0, y), (WIDTH, y)], fill=(c, c, int(c * 1.1)))

    # Colonnes
    for cx in [100, 280, 1000, 1180]:
        col_h = int(HEIGHT * 0.42)
        col_y = ground_y - col_h
        draw.rectangle([cx, col_y, cx+35, ground_y],
                       fill=(50, 45, 65), outline=(75, 70, 95))
        draw.rectangle([cx-8, col_y, cx+43, col_y+18],
                       fill=(62, 57, 78))

    draw.line([(0, ground_y), (WIDTH, ground_y)],
              fill=(80, 70, 100), width=2)
    return ground_y

# ─── MARIONNETTE GÉNÉRIQUE ──────────────────────────────────────────
def draw_puppet(draw, cx, cy, frame, offset=0.0, scale=1.0,
                sway_amp=1.0, robe_color=None, show_strings=True):
    snap_t   = (frame // 4) * 4 / FPS
    sway     = math.sin(snap_t * 2 + offset) * 8 * sway_amp
    bob      = abs(math.sin(snap_t * 2 + offset)) * 5 * sway_amp
    s        = scale
    lw       = max(2, int(3 * s))

    hx, hy         = cx + sway,       cy - bob
    nx, ny         = cx + sway*.8,    cy + int(20*s) - bob
    bx, by         = cx + sway*.5,    cy + int(55*s) - bob
    lhx, lhy       = bx - int(12*s),  by + int(25*s)
    rhx, rhy       = bx + int(12*s),  by + int(25*s)

    leg_sw = math.sin(snap_t * 3 + offset) * 15 * sway_amp
    lkx, lky = lhx - int(leg_sw*.5), lhy + int(30*s)
    lfx, lfy = lkx - int(leg_sw*.3), lky + int(28*s)
    rkx, rky = rhx + int(leg_sw*.5), rhy + int(30*s)
    rfx, rfy = rkx + int(leg_sw*.3), rky + int(28*s)

    arm_sw = math.sin(snap_t * 3 + offset + math.pi) * 20 * sway_amp
    lsx, lsy = nx - int(18*s), ny + int(10*s)
    lex, ley = lsx - int(15*s) - int(arm_sw*.4), lsy + int(20*s)
    lhndx, lhndy = lex - int(10*s), ley + int(18*s)
    rsx, rsy = nx + int(18*s), ny + int(10*s)
    rex, rey = rsx + int(15*s) + int(arm_sw*.4), rsy + int(20*s)
    rhndx, rhndy = rex + int(10*s), rey + int(18*s)

    # Fils
    if show_strings:
        top_y = cy - int(110*s)
        for (px, py) in [(hx, hy - int(12*s)), (lhndx, lhndy),
                         (rhndx, rhndy), (lfx, lfy), (rfx, rfy)]:
            draw.line([(px, top_y), (px, py)],
                      fill=(180, 160, 120), width=max(1, int(s)))

    # Robe optionnelle
    if robe_color:
        robe_pts = [
            (nx - int(20*s), ny),
            (nx + int(20*s), ny),
            (bx + int(35*s), by + int(55*s)),
            (bx - int(35*s), by + int(55*s)),
        ]
        draw.polygon(robe_pts, fill=robe_color,
                     outline=tuple(min(255, c+30) for c in robe_color))

    # Corps
    for seg in [(nx,ny,bx,by),(bx,by,lhx,lhy),(bx,by,rhx,rhy),
                (lhx,lhy,lkx,lky),(lkx,lky,lfx,lfy),
                (rhx,rhy,rkx,rky),(rkx,rky,rfx,rfy),
                (lsx,lsy,lex,ley),(lex,ley,lhndx,lhndy),
                (rsx,rsy,rex,rey),(rex,rey,rhndx,rhndy),
                (lsx,lsy,rsx,rsy)]:
        draw.line([seg[:2], seg[2:]], fill=PUPPET_COLOR, width=lw)

    # Articulations
    jr = max(3, int(4*s))
    for (jx, jy) in [(nx,ny),(bx,by),(lhx,lhy),(rhx,rhy),
                     (lkx,lky),(rkx,rky),(lsx,lsy),(rsx,rsy),
                     (lex,ley),(rex,rey)]:
        draw.ellipse([jx-jr, jy-jr, jx+jr, jy+jr],
                     fill=PUPPET_JOINT, outline=PUPPET_COLOR)
                     
    # Tête
    hr = int(14 * s)
    draw.ellipse([hx - hr, hy - hr*2, hx + hr, hy],
                 fill=PUPPET_COLOR, outline=PUPPET_JOINT, width=lw)
                 
    # Yeux et Sourire
    draw.ellipse([hx-5, hy-hr, hx-2, hy-hr+4], fill=(20, 10, 5))
    draw.ellipse([hx+2, hy-hr, hx+5, hy-hr+4], fill=(20, 10, 5))
    draw.arc([hx-5, hy-hr//2, hx+5, hy-2], start=0, end=180, fill=(20, 10, 5), width=2)

# ─── DESSIN : DIEU (vivant, lumineux) ───────────────────────────────
def draw_god(draw, cx, cy, frame, name="Athena", robe_color="GOD_ROBE", scale=1.2):
    """
    Dieu vivant : mouvements fluides, aura lumineuse, robe.
    """
    t = frame / FPS
    sway  = math.sin(t * 1.2) * 6
    float_y = math.sin(t * 0.8) * 4  # légère lévitation

    s = scale
    glow_r = int(40 + 20 * pulse(t / DURATION, 1.5))

    # ── Aura / halo ──────────────────────────────────────────────────
    for g in range(5, 0, -1):
        alpha = int(30 * g / 5)
        gr = glow_r + g * 8
        draw.ellipse([cx - gr, cy - int(150*s) - gr,
                      cx + gr, cy + int(20*s) + gr],
                     fill=(255, 200, 50, alpha) if name != "Zeus"
                          else (100, 150, 255, alpha))

    # ── Robe ─────────────────────────────────────────────────────────
    robe_color = GOD_ROBE if name == "Athena" else (80, 120, 220)
    robe_pts = [
        (cx + sway - int(25*s), cy - int(30*s) + float_y),
        (cx + sway + int(25*s), cy - int(30*s) + float_y),
        (cx + sway + int(40*s), cy + int(80*s) + float_y),
        (cx + sway - int(40*s), cy + int(80*s) + float_y),
    ]
    draw.polygon(robe_pts, fill=robe_color,
                 outline=tuple(min(255, c+40) for c in robe_color))

    # ── Corps ────────────────────────────────────────────────────────
    lw = max(2, int(3 * s))
    neck_x, neck_y   = cx + sway, cy - int(30*s) + float_y
    body_x, body_y   = cx + sway * 0.7, cy + int(10*s) + float_y

    # Bras (fluides, courbes simulées)
    arm_t = math.sin(t * 1.5) * 25
    lshoulder = (neck_x - int(20*s), neck_y + int(5*s))
    lelbow     = (neck_x - int(40*s) - arm_t, neck_y + int(35*s))
    lhand      = (neck_x - int(30*s) - arm_t*0.5, neck_y + int(60*s))

    rshoulder = (neck_x + int(20*s), neck_y + int(5*s))
    relbow     = (neck_x + int(40*s) + arm_t, neck_y + int(35*s))
    rhand      = (neck_x + int(30*s) + arm_t*0.5, neck_y + int(60*s))

    # Bras gauche
    draw.line([lshoulder, lelbow], fill=GOD_SKIN, width=lw+1)
    draw.line([lelbow, lhand],     fill=GOD_SKIN, width=lw+1)
    # Bras droit
    draw.line([rshoulder, relbow], fill=GOD_SKIN, width=lw+1)
    draw.line([relbow, rhand],     fill=GOD_SKIN, width=lw+1)

    # ── Tête ─────────────────────────────────────────────────────────
    hr = int(18 * s)
    head_x = cx + sway
    head_y = cy - int(60*s) + float_y

    # Halo doré
    draw.ellipse([head_x - hr - 6, head_y - hr*2 - 6,
                  head_x + hr + 6, head_y + 6],
                 fill=GOD_GLOW)
    # Visage
    draw.ellipse([head_x - hr, head_y - hr*2,
                  head_x + hr, head_y],
                 fill=GOD_SKIN, outline=(220, 170, 80), width=2)
    # Yeux expressifs
    draw.ellipse([head_x-7, head_y-hr, head_x-3, head_y-hr+6],
                 fill=(60, 30, 10))
    draw.ellipse([head_x+3, head_y-hr, head_x+7, head_y-hr+6],
                 fill=(60, 30, 10))
    # Reflet dans les yeux
    draw.ellipse([head_x-6, head_y-hr, head_x-5, head_y-hr+2],
                 fill=(255, 255, 255))
    draw.ellipse([head_x+4, head_y-hr, head_x+5, head_y-hr+2],
                 fill=(255, 255, 255))
    # Sourire doux
    draw.arc([head_x-6, head_y-hr//2+2,
              head_x+6, head_y-2],
             start=0, end=180, fill=(180, 80, 80), width=2)

    # ── Nom du dieu ──────────────────────────────────────────────────
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", int(16*s))
    except:
        font = ImageFont.load_default()
    draw.text((cx - 30, cy - int(90*s) + float_y),
              name, fill=GOD_GLOW, font=font)

# ─── DESSIN : PARTICULES MAGIQUES ───────────────────────────────────
def draw_particles(draw, frame):
    rng = np.random.RandomState(frame // 3)
    t = frame / FPS
    for i in range(25):
        px = int(rng.uniform(WIDTH * 0.3, WIDTH * 0.7))
        py = int(rng.uniform(HEIGHT * 0.1, HEIGHT * 0.7))
        py -= int((frame % 30) * 2)  # monte
        alpha = int(200 * (1 - (frame % 30) / 30))
        r = int(rng.uniform(1, 4))
        brightness = int(rng.uniform(180, 255))
        draw.ellipse([px-r, py-r, px+r, py+r],
                     fill=(brightness, int(brightness*0.85), 50))

# ─── SCÈNES ─────────────────────────────────────────────────────────
def get_scene(frame):
    t = frame / TOTAL_FRAMES
    if t < 0.10:    return "intro"          # 0–4s   : Titre / ouverture
    elif t < 0.28:  return "puppet_dance"   # 4–11s  : Humains-marionnettes
    elif t < 0.45:  return "god_appears"    # 11–18s : Aphrodite descend
    elif t < 0.62:  return "confrontation"  # 18–25s : Face à face
    elif t < 0.80:  return "duet"           # 25–33s : Duo / tension
    else:           return "finale"         # 33–41s : Climax + fondu


# ─── GÉNÉRATION DES FRAMES ──────────────────────────────────────────
print("🎬 Génération des frames EPIC...")

for frame in range(TOTAL_FRAMES):
    img  = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    ground_y = draw_background(draw, frame)
    scene    = get_scene(frame)
    t        = frame / TOTAL_FRAMES
    t_scene = (frame - SCENE_STARTS[scene]) / TOTAL_FRAMES


    # ── INTRO : Titre ────────────────────────────────────────────────
    if scene == "intro":
        alpha = min(1.0, t_scene / 0.1)
        try:
            font_big = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 48)
            font_sub = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 24)
        except:
            font_big = ImageFont.load_default()
            font_sub = font_big

        title_color = tuple(int(c * alpha) for c in GOD_GLOW)
        draw.text((WIDTH//2 - 280, HEIGHT//2 - 60),
                  "NEED HER TO BE MINE", fill=title_color, font=font_big)
        draw.text((WIDTH//2 - 160, HEIGHT//2 + 10),
                  "EPIC: The Musical", fill=title_color, font=font_sub)

        # Marionnette qui apparaît
        if t_scene > 0.4:
            fade = (t_scene - 0.4) / 0.6
            draw_puppet(draw, int(WIDTH*0.3), ground_y - 140,
                        frame, offset=0, scale=0.9 * fade)

    # ── PUPPET DANCE : Les humains dansent ───────────────────────────
    elif scene == "puppet_dance":
        draw_particles(draw, frame)
        # 3 marionnettes
        draw_puppet(draw, int(WIDTH*0.25), ground_y - 140,
                    frame, offset=0.0, scale=0.9)
        draw_puppet(draw, int(WIDTH*0.50), ground_y - 140,
                    frame, offset=1.0, scale=1.0)
        draw_puppet(draw, int(WIDTH*0.75), ground_y - 140,
                    frame, offset=2.0, scale=0.85)

    # ── GOD APPEARS : Aphrodite descend ─────────────────────────────
    elif scene == "god_appears":
        draw_particles(draw, frame)
        draw_puppet(draw, int(WIDTH*0.25), ground_y - 140,
                    frame, offset=0.0, scale=0.9, sway_amp=0.5)
        draw_puppet(draw, int(WIDTH*0.75), ground_y - 140,
                    frame, offset=2.0, scale=0.85, sway_amp=0.5)

        # Aphrodite descend du ciel
        god_y_start = int(HEIGHT * 0.1)
        god_y_end   = ground_y - 160
        god_y = int(lerp(god_y_start, god_y_end, ease_in_out(min(1, t_scene * 3))))
        draw_god(draw, WIDTH//2, god_y, frame, name="Aphrodite", scale=1.1)

    # ── CONFRONTATION ────────────────────────────────────────────────
    elif scene == "confrontation":
        draw_particles(draw, frame)
        # Marionnettes qui regardent le dieu (inclinées)
        draw_puppet(draw, int(WIDTH*0.2), ground_y - 140,
                    frame, offset=0.0, scale=0.9, sway_amp=0.3)
        draw_puppet(draw, int(WIDTH*0.8), ground_y - 140,
                    frame, offset=1.5, scale=0.9, sway_amp=0.3)

        # Aphrodite au centre
        draw_god(draw, WIDTH//2, ground_y - 160,
                 frame, name="Aphrodite", scale=1.2)

        # Zeus apparaît à droite
        zeus_x = int(lerp(WIDTH + 100, int(WIDTH * 0.78),
                          ease_in_out(min(1, t_scene * 4))))
        draw_god(draw, zeus_x, ground_y - 150,
                 frame, name="Zeus", scale=1.0)

    # ── FINALE : Tous ensemble ───────────────────────────────────────
    elif scene == "finale":
        draw_particles(draw, frame)
        draw_particles(draw, frame + 15)

        draw_puppet(draw, int(WIDTH*0.15), ground_y - 140,
                    frame, offset=0.0, scale=0.8)
        draw_puppet(draw, int(WIDTH*0.35), ground_y - 140,
                    frame, offset=1.0, scale=0.9)
        draw_puppet(draw, int(WIDTH*0.65), ground_y - 140,
                    frame, offset=2.0, scale=0.85)
        draw_puppet(draw, int(WIDTH*0.85), ground_y - 140,
                    frame, offset=3.0, scale=0.8)

        draw_god(draw, int(WIDTH*0.5), ground_y - 170,
                 frame, name="Aphrodite", scale=1.3)

        # Fondu final
        fade_out = min(1.0, (t_scene - 0.7) / 0.3)
        if fade_out > 0:
            overlay = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
            img = Image.blend(img, overlay, fade_out)
            draw = ImageDraw.Draw(img)

    img.save(f"{OUTPUT_DIR}/frame_{frame:04d}.png")

    if frame % FPS == 0:
        print(f"  🎞️  {frame // FPS}s / {DURATION}s")

# ─── ASSEMBLAGE MP4 AVEC MUSIQUE ────────────────────────────────────
print("🎵 Assemblage avec la musique...")

video_clip = ImageSequenceClip(OUTPUT_DIR, fps=FPS)

try:
    audio_clip = AudioFileClip(MUSIC_FILE).subclipped(0, DURATION)
    final_clip = video_clip.with_audio(audio_clip)
    final_clip.write_videofile(OUTPUT_VIDEO, codec='libx264', audio_codec='aac')
    print(f"✅ Vidéo avec musique exportée : {OUTPUT_VIDEO}")
except Exception as e:
    print(f"⚠️  Musique non trouvée ({e}), export sans audio...")
    video_clip.write_videofile(OUTPUT_VIDEO, codec='libx264')
    print(f"✅ Vidéo exportée (sans audio) : {OUTPUT_VIDEO}")
