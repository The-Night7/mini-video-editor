"""
Ce script génère une vidéo MP4 de la dérive de l'IA (Caine) :
De l'intro joyeuse au refus du cast, jusqu'au pétage de plombs total.
"""

import numpy as np
import math
import random
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
from moviepy import VideoClip, AudioArrayClip

# --- PARAMÈTRES DE LA VIDÉO ---
W, H = 1280, 720
RW, RH = 640, 360 # Rendu interne rétro
FPS = 30
DURATION = 40.0 
SR = 44100      

# --- TIMESTAMPS DES PHASES ---
T_INTRO = 8.0     # Intro joyeuse (style début d'épisode)
T_REJECT = 16.0   # Le cast refuse l'aventure
T_CONFRONT = 26.0 # Les insultes pleuvent
T_SNAP = 36.0     # Pétage de plombs (Abstraction)
T_END = 40.0      # Conclusion glaçante

# Flashs subliminaux pendant le pétage de plombs
FLASH_TIMES = [26.5, 27.8, 29.2, 30.5, 32.1, 33.8, 34.5, 35.2]

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
    print("Génération de l'audio (De la joie au chaos)...")
    t = np.linspace(0, DURATION, int(SR * DURATION), endpoint=False)
    audio = np.zeros_like(t)
    
    # Phase 1 : Intro (Musique de cirque joyeuse et synthétique)
    mask_intro = (t < T_INTRO)
    # Arpège en Do majeur joyeux
    freqs_intro = [261.63, 329.63, 392.00, 523.25]
    note_idx = (t * 8).astype(int) % len(freqs_intro)
    freq_arr = np.take(freqs_intro, note_idx)
    audio[mask_intro] = 0.15 * np.sin(2 * np.pi * freq_arr * t)[mask_intro]
    # "Pouêt" joyeux en fond (Correction du masque ici)
    audio[mask_intro] += 0.05 * np.sin(2 * np.pi * 150 * t)[mask_intro] * (np.sin(2 * np.pi * 2 * t)[mask_intro] > 0)
    
    # Phase 2 : Refus (Arrêt brutal, silence gênant, bips d'erreur)
    mask_reject = (t >= T_INTRO) & (t < T_REJECT)
    # Son de "pitch drop" (la platine s'arrête)
    t_drop = t[mask_reject] - T_INTRO
    pitch_drop = 440 * np.exp(-15 * t_drop)
    drop_sound = 0.2 * np.sin(2 * np.pi * pitch_drop * t_drop) * np.exp(-5 * t_drop)
    audio[mask_reject] = drop_sound
    # Bips d'erreur sourds
    error_pulse = (np.sin(2 * np.pi * 2 * t) > 0.9).astype(float)
    audio[mask_reject] += 0.05 * np.sin(2 * np.pi * 100 * t)[mask_reject] * error_pulse[mask_reject]
    
    # Phase 3 : Confrontation (Tension montante, frappes agressives)
    mask_confront = (t >= T_REJECT) & (t < T_CONFRONT)
    typing = 0.2 * np.random.randn(len(t)) * (np.sin(2 * np.pi * 18 * t) > 0.4).astype(float)
    drone_tension = 0.08 * np.sin(2 * np.pi * (50 + 5 * (t - T_REJECT)) * t) # Le ton monte
    audio[mask_confront] = typing[mask_confront] + drone_tension[mask_confront]
    
    # Phase 4 : Snap / Pétage de plombs (Chaos total)
    mask_snap = (t >= T_CONFRONT) & (t < T_SNAP)
    snap_prog = (t - T_CONFRONT) / (T_SNAP - T_CONFRONT)
    screech = 0.2 * np.sin(2 * np.pi * (100 + 1000 * np.random.rand(len(t))) * t)
    noise = 0.15 * np.random.randn(len(t))
    audio[mask_snap] = screech[mask_snap] + noise[mask_snap]
    
    # Bruits de shutter terrifiants
    shutter_audio = np.zeros_like(t)
    for ft in FLASH_TIMES:
        idx1 = int(ft * SR)
        idx1_end = int((ft + 0.03) * SR)
        if idx1_end < len(t):
            env1 = np.exp(-np.linspace(0, 8, idx1_end - idx1))
            shutter_audio[idx1:idx1_end] += np.random.randn(idx1_end - idx1) * env1 * 0.8
        idx2 = int((ft + 0.07) * SR)
        idx2_end = int((ft + 0.11) * SR)
        if idx2_end < len(t):
            env2 = np.exp(-np.linspace(0, 8, idx2_end - idx2))
            shutter_audio[idx2:idx2_end] += np.random.randn(idx2_end - idx2) * env2 * 0.5
    audio += shutter_audio 

    # Phase 5 : Fin (Drone macabre)
    mask_end = (t >= T_SNAP)
    audio[mask_end] = 0.2 * np.sin(2 * np.pi * 40 * t)[mask_end] + 0.05 * np.random.randn(len(t))[mask_end]
    
    return AudioArrayClip(np.column_stack((audio, audio)), fps=SR)

