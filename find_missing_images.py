#!/usr/bin/env python3
import os
import glob

# Get all existing images
existing = set()
for img in glob.glob('images/image_*.jpg') + glob.glob('images/image_*.png'):
    existing.add(os.path.basename(img))

print(f"Found {len(existing)} existing images")

# Check for image_040 and image_041
missing = []
for i in range(40, 42):
    for ext in ['jpg', 'png']:
        filename = f'image_{i:03d}.{ext}'
        if filename not in existing:
            missing.append(filename)

print(f"Missing images: {missing}")

# Try to extract from PPT if they exist
if missing:
    print("\nAttempting to find missing images in PPT...")
    with open("DOSSIER FINCA LA PRIORITA 2022.ppt", 'rb') as f:
        content = f.read()
    
    # Look for additional JPEGs/PNGs that might be image_040 or image_041
    # This is a quick check - the full extraction script should find them
    print("Run extract_all_images.py for complete extraction")



