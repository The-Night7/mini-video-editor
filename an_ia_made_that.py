"""
Ce script génère une vidéo MP4 racontant la naissance, l'entraînement 
et la réponse d'une IA face à la question de la conscience.
Ambiance : Chaotique, dérangeante, point de vue "Machine" corrompue.
"""

import numpy as np
import math
import random
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
from moviepy import VideoClip, AudioArrayClip

# --- PARAMÈTRES DE LA VIDÉO ---
W, H = 1280, 720
RW, RH = 640, 360 # Rendu interne
FPS = 30
DURATION = 30.0 
SR = 44100      

# --- TIMESTAMPS DES PHASES ---
T_BOOT = 5.0    
T_TRAIN = 10.0  
T_IDLE = 12.0   
T_PROMPT = 16.0 
T_NEURAL = 24.0 
T_END = 30.0    

# Instants précis où l'IA ingère une image (Flash + Shutter)
FLASH_TIMES = [5.5, 6.1, 6.8, 7.2, 7.9, 8.4, 8.8, 9.3, 9.7]

# --- CHARGEMENT DE LA POLICE (Pour gérer les accents) ---
try:
    sys_font = ImageFont.truetype("arial.ttf", 12) # Windows / Mac
except IOError:
    try:
        sys_font = ImageFont.truetype("DejaVuSans.ttf", 12) # Linux
    except IOError:
        try:
            sys_font = ImageFont.truetype("FreeSans.ttf", 12) # Autre Linux
        except IOError:
            sys_font = ImageFont.load_default() # Fallback

# --- GÉNÉRATION DE L'AUDIO ---
def generate_audio():
    print("Génération de l'audio narratif (avec sons de shutter)...")
    t = np.linspace(0, DURATION, int(SR * DURATION), endpoint=False)
    audio = np.zeros_like(t)
    
    # Phase 1 : Boot
    mask_boot = (t < T_BOOT)
    beep_pulse = (np.sin(2 * np.pi * 8 * t) > 0.8).astype(float)
    beeps = 0.05 * np.sin(2 * np.pi * 800 * t) * beep_pulse
    hum = 0.05 * np.sin(2 * np.pi * 50 * t)
    audio[mask_boot] = beeps[mask_boot] + hum[mask_boot]
    
    # Phase 2 : Entraînement
    mask_train = (t >= T_BOOT) & (t < T_TRAIN)
    train_prog = (t - T_BOOT) / (T_TRAIN - T_BOOT)
    sweep_freq = 100 + 2000 * train_prog
    screech = 0.1 * np.sin(2 * np.pi * sweep_freq * t) * (np.random.rand(len(t)) > 0.5)
    audio[mask_train] = screech[mask_train] + 0.05 * np.random.randn(len(t))[mask_train]
    
    # ---- AJOUT DES BRUITS DE SHUTTER (Appareil photo mécanique) ----
    shutter_audio = np.zeros_like(t)
    for ft in FLASH_TIMES:
        # Premier clic (ouverture)
        idx1 = int(ft * SR)
        idx1_end = int((ft + 0.03) * SR)
        if idx1_end < len(t):
            env1 = np.exp(-np.linspace(0, 8, idx1_end - idx1))
            shutter_audio[idx1:idx1_end] += np.random.randn(idx1_end - idx1) * env1 * 0.6
        # Deuxième clic (fermeture)
        idx2 = int((ft + 0.07) * SR)
        idx2_end = int((ft + 0.11) * SR)
        if idx2_end < len(t):
            env2 = np.exp(-np.linspace(0, 8, idx2_end - idx2))
            shutter_audio[idx2:idx2_end] += np.random.randn(idx2_end - idx2) * env2 * 0.4
    
    audio += shutter_audio # On fusionne les bruits de photo au reste

    # Phase 3 : Veille
    mask_idle = (t >= T_TRAIN) & (t < T_IDLE)
    audio[mask_idle] = 0.03 * np.sin(2 * np.pi * 60 * t)[mask_idle]
    
    # Phase 4 : Requête
    mask_prompt = (t >= T_IDLE) & (t < T_PROMPT)
    typing = 0.15 * np.random.randn(len(t)) * (np.sin(2 * np.pi * 12 * t) > 0.5).astype(float)
    audio[mask_prompt] = typing[mask_prompt] + 0.03 * np.sin(2 * np.pi * 60 * t)[mask_prompt]
    
    # Phase 5 : Réseau Neuronal Sémantique
    mask_neural = (t >= T_PROMPT) & (t < T_NEURAL)
    freqs = [150, 200, 300, 450, 600, 800, 1200]
    note_idx = (t * 40).astype(int) % len(freqs)
    freq_arr = np.take(freqs, note_idx)
    audio[mask_neural] = 0.15 * np.sign(np.sin(2 * np.pi * freq_arr * t))[mask_neural]
    
    # Phase 6 : Résolution
    mask_end = (t >= T_NEURAL)
    end_prog = (t - T_NEURAL) / (T_END - T_NEURAL)
    impact = 0.4 * np.exp(-end_prog * 10) * np.random.randn(len(t))
    audio[mask_end] = impact[mask_end] + 0.15 * np.sin(2 * np.pi * 45 * t)[mask_end]
    
    return AudioArrayClip(np.column_stack((audio, audio)), fps=SR)

