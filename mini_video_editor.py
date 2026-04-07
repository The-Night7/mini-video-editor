"""
Mini Video Editor (Programmatic)
To run this, you will need to install moviepy:
pip install moviepy

This script demonstrates the core concept of Non-Linear Editing (NLE).
We don't modify the original video. Instead, we define "instructions" 
(cuts, text overlays) and render a completely new file.
"""

import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips

def create_mini_edit(input_path, output_path):
    print(f"Loading original video: {input_path}")
    
    # 1. Load the source media (This does not load the whole video into RAM, 
    # it just opens a reader to fetch frames as needed).
    try:
        source_video = VideoFileClip(input_path)
    except IOError:
        print(f"Error: Could not load {input_path}. Please provide a valid video file.")
        return

    print("Executing Edit Decision List (EDL)...")

    # 2. Perform non-destructive cuts
    # Let's say we want the first 5 seconds, and then a clip from 10s to 15s.
    clip_1 = source_video.subclip(0, 5)
    clip_2 = source_video.subclip(10, 15)

    # 3. Apply an Effect / Overlay
    # Let's add a title card to the first clip.
    # (Requires ImageMagick installed on your system for TextClip)
    try:
        title_text = TextClip("My Awesome Edit", fontsize=70, color='white', font='Arial-Bold')
        # Center the text and make it last for 2 seconds
        title_text = title_text.set_pos('center').set_duration(2)
        
        # Composite the text over the first clip
        clip_1_with_text = CompositeVideoClip([clip_1, title_text])
    except Exception as e:
        print("Note: ImageMagick not found or configured, skipping text overlay.")
        clip_1_with_text = clip_1

    # 4. Assemble the timeline
    # Concatenate our processed clips back-to-back
    final_timeline = concatenate_videoclips([clip_1_with_text, clip_2])

    # 5. Render / Export
    # This is where the actual heavy lifting (decoding, compositing, encoding) happens.
    print(f"Rendering final output to {output_path}...")
    final_timeline.write_videofile(
        output_path, 
        codec="libx264",     # Standard H.264 video codec
        audio_codec="aac",   # Standard AAC audio codec
        fps=24,              # Force 24 frames per second
        preset="ultrafast"   # Encoding speed vs compression ratio
    )
    
    # Clean up resources
    source_video.close()
    final_timeline.close()
    print("Render complete!")

if __name__ == "__main__":
    # Create a dummy text file to act as a placeholder if no video exists, 
    # though this script requires a real video to function.
    sample_input = "input_sample.mp4"
    sample_output = "final_edit.mp4"
    
    if not os.path.exists(sample_input):
        print(f"Please place a video file named '{sample_input}' in this directory to run the edit.")
    else:
        create_mini_edit(sample_input, sample_output)