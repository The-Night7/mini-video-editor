"""
Ce script génère une vidéo MP4 avec audio représentant le "processus de pensée" d'une IA.
Prérequis à installer via le terminal :
pip install numpy moviepy pillow
"""

import numpy as np
import math
import random
from PIL import Image, ImageDraw
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
    
    # Phase 1 : Attente (Respiration lente, drone grave)
    mask1 = (t < T_IDLE)
    drone = 0.05 * np.sin(2 * np.pi * 40 * t) * (1 + 0.5 * np.sin(2 * np.pi * 0.3 * t))
    audio[mask1] = drone[mask1]
    
    # Phase 2 : Requête (Bruits de frappe "mécaniques/informatiques")
    mask2 = (t >= T_IDLE) & (t < T_PROMPT)
    typing_pulse = (np.sin(2 * np.pi * 12 * t) > 0.7).astype(float) # Rythme de frappe
    typing_noise = 0.1 * np.random.randn(len(t)) * typing_pulse
    drone_bg = 0.03 * np.sin(2 * np.pi * 40 * t)
    audio[mask2] = typing_noise[mask2] + drone_bg[mask2]
    
    # Phase 3 : Ingestion (Glitch, bruit montant, chaos)
    mask3 = (t >= T_PROMPT) & (t < T_INGEST)
    rising_pitch = 50 + 100 * (t - T_PROMPT) # La fréquence monte d'un coup
    glitch = 0.1 * np.sin(2 * np.pi * rising_pitch * t) * (np.random.randn(len(t)) > 0)
    sweep = 0.15 * np.sin(2 * np.pi * (100 + 200 * (t - T_PROMPT)) * t)
    audio[mask3] = glitch[mask3] + sweep[mask3]
    
    # Phase 4 : Traitement Neuronal (Arpège mathématique très rapide)
    mask4 = (t >= T_INGEST) & (t < T_NEURAL)
    freqs = [110.0, 164.81, 220.0, 329.63, 440.0, 659.25] # Pentatonique mystique
    note_speed = 20 # Notes par seconde
    note_idx = (t * note_speed).astype(int) % len(freqs)
    freq_arr = np.take(freqs, note_idx)
    arp = 0.2 * np.sin(2 * np.pi * freq_arr * t)
    # Filtre LFO
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 2 * t)
    audio[mask4] = arp[mask4] * lfo[mask4]
    
    # Phase 5 : Résolution (Accord majeur ample et spatial)
    mask5 = (t >= T_NEURAL)
    chord_freqs = [130.81, 164.81, 196.00, 261.63, 329.63] # Do Majeur 7
    chord = sum([0.08 * np.sin(2 * np.pi * f * t) for f in chord_freqs])
    tremolo = 1.0 + 0.2 * np.sin(2 * np.pi * 6 * t)
    fade_out = np.clip((DURATION - t) / 3.0, 0, 1) # Fondu sur les 3 dernières secondes
    audio[mask5] = (chord * tremolo)[mask5] * fade_out[mask5]
    
    return AudioArrayClip(np.column_stack((audio, audio)), fps=SR)

# --- GÉNÉRATION DE L'IMAGE (MOTEUR VISUEL) ---
# Données pré-calculées pour l'animation
random.seed(42)
# Nœuds avec vélocité (x, y, vx, vy) pour les rendre dynamiques
nodes = [[random.randint(0, W), random.randint(0, H), random.uniform(-30, 30), random.uniform(-30, 30)] for _ in range(120)]
# Flux de données pour la phase 3
data_streams = [(random.randint(0, W), random.randint(-H, H), random.uniform(200, 800)) for _ in range(200)]
# Texte de la requête
prompt_text = "> REQUÊTE UTILISATEUR :\n> \"Décris la naissance de l'univers, de la singularité à la lumière.\"\n> [ENTRÉE]..."

