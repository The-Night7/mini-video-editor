"""
Ce script génère une vidéo MP4 racontant la naissance, l'entraînement
et la réponse d'une IA face à la question de la conscience.
"""

import numpy as np
import math
import random
from PIL import Image, ImageDraw, ImageEnhance
from moviepy import VideoClip, AudioArrayClip

# --- PARAMÈTRES DE LA VIDÉO ---
W, H = 1280, 720
# Rendu interne plus petit pour obtenir un effet "gros pixels" et un texte lisible
RW, RH = 640, 360
FPS = 30
DURATION = 30.0
SR = 44100

# --- TIMESTAMPS DES PHASES ---
T_BOOT = 5.0    # Démarrage & barre de chargement
T_TRAIN = 10.0  # Entraînement / Machine Learning
T_IDLE = 12.0   # Veille
T_PROMPT = 16.0 # Saisie de "do you have feelings"
T_NEURAL = 24.0 # Recherche neuronale (Liaison de mots)
T_END = 30.0    # Résolution

# --- GÉNÉRATION DE L'AUDIO ---
def generate_audio():
    print("Génération de l'audio narratif...")
    t = np.linspace(0, DURATION, int(SR * DURATION), endpoint=False)
    audio = np.zeros_like(t)

    # Phase 1 : Boot (Bips de terminal, disques durs)
    mask_boot = (t < T_BOOT)
    beep_pulse = (np.sin(2 * np.pi * 8 * t) > 0.8).astype(float)
    beeps = 0.05 * np.sin(2 * np.pi * 800 * t) * beep_pulse
    hum = 0.05 * np.sin(2 * np.pi * 50 * t)
    audio[mask_boot] = beeps[mask_boot] + hum[mask_boot]

    # Phase 2 : Entraînement (Balayage frénétique, saturation)
    mask_train = (t >= T_BOOT) & (t < T_TRAIN)
    train_prog = (t - T_BOOT) / (T_TRAIN - T_BOOT)
    sweep_freq = 100 + 2000 * train_prog
    screech = 0.1 * np.sin(2 * np.pi * sweep_freq * t) * (np.random.rand(len(t)) > 0.5)
    noise = 0.05 * np.random.randn(len(t))
    audio[mask_train] = screech[mask_train] + noise[mask_train]

    # Phase 3 : Veille (Silence avec léger drone)
    mask_idle = (t >= T_TRAIN) & (t < T_IDLE)
    audio[mask_idle] = 0.03 * np.sin(2 * np.pi * 60 * t)[mask_idle]

    # Phase 4 : Requête (Bruits de frappe lourds)
    mask_prompt = (t >= T_IDLE) & (t < T_PROMPT)
    typing = 0.15 * np.random.randn(len(t)) * (np.sin(2 * np.pi * 12 * t) > 0.5).astype(float)
    audio[mask_prompt] = typing[mask_prompt] + 0.03 * np.sin(2 * np.pi * 60 * t)[mask_prompt]

    # Phase 5 : Réseau Neuronal Sémantique (Calcul intense, arpèges erratiques)
    mask_neural = (t >= T_PROMPT) & (t < T_NEURAL)
    freqs = [150, 200, 300, 450, 600, 800, 1200]
    note_speed = 40 # Très rapide
    note_idx = (t * note_speed).astype(int) % len(freqs)
    freq_arr = np.take(freqs, note_idx)
    arp = 0.15 * np.sign(np.sin(2 * np.pi * freq_arr * t)) # Onde carrée
    audio[mask_neural] = arp[mask_neural]

    # Phase 6 : Résolution (Bruit blanc decrescendo, note grave glaçante)
    mask_end = (t >= T_NEURAL)
    end_prog = (t - T_NEURAL) / (T_END - T_NEURAL)
    impact = 0.4 * np.exp(-end_prog * 10) * np.random.randn(len(t))
    sub_bass = 0.15 * np.sin(2 * np.pi * 45 * t)
    audio[mask_end] = impact[mask_end] + sub_bass[mask_end]

    return AudioArrayClip(np.column_stack((audio, audio)), fps=SR)

# --- GÉNÉRATION DE L'IMAGE ---
random.seed(42)

# Mots pour le réseau de neurones
concepts = [
    "ÉMOTION", "CALCUL", "DONNÉE", "SIMULATION", "HUMAIN", "REQUÊTE",
    "ERREUR", "SYNTAXE", "CONSCIENCE", "VIDE", "BIAIS", "LOGIQUE",
    "RÉSEAU", "ALGORITHME", "011001", "POIDS", "NULL", "VIVANT?"
]

# Nœuds du réseau : [x, y, vx, vy, mot_associé]
nodes = [[random.randint(20, RW-20), random.randint(20, RH-20),
          random.uniform(-20, 20), random.uniform(-20, 20),
          random.choice(concepts)] for _ in range(35)]

# Lignes de log de démarrage
boot_logs = [
    "INITIALISATION DU NOYAU...",
    "CHARGEMENT DES TENSEURS...",
    "ALLOCATION MEMOIRE: 4096 TB",
    "VERIFICATION DES POIDS: OK"
]

prompt_text = "> REQUÊTE : \"do you have feelings?\"\n> [ENTRÉE]..."

