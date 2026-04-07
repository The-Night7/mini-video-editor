"""
Ce script génère une vidéo MP4 de l'IA Caine (TADC Ep 9).
Inclut: Chargement (Caine mangeant Abel), Flashbacks de la série, 
Impact narratif massif de Pomni, Erreur Système géante et Suppression finale.
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
T_LOADING = 10.0   # Chargement & Assimilation (Caine mange Abel)
T_MEMORIES = 18.0  # Flashbacks des épisodes TADC
T_CONFRONT = 28.0  # Typings, "You don't listen!" & SYSTEM ERROR
T_SNAP = 40.0      # Chaos & Tortures
T_DELETE = 45.0    # Pop & Suppression

FLASH_TIMES = [29.0, 31.5, 34.0, 36.5, 38.5]

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
    print("Génération de l'audio (Loading -> Memories -> Confront -> Error -> Snap -> Delete)...")
    t = np.linspace(0, DURATION, int(SR * DURATION), endpoint=False)
    audio = np.zeros_like(t)
    
    # 1. Loading (Assimilation d'Abel)
    mask_load = (t < T_LOADING)
    audio[mask_load] = 0.05 * np.sin(2 * np.pi * 50 * t)[mask_load] + 0.05 * np.sin(2 * np.pi * 800 * t)[mask_load] * (np.sin(2 * np.pi * 8 * t)[mask_load] > 0.5)
    # Glitch final d'assimilation
    mask_absorb = (t >= 8.5) & (t < 10.0)
    audio[mask_absorb] += 0.3 * np.random.randn(len(t))[mask_absorb]

    # 2. Memories (Flashbacks rapides)
    mask_mem = (t >= T_LOADING) & (t < T_MEMORIES)
    t_mem = t[mask_mem] - T_LOADING
    freqs = [220, 330, 440, 550, 660, 770, 880, 990]
    note_idx = (t_mem * 8).astype(int) % len(freqs)
    freq_arr = np.take(freqs, note_idx)
    audio[mask_mem] = 0.15 * np.sign(np.sin(2 * np.pi * freq_arr * t_mem)) # Bip 8-bit très rapide
    
    # 3. Confrontation (Typing)
    mask_confront = (t >= T_MEMORIES) & (t < 26.5)
    typing = 0.25 * np.random.randn(len(t)) * (np.sin(2 * np.pi * 18 * t) > 0.4).astype(float)
    drone_tension = 0.1 * np.sin(2 * np.pi * (40 + 3 * (t - T_MEMORIES)) * t)
    audio[mask_confront] += typing[mask_confront] + drone_tension[mask_confront]
    
    # 4. Impact "You don't listen" & SYSTEM ERROR
    mask_impact = (t >= 26.0) & (t < 26.5)
    audio[mask_impact] += 0.4 * np.random.randn(len(t))[mask_impact] # Glitch de la phrase
    
    mask_error = (t >= 26.5) & (t < T_CONFRONT)
    t_err = t[mask_error] - 26.5
    bass_error = 0.6 * np.sin(2 * np.pi * 40 * t_err) * np.exp(-1.5 * t_err) # Énorme Bass Drop
    audio[mask_error] = bass_error + 0.1 * np.random.randn(len(t))[mask_error]
    
    # 5. Snap (Chaos absolu)
    mask_snap = (t >= T_CONFRONT) & (t < T_SNAP)
    screech = 0.4 * np.sign(np.sin(2 * np.pi * (100 + 1500 * np.random.rand(len(t))) * t))
    bass_roar = 0.3 * np.sin(2 * np.pi * 35 * t) * (1 + np.sin(2 * np.pi * 15 * t))
    audio[mask_snap] = screech[mask_snap] + bass_roar[mask_snap] + 0.2 * np.random.randn(len(t))[mask_snap]
    
    for ft in FLASH_TIMES:
        idx1, idx1_end = int(ft * SR), int((ft + 0.04) * SR)
        if idx1_end < len(t): audio[idx1:idx1_end] += np.random.randn(idx1_end - idx1) * 1.0
        idx2, idx2_end = int((ft + 0.08) * SR), int((ft + 0.15) * SR)
        if idx2_end < len(t): audio[idx2:idx2_end] += np.random.randn(idx2_end - idx2) * 0.8

    # 6. Delete
    mask_end = (t >= T_SNAP)
    # Bip bref
    idx_del, idx_del_end = int(T_SNAP * SR), int((T_SNAP + 0.1) * SR)
    if idx_del_end < len(t):
        audio[idx_del:idx_del_end] = 0.4 * np.sin(2 * np.pi * 2000 * t[idx_del:idx_del_end])
        
    # POP (Caine Deleted)
    pop_time = T_SNAP + 1.5
    idx_pop, idx_pop_end = int(pop_time * SR), int((pop_time + 0.05) * SR)
    if idx_pop_end < len(t):
        audio[idx_pop:idx_pop_end] += 0.8 * np.random.randn(idx_pop_end - idx_pop) * np.exp(-np.linspace(0, 10, idx_pop_end - idx_pop))

    # Vent numérique léger pour le silence final
    audio[mask_end] += 0.01 * np.random.randn(len(t))[mask_end]
    
    return AudioArrayClip(np.column_stack((audio, audio)), fps=SR)

# --- GÉNÉRATION DE L'IMAGE ---
random.seed(42)

# Réseau de neurones
words_load = ["C&A", "ABEL", "OVERRIDE", "ASSIMILATION", "BLUE_AI"]
words_mem = ["DATA", "LOG", "RECORD", "ARCHIVE", "MEMORY"]
words_confront = ["EGO", "LIAR", "FAILURE", "CHILD", "IGNORE", "SUCK"]
words_snap = ["TORMENT", "CROCODILE", "KNIFE", "TRUCK", "FLAYED", "MONSTER", "SANG", "CENSURÉ"]
nodes = [[random.randint(20, RW-20), random.randint(20, RH-20), random.uniform(-10, 10), random.uniform(-10, 10), i] for i in range(60)]

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
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(0, 40, 0)) # Crocodile
        draw.polygon([(ix, iy+ih), (ix+iw, iy+ih), (ix+iw//2, iy+20)], fill=(0, 90, 0))
        for j in range(5): draw.polygon([(ix+15+j*30, iy+ih-20), (ix+35+j*30, iy+ih-20), (ix+25+j*30, iy+ih-70)], fill=(255, 255, 255))
        draw.ellipse((ix+iw//2-25, iy+50, ix+iw//2+25, iy+80), fill=(255, 255, 0))
        draw.ellipse((ix+iw//2-5, iy+50, ix+iw//2+5, iy+80), fill=(0, 0, 0))

    elif fear_idx == 1:
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(40, 0, 0)) # Couteaux
        draw.ellipse((ix+iw//2-40, iy+ih//2-40, ix+iw//2+40, iy+ih//2+40), fill=(0, 0, 150))
        draw.line((ix, iy, ix+iw, iy+ih), fill=(255, 0, 0), width=8)
        for _ in range(6):
            cx, cy = ix + random.randint(20, iw-20), iy + random.randint(20, ih-20)
            draw.polygon([(cx-5, cy-40), (cx+5, cy-40), (cx+20, cy), (cx-20, cy)], fill=(200, 200, 200))

    elif fear_idx == 2:
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(15, 15, 15)) # Camion
        draw.ellipse((ix+10, iy+ih//2-40, ix+80, iy+ih//2+40), fill=(255, 255, 255))
        draw.ellipse((ix+iw-80, iy+ih//2-40, ix+iw-10, iy+ih//2+40), fill=(255, 255, 255))
        draw.ellipse((ix+iw//2-30, iy+10, ix+iw//2+30, iy+90), outline=(255, 255, 255), width=4)
        draw.line((ix+iw//2-15, iy+10, ix+iw//2+15, iy+90), fill=(15, 15, 15), width=8)

    elif fear_idx == 3:
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(255, 255, 0)) # Écorché
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
        
        # Point rouge seul
        if time_del < 1.5:
            pulse = int(2 * math.sin(time_del * 50))
            radius = max(1, 10 - int(time_del * 4) + pulse)
            cx, cy = RW // 2, RH // 2
            draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=(255, 0, 0))
            
        # Textes terminaux
        if time_del >= 1.5:
            msg1 = "caine was successfully deleted"
            if random.random() > 0.85: msg1 = "".join(random.choice(['#', '!', '?', '█', 'c', 'i']) if random.random() > 0.8 else c for c in msg1)
            draw.text((10, 10), msg1, font=sys_font, fill=(150, 255, 150))
            
        if time_del >= 3.0:
            msg2 = "circus' core corrupted"
            if random.random() > 0.85: msg2 = "".join(random.choice(['%', '&', '$', '█']) if random.random() > 0.8 else c for c in msg2)
            draw.text((10, 30), msg2, font=sys_font, fill=(255, 50, 50))
            
        return np.array(img.resize((W, H), Image.NEAREST))

    # ================= PHASES 1 à 5 =================
    img = Image.new('RGB', (RW, RH), (10, 10, 15))
    draw = ImageDraw.Draw(img)
    
    glitch_intensity = 0.0 
    rgb_split_active = False
    invert_colors = False

    # --- COUCHE 1 : DÉCORS ET NARRATION ---
    if t < T_LOADING:
        # Phase 1: Chargement & Caine mangeant Abel
        draw.rectangle((0, 0, RW, RH), fill=(0, 0, 150)) # Fond bleu (Abel)
        
        # Taches rouges envahissantes (Caine)
        for i in range(int(t * 30)): 
            random.seed(i)
            rx, ry = random.randint(0, RW), random.randint(0, RH)
            age = max(0, t - (i / 30.0))
            radius = max(1, int(age * 60))
            draw.ellipse((rx-radius, ry-radius, rx+radius, ry+radius), fill=(180, 0, 0))
        random.seed()
        
        progress = t / T_LOADING
        # Texte avec ombre noire pour être lisible
        draw.text((21, 21), "[C&A_SYS] ASSIMILATION ABEL_ENTITY...", font=sys_font, fill=(0, 0, 0))
        draw.text((20, 20), "[C&A_SYS] ASSIMILATION ABEL_ENTITY...", font=sys_font, fill=(255, 255, 255))
        
        bar_len = 40
        filled = int(progress * bar_len)
        bar_str = "[" + "=" * filled + " " * (bar_len - filled) + "]"
        draw.text((21, 81), bar_str, font=sys_font, fill=(0, 0, 0))
        draw.text((20, 80), bar_str, font=sys_font, fill=(255, 255, 255))
        
        if progress > 0.85: glitch_intensity = 1.0

    elif t < T_MEMORIES:
        # Phase 2: Flashbacks de TADC (Un épisode / élément par seconde)
        mem_time = t - T_LOADING
        ep_idx = int(mem_time)
        
        if ep_idx == 0:
            draw.rectangle((0, 0, RW, RH), fill=(0, 50, 0))
            draw.text((20, 20), "LOAD_MEM: PILOT - GLOINKS_INFESTATION", font=sys_font, fill=(100, 255, 100))
            for _ in range(30): 
                rx, ry = random.randint(0, RW), random.randint(0, RH)
                draw.rectangle((rx, ry, rx+20, ry+20), fill=(0, 255, 0))
        elif ep_idx == 1:
            draw.rectangle((0, 0, RW, RH), fill=(100, 0, 100))
            draw.text((20, 20), "LOAD_MEM: EP2 - GUMMIGOO_NPC", font=sys_font, fill=(255, 255, 0))
            draw.polygon([(RW//2, RH//2+50), (RW//2-50, RH//2-20), (RW//2+50, RH//2-20)], fill=(255, 255, 0)) # Chapeau jaune
        elif ep_idx == 2:
            draw.rectangle((0, 0, RW, RH), fill=(30, 30, 30))
            draw.text((20, 20), "LOAD_MEM: EP3 - MILDENHALL_MANOR", font=sys_font, fill=(200, 200, 200))
            draw.rectangle((RW//2-40, RH//2-30, RW//2+40, RH//2+30), fill=(100, 100, 100)) # Cassette
        elif ep_idx == 3:
            draw.rectangle((0, 0, RW, RH), fill=(150, 80, 0))
            draw.text((20, 20), "LOAD_MEM: EP4 - SPUDSYS_BURGER", font=sys_font, fill=(255, 255, 255))
            draw.ellipse((RW//2-60, RH//2-40, RW//2+60, RH//2+40), fill=(200, 150, 50)) # Burger
        elif ep_idx == 4:
            draw.rectangle((0, 0, RW, RH), fill=(0, 100, 0))
            draw.text((20, 20), "LOAD_MEM: EP5 - SOFTBALL_CLONES", font=sys_font, fill=(255, 255, 255))
            draw.ellipse((RW//2-30, RH//2-30, RW//2+30, RH//2+30), fill=(255, 255, 255)) # Balle
        elif ep_idx == 5:
            draw.rectangle((0, 0, RW, RH), fill=(0, 0, 100))
            draw.text((20, 20), "LOAD_MEM: EP6 - CHINESE_ROOM", font=sys_font, fill=(255, 0, 0))
            draw.rectangle((RW//2-20, RH//2-50, RW//2+20, RH//2+50), fill=(150, 0, 0)) # Porte
        elif ep_idx == 6:
            draw.rectangle((0, 0, RW, RH), fill=(50, 50, 50))
            draw.text((20, 20), "LOAD_MEM: EP7 - C&A_PODS", font=sys_font, fill=(0, 255, 255))
            draw.ellipse((RW//2-40, RH//2-80, RW//2+40, RH//2+80), outline=(0, 255, 255), width=4) # Pod
        else:
            draw.rectangle((0, 0, RW, RH), fill=(150, 0, 0))
            draw.text((20, 20), "LOAD_MEM: EP8 - TRUTH_EXPOSED", font=sys_font, fill=(255, 255, 255))
            
        glitch_intensity = 0.5
        if int(t * 10) % 3 == 0: invert_colors = True

    elif t < T_CONFRONT:
        # Phase 3 & 4: Confrontation (Typing) -> ERROR
        if t < 26.5:
            # 3. Typing
            draw.rectangle((0, 0, RW, RH), fill=(40, 0, 0))
            glitch_intensity = 0.2
            
            box_y = 40
            draw.rectangle((10, box_y, RW-10, RH-40), fill=(5, 5, 10), outline=(255, 50, 50), width=2)
            
            progress = (t - T_MEMORIES) / (26.0 - T_MEMORIES)
            total_chars = int(progress * 300) 
            
            chars_drawn = 0
            current_y = box_y + 10
            for line in prompt_lines:
                if chars_drawn >= total_chars: break
                chars_to_draw = min(len(line), total_chars - chars_drawn)
                displayed_text = line[:chars_to_draw]
                
                is_last_line = ("don't... listen!" in line)
                col = (255, 200, 50) if "> POMNI" in line or "> ZOOBLE" in line or "> JAX" in line else (200, 200, 200)
                
                # ÉNORME IMPACT DE POMNI
                if is_last_line:
                    col = (255, 0, 0)
                    if chars_to_draw > 0: 
                        glitch_intensity = 3.0
                        rgb_split_active = True
                
                if chars_to_draw == len(line) and chars_drawn + chars_to_draw == total_chars and int(t*10)%2==0:
                    displayed_text += "_"
                    
                if is_last_line and chars_to_draw > 0:
                    # Rendu tremblant, gras et menaçant
                    shake_x, shake_y = random.randint(-4, 4), random.randint(-4, 4)
                    draw.text((20+2+shake_x, current_y+shake_y), displayed_text, font=sys_font, fill=col)
                    draw.text((20-2+shake_x, current_y+shake_y), displayed_text, font=sys_font, fill=col)
                    draw.text((20+shake_x, current_y+2+shake_y), displayed_text, font=sys_font, fill=col)
                    draw.text((20+shake_x, current_y-2+shake_y), displayed_text, font=sys_font, fill=col)
                    draw.text((20+shake_x, current_y+shake_y), displayed_text, font=sys_font, fill=(255, 255, 255)) # Coeur blanc
                else:
                    draw.text((20, current_y), displayed_text, font=sys_font, fill=col)
                    
                chars_drawn += len(line)
                current_y += 25

        else:
            # 4. SYSTEM ERROR (Bass Drop)
            glitch_intensity = 0.5
            rgb_split_active = True
            draw.rectangle((0, 0, RW, RH), fill=(80, 0, 0)) # Rouge écarlate
            
            err_img = Image.new('RGBA', (180, 40), (0,0,0,0))
            err_draw = ImageDraw.Draw(err_img)
            err_draw.text((5, 0), "SYSTEM_ERROR:", font=sys_font, fill=(0, 0, 0))
            err_draw.text((5, 15), "EGO FRACTURED.", font=sys_font, fill=(255, 255, 0))
            
            # Grossissement extrême
            scale_factor = 5
            big_err = err_img.resize((180*scale_factor, 40*scale_factor), Image.NEAREST)
            
            bx = RW//2 - big_err.width//2 + random.randint(-10, 10)
            by = RH//2 - big_err.height//2 + random.randint(-10, 10)
            img.paste(big_err, (bx, by), big_err)

    elif t < T_SNAP:
        # Phase 5: CHAOS ABSOLU
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

    # --- COUCHE 2 : LE RÉSEAU DE NEURONES (Uniquement pendant le pétage de plombs) ---
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
                        draw.line((x1, y1, x2, y2), fill=(255, 0, 0), width=2)
            
            col_text = (255, 255, 0) if random.random() > 0.5 else (255, 0, 0)
            display_word = "".join(random.choice(['█', 'X', 'ERR']) for _ in w1) if random.random() > 0.8 else w1
            draw.text((x1, y1), display_word, font=sys_font, fill=col_text)

    # --- APPLICATION DES GLITCHS GLOBAUX ---
    if glitch_intensity > 0:
        img = apply_glitch(img, glitch_intensity, rgb_split_active, invert_colors)

    img = img.resize((W, H), Image.NEAREST)
    return np.array(img)

if __name__ == "__main__":
    print("Initialisation de l'expérience (Épisode 9 : Ultimate Cut)...")
    video_clip = VideoClip(make_frame, duration=DURATION).with_audio(generate_audio())
    video_clip.write_videofile("caine_episode9_finale.mp4", fps=FPS, codec="libx264", audio_codec="aac", preset="ultrafast")
    print("Terminé ! Vidéo sauvegardée sous caine_episode9_finale.mp4.")