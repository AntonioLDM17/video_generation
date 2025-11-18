#!/bin/bash
# Script para descargar modelos de Wan 2.1 desde Hugging Face
# Uso: ./descargar_modelo.sh [1.3B|14B|ambos]

set -e

MODELO=${1:-""}
DIR_DESTINO=${2:-"/app/models"}

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Descarga de Modelos Wan 2.1"
echo "=========================================="
echo ""

# Verificar que huggingface-cli esté instalado
if ! command -v huggingface-cli &> /dev/null; then
    echo -e "${YELLOW}⚠ huggingface-cli no encontrado. Instalando...${NC}"
    pip install -q huggingface_hub[cli]
fi

# Función para descargar un modelo
descargar() {
    local modelo=$1
    local repo_id=""
    local local_dir=""
    local descripcion=""
    
    case $modelo in
        "1.3B")
            repo_id="Wan-AI/Wan2.1-T2V-1.3B"
            local_dir="$DIR_DESTINO/Wan2.1-T2V-1.3B"
            descripcion="Modelo 1.3B (~5 GB, recomendado para GPUs con 8-12 GB VRAM)"
            ;;
        "14B")
            repo_id="Wan-AI/Wan2.1-T2V-14B"
            local_dir="$DIR_DESTINO/Wan2.1-T2V-14B"
            descripcion="Modelo 14B (~28 GB, requiere GPU con 16+ GB VRAM, necesario para I2V)"
            ;;
        *)
            echo -e "${RED}✗ Error: Modelo '$modelo' no válido${NC}"
            echo "  Modelos disponibles: 1.3B, 14B, ambos"
            return 1
            ;;
    esac
    
    # Verificar si ya existe
    if [ -d "$local_dir" ] && [ "$(ls -A $local_dir 2>/dev/null)" ]; then
        echo -e "${YELLOW}⚠ El modelo $modelo ya existe en $local_dir${NC}"
        read -p "  ¿Deseas descargarlo de nuevo? (s/N): " respuesta
        if [ "$respuesta" != "s" ] && [ "$respuesta" != "S" ]; then
            echo -e "${GREEN}✓ Usando modelo existente${NC}"
            return 0
        fi
    fi
    
    echo ""
    echo "=========================================="
    echo "Descargando modelo $modelo"
    echo "=========================================="
    echo "  Repositorio: $repo_id"
    echo "  Descripción: $descripcion"
    echo "  Destino: $local_dir"
    echo "  (En el host: ${local_dir//\/app\/models/\/home\/202111068\/workdata\/models})"
    echo ""
    echo "⚠ Esto puede tomar mucho tiempo..."
    echo ""
    
    # Crear directorio si no existe
    mkdir -p "$local_dir"
    
    # Descargar
    if huggingface-cli download "$repo_id" --local-dir "$local_dir" --local-dir-use-symlinks False; then
        echo ""
        echo -e "${GREEN}✓ Modelo $modelo descargado exitosamente${NC}"
        echo "  Ubicación: $local_dir"
        return 0
    else
        echo ""
        echo -e "${RED}✗ Error al descargar modelo $modelo${NC}"
        return 1
    fi
}

# Función para verificar modelos
verificar() {
    echo "=========================================="
    echo "Modelos Disponibles"
    echo "=========================================="
    echo ""
    
    for modelo in "1.3B" "14B"; do
        local_dir="$DIR_DESTINO/Wan2.1-T2V-$modelo"
        if [ -d "$local_dir" ] && [ "$(ls -A $local_dir 2>/dev/null)" ]; then
            tamaño=$(du -sh "$local_dir" 2>/dev/null | cut -f1)
            echo -e "${GREEN}✓ $modelo: Disponible${NC}"
            echo "  Ruta: $local_dir"
            echo "  Tamaño: $tamaño"
        else
            echo -e "${RED}✗ $modelo: No disponible${NC}"
            echo "  Ruta: $local_dir"
        fi
        echo ""
    done
}

# Procesar argumentos
case $MODELO in
    "")
        echo "Uso: $0 [1.3B|14B|ambos|verificar] [directorio_destino]"
        echo ""
        echo "Ejemplos:"
        echo "  $0 1.3B                    # Descargar modelo 1.3B"
        echo "  $0 14B                     # Descargar modelo 14B"
        echo "  $0 ambos                   # Descargar ambos modelos"
        echo "  $0 verificar               # Verificar modelos disponibles"
        echo "  $0 1.3B /ruta/personalizada # Descargar a directorio personalizado"
        exit 1
        ;;
    "verificar")
        verificar
        ;;
    "ambos")
        echo "Esto descargará ambos modelos (~33 GB total)"
        read -p "¿Deseas continuar? (s/N): " respuesta
        if [ "$respuesta" != "s" ] && [ "$respuesta" != "S" ]; then
            echo "Descarga cancelada."
            exit 0
        fi
        descargar "1.3B" && descargar "14B"
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✓ Ambos modelos descargados exitosamente${NC}"
        fi
        ;;
    "1.3B"|"14B")
        descargar "$MODELO"
        ;;
    *)
        echo -e "${RED}✗ Error: Opción '$MODELO' no válida${NC}"
        echo "  Opciones: 1.3B, 14B, ambos, verificar"
        exit 1
        ;;
esac

