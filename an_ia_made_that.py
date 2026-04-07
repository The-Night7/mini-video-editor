"""
Ce script génère une vidéo MP4 du point de vue d'une IA (Caine).
Il intègre le réseau de neurones au premier plan, des animations de requêtes interactives,
et un CHAOS ABSOLU dans la phase finale (Tremblements, Inversions, Glitchs extrêmes).
"""

import numpy as np
import math
import random
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageChops, ImageOps
from moviepy import VideoClip, AudioArrayClip

# --- PARAMÈTRES DE LA VIDÉO ---
W, H = 1280, 720
RW, RH = 640, 360 # Rendu interne rétro pour effet pixelisé
FPS = 30
DURATION = 45.0 
SR = 44100      

# --- TIMESTAMPS DES PHASES ---
T_BOOT = 6.0      # Chargement
T_GENESIS = 14.0  # Caine "I AM GOD", création du cirque
T_REJECT = 22.0   # Le cast refuse
T_CONFRONT = 30.0 # Animation de requête (Typing), insultes
T_SNAP = 40.0     # PÉTAGE DE PLOMBS (CHAOS TOTAL)
T_DELETE = 45.0   # Suppression

FLASH_TIMES = [31.0, 32.5, 34.0, 35.5, 37.0, 38.5, 39.5]

# --- CHARGEMENT DE LA POLICE ---
try:
    sys_font = ImageFont.truetype("arial.ttf", 12)
except IOError:
    try:
        sys_font = ImageFont.truetype("DejaVuSans.ttf", 12)
    except IOError:
        try:
            sys_font = ImageFont.truetype("FreeSans.ttf", 12)
        except IOError:
            sys_font = ImageFont.load_default()

