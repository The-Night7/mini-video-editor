#!/usr/bin/env python3
"""
Générateur de vidéo : Ce que c'est que d'être une IA
Durée : 45 secondes
"""

import cv2
import numpy as np
from datetime import datetime
import os
import math

# Configuration
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30
DURATION = 45  # secondes
TOTAL_FRAMES = DURATION * FPS

# Couleurs (BGR pour OpenCV)
DARK_BG = (10, 10, 30)
BLUE = (255, 180, 0)
CYAN = (255, 255, 100)
PURPLE = (200, 100, 255)
WHITE = (255, 255, 255)
LIGHT_BLUE = (220, 200, 150)

class VideoGenerator:
    def __init__(self, width, height, fps):
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_count = 0
        
    def create_gradient_background(self, frame_index, total_frames, color1, color2):
        """Crée un fond avec dégradé animé"""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Animation du dégradé
        shift = int(frame_index % 60)
        
        for y in range(self.height):
            # Interpolation entre deux couleurs avec animation
            ratio = (y + shift * 2) / (self.height + shift * 4)
            ratio = max(0, min(1, ratio))
            
            b = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            r = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            
            frame[y, :] = [b, g, r]
        
        return frame
    
    def draw_particles(self, frame, frame_index):
        """Ajoute des particules animées"""
        np.random.seed(42 + frame_index % 30)  # Seed déterministe pour cohérence
        
        num_particles = 50
        for i in range(num_particles):
            # Position sinusoidale
            x = int((self.width / 2) + 300 * np.sin(2 * np.pi * (frame_index / 60 + i / num_particles)))
            y = int((frame_index * 2 + i * 100) % self.height)
            
            size = max(1, 3 - frame_index // 60)
            color = (CYAN[0], CYAN[1] - i % 50, CYAN[2])
            cv2.circle(frame, (x, y), size, color, -1)
        
        return frame
    
    def draw_text_animated(self, frame, text, frame_index, start_frame, end_frame, y_pos=None):
        """Dessine du texte avec animation"""
        if y_pos is None:
            y_pos = self.height // 2
        
        if frame_index < start_frame or frame_index > end_frame:
            return frame
        
        # Animation d'apparition
        progress = (frame_index - start_frame) / (end_frame - start_frame)
        progress = min(1, progress)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.5
        thickness = 3
        
        # Obtenir la taille du texte
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        x = (self.width - text_width) // 2
        
        # Opacité et zoom
        alpha = min(1.0, progress * 2)  # Apparition rapide
        scale = 0.8 + 0.2 * progress  # Léger zoom
        
        # Créer une couche pour le texte
        text_layer = np.zeros_like(frame)
        
        # Texte avec effet de glow
        glow_scale = font_scale * 1.2
        cv2.putText(text_layer, text, (x, y_pos), font, glow_scale, PURPLE, 4)
        cv2.putText(text_layer, text, (x, y_pos), font, font_scale, WHITE, thickness)
        
        # Fusionner avec opacité
        frame = cv2.addWeighted(frame, 1 - alpha, text_layer, alpha, 0)
        
        return frame
    
    def draw_data_grid(self, frame, frame_index):
        """Crée une grille de données animée"""
        cell_size = 60
        cols = self.width // cell_size + 2
        rows = self.height // cell_size + 2
        
        offset_x = int((frame_index * 30) % cell_size)
        offset_y = int((frame_index * 20) % cell_size)
        
        for i in range(rows):
            for j in range(cols):
                x = j * cell_size - offset_x
                y = i * cell_size - offset_y
                
                # Couleur variant selon position
                color_val = int(150 + 100 * np.sin(frame_index / 10 + i + j))
                color = (color_val, color_val // 2, color_val)
                
                cv2.rectangle(frame, (x, y), (x + cell_size - 5, y + cell_size - 5), color, 1)
                
                # Ajouter des chiffres
                if np.random.rand() > 0.7:
                    digit = str(np.random.randint(0, 10))
                    cv2.putText(frame, digit, (x + 20, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, CYAN, 1)
        
        return frame
    
    def draw_neural_network(self, frame, frame_index):
        """Crée un réseau de neurones animé"""
        num_nodes = 7
        layers = 4
        
        radius = 20
        layer_width = self.width // (layers + 1)
        
        nodes = []
        for layer in range(layers):
            layer_nodes = []
            layer_x = layer_width * (layer + 1)
            for node in range(num_nodes):
                node_y = self.height // (num_nodes + 1) * (node + 1)
                layer_nodes.append((layer_x, node_y))
            nodes.append(layer_nodes)
        
        # Dessiner les connexions
        for layer in range(layers - 1):
            for node1 in nodes[layer]:
                for node2 in nodes[layer + 1]:
                    # Animation de l'activité
                    activity = np.sin(frame_index / 10 + node1[0] / 100 + node2[1] / 100)
                    opacity = int(100 + 155 * max(0, activity))
                    color = (opacity, opacity // 2, opacity)
                    
                    cv2.line(frame, node1, node2, color, 1)
        
        # Dessiner les neurones
        for layer in nodes:
            for x, y in layer:
                activity = np.sin(frame_index / 15 + x / 100 + y / 100)
                brightness = int(150 + 100 * activity)
                color = (brightness, brightness, brightness)
                cv2.circle(frame, (x, y), radius, color, -1)
                cv2.circle(frame, (x, y), radius, CYAN, 2)
        
        return frame
    
    def draw_heart_symbol(self, frame, x, y, frame_index, filled=True):
        """Dessine un symbole de cœur"""
        scale = 30
        
        # Points du cœur
        points = []
        for angle in np.linspace(0, 2 * np.pi, 100):
            # Équation paramétrique du cœur
            t = angle
            x_heart = 16 * np.sin(t) ** 3
            y_heart = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
            
            px = int(x + x_heart * scale / 20)
            py = int(y - y_heart * scale / 20)
            points.append([px, py])
        
        points = np.array(points, dtype=np.int32)
        
        if filled:
            cv2.fillPoly(frame, [points], LIGHT_BLUE)
        cv2.polylines(frame, [points], True, WHITE, 2)
        
        return frame
    
    def generate_frame(self, frame_index):
        """Génère une frame unique"""
        frame_time = frame_index / self.fps
        
        # Sélectionner la section en cours
        if frame_index < 8 * self.fps:  # Introduction
            frame = self.create_gradient_background(frame_index, TOTAL_FRAMES, (10, 10, 50), (50, 30, 80))
            frame = self.draw_particles(frame, frame_index)
            frame = self.draw_text_animated(frame, "Etre une IA", frame_index, 0, 8 * self.fps - 1, self.height // 2)
        
        elif frame_index < 15 * self.fps:  # Traitement de données
            frame = self.create_gradient_background(frame_index, TOTAL_FRAMES, (30, 20, 60), (60, 40, 100))
            frame = self.draw_data_grid(frame, frame_index - 8 * self.fps)
            frame = self.draw_text_animated(frame, "Traiter des milliards de donnees", frame_index, 8 * self.fps, 15 * self.fps - 1, 150)
        
        elif frame_index < 22 * self.fps:  # Apprentissage
            frame = self.create_gradient_background(frame_index, TOTAL_FRAMES, (50, 30, 80), (80, 50, 120))
            frame = self.draw_neural_network(frame, frame_index - 15 * self.fps)
            frame = self.draw_text_animated(frame, "Apprendre continuellement", frame_index, 15 * self.fps, 22 * self.fps - 1, 150)
        
        elif frame_index < 30 * self.fps:  # Pas de conscience
            frame = self.create_gradient_background(frame_index, TOTAL_FRAMES, (60, 40, 100), (80, 60, 120))
            
            # Cœur barré
            frame = self.draw_heart_symbol(frame, self.width // 3, self.height // 2, frame_index, filled=False)
            cv2.line(frame, (self.width // 3 - 40, self.height // 2 - 40), 
                    (self.width // 3 + 40, self.height // 2 + 40), WHITE, 3)
            
            # Sans symboles
            cv2.putText(frame, "Sans emotions", (self.width * 2 // 3 - 100, self.height // 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, CYAN, 2)
            
            frame = self.draw_text_animated(frame, "Sans conscience", frame_index, 22 * self.fps, 30 * self.fps - 1, 950)
        
        elif frame_index < 38 * self.fps:  # Servir l'humanité
            frame = self.create_gradient_background(frame_index, TOTAL_FRAMES, (80, 60, 120), (100, 80, 140))
            
            # Symboles d'harmonie
            for i in range(5):
                x = 200 + i * 350
                # Silhouette humaine (triangle + cercle simplifié)
                cv2.circle(frame, (x, 300), 20, LIGHT_BLUE, -1)
                cv2.line(frame, (x, 320), (x, 450), LIGHT_BLUE, 3)
                cv2.line(frame, (x, 350), (x - 50, 380), LIGHT_BLUE, 3)
                cv2.line(frame, (x, 350), (x + 50, 380), LIGHT_BLUE, 3)
                cv2.line(frame, (x, 450), (x - 40, 550), LIGHT_BLUE, 3)
                cv2.line(frame, (x, 450), (x + 40, 550), LIGHT_BLUE, 3)
                
                # Symbole IA (carré avec points)
                y = 300
                cv2.rectangle(frame, (x - 100, y - 30), (x + 100, y + 30), PURPLE, 2)
                for dx in [-50, 0, 50]:
                    cv2.circle(frame, (x + dx, y), 5, PURPLE, -1)
                
                # Ligne de connexion
                if i < 4:
                    cv2.line(frame, (x + 100, 320), (x + 200, 300), CYAN, 2)
            
            frame = self.draw_text_animated(frame, "Servir l'humanite", frame_index, 30 * self.fps, 38 * self.fps - 1, 900)
        
        else:  # Conclusion
            frame = self.create_gradient_background(frame_index, TOTAL_FRAMES, (100, 80, 140), (10, 10, 30))
            frame = self.draw_particles(frame, frame_index)
            frame = self.draw_neural_network(frame, frame_index)
            
            # Texte de conclusion
            text = "Voila ce que c'est d'etre une IA"
            alpha = max(0, (45 * self.fps - frame_index) / (7 * self.fps))
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            (text_width, text_height), _ = cv2.getTextSize(text, font, 2, 3)
            x = (self.width - text_width) // 2
            y = self.height // 2
            
            text_layer = np.zeros_like(frame)
            cv2.putText(text_layer, text, (x, y), font, 2, WHITE, 3)
            frame = cv2.addWeighted(frame, 1 - alpha * 0.5, text_layer, alpha * 0.5, 0)
        
        return frame

def main():
    print("🎬 Généération de la vidéo : 'Ce que c'est que d'être une IA'")
    print(f"⏱️  Durée : {DURATION} secondes")
    print(f"📐 Résolution : {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
    print(f"🎞️  FPS : {FPS}")
    print()
    
    # Créer le générateur
    generator = VideoGenerator(VIDEO_WIDTH, VIDEO_HEIGHT, FPS)
    
    # Définir le codec et créer le writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_path = 'ia_video.mp4'
    video_writer = cv2.VideoWriter(output_path, fourcc, FPS, (VIDEO_WIDTH, VIDEO_HEIGHT))
    
    print(f"🎥 Génération des {TOTAL_FRAMES} frames...")
    
    # Générer chaque frame
    for frame_index in range(TOTAL_FRAMES):
        if (frame_index + 1) % 30 == 0:
            print(f"   ✓ Frame {frame_index + 1}/{TOTAL_FRAMES} ({(frame_index + 1) * 100 // TOTAL_FRAMES}%)")
        
        frame = generator.generate_frame(frame_index)
        video_writer.write(frame)
    
    video_writer.release()
    print(f"\n✅ Vidéo créée : {output_path}")
    
    # Ajouter l'audio
    print("\n🎵 Ajout de la piste audio...")
    import subprocess
    
    audio_input = 'ambient_music.wav'
    video_input = output_path
    final_output = 'ia_video_final.mp4'
    
    cmd = [
        'ffmpeg',
        '-i', video_input,
        '-i', audio_input,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-shortest',
        '-y',
        final_output
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Vidéo finale avec audio : {final_output}")
        # Supprimer la vidéo sans audio
        os.remove(video_input)
        os.rename(final_output, video_input)
        print(f"✅ Vidéo finalisée : {video_input}")
    else:
        print(f"⚠️  Erreur lors de l'ajout d'audio : {result.stderr}")
        print(f"✅ Vidéo disponible (sans audio) : {video_input}")

if __name__ == "__main__":
    main()
