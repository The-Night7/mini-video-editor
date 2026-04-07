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
DURATION = 12.0 # durée totale en secondes
SR = 44100      # Fréquence d'échantillonnage audio (Sample Rate)

# --- GÉNÉRATION DE L'AUDIO (SYNTHÉTISEUR NUMÉRIQUE) ---
def generate_audio():
    print("Génération de l'audio numérique...")
    t = np.linspace(0, DURATION, int(SR * DURATION), endpoint=False)
    audio = np.zeros_like(t)
    
    # Phase 1 : Ingestion (Bruit statique et basses fréquences)
    # Simule le traitement de téraoctets de données brutes
    mask1 = (t < 4.0)
    drone = 0.1 * np.sin(2 * np.pi * 55 * t) # Basse fréquence
    noise = 0.05 * np.random.randn(len(t)) * (np.sin(2 * np.pi * 15 * t) > 0) # Grésillements
    audio[mask1] = drone[mask1] + noise[mask1]
    
    # Phase 2 : Traitement (Réseau de neurones / Arpège de calcul)
    # Simule les connexions synaptiques de l'IA
    mask2 = (t >= 4.0) & (t < 8.0)
    # Fréquences d'un arpège synthétique (A mineur complexe)
    freqs = [220.0, 277.18, 329.63, 440.0, 554.37] 
    note_idx = (t * 12).astype(int) % len(freqs) # 12 notes par seconde
    freq_arr = np.take(freqs, note_idx)
    arp = 0.15 * np.sin(2 * np.pi * freq_arr * t)
    # Ajout d'une enveloppe de fondu pour la transition
    fade_in_arp = np.clip(t - 4.0, 0, 0.5) * 2
    audio[mask2] = arp[mask2] * fade_in_arp[mask2]
    
    # Phase 3 : Synthèse / Sortie (Accord clair et harmonique)
    # Simule la clarté d'une réponse trouvée
    mask3 = (t >= 8.0)
    # Accord de Do Majeur (C, E, G, C)
    chord = 0.1 * (
        np.sin(2 * np.pi * 261.63 * t) + 
        np.sin(2 * np.pi * 329.63 * t) + 
        np.sin(2 * np.pi * 392.00 * t) +
        np.sin(2 * np.pi * 523.25 * t)
    )
    # Tremolo doux
    tremolo = 1.0 + 0.2 * np.sin(2 * np.pi * 4 * t)
    # Enveloppe globale pour terminer en douceur
    fade_out = np.clip((12.0 - t) / 2.0, 0, 1) 
    
    audio[mask3] = (chord * tremolo)[mask3] * fade_out[mask3]
    
    # Convertir en stéréo (2 colonnes)
    stereo_audio = np.column_stack((audio, audio))
    return AudioArrayClip(stereo_audio, fps=SR)

# --- GÉNÉRATION DE L'IMAGE (MOTEUR VISUEL) ---
# Pré-calculer les positions des neurones pour la phase 2
random.seed(42)
nodes = [(random.randint(100, W-100), random.randint(100, H-100)) for _ in range(100)]

def make_frame(t):
    # Créer un canevas noir vide avec Pillow
    img = Image.new('RGB', (W, H), (5, 5, 10))
    draw = ImageDraw.Draw(img)
    
    if t < 4.0:
        # PHASE 1 : INGESTION DES DONNÉES
        # Effet visuel rappelant le chaos de l'analyse lexicale
        intensity = min(255, max(50, int(t * 60)))
        for _ in range(500):
            x = random.randint(0, W)
            y = random.randint(0, H)
            color = (0, random.randint(50, intensity), 0) # Nuances de vert
            draw.text((x, y), random.choice(['0', '1', 'A', 'X', '{', '}']), fill=color)
            
    elif t < 8.0:
        # PHASE 2 : TRAITEMENT ET CONNEXIONS NEURALES
        progress = (t - 4.0) / 4.0  # Varie de 0 à 1 sur la phase
        
        # Le seuil de connexion augmente avec le temps, liant plus de neurones
        connect_threshold = progress * 250 
        
        for i, (x1, y1) in enumerate(nodes):
            # Dessiner les connexions synaptiques
            for j, (x2, y2) in enumerate(nodes):
                if i < j:
                    dist = math.hypot(x2 - x1, y2 - y1)
                    if dist < connect_threshold:
                        alpha = int(255 * (1 - dist / max(1, connect_threshold)))
                        # Lignes bleutées/blanches
                        draw.line((x1, y1, x2, y2), fill=(alpha//2, alpha//2, alpha), width=1)
            
            # Dessiner les neurones
            node_size = 2 + int(progress * 3)
            draw.ellipse((x1-node_size, y1-node_size, x1+node_size, y1+node_size), fill=(200, 200, 255))
            
    else:
        # PHASE 3 : SYNTHÈSE ET ÉMERGENCE DE L'IDÉE
        progress = min((t - 8.0) / 2.0, 1.0) # Varie de 0 à 1 sur les 2 premières secondes
        cx, cy = W // 2, H // 2
        
        # Anneaux concentriques représentant la structure de la réponse finale
        num_rings = int(10 * progress) + 1
        for i in range(num_rings):
            # Les anneaux pulsent et s'étendent mathématiquement
            radius = 20 + i * 35 + math.sin(t * 3 - i) * 15
            color = (
                int(50 + progress * 100), 
                int(150 + progress * 50), 
                255
            )
            # Epaisseur qui bat au rythme de la "pensée"
            thickness = max(1, int(3 + math.sin(t * 10) * 2))
            draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline=color, width=thickness)
            
        # Cœur central incandescent
        core_radius = 15 + math.sin(t * 8) * 5
        draw.ellipse((cx-core_radius, cy-core_radius, cx+core_radius, cy+core_radius), fill=(255, 255, 255))

    # Retourner l'image au format lisible par MoviePy (tableau NumPy RGB)
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