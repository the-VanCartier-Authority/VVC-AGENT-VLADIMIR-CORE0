#!/bin/bash

# ==============================================================================
# VVC EDGE - PIPELINE DE DESPLIEGUE AUTOMATIZADO (VLADIMIR CORE 0)
# ==============================================================================
# Este script empaqueta la arquitectura modular y la envía a Kaggle de forma segura.

COMPETITION_NAME="pokemon-tcg-ai-battle"
SUBMISSION_DIR="./submission"
ZIP_NAME="submission.tar.gz"

echo -e "\n[+] Iniciando auditoría y empaquetado para VVC-AGENT-VLADIMIR-CORE0..."

# 1. Validar la existencia de los componentes mínimos obligatorios
if [ ! -f "$SUBMISSION_DIR/main.py" ] || [ ! -f "$SUBMISSION_DIR/deck.csv" ]; then
    echo -e "[-] ERROR CRÍTICO: No se encuentra main.py o deck.csv en $SUBMISSION_DIR."
    exit 1
fi

# 2. Limpiar empaquetados anteriores si existen
if [ -f "$ZIP_NAME" ]; then
    rm "$ZIP_NAME"
fi

# 3. Moverse al directorio y comprimir con la sintaxis exacta exigida por el simulador
cd "$SUBMISSION_DIR" || exit
tar -czvf "../$ZIP_NAME" *
cd ..

echo -e "[+] Paquete $ZIP_NAME creado exitosamente."

# 4. Validar si la CLI de Kaggle está configurada antes de intentar el envío
if ! command -v kaggle &> /dev/null; then
    echo -e "[-] ALERTA: La CLI de Kaggle no está instalada localmente."
    echo -e "[*] Entrega el archivo '$ZIP_NAME' a Manus o súbelo manualmente."
    exit 0
fi

# 5. Envío automatizado oficial vía API oficial (Seguro y Zero-Cloud)
echo -e "[+] Transmitiendo solución a Kaggle mediante API Oficial CLI..."
kaggle competitions submit -c "$COMPETITION_NAME" -f "$ZIP_NAME" -m "VVC Core 0 - Audit Automated Step"

echo -e "[+] Despliegue finalizado. Monitorea los logs en sys.stderr desde la plataforma.\n"
