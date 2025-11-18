#!/usr/bin/env python3
"""
Script para descargar el tokenizer xlm-roberta-large necesario para I2V.

El tokenizer se descarga automáticamente desde Hugging Face, pero el código
de Wan2.1 espera que esté en el directorio del modelo. Este script lo descarga
y lo coloca en el lugar correcto.
"""

import sys
from pathlib import Path


def descargar_tokenizer(directorio_modelo="/app/models/Wan2.1-T2V-14B"):
    """
    Descarga el tokenizer xlm-roberta-large y lo coloca en el directorio del modelo.
    
    Args:
        directorio_modelo: Directorio donde está el modelo 14B
    """
    try:
        from transformers import AutoTokenizer
    except ImportError:
        print("✗ Error: transformers no está instalado.")
        print("  Instalando transformers...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "transformers"])
        from transformers import AutoTokenizer
    
    modelo_tokenizer = "xlm-roberta-large"
    directorio_tokenizer = Path(directorio_modelo) / modelo_tokenizer
    
    print("="*60)
    print("DESCARGANDO TOKENIZER XLM-ROBERTA-LARGE")
    print("="*60)
    print(f"  Modelo: {modelo_tokenizer}")
    print(f"  Destino: {directorio_tokenizer}")
    print(f"  (En el host: {str(directorio_tokenizer).replace('/app/models', '/home/202111068/workdata/models')})")
    print()
    
    # Verificar si ya existe
    if directorio_tokenizer.exists() and any(directorio_tokenizer.iterdir()):
        print(f"✓ El tokenizer ya existe en: {directorio_tokenizer}")
        respuesta = input("  ¿Deseas descargarlo de nuevo? (s/N): ")
        if respuesta.lower() != 's':
            return True
    
    # Crear directorio si no existe
    directorio_tokenizer.mkdir(parents=True, exist_ok=True)
    
    print("Descargando tokenizer desde Hugging Face...")
    print("⚠ Esto puede tomar unos minutos...")
    
    try:
        # Descargar el tokenizer
        tokenizer = AutoTokenizer.from_pretrained(modelo_tokenizer)
        
        # Guardar el tokenizer en el directorio del modelo
        tokenizer.save_pretrained(str(directorio_tokenizer))
        
        print(f"\n✓ Tokenizer descargado exitosamente")
        print(f"  Ubicación: {directorio_tokenizer}")
        print(f"  (En el host: {str(directorio_tokenizer).replace('/app/models', '/home/202111068/workdata/models')})")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error al descargar tokenizer: {e}")
        print("\nTroubleshooting:")
        print("1. Verifica tu conexión a internet")
        print("2. Verifica que transformers esté actualizado:")
        print("   pip install --upgrade transformers")
        print("3. Intenta descargar manualmente:")
        print(f"   python -c \"from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('{modelo_tokenizer}').save_pretrained('{directorio_tokenizer}')\"")
        return False


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Descarga el tokenizer xlm-roberta-large necesario para I2V"
    )
    parser.add_argument(
        "--directorio",
        type=str,
        default="/app/models/Wan2.1-T2V-14B",
        help="Directorio del modelo 14B (default: /app/models/Wan2.1-T2V-14B)"
    )
    
    args = parser.parse_args()
    
    exito = descargar_tokenizer(args.directorio)
    
    if exito:
        print("\n✓ Proceso completado exitosamente")
        print("\nAhora puedes usar I2V sin problemas.")
    else:
        print("\n✗ Error en el proceso de descarga")
        sys.exit(1)


if __name__ == "__main__":
    main()

