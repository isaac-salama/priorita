#!/bin/bash
# Script para monitorear Lama Cleaner y avisar cuando esté listo

echo "Monitoreando descarga de Lama Cleaner..."
echo "Esto puede tardar 2-3 minutos..."
echo ""

check_count=0
max_checks=40  # 40 checks x 15 segundos = 10 minutos máximo

while [ $check_count -lt $max_checks ]; do
    check_count=$((check_count + 1))
    
    # Verificar progreso
    progress=$(tail -1 /tmp/lama_cleaner.log 2>/dev/null | grep -oE '[0-9]+%' | tail -1)
    if [ -n "$progress" ]; then
        echo "[$check_count] Progreso: $progress"
    else
        echo "[$check_count] Verificando..."
    fi
    
    # Verificar si el servidor está activo
    if curl -s http://localhost:8888 > /dev/null 2>&1; then
        echo ""
        echo "════════════════════════════════════════════════"
        echo "✓✓✓ LAMA CLEANER ESTÁ LISTO ✓✓✓"
        echo "════════════════════════════════════════════════"
        echo ""
        echo "Servidor activo en: http://localhost:8888"
        echo ""
        echo "Abriendo en el navegador..."
        open http://localhost:8888
        exit 0
    fi
    
    sleep 15
done

echo ""
echo "⚠ Tiempo de espera agotado. Verificando estado..."
tail -20 /tmp/lama_cleaner.log


