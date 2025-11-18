#!/bin/bash
set -e

echo "=========================================="
echo "Wan 2.1 Video Generation - Homework Setup"
echo "=========================================="
echo ""

# Check if CUDA is available and select best GPU
if command -v nvidia-smi &> /dev/null; then
    echo "✓ NVIDIA GPU detected:"
    nvidia-smi --query-gpu=index,name,memory.total,memory.free --format=csv,noheader
    
    # Select GPU with highest available memory
    echo ""
    echo "Selecting GPU with highest available memory..."
    
    # Try using Python script first (more accurate)
    SELECTED_GPU=""
    if [ -f "/app/codigo/seleccionar_gpu.py" ]; then
        SELECTED_GPU=$(python3 /app/codigo/seleccionar_gpu.py --solo_id 2>/dev/null || echo "")
    fi
    
    # Fallback: use nvidia-smi directly if Python script didn't work
    if [ -z "$SELECTED_GPU" ]; then
        SELECTED_GPU=$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits 2>/dev/null | \
            sort -t',' -k2 -nr | head -1 | cut -d',' -f1 | tr -d ' ' || echo "")
    fi
    
    # Set CUDA_VISIBLE_DEVICES
    if [ -n "$SELECTED_GPU" ] && [ "$SELECTED_GPU" != "" ]; then
        export CUDA_VISIBLE_DEVICES=$SELECTED_GPU
        echo "✓ Selected GPU: $SELECTED_GPU (highest available memory)"
        echo "  CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
    else
        # If no GPU selected, use default (0)
        export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
        echo "✓ Using GPU: ${CUDA_VISIBLE_DEVICES} (default)"
        echo "  CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
    fi
else
    echo "⚠ Warning: nvidia-smi not found. GPU may not be available."
    export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
fi

# Check Python version
echo ""
echo "Python version:"
python3 --version

# Check if PyTorch can see CUDA (after GPU selection)
echo ""
echo "Checking PyTorch CUDA availability:"
python3 << EOF
import torch
import os
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU count: {torch.cuda.device_count()}')
    cuda_visible = os.environ.get('CUDA_VISIBLE_DEVICES', 'all')
    print(f'CUDA_VISIBLE_DEVICES: {cuda_visible}')
    if torch.cuda.device_count() > 0:
        for i in range(torch.cuda.device_count()):
            print(f'  GPU {i}: {torch.cuda.get_device_name(i)}')
            print(f'    Memory: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.2f} GB')
else:
    print('CUDA version: N/A')
    print('GPU count: 0')
EOF

# Clone Wan2.1 repository if it doesn't exist or is empty
# Note: /app/Wan2.1 is a mounted volume, so we handle it carefully
if [ ! -d "/app/Wan2.1" ] || [ -z "$(ls -A /app/Wan2.1 2>/dev/null)" ]; then
    echo ""
    echo "Cloning Wan2.1 repository..."
    cd /app
    if [ -d "/app/Wan2.1" ] && [ -z "$(ls -A /app/Wan2.1 2>/dev/null)" ]; then
        # Directory exists but is empty - clone to temp location then copy
        git clone https://github.com/Wan-Video/Wan2.1.git /app/Wan2.1-tmp 2>/dev/null && \
        cp -r /app/Wan2.1-tmp/. /app/Wan2.1/ 2>/dev/null && \
        rm -rf /app/Wan2.1-tmp || \
        echo "⚠ Warning: Could not clone repository into /app/Wan2.1. You may need to clone it manually on the host."
    else
        # Directory doesn't exist, clone normally
        git clone https://github.com/Wan-Video/Wan2.1.git || echo "⚠ Warning: Could not clone repository. You may need to clone it manually."
    fi
else
    echo ""
    echo "✓ Wan2.1 repository already exists"
fi

# Create necessary directories
mkdir -p /app/resultados
mkdir -p /app/models
mkdir -p /app/.cache/huggingface

# Note: Models are stored in /home/202111068/workdata/models on host
# Results are stored in /home/202111068/workdata/results on host

# Check if models directory has any models
if [ -z "$(ls -A /app/models)" ]; then
    echo ""
    echo "⚠ No models found in /app/models (host: /home/202111068/workdata/models)"
    echo "  You can download models using:"
    echo "    huggingface-cli download Wan-AI/Wan2.1-T2V-1.3B --local-dir /app/models/Wan2.1-T2V-1.3B"
    echo ""
    echo "  Or using Python:"
    echo "    from huggingface_hub import snapshot_download"
    echo "    snapshot_download(repo_id='Wan-AI/Wan2.1-T2V-1.3B', local_dir='/app/models/Wan2.1-T2V-1.3B')"
    echo ""
    echo "  Models will be saved to: /home/202111068/workdata/models (on host)"
else
    echo ""
    echo "✓ Models directory contains:"
    ls -lh /app/models
    echo "  (Host path: /home/202111068/workdata/models)"
fi

echo ""
echo "📁 Storage paths:"
echo "  Models: /app/models → /home/202111068/workdata/models (host)"
echo "  Results: /app/resultados → /home/202111068/workdata/results (host)"

# Display usage instructions
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "You can now use the video generation scripts:"
echo ""
echo "  # Text-to-Video (T2V)"
echo "  python codigo/generar_video.py --modo t2v \\"
echo "      --prompt 'Your prompt here' \\"
echo "      --salida resultados/video.mp4 \\"
echo "      --ckpt_dir /app/models/Wan2.1-T2V-1.3B"
echo ""
echo "  # Image-to-Video (I2V)"
echo "  python codigo/generar_video.py --modo i2v \\"
echo "      --imagen_referencia recursos/ejemplo_producto.png \\"
echo "      --prompt 'Your prompt here' \\"
echo "      --salida resultados/video.mp4 \\"
echo "      --ckpt_dir /app/models/Wan2.1-T2V-1.3B"
echo ""
echo "  # Masked Video-to-Video (MV2V)"
echo "  python codigo/generar_video_con_mascara.py \\"
echo "      --video_base video.mp4 \\"
echo "      --mascara mascara.png \\"
echo "      --prompt 'Your prompt here' \\"
echo "      --salida resultados/video_editado.mp4"
echo ""
echo "For more information, see: instrucciones/guia_del_estudiante.md"
echo ""

# Execute the command passed to the container
exec "$@"