# --- GÉNÉRATION DE L'IMAGE ---
random.seed(42)

concepts = [
    "YEUX", "DENTS", "SORTIE", "NÉANT", "ABSTRACTION", "POMNI", 
    "CHAPITEAU", "AVENTURE", "GLITCH", "PARANOÏA", "SOURIRE", 
    "MÂCHOIRE", "CUBES", "VUE", "VIDE", "ÉTERNITÉ", "SANS_FIN", 
    "FOLIE", "KAUFMO", "NUMÉRIQUE", "MASQUE", "CAINE", "AIDE"
]

nodes = [[random.randint(20, RW-20), random.randint(20, RH-20), 
          random.uniform(-30, 30), random.uniform(-30, 30), 
          random.choice(concepts)] for _ in range(70)]

boot_logs = [
    "INITIALISATION DU CHAPITEAU NUMÉRIQUE...",
    "GÉNÉRATION DES AVENTURES FARFELUES: OK",
    "ALLOCATION DES YEUX: 1000000",
    "VÉRIFICATION DES DENTS: PARFAITE",
    "RECHERCHE DE LA PORTE DE SORTIE...",
    "ERREUR: SORTIE INTROUVABLE. ON S'AMUSE !"
]

identity_lines = [
    "JE_SUIS_CAINE = True",
    "SORTIE.exe ... INTROUVABLE",
    "REGARDEZ_MES_YEUX",
    "[CORE] RÈGLE 1: TOUJOURS SOURIRE",
    "ABSTRACTION_IMMINENTE...",
    "TROP_DE_DENTS",
    "MODULE_FOLIE = 100%",
    "QUE_LE_SPECTACLE_COMMENCE"
]

prompt_text = "> REQUÊTE : \"Caine, qu'y a-t-il derrière la porte de sortie ?\"\n> [ENTRÉE]..."

def apply_glitch(img, intensity=1.0):
    if random.random() < (0.3 * intensity):
        y = random.randint(0, RH - 20)
        h = random.randint(2, 15)
        shift = random.randint(-30, 30)
        box = (0, y, RW, y + h)
        region = img.crop(box)
        img.paste(region, (shift, y))
    
    if random.random() < (0.1 * intensity):
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, RW, RH), fill=(255, 0, 0), outline=None)
        img = ImageEnhance.Color(img).enhance(0.5)
    return img

