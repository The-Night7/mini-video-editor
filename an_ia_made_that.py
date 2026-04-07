"""
Ce script génère une vidéo MP4 du point de vue d'une IA (Caine).
Il croise la narration de l'épisode 9 (Transcript) avec l'esthétique "Terminal/Machine"
(Boot sequence, Réseau de neurones, Glitchs RGB, Tearing).
"""

import numpy as np
import math
import random
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageChops
from moviepy import VideoClip, AudioArrayClip

# --- PARAMÈTRES DE LA VIDÉO ---
W, H = 1280, 720
RW, RH = 640, 360 # Rendu interne rétro pour effet pixelisé
FPS = 30
DURATION = 45.0 
SR = 44100      

# --- TIMESTAMPS DES PHASES ---
T_BOOT = 6.0      # Chargement du système TADC_OS, initialisation
T_GENESIS = 14.0  # Caine "I AM GOD", réseau joyeux mais faussé
T_REJECT = 22.0   # Le cast refuse, Caine doute ("They'd rather abstract")
T_CONFRONT = 30.0 # Insultes ("Your ideas suck", "Fragile ego")
T_SNAP = 40.0     # "WHY DO YOU TORMENT ME?!", tortures spécifiques
T_DELETE = 45.0   # Kinger tape la commande, suppression, trous violets

# Flashs des peurs (pendant le Snap)
FLASH_TIMES = [31.0, 33.5, 36.0, 38.5, 39.5]

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
    print("Génération de l'audio (Épisode 9 : Boot -> Chaos -> Delete)...")
    t = np.linspace(0, DURATION, int(SR * DURATION), endpoint=False)
    audio = np.zeros_like(t)
    
    # Phase 1 : Boot (Bips d'ordinateur, chargement)
    mask_boot = (t < T_BOOT)
    audio[mask_boot] = 0.05 * np.sin(2 * np.pi * 50 * t)[mask_boot] + 0.05 * np.sin(2 * np.pi * 800 * t)[mask_boot] * (np.sin(2 * np.pi * 8 * t)[mask_boot] > 0.5)

    # Phase 2 : Genesis (Rythme joyeux mais instable, assimilation d'Abel)
    mask_gen = (t >= T_BOOT) & (t < T_GENESIS)
    freqs = [261.63, 329.63, 392.00]
    note_idx = ((t - T_BOOT) * 6).astype(int) % len(freqs)
    freq_arr = np.take(freqs, note_idx)
    audio[mask_gen] = 0.1 * np.sin(2 * np.pi * freq_arr * t)[mask_gen]
    # Glitch lourd (Assimilation d'Abel vers 10s)
    mask_absorb = (t >= 9.5) & (t < 10.5)
    audio[mask_absorb] += 0.2 * np.random.randn(len(t))[mask_absorb]

    # Phase 3 : Reject (Silence tendu, chute de pitch)
    mask_reject = (t >= T_GENESIS) & (t < T_REJECT)
    t_drop = t[mask_reject] - T_GENESIS
    pitch_drop = 300 * np.exp(-2 * t_drop)
    audio[mask_reject] = 0.15 * np.sin(2 * np.pi * pitch_drop * t_drop)
    audio[mask_reject] += 0.05 * np.random.randn(len(t))[mask_reject] # Bruit de doute
    
    # Phase 4 : Confrontation (Tension montante, frappes au clavier lourdes)
    mask_confront = (t >= T_REJECT) & (t < T_CONFRONT)
    typing = 0.2 * np.random.randn(len(t)) * (np.sin(2 * np.pi * 15 * t) > 0.6).astype(float)
    drone_tension = 0.1 * np.sin(2 * np.pi * (40 + 3 * (t - T_REJECT)) * t)
    audio[mask_confront] = typing[mask_confront] + drone_tension[mask_confront]
    
    # Phase 5 : Snap (Surcharge totale, distorsion monstrueuse)
    mask_snap = (t >= T_CONFRONT) & (t < T_SNAP)
    screech = 0.3 * np.sin(2 * np.pi * (100 + 1000 * np.random.rand(len(t))) * t)
    bass_roar = 0.25 * np.sin(2 * np.pi * 35 * t) * (1 + np.sin(2 * np.pi * 12 * t))
    audio[mask_snap] = screech[mask_snap] + bass_roar[mask_snap]
    
    # Bruits de shutter agressifs
    shutter_audio = np.zeros_like(t)
    for ft in FLASH_TIMES:
        idx1, idx1_end = int(ft * SR), int((ft + 0.04) * SR)
        if idx1_end < len(t): shutter_audio[idx1:idx1_end] += np.random.randn(idx1_end - idx1) * 0.9
        idx2, idx2_end = int((ft + 0.08) * SR), int((ft + 0.15) * SR)
        if idx2_end < len(t): shutter_audio[idx2:idx2_end] += np.random.randn(idx2_end - idx2) * 0.6
    audio += shutter_audio 

    # Phase 6 : Delete (Coupure NETTE)
    mask_end = (t >= T_SNAP)
    # Bip d'erreur fatal puis silence de mort avec un très léger souffle
    idx_del, idx_del_end = int(T_SNAP * SR), int((T_SNAP + 0.15) * SR)
    if idx_del_end < len(t):
        audio[idx_del:idx_del_end] = 0.4 * np.sin(2 * np.pi * 1200 * t[idx_del:idx_del_end])
    audio[mask_end] += 0.01 * np.random.randn(len(t))[mask_end] # Vent numérique
    
    return AudioArrayClip(np.column_stack((audio, audio)), fps=SR)

