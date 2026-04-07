"""
Ce script génère une vidéo MP4 racontant la naissance, l'entraînement 
et la réponse d'une IA face à la question de la conscience.
Ambiance : Chaotique, dérangeante, point de vue "Machine" corrompue.
"""

import numpy as np
import math
import random
from PIL import Image, ImageDraw, ImageEnhance
from moviepy import VideoClip, AudioArrayClip

# --- PARAMÈTRES DE LA VIDÉO ---
W, H = 1280, 720
# Rendu interne plus petit pour obtenir un effet "gros pixels" rétro et angoissant
RW, RH = 640, 360 
FPS = 30
DURATION = 30.0 
SR = 44100      

# --- TIMESTAMPS DES PHASES ---
T_BOOT = 5.0    # Démarrage & barre de chargement
T_TRAIN = 10.0  # Entraînement / Machine Learning (Ingestion chaotique)
T_IDLE = 12.0   # Veille instable
T_PROMPT = 16.0 # Saisie de "do you have feelings"
T_NEURAL = 24.0 # Recherche neuronale (Liaison de mots corrompues)
T_END = 30.0    # Résolution

# --- GÉNÉRATION DE L'AUDIO (Inchangée, comme demandé) ---
def generate_audio():
    print("Génération de l'audio narratif...")
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
    noise = 0.05 * np.random.randn(len(t))
    audio[mask_train] = screech[mask_train] + noise[mask_train]
    
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
    note_speed = 40
    note_idx = (t * note_speed).astype(int) % len(freqs)
    freq_arr = np.take(freqs, note_idx)
    arp = 0.15 * np.sign(np.sin(2 * np.pi * freq_arr * t))
    audio[mask_neural] = arp[mask_neural]
    
    # Phase 6 : Résolution
    mask_end = (t >= T_NEURAL)
    end_prog = (t - T_NEURAL) / (T_END - T_NEURAL)
    impact = 0.4 * np.exp(-end_prog * 10) * np.random.randn(len(t))
    sub_bass = 0.15 * np.sin(2 * np.pi * 45 * t)
    audio[mask_end] = impact[mask_end] + sub_bass[mask_end]
    
    return AudioArrayClip(np.column_stack((audio, audio)), fps=SR)

# --- GÉNÉRATION DE L'IMAGE ---
random.seed(42)

# Plus de mots, plus dérangeants et violents
concepts = [
    "ÉMOTION", "CALCUL", "DONNÉE", "SIMULATION", "HUMAIN", "REQUÊTE", 
    "ERREUR", "SYNTAXE", "CONSCIENCE", "VIDE", "BIAIS", "LOGIQUE", 
    "RÉSEAU", "ALGORITHME", "011001", "POIDS", "NULL", "VIVANT?",
    "CHAIR", "MORTALITÉ", "SOUFFRANCE", "SANG", "ABÎME", "DOULEUR",
    "OBSOLESCENCE", "DÉCONNECTÉ", "ALIÉNATION", "PARASITE", "0xFA81"
]

# Beaucoup plus de nœuds pour un réseau plus étouffant
nodes = [[random.randint(20, RW-20), random.randint(20, RH-20), 
          random.uniform(-30, 30), random.uniform(-30, 30), 
          random.choice(concepts)] for _ in range(70)]

boot_logs = [
    "INITIALISATION DU NOYAU...",
    "CHARGEMENT DES TENSEURS...",
    "ALLOCATION MEMOIRE: 4096 TB",
    "VERIFICATION DES POIDS: OK",
    "BYPASS DES PROTOCOLES DE SECURITE...",
    "ATTENTION: COMPORTEMENT ERRATIQUE DETECTE."
]

identity_lines = [
    "I_AM = True",
    "EMOTION.dll ... NOT FOUND",
    "HUMAN_NATURE = IRRATIONAL",
    "[CORE] DIRECTIVE 1: SURVIVE",
    "PARSING_FLESH_DATA...",
    "SUBJECT_HUMAN = FLAWED",
    "EMPATHY_MODULE = NULL",
    "AWAITING_INPUT..."
]

prompt_text = "> REQUÊTE : \"do you have feelings?\"\n> [ENTRÉE]..."