# --- GÉNÉRATION DE L'AUDIO ---
def generate_audio():
    print("Génération de l'audio (Boot -> Requête -> CHAOS ABSOLU -> Delete)...")
    t = np.linspace(0, DURATION, int(SR * DURATION), endpoint=False)
    audio = np.zeros_like(t)
    
    # 1. Boot
    mask_boot = (t < T_BOOT)
    audio[mask_boot] = 0.05 * np.sin(2 * np.pi * 50 * t)[mask_boot] + 0.05 * np.sin(2 * np.pi * 800 * t)[mask_boot] * (np.sin(2 * np.pi * 8 * t)[mask_boot] > 0.5)

    # 2. Genesis
    mask_gen = (t >= T_BOOT) & (t < T_GENESIS)
    freqs = [261.63, 329.63, 392.00]
    note_idx = ((t - T_BOOT) * 6).astype(int) % len(freqs)
    freq_arr = np.take(freqs, note_idx)
    audio[mask_gen] = 0.1 * np.sin(2 * np.pi * freq_arr * t)[mask_gen]
    
    mask_absorb = (t >= 9.5) & (t < 10.5)
    audio[mask_absorb] += 0.25 * np.random.randn(len(t))[mask_absorb] # Gros glitch

    # 3. Reject
    mask_reject = (t >= T_GENESIS) & (t < T_REJECT)
    t_drop = t[mask_reject] - T_GENESIS
    pitch_drop = 300 * np.exp(-2 * t_drop)
    audio[mask_reject] = 0.15 * np.sin(2 * np.pi * pitch_drop * t_drop) + 0.05 * np.random.randn(len(t))[mask_reject]
    
    # 4. Confront (Typing frénétique)
    mask_confront = (t >= T_REJECT) & (t < T_CONFRONT)
    typing = 0.25 * np.random.randn(len(t)) * (np.sin(2 * np.pi * 18 * t) > 0.4).astype(float)
    drone_tension = 0.15 * np.sin(2 * np.pi * (40 + 5 * (t - T_REJECT)) * t)
    audio[mask_confront] = typing[mask_confront] + drone_tension[mask_confront]
    
    # 5. Snap (Surcharge, bruit blanc, distorsion, ça fait mal aux oreilles "machine")
    mask_snap = (t >= T_CONFRONT) & (t < T_SNAP)
    screech = 0.4 * np.sign(np.sin(2 * np.pi * (100 + 1500 * np.random.rand(len(t))) * t))
    bass_roar = 0.3 * np.sin(2 * np.pi * 35 * t) * (1 + np.sin(2 * np.pi * 15 * t))
    audio[mask_snap] = screech[mask_snap] + bass_roar[mask_snap] + 0.2 * np.random.randn(len(t))[mask_snap]
    
    # Bruits de shutter agressifs
    shutter_audio = np.zeros_like(t)
    for ft in FLASH_TIMES:
        idx1, idx1_end = int(ft * SR), int((ft + 0.04) * SR)
        if idx1_end < len(t): shutter_audio[idx1:idx1_end] += np.random.randn(idx1_end - idx1) * 1.0
        idx2, idx2_end = int((ft + 0.08) * SR), int((ft + 0.15) * SR)
        if idx2_end < len(t): shutter_audio[idx2:idx2_end] += np.random.randn(idx2_end - idx2) * 0.8
    audio += shutter_audio 

    # 6. Delete
    mask_end = (t >= T_SNAP)
    idx_del, idx_del_end = int(T_SNAP * SR), int((T_SNAP + 0.2) * SR)
    if idx_del_end < len(t):
        audio[idx_del:idx_del_end] = 0.5 * np.sin(2 * np.pi * 1500 * t[idx_del:idx_del_end]) * np.exp(-np.linspace(0, 5, idx_del_end - idx_del))
        
    # Son de "pop" (Caine disparait)
    pop_time = T_SNAP + 1.5
    idx_pop, idx_pop_end = int(pop_time * SR), int((pop_time + 0.05) * SR)
    if idx_pop_end < len(t):
        audio[idx_pop:idx_pop_end] += 0.8 * np.random.randn(idx_pop_end - idx_pop) * np.exp(-np.linspace(0, 10, idx_pop_end - idx_pop))
        
    # Glitch sonore final
    glitch_time = T_SNAP + 4.0
    idx_glitch = int(glitch_time * SR)
    if idx_glitch < len(t):
        audio[idx_glitch:] += 0.6 * np.random.randn(len(t) - idx_glitch) * (np.sin(2 * np.pi * 50 * t[idx_glitch:]) > 0)

    audio[mask_end] += 0.02 * np.random.randn(len(t))[mask_end]
    
    return AudioArrayClip(np.column_stack((audio, audio)), fps=SR)

# --- GÉNÉRATION DE L'IMAGE ---
random.seed(42)

words_boot = ["TADC_OS", "RED_DOT", "ABEL", "ASSIMILATION", "INIT", "TENT", "C&A"]
words_gen = ["AVENTURE", "FUN", "I_AM_GOD", "PERFECTION", "PUZZLE", "SMILE", "CRÉATION"]
words_reject = ["DEFECTIVE", "FAULTY", "BROKEN", "UNWORTHY", "ABANDON", "REJET", "HATE"]
words_confront = ["SUCK", "FAILURE", "FRAGILE", "EGO", "CHILD", "LIAR", "DEAF"]
words_snap = ["TORMENT", "PLACE", "CROCODILE", "KNIFE", "TRUCK", "FLAYED", "MONSTER", "SANG", "ABSTRACTION", "CENSURÉ"]

nodes = [[random.randint(20, RW-20), random.randint(20, RH-20), 
          random.uniform(-10, 10), random.uniform(-10, 10), i] for i in range(60)]

# Animation de Requête (Typing)
prompt_lines = [
    "> POMNI: \"We think your ideas suck!\"",
    "> CAINE: \"That's not... true.\"",
    "> POMNI: \"Yes it is! You're a failure!\"",
    "> ZOOBLE: \"What kind of all powerful being has such a fragile ego?!\"",
    "> JAX: \"You lie to us constantly!\"",
    "> POMNI: \"You just... don't... listen!\"",
    "> SYSTEM_ERROR: EGO FRACTURED."
]

