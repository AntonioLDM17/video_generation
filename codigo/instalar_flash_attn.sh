#!/bin/bash
# Script para instalar flash-attn dentro del contenedor
# Úsalo si flash-attn no se instaló correctamente durante el build

set -e

echo "=========================================="
echo "Instalando flash-attn"
echo "=========================================="
echo ""

# Verificar que estamos en un contenedor con CUDA
if ! command -v nvcc &> /dev/null; then
    echo "⚠ Advertencia: nvcc no encontrado."
    echo "  Intentando instalar CUDA development tools..."
    apt-get update && apt-get install -y cuda-cudart-dev-12-1 cuda-nvcc-12-1 || true
fi

# Verificar PyTorch
python3 -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')" || {
    echo "✗ Error: PyTorch no está disponible"
    exit 1
}

echo ""
echo "Instalando dependencias..."
pip install --upgrade pip setuptools wheel packaging ninja

echo ""
echo "Instalando flash-attn..."
echo "⚠ Esto puede tomar varios minutos..."

# Intentar instalar flash-attn
if pip install flash-attn --no-build-isolation; then
    echo ""
    echo "✓ flash-attn instalado exitosamente"
    echo ""
    echo "Verificando instalación..."
    python3 -c "import flash_attn; print('✓ flash_attn importado correctamente')" && \
        echo "✓ Instalación verificada correctamente"
else
    echo ""
    echo "✗ Error al instalar flash-attn"
    echo ""
    echo "Opciones alternativas:"
    echo "1. Instalar desde wheel precompilado (si está disponible):"
    echo "   pip install flash-attn --no-build-isolation --find-links https://github.com/Dao-AILab/flash-attention/releases"
    echo ""
    echo "2. Compilar manualmente (requiere más tiempo):"
    echo "   MAX_JOBS=4 pip install flash-attn --no-build-isolation"
    echo ""
    echo "3. Usar una imagen Docker con flash-attn preinstalado"
    exit 1
fi

