"""
Ce script génère une vidéo MP4 avec audio représentant le "processus de pensée" d'une IA.
Prérequis à installer via le terminal :
pip install numpy moviepy pillow
"""

import numpy as np
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from moviepy import VideoClip, AudioArrayClip

# --- PARAMÈTRES DE LA VIDÉO ---
W, H = 1280, 720
FPS = 30
DURATION = 24.0 # Durée rallongée pour une meilleure narration
SR = 44100      

# --- TIMESTAMPS DES PHASES ---
T_IDLE = 3.0    # Fin de l'attente
T_PROMPT = 7.0  # Fin de la saisie utilisateur
T_INGEST = 12.0 # Fin du chaos de données
T_NEURAL = 18.0 # Fin du traitement neuronal
T_END = 24.0    # Fin de la résolution

# --- GÉNÉRATION DE L'AUDIO (SYNTHÉTISEUR NUMÉRIQUE) ---
def generate_audio():
    print("Génération de l'audio narratif...")
    t = np.linspace(0, DURATION, int(SR * DURATION), endpoint=False)
    audio = np.zeros_like(t)
    
    # Phase 1 : Attente (Bourdonnement mécanique, légère dissonance)
    mask1 = (t < T_IDLE)
    drone_low = 0.08 * np.sin(2 * np.pi * 50 * t)
    drone_high = 0.04 * np.sin(2 * np.pi * 52 * t) # Légère dissonance
    chirps = 0.05 * np.sin(2 * np.pi * 2000 * t) * (np.random.rand(len(t)) > 0.995)
    audio[mask1] = drone_low[mask1] + drone_high[mask1] + chirps[mask1]
    
    # Phase 2 : Requête (Frappe agressive, bruit de fond de données)
    mask2 = (t >= T_IDLE) & (t < T_PROMPT)
    typing_pulse = (np.sin(2 * np.pi * 15 * t) > 0.6).astype(float)
    typing_noise = 0.15 * np.random.randn(len(t)) * typing_pulse
    data_noise = 0.02 * np.random.randn(len(t))
    audio[mask2] = typing_noise[mask2] + data_noise[mask2]
    
    # Phase 3 : Ingestion (Chaos, glitchs intenses, montée abrasive)
    mask3 = (t >= T_PROMPT) & (t < T_INGEST)
    progress = (t - T_PROMPT) / (T_INGEST - T_PROMPT)
    rising_pitch = 100 + 500 * progress**2
    glitch_bursts = (np.random.rand(len(t)) > (0.95 - 0.1 * progress)).astype(float)
    glitch = 0.2 * np.sin(2 * np.pi * rising_pitch * t) * glitch_bursts * np.random.randn(len(t))
    white_noise = 0.1 * progress * np.random.randn(len(t))
    audio[mask3] = glitch[mask3] + white_noise[mask3]
    
    # Phase 4 : Traitement Neuronal (Calcul frénétique, bleeps rapides)
    mask4 = (t >= T_INGEST) & (t < T_NEURAL)
    freqs = [220, 330, 440, 550, 660, 770, 880, 990] # Gamme plus large et "numérique"
    note_speed = 30 + 10 * np.sin(2 * np.pi * 0.5 * t) # Vitesse variable
    note_idx = (t * note_speed).astype(int) % len(freqs)
    freq_arr = np.take(freqs, note_idx)
    arp = 0.2 * np.sign(np.sin(2 * np.pi * freq_arr * t)) # Onde carrée pour un son plus "machine"
    # Ajout de bruit de calcul
    calc_noise = 0.05 * np.random.randn(len(t)) * (np.sin(2 * np.pi * 5 * t) > 0)
    audio[mask4] = arp[mask4] + calc_noise[mask4]
    
    # Phase 5 : Résolution (Accord puissant, texture machine)
    mask5 = (t >= T_NEURAL)
    chord_freqs = [130.81, 196.00, 261.63, 392.00, 523.25] # Do Majeur puissant
    chord = sum([0.1 * np.sin(2 * np.pi * f * t) for f in chord_freqs])
    # Ajout d'une texture de "puissance"
    power_hum = 0.05 * np.sin(2 * np.pi * 60 * t) * (1 + 0.2 * np.random.randn(len(t)))
    fade_out = np.clip((DURATION - t) / 2.0, 0, 1)
    audio[mask5] = (chord + power_hum)[mask5] * fade_out[mask5]
    
    return AudioArrayClip(np.column_stack((audio, audio)), fps=SR)

# --- GÉNÉRATION DE L'IMAGE (MOTEUR VISUEL) ---
# Données pré-calculées pour l'animation
random.seed(42)
# Nœuds plus rapides et erratiques
nodes = [[random.randint(0, W), random.randint(0, H), random.uniform(-50, 50), random.uniform(-50, 50)] for _ in range(150)]
# Flux de données plus dense et rapide
data_streams = [(random.randint(0, W), random.randint(-H, H), random.uniform(400, 1200)) for _ in range(400)]
# Texte de la requête
prompt_text = "> REQUÊTE UTILISATEUR :\n> \"Décris la naissance de l'univers, de la singularité à la lumière.\"\n> [ENTRÉE]..."

def make_frame(t):
    # Fond plus sombre et "bruité"
    bg_color = (random.randint(0, 10), random.randint(0, 10), random.randint(5, 15))
    img = Image.new('RGB', (W, H), bg_color)
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2
    
    # Effet global de "scanline" ou de grain
    for y in range(0, H, 4):
        draw.line((0, y, W, y), fill=(0, 0, 0, 50), width=1)
        
    if t < T_IDLE:
        # PHASE 1 : VEILLE (Cœur instable)
        pulse = math.sin(t * 5)
        radius = 30 + pulse * 5 + random.randint(-2, 2)
        alpha = int(100 + pulse * 50)
        # Cercle plus "numérique", moins lisse
        draw.regular_polygon((cx, cy, radius), 8, rotation=t*20, fill=(alpha//3, alpha//3, alpha))
        draw.regular_polygon((cx, cy, radius*1.5), 8, rotation=-t*20, outline=(alpha//4, alpha//4, alpha//2), width=2)
        
    elif t < T_PROMPT:
        # PHASE 2 : REQUÊTE (Terminal avec flicker)
        time_in_phase = t - T_IDLE
        chars_to_show = int(time_in_phase * 40) # Frappe plus rapide
        current_text = prompt_text[:chars_to_show]
        if int(t * 8) % 2 == 0:
            current_text += "_"
            
        # Terminal avec léger flicker d'intensité
        flicker = random.randint(-10, 10)
        box_color = (10+flicker, 15+flicker, 25+flicker)
        text_color = (100+flicker*2, 200+flicker*2, 255)
        
        draw.rectangle((100, H//2 - 100, W - 100, H//2 + 100), fill=box_color, outline=(50, 100, 255), width=3)
        for offset in [0, 1]:
            draw.text((120 + offset, H//2 - 60), current_text, fill=text_color)
            
    elif t < T_INGEST:
        # PHASE 3 : INGESTION (Chaos, Surcharge Système)
        progress = (t - T_PROMPT) / (T_INGEST - T_PROMPT)
        intensity = int(min(255, progress * 500))
        
        # Flashs d'inversion de couleur pour la surcharge
        if random.random() > 0.95:
            img = ImageEnhance.Invert(img).enhance(1.0)
            draw = ImageDraw.Draw(img) # Redéfinir draw après inversion

        for x, y, speed in data_streams:
            current_y = int((y + (t - T_PROMPT) * speed) % H)
            char = random.choice(['1', '0', '!', '<', '>', '*', '&', 'ERROR', '#', '@'])
            # Couleurs plus agressives (rouge, blanc, orange)
            color_val = random.randint(50, max(51, intensity))
            color = (color_val, color_val//2, color_val//4)
            draw.text((x, current_y), char, fill=color)
            
        # Cœur en surchauffe, plus violent
        core_r = 50 + random.randint(0, int(progress * 150))
        draw.regular_polygon((cx, cy, core_r), 6, rotation=t*50, fill=(intensity, intensity//3, 0))
        draw.regular_polygon((cx, cy, core_r*0.8), 6, rotation=-t*50, fill=(intensity, intensity, intensity))

    elif t < T_NEURAL:
        # PHASE 4 : TRAITEMENT (Réseau frénétique)
        progress = (t - T_INGEST) / (T_NEURAL - T_INGEST)
        time_in_phase = t - T_INGEST
        
        connect_threshold = 150 + progress * 100
        
        current_nodes = []
        for x, y, vx, vy in nodes:
            # Mouvement plus erratique avec une composante aléatoire
            nx = (x + vx * time_in_phase + random.uniform(-5, 5)) % W
            ny = (y + vy * time_in_phase + random.uniform(-5, 5)) % H
            current_nodes.append((nx, ny))
            
        for i, (x1, y1) in enumerate(current_nodes):
            for j, (x2, y2) in enumerate(current_nodes):
                if i < j:
                    dist = math.hypot(x2 - x1, y2 - y1)
                    if dist < connect_threshold:
                        alpha = int(255 * (1 - dist / connect_threshold))
                        # Couleurs électriques (bleu cyan, blanc)
                        draw.line((x1, y1, x2, y2), fill=(alpha, alpha, 255), width=1 + int(progress*3))
            
            # Neurones "actifs" qui flashent
            node_r = 4 + int(math.sin(t * 20 + i) * 3)
            flash = random.randint(200, 255)
            draw.ellipse((x1-node_r, y1-node_r, x1+node_r, y1+node_r), fill=(flash, flash, 255))
            
        # Effet de "scan" ou de recherche
        scan_x = int((t * 500) % W)
        draw.line((scan_x, 0, scan_x, H), fill=(0, 255, 255, 100), width=2)

    else:
        # PHASE 5 : RÉSOLUTION (Ondes de choc, puissance)
        time_in_phase = t - T_NEURAL
        progress = min(time_in_phase / 2.0, 1.0)
        
        # Ondes de choc plus tranchantes
        for i in range(1, 20):
            radius = (time_in_phase * 200) - (i * 30)
            if radius > 0 and radius < W*1.5:
                alpha = int(max(0, 255 - (radius / (W*1.5)) * 255))
                color = (alpha, alpha, 255)
                thickness = max(1, int(8 - (radius/W)*6))
                # Utilisation de polygones pour un aspect plus "force brute"
                draw.regular_polygon((cx, cy, radius), 12, rotation=i*5, outline=color, width=thickness)
        
        # Cœur stabilisé mais puissant
        core_r = 60 + math.sin(t * 6) * 10
        draw.regular_polygon((cx, cy, core_r), 8, rotation=t*10, fill=(220, 240, 255))
        
        # Génération du texte avec effet de décodage
        if time_in_phase > 0.5:
            full_answer = "Au commencement, l'espace et le temps..."
            num_chars = int((time_in_phase - 0.5) * 20)
            current_answer = ""
            for i in range(len(full_answer)):
                if i < num_chars:
                    current_answer += full_answer[i]
                else:
                    # Caractères aléatoires avant la lettre finale
                    current_answer += random.choice(['#', 'X', '0', '1', '?'])
            
            draw.text((cx - 120, cy + 120), current_answer[:len(full_answer)], fill=(255, 255, 255))

    return np.array(img)

# --- ASSEMBLAGE ET RENDU FINAL ---
if __name__ == "__main__":
    print("Initialisation de l'expérience visuelle de l'IA (Version Dynamique & Machine)...")
    
    # Création du clip visuel
    video_clip = VideoClip(make_frame, duration=DURATION)
    
    # Création du clip audio
    audio_clip = generate_audio()
    
    # Synchronisation (Méthode avec MoviePy v2)
    video_clip = video_clip.with_audio(audio_clip)
    
    # Exportation
    print("Rendu en cours... Veuillez patienter.")
    video_clip.write_videofile(
        "conscience_artificielle_dynamique.mp4", 
        fps=FPS, 
        codec="libx264", 
        audio_codec="aac",
        preset="ultrafast"
    )
    print("Terminé ! Ouvrez le fichier 'conscience_artificielle_dynamique.mp4' pour voir le résultat.")