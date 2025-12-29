#!/usr/bin/env python3
"""
Test script to remove watermark from a single image using OpenCV
"""
import cv2
import numpy as np
from pathlib import Path
import sys

def detect_watermark_region(img, threshold=200, corner_only=True):
    """Detect watermark regions"""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Method 1: Detect very bright areas (white watermarks)
    _, mask1 = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    
    # Method 2: Detect semi-transparent watermarks
    gray_float = gray.astype(np.float32)
    bright_areas = (gray_float > 180) & (gray_float < 250)
    mask2 = bright_areas.astype(np.uint8) * 255
    
    # Method 3: Edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Combine masks
    mask = cv2.bitwise_or(mask1, mask2)
    mask = cv2.bitwise_or(mask, edges)
    
    # Focus on corners/edges if corner_only is True
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
    mask = cv2.dilate(mask, kernel, iterations=1)
    
    return mask

def remove_watermark(img_path, output_path):
    """Remove watermark from a single image"""
    print(f"Procesando: {img_path}")
    
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"Error: No se pudo cargar la imagen {img_path}")
        return False
    
    print(f"  Tamaño original: {img.shape[1]}x{img.shape[0]}")
    
    # Detect watermark
    print("  Detectando watermark...")
    mask = detect_watermark_region(img, corner_only=True)
    
    # Check if watermark detected
    white_pixels = cv2.countNonZero(mask)
    print(f"  Píxeles detectados como watermark: {white_pixels}")
    
    if white_pixels == 0:
        print("  ⚠ No se detectó watermark, copiando imagen original")
        import shutil
        shutil.copy2(img_path, output_path)
        return True
    
    # Show mask preview (save it)
    mask_preview_path = str(output_path).replace('.jpg', '_mask.jpg')
    cv2.imwrite(mask_preview_path, mask)
    print(f"  Máscara guardada en: {mask_preview_path}")
    
    # Inpaint with Navier-Stokes (best quality)
    print("  Eliminando watermark con inpainting Navier-Stokes...")
    result = cv2.inpaint(img, mask, 5, cv2.INPAINT_NS)
    
    # Save result
    cv2.imwrite(str(output_path), result, [cv2.IMWRITE_JPEG_QUALITY, 98])
    print(f"  ✓ Imagen procesada guardada en: {output_path}")
    
    return True

if __name__ == "__main__":
    # Test with first image
    test_image = Path("images_ruralidays/ruralidays_002.jpg")
    output_image = Path("test_result.jpg")
    mask_preview = Path("test_mask.jpg")
    
    if not test_image.exists():
        print(f"Error: {test_image} no existe")
        sys.exit(1)
    
    print("=" * 50)
    print("PRUEBA DE ELIMINACIÓN DE WATERMARK CON OPENCV")
    print("=" * 50)
    print()
    
    if remove_watermark(test_image, output_image):
        print()
        print("=" * 50)
        print("✓ PROCESO COMPLETADO")
        print("=" * 50)
        print(f"Imagen original: {test_image}")
        print(f"Imagen procesada: {output_image}")
        print(f"Máscara de watermark: {test_image.stem}_mask.jpg")
        print()
        print("Abre las imágenes para comparar los resultados")
    else:
        print("✗ Error al procesar la imagen")