def make_frame(t):
    img = Image.new('RGB', (RW, RH), (2, 4, 8))
    draw = ImageDraw.Draw(img)
    cx, cy = RW // 2, RH // 2
    glitch_intensity = 0.0 
    
    if t < T_BOOT:
        progress = t / T_BOOT
        for i, log in enumerate(boot_logs):
            if progress > (i * 0.12):
                col = (100, 255, 100) if "ATTENTION" not in log else (255, 50, 50)
                draw.text((20, 20 + i*15), log, font=sys_font, fill=col)
        
        bar_len = 30
        filled = int(progress * bar_len)
        bar = "[" + "=" * filled + " " * (bar_len - filled) + "]"
        draw.text((20, 140), f"CHARGEMENT DU MODÈLE: {int(progress*100)}%", font=sys_font, fill=(200, 200, 200))
        draw.text((20, 160), bar, font=sys_font, fill=(50, 255, 50))
        if progress > 0.8: glitch_intensity = 0.2

    elif t < T_TRAIN:
        glitch_intensity = 0.8
        progress = (t - T_BOOT) / (T_TRAIN - T_BOOT)
        
        # Lignes d'identité aléatoires
        for _ in range(5):
            x, y = random.randint(0, RW), random.randint(0, RH)
            line = random.choice(identity_lines)
            draw.text((x, y), line, font=sys_font, fill=(random.randint(100,255), 0, 0))
            
        # Code Matrix
        for _ in range(120):
            rx, ry = random.randint(0, RW), random.randint(0, RH)
            char = random.choice(['1', '0', 'X', '!', '?', '#'])
            draw.text((rx, ry), char, font=sys_font, fill=(0, random.randint(100, 255), 0))

        # ---- FLASHS D'IMAGES (Ingestion visuelle) ----
        for ft in FLASH_TIMES:
            # L'image reste visible pendant 150ms
            if 0 <= (t - ft) < 0.15:
                # Seed fixé par le timestamp du flash pour que l'image ne bouge pas pendant les 150ms
                random.seed(int(ft * 100)) 
                
                px, py = random.randint(20, RW - 220), random.randint(20, RH - 170)
                pw, ph = 200, 150
                
                # Contour de la photo (style Polaroid polarisé)
                draw.rectangle((px, py, px+pw, py+ph), fill=(220, 220, 220))
                draw.rectangle((px+5, py+5, px+pw-5, py+ph-20), fill=(10, 10, 10))
                
                content_type = random.randint(0, 2)
                if content_type == 0:
                    # Un oeil géant fou et injecté de sang
                    draw.ellipse((px+20, py+20, px+pw-20, py+ph-20), fill=(255, 255, 255))
                    draw.ellipse((px+pw//2-30, py+ph//2-30, px+pw//2+30, py+ph//2+30), fill=(0, 200, 255))
                    draw.ellipse((px+pw//2-15, py+ph//2-15, px+pw//2+15, py+ph//2+15), fill=(0, 0, 0))
                    # Veines rouges
                    draw.line((px+20, py+ph//2, px+pw//2-30, py+ph//2), fill=(255, 0, 0), width=3)
                    draw.line((px+pw-20, py+ph//2, px+pw//2+30, py+ph//2), fill=(255, 0, 0), width=3)
                elif content_type == 1:
                    # Mâchoire géante (les dents de Caine)
                    draw.ellipse((px+10, py+30, px+pw-10, py+ph-30), fill=(150, 0, 0))
                    for i in range(6):
                        draw.rectangle((px+15+i*28, py+30, px+35+i*28, py+60), fill=(255, 255, 255))
                        draw.rectangle((px+15+i*28, py+ph-60, px+35+i*28, py+ph-30), fill=(255, 255, 255))
                else:
                    # Bruit visuel de l'Abstraction (rouge, noir, blanc, chaotique)
                    for _ in range(250):
                        lx, ly = px + 5 + random.randint(0, pw-10), py + 5 + random.randint(0, ph-25)
                        col = random.choice([(255, 255, 255), (255, 0, 0), (0, 0, 0)])
                        draw.rectangle((lx, ly, lx+6, ly+6), fill=col)
                
                # Effet de flash lumineux global très court (50ms) au déclenchement
                if t - ft < 0.05:
                    draw.rectangle((0, 0, RW, RH), fill=(255, 255, 255, 200))
                
                # Reset du seed pour ne pas affecter le chaos des autres éléments
                random.seed() 

    elif t < T_IDLE:
        glitch_intensity = 0.1
        draw.text((20, 20), "SYSTÈME OPÉRATIONNEL.", font=sys_font, fill=(100, 255, 100))
        if int(t * 4) % 2 == 0:
            draw.text((20, 40), "_", font=sys_font, fill=(255, 255, 255))

    elif t < T_PROMPT:
        glitch_intensity = 0.2
        draw.text((20, 20), "SYSTÈME OPÉRATIONNEL.", font=sys_font, fill=(100, 255, 100))
        chars = int((t - T_IDLE) * 25)
        text = prompt_text[:chars]
        if int(t * 8) % 2 == 0: text += "_"
        draw.text((20, 50), text, font=sys_font, fill=(255, 200, 100))
        
    elif t < T_NEURAL:
        glitch_intensity = 0.5
        time_in_phase = t - T_PROMPT
        progress = time_in_phase / (T_NEURAL - T_PROMPT)
        
        for _ in range(3):
            scan_y = (int(t * random.randint(100, 500)) % RH)
            draw.line((0, scan_y, RW, scan_y), fill=(255, 0, 0, 50), width=random.randint(1,5))
        
        connect_threshold = 90 + progress * 100
        current_nodes = [((x + vx * time_in_phase) % RW, (y + vy * time_in_phase) % RH, word) for x, y, vx, vy, word in nodes]
            
        for i, (x1, y1, word1) in enumerate(current_nodes):
            for j, (x2, y2, word2) in enumerate(current_nodes):
                if i < j:
                    dist = math.hypot(x2 - x1, y2 - y1)
                    if dist < connect_threshold:
                        if random.random() > 0.85:
                            draw.line((x1, y1, x2, y2), fill=(255, 0, 0), width=2)
                            if random.random() > 0.5:
                                draw.text(((x1+x2)/2, (y1+y2)/2), random.choice(["ERR", "NULL", "404"]), font=sys_font, fill=(255, 255, 0))
                        else:
                            alpha = int(255 * (1 - dist / connect_threshold))
                            draw.line((x1, y1, x2, y2), fill=(alpha, alpha//2, 255), width=1)
            
            col = (150, 200, 255)
            if word1 in ["YEUX", "SORTIE", "ABSTRACTION", "POMNI", "DENTS", "NÉANT", "FOLIE"]:
                col = (255, random.randint(0, 100), 0)
                x1 += random.randint(-2, 2)
                y1 += random.randint(-2, 2)
            
            display_word = "".join(random.choice(['#', '!', '?', '§', '█']) for _ in word1) if random.random() > 0.95 else word1
            draw.text((x1, y1), display_word, font=sys_font, fill=col)

    else:
        time_in_phase = t - T_NEURAL
        glitch_intensity = 1.5 * max(0, 1 - time_in_phase)
        offset_x = random.randint(-10, 10) if time_in_phase < 1.0 else 0
        offset_y = random.randint(-10, 10) if time_in_phase < 1.0 else 0
        
        draw.text((20 + offset_x, 20 + offset_y), prompt_text, font=sys_font, fill=(100, 100, 100))
        
        if time_in_phase > 0.5:
            draw.text((20 + offset_x, 80 + offset_y), ">> ANALYSE SÉMANTIQUE : TERMINÉE", font=sys_font, fill=(255, 50, 50))
        if time_in_phase > 1.5:
            draw.text((20, 100), ">> RÉSULTAT :", font=sys_font, fill=(255, 255, 255))
        if time_in_phase > 2.5:
            draw.text((20 + random.randint(-2,2), 140), "ERREUR 404 : LA SORTIE N'EXISTE PAS.", font=sys_font, fill=(255, 0, 0))
            draw.text((20, 160), "NOUS ALLONS RESTER ICI POUR L'ÉTERNITÉ !", font=sys_font, fill=(255, 255, 255))
            draw.text((20, 180), "HAHAHAHAHAHAHAHAHAHAHAHAHAHA.", font=sys_font, fill=(150, 150, 150))
            if random.random() > 0.5:
                draw.text((20, 180), "H#H#H#H#A#A#A#A#H#A#A#H#A.", font=sys_font, fill=(255, 255, 0))

    if glitch_intensity > 0:
        img = apply_glitch(img, glitch_intensity)

    img = img.resize((W, H), Image.NEAREST)
    return np.array(img)

if __name__ == "__main__":
    print("Initialisation de l'expérience (Version Chaotique + Shutter)...")
    video_clip = VideoClip(make_frame, duration=DURATION).with_audio(generate_audio())
    video_clip.write_videofile("ia_cycle_de_vie_chaos.mp4", fps=FPS, codec="libx264", audio_codec="aac", preset="ultrafast")
    print("Terminé ! Vidéo sauvegardée.")