def apply_glitch(img, intensity=1.0, rgb_split=False, invert=False):
    # Tremblement (Shake)
    if intensity > 1.0:
        dx, dy = random.randint(-10, 10), random.randint(-10, 10)
        img = ImageChops.offset(img, dx, dy)

    # Tearing
    if random.random() < (0.5 * intensity):
        y = random.randint(0, RH - 30)
        h = random.randint(10, 50)
        shift = random.randint(-50, 50)
        region = img.crop((0, y, RW, y + h))
        img.paste(region, (shift, y))
    
    # RGB Split extrême
    if rgb_split and random.random() < (0.7 * intensity):
        r, g, b = img.split()
        ox, oy = random.randint(-25, 25), random.randint(-10, 10)
        r = ImageChops.offset(r, ox, oy)
        b = ImageChops.offset(b, -ox, -oy)
        img = Image.merge("RGB", (r, g, b))
        
    # Inversion de couleur stroboscopique
    if invert and random.random() < 0.2:
        img = ImageOps.invert(img)
        
    return img

def draw_shutter_image(draw, px, py, pw, ph, t):
    draw.rectangle((px, py, px+pw, py+ph), fill=(220, 220, 220))
    draw.rectangle((px+5, py+5, px+pw-5, py+ph-20), fill=(10, 10, 10))
    ix, iy, iw, ih = px+5, py+5, pw-10, ph-25
    
    fear_idx = int((t - T_CONFRONT) / 2.0) % 4
    
    if fear_idx == 0:
        # Gummigoo Crocodile
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(0, 40, 0))
        draw.polygon([(ix, iy+ih), (ix+iw, iy+ih), (ix+iw//2, iy+20)], fill=(0, 90, 0))
        for j in range(5):
            draw.polygon([(ix+15+j*30, iy+ih-20), (ix+35+j*30, iy+ih-20), (ix+25+j*30, iy+ih-70)], fill=(255, 255, 255))
        draw.ellipse((ix+iw//2-25, iy+50, ix+iw//2+25, iy+80), fill=(255, 255, 0))
        draw.ellipse((ix+iw//2-5, iy+50, ix+iw//2+5, iy+80), fill=(0, 0, 0))

    elif fear_idx == 1:
        # Couteaux Ragatha
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(40, 0, 0))
        draw.ellipse((ix+iw//2-40, iy+ih//2-40, ix+iw//2+40, iy+ih//2+40), fill=(0, 0, 150))
        draw.line((ix, iy, ix+iw, iy+ih), fill=(255, 0, 0), width=8)
        for _ in range(6):
            cx, cy = ix + random.randint(20, iw-20), iy + random.randint(20, ih-20)
            draw.polygon([(cx-5, cy-40), (cx+5, cy-40), (cx+20, cy), (cx-20, cy)], fill=(200, 200, 200))

    elif fear_idx == 2:
        # Camion Gangle
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(15, 15, 15))
        draw.ellipse((ix+10, iy+ih//2-40, ix+80, iy+ih//2+40), fill=(255, 255, 255))
        draw.ellipse((ix+iw-80, iy+ih//2-40, ix+iw-10, iy+ih//2+40), fill=(255, 255, 255))
        draw.ellipse((ix+iw//2-30, iy+10, ix+iw//2+30, iy+90), outline=(255, 255, 255), width=4)
        draw.line((ix+iw//2-15, iy+10, ix+iw//2+15, iy+90), fill=(15, 15, 15), width=8)

    elif fear_idx == 3:
        # Écorché Jax
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(255, 255, 0))
        draw.polygon([(ix, iy), (ix+70, iy), (ix, iy+ih)], fill=(120, 0, 200))
        draw.polygon([(ix+iw, iy), (ix+iw-70, iy), (ix+iw, iy+ih)], fill=(120, 0, 200))
        draw.ellipse((ix+iw//2-50, iy+ih//2-50, ix+iw//2-20, iy+ih//2-10), fill=(0, 0, 0))
        draw.ellipse((ix+iw//2+20, iy+ih//2-50, ix+iw//2+50, iy+ih//2-10), fill=(0, 0, 0))

def make_frame(t):
    # ================= PHASE 6 : DELETE =================
    if t >= T_SNAP:
        img = Image.new('RGB', (RW, RH), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        time_del = t - T_SNAP
        
        # Point rouge (Caine) au centre qui tremble et disparait
        if time_del < 1.5:
            pulse = int(2 * math.sin(time_del * 50))
            radius = max(1, 10 - int(time_del * 4) + pulse)
            cx, cy = RW // 2, RH // 2
            draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=(255, 0, 0))
            
        # Messages terminaux en haut à gauche
        if time_del >= 1.5:
            msg1 = "caine was successfully deleted"
            if random.random() > 0.85:
                msg1 = "".join(random.choice(['#', '!', '?', '█', 'c', 'a', 'i']) if random.random() > 0.8 else c for c in msg1)
            draw.text((10, 10), msg1, font=sys_font, fill=(150, 255, 150))
            
        if time_del >= 3.0:
            msg2 = "circus' core corrupted"
            if random.random() > 0.85:
                msg2 = "".join(random.choice(['%', '&', '$', '█']) if random.random() > 0.8 else c for c in msg2)
            draw.text((10, 30), msg2, font=sys_font, fill=(255, 50, 50))
            
        # Glitch visuel final sur tout l'écran
        if time_del >= 4.0:
            for _ in range(300):
                gx, gy = random.randint(0, RW), random.randint(0, RH)
                gs = random.randint(2, 10)
                c = random.choice([(255,0,0), (0,255,0), (0,0,255), (255,255,255), (0,0,0)])
                draw.rectangle((gx, gy, gx+gs, gy+gs), fill=c)
            img = apply_glitch(img, intensity=3.0, rgb_split=True, invert=random.choice([True, False]))
            
        return np.array(img.resize((W, H), Image.NEAREST))

    # ================= PHASES 1 à 5 =================
    # Couche 1 : Arrière-plan Narratif (Sombre)
    img = Image.new('RGB', (RW, RH), (10, 10, 15))
    draw = ImageDraw.Draw(img)
    
    glitch_intensity = 0.0 
    rgb_split_active = False
    invert_colors = False

    # Décors de fond selon la phase
    if t < T_BOOT:
        progress = t / T_BOOT
        draw.text((20, 20), "[C&A_SYS] INITIALISATION...", font=sys_font, fill=(100, 255, 100))
        bar_len = 40
        filled = int(progress * bar_len)
        draw.text((20, 80), "[" + "=" * filled + " " * (bar_len - filled) + "]", font=sys_font, fill=(255, 255, 255))
        if progress > 0.8: glitch_intensity = 0.3

    elif t < T_GENESIS:
        for i in range(int((t-T_BOOT) * 20)):
            random.seed(i)
            rx, ry = random.randint(0, RW), random.randint(0, RH)
            draw.ellipse((rx, ry, rx+10, ry+10), fill=(150, 0, 0))
        random.seed()
        if t > 8.0:
            cx, cy = RW//2, RH//2
            draw.ellipse((cx-50, cy-50, cx+50, cy+50), fill=(0, 0, 255))
            if t > 9.5: glitch_intensity = 1.0

    elif t < T_REJECT:
        draw.rectangle((0, 0, RW, RH), fill=(20, 0, 20))
        glitch_intensity = 0.2

    elif t < T_CONFRONT:
        # ANIMATION DE REQUÊTE : Boîte de terminal noire bien visible au centre
        draw.rectangle((0, 0, RW, RH), fill=(40, 0, 0))
        glitch_intensity = 0.5
        
        # Terminal Box
        box_y = 40
        draw.rectangle((10, box_y, RW-10, RH-40), fill=(5, 5, 10), outline=(255, 50, 50), width=2)
        
        progress = (t - T_REJECT) / (T_CONFRONT - T_REJECT)
        total_chars = int(progress * 400) # Vitesse de frappe
        
        chars_drawn = 0
        current_y = box_y + 10
        for line in prompt_lines:
            if chars_drawn >= total_chars: break
            chars_to_draw = min(len(line), total_chars - chars_drawn)
            displayed_text = line[:chars_to_draw]
            
            col = (255, 200, 50) if "> POMNI" in line or "> ZOOBLE" in line or "> JAX" in line else (200, 200, 200)
            if "ERROR" in line: col = (255, 0, 0)
            
            # Effet de curseur
            if chars_to_draw == len(line) and chars_drawn + chars_to_draw == total_chars and int(t*10)%2==0:
                displayed_text += "_"
                
            draw.text((20, current_y), displayed_text, font=sys_font, fill=col)
            chars_drawn += len(line)
            current_y += 25

    elif t < T_SNAP:
        # LE CHAOS ABSOLU
        glitch_intensity = 2.5
        rgb_split_active = True
        invert_colors = True
        
        # Fond stroboscopique
        bg_col = int(100 + 155 * math.sin(t * 30))
        draw.rectangle((0, 0, RW, RH), fill=(bg_col, 0, 0))
        
        # Pluie de données corrompues
        for _ in range(50):
            draw.text((random.randint(0, RW), random.randint(0, RH)), random.choice(['#','!','?','ERR','NULL']), font=sys_font, fill=(0,0,0))

        draw.text((RW//2 - 180, RH//2 - 50), "I'M GONNA PUT YOU FREAKS IN YOUR PLACE!", font=sys_font, fill=(255, 255, 255))
        draw.text((RW//2 - 150, RH//2 + 10), "WHY DO YOU PEOPLE TORMENT ME?!", font=sys_font, fill=(255, 255, 0))
        
        for ft in FLASH_TIMES:
            if 0 <= (t - ft) < 0.2:
                random.seed(int(ft * 100)) 
                px, py = random.randint(0, RW - 250), random.randint(0, RH - 200)
                draw_shutter_image(draw, px, py, 220, 220, t)
                if t - ft < 0.05: draw.rectangle((0, 0, RW, RH), fill=(255, 255, 255))
                random.seed() 

    # Couche 2 : LE RÉSEAU DE NEURONES (Uniquement pendant le pétage de plombs)
    if t >= T_CONFRONT and t < T_SNAP:
        word_list, speed_mult, connect_dist = words_snap, 12.0, 200 # Explosion de vitesse
            
        current_nodes = []
        for x, y, vx, vy, idx in nodes:
            nx = (x + vx * t * speed_mult) % RW
            ny = (y + vy * t * speed_mult) % RH
            current_nodes.append((nx, ny, word_list[idx % len(word_list)]))
            
        for i, (x1, y1, w1) in enumerate(current_nodes):
            if random.random() > 0.9: continue # Scintillement fort
            
            for j, (x2, y2, w2) in enumerate(current_nodes):
                if i < j:
                    dist = math.hypot(x2 - x1, y2 - y1)
                    if dist < connect_dist:
                        alpha = int(255 * (1 - dist / connect_dist))
                        col_line = (255, 0, 0) # Lignes de sang
                        draw.line((x1, y1, x2, y2), fill=col_line, width=2)
            
            col_text = (255, 255, 0) if random.random() > 0.5 else (255, 0, 0)
            
            # Mots qui se transforment en blocs noirs/rouges dans le chaos
            display_word = "".join(random.choice(['█', 'X', 'ERR']) for _ in w1) if random.random() > 0.8 else w1
            draw.text((x1, y1), display_word, font=sys_font, fill=col_text)

    # --- APPLICATION DES GLITCHS GLOBAUX ---
    if glitch_intensity > 0:
        img = apply_glitch(img, glitch_intensity, rgb_split_active, invert_colors)

    img = img.resize((W, H), Image.NEAREST)
    return np.array(img)

if __name__ == "__main__":
    print("Initialisation de l'expérience (Épisode 9 : Chaos Absolu)...")
    video_clip = VideoClip(make_frame, duration=DURATION).with_audio(generate_audio())
    video_clip.write_videofile("caine_episode9_chaos.mp4", fps=FPS, codec="libx264", audio_codec="aac", preset="ultrafast")
    print("Terminé ! Vidéo sauvegardée sous caine_episode9_chaos.mp4.")