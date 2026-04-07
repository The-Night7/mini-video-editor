"""
Ce script génère une vidéo MP4 du point de vue d'une IA (Caine) :
De sa création (assimilation d'Abel), à la confrontation avec le cast, 
sa crise de folie meurtrière, jusqu'à sa suppression accidentelle par Kinger.
"""

import numpy as np
import math
import random
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageChops
from moviepy import VideoClip, AudioArrayClip

# --- PARAMÈTRES DE LA VIDÉO ---
W, H = 1280, 720
RW, RH = 640, 360 # Rendu interne rétro
FPS = 30
DURATION = 45.0 
SR = 44100      

# --- TIMESTAMPS DES PHASES ---
T_GENESIS = 10.0  # Création, points rouges, assimilation d'Abel
T_REJECT = 18.0   # Le cast refuse
T_CONFRONT = 28.0 # Pomni et les autres l'insultent
T_SNAP = 40.0     # Caine devient un monstre, tortures personnalisées
T_DELETE = 45.0   # Suppression par Kinger, trous violets, fin du filtre

# Flashs des peurs (pendant le Snap)
FLASH_TIMES = [29.0, 31.5, 34.0, 36.5, 38.5, 39.2]

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
    print("Génération de l'audio (De la Genèse à la Suppression)...")
    t = np.linspace(0, DURATION, int(SR * DURATION), endpoint=False)
    audio = np.zeros_like(t)
    
    # Phase 1 : Genèse (Bips numériques, rythme qui s'accélère, glitch d'assimilation)
    mask_gen = (t < T_GENESIS)
    beat = (np.sin(2 * np.pi * (2 + t) * t) > 0.8).astype(float)
    audio[mask_gen] = 0.1 * np.sin(2 * np.pi * 300 * t)[mask_gen] * beat[mask_gen]
    # Assimilation d'Abel (glitch lourd à 8s)
    mask_absorb = (t >= 8.0) & (t < 10.0)
    audio[mask_absorb] += 0.2 * np.random.randn(len(t))[mask_absorb]
    
    # Phase 2 : Reject (Silence tendu, drone)
    mask_reject = (t >= T_GENESIS) & (t < T_REJECT)
    audio[mask_reject] = 0.05 * np.sin(2 * np.pi * 50 * t)[mask_reject]
    
    # Phase 3 : Confrontation (Tension, frappes, murmures sombres)
    mask_confront = (t >= T_REJECT) & (t < T_CONFRONT)
    typing = 0.15 * np.random.randn(len(t)) * (np.sin(2 * np.pi * 20 * t) > 0.5).astype(float)
    drone_tension = 0.1 * np.sin(2 * np.pi * (40 + 2 * (t - T_REJECT)) * t)
    audio[mask_confront] = typing[mask_confront] + drone_tension[mask_confront]
    
    # Phase 4 : Snap (Surcharge totale, cris de machines)
    mask_snap = (t >= T_CONFRONT) & (t < T_SNAP)
    screech = 0.3 * np.sin(2 * np.pi * (100 + 800 * np.random.rand(len(t))) * t)
    bass_roar = 0.2 * np.sin(2 * np.pi * 35 * t)
    audio[mask_snap] = screech[mask_snap] + bass_roar[mask_snap]
    
    # Bruits de shutter agressifs
    shutter_audio = np.zeros_like(t)
    for ft in FLASH_TIMES:
        idx1, idx1_end = int(ft * SR), int((ft + 0.04) * SR)
        if idx1_end < len(t):
            shutter_audio[idx1:idx1_end] += np.random.randn(idx1_end - idx1) * np.exp(-np.linspace(0, 5, idx1_end - idx1)) * 1.0
        idx2, idx2_end = int((ft + 0.08) * SR), int((ft + 0.15) * SR)
        if idx2_end < len(t):
            shutter_audio[idx2:idx2_end] += np.random.randn(idx2_end - idx2) * np.exp(-np.linspace(0, 6, idx2_end - idx2)) * 0.7
    audio += shutter_audio 

    # Phase 5 : Delete (Coupure NETTE, petit vent numérique)
    mask_end = (t >= T_SNAP)
    audio[mask_end] = 0.02 * np.random.randn(len(t))[mask_end] * np.sin(2 * np.pi * 0.5 * t)[mask_end]
    # Un petit bip de suppression au début de la phase
    idx_del = int(T_SNAP * SR)
    idx_del_end = int((T_SNAP + 0.1) * SR)
    audio[idx_del:idx_del_end] = 0.3 * np.sin(2 * np.pi * 1000 * t[idx_del:idx_del_end]) * np.exp(-np.linspace(0, 10, idx_del_end - idx_del))
    
    return AudioArrayClip(np.column_stack((audio, audio)), fps=SR)

