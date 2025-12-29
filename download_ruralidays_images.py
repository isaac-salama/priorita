#!/usr/bin/env python3
"""
Script to download images from Ruralidays property gallery
"""
import os
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

def download_image(url, save_path):
    """Download an image from URL to save_path"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def extract_images_from_ruralidays(url):
    """Extract all images from Ruralidays property page"""
    output_dir = Path("images_ruralidays")
    output_dir.mkdir(exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Fetching {url}...")
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    html_content = response.text
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Collect all image URLs
    image_urls = set()
    
    # Method 1: Find by id="gallery-images" and all nested images
    gallery = soup.find(id="gallery-images")
    if gallery:
        print("Found gallery-images container")
        img_tags = gallery.find_all('img')
        for img in img_tags:
            for attr in ['src', 'data-src', 'data-lazy-src', 'data-original', 'data-full']:
                src = img.get(attr)
                if src:
                    image_urls.add(src)
    
    # Method 2: Search for image URLs in script tags (often stored as JSON)
    script_tags = soup.find_all('script')
    for script in script_tags:
        if script.string:
            # Look for URLs ending in .jpg, .jpeg, .png, .webp
            urls = re.findall(r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)(?:\?[^\s"\'<>]*)?', script.string, re.IGNORECASE)
            image_urls.update(urls)
            # Also look for relative paths
            rel_urls = re.findall(r'/[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)(?:\?[^\s"\'<>]*)?', script.string, re.IGNORECASE)
            image_urls.update(rel_urls)
    
    # Method 3: Find all img tags with various data attributes
    all_imgs = soup.find_all('img')
    for img in all_imgs:
        for attr in ['src', 'data-src', 'data-lazy-src', 'data-original', 'data-full', 'data-image']:
            src = img.get(attr)
            if src:
                image_urls.add(src)
    
    # Method 4: Search HTML content directly for image URLs
    html_urls = re.findall(r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)(?:\?[^\s"\'<>]*)?', html_content, re.IGNORECASE)
    image_urls.update(html_urls)
    
    # Filter out icons, logos, and small images
    filtered_urls = []
    for url in image_urls:
        url_lower = url.lower()
        # Skip obvious non-property images
        if any(skip in url_lower for skip in ['icon', 'logo', 'star', 'arrow', 'button', 'badge', 'trustpilot']):
            continue
        # Prefer larger images (look for size indicators or CDN patterns)
        if any(indicator in url_lower for indicator in ['large', 'full', 'original', 'photo', 'image', 'property', 'casa']):
            filtered_urls.append(url)
        elif '.jpg' in url_lower or '.jpeg' in url_lower or '.png' in url_lower:
            # Include if it looks like a property photo URL
            if not any(skip in url_lower for skip in ['thumb', 'small', 'mini']):
                filtered_urls.append(url)
    
    print(f"Found {len(filtered_urls)} potential property images")
    
    downloaded = 0
    for idx, src in enumerate(filtered_urls, 1):
        # Make absolute URL
        if src.startswith('//'):
            src = 'https:' + src
        elif src.startswith('/'):
            src = urljoin(url, src)
        elif not src.startswith('http'):
            src = urljoin(url, src)
        
        # Get file extension
        parsed = urlparse(src)
        path = parsed.path
        # Remove query parameters for extension detection
        path_clean = path.split('?')[0]
        ext = os.path.splitext(path_clean)[1] or '.jpg'
        
        # Clean filename
        filename = f"ruralidays_{idx:03d}{ext}"
        save_path = output_dir / filename
        
        print(f"[{idx}/{len(filtered_urls)}] Downloading: {src[:80]}...")
        if download_image(src, save_path):
            downloaded += 1
            print(f"  ✓ Saved to {save_path}")
        else:
            print(f"  ✗ Failed")
    
    print(f"\n✓ Downloaded {downloaded} images to {output_dir}/")
    return downloaded

if __name__ == "__main__":
    url = "https://www.ruralidays.com/casas-rurales/COR4327/"
    extract_images_from_ruralidays(url)

