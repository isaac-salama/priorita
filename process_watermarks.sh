#!/bin/bash
# Script to process images and remove watermarks using the best available method

INPUT_DIR="images_ruralidays"
OUTPUT_DIR="images_ruralidays_clean"

echo "=== Watermark Removal Tool ==="
echo ""
echo "Choose method:"
echo "1. Lama Cleaner (Best quality, AI-powered) - Recommended"
echo "2. OpenCV Inpainting (Fast, good for simple watermarks)"
echo "3. Check watermarks first (inspect images)"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo "Installing Lama Cleaner..."
        pip3 install lama-cleaner --quiet
        echo ""
        echo "Starting Lama Cleaner web interface..."
        echo "Open http://localhost:8080 in your browser"
        echo "Press Ctrl+C to stop"
        lama-cleaner --model=lama --device=cpu --port=8080
        ;;
    2)
        echo "Using OpenCV inpainting..."
        python3 remove_watermarks.py --input "$INPUT_DIR" --output "$OUTPUT_DIR" --method ns
        ;;
    3)
        echo "Opening first few images for inspection..."
        open images_ruralidays/ruralidays_002.jpg 2>/dev/null || xdg-open images_ruralidays/ruralidays_002.jpg 2>/dev/null
        echo "Check the images to see watermark locations"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac


