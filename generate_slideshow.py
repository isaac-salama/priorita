#!/usr/bin/env python3
import os
from pathlib import Path

def generate_slideshow_with_images():
    """Generate HTML slideshow with all extracted images"""
    
    images_dir = Path("images")
    if not images_dir.exists():
        print("Images directory not found!")
        return
    
    # Get all image files
    image_files = sorted([f for f in os.listdir(images_dir) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))])
    
    print(f"Found {len(image_files)} images")
    
    # Generate image slides HTML
    image_slides = ""
    for img_file in image_files:
        img_path = f"images/{img_file}"
        image_slides += f'''            <section>
                <img src="{img_path}" alt="{img_file}" style="max-width: 100%; max-height: 80vh; object-fit: contain;">
            </section>
'''
    
    html_content = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Finca La Priorita - Dossier 2022</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.3.1/dist/reveal.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.3.1/dist/theme/white.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f5f5;
        }}

        .reveal {{
            width: 100%;
            height: 100vh;
        }}

        .reveal .slides section {{
            text-align: center;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .reveal h1 {{
            color: #2c5530;
            font-size: 3em;
            margin-bottom: 0.5em;
            border-bottom: 3px solid #4a7c59;
            padding-bottom: 0.3em;
        }}

        .reveal h2 {{
            color: #2c5530;
            font-size: 2.5em;
            margin-bottom: 0.8em;
        }}

        .reveal img {{
            max-width: 100%;
            max-height: 85vh;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}

        .reveal .progress {{
            color: #4a7c59;
        }}

        .reveal .controls {{
            color: #4a7c59;
        }}

        .title-slide {{
            background: linear-gradient(135deg, #2c5530 0%, #4a7c59 100%);
            color: white;
        }}

        .title-slide h1, .title-slide h2 {{
            color: white;
            border-bottom: 3px solid rgba(255,255,255,0.3);
        }}

        @media (max-width: 768px) {{
            .reveal .slides section {{
                padding: 10px;
            }}

            .reveal h1 {{
                font-size: 2em;
            }}

            .reveal h2 {{
                font-size: 1.8em;
            }}
        }}
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
            <!-- Title Slide -->
            <section class="title-slide">
                <h1>Finca La Priorita</h1>
                <h2>Dossier 2022</h2>
                <p style="margin-top: 2em; font-size: 1.5em;">
                    Galería de Imágenes
                </p>
                <p style="font-size: 1em; margin-top: 2em; opacity: 0.9;">
                    {len(image_files)} imágenes • Use las flechas para navegar
                </p>
            </section>

{image_slides}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.3.1/dist/reveal.js"></script>
    <script>
        Reveal.initialize({{
            hash: true,
            controls: true,
            progress: true,
            center: true,
            touch: true,
            transition: 'slide',
            backgroundTransition: 'fade'
        }});
    </script>
</body>
</html>'''
    
    output_file = "dossier.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated {output_file} with {len(image_files)} image slides")

if __name__ == "__main__":
    generate_slideshow_with_images()