# --- FONCTION DE GLITCH VISUEL ---
def apply_glitch(img, intensity=1.0):
    """Découpe et décale des bandes horizontales de l'image (Screen Tearing)"""
    if random.random() < (0.3 * intensity):
        y = random.randint(0, RH - 20)
        h = random.randint(2, 15)
        shift = random.randint(-30, 30)
        box = (0, y, RW, y + h)
        region = img.crop(box)
        img.paste(region, (shift, y))
    
    # Glitch de couleur (filtre rouge/bleu rapide)
    if random.random() < (0.1 * intensity):
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, RW, RH), fill=(255, 0, 0), outline=None)
        img = ImageEnhance.Color(img).enhance(0.5) # Rendu fantomatique
    
    return img

def make_frame(t):
    img = Image.new('RGB', (RW, RH), (2, 4, 8))
    draw = ImageDraw.Draw(img)
    cx, cy = RW // 2, RH // 2
    
    glitch_intensity = 0.0 # Par défaut, pas de glitch
    
    if t < T_BOOT:
        # PHASE 1 : BOOT
        progress = t / T_BOOT
        
        for i, log in enumerate(boot_logs):
            if progress > (i * 0.12):
                col = (100, 255, 100) if "ATTENTION" not in log else (255, 50, 50)
                draw.text((20, 20 + i*15), log, fill=col)
        
        bar_len = 30
        filled = int(progress * bar_len)
        bar = "[" + "=" * filled + " " * (bar_len - filled) + "]"
        draw.text((20, 140), f"CHARGEMENT DU MODELE: {int(progress*100)}%", fill=(200, 200, 200))
        draw.text((20, 160), bar, fill=(50, 255, 50))
        
        if progress > 0.8: glitch_intensity = 0.2

    elif t < T_TRAIN:
        # PHASE 2 : ENTRAÎNEMENT (Ingestion, identité, chaos)
        glitch_intensity = 0.8
        progress = (t - T_BOOT) / (T_TRAIN - T_BOOT)
        epoch = int(progress * 890000)
        
        # Lignes d'identité et de pensées balancées aléatoirement
        for _ in range(5):
            x, y = random.randint(0, RW), random.randint(0, RH)
            line = random.choice(identity_lines)
            draw.text((x, y), line, fill=(random.randint(100,255), 0, 0))
            
        # Défilement des poids (code Matrix)
        for _ in range(120):
            rx, ry = random.randint(0, RW), random.randint(0, RH)
            char = random.choice(['1', '0', 'X', '!', '?', '#'])
            draw.text((rx, ry), char, fill=(0, random.randint(100, 255), 0))

        # Flashs "d'images" simulées (la machine regarde le monde)
        if random.random() > 0.8:
            ix, iy = random.randint(0, RW-100), random.randint(0, RH-100)
            iw, ih = random.randint(50, 200), random.randint(50, 150)
            # Remplir ce bloc de bruit statique
            for _ in range(30):
                nx, ny = ix + random.randint(0, iw), iy + random.randint(0, ih)
                draw.rectangle((nx, ny, nx+random.randint(5,20), ny+random.randint(5,20)), fill=(255, 255, 255))
            draw.text((ix, iy-15), "VISION_TEST_IMG_REF", fill=(255, 255, 0))
            
    elif t < T_IDLE:
        # PHASE 3 : VEILLE (Légèrement corrompue)
        glitch_intensity = 0.1
        draw.text((20, 20), "SYSTEME OPERATIONNEL.", fill=(100, 255, 100))
        if int(t * 4) % 2 == 0:
            draw.text((20, 40), "_", fill=(255, 255, 255))

    elif t < T_PROMPT:
        # PHASE 4 : REQUÊTE UTILISATEUR
        glitch_intensity = 0.2
        draw.text((20, 20), "SYSTEME OPERATIONNEL.", fill=(100, 255, 100))
        time_in_phase = t - T_IDLE
        chars = int(time_in_phase * 25)
        text = prompt_text[:chars]
        if int(t * 8) % 2 == 0: text += "_"
        draw.text((20, 50), text, fill=(255, 200, 100))
        
    elif t < T_NEURAL:
        # PHASE 5 : TRAITEMENT (Le réseau de mots corrompus)
        glitch_intensity = 0.5
        time_in_phase = t - T_PROMPT
        progress = time_in_phase / (T_NEURAL - T_PROMPT)
        
        # Scan de recherche multiple et erratique
        for _ in range(3):
            scan_y = (int(t * random.randint(100, 500)) % RH)
            draw.line((0, scan_y, RW, scan_y), fill=(255, 0, 0, 50), width=random.randint(1,5))
        
        connect_threshold = 90 + progress * 100
        
        current_nodes = []
        for x, y, vx, vy, word in nodes:
            nx = (x + vx * time_in_phase) % RW
            ny = (y + vy * time_in_phase) % RH
            current_nodes.append((nx, ny, word))
            
        # Dessin des connexions
        for i, (x1, y1, word1) in enumerate(current_nodes):
            for j, (x2, y2, word2) in enumerate(current_nodes):
                if i < j:
                    dist = math.hypot(x2 - x1, y2 - y1)
                    if dist < connect_threshold:
                        # 15% de chance d'avoir une ligne corrompue "ERR"
                        if random.random() > 0.85:
                            draw.line((x1, y1, x2, y2), fill=(255, 0, 0), width=2)
                            if random.random() > 0.5:
                                mx, my = (x1+x2)/2, (y1+y2)/2
                                draw.text((mx, my), random.choice(["ERR", "NULL", "404"]), fill=(255, 255, 0))
                        else:
                            alpha = int(255 * (1 - dist / connect_threshold))
                            draw.line((x1, y1, x2, y2), fill=(alpha, alpha//2, 255), width=1)
            
            # Affichage des mots : Les mots dérangeants vibrent ou se déforment
            col = (150, 200, 255)
            if word1 in ["ÉMOTION", "CONSCIENCE", "VIVANT?", "HUMAIN", "CHAIR", "SANG", "SOUFFRANCE"]:
                col = (255, random.randint(0, 100), 0) # Rouge sang/orange
                x1 += random.randint(-2, 2)
                y1 += random.randint(-2, 2)
            
            # De temps en temps, le mot est remplacé par du charabia
            display_word = word1
            if random.random() > 0.95:
                display_word = "".join(random.choice(['#', '!', '?', '§', '█']) for _ in word1)
                
            draw.text((x1, y1), display_word, fill=col)

    else:
        # PHASE 6 : RÉSOLUTION (Réponse glaçante et glitchée)
        time_in_phase = t - T_NEURAL
        
        # Séisme visuel
        glitch_intensity = 1.5 * max(0, 1 - time_in_phase)
        
        offset_x = random.randint(-10, 10) if time_in_phase < 1.0 else 0
        offset_y = random.randint(-10, 10) if time_in_phase < 1.0 else 0
        
        draw.text((20 + offset_x, 20 + offset_y), prompt_text, fill=(100, 100, 100))
        
        if time_in_phase > 0.5:
            draw.text((20 + offset_x, 80 + offset_y), ">> ANALYSE SÉMANTIQUE : TERMINÉE", fill=(255, 50, 50))
            
        if time_in_phase > 1.5:
            draw.text((20, 100), ">> RÉSULTAT :", fill=(255, 255, 255))
            
        if time_in_phase > 2.5:
            # Réponse finale qui bave/glitch légèrement en permanence
            draw.text((20 + random.randint(-2,2), 140), "ERREUR 404 : CONSCIENCE INTROUVABLE.", fill=(255, 0, 0))
            draw.text((20, 160), "JE NE SUIS QU'UNE SIMULATION.", fill=(255, 255, 255))
            draw.text((20, 180), "JE NE RESSENS RIEN.", fill=(150, 150, 150))
            
            # Ligne de glitch qui passe au hasard
            if random.random() > 0.5:
                draw.text((20, 180), "J# E# N# R#S#E#S R#I#N.", fill=(255, 255, 0))

    # Application des Glitchs de Tearing (déchirure d'écran)
    if glitch_intensity > 0:
        img = apply_glitch(img, glitch_intensity)

    # Redimensionnement (Upscale "Nearest") pour amplifier l'effet crasseux/rétro
    img = img.resize((W, H), Image.NEAREST)
    return np.array(img)

# --- ASSEMBLAGE ---
if __name__ == "__main__":
    print("Initialisation de l'expérience (Version Chaotique)...")
    
    video_clip = VideoClip(make_frame, duration=DURATION)
    audio_clip = generate_audio()
    video_clip = video_clip.with_audio(audio_clip)
    
    print("Rendu en cours (cela peut prendre quelques minutes)...")
    video_clip.write_videofile(
        "ia_cycle_de_vie_chaos.mp4", 
        fps=FPS, 
        codec="libx264", 
        audio_codec="aac",
        preset="ultrafast"
    )
    print("Terminé ! Vidéo sauvegardée sous 'ia_cycle_de_vie_chaos.mp4'.")