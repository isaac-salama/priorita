#!/usr/bin/env python3
import os
import struct
from pathlib import Path

def extract_all_images_from_ppt(ppt_path, output_dir="images_all"):
    """Extract ALL images from old .ppt format using multiple methods"""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Reading {ppt_path}...")
    
    with open(ppt_path, 'rb') as f:
        content = bytearray(f.read())
    
    file_size = len(content)
    print(f"File size: {file_size:,} bytes")
    
    images_found = []
    
    # Method 1: Find JPEG images (SOI + data + EOI)
    print("\n[Method 1] Searching for JPEG images...")
    offset = 0
    jpeg_count = 0
    while offset < file_size - 4:
        # Look for JPEG Start of Image marker
        soi_pos = content.find(b'\xff\xd8\xff', offset)
        if soi_pos == -1:
            break
        
        # Find JPEG End of Image marker
        eoi_pos = content.find(b'\xff\xd9', soi_pos + 2)
        if eoi_pos != -1:
            eoi_pos += 2
            img_data = bytes(content[soi_pos:eoi_pos])
            
            # Validate JPEG: should start with FFD8 and end with FFD9
            if len(img_data) > 1000:  # Minimum size
                # Check if it's a valid JPEG by looking for JFIF or EXIF markers
                if b'JFIF' in img_data[:100] or b'Exif' in img_data[:100] or b'\xff\xe0' in img_data[:20] or b'\xff\xe1' in img_data[:20]:
                    images_found.append(('jpg', soi_pos, img_data))
                    jpeg_count += 1
            offset = eoi_pos
        else:
            offset = soi_pos + 1
    
    print(f"  Found {jpeg_count} JPEG images")
    
    # Method 2: Find PNG images
    print("\n[Method 2] Searching for PNG images...")
    offset = 0
    png_count = 0
    while offset < file_size - 8:
        # PNG signature: 89 50 4E 47 0D 0A 1A 0A
        png_start = content.find(b'\x89PNG\r\n\x1a\n', offset)
        if png_start == -1:
            break
        
        # Find IEND chunk (end of PNG)
        iend_pos = content.find(b'IEND\xaeB`\x82', png_start)
        if iend_pos != -1:
            iend_pos += 8
            img_data = bytes(content[png_start:iend_pos])
            
            if len(img_data) > 100:  # Minimum size
                images_found.append(('png', png_start, img_data))
                png_count += 1
            offset = iend_pos
        else:
            # Try to find end by looking for IEND without checksum
            iend_alt = content.find(b'IEND', png_start)
            if iend_alt != -1 and iend_alt < png_start + 50000000:  # Max 50MB PNG
                iend_alt += 12  # IEND + length + type + data + checksum
                img_data = bytes(content[png_start:min(iend_alt, file_size)])
                if len(img_data) > 100:
                    images_found.append(('png', png_start, img_data))
                    png_count += 1
            offset = png_start + 1
        if offset >= file_size:
            break
    
    print(f"  Found {png_count} PNG images")
    
    # Method 3: Find embedded OLE objects that might contain images
    print("\n[Method 3] Searching for embedded image objects...")
    offset = 0
    ole_count = 0
    
    # Look for common OLE stream patterns that might contain images
    while offset < file_size - 100:
        # Look for patterns that might indicate embedded images
        # PowerPoint often embeds images in OLE streams
        
        # Check for DIB (Device Independent Bitmap) headers
        dib_patterns = [
            b'BITMAPINFOHEADER',
            b'BITMAPCOREHEADER',
        ]
        
        for pattern in dib_patterns:
            pos = content.find(pattern, offset)
            if pos != -1:
                # Try to extract bitmap data
                # Bitmap files start with 'BM'
                bm_pos = content.find(b'BM', max(0, pos - 100), pos + 1000)
                if bm_pos != -1:
                    # Read bitmap size from header (offset 2-5)
                    try:
                        bmp_size = struct.unpack('<I', content[bm_pos+2:bm_pos+6])[0]
                        if 100 < bmp_size < 50000000:  # Reasonable size
                            end_pos = bm_pos + bmp_size
                            if end_pos < file_size:
                                img_data = bytes(content[bm_pos:end_pos])
                                images_found.append(('bmp', bm_pos, img_data))
                                ole_count += 1
                    except:
                        pass
                offset = pos + len(pattern)
                break
        else:
            offset += 1000
    
    print(f"  Found {ole_count} embedded image objects")
    
    # Method 4: Look for GIF images
    print("\n[Method 4] Searching for GIF images...")
    offset = 0
    gif_count = 0
    while offset < file_size - 10:
        gif_start = content.find(b'GIF89a', offset)
        if gif_start == -1:
            gif_start = content.find(b'GIF87a', offset)
            if gif_start == -1:
                break
        
        # GIF ends with 0x3B (semicolon)
        gif_end = content.find(b'\x00;', gif_start)
        if gif_end == -1:
            # Try to find reasonable end
            gif_end = min(gif_start + 10000000, file_size)  # Max 10MB
        
        img_data = bytes(content[gif_start:gif_end])
        if len(img_data) > 100:
            images_found.append(('gif', gif_start, img_data))
            gif_count += 1
        offset = gif_end if gif_end < file_size else gif_start + 1
        if offset >= file_size:
            break
    
    print(f"  Found {gif_count} GIF images")
    
    # Method 5: Look for TIFF images
    print("\n[Method 5] Searching for TIFF images...")
    offset = 0
    tiff_count = 0
    while offset < file_size - 10:
        # TIFF can start with II (Intel) or MM (Motorola) byte order
        tiff_start = content.find(b'II*\x00', offset)  # Intel byte order
        if tiff_start == -1:
            tiff_start = content.find(b'MM\x00*', offset)  # Motorola byte order
            if tiff_start == -1:
                break
        
        # TIFF is complex, try to find reasonable end
        # Look for next image signature or end of reasonable size
        tiff_end = min(tiff_start + 50000000, file_size)  # Max 50MB
        
        # Try to find actual end by looking for common patterns
        for check_offset in range(tiff_start + 1000, min(tiff_start + 10000000, file_size), 1000):
            # Check if we hit another image signature
            if (content[check_offset:check_offset+2] == b'\xff\xd8' or  # JPEG
                content[check_offset:check_offset+8] == b'\x89PNG\r\n\x1a\n'):  # PNG
                tiff_end = check_offset
                break
        
        img_data = bytes(content[tiff_start:tiff_end])
        if len(img_data) > 1000:
            images_found.append(('tiff', tiff_start, img_data))
            tiff_count += 1
        offset = tiff_end
        if offset >= file_size:
            break
    
    print(f"  Found {tiff_count} TIFF images")
    
    # Remove duplicates based on position (within 100 bytes tolerance)
    print("\n[Cleaning] Removing duplicates...")
    unique_images = []
    seen_ranges = []
    
    for img_type, pos, data in images_found:
        is_duplicate = False
        for seen_pos, seen_data in seen_ranges:
            # Check if this image overlaps with a previously seen one
            if abs(pos - seen_pos) < 100 or (pos >= seen_pos and pos < seen_pos + len(seen_data)):
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_images.append((img_type, pos, data))
            seen_ranges.append((pos, data))
    
    # Sort by position
    unique_images.sort(key=lambda x: x[1])
    
    print(f"\nTotal unique images found: {len(unique_images)}")
    
    # Save images
    print("\n[Saving] Extracting images...")
    saved_count = 0
    failed_count = 0
    
    for i, (img_type, pos, img_data) in enumerate(unique_images, 1):
        filename = f"image_{i:03d}.{img_type}"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'wb') as img_file:
                img_file.write(img_data)
            
            # Verify file was written and has reasonable size
            if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
                print(f"  ✓ Saved: {filename} ({len(img_data):,} bytes) at offset {pos:,}")
                saved_count += 1
            else:
                if os.path.exists(filepath):
                    os.remove(filepath)
                failed_count += 1
                print(f"  ✗ Failed: {filename} (too small or invalid)")
        except Exception as e:
            print(f"  ✗ Error saving {filename}: {e}")
            failed_count += 1
    
    print(f"\n{'='*60}")
    print(f"Extraction complete!")
    print(f"  Successfully saved: {saved_count} images")
    print(f"  Failed: {failed_count} images")
    print(f"  Output directory: {output_dir}/")
    print(f"{'='*60}")
    
    return saved_count

if __name__ == "__main__":
    ppt_file = "DOSSIER FINCA LA PRIORITA 2022.ppt"
    
    if not os.path.exists(ppt_file):
        print(f"Error: {ppt_file} not found!")
        exit(1)
    
    extract_all_images_from_ppt(ppt_file)