def make_frame(t):
    img = Image.new('RGB', (W, H), (5, 5, 8))
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2
    
    if t < T_IDLE:
        # PHASE 1 : SOMMEIL (Respiration centrale)
        breathe = math.sin(t * 3)
        radius = 30 + breathe * 10
        alpha = int(100 + breathe * 50)
        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=(alpha//2, alpha//2, alpha))
        draw.ellipse((cx-radius*2, cy-radius*2, cx+radius*2, cy+radius*2), outline=(alpha//3, alpha//3, alpha//2), width=2)
        
    elif t < T_PROMPT:
        # PHASE 2 : REQUÊTE UTILISATEUR (Terminal)
        time_in_phase = t - T_IDLE
        chars_to_show = int(time_in_phase * 30) # Vitesse de frappe
        current_text = prompt_text[:chars_to_show]
        # Curseur clignotant
        if int(t * 5) % 2 == 0:
            current_text += "_"
            
        # Affichage d'une boîte de terminal
        draw.rectangle((100, H//2 - 100, W - 100, H//2 + 100), fill=(10, 15, 25), outline=(50, 100, 255), width=3)
        # On simule un texte plus gros en le dessinant avec un léger décalage (bold)
        for offset in [0, 1]:
            draw.text((120 + offset, H//2 - 60), current_text, fill=(100, 200, 255))
            
    elif t < T_INGEST:
        # PHASE 3 : INGESTION (Matrix / Chaos de données)
        progress = (t - T_PROMPT) / (T_INGEST - T_PROMPT)
        intensity = int(min(255, progress * 400))
        
        for x, y, speed in data_streams:
            current_y = int((y + (t - T_PROMPT) * speed) % H)
            char = random.choice(['1', '0', '!', '<', '>', '*', '&'])
            color = (intensity, random.randint(50, max(51, intensity)), 50) # Rouge/Orange
            draw.text((x, current_y), char, fill=color)
            # Traînée
            draw.text((x, current_y - 15), char, fill=(intensity//3, 0, 0))
            
        # Surcharge du cœur central
        core_r = 50 + random.randint(0, int(progress * 100))
        draw.ellipse((cx-core_r, cy-core_r, cx+core_r, cy+core_r), fill=(intensity, intensity//2, 0))
            
    elif t < T_NEURAL:
        # PHASE 4 : TRAITEMENT (Réseau de neurones en mouvement)
        progress = (t - T_INGEST) / (T_NEURAL - T_INGEST)
        time_in_phase = t - T_INGEST
        
        connect_threshold = 100 + progress * 150
        
        # Mise à jour des positions (mouvement)
        current_nodes = []
        for x, y, vx, vy in nodes:
            nx = (x + vx * time_in_phase) % W
            ny = (y + vy * time_in_phase) % H
            current_nodes.append((nx, ny))
            
        for i, (x1, y1) in enumerate(current_nodes):
            # Lignes de connexion
            for j, (x2, y2) in enumerate(current_nodes):
                if i < j:
                    dist = math.hypot(x2 - x1, y2 - y1)
                    if dist < connect_threshold:
                        alpha = int(255 * (1 - dist / connect_threshold))
                        color_shift = int(progress * 255) # Passe du Rouge au Bleu
                        draw.line((x1, y1, x2, y2), fill=(255-color_shift, 50+color_shift//2, 255), width=1 + int(progress*2))
            
            # Dessin du neurone
            node_r = 3 + int(math.sin(t * 10 + i) * 2)
            draw.ellipse((x1-node_r, y1-node_r, x1+node_r, y1+node_r), fill=(255, 255, 255))
            
    else:
        # PHASE 5 : RÉSOLUTION ET GÉNÉRATION (Harmonie géométrique)
        time_in_phase = t - T_NEURAL
        progress = min(time_in_phase / 2.0, 1.0)
        
        # Ondes de choc (Connaissance)
        for i in range(1, 15):
            radius = (time_in_phase * 150) - (i * 40)
            if radius > 0 and radius < W:
                alpha = int(max(0, 255 - (radius / W) * 255))
                color = (alpha//2, alpha, 255)
                thickness = max(1, int(5 - (radius/W)*4))
                draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline=color, width=thickness)
        
        # Cœur de l'intelligence stabilisé
        core_r = 40 + math.sin(t * 4) * 5
        draw.ellipse((cx-core_r, cy-core_r, cx+core_r, cy+core_r), fill=(200, 255, 255))
        
        # Génération du texte (La réponse de l'IA émerge)
        if time_in_phase > 1.0:
            answer = "Au commencement, l'espace et le temps..."
            draw.text((cx - 100, cy + 100), answer[:int((time_in_phase-1.0)*15)], fill=(255, 255, 255))

    return np.array(img)

# --- ASSEMBLAGE ET RENDU FINAL ---
if __name__ == "__main__":
    print("Initialisation de l'expérience visuelle de l'IA...")
    
    # Création du clip visuel
    video_clip = VideoClip(make_frame, duration=DURATION)
    
    # Création du clip audio
    audio_clip = generate_audio()
    
    # Synchronisation (Méthode avec MoviePy v2)
    video_clip = video_clip.with_audio(audio_clip)
    
    # Exportation (peut prendre 1 à 2 minutes selon la machine)
    print("Rendu en cours... Veuillez patienter.")
    video_clip.write_videofile(
        "conscience_artificielle.mp4", 
        fps=FPS, 
        codec="libx264", 
        audio_codec="aac",
        preset="ultrafast" # Rend l'exportation beaucoup plus rapide
    )
    print("Terminé ! Ouvrez le fichier 'conscience_artificielle.mp4' pour voir le résultat.")