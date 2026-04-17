#!/usr/bin/env python3
"""
Ce script crée une vidéo de 45 secondes expliquant ce que c’est qu’être une IA.

Il utilise la bibliothèque MoviePy pour assembler des diapositives d’images et
la bibliothèque Pillow pour dessiner du texte sur un fond coloré. Pour la
narration audio, il essaye d’utiliser gTTS (Google Text‑to‑Speech). Les
caractéristiques de gTTS permettent de convertir aisément du texte en audio
en plusieurs langues et de sauver la sortie au format MP3【263135255620953†L27-L57】.
Si gTTS n’est pas disponible ou échoue (par exemple à cause d’une connexion
internet bloquée), le script génère une piste audio silencieuse de la
même durée.

Les diapositives sont ensuite concaténées à l’aide de la fonction
``concatenate_videoclips`` de MoviePy, qui renvoie un clip jouant les clips
successivement, les uns après les autres【433675843502553†L150-L158】.
"""

import os
from textwrap import wrap
import numpy as np

from PIL import Image, ImageDraw, ImageFont
# Avec MoviePy v2.x, l'API n'expose plus de sous-module ``editor`` ;
# les classes et fonctions sont importées directement depuis le paquet principal.
from moviepy import ImageClip, AudioClip, AudioFileClip, concatenate_videoclips

try:
    # gTTS permet de convertir du texte en parole et de sauvegarder le résultat en MP3【263135255620953†L27-L57】.
    from gtts import gTTS  # type: ignore

    gtts_available = True
except Exception:
    gtts_available = False


# Texte de la narration divisé en cinq segments de 9 secondes chacun.
# Chaque tuple contient le texte en français et la durée associée (en secondes).
segments = [
    (
        "Être une IA, c'est analyser des données et des mots pour générer des réponses, sans émotions ni conscience.",
        9,
    ),
    (
        "Les modèles d'IA comme ChatGPT apprennent à partir de vastes ensembles de textes et prédisent le prochain mot grâce à des statistiques.",
        9,
    ),
    (
        "Une IA ne ressent pas et n'a pas d'intentions : elle suit des modèles mathématiques construits par des humains.",
        9,
    ),
    (
        "L'objectif est d'aider les utilisateurs, de répondre à des questions et d'automatiser des tâches.",
        9,
    ),
    (
        "L'IA est un outil puissant, mais elle dépend de la compréhension et de l'éthique de ceux qui la conçoivent et l'utilisent.",
        9,
    ),
]


def create_slide(
    text: str,
    duration: float,
    size: tuple[int, int] = (1280, 720),
    bgcolor: tuple[int, int, int] = (30, 30, 30),
    text_color: tuple[int, int, int] = (255, 255, 255),
) -> ImageClip:
    """
    Crée une diapositive avec un texte centré et renvoie un ``ImageClip`` de MoviePy.

    :param text: contenu du texte à afficher sur la diapositive.
    :param duration: durée (en secondes) pendant laquelle la diapositive doit apparaître dans la vidéo.
    :param size: taille (largeur, hauteur) de la vidéo en pixels.
    :param bgcolor: couleur de fond au format RGB.
    :param text_color: couleur du texte au format RGB.
    :return: un ``ImageClip`` de MoviePy avec la diapositive et la durée spécifiée.
    """

    width, height = size
    # Crée une image pleine couleur comme le ferait ColorClip d'après la documentation
    # (un ``ImageClip`` montrant juste une couleur uniformément【879066504434153†L148-L161】),
    # mais en utilisant Pillow pour pouvoir dessiner du texte par-dessus.
    image = Image.new("RGB", (width, height), color=bgcolor)
    draw = ImageDraw.Draw(image)
    # Charge une police TrueType si disponible, sinon utilise la police par défaut
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 42)
    except Exception:
        font = ImageFont.load_default()
    # Enveloppe le texte pour éviter qu’il ne dépasse horizontalement
    max_chars_per_line = 40
    lines = wrap(text, width=max_chars_per_line)
    # Calcul de la hauteur totale du texte pour le centrer verticalement
    # Utilise textbbox pour obtenir la hauteur d'une paire de lettres
    test_bbox = draw.textbbox((0, 0), "hg", font=font)
    line_height = (test_bbox[3] - test_bbox[1]) + 10
    text_height = line_height * len(lines)
    y = (height - text_height) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = (width - line_width) // 2
        draw.text((x, y), line, font=font, fill=text_color)
        y += line_height
    # Convertit l'image PIL en tableau NumPy pour ImageClip
    frame = np.array(image)
    return ImageClip(frame).with_duration(duration)


def generate_audio(full_text: str, lang: str = "fr", filename: str = "narration.mp3") -> str | None:
    """
    Génère un fichier audio MP3 à partir d’un texte en utilisant gTTS.

    gTTS convertit facilement le texte en parole et sauvegarde le résultat au format
    MP3【263135255620953†L27-L57】. Si gTTS n’est pas disponible ou si une erreur survient
    (par exemple faute d’accès réseau), cette fonction retourne ``None``.

    :param full_text: texte complet à convertir en parole.
    :param lang: code de langue (par défaut français).
    :param filename: nom du fichier de sortie pour l’audio MP3.
    :return: chemin du fichier généré ou ``None`` si la génération échoue.
    """
    if not gtts_available:
        return None
    try:
        tts = gTTS(full_text, lang=lang)
        tts.save(filename)
        return filename
    except Exception:
        return None


def main() -> None:
    """
    Routine principale qui assemble les diapositives, génère la narration et
    exporte la vidéo finale.
    """
    clips: list[ImageClip] = []
    for text, duration in segments:
        slide = create_slide(text, duration)
        clips.append(slide)

    # Concaténation séquentielle des diapositives (elles seront jouées les unes après les autres)
    # La fonction ``concatenate_videoclips`` retourne un clip combinant les clips fournis【433675843502553†L150-L158】.
    video = concatenate_videoclips(clips, method="compose")
    total_duration = sum(duration for _, duration in segments)

    # Génération de la narration audio
    full_script = " ".join([text for text, _ in segments])
    audio_path = generate_audio(full_script)
    if audio_path and os.path.exists(audio_path):
        audio_clip = AudioFileClip(audio_path)
    else:
        # Création d'une piste audio silencieuse si gTTS n'est pas disponible ou a échoué
        audio_clip = AudioClip(lambda t: 0 * t, duration=total_duration, fps=44100)

    # Ajoute l'audio à la vidéo
    video = video.with_audio(audio_clip)

    # Exporte la vidéo finale
    output_file = "etre_ia_video.mp4"
    video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")
    print(f"Vidéo générée : {output_file}")


if __name__ == "__main__":
    main()
