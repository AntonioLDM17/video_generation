#!/usr/bin/env python3
"""
Script de ejemplo para generar un video de prueba con Wan 2.1.

Este script genera un video simple para verificar que el entorno
está correctamente configurado.

Uso:
    python codigo/ejemplo_generacion.py
"""

import sys
from pathlib import Path

# Agregar el directorio codigo al path
sys.path.insert(0, str(Path(__file__).parent))

from generar_video import generar_video_t2v, verificar_entorno


def main():
    """Genera un video de ejemplo."""
    print("="*60)
    print("EJEMPLO DE GENERACIÓN DE VIDEO")
    print("="*60)
    print()
    
    # Verificar entorno
    if not verificar_entorno():
        print("\n✗ El entorno no está correctamente configurado.")
        print("  Por favor, verifica:")
        print("  1. Que el repositorio Wan2.1 esté clonado")
        print("  2. Que los modelos estén descargados en /app/models")
        print("  3. Que PyTorch y CUDA estén funcionando")
        sys.exit(1)
    
    # Configuración del ejemplo
    prompt = "A blue soda can on a wooden table, soft lighting, cinematic"
    salida = "resultados/ejemplo_video.mp4"
    ckpt_dir = "/app/models/Wan2.1-T2V-14B"
    
    # Verificar que el modelo existe
    if not Path(ckpt_dir).exists():
        print(f"\n⚠ Modelo no encontrado en: {ckpt_dir}")
        print("\nPor favor, descarga el modelo primero:")
        print("  huggingface-cli download Wan-AI/Wan2.1-T2V-1.3B --local-dir /app/models/Wan2.1-T2V-1.3B")
        print("\nO usando Python:")
        print("  from huggingface_hub import snapshot_download")
        print("  snapshot_download(repo_id='Wan-AI/Wan2.1-T2V-1.3B', local_dir='/app/models/Wan2.1-T2V-1.3B')")
        sys.exit(1)
    
    print(f"\nGenerando video de ejemplo...")
    print(f"  Prompt: {prompt}")
    print(f"  Modelo: {ckpt_dir}")
    print(f"  Salida: {salida}")
    print("\n⚠ Nota: Esto puede tomar 15-30 minutos dependiendo de tu GPU")
    print()
    
    # Generar video
    exito = generar_video_t2v(
        prompt=prompt,
        salida=salida,
        ckpt_dir=ckpt_dir,
        resolucion="832x480",
        offload_model=False,
        t5_cpu=False,
        sample_guide_scale=7.5
    )
    
    if exito:
        print("\n" + "="*60)
        print("✓ VIDEO GENERADO EXITOSAMENTE")
        print("="*60)
        print(f"\nEl video se encuentra en: {salida}")
        print("(En el host: /home/202111068/workdata/results/ejemplo_video.mp4)")
    else:
        print("\n" + "="*60)
        print("✗ ERROR AL GENERAR VIDEO")
        print("="*60)
        print("\nPor favor, verifica:")
        print("  1. Que el modelo esté correctamente descargado")
        print("  2. Que tengas suficiente memoria GPU")
        print("  3. Los logs de error arriba para más detalles")
        sys.exit(1)


if __name__ == "__main__":
    main()