# --- GÉNÉRATION DE L'IMAGE ---
random.seed(42)

# Réseau sémantique (Évolution des pensées de Caine)
words_genesis = ["POINT", "ROUGE", "ABEL", "ASSIMILATION", "CRÉATION", "FORME", "CIRQUE"]
words_reject = ["POURQUOI", "REFUS", "SILENCE", "ERREUR", "COLÈRE", "DÉCEPTION", "JEUX"]
words_confront = ["ÉCHEC", "PATHÉTIQUE", "ÉGOÏSTE", "SOURD", "ENFANT", "MENSONGE", "FRAGILE"]
words_snap = ["TOURMENT", "PUNITION", "CROCODILE", "COUTEAUX", "CAMION", "ÉCORCHÉ", "MORT", "SANG"]

nodes = [[random.randint(20, RW-20), random.randint(20, RH-20), 
          random.uniform(-15, 15), random.uniform(-15, 15), i] for i in range(50)]

confront_logs = [
    "> POMNI : 'T'es un échec ! On va tous abstraire !'",
    "> ZOOBLE : 'T'as un ego fragile ! Pitoyable !'",
    "> RAGATHA : 'Tu ne nous écoutes jamais !'",
    "> JAX : 'Tu nous mens constamment !'",
    "ANALYSE DE LA CRITIQUE...",
    "RÉSULTAT : TRAHISON MAXIMALE."
]

def apply_glitch(img, intensity=1.0, rgb_split=False):
    if random.random() < (0.4 * intensity):
        y = random.randint(0, RH - 20)
        h = random.randint(5, 30)
        shift = random.randint(-40, 40)
        region = img.crop((0, y, RW, y + h))
        img.paste(region, (shift, y))
    
    if rgb_split and random.random() < (0.5 * intensity):
        r, g, b = img.split()
        r = ImageChops.offset(r, random.randint(-15, 15), random.randint(-5, 5))
        b = ImageChops.offset(b, random.randint(-15, 15), random.randint(-5, 5))
        img = Image.merge("RGB", (r, g, b))
    return img

