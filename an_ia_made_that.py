"""
Ce script génère une vidéo MP4 du point de vue d'une IA (Caine).
Il intègre des animations de requêtes interactives avec une rupture psychologique
mise en scène par des glitchs "Genèse" et une Erreur Système massive et menaçante.
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
T_CONFRONT = 30.0 # Animation de requête (Typing) -> Glitch Boules -> System Error
T_SNAP = 40.0     # PÉTAGE DE PLOMBS (CHAOS TOTAL + RÉSEAU DE NEURONES)
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
    print("Génération de l'audio (Boot -> Requête -> Genèse Glitch -> CHAOS -> Delete)...")
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
    audio[mask_absorb] += 0.25 * np.random.randn(len(t))[mask_absorb]

    # 3. Reject
    mask_reject = (t >= T_GENESIS) & (t < T_REJECT)
    t_drop = t[mask_reject] - T_GENESIS
    pitch_drop = 300 * np.exp(-2 * t_drop)
    audio[mask_reject] = 0.15 * np.sin(2 * np.pi * pitch_drop * t_drop) + 0.05 * np.random.randn(len(t))[mask_reject]
    
    # 4. Confront (Typing -> Glitch Boules -> SYSTEM ERROR)
    mask_confront = (t >= T_REJECT) & (t < T_CONFRONT)
    
    # a. Typing
    mask_typing = (t >= T_REJECT) & (t < 27.5)
    typing = 0.25 * np.random.randn(len(t)) * (np.sin(2 * np.pi * 18 * t) > 0.4).astype(float)
    audio[mask_typing] += typing[mask_typing]
    
    # b. Glitch Boules ("I AM GOD" callback)
    mask_balls = (t >= 27.5) & (t < 28.5)
    screech_balls = 0.4 * np.sign(np.sin(2 * np.pi * 800 * t)) * np.random.randn(len(t))
    audio[mask_balls] += screech_balls[mask_balls]
    
    # c. SYSTEM ERROR (Bass drop lourd)
    mask_error = (t >= 28.5) & (t < T_CONFRONT)
    bass_error = 0.5 * np.sin(2 * np.pi * 40 * t) * np.exp(-2 * (t - 28.5))
    audio[mask_error] += bass_error[mask_error] + 0.1 * np.random.randn(len(t))[mask_error]
    
    # Tension drone
    drone_tension = 0.15 * np.sin(2 * np.pi * (40 + 5 * (t - T_REJECT)) * t)
    audio[mask_confront] += drone_tension[mask_confront]
    
    # 5. Snap
    mask_snap = (t >= T_CONFRONT) & (t < T_SNAP)
    screech = 0.4 * np.sign(np.sin(2 * np.pi * (100 + 1500 * np.random.rand(len(t))) * t))
    bass_roar = 0.3 * np.sin(2 * np.pi * 35 * t) * (1 + np.sin(2 * np.pi * 15 * t))
    audio[mask_snap] = screech[mask_snap] + bass_roar[mask_snap] + 0.2 * np.random.randn(len(t))[mask_snap]
    
    for ft in FLASH_TIMES:
        idx1, idx1_end = int(ft * SR), int((ft + 0.04) * SR)
        if idx1_end < len(t): shutter_audio = np.random.randn(idx1_end - idx1) * 1.0; audio[idx1:idx1_end] += shutter_audio
        idx2, idx2_end = int((ft + 0.08) * SR), int((ft + 0.15) * SR)
        if idx2_end < len(t): shutter_audio = np.random.randn(idx2_end - idx2) * 0.8; audio[idx2:idx2_end] += shutter_audio

    # 6. Delete
    mask_end = (t >= T_SNAP)
    idx_del, idx_del_end = int(T_SNAP * SR), int((T_SNAP + 0.2) * SR)
    if idx_del_end < len(t):
        audio[idx_del:idx_del_end] = 0.5 * np.sin(2 * np.pi * 1500 * t[idx_del:idx_del_end]) * np.exp(-np.linspace(0, 5, idx_del_end - idx_del))
        
    pop_time = T_SNAP + 1.5
    idx_pop, idx_pop_end = int(pop_time * SR), int((pop_time + 0.05) * SR)
    if idx_pop_end < len(t):
        audio[idx_pop:idx_pop_end] += 0.8 * np.random.randn(idx_pop_end - idx_pop) * np.exp(-np.linspace(0, 10, idx_pop_end - idx_pop))

    audio[mask_end] += 0.02 * np.random.randn(len(t))[mask_end]
    
    return AudioArrayClip(np.column_stack((audio, audio)), fps=SR)

# --- GÉNÉRATION DE L'IMAGE ---
random.seed(42)

words_snap = ["TORMENT", "PLACE", "CROCODILE", "KNIFE", "TRUCK", "FLAYED", "MONSTER", "SANG", "ABSTRACTION", "CENSURÉ"]
nodes = [[random.randint(20, RW-20), random.randint(20, RH-20), random.uniform(-10, 10), random.uniform(-10, 10), i] for i in range(60)]

# Lignes de requête
prompt_lines = [
    "> POMNI: \"We think your ideas suck!\"",
    "> CAINE: \"That's not... true.\"",
    "> POMNI: \"Yes it is! You're a failure!\"",
    "> ZOOBLE: \"What kind of all powerful being has such a fragile ego?!\"",
    "> JAX: \"You lie to us constantly!\"",
    "> POMNI: \"You just... don't... listen!\""
]

def apply_glitch(img, intensity=1.0, rgb_split=False, invert=False):
    if intensity > 1.0:
        dx, dy = random.randint(-10, 10), random.randint(-10, 10)
        img = ImageChops.offset(img, dx, dy)

    if random.random() < (0.5 * intensity):
        y = random.randint(0, RH - 30)
        h = random.randint(10, 50)
        shift = random.randint(-50, 50)
        region = img.crop((0, y, RW, y + h))
        img.paste(region, (shift, y))
    
    if rgb_split and random.random() < (0.7 * intensity):
        r, g, b = img.split()
        ox, oy = random.randint(-25, 25), random.randint(-10, 10)
        r = ImageChops.offset(r, ox, oy)
        b = ImageChops.offset(b, -ox, -oy)
        img = Image.merge("RGB", (r, g, b))
        
    if invert and random.random() < 0.2:
        img = ImageOps.invert(img)
        
    return img

def draw_shutter_image(draw, px, py, pw, ph, t):
    draw.rectangle((px, py, px+pw, py+ph), fill=(220, 220, 220))
    draw.rectangle((px+5, py+5, px+pw-5, py+ph-20), fill=(10, 10, 10))
    ix, iy, iw, ih = px+5, py+5, pw-10, ph-25
    
    fear_idx = int((t - T_CONFRONT) / 2.0) % 4
    
    if fear_idx == 0:
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(0, 40, 0))
        draw.polygon([(ix, iy+ih), (ix+iw, iy+ih), (ix+iw//2, iy+20)], fill=(0, 90, 0))
        for j in range(5):
            draw.polygon([(ix+15+j*30, iy+ih-20), (ix+35+j*30, iy+ih-20), (ix+25+j*30, iy+ih-70)], fill=(255, 255, 255))
        draw.ellipse((ix+iw//2-25, iy+50, ix+iw//2+25, iy+80), fill=(255, 255, 0))
        draw.ellipse((ix+iw//2-5, iy+50, ix+iw//2+5, iy+80), fill=(0, 0, 0))

    elif fear_idx == 1:
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(40, 0, 0))
        draw.ellipse((ix+iw//2-40, iy+ih//2-40, ix+iw//2+40, iy+ih//2+40), fill=(0, 0, 150))
        draw.line((ix, iy, ix+iw, iy+ih), fill=(255, 0, 0), width=8)
        for _ in range(6):
            cx, cy = ix + random.randint(20, iw-20), iy + random.randint(20, ih-20)
            draw.polygon([(cx-5, cy-40), (cx+5, cy-40), (cx+20, cy), (cx-20, cy)], fill=(200, 200, 200))

    elif fear_idx == 2:
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(15, 15, 15))
        draw.ellipse((ix+10, iy+ih//2-40, ix+80, iy+ih//2+40), fill=(255, 255, 255))
        draw.ellipse((ix+iw-80, iy+ih//2-40, ix+iw-10, iy+ih//2+40), fill=(255, 255, 255))
        draw.ellipse((ix+iw//2-30, iy+10, ix+iw//2+30, iy+90), outline=(255, 255, 255), width=4)
        draw.line((ix+iw//2-15, iy+10, ix+iw//2+15, iy+90), fill=(15, 15, 15), width=8)

    elif fear_idx == 3:
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
        
        if time_del < 1.5:
            pulse = int(2 * math.sin(time_del * 50))
            radius = max(1, 10 - int(time_del * 4) + pulse)
            cx, cy = RW // 2, RH // 2
            draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=(255, 0, 0))
            
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
            
        return np.array(img.resize((W, H), Image.NEAREST))

    # ================= PHASES 1 à 5 =================
    if t < 10.5:
        # Fond Bleu (Abel) se faisant progressivement dévorer
        img = Image.new('RGB', (RW, RH), (0, 0, 150))
    else:
        # Caine a totalement pris le contrôle
        img = Image.new('RGB', (RW, RH), (10, 10, 15))
        
    draw = ImageDraw.Draw(img)
    
    glitch_intensity = 0.0 
    rgb_split_active = False
    invert_colors = False

    if t < 10.5:
        # Taches rouges (Caine) qui se multiplient et grossissent
        for i in range(int(t * 40)): 
            random.seed(i)
            rx, ry = random.randint(0, RW), random.randint(0, RH)
            birth_time = i / 40.0
            age = max(0, t - birth_time)
            radius = int(age * 80) # Croissance rapide des taches
            draw.ellipse((rx-radius, ry-radius, rx+radius, ry+radius), fill=(180, 0, 0))
        random.seed()
        if t > 9.5: glitch_intensity = 1.0 # Glitch final de l'assimilation

    if t < T_BOOT:
        progress = t / T_BOOT
        # Contour noir autour du texte pour rester lisible sur l'invasion rouge
        draw.text((21, 21), "[C&A_SYS] INITIALISATION...", font=sys_font, fill=(0, 0, 0))
        draw.text((20, 20), "[C&A_SYS] INITIALISATION...", font=sys_font, fill=(100, 255, 100))
        
        bar_len = 40
        filled = int(progress * bar_len)
        bar_str = "[" + "=" * filled + " " * (bar_len - filled) + "]"
        draw.text((21, 81), bar_str, font=sys_font, fill=(0, 0, 0))
        draw.text((20, 80), bar_str, font=sys_font, fill=(255, 255, 255))
        
        if progress > 0.8: glitch_intensity = max(glitch_intensity, 0.3)

    elif t < T_GENESIS:
        if t > 10.5:
            # Après l'assimilation complète d'Abel
            draw.text((20, 20), "> SYSTEM OVERRIDE : CAINE ACTIVE.", font=sys_font, fill=(255, 50, 50))
            draw.text((20, 40), "> BIENVENUE DANS LE CIRQUE.", font=sys_font, fill=(255, 255, 255))

    elif t < T_REJECT:
        draw.rectangle((0, 0, RW, RH), fill=(20, 0, 20))
        glitch_intensity = 0.2

    elif t < T_CONFRONT:
        # T_CONFRONT est coupé en 3 sous-phases d'animation
        if t < 27.5:
            # 1. Animation Typing (avec impact renforcé sur la dernière ligne)
            draw.rectangle((0, 0, RW, RH), fill=(40, 0, 0))
            glitch_intensity = 0.5
            box_y = 40
            draw.rectangle((10, box_y, RW-10, RH-40), fill=(5, 5, 10), outline=(255, 50, 50), width=2)
            
            progress = (t - T_REJECT) / (27.5 - T_REJECT)
            total_chars = int(progress * 300) # Assure que le texte se termine avant 27.5
            
            chars_drawn = 0
            current_y = box_y + 10
            for line in prompt_lines:
                if chars_drawn >= total_chars: break
                chars_to_draw = min(len(line), total_chars - chars_drawn)
                displayed_text = line[:chars_to_draw]
                
                is_last_line = ("don't... listen!" in line)
                col = (255, 200, 50) if "> POMNI" in line or "> ZOOBLE" in line or "> JAX" in line else (200, 200, 200)
                
                # Effet d'impact intense pour Pomni
                if is_last_line:
                    col = (255, 50, 50)
                    if chars_to_draw > 0: glitch_intensity = max(glitch_intensity, 1.5)
                    
                if chars_to_draw == len(line) and chars_drawn + chars_to_draw == total_chars and int(t*10)%2==0:
                    displayed_text += "_"
                    
                # Rendu du texte avec effet gras/tremblant pour la phrase clé
                if is_last_line:
                    shake_x, shake_y = random.randint(-2, 2), random.randint(-2, 2)
                    draw.text((20+1+shake_x, current_y+shake_y), displayed_text, font=sys_font, fill=col)
                    draw.text((20+shake_x, current_y+1+shake_y), displayed_text, font=sys_font, fill=col)
                    draw.text((20+shake_x, current_y+shake_y), displayed_text, font=sys_font, fill=col)
                else:
                    draw.text((20, current_y), displayed_text, font=sys_font, fill=col)
                    
                chars_drawn += len(line)
                current_y += 25

        elif t < 28.5:
            # 2. Le Glitch "Genèse" des boules "I am GOD"
            glitch_intensity = 2.0
            invert_colors = random.choice([True, False])
            draw.rectangle((0, 0, RW, RH), fill=(0, 0, 0))
            
            # Avalanche de points rouges de Caine
            for _ in range(80):
                rx, ry = random.randint(0, RW), random.randint(0, RH)
                r_size = random.randint(10, 80)
                draw.ellipse((rx, ry, rx+r_size, ry+r_size), fill=(255, 0, 0))
            
            # Point bleu (Abel) clignotant
            if int(t * 20) % 2 == 0:
                cx, cy = RW//2, RH//2
                draw.ellipse((cx-100, cy-100, cx+100, cy+100), fill=(0, 0, 255))
                
        else:
            # 3. Le SYSTEM ERROR massif et menaçant sur tout l'écran
            glitch_intensity = 0.5
            rgb_split_active = True
            draw.rectangle((0, 0, RW, RH), fill=(30, 0, 0)) # Fond rouge très sombre
            
            # On dessine l'erreur sur une petite image pour la grossir violemment (effet pixel menaçant)
            err_img = Image.new('RGBA', (180, 40), (0,0,0,0))
            err_draw = ImageDraw.Draw(err_img)
            err_draw.text((5, 0), "SYSTEM_ERROR:", font=sys_font, fill=(255, 0, 0))
            err_draw.text((5, 15), "EGO FRACTURED.", font=sys_font, fill=(255, 255, 0))
            
            scale_factor = 4
            big_err = err_img.resize((180*scale_factor, 40*scale_factor), Image.NEAREST)
            
            bx = RW//2 - big_err.width//2 + random.randint(-5, 5)
            by = RH//2 - big_err.height//2 + random.randint(-5, 5)
            
            img.paste(big_err, (bx, by), big_err)

    elif t < T_SNAP:
        # LE CHAOS ABSOLU
        glitch_intensity = 2.5
        rgb_split_active = True
        invert_colors = True
        
        bg_col = int(100 + 155 * math.sin(t * 30))
        draw.rectangle((0, 0, RW, RH), fill=(bg_col, 0, 0))
        
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
        word_list, speed_mult, connect_dist = words_snap, 12.0, 200
            
        current_nodes = []
        for x, y, vx, vy, idx in nodes:
            nx = (x + vx * t * speed_mult) % RW
            ny = (y + vy * t * speed_mult) % RH
            current_nodes.append((nx, ny, word_list[idx % len(word_list)]))
            
        for i, (x1, y1, w1) in enumerate(current_nodes):
            if random.random() > 0.9: continue
            
            for j, (x2, y2, w2) in enumerate(current_nodes):
                if i < j:
                    dist = math.hypot(x2 - x1, y2 - y1)
                    if dist < connect_dist:
                        alpha = int(255 * (1 - dist / connect_dist))
                        col_line = (255, 0, 0)
                        draw.line((x1, y1, x2, y2), fill=col_line, width=2)
            
            col_text = (255, 255, 0) if random.random() > 0.5 else (255, 0, 0)
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