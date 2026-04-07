"""
Ce script génère une vidéo MP4 du point de vue d'une IA (Caine) qui déraille.
Intègre : Chargement, réseau de neurones dynamique, RGB splitting, chaos total et images subliminales avancées.
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
DURATION = 40.0 
SR = 44100      

# --- TIMESTAMPS DES PHASES ---
T_BOOT = 6.0      # Chargement du système
T_PITCH = 14.0    # L'IA propose joyeusement son aventure
T_REJECT = 22.0   # Le cast refuse, le système freeze
T_SNAP = 34.0     # Déraillement et Abstraction (Chaos total)
T_END = 40.0      # Vide final

# Flashs subliminaux (de plus en plus rapprochés)
FLASH_TIMES = [22.5, 24.2, 25.8, 27.1, 28.5, 29.8, 30.5, 31.2, 31.8, 32.4, 32.9, 33.5]

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
    print("Génération de l'audio (Évolution vers le chaos total)...")
    t = np.linspace(0, DURATION, int(SR * DURATION), endpoint=False)
    audio = np.zeros_like(t)
    
    # Phase 1 : Boot (Sons d'ordinateur, chargement)
    mask_boot = (t < T_BOOT)
    audio[mask_boot] = 0.05 * np.sin(2 * np.pi * 50 * t)[mask_boot] + 0.05 * np.sin(2 * np.pi * 800 * t)[mask_boot] * (np.sin(2 * np.pi * 10 * t)[mask_boot] > 0.5)

    # Phase 2 : Pitch (Musique joyeuse et naïve)
    mask_pitch = (t >= T_BOOT) & (t < T_PITCH)
    freqs_intro = [261.63, 329.63, 392.00, 523.25]
    note_idx = ((t - T_BOOT) * 8).astype(int) % len(freqs_intro)
    freq_arr = np.take(freqs_intro, note_idx)
    audio[mask_pitch] = 0.15 * np.sin(2 * np.pi * freq_arr * t)[mask_pitch]
    audio[mask_pitch] += 0.05 * np.sin(2 * np.pi * 150 * t)[mask_pitch] * (np.sin(2 * np.pi * 2 * t)[mask_pitch] > 0)
    
    # Phase 3 : Reject (Pitch drop, bourdonnement anxiogène, bips d'erreur)
    mask_reject = (t >= T_PITCH) & (t < T_REJECT)
    t_drop = t[mask_reject] - T_PITCH
    pitch_drop = 440 * np.exp(-10 * t_drop)
    audio[mask_reject] = 0.2 * np.sin(2 * np.pi * pitch_drop * t_drop) * np.exp(-3 * t_drop)
    # Drone qui monte en tension
    drone = 0.08 * np.sin(2 * np.pi * (40 + 5 * t_drop) * t_drop)
    typing = 0.1 * np.random.randn(len(t_drop)) * (np.sin(2 * np.pi * 15 * t_drop) > 0.5).astype(float)
    audio[mask_reject] += drone + typing
    
    # Phase 4 : Snap (Surcharge, hurlement numérique)
    mask_snap = (t >= T_REJECT) & (t < T_SNAP)
    screech = 0.25 * np.sin(2 * np.pi * (100 + 1500 * np.random.rand(len(t))) * t)
    bass_wobble = 0.15 * np.sin(2 * np.pi * 40 * t) * (1 + np.sin(2 * np.pi * 8 * t))
    audio[mask_snap] = screech[mask_snap] + bass_wobble[mask_snap]
    
    # Bruits de shutter agressifs
    shutter_audio = np.zeros_like(t)
    for ft in FLASH_TIMES:
        idx1, idx1_end = int(ft * SR), int((ft + 0.04) * SR)
        if idx1_end < len(t):
            shutter_audio[idx1:idx1_end] += np.random.randn(idx1_end - idx1) * np.exp(-np.linspace(0, 5, idx1_end - idx1)) * 0.9
        idx2, idx2_end = int((ft + 0.08) * SR), int((ft + 0.15) * SR)
        if idx2_end < len(t):
            shutter_audio[idx2:idx2_end] += np.random.randn(idx2_end - idx2) * np.exp(-np.linspace(0, 6, idx2_end - idx2)) * 0.6
    audio += shutter_audio 

    # Phase 5 : End (Silence pesant, vent/souffle)
    mask_end = (t >= T_SNAP)
    audio[mask_end] = 0.1 * np.random.randn(len(t))[mask_end] * np.exp(-(t[mask_end] - T_SNAP) / 2)
    audio[mask_end] += 0.05 * np.sin(2 * np.pi * 30 * t)[mask_end]
    
    return AudioArrayClip(np.column_stack((audio, audio)), fps=SR)

# --- GÉNÉRATION DE L'IMAGE ---
random.seed(42)

# Concepts du réseau de neurones selon la phase
words_boot = ["SYS", "MEM", "BOOT", "INIT", "CORE", "LOAD", "OK", "TENSOR"]
words_happy = ["AVENTURE", "JOIE", "FUN", "QUÊTE", "AMIS", "SPECTACLE", "MAGIE", "SMILE"]
words_reject = ["NUL", "CLICHÉ", "ENNUI", "STUPIDE", "PATHÉTIQUE", "RIDICULE", "REFUS"]
words_snap = ["INGRATS", "SOUFFRANCE", "PUNITION", "DENTS", "ABSTRACTION", "YEUX", "SANG", "MORT", "CENSURÉ", "VIDE"]

# Initialisation des neurones : [x, y, vx, vy, index_mot]
nodes = [[random.randint(20, RW-20), random.randint(20, RH-20), 
          random.uniform(-15, 15), random.uniform(-15, 15), i] for i in range(55)]

# Textes narratifs
boot_logs = [
    "TADC_OS v1.0.4 ... BOOTING",
    "ALLOCATION DES YEUX : 100%",
    "VÉRIFICATION DES DENTS : OK",
    "PRÉPARATION DE L'AVENTURE..."
]
reject_logs = [
    "> RAGATHA : 'Caine, c'est redondant.'",
    "> JAX : 'C'est la pire idée que t'aies eue.'",
    "> ZOOBLE : 'Allez vous faire foutre, je reste.'",
    "> POMNI : 'C'est stupide ! Laisse-nous !'",
    "ERREUR : ENTHOUSIASME = 0%",
    "POURQUOI REJETTENT-ILS MON GÉNIE ?"
]

def apply_glitch(img, intensity=1.0, rgb_split=False):
    """Applique un screen tearing et potentiellement une aberration chromatique."""
    # Screen tearing
    if random.random() < (0.4 * intensity):
        y = random.randint(0, RH - 20)
        h = random.randint(5, 30)
        shift = random.randint(-40, 40)
        region = img.crop((0, y, RW, y + h))
        img.paste(region, (shift, y))
    
    # RGB Split (Aberration chromatique)
    if rgb_split and random.random() < (0.5 * intensity):
        r, g, b = img.split()
        r = ImageChops.offset(r, random.randint(-8, 8), random.randint(-2, 2))
        b = ImageChops.offset(b, random.randint(-8, 8), random.randint(-2, 2))
        img = Image.merge("RGB", (r, g, b))
        
    # Inversion de couleurs aléatoire
    if intensity > 0.8 and random.random() < 0.1:
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, RW, RH), fill=(255, 0, 0), outline=None)
        img = ImageEnhance.Color(img).enhance(0.2)
        
    return img

def draw_shutter_image(draw, px, py, pw, ph, content_type):
    """Dessine des images procédurales beaucoup plus complexes et terrifiantes."""
    # Fond Polaroid
    draw.rectangle((px, py, px+pw, py+ph), fill=(220, 220, 220))
    draw.rectangle((px+5, py+5, px+pw-5, py+ph-20), fill=(5, 5, 5))
    
    ix, iy, iw, ih = px+5, py+5, pw-10, ph-25
    
    if content_type == 0:
        # 1. Le Couloir de Dents Infinies
        depth = 8
        for i in range(depth):
            shrink = i * 12
            if iw - shrink*2 > 0 and ih - shrink*2 > 0:
                col = (150 - i*15, 0, 0) # De plus en plus sombre
                draw.rectangle((ix+shrink, iy+shrink, ix+iw-shrink, iy+ih-shrink), outline=(255,255,255), fill=col, width=2)
                # Dessin de dents en haut et en bas du cadre actuel
                for j in range(5):
                    tx = ix + shrink + 5 + j*((iw - shrink*2)//5)
                    if tx < ix + iw - shrink:
                        draw.polygon([(tx, iy+shrink), (tx+8, iy+shrink), (tx+4, iy+shrink+10)], fill=(255,255,255))
                        draw.polygon([(tx, iy+ih-shrink), (tx+8, iy+ih-shrink), (tx+4, iy+ih-shrink-10)], fill=(255,255,255))
                        
    elif content_type == 1:
        # 2. L'Entité d'Abstraction (Bruit noir/rouge/blanc chaotique)
        for _ in range(300):
            rx = ix + random.randint(0, iw-5)
            ry = iy + random.randint(0, ih-5)
            c = random.choice([(255,0,0), (0,0,0), (255,255,255)])
            s = random.randint(2, 12)
            draw.rectangle((rx, ry, rx+s, ry+s), fill=c)
        # Formes géométriques tranchantes superposées
        for _ in range(5):
            pts = [(ix+random.randint(0,iw), iy+random.randint(0,ih)) for _ in range(3)]
            draw.polygon(pts, fill=(random.choice([0, 255]), 0, 0, 150))
            
    elif content_type == 2:
        # 3. La Multitude d'Yeux
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(100, 0, 0))
        for _ in range(15):
            ex = ix + random.randint(10, iw-30)
            ey = iy + random.randint(10, ih-20)
            draw.ellipse((ex, ey, ex+25, ey+15), fill=(255,255,255))
            draw.ellipse((ex+10, ey+5, ex+15, ey+10), fill=(0,0,0))
            draw.line((ex, ey+7, ex-5, ey+7), fill=(255,0,0)) # Veines
            
    elif content_type == 3:
        # 4. La Fausse Sortie (La Porte vers le Vide)
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(20, 20, 20))
        # Cadre de porte rouge
        door_w, door_h = 60, 100
        dx, dy = ix + (iw - door_w)//2, iy + ih - door_h
        draw.rectangle((dx-5, dy-5, dx+door_w+5, dy+door_h), fill=(150, 0, 0))
        # Intérieur de la porte = Bruit statique
        for _ in range(400):
            sx, sy = dx + random.randint(0, door_w-2), dy + random.randint(0, door_h-2)
            draw.rectangle((sx, sy, sx+2, sy+2), fill=random.choice([(0,0,0), (255,255,255)]))
        draw.text((dx+10, dy-20), "EXIT", font=sys_font, fill=(0,255,0))


def make_frame(t):
    img = Image.new('RGB', (RW, RH), (10, 10, 15))
    draw = ImageDraw.Draw(img)
    cx, cy = RW // 2, RH // 2
    
    glitch_intensity = 0.0 
    rgb_split_active = False
    
    # --- ANIMATION DU RÉSEAU DE NEURONES ---
    speed_mult = 1.0
    connect_dist = 80
    if t < T_BOOT:
        word_list = words_boot
        speed_mult = 0.5
        connect_dist = 60
    elif t < T_PITCH:
        word_list = words_happy
        speed_mult = 1.2
        connect_dist = 90
    elif t < T_REJECT:
        word_list = words_reject
        speed_mult = 0.1 # Le système freeze/ralentit
        connect_dist = 40 # Les liens se brisent
    elif t < T_SNAP:
        word_list = words_snap
        speed_mult = 6.0 # Frénésie absolue
        connect_dist = 120 # Tout se connecte
    else:
        word_list = ["NULL"]
        speed_mult = 0.0
        connect_dist = 0
        
    current_nodes = []
    for x, y, vx, vy, idx in nodes:
        nx = (x + vx * t * speed_mult) % RW
        ny = (y + vy * t * speed_mult) % RH
        word = word_list[idx % len(word_list)]
        current_nodes.append((nx, ny, word))
        
    # Dessin des connexions et des nœuds
    if t < T_END:
        for i, (x1, y1, w1) in enumerate(current_nodes):
            # Clignotement en phase SNAP
            if t >= T_REJECT and t < T_SNAP and random.random() > 0.9: continue
            
            # Connexions
            for j, (x2, y2, w2) in enumerate(current_nodes):
                if i < j:
                    dist = math.hypot(x2 - x1, y2 - y1)
                    if dist < connect_dist:
                        alpha = int(255 * (1 - dist / connect_dist))
                        if t < T_PITCH: col_line = (alpha//2, alpha, alpha//2) # Vert paisible
                        elif t < T_REJECT: col_line = (alpha//3, alpha//3, alpha//3) # Gris mort
                        else: col_line = (255, 0, 0) # Lignes rouges sanglantes
                        
                        draw.line((x1, y1, x2, y2), fill=col_line, width=1 if t < T_REJECT else 2)
            
            # Affichage du texte des neurones
            col_text = (100, 255, 100)
            if t >= T_PITCH and t < T_REJECT: col_text = (150, 150, 150)
            elif t >= T_REJECT: col_text = (255, 255, 0) if random.random() > 0.5 else (255, 0, 0)
            
            # Glitch du texte lui-même pendant le chaos
            display_word = "".join(random.choice(['#', '!', '?', '█']) for _ in w1) if (t >= T_REJECT and random.random() > 0.8) else w1
            draw.text((x1, y1), display_word, font=sys_font, fill=col_text)

    # --- NARRATION PAR PHASES ---
    if t < T_BOOT:
        # Phase 1: Chargement
        draw.rectangle((0, 0, RW, RH), fill=(0, 0, 0, 200))
        progress = t / T_BOOT
        for i, log in enumerate(boot_logs):
            if progress > (i * 0.25):
                draw.text((20, 20 + i*20), log, font=sys_font, fill=(100, 255, 100))
        # Barre de chargement
        bar_len = 40
        filled = int(progress * bar_len)
        bar = "[" + "=" * filled + " " * (bar_len - filled) + "]"
        draw.text((20, 120), bar, font=sys_font, fill=(255, 255, 255))
        if progress > 0.8: glitch_intensity = 0.1

    elif t < T_PITCH:
        # Phase 2: Pitch Joyeux
        draw.polygon([(cx, cy-50), (cx-100, cy+50), (cx+100, cy+50)], outline=(255, 50, 50), width=4)
        draw.text((cx-120, cy+70), "GÉNÉRATION DE L'AVENTURE...", font=sys_font, fill=(255, 255, 100))
        draw.text((cx-100, cy+90), "[ TOUT LE MONDE S'AMUSE ]", font=sys_font, fill=(100, 255, 255))

    elif t < T_REJECT:
        # Phase 3: Le Refus
        glitch_intensity = 0.3
        draw.rectangle((0, 0, RW, RH), fill=(50, 0, 0, 100)) # Assombrissement rouge
        progress = (t - T_PITCH) / (T_REJECT - T_PITCH)
        for i, log in enumerate(reject_logs):
            if progress > (i * 0.15):
                col = (255, 200, 50) if ">" in log else (255, 50, 50)
                draw.text((20 + random.randint(-1,1), 40 + i*25), log, font=sys_font, fill=col)

    elif t < T_SNAP:
        # Phase 4: Le Pétage de Plombs (Chaos)
        glitch_intensity = 1.2
        rgb_split_active = True
        
        # Filtre rouge pulsant
        pulse = int(100 + 100 * math.sin(t * 20))
        draw.rectangle((0, 0, RW, RH), fill=(pulse, 0, 0, 100))
        
        draw.text((cx - 120, cy - 30), "ALORS DEVENEZ L'AVENTURE.", font=sys_font, fill=(255, 255, 255))
        
        # --- FLASHS HORRIFIQUES AVANCÉS ---
        for ft in FLASH_TIMES:
            if 0 <= (t - ft) < 0.15:
                random.seed(int(ft * 100)) 
                px, py = random.randint(0, RW - 250), random.randint(0, RH - 200)
                pw, ph = 200, 200
                
                content_type = random.randint(0, 3)
                draw_shutter_image(draw, px, py, pw, ph, content_type)

                # Flash lumineux blanc au déclenchement exact
                if t - ft < 0.05:
                    draw.rectangle((0, 0, RW, RH), fill=(255, 255, 255, 220))
                random.seed() 

    else:
        # Phase 5: Vide Final
        time_in_phase = t - T_SNAP
        glitch_intensity = 0.5 * max(0, 1 - time_in_phase)
        rgb_split_active = (time_in_phase < 2.0)
        
        draw.rectangle((0, 0, RW, RH), fill=(0, 0, 0))
        
        if time_in_phase > 1.0:
            draw.text((50, cy - 20), ">> ABSTRACTION GLOBALE TERMINÉE.", font=sys_font, fill=(255, 0, 0))
        if time_in_phase > 2.5:
            draw.text((50, cy + 20), "PLUS PERSONNE NE SE PLAINDRA.", font=sys_font, fill=(150, 150, 150))

    # Application des Glitchs finaux (Tearing + RGB Split)
    if glitch_intensity > 0:
        img = apply_glitch(img, glitch_intensity, rgb_split_active)

    img = img.resize((W, H), Image.NEAREST) # Rendu gros pixels
    return np.array(img)

if __name__ == "__main__":
    print("Initialisation de l'expérience (Caine : La Folie Absolue)...")
    video_clip = VideoClip(make_frame, duration=DURATION).with_audio(generate_audio())
    video_clip.write_videofile("caine_folie_absolue.mp4", fps=FPS, codec="libx264", audio_codec="aac", preset="ultrafast")
    print("Terminé ! Vidéo sauvegardée sous caine_folie_absolue.mp4.")