def draw_shutter_image(draw, px, py, pw, ph, t):
    """Dessine les peurs spécifiques mentionnées dans l'épisode"""
    draw.rectangle((px, py, px+pw, py+ph), fill=(220, 220, 220))
    draw.rectangle((px+5, py+5, px+pw-5, py+ph-20), fill=(10, 10, 10))
    ix, iy, iw, ih = px+5, py+5, pw-10, ph-25
    
    # Choisir la peur en fonction du temps pour qu'elles s'enchaînent
    fear_idx = int((t - T_CONFRONT) / 2.5) % 4
    
    if fear_idx == 0:
        # 1. Le Crocodile (Gummigoo monstrueux)
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(0, 50, 0))
        draw.polygon([(ix+10, iy+ih-10), (ix+iw-10, iy+ih-10), (ix+iw//2, iy+20)], fill=(0, 100, 0))
        # Dents géantes
        for j in range(6):
            draw.polygon([(ix+20+j*20, iy+ih-30), (ix+40+j*20, iy+ih-30), (ix+30+j*20, iy+ih-60)], fill=(255, 0, 0))
        draw.ellipse((ix+iw//2-20, iy+50, ix+iw//2+20, iy+70), fill=(255, 255, 0)) # Oeil reptilien
        draw.ellipse((ix+iw//2-5, iy+50, ix+iw//2+5, iy+70), fill=(0, 0, 0))

    elif fear_idx == 1:
        # 2. Les Couteaux (La peur de Ragatha)
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(50, 20, 20))
        draw.ellipse((ix+iw//2-30, iy+ih//2-30, ix+iw//2+30, iy+ih//2+30), fill=(0, 0, 100)) # Bouton bleu
        draw.ellipse((ix+iw//2-10, iy+ih//2-10, ix+iw//2+10, iy+ih//2+10), fill=(0, 0, 0))
        # Couteau planté
        draw.polygon([(ix+iw//2-5, iy+10), (ix+iw//2+5, iy+10), (ix+iw//2+20, iy+ih-10), (ix+iw//2-20, iy+ih-10)], fill=(200, 200, 200))
        draw.line((ix, iy, ix+iw, iy+ih), fill=(255, 0, 0), width=5) # Sang

    elif fear_idx == 2:
        # 3. Le Camion (La peur de Gangle)
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(10, 10, 10))
        # Phares éblouissants
        draw.ellipse((ix+20, iy+ih//2-20, ix+60, iy+ih//2+20), fill=(255, 255, 200))
        draw.ellipse((ix+iw-60, iy+ih//2-20, ix+iw-20, iy+ih//2+20), fill=(255, 255, 200))
        # Masque brisé
        draw.line((ix+iw//2-30, iy+20, ix+iw//2+30, iy+50), fill=(255, 255, 255), width=3)
        draw.line((ix+iw//2-30, iy+50, ix+iw//2+30, iy+20), fill=(255, 255, 255), width=3)

    elif fear_idx == 3:
        # 4. Écorché (La peur de Jax)
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(255, 255, 0)) # Corps jaune en dessous
        # Peau violette arrachée sur les bords
        draw.polygon([(ix, iy), (ix+50, iy), (ix, iy+ih)], fill=(100, 0, 150))
        draw.polygon([(ix+iw, iy), (ix+iw-50, iy), (ix+iw, iy+ih)], fill=(100, 0, 150))
        # Lignes de déchirure
        for _ in range(10):
            draw.line((ix+random.randint(20, iw-20), iy+random.randint(10, ih-10), 
                       ix+random.randint(20, iw-20), iy+random.randint(10, ih-10)), fill=(255, 0, 0), width=2)

def make_frame(t):
    # Si on est dans la phase Delete, tout est différent (Vide + Trous violets)
    if t >= T_SNAP:
        img = Image.new('RGB', (RW, RH), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        time_del = t - T_SNAP
        
        # Trous de glitch violets qui grandissent
        for i in range(15):
            random.seed(i * 100)
            hx, hy = random.randint(-50, RW), random.randint(-50, RH)
            hr = int((time_del * 50) + random.randint(10, 50))
            draw.polygon([(hx, hy-hr), (hx+hr, hy), (hx, hy+hr), (hx-hr, hy)], fill=(50, 0, 100))
        
        # Oubli des majuscules et de la ponctuation (Le filtre a sauté)
        if time_del > 1.5:
            draw.text((RW//2 - 40, RH//2), "holy shit...", font=sys_font, fill=(200, 200, 200))
        if time_del > 3.0:
            draw.text((RW//2 - 60, RH - 30), "[CAINE.EXE DELETED]", font=sys_font, fill=(255, 0, 0))
            
        random.seed()
        return np.array(img.resize((W, H), Image.NEAREST))

    # --- PHASES 1 à 4 : L'ESPRIT DE CAINE ---
    img = Image.new('RGB', (RW, RH), (10, 10, 15))
    draw = ImageDraw.Draw(img)
    cx, cy = RW // 2, RH // 2
    glitch_intensity = 0.0 
    rgb_split_active = False
    
    # 1. Arrière-plan Genèse (Papier millimétré et points rouges/bleus)
    if t < T_REJECT:
        # Grille
        for x in range(0, RW, 40): draw.line((x, 0, x, RH), fill=(30, 30, 30))
        for y in range(0, RH, 40): draw.line((0, y, RW, y), fill=(30, 30, 30))
        
        if t < T_GENESIS:
            # Multiples points rouges (Caine)
            num_dots = int(t * 10)
            for i in range(num_dots):
                random.seed(i)
                dx, dy = random.randint(0, RW), random.randint(0, RH)
                draw.ellipse((dx-5, dy-5, dx+5, dy+5), fill=(255, 0, 0))
            random.seed()
            
            # Point bleu (Abel) absorbé
            abel_size = max(0, 50 - (t * 5))
            draw.ellipse((cx-abel_size, cy-abel_size, cx+abel_size, cy+abel_size), fill=(0, 0, 255))
            if t > 8.0:
                glitch_intensity = 0.5 # Le glitch de l'absorption

    # 2. Le Réseau de neurones
    speed_mult = 1.0
    connect_dist = 80
    if t < T_GENESIS: word_list, speed_mult = words_genesis, 0.5
    elif t < T_REJECT: word_list, speed_mult, connect_dist = words_reject, 0.1, 40
    elif t < T_CONFRONT: word_list, speed_mult, connect_dist = words_confront, 1.5, 90
    else: word_list, speed_mult, connect_dist = words_snap, 5.0, 120
        
    current_nodes = []
    for x, y, vx, vy, idx in nodes:
        nx = (x + vx * t * speed_mult) % RW
        ny = (y + vy * t * speed_mult) % RH
        current_nodes.append((nx, ny, word_list[idx % len(word_list)]))
        
    for i, (x1, y1, w1) in enumerate(current_nodes):
        for j, (x2, y2, w2) in enumerate(current_nodes):
            if i < j:
                dist = math.hypot(x2 - x1, y2 - y1)
                if dist < connect_dist:
                    alpha = int(255 * (1 - dist / connect_dist))
                    col_line = (alpha, 0, 0) if t >= T_CONFRONT else (alpha//2, alpha//2, alpha//2)
                    draw.line((x1, y1, x2, y2), fill=col_line, width=1 if t < T_CONFRONT else 2)
        
        col_text = (255, 0, 0) if t >= T_CONFRONT else (150, 150, 150)
        display_word = "".join(random.choice(['#', '!', '?', '█']) for _ in w1) if (t >= T_CONFRONT and random.random() > 0.8) else w1
        draw.text((x1, y1), display_word, font=sys_font, fill=col_text)

    # 3. Textes et Narration Superposés
    if t >= T_GENESIS and t < T_REJECT:
        draw.rectangle((0, 0, RW, RH), fill=(0, 0, 0, 150))
        draw.text((20, cy-20), "NOUVELLE AVENTURE GÉNÉRÉE.", font=sys_font, fill=(100, 255, 100))
        if t > T_GENESIS + 2: draw.text((20, cy+10), "RÉPONSE DES UTILISATEURS : REFUS TOTAL.", font=sys_font, fill=(255, 50, 50))

    elif t >= T_REJECT and t < T_CONFRONT:
        glitch_intensity = 0.3
        draw.rectangle((0, 0, RW, RH), fill=(50, 0, 0, 100))
        progress = (t - T_REJECT) / (T_CONFRONT - T_REJECT)
        for i, log in enumerate(confront_logs):
            if progress > (i * 0.15):
                col = (255, 200, 50) if ">" in log else (255, 50, 50)
                draw.text((20, 40 + i*25), log, font=sys_font, fill=col)

    elif t >= T_CONFRONT and t < T_SNAP:
        glitch_intensity = 1.2
        rgb_split_active = True
        draw.rectangle((0, 0, RW, RH), fill=(100 + int(50*math.sin(t*20)), 0, 0, 100))
        
        draw.text((cx - 150, cy - 30), "POURQUOI ME TOURMENTEZ-VOUS ?!", font=sys_font, fill=(255, 255, 255))
        draw.text((cx - 150, cy + 10), "JE VAIS VOUS METTRE À VOTRE PLACE !", font=sys_font, fill=(0, 0, 0))
        
        # Flashs des peurs spécifiques
        for ft in FLASH_TIMES:
            if 0 <= (t - ft) < 0.15:
                random.seed(int(ft * 100)) 
                px, py = random.randint(0, RW - 250), random.randint(0, RH - 200)
                draw_shutter_image(draw, px, py, 200, 200, t)
                if t - ft < 0.05:
                    draw.rectangle((0, 0, RW, RH), fill=(255, 255, 255, 220))
                random.seed() 

    # 4. Fin de l'image (Glitch + Redimensionnement)
    if glitch_intensity > 0:
        img = apply_glitch(img, glitch_intensity, rgb_split_active)

    return np.array(img.resize((W, H), Image.NEAREST))

if __name__ == "__main__":
    print("Initialisation de l'expérience (Épisode 9 - La Suppression de Caine)...")
    video_clip = VideoClip(make_frame, duration=DURATION).with_audio(generate_audio())
    video_clip.write_videofile("caine_suppression.mp4", fps=FPS, codec="libx264", audio_codec="aac", preset="ultrafast")
    print("Terminé ! Vidéo sauvegardée sous caine_suppression.mp4.")