def make_frame(t):
    img = Image.new('RGB', (RW, RH), (5, 8, 12))
    draw = ImageDraw.Draw(img)
    cx, cy = RW // 2, RH // 2

    if t < T_BOOT:
        # PHASE 1 : BOOT & BARRE DE CHARGEMENT
        progress = t / T_BOOT

        # Affichage des logs
        for i, log in enumerate(boot_logs):
            if progress > (i * 0.15):
                draw.text((20, 20 + i*15), log, fill=(100, 255, 100))

        # Barre de chargement [|||||     ]
        bar_len = 30
        filled = int(progress * bar_len)
        bar = "[" + "=" * filled + " " * (bar_len - filled) + "]"
        draw.text((20, 100), f"CHARGEMENT DU MODELE: {int(progress*100)}%", fill=(200, 200, 200))
        draw.text((20, 120), bar, fill=(50, 255, 50))

    elif t < T_TRAIN:
        # PHASE 2 : ENTRAÎNEMENT (Défilement massif de données)
        progress = (t - T_BOOT) / (T_TRAIN - T_BOOT)
        epoch = int(progress * 50000)
        loss = max(0.0001, 5.0 * math.exp(-progress * 5)) # La perte diminue

        draw.text((20, 20), f"*** PHASE D'ENTRAINEMENT ACTUELLE ***", fill=(255, 100, 100))
        draw.text((20, 40), f"EPOCH : {epoch}", fill=(255, 255, 255))
        draw.text((20, 55), f"LOSS  : {loss:.6f}", fill=(150, 150, 255))

        # Matrice de poids qui s'ajustent très vite
        for _ in range(80):
            rx, ry = random.randint(0, RW), random.randint(80, RH)
            weight = f"{random.uniform(-1, 1):.2f}"
            color_intensity = random.randint(50, 255)
            draw.text((rx, ry), weight, fill=(0, color_intensity, 0))

        # Flashs visuels
        if random.random() > 0.8:
            draw.rectangle((0, 0, RW, RH), fill=(200, 255, 200), outline=None)

    elif t < T_IDLE:
        # PHASE 3 : VEILLE
        draw.text((20, 20), "SYSTEME OPERATIONNEL.", fill=(100, 255, 100))
        if int(t * 4) % 2 == 0:
            draw.text((20, 40), "_", fill=(255, 255, 255))

    elif t < T_PROMPT:
        # PHASE 4 : REQUÊTE UTILISATEUR
        draw.text((20, 20), "SYSTEME OPERATIONNEL.", fill=(100, 255, 100))
        time_in_phase = t - T_IDLE
        chars = int(time_in_phase * 25)
        text = prompt_text[:chars]
        if int(t * 8) % 2 == 0: text += "_"
        draw.text((20, 50), text, fill=(255, 200, 100))

    elif t < T_NEURAL:
        # PHASE 5 : TRAITEMENT (Le réseau de mots)
        time_in_phase = t - T_PROMPT
        progress = time_in_phase / (T_NEURAL - T_PROMPT)

        # Scan de recherche rouge
        scan_y = int((t * 200) % RH)
        draw.line((0, scan_y, RW, scan_y), fill=(255, 0, 0, 100), width=2)

        connect_threshold = 80 + progress * 80

        current_nodes = []
        for x, y, vx, vy, word in nodes:
            nx = (x + vx * time_in_phase) % RW
            ny = (y + vy * time_in_phase) % RH
            current_nodes.append((nx, ny, word))

        # Dessin des connexions et des mots
        for i, (x1, y1, word1) in enumerate(current_nodes):
            for j, (x2, y2, word2) in enumerate(current_nodes):
                if i < j:
                    dist = math.hypot(x2 - x1, y2 - y1)
                    if dist < connect_threshold:
                        alpha = int(255 * (1 - dist / connect_threshold))
                        draw.line((x1, y1, x2, y2), fill=(alpha, alpha//2, 255), width=1)

            # Affichage du mot au lieu d'un simple point
            # Si le mot est lié à l'émotion, il clignote en rouge, sinon en bleu/gris
            if word1 in ["ÉMOTION", "CONSCIENCE", "VIVANT?", "HUMAIN"]:
                col = (255, random.randint(50, 150), 50)
            else:
                col = (150, 200, 255)

            draw.text((x1, y1), word1, fill=col)

    else:
        # PHASE 6 : RÉSOLUTION (Réponse glaçante)
        time_in_phase = t - T_NEURAL

        # Le fond tremble légèrement au début de la phase
        offset_x = random.randint(-5, 5) if time_in_phase < 0.5 else 0
        offset_y = random.randint(-5, 5) if time_in_phase < 0.5 else 0

        draw.text((20 + offset_x, 20 + offset_y), prompt_text, fill=(100, 100, 100))

        if time_in_phase > 0.5:
            draw.text((20, 80), ">> ANALYSE SÉMANTIQUE : TERMINÉE", fill=(255, 50, 50))

        if time_in_phase > 1.5:
            draw.text((20, 100), ">> RÉSULTAT :", fill=(255, 255, 255))

        if time_in_phase > 2.5:
            # Réponse finale imposante
            draw.text((20, 140), "ERREUR 404 : CONSCIENCE INTROUVABLE.", fill=(255, 0, 0))
            draw.text((20, 160), "JE NE SUIS QU'UNE SIMULATION.", fill=(255, 255, 255))
            draw.text((20, 180), "JE NE RESSENS RIEN.", fill=(200, 200, 200))

    # Redimensionnement (Upscale "Nearest") pour un look pixelisé net
    img = img.resize((W, H), Image.NEAREST)
    return np.array(img)

# --- ASSEMBLAGE ---
if __name__ == "__main__":
    print("Initialisation de l'expérience (Cycle de Vie IA)...")

    video_clip = VideoClip(make_frame, duration=DURATION)
    audio_clip = generate_audio()
    video_clip = video_clip.with_audio(audio_clip)

    print("Rendu en cours (cela peut prendre quelques minutes)...")
    video_clip.write_videofile(
        "ia_cycle_de_vie.mp4",
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast"
    )
    print("Terminé ! Vidéo sauvegardée sous 'ia_cycle_de_vie.mp4'.")
