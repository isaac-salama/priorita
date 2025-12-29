#!/bin/bash
# Script para verificar el progreso del procesamiento

total=$(wc -l < list_images.txt)
processed=$(ls images_ruralidays_processed/ 2>/dev/null | wc -l | xargs)
pending=$((total - processed))

echo "════════════════════════════════════════════════"
echo "  PROGRESO DE PROCESAMIENTO DE IMÁGENES"
echo "════════════════════════════════════════════════"
echo ""
echo "Total de imágenes:        $total"
echo "Procesadas:               $processed"
echo "Pendientes:               $pending"
echo ""
echo "Progreso:                 $(( processed * 100 / total ))%"
echo ""

if [ $processed -gt 0 ]; then
    echo "Últimas imágenes procesadas:"
    ls -t images_ruralidays_processed/ | head -5 | while read img; do
        echo "  ✓ $img"
    done
    echo ""
fi

if [ $pending -gt 0 ]; then
    echo "Próximas imágenes a procesar:"
    comm -23 <(sort list_images.txt | sed 's|images_ruralidays/||') <(ls images_ruralidays_processed/ 2>/dev/null | sort) | head -5 | while read img; do
        echo "  ○ $img"
    done
fi

echo ""


