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
MUSIC_FILE = "epic_music.mp3"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── COULEURS ───────────────────────────────────────────────────────
BG_COLOR      = (10, 5, 25)
PUPPET_COLOR  = (139, 90, 43)
PUPPET_JOINT  = (80, 50, 20)
GOD_GLOW      = (255, 220, 80)
GOD_SKIN      = (255, 200, 120)
ATHENA_ROBE   = (100, 160, 255)
PENELOPE_ROBE = (200, 120, 160)

# ─── UTILITAIRES ────────────────────────────────────────────────────
def lerp(a, b, t):      return a + (b - a) * t
def ease_in_out(t):     return t * t * (3 - 2 * t)
def clamp(v, lo, hi):   return max(lo, min(hi, v))
def pulse(t, freq=1.0): return 0.5 + 0.5 * math.sin(t * freq * 2 * math.pi)

# ─── SCÈNES (défini tôt, utilisé partout) ───────────────────────────
SCENE_STARTS = {
    "intro":          0,
    "odysseus_sings": int(TOTAL_FRAMES * 4  / 41),
    "penelope":       int(TOTAL_FRAMES * 13 / 41),
    "asks_help":      int(TOTAL_FRAMES * 19 / 41),
    "athena_annoyed": int(TOTAL_FRAMES * 22 / 41),
    "plea":           int(TOTAL_FRAMES * 24 / 41),
    "climax":         int(TOTAL_FRAMES * 29 / 41),
    "finale":         int(TOTAL_FRAMES * 35 / 41),
}

def get_scene(frame):
    scene = "intro"
    for name, start in SCENE_STARTS.items():
        if frame >= start:
            scene = name
    return scene

# ─── FOND ───────────────────────────────────────────────────────────
def draw_background(draw, frame):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(lerp(10, 30, ratio))
        g = int(lerp(5, 15, ratio))
        b = int(lerp(40, 70, ratio))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    rng = np.random.RandomState(42)
    for i in range(100):
        x = int(rng.uniform(0, WIDTH))
        y = int(rng.uniform(0, HEIGHT * 0.65))
        twinkle = 0.5 + 0.5 * math.sin(frame * 0.04 + i * 1.3)
        b2 = int(140 + 115 * twinkle)
        draw.ellipse([x-1, y-1, x+1, y+1], fill=(b2, b2, int(b2*0.9)))

    ground_y = int(HEIGHT * 0.76)
    for y in range(ground_y, HEIGHT):
        ratio = (y - ground_y) / (HEIGHT - ground_y)
        c = int(lerp(45, 22, ratio))
        draw.line([(0, y), (WIDTH, y)], fill=(c, c, int(c * 1.1)))

    for cx in [100, 280, 1000, 1180]:
        col_h = int(HEIGHT * 0.42)
        col_y = ground_y - col_h
        draw.rectangle([cx, col_y, cx+35, ground_y],
                       fill=(50, 45, 65), outline=(75, 70, 95))
        draw.rectangle([cx-8, col_y, cx+43, col_y+18], fill=(62, 57, 78))

    draw.line([(0, ground_y), (WIDTH, ground_y)], fill=(80, 70, 100), width=2)
    return ground_y

# ─── MARIONNETTE ────────────────────────────────────────────────────
def draw_puppet(draw, cx, cy, frame, offset=0.0, scale=1.0,
                sway_amp=1.0, robe_color=None, show_strings=True):
    snap_t = (frame // 4) * 4 / FPS
    sway   = math.sin(snap_t * 2 + offset) * 8 * sway_amp
    bob    = abs(math.sin(snap_t * 2 + offset)) * 5 * sway_amp
    s, lw  = scale, max(2, int(3 * scale))

    hx, hy   = cx + sway,      cy - bob
    nx, ny   = cx + sway*.8,   cy + int(20*s) - bob
    bx, by   = cx + sway*.5,   cy + int(55*s) - bob
    lhx, lhy = bx - int(12*s), by + int(25*s)
    rhx, rhy = bx + int(12*s), by + int(25*s)

    leg_sw   = math.sin(snap_t * 3 + offset) * 15 * sway_amp
    lkx, lky = lhx - int(leg_sw*.5), lhy + int(30*s)
    lfx, lfy = lkx - int(leg_sw*.3), lky + int(28*s)
    rkx, rky = rhx + int(leg_sw*.5), rhy + int(30*s)
    rfx, rfy = rkx + int(leg_sw*.3), rky + int(28*s)

    arm_sw       = math.sin(snap_t * 3 + offset + math.pi) * 20 * sway_amp
    lsx, lsy     = nx - int(18*s), ny + int(10*s)
    lex, ley     = lsx - int(15*s) - int(arm_sw*.4), lsy + int(20*s)
    lhndx, lhndy = lex - int(10*s), ley + int(18*s)
    rsx, rsy     = nx + int(18*s), ny + int(10*s)
    rex, rey     = rsx + int(15*s) + int(arm_sw*.4), rsy + int(20*s)
    rhndx, rhndy = rex + int(10*s), rey + int(18*s)

    if show_strings:
        top_y = cy - int(110*s)
        for (px, py) in [(hx, hy-int(12*s)), (lhndx, lhndy),
                         (rhndx, rhndy), (lfx, lfy), (rfx, rfy)]:
            draw.line([(px, top_y), (px, py)],
                      fill=(180, 160, 120), width=max(1, int(s)))

    if robe_color:
        draw.polygon([
            (nx-int(20*s), ny), (nx+int(20*s), ny),
            (bx+int(35*s), by+int(55*s)), (bx-int(35*s), by+int(55*s)),
        ], fill=robe_color, outline=tuple(min(255, c+30) for c in robe_color))

    for seg in [(nx,ny,bx,by),(bx,by,lhx,lhy),(bx,by,rhx,rhy),
                (lhx,lhy,lkx,lky),(lkx,lky,lfx,lfy),
                (rhx,rhy,rkx,rky),(rkx,rky,rfx,rfy),
                (lsx,lsy,lex,ley),(lex,ley,lhndx,lhndy),
                (rsx,rsy,rex,rey),(rex,rey,rhndx,rhndy),(lsx,lsy,rsx,rsy)]:
        draw.line([seg[:2], seg[2:]], fill=PUPPET_COLOR, width=lw)

    jr = max(3, int(4*s))
    for (jx, jy) in [(nx,ny),(bx,by),(lhx,lhy),(rhx,rhy),(lkx,lky),
                     (rkx,rky),(lsx,lsy),(rsx,rsy),(lex,ley),(rex,rey)]:
        draw.ellipse([jx-jr,jy-jr,jx+jr,jy+jr],
                     fill=PUPPET_JOINT, outline=PUPPET_COLOR)

    hr = int(14*s)
    draw.ellipse([hx-hr, hy-hr*2, hx+hr, hy],
                 fill=PUPPET_COLOR, outline=PUPPET_JOINT, width=lw)
    draw.ellipse([hx-5, hy-hr, hx-2, hy-hr+4], fill=(20,10,5))
    draw.ellipse([hx+2, hy-hr, hx+5, hy-hr+4], fill=(20,10,5))
    draw.arc([hx-5, hy-hr//2, hx+5, hy-2], start=0, end=180, fill=(20,10,5), width=2)

# ─── DIEU ───────────────────────────────────────────────────────────
def draw_god(draw, cx, cy, frame, name="Athena",
             robe_color=None, scale=1.1, agitated=False):
    t      = frame / FPS
    sway   = math.sin(t * 1.2) * (10 if agitated else 5)
    floaty = math.sin(t * 0.9) * 5
    s      = scale
    rc     = robe_color if robe_color else ATHENA_ROBE
    glow   = GOD_GLOW

    for g in range(6, 0, -1):
        gr  = int(35 + g*9)
        col = tuple(int(c * g/6) for c in glow)
        draw.ellipse([cx-gr, cy-int(160*s)-gr, cx+gr, cy+int(30*s)+gr], fill=col)

    draw.polygon([
        (cx+sway-int(28*s), cy-int(28*s)+floaty),
        (cx+sway+int(28*s), cy-int(28*s)+floaty),
        (cx+sway+int(45*s), cy+int(85*s)+floaty),
        (cx+sway-int(45*s), cy+int(85*s)+floaty),
    ], fill=rc, outline=tuple(min(255, c+50) for c in rc))

    lw  = max(2, int(3*s))
    nx2 = cx+sway
    ny2 = cy-int(28*s)+floaty
    arm_t = math.sin(t * (2.0 if agitated else 1.2)) * 30
    lsx,lsy = nx2-int(22*s), ny2+int(8*s)
    lex,ley = nx2-int(45*s)-arm_t, ny2+int(38*s)
    lhx2,lhy2 = nx2-int(35*s)-arm_t*.5, ny2+int(62*s)
    rsx,rsy = nx2+int(22*s), ny2+int(8*s)
    rex,rey = nx2+int(45*s)+arm_t, ny2+int(38*s)
    rhx2,rhy2 = nx2+int(35*s)+arm_t*.5, ny2+int(62*s)

    for seg in [(lsx,lsy,lex,ley),(lex,ley,lhx2,lhy2),
                (rsx,rsy,rex,rey),(rex,rey,rhx2,rhy2)]:
        draw.line([seg[:2], seg[2:]], fill=GOD_SKIN, width=lw+1)

    hr  = int(18*s)
    hx2 = cx+sway
    hy2 = cy-int(62*s)+floaty
    draw.ellipse([hx2-hr-7, hy2-hr*2-7, hx2+hr+7, hy2+7], fill=glow)
    draw.ellipse([hx2-hr, hy2-hr*2, hx2+hr, hy2],
                 fill=GOD_SKIN, outline=(220,170,80), width=2)

    ey = hy2 - hr + (4 if agitated else 0)
    draw.ellipse([hx2-7, ey, hx2-3, ey+6], fill=(50,25,10))
    draw.ellipse([hx2+3, ey, hx2+7, ey+6], fill=(50,25,10))
    draw.ellipse([hx2-6, ey, hx2-5, ey+2], fill=(255,255,255))
    draw.ellipse([hx2+4, ey, hx2+5, ey+2], fill=(255,255,255))

    if agitated:
        draw.line([(hx2-8,ey-3),(hx2-2,ey-1)], fill=(80,40,10), width=2)
        draw.line([(hx2+2,ey-1),(hx2+8,ey-3)], fill=(80,40,10), width=2)
        draw.arc([hx2-5, hy2-hr//2, hx2+5, hy2-3],
                 start=180, end=360, fill=(160,60,60), width=2)
    else:
        draw.arc([hx2-5, hy2-hr//2, hx2+5, hy2-3],
                 start=0, end=180, fill=(180,80,80), width=2)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", int(16*s))
    except:
        font = ImageFont.load_default()
    draw.text((cx-25, cy-int(95*s)+floaty), name, fill=glow, font=font)

# ─── PARTICULES ─────────────────────────────────────────────────────
def draw_particles(draw, frame, intensity=1.0):
    rng = np.random.RandomState(frame // 3)
    for i in range(int(20 * intensity)):
        px = int(rng.uniform(WIDTH*0.2, WIDTH*0.8))
        py = int(rng.uniform(HEIGHT*0.1, HEIGHT*0.7)) - (frame % 30)*2
        r  = int(rng.uniform(1, 4))
        b  = int(rng.uniform(180, 255))
        draw.ellipse([px-r, py-r, px+r, py+r], fill=(b, int(b*.85), 50))

# ─── LYRICS ─────────────────────────────────────────────────────────
LYRICS = [
    (4,  7,  "Penelope is her name..."),
    (7,  10, "She\'s the smartest girl in the game"),
    (10, 13, "Seventeen was the age..."),
    (13, 16, "I knew that we\'d be engaged"),
    (16, 19, "She was out of this world..."),
    (19, 22, "So I asked for help..."),
    (22, 24, "\"You\'ve got to be kidding me\""),
    (24, 29, "Athena! You\'ve got to help me!"),
    (29, 35, "I need her to be MINE!"),
    (35, 41, "Believe it — I\'m in love!"),
]

def draw_lyrics(draw, frame):
    t = frame / FPS
    for (start, end, text) in LYRICS:
        if start <= t < end:
            alpha = 1.0
            if t < start + 0.4:   alpha = (t - start) / 0.4
            elif t > end - 0.4:   alpha = (end - t) / 0.4
            try:
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 28)
            except:
                font = ImageFont.load_default()
            color = tuple(int(c * alpha) for c in (255, 230, 120))
            draw.text((WIDTH//2 - len(text)*7 + 2, HEIGHT-72),
                      text, fill=(0,0,0), font=font)
            draw.text((WIDTH//2 - len(text)*7, HEIGHT-74),
                      text, fill=color, font=font)

# ─── BOUCLE PRINCIPALE ──────────────────────────────────────────────
print("Génération des frames EPIC: The Musical...")

for frame in range(TOTAL_FRAMES):
    img      = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw     = ImageDraw.Draw(img)
    ground_y = draw_background(draw, frame)
    scene    = get_scene(frame)
    t        = frame / FPS
    t_scene  = (frame - SCENE_STARTS[scene]) / TOTAL_FRAMES

    # ── INTRO (0–4s) ────────────────────────────────────────────────
    if scene == "intro":
        fade = clamp(t / 1.5, 0, 1)
        try:
            f_big = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 52)
            f_sub = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 26)
        except:
            f_big = f_sub = ImageFont.load_default()
        col = tuple(int(c * fade) for c in (255, 220, 80))
        draw.text((WIDTH//2-310, HEIGHT//2-70), "NEED HER TO BE MINE", fill=col, font=f_big)
        draw.text((WIDTH//2-175, HEIGHT//2+10), "EPIC: The Musical",   fill=col, font=f_sub)

    # ── ODYSSEUS CHANTE (4–13s) ──────────────────────────────────────
    elif scene == "odysseus_sings":
        draw_particles(draw, frame, 0.5)
        draw_puppet(draw, WIDTH//2, ground_y-145, frame,
                    offset=0.0, scale=1.05, sway_amp=1.5)
        heart_t = (frame % 20) / 20
        for i in range(3):
            hx = int(WIDTH//2 + math.sin(i*2.1)*80)
            hy = int(ground_y - 200 - heart_t*80 - i*30)
            draw.text((hx, hy), "♥", fill=(int(255*(1-heart_t)), 50, 80))

    # ── PENELOPE APPARAÎT (13–19s) ───────────────────────────────────
    elif scene == "penelope":
        draw_particles(draw, frame, 0.7)
        draw_puppet(draw, int(WIDTH*0.30), ground_y-145, frame,
                    offset=0.0, scale=1.0, sway_amp=1.2)
        pen_x = int(lerp(WIDTH+100, int(WIDTH*0.68),
                         ease_in_out(clamp(t_scene*6, 0, 1))))
        draw_puppet(draw, pen_x, ground_y-145, frame,
                    offset=1.5, scale=1.0, sway_amp=0.8,
                    robe_color=PENELOPE_ROBE)
        if t > 15:
            draw.line([(int(WIDTH*0.38), ground_y-180),
                       (int(WIDTH*0.60), ground_y-180)],
                      fill=(255,100,100), width=2)
            draw.polygon([(int(WIDTH*0.60), ground_y-185),
                          (int(WIDTH*0.60), ground_y-175),
                          (int(WIDTH*0.63), ground_y-180)],
                         fill=(255,100,100))

    # ── ODYSSEUS DEMANDE DE L'AIDE (19–22s) ─────────────────────────
    elif scene == "asks_help":
        draw_particles(draw, frame, 0.8)
        draw_puppet(draw, WIDTH//2, ground_y-145, frame,
                    offset=0.0, scale=1.1, sway_amp=2.0)
        ray_alpha = int(100 + 80 * pulse(t, 1.5))
        for rx in range(WIDTH//2-30, WIDTH//2+30, 8):
            draw.line([(rx, 0), (rx+20, ground_y-145)],
                      fill=(255, 220, 80), width=1)

    # ── ATHENA AGACÉE (22–24s) ───────────────────────────────────────
    elif scene == "athena_annoyed":
        draw_particles(draw, frame, 0.6)
        draw_puppet(draw, int(WIDTH*0.35), ground_y-145, frame,
                    offset=0.0, scale=1.0, sway_amp=0.5)
        ath_y = int(lerp(-50, ground_y-165,
                         ease_in_out(clamp(t_scene*8, 0, 1))))
        draw_god(draw, int(WIDTH*0.65), ath_y, frame,
                 name="Athena", robe_color=ATHENA_ROBE,
                 scale=1.15, agitated=True)
        bx2, by2 = int(WIDTH*0.65)+60, ath_y-55
        draw.rounded_rectangle([bx2, by2, bx2+280, by2+45],
                                radius=12, fill=(240,240,255),
                                outline=(100,100,200), width=2)
        try:
            fb = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 17)
        except:
            fb = ImageFont.load_default()
        draw.text((bx2+8, by2+10), "You've got to be kidding me",
                  fill=(40,40,120), font=fb)

    # ── ODYSSEUS SUPPLIE (24–29s) ────────────────────────────────────
    elif scene == "plea":
        draw_particles(draw, frame, 1.0)
        draw_puppet(draw, int(WIDTH*0.35), ground_y-120, frame,
                    offset=0.0, scale=1.05, sway_amp=0.4)
        draw_god(draw, int(WIDTH*0.65), ground_y-165, frame,
                 name="Athena", robe_color=ATHENA_ROBE,
                 scale=1.15, agitated=True)

    # ── CLIMAX (29–35s) ─────────────────────────────────────────────
    elif scene == "climax":
        draw_particles(draw, frame, 2.0)
        draw_particles(draw, frame+7, 1.5)
        draw_puppet(draw, WIDTH//2, ground_y-145, frame,
                    offset=0.0, scale=1.2, sway_amp=3.0)
        draw_puppet(draw, int(WIDTH*0.75), ground_y-145, frame,
                    offset=1.5, scale=1.0, sway_amp=0.5,
                    robe_color=PENELOPE_ROBE)
        draw_god(draw, int(WIDTH*0.20), ground_y-220, frame,
                 name="Athena", robe_color=ATHENA_ROBE,
                 scale=1.0, agitated=False)
        flash = int(30 * pulse(t, 4.0))
        if flash > 15:
            overlay = Image.new("RGB", (WIDTH, HEIGHT), (flash, flash, flash//2))
            img = Image.blend(img, overlay, 0.15)
            draw = ImageDraw.Draw(img)

    # ── FINALE (35–41s) ─────────────────────────────────────────────
    elif scene == "finale":
        draw_particles(draw, frame, 2.5)
        draw_particles(draw, frame+10, 1.5)
        draw_puppet(draw, int(WIDTH*0.20), ground_y-145, frame,
                    offset=0.0, scale=0.9, sway_amp=1.5)
        draw_puppet(draw, int(WIDTH*0.45), ground_y-145, frame,
                    offset=1.2, scale=1.1, sway_amp=2.0)
        draw_puppet(draw, int(WIDTH*0.70), ground_y-145, frame,
                    offset=2.4, scale=1.0, sway_amp=1.0,
                    robe_color=PENELOPE_ROBE)
        draw_god(draw, int(WIDTH*0.88), ground_y-165, frame,
                 name="Athena", robe_color=ATHENA_ROBE,
                 scale=1.05, agitated=False)
        fade_out = clamp((t - 37) / 4.0, 0, 1)
        if fade_out > 0:
            overlay = Image.new("RGB", (WIDTH, HEIGHT), (0,0,0))
            img = Image.blend(img, overlay, fade_out)
            draw = ImageDraw.Draw(img)

    draw_lyrics(draw, frame)
    img.save(f"{OUTPUT_DIR}/frame_{frame:04d}.png")
    if frame % FPS == 0:
        print(f"  {frame // FPS}s / {DURATION}s  [{scene}]")

# ─── ASSEMBLAGE MP4 ─────────────────────────────────────────────────
print("Assemblage MP4...")
video_clip = ImageSequenceClip(OUTPUT_DIR, fps=FPS)
try:
    audio_clip = AudioFileClip(MUSIC_FILE).subclipped(0, DURATION)
    final_clip = video_clip.with_audio(audio_clip)
    final_clip.write_videofile(OUTPUT_VIDEO, codec='libx264', audio_codec='aac')
    print(f"Vidéo avec musique : {OUTPUT_VIDEO}")
except Exception as e:
    print(f"Sans audio ({e})")
    video_clip.write_videofile(OUTPUT_VIDEO, codec='libx264')
    print(f"Vidéo sans audio : {OUTPUT_VIDEO}")