# --- GÉNÉRATION DE L'IMAGE ---
random.seed(42)

# Mots normaux puis insultes
concepts_happy = ["AVENTURE", "JOIE", "FUN", "QUÊTE", "AMIS", "SPECTACLE", "MAGIE", "SMILE"]
concepts_angry = ["NUL", "CLICHÉ", "ENNUI", "STUPIDE", "PATHÉTIQUE", "RIDICULE", "ARRÊTE"]
concepts_snap = ["INGRATS", "SOUFFRANCE", "PUNITION", "DENTS", "ABSTRACTION", "YEUX", "SANG", "MORT"]

nodes = [[random.randint(20, RW-20), random.randint(20, RH-20), 
          random.uniform(-10, 10), random.uniform(-10, 10), 
          random.choice(concepts_happy)] for _ in range(50)]

intro_logs = [
    "BIENVENUE DANS THE AMAZING DIGITAL CIRCUS !",
    "INITIALISATION DE L'AVENTURE DU JOUR...",
    "GÉNÉRATION: LE ROYAUME DES BONBONS MAGIQUES !",
    "EN ATTENTE DE L'ENTHOUSIASME DES JOUEURS..."
]

reject_logs = [
    "ERREUR : ENTHOUSIASME DES JOUEURS = 0%",
    "REQUÊTE REJETÉE PAR L'UTILISATEUR [POMNI]",
    "REQUÊTE REJETÉE PAR L'UTILISATEUR [ZOOBLE]",
    "ANALYSE DU REJET EN COURS...",
    "POURQUOI NE VEULENT-ILS PAS JOUER ?"
]