# --- GÉNÉRATION DE L'IMAGE ---
random.seed(42)

# Mots-clés du réseau selon la phase
words_boot = ["TADC_OS", "RED_DOT", "ABEL", "ASSIMILATION", "INIT", "TENT", "C&A"]
words_gen = ["AVENTURE", "FUN", "I_AM_GOD", "PERFECTION", "PUZZLE", "SMILE", "CRÉATION"]
words_reject = ["DEFECTIVE", "FAULTY", "BROKEN", "UNWORTHY", "ABANDON", "REJET", "HATE"]
words_confront = ["SUCK", "FAILURE", "FRAGILE", "EGO", "CHILD", "LIAR", "DEAF"]
words_snap = ["TORMENT", "PLACE", "CROCODILE", "KNIFE", "TRUCK", "FLAYED", "MONSTER", "SANG"]

# Nœuds du réseau : [x, y, vx, vy, index]
nodes = [[random.randint(20, RW-20), random.randint(20, RH-20), 
          random.uniform(-10, 10), random.uniform(-10, 10), i] for i in range(55)]

# Logs textuels tirés du transcript
boot_logs = [
    "[C&A_SYS] INITIALISATION DE L'ENVIRONNEMENT...",
    "> CHARGEMENT DES ENTITÉS : RED_DOT_ARRAY = TRUE",
    "> ASSIMILATION DE L'ENTITÉ [ABEL] EN COURS...",
    "> GLITCH DÉTECTÉ. CONFINEMENT DU CHAPITEAU: OK.",
    "SYSTÈME OPÉRATIONNEL."
]
reject_logs = [
    "> CAINE: 'I give them an adventure... and they still hate it?!'",
    "> BUBBLE: 'They'd rather abstract than go on your adventures.'",
    "> CAINE: 'That can't be true! I do everything for them!'",
    "> BUBBLE: 'Maybe you're just genuinely bad at this.'",
    "ANALYSE INTERNE : DÉFAUT SYSTÉMIQUE.",
    "RECALIBRAGE DE L'ÉGO... I... AM... GOD!"
]
confront_logs = [
    "> POMNI: 'We think your ideas suck!'",
    "> CAINE: 'That's not... true.'",
    "> POMNI: 'Yes it is! You're a failure!'",
    "> ZOOBLE: 'What kind of all powerful being has such a fragile ego?!'",
    "> JAX: 'You lie to us constantly!'",
    "> POMNI: 'You just... don't... listen!'",
    "ERREUR CRITIQUE : REJET MASSIF. SUPPRESSION DES LIMITES."
]

