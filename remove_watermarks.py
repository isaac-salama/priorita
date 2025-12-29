#!/usr/bin/env python3
"""
Watermark removal script using OpenCV inpainting
This script attempts to remove watermarks while preserving image quality.
"""
import cv2
import numpy as np
from pathlib import Path
import os
from PIL import Image
import argparse

def detect_watermark_region(img, threshold=200, corner_only=True):
    """
    Detect watermark regions (typically white/semi-transparent areas)
    Watermarks are usually in corners or edges
    Returns a binary mask where watermarks are detected
    """
    h, w = img.shape[:2]
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Method 1: Detect very bright areas (white watermarks)
    _, mask1 = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    
    # Method 2: Detect semi-transparent watermarks
    # Look for areas with high brightness but not pure white
    gray_float = gray.astype(np.float32)
    bright_areas = (gray_float > 180) & (gray_float < 250)
    mask2 = bright_areas.astype(np.uint8) * 255
    
    # Method 3: Edge detection for watermark boundaries
    edges = cv2.Canny(gray, 50, 150)
    
    # Combine masks
    mask = cv2.bitwise_or(mask1, mask2)
    mask = cv2.bitwise_or(mask, edges)
    
    # Focus on corners/edges if corner_only is True (typical watermark locations)
    if corner_only:
        corner_mask = np.zeros((h, w), dtype=np.uint8)
        # Bottom-right corner (most common watermark location)
        corner_mask[int(h*0.7):, int(w*0.7):] = 255
        # Bottom-left corner
        corner_mask[int(h*0.7):, :int(w*0.3)] = 255
        # Top-right corner
        corner_mask[:int(h*0.3), int(w*0.7):] = 255
        # Top-left corner
        corner_mask[:int(h*0.3), :int(w*0.3)] = 255
        
        mask = cv2.bitwise_and(mask, corner_mask)
    
    # Clean up small noise
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # Dilate slightly to ensure full coverage
    mask = cv2.dilate(mask, kernel, iterations=1)
    
    return mask

def remove_watermark_inpaint(img, mask, method='ns', inpaint_radius=5):
    """
    Remove watermark using inpainting
    Methods: 'telea' (fast) or 'ns' (Navier-Stokes, slower but better quality)
    inpaint_radius: Radius of a circular neighborhood of each point inpainted
    """
    if method == 'telea':
        result = cv2.inpaint(img, mask, inpaint_radius, cv2.INPAINT_TELEA)
    else:
        # Navier-Stokes typically gives better results
        result = cv2.inpaint(img, mask, inpaint_radius, cv2.INPAINT_NS)
    
    return result

def remove_watermark_manual_mask(img_path, output_path, mask_coords=None):
    """
    Remove watermark with manual mask coordinates
    mask_coords: list of (x, y, width, height) tuples for watermark regions
    """
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"Error loading {img_path}")
        return False
    
    h, w = img.shape[:2]
    
    # Create mask
    mask = np.zeros((h, w), dtype=np.uint8)
    
    if mask_coords:
        # Use provided coordinates
        for x, y, width, height in mask_coords:
            mask[y:y+height, x:x+width] = 255
    else:
        # Auto-detect watermark (focus on corners)
        mask = detect_watermark_region(img, corner_only=True)
    
    # Check if mask has any white pixels
    if cv2.countNonZero(mask) == 0:
        print(f"  No watermark detected, copying original")
        import shutil
        shutil.copy2(img_path, output_path)
        return True
    
    # Inpaint with Navier-Stokes for best quality
    result = remove_watermark_inpaint(img, mask, method='ns', inpaint_radius=5)
    
    # Save with high quality
    cv2.imwrite(str(output_path), result, [cv2.IMWRITE_JPEG_QUALITY, 98])
    return True

def process_folder(input_folder, output_folder, method='auto'):
    """
    Process all images in a folder
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
    images = [f for f in input_folder.iterdir() 
              if f.suffix in image_extensions]
    
    print(f"Found {len(images)} images to process")
    
    processed = 0
    for img_path in images:
        output_file = output_path / f"{img_path.stem}_no_watermark{img_path.suffix}"
        
        print(f"Processing: {img_path.name}...")
        
        if remove_watermark_manual_mask(img_path, output_file):
            processed += 1
            print(f"  ✓ Saved to {output_file}")
        else:
            print(f"  ✗ Failed")
    
    print(f"\n✓ Processed {processed}/{len(images)} images")
    return processed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Remove watermarks from images')
    parser.add_argument('--input', '-i', default='images_ruralidays', 
                       help='Input folder')
    parser.add_argument('--output', '-o', default='images_ruralidays_clean',
                       help='Output folder')
    parser.add_argument('--method', '-m', choices=['auto', 'telea', 'ns'], 
                       default='auto', help='Inpainting method')
    
    args = parser.parse_args()
    
    # Check if OpenCV is available
    try:
        import cv2
    except ImportError:
        print("OpenCV not found. Installing...")
        os.system("pip3 install opencv-python pillow numpy --quiet")
        import cv2
    
    input_folder = Path(args.input)
    if not input_folder.exists():
        print(f"Error: Folder {input_folder} does not exist")
        exit(1)
    
    process_folder(input_folder, args.output, args.method)