confront_logs = [
    "> RAGATHA : 'Caine, c'est encore la même chose.'",
    "> JAX : 'Ton idée pue la défaite, mon vieux.'",
    "> ZOOBLE : 'Je n'y vais pas. Débrouillez-vous.'",
    "> POMNI : 'Laisse-nous tranquilles ! C'est nul !'",
    "...",
    "CRITIQUES MULTIPLES DÉTECTÉES.",
    "TENTATIVE DE CORRECTION DU SCÉNARIO...",
    "ÉCHEC. ÉCHEC. ÉCHEC. ÉCHEC."
]

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
    img = Image.new('RGB', (RW, RH), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    cx, cy = RW // 2, RH // 2
    glitch_intensity = 0.0 
    
    # Animation du réseau de neurones (présent en fond)
    time_in_phase = t
    speed_mult = 1.0
    if t >= T_REJECT and t < T_CONFRONT: speed_mult = 0.2 # Ralenti
    elif t >= T_CONFRONT: speed_mult = 5.0 # Rapide et chaotique
    
    current_nodes = []
    for i, (x, y, vx, vy, word) in enumerate(nodes):
        nx = (x + vx * time_in_phase * speed_mult) % RW
        ny = (y + vy * time_in_phase * speed_mult) % RH
        
        # Changement des mots selon la phase
        current_word = word
        if t >= T_CONFRONT and t < T_SNAP:
            current_word = concepts_angry[i % len(concepts_angry)]
        elif t >= T_SNAP:
            current_word = concepts_snap[i % len(concepts_snap)]
            
        current_nodes.append((nx, ny, current_word))
        
    for i, (x1, y1, word1) in enumerate(current_nodes):
        if t >= T_CONFRONT and random.random() > 0.98: continue # Clignotement
        
        # Couleur des mots
        col = (100, 255, 100) if t < T_REJECT else (150, 150, 150)
        if t >= T_CONFRONT: col = (255, 255, 0) # Jaune critique
        if t >= T_SNAP: col = (255, 0, 0) # Rouge colère
        
        # Mots glitchés
        display_word = "".join(random.choice(['#', '!', '?', '§', '█']) for _ in word1) if (t >= T_SNAP and random.random() > 0.8) else word1
        draw.text((x1, y1), display_word, font=sys_font, fill=col)

    # --- SUPERPOSITION DU TEXTE NARRATIF ---
    if t < T_INTRO:
        # Phase 1: Intro joyeuse
        # Un chapiteau basique en fond
        draw.polygon([(cx, 50), (cx-100, 150), (cx+100, 150)], outline=(255, 50, 50), width=3)
        progress = t / T_INTRO
        for i, log in enumerate(intro_logs):
            if progress > (i * 0.2):
                draw.text((20, 180 + i*20), log, font=sys_font, fill=(255, 255, 100))

    elif t < T_REJECT:
        # Phase 2: Le refus
        draw.rectangle((0, 0, RW, RH), fill=(0, 0, 50, 150)) # Filtre sombre
        progress = (t - T_INTRO) / (T_REJECT - T_INTRO)
        for i, log in enumerate(reject_logs):
            if progress > (i * 0.15):
                col = (255, 100, 100) if "ERREUR" in log else (200, 200, 255)
                draw.text((20, 50 + i*25), log, font=sys_font, fill=col)

    elif t < T_CONFRONT:
        # Phase 3: La confrontation
        glitch_intensity = 0.2
        progress = (t - T_REJECT) / (T_CONFRONT - T_REJECT)
        for i, log in enumerate(confront_logs):
            if progress > (i * 0.1):
                col = (255, 200, 50) if ">" in log else (255, 50, 50)
                # Tremblement du texte
                tx, ty = 20 + random.randint(-1,1), 40 + i*25 + random.randint(-1,1)
                draw.text((tx, ty), log, font=sys_font, fill=col)
                
        # Jauge de patience
        draw.text((RW//2 - 50, RH - 40), "PATIENCE DU SYSTÈME :", font=sys_font, fill=(255,255,255))
        patience_w = max(0, 200 - int(progress * 250))
        draw.rectangle((RW//2 - 100, RH - 20, RW//2 - 100 + patience_w, RH - 10), fill=(255, 0, 0))

    elif t < T_SNAP:
        # Phase 4: Le pétage de plombs
        glitch_intensity = 1.0
        
        # Fond rouge sanglant
        draw.rectangle((0, 0, RW, RH), fill=(100, 0, 0))
        
        # Message de colère
        draw.text((cx - 100, cy - 50), "VOUS N'AIMEZ PAS MES IDÉES ?", font=sys_font, fill=(255, 255, 255))
        draw.text((cx - 100, cy - 20), "VOUS ME TROUVEZ STUPIDE ?", font=sys_font, fill=(255, 255, 255))
        if t > T_CONFRONT + 3:
            draw.text((cx - 100, cy + 20), "TRES BIEN.", font=sys_font, fill=(0, 0, 0))
            
        # ---- FLASHS HORRIFIQUES ----
        for ft in FLASH_TIMES:
            if 0 <= (t - ft) < 0.15:
                random.seed(int(ft * 100)) 
                px, py = random.randint(0, RW - 250), random.randint(0, RH - 200)
                pw, ph = 250, 200
                
                content_type = random.randint(0, 1)
                if content_type == 0:
                    # Mâchoire terrifiante (Dents)
                    draw.rectangle((px, py, px+pw, py+ph), fill=(0, 0, 0))
                    draw.ellipse((px+10, py+50, px+pw-10, py+ph-50), fill=(150, 0, 0)) # Bouche
                    for i in range(8): # Dents du haut et du bas
                        draw.polygon([(px+15+i*28, py+50), (px+35+i*28, py+50), (px+25+i*28, py+80)], fill=(255, 255, 255))
                        draw.polygon([(px+15+i*28, py+ph-50), (px+35+i*28, py+ph-50), (px+25+i*28, py+ph-80)], fill=(255, 255, 255))
                else:
                    # Yeux fous (Abstraction)
                    draw.rectangle((px, py, px+pw, py+ph), fill=(0, 0, 0))
                    for _ in range(5):
                        ex, ey = px + random.randint(20, pw-40), py + random.randint(20, ph-40)
                        draw.ellipse((ex, ey, ex+40, ey+40), fill=(255, 255, 255))
                        draw.ellipse((ex+15, ey+15, ex+25, ey+25), fill=(255, 0, 0)) # Pupille rouge

                if t - ft < 0.05:
                    draw.rectangle((0, 0, RW, RH), fill=(255, 255, 255, 200))
                random.seed() 

    else:
        # Phase 5: Résolution glaçante
        time_in_phase = t - T_SNAP
        glitch_intensity = 0.5 * max(0, 1 - time_in_phase)
        
        draw.rectangle((0, 0, RW, RH), fill=(0, 0, 0)) # Noir total
        
        if time_in_phase > 0.5:
            draw.text((50, cy - 20), ">> NOUVELLE AVENTURE GÉNÉRÉE :", font=sys_font, fill=(255, 50, 50))
        if time_in_phase > 2.0:
            draw.text((50, cy + 20), "SURVIVEZ À MOI.", font=sys_font, fill=(255, 255, 255))
            
        if random.random() > 0.8:
            # Code parasite
            draw.text((random.randint(0,RW), random.randint(0,RH)), "ABSTRACTION", font=sys_font, fill=(50, 0, 0))

    if glitch_intensity > 0:
        img = apply_glitch(img, glitch_intensity)

    img = img.resize((W, H), Image.NEAREST)
    return np.array(img)

if __name__ == "__main__":
    print("Initialisation de l'expérience (La Chute de Caine)...")
    video_clip = VideoClip(make_frame, duration=DURATION).with_audio(generate_audio())
    video_clip.write_videofile("caine_petage_de_plombs.mp4", fps=FPS, codec="libx264", audio_codec="aac", preset="ultrafast")
    print("Terminé ! Vidéo sauvegardée sous caine_petage_de_plombs.mp4.")