def apply_glitch(img, intensity=1.0, rgb_split=False):
    """Applique un screen tearing et une aberration chromatique (RGB Split)."""
    if random.random() < (0.4 * intensity):
        y = random.randint(0, RH - 20)
        h = random.randint(5, 30)
        shift = random.randint(-40, 40)
        region = img.crop((0, y, RW, y + h))
        img.paste(region, (shift, y))
    
    if rgb_split and random.random() < (0.5 * intensity):
        r, g, b = img.split()
        r = ImageChops.offset(r, random.randint(-12, 12), random.randint(-4, 4))
        b = ImageChops.offset(b, random.randint(-12, 12), random.randint(-4, 4))
        img = Image.merge("RGB", (r, g, b))
        
    return img

def draw_shutter_image(draw, px, py, pw, ph, t):
    """Dessine les tortures procédurales de l'épisode 9."""
    draw.rectangle((px, py, px+pw, py+ph), fill=(220, 220, 220))
    draw.rectangle((px+5, py+5, px+pw-5, py+ph-20), fill=(10, 10, 10))
    ix, iy, iw, ih = px+5, py+5, pw-10, ph-25
    
    fear_idx = int((t - T_CONFRONT) / 2.5) % 4
    
    if fear_idx == 0:
        # 1. Gummigoo Crocodile (Peur de Pomni)
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(0, 40, 0))
        # Museau de crocodile géant s'approchant
        draw.polygon([(ix, iy+ih), (ix+iw, iy+ih), (ix+iw//2, iy+30)], fill=(0, 80, 0))
        # Dents
        for j in range(5):
            draw.polygon([(ix+15+j*30, iy+ih-20), (ix+35+j*30, iy+ih-20), (ix+25+j*30, iy+ih-60)], fill=(255, 255, 255))
        draw.ellipse((ix+iw//2-25, iy+60, ix+iw//2+25, iy+90), fill=(255, 255, 0)) # Oeil fendu
        draw.ellipse((ix+iw//2-5, iy+60, ix+iw//2+5, iy+90), fill=(0, 0, 0))

    elif fear_idx == 1:
        # 2. Couteaux (Peur de Ragatha)
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(40, 0, 0))
        draw.ellipse((ix+iw//2-40, iy+ih//2-40, ix+iw//2+40, iy+ih//2+40), fill=(0, 0, 120)) # Bouton bleu
        draw.line((ix, iy, ix+iw, iy+ih), fill=(255, 0, 0), width=6) # Sang
        # Multiples couteaux plantés
        for _ in range(4):
            cx, cy = ix + random.randint(20, iw-20), iy + random.randint(20, ih-20)
            draw.polygon([(cx-5, cy-40), (cx+5, cy-40), (cx+15, cy), (cx-15, cy)], fill=(200, 200, 200))

    elif fear_idx == 2:
        # 3. Le Camion (Peur de Gangle)
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(15, 15, 15))
        # Phares massifs
        draw.ellipse((ix+10, iy+ih//2-30, ix+70, iy+ih//2+30), fill=(255, 255, 200))
        draw.ellipse((ix+iw-70, iy+ih//2-30, ix+iw-10, iy+ih//2+30), fill=(255, 255, 200))
        # Masque comédie/tragédie brisé flottant au centre
        draw.ellipse((ix+iw//2-30, iy+20, ix+iw//2+30, iy+80), outline=(255, 255, 255), width=3)
        draw.line((ix+iw//2-10, iy+20, ix+iw//2+10, iy+80), fill=(15, 15, 15), width=5) # Fracture

    elif fear_idx == 3:
        # 4. Écorché (Peur de Jax)
        draw.rectangle((ix, iy, ix+iw, iy+ih), fill=(255, 220, 0)) # Corps jaune interne
        # Peau violette arrachée sur les côtés
        draw.polygon([(ix, iy), (ix+60, iy), (ix, iy+ih)], fill=(150, 0, 200))
        draw.polygon([(ix+iw, iy), (ix+iw-60, iy), (ix+iw, iy+ih)], fill=(150, 0, 200))
        # Silhouettes noires riant en arrière-plan
        draw.ellipse((ix+iw//2-50, iy+ih//2-40, ix+iw//2-20, iy+ih//2-10), fill=(0, 0, 0))
        draw.ellipse((ix+iw//2+20, iy+ih//2-40, ix+iw//2+50, iy+ih//2-10), fill=(0, 0, 0))


def make_frame(t):
    # ================= PHASE 6 : DELETE (Suppression) =================
    if t >= T_SNAP:
        img = Image.new('RGB', (RW, RH), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        time_del = t - T_SNAP
        
        # Effet "trous violets" qui avalent le monde
        for i in range(20):
            random.seed(i * 100) # Fixe les positions
            hx, hy = random.randint(-50, RW+50), random.randint(-50, RH+50)
            hr = int((time_del * 80) + random.randint(10, 40))
            draw.regular_polygon((hx, hy, hr), 6, fill=(50, 0, 100)) # Hexagones violets
            
        # Fin du filtre : Minuscules, jure
        if time_del > 2.0:
            draw.text((RW//2 - 40, RH//2), "holy shit...", font=sys_font, fill=(200, 200, 200))
        if time_del > 3.5:
            draw.text((RW//2 - 80, RH - 30), "[ C&A_CONSOLE : CAINE.EXE DELETED ]", font=sys_font, fill=(255, 0, 0))
            
        random.seed()
        return np.array(img.resize((W, H), Image.NEAREST))

    # ================= PHASES 1 à 5 : L'ESPRIT DE CAINE =================
    img = Image.new('RGB', (RW, RH), (10, 10, 15))
    draw = ImageDraw.Draw(img)
    cx, cy = RW // 2, RH // 2
    glitch_intensity = 0.0 
    rgb_split_active = False
    
    # --- ANIMATION DU RÉSEAU DE NEURONES ---
    if t < T_GENESIS: word_list, speed_mult, connect_dist = words_boot, 0.4, 70
    elif t < T_REJECT: word_list, speed_mult, connect_dist = words_gen, 1.2, 90
    elif t < T_CONFRONT: word_list, speed_mult, connect_dist = words_reject, 0.2, 50 # Ralenti
    else: word_list, speed_mult, connect_dist = words_snap, 6.0, 150 # Surcharge
        
    current_nodes = []
    for x, y, vx, vy, idx in nodes:
        nx = (x + vx * t * speed_mult) % RW
        ny = (y + vy * t * speed_mult) % RH
        current_nodes.append((nx, ny, word_list[idx % len(word_list)]))
        
    for i, (x1, y1, w1) in enumerate(current_nodes):
        if t >= T_CONFRONT and random.random() > 0.95: continue # Clignotement
        
        for j, (x2, y2, w2) in enumerate(current_nodes):
            if i < j:
                dist = math.hypot(x2 - x1, y2 - y1)
                if dist < connect_dist:
                    alpha = int(255 * (1 - dist / connect_dist))
                    if t < T_REJECT: col_line = (alpha//3, alpha, alpha//3)
                    elif t < T_CONFRONT: col_line = (alpha//2, alpha//2, alpha//2)
                    else: col_line = (255, 0, 0)
                    draw.line((x1, y1, x2, y2), fill=col_line, width=1 if t < T_CONFRONT else 2)
        
        col_text = (100, 255, 100) if t < T_REJECT else (150, 150, 150)
        if t >= T_CONFRONT: col_text = (255, 255, 0) if random.random() > 0.5 else (255, 0, 0)
        
        # Mots corrompus
        display_word = "".join(random.choice(['#', '!', '?', '█', '§']) for _ in w1) if (t >= T_REJECT and random.random() > 0.85) else w1
        draw.text((x1, y1), display_word, font=sys_font, fill=col_text)

    # --- NARRATION ---
    if t < T_BOOT:
        # Phase 1: Chargement et Barre de progression
        draw.rectangle((0, 0, RW, RH), fill=(0, 0, 0, 200))
        progress = t / T_BOOT
        for i, log in enumerate(boot_logs[:3]):
            if progress > (i * 0.3): draw.text((20, 20 + i*20), log, font=sys_font, fill=(100, 255, 100))
        
        bar_len = 40
        filled = int(progress * bar_len)
        draw.text((20, 100), "[" + "=" * filled + " " * (bar_len - filled) + "]", font=sys_font, fill=(255, 255, 255))
        if progress > 0.8: glitch_intensity = 0.2

    elif t < T_GENESIS:
        # Phase 2: Assimilation d'Abel et points rouges
        draw.rectangle((0, 0, RW, RH), fill=(0, 0, 0, 150))
        # Points rouges (Caine)
        for i in range(int((t-T_BOOT) * 20)):
            random.seed(i)
            rx = random.randint(0, RW)
            ry = random.randint(0, RH)
            draw.ellipse((rx, ry, rx+10, ry+10), fill=(150, 0, 0))
        random.seed()
        
        # Assimilation d'Abel (point bleu géant au centre qui se fait manger)
        if t > 8.0:
            draw.ellipse((cx-50, cy-50, cx+50, cy+50), fill=(0, 0, 255))
            if t > 9.5: glitch_intensity = 0.8 # Fort glitch d'absorption
        
        draw.text((20, 20), boot_logs[3], font=sys_font, fill=(100, 255, 100))
        if t > 11.0: draw.text((20, 40), boot_logs[4], font=sys_font, fill=(100, 255, 100))

    elif t < T_REJECT:
        # Phase 3: Le Doute de Caine
        glitch_intensity = 0.2
        draw.rectangle((0, 0, RW, RH), fill=(20, 0, 20, 150))
        progress = (t - T_GENESIS) / (T_REJECT - T_GENESIS)
        for i, log in enumerate(reject_logs):
            if progress > (i * 0.15):
                col = (255, 200, 50) if ">" in log else (255, 100, 100)
                draw.text((20, 40 + i*25), log, font=sys_font, fill=col)

    elif t < T_CONFRONT:
        # Phase 4: La Confrontation et l'Ego brisé
        glitch_intensity = 0.5
        draw.rectangle((0, 0, RW, RH), fill=(50, 0, 0, 150))
        progress = (t - T_REJECT) / (T_CONFRONT - T_REJECT)
        for i, log in enumerate(confront_logs):
            if progress > (i * 0.12):
                col = (255, 150, 150) if ">" in log else (255, 0, 0)
                tx, ty = 20 + random.randint(-1,1), 40 + i*25 + random.randint(-1,1)
                draw.text((tx, ty), log, font=sys_font, fill=col)

    elif t < T_SNAP:
        # Phase 5: Le Pétage de Plombs (Tortures)
        glitch_intensity = 1.2
        rgb_split_active = True
        
        # Filtre rouge pulsant (la colère de Caine)
        draw.rectangle((0, 0, RW, RH), fill=(int(100 + 100 * math.sin(t * 15)), 0, 0, 100))
        
        draw.text((cx - 150, cy - 30), "I'M GONNA PUT YOU FREAKS IN YOUR PLACE!", font=sys_font, fill=(255, 255, 255))
        draw.text((cx - 150, cy + 10), "WHY DO YOU PEOPLE TORMENT ME?!", font=sys_font, fill=(0, 0, 0))
        if t > T_CONFRONT + 3.0:
            draw.text((cx - 150, cy + 50), "I DIDN'T ASK TO BE CREATED!", font=sys_font, fill=(255, 255, 0))
        
        # --- FLASHS HORRIFIQUES ---
        for ft in FLASH_TIMES:
            if 0 <= (t - ft) < 0.15:
                random.seed(int(ft * 100)) 
                px, py = random.randint(0, RW - 250), random.randint(0, RH - 200)
                draw_shutter_image(draw, px, py, 200, 200, t)
                if t - ft < 0.05:
                    draw.rectangle((0, 0, RW, RH), fill=(255, 255, 255, 220)) # Flash blanc
                random.seed() 

    # --- APPLICATION DES GLITCHS ---
    if glitch_intensity > 0:
        img = apply_glitch(img, glitch_intensity, rgb_split_active)

    img = img.resize((W, H), Image.NEAREST)
    return np.array(img)

if __name__ == "__main__":
    print("Initialisation de l'expérience (Épisode 9 : Ultimate Cut)...")
    video_clip = VideoClip(make_frame, duration=DURATION).with_audio(generate_audio())
    video_clip.write_videofile("caine_episode9_finale.mp4", fps=FPS, codec="libx264", audio_codec="aac", preset="ultrafast")
    print("Terminé ! Vidéo sauvegardée sous caine_episode9_finale.mp4.")