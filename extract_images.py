#!/usr/bin/env python3
import os
import re
import struct
from pathlib import Path

def extract_images_from_ppt(ppt_path, output_dir="images"):
    """Extract images from old .ppt format"""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Reading {ppt_path}...")
    
    with open(ppt_path, 'rb') as f:
        content = f.read()
    
    # Common image signatures
    image_signatures = {
        b'\xff\xd8\xff': 'jpg',
        b'\x89PNG\r\n\x1a\n': 'png',
        b'GIF87a': 'gif',
        b'GIF89a': 'gif',
        b'BM': 'bmp',
        b'RIFF': 'webp',  # May need more checking
    }
    
    images_found = []
    offset = 0
    
    while True:
        # Look for JPEG
        jpeg_start = content.find(b'\xff\xd8\xff', offset)
        if jpeg_start == -1:
            break
        
        # Find JPEG end
        jpeg_end = content.find(b'\xff\xd9', jpeg_start)
        if jpeg_end != -1:
            jpeg_end += 2
            img_data = content[jpeg_start:jpeg_end]
            if len(img_data) > 1000:  # Minimum size filter
                images_found.append(('jpg', jpeg_start, img_data))
            offset = jpeg_end
        else:
            offset = jpeg_start + 1
    
    # Reset and look for PNG
    offset = 0
    while True:
        png_start = content.find(b'\x89PNG\r\n\x1a\n', offset)
        if png_start == -1:
            break
        
        # PNG has IEND marker
        png_end = content.find(b'IEND\xaeB`\x82', png_start)
        if png_end != -1:
            png_end += 8
            img_data = content[png_start:png_end]
            if len(img_data) > 100:  # Minimum size filter
                images_found.append(('png', png_start, img_data))
            offset = png_end
        else:
            offset = png_start + 1
    
    # Reset and look for GIF
    offset = 0
    while True:
        gif_start = content.find(b'GIF89a', offset)
        if gif_start == -1:
            gif_start = content.find(b'GIF87a', offset)
            if gif_start == -1:
                break
        
        # Find GIF end (look for terminator)
        gif_end = content.find(b'\x00;', gif_start)
        if gif_end == -1:
            # Try to find a reasonable end
            gif_end = gif_start + 1000000  # 1MB max
            if gif_end > len(content):
                gif_end = len(content)
        
        img_data = content[gif_start:gif_end]
        if len(img_data) > 100:
            images_found.append(('gif', gif_start, img_data))
        offset = gif_end
        if offset >= len(content):
            break
    
    # Remove duplicates (same position)
    seen_positions = set()
    unique_images = []
    for img_type, pos, data in images_found:
        if pos not in seen_positions:
            seen_positions.add(pos)
            unique_images.append((img_type, pos, data))
    
    # Sort by position
    unique_images.sort(key=lambda x: x[1])
    
    print(f"Found {len(unique_images)} potential images")
    
    # Save images
    saved_count = 0
    for i, (img_type, pos, img_data) in enumerate(unique_images, 1):
        filename = f"image_{i:03d}.{img_type}"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'wb') as img_file:
                img_file.write(img_data)
            
            # Verify it's a valid image by checking file size
            if os.path.getsize(filepath) > 500:  # At least 500 bytes
                print(f"  Saved: {filename} ({len(img_data)} bytes)")
                saved_count += 1
            else:
                os.remove(filepath)
        except Exception as e:
            print(f"  Error saving {filename}: {e}")
    
    print(f"\nSuccessfully extracted {saved_count} images to '{output_dir}' directory")
    return saved_count

if __name__ == "__main__":
    ppt_file = "DOSSIER FINCA LA PRIORITA 2022.ppt"
    
    if not os.path.exists(ppt_file):
        print(f"Error: {ppt_file} not found!")
        exit(1)
    
    extract_images_from_ppt(ppt_file)

