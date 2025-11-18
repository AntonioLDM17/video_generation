#!/usr/bin/env python3
"""
Script para descargar modelos de Wan 2.1 desde Hugging Face.

Este script permite descargar los modelos necesarios para generar videos:
- Wan2.1-T2V-1.3B: Modelo pequeño (recomendado para GPUs con 8-12 GB VRAM)
- Wan2.1-T2V-14B: Modelo grande (requiere GPU con 16+ GB VRAM, necesario para I2V)

Uso:
    python descargar_modelo.py --modelo 1.3B
    python descargar_modelo.py --modelo 14B
    python descargar_modelo.py --modelo ambos
"""

import argparse
import sys
from pathlib import Path


def verificar_archivos_modelo(modelo, local_dir):
    """
    Verifica que los archivos requeridos del modelo estén presentes.
    
    Args:
        modelo: "1.3B" o "14B"
        local_dir: Directorio del modelo
    
    Returns:
        True si todos los archivos están presentes, False en caso contrario
    """
    local_path = Path(local_dir)
    
    # Archivos requeridos según el modelo
    if modelo == "14B":
        archivos_requeridos = [
            "models_t5_umt5-xxl-enc-bf16.pth",
            "Wan2.1_VAE.pth",
            "models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth",  # CLIP para I2V
        ]
        # También verificar archivos del transformer (pueden tener diferentes nombres)
        archivos_opcionales = [
            "Wan2.1_I2V_14B.pth",
            "Wan2.1_T2V_14B.pth",
        ]
    elif modelo in ["i2v-480p", "i2v-720p"]:
        # Modelos I2V tienen archivos específicos
        archivos_requeridos = [
            "models_t5_umt5-xxl-enc-bf16.pth",
            "Wan2.1_VAE.pth",
            "models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth",  # CLIP para I2V
            "Wan2.1_I2V_14B.pth",  # Modelo principal de I2V
        ]
        archivos_opcionales = []
    else:  # 1.3B
        archivos_requeridos = [
            "models_t5_umt5-xxl-enc-bf16.pth",
            "Wan2.1_VAE.pth",
        ]
        archivos_opcionales = [
            "Wan2.1_T2V_1.3B.pth",
        ]
    
    todos_presentes = True
    
    # Verificar archivos requeridos
    for archivo in archivos_requeridos:
        archivo_path = local_path / archivo
        if archivo_path.exists():
            tamaño = archivo_path.stat().st_size / (1024**3)
            print(f"  ✓ {archivo} ({tamaño:.2f} GB)")
        else:
            print(f"  ✗ {archivo} - FALTANTE")
            todos_presentes = False
    
    # Verificar archivos opcionales
    for archivo in archivos_opcionales:
        archivo_path = local_path / archivo
        if archivo_path.exists():
            tamaño = archivo_path.stat().st_size / (1024**3)
            print(f"  ✓ {archivo} ({tamaño:.2f} GB)")
        else:
            # Buscar variaciones del nombre
            encontrado = False
            for archivo_alt in local_path.glob("*.pth"):
                if "14B" in archivo_alt.name or "1.3B" in archivo_alt.name:
                    tamaño = archivo_alt.stat().st_size / (1024**3)
                    print(f"  ℹ {archivo_alt.name} encontrado ({tamaño:.2f} GB) - puede ser el archivo del transformer")
                    encontrado = True
                    break
            if not encontrado:
                print(f"  ⚠ {archivo} - no encontrado (puede tener otro nombre)")
    
    return todos_presentes


def descargar_clip_modelo(directorio_destino="/app/models"):
    """
    Descarga el modelo CLIP necesario para I2V si falta.
    
    El modelo CLIP puede no estar incluido en el repositorio principal
    y necesitar descarga separada.
    """
    snapshot_download = verificar_huggingface()
    if snapshot_download is None:
        return False
    
    clip_file = "models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth"
    clip_dir = f"{directorio_destino}/Wan2.1-T2V-14B"
    clip_path = Path(clip_dir) / clip_file
    
    if clip_path.exists():
        print(f"✓ Modelo CLIP ya existe: {clip_path}")
        return True
    
    print("\n" + "="*60)
    print("DESCARGANDO MODELO CLIP PARA I2V")
    print("="*60)
    print(f"  Archivo requerido: {clip_file}")
    print(f"  Destino: {clip_dir}")
    print("\n⚠ El modelo CLIP puede estar en el repositorio principal.")
    print("  Si la descarga falla, verifica que el repositorio esté completo.")
    print("  Repositorio: Wan-AI/Wan2.1-T2V-14B\n")
    
    # Intentar descargar desde los repositorios de I2V (donde está el CLIP)
    try:
        from huggingface_hub import hf_hub_download
        
        # El modelo CLIP está en los repositorios de I2V, no en T2V
        repositorios_i2v = [
            "Wan-AI/Wan2.1-I2V-14B-480P",  # Para 480P
            "Wan-AI/Wan2.1-I2V-14B-720P",  # Para 720P
            "Wan-AI/Wan2.1-T2V-14B",       # Intentar también T2V por si acaso
        ]
        
        print("Intentando descargar desde repositorios de I2V...")
        descargado = False
        
        for repo_id in repositorios_i2v:
            try:
                print(f"  Intentando desde: {repo_id}...")
                hf_hub_download(
                    repo_id=repo_id,
                    filename=clip_file,
                    local_dir=clip_dir,
                    local_dir_use_symlinks=False,
                    resume_download=True
                )
                
                if clip_path.exists():
                    print(f"\n✓ Modelo CLIP descargado exitosamente desde {repo_id}")
                    print(f"  Ubicación: {clip_path}")
                    descargado = True
                    break
            except Exception as e:
                print(f"    No encontrado en {repo_id}: {e}")
                continue
        
        if descargado:
            return True
        else:
            print(f"\n⚠ El archivo no se encontró en ninguno de los repositorios.")
            print("  Puede que necesites descargarlo manualmente.")
            print("\nOpciones:")
            print("1. Descarga manualmente desde Hugging Face:")
            print("   https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-480P/tree/main")
            print("   o")
            print("   https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-720P/tree/main")
            print(f"   Busca el archivo: {clip_file}")
            print("\n2. Descarga todo el repositorio I2V:")
            print("   huggingface-cli download Wan-AI/Wan2.1-I2V-14B-480P --local-dir /app/models/Wan2.1-I2V-14B-480P")
            print("   Luego copia el archivo CLIP al directorio del modelo 14B")
            return False
            
    except Exception as e:
        print(f"\n✗ Error al descargar modelo CLIP: {e}")
        print("\nOpciones:")
        print("1. Descarga manualmente desde Hugging Face:")
        print("   https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-480P/tree/main")
        print(f"   Busca el archivo: {clip_file}")
        print("\n2. Descarga todo el repositorio I2V y copia el archivo:")
        print("   huggingface-cli download Wan-AI/Wan2.1-I2V-14B-480P --local-dir /tmp/i2v")
        print(f"   cp /tmp/i2v/{clip_file} {clip_dir}/")
        return False


def verificar_huggingface():
    """Verifica que huggingface_hub esté instalado."""
    try:
        from huggingface_hub import snapshot_download
        return snapshot_download
    except ImportError:
        print("✗ Error: huggingface_hub no está instalado.")
        print("  Instalando huggingface_hub...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub[cli]"])
            from huggingface_hub import snapshot_download
            return snapshot_download
        except Exception as e:
            print(f"✗ Error al instalar huggingface_hub: {e}")
            print("\nPor favor, instala manualmente:")
            print("  pip install huggingface_hub[cli]")
            return None


def descargar_modelo(modelo, directorio_destino="/app/models"):
    """
    Descarga un modelo de Wan 2.1 desde Hugging Face.
    
    Args:
        modelo: "1.3B" o "14B"
        directorio_destino: Directorio donde guardar el modelo
    
    Returns:
        True si la descarga fue exitosa, False en caso contrario
    """
    snapshot_download = verificar_huggingface()
    if snapshot_download is None:
        return False
    
    # Mapear modelo a repo_id y nombre de directorio
    modelos = {
        "1.3B": {
            "repo_id": "Wan-AI/Wan2.1-T2V-1.3B",
            "local_dir": f"{directorio_destino}/Wan2.1-T2V-1.3B",
            "descripcion": "Modelo 1.3B (recomendado para GPUs con 8-12 GB VRAM, ~5 GB)"
        },
        "14B": {
            "repo_id": "Wan-AI/Wan2.1-T2V-14B",
            "local_dir": f"{directorio_destino}/Wan2.1-T2V-14B",
            "descripcion": "Modelo 14B T2V (requiere GPU con 16+ GB VRAM, ~28 GB)"
        },
        "i2v-480p": {
            "repo_id": "Wan-AI/Wan2.1-I2V-14B-480P",
            "local_dir": f"{directorio_destino}/Wan2.1-I2V-14B-480P",
            "descripcion": "Modelo I2V 14B 480P (requiere GPU con 16+ GB VRAM, para I2V, ~28 GB)"
        },
        "i2v-720p": {
            "repo_id": "Wan-AI/Wan2.1-I2V-14B-720P",
            "local_dir": f"{directorio_destino}/Wan2.1-I2V-14B-720P",
            "descripcion": "Modelo I2V 14B 720P (requiere GPU con 16+ GB VRAM, para I2V, ~28 GB)"
        }
    }
    
    if modelo not in modelos:
        print(f"✗ Error: Modelo '{modelo}' no válido.")
        print(f"  Modelos disponibles: {', '.join(modelos.keys())}")
        return False
    
    info = modelos[modelo]
    repo_id = info["repo_id"]
    local_dir = info["local_dir"]
    descripcion = info["descripcion"]
    
    # Verificar si el modelo ya existe
    local_path = Path(local_dir)
    if local_path.exists() and any(local_path.iterdir()):
        respuesta = input(f"\n⚠ El modelo {modelo} ya existe en {local_dir}.\n"
                         f"  ¿Deseas descargarlo de nuevo? (s/N): ")
        if respuesta.lower() != 's':
            print(f"✓ Usando modelo existente en: {local_dir}")
            return True
    
    print("\n" + "="*60)
    print(f"DESCARGANDO MODELO {modelo}")
    print("="*60)
    print(f"  Repositorio: {repo_id}")
    print(f"  Descripción: {descripcion}")
    print(f"  Destino: {local_dir}")
    print(f"  (En el host: {local_dir.replace('/app/models', '/home/202111068/workdata/models')})")
    print("\n⚠ Esto puede tomar mucho tiempo dependiendo de tu conexión...")
    print("   El modelo se descargará en segundo plano.\n")
    
    try:
        # Crear directorio si no existe
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Descargar modelo
        print(f"Descargando {repo_id}...")
        snapshot_download(
            repo_id=repo_id,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        
        # Verificar archivos requeridos después de la descarga
        print("\nVerificando archivos del modelo...")
        archivos_requeridos = verificar_archivos_modelo(modelo, local_dir)
        
        if not archivos_requeridos:
            print("\n⚠ Algunos archivos pueden estar faltando.")
            print("  Si encuentras errores, intenta descargar nuevamente o verifica manualmente.")
        
        print(f"\n✓ Modelo {modelo} descargado exitosamente")
        print(f"  Ubicación: {local_dir}")
        print(f"  (En el host: {local_dir.replace('/app/models', '/home/202111068/workdata/models')})")
        
        # Si es el modelo 14B o I2V, verificar y descargar CLIP y tokenizer si faltan
        if modelo in ["14B", "i2v-480p", "i2v-720p"]:
            clip_file = local_path / "models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth"
            tokenizer_dir = local_path / "xlm-roberta-large"
            
            if not clip_file.exists():
                print("\n⚠ Modelo CLIP no encontrado. Intentando descargar...")
                # Para I2V, el CLIP debería estar en el mismo directorio
                if modelo.startswith("i2v"):
                    print("  (El modelo CLIP debería estar incluido en el repositorio I2V)")
                else:
                    descargar_clip_modelo(directorio_destino)
            
            if not tokenizer_dir.exists() or not any(tokenizer_dir.iterdir()):
                print("\n⚠ Tokenizer xlm-roberta-large no encontrado.")
                print("  Ejecuta: python codigo/descargar_tokenizer.py --directorio " + str(local_path))
                print("  O manualmente:")
                print(f"  python -c \"from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('xlm-roberta-large').save_pretrained('{tokenizer_dir}')\"")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠ Descarga interrumpida por el usuario.")
        print(f"  Puedes reanudar la descarga ejecutando el script nuevamente.")
        return False
    except Exception as e:
        print(f"\n✗ Error al descargar modelo: {e}")
        print("\nTroubleshooting:")
        print("1. Verifica tu conexión a internet")
        print("2. Verifica que tengas suficiente espacio en disco")
        print("3. Intenta descargar manualmente usando:")
        print(f"   huggingface-cli download {repo_id} --local-dir {local_dir}")
        return False


def descargar_ambos(directorio_destino="/app/models"):
    """Descarga ambos modelos (1.3B y 14B)."""
    print("="*60)
    print("DESCARGANDO AMBOS MODELOS")
    print("="*60)
    print("\nEsto descargará:")
    print("  1. Modelo 1.3B (~5 GB)")
    print("  2. Modelo 14B (~28 GB)")
    print("\n⚠ Total aproximado: ~33 GB")
    print("   Esto puede tomar varias horas dependiendo de tu conexión.\n")
    
    respuesta = input("¿Deseas continuar? (s/N): ")
    if respuesta.lower() != 's':
        print("Descarga cancelada.")
        return False
    
    # Descargar 1.3B primero
    print("\n" + "="*60)
    print("PASO 1/2: Descargando modelo 1.3B")
    print("="*60)
    if not descargar_modelo("1.3B", directorio_destino):
        print("\n✗ Error al descargar modelo 1.3B")
        return False
    
    # Descargar 14B
    print("\n" + "="*60)
    print("PASO 2/2: Descargando modelo 14B")
    print("="*60)
    if not descargar_modelo("14B", directorio_destino):
        print("\n✗ Error al descargar modelo 14B")
        return False
    
    # Verificar y descargar CLIP si falta
    print("\n" + "="*60)
    print("Verificando modelo CLIP para I2V")
    print("="*60)
    clip_dir = f"{directorio_destino}/Wan2.1-T2V-14B"
    clip_file = Path(clip_dir) / "models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth"
    if not clip_file.exists():
        print("⚠ Modelo CLIP no encontrado. Intentando descargar...")
        descargar_clip_modelo(directorio_destino)
    
    print("\n" + "="*60)
    print("✓ AMBOS MODELOS DESCARGADOS EXITOSAMENTE")
    print("="*60)
    return True


def verificar_modelos(directorio_destino="/app/models"):
    """Verifica qué modelos están disponibles."""
    print("\n" + "="*60)
    print("MODELOS DISPONIBLES")
    print("="*60)
    
    modelos = {
        "1.3B": f"{directorio_destino}/Wan2.1-T2V-1.3B",
        "14B": f"{directorio_destino}/Wan2.1-T2V-14B"
    }
    
    todos_disponibles = True
    for nombre, ruta in modelos.items():
        path = Path(ruta)
        if path.exists() and any(path.iterdir()):
            tamaño = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            tamaño_gb = tamaño / (1024**3)
            print(f"\n✓ {nombre}: Disponible")
            print(f"  Ruta: {ruta}")
            print(f"  Tamaño: {tamaño_gb:.2f} GB")
        else:
            print(f"\n✗ {nombre}: No disponible")
            print(f"  Ruta: {ruta}")
            todos_disponibles = False
    
    print("\n" + "="*60)
    if todos_disponibles:
        print("✓ Todos los modelos están disponibles")
    else:
        print("⚠ Algunos modelos no están disponibles")
        print("  Usa este script para descargarlos.")
    print("="*60)
    
    return todos_disponibles


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Descarga modelos de Wan 2.1 desde Hugging Face",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Descargar modelo 1.3B (para T2V)
  python descargar_modelo.py --modelo 1.3B

  # Descargar modelo 14B T2V
  python descargar_modelo.py --modelo 14B

  # Descargar modelo I2V 480P (para I2V con resolución 832x480)
  python descargar_modelo.py --modelo i2v-480p

  # Descargar modelo I2V 720P (para I2V con resolución 1280x720)
  python descargar_modelo.py --modelo i2v-720p

  # Descargar ambos modelos T2V (1.3B y 14B)
  python descargar_modelo.py --modelo ambos

  # Verificar qué modelos están disponibles
  python descargar_modelo.py --verificar

  # Especificar directorio de destino
  python descargar_modelo.py --modelo i2v-480p --directorio /ruta/personalizada
        """
    )
    
    parser.add_argument("--modelo", type=str, 
                       choices=["1.3B", "14B", "i2v-480p", "i2v-720p", "ambos"],
                       help="Modelo a descargar: '1.3B', '14B', 'i2v-480p', 'i2v-720p', o 'ambos'")
    parser.add_argument("--directorio", type=str, default="/app/models",
                       help="Directorio donde guardar los modelos (default: /app/models)")
    parser.add_argument("--verificar", action="store_true",
                       help="Solo verificar qué modelos están disponibles, sin descargar")
    parser.add_argument("--descargar_clip", action="store_true",
                       help="Descargar solo el modelo CLIP necesario para I2V")
    
    args = parser.parse_args()
    
    # Si solo se quiere verificar
    if args.verificar:
        verificar_modelos(args.directorio)
        return
    
    # Si solo se quiere descargar CLIP
    if args.descargar_clip:
        exito = descargar_clip_modelo(args.directorio)
        sys.exit(0 if exito else 1)
    
    # Validar que se especifique un modelo
    if not args.modelo:
        print("✗ Error: Debes especificar --modelo o usar --verificar")
        print("\nOpciones:")
        print("  --modelo 1.3B      : Descargar modelo 1.3B (T2V)")
        print("  --modelo 14B       : Descargar modelo 14B (T2V)")
        print("  --modelo i2v-480p  : Descargar modelo I2V 480P (para I2V)")
        print("  --modelo i2v-720p  : Descargar modelo I2V 720P (para I2V)")
        print("  --modelo ambos     : Descargar ambos modelos T2V (1.3B y 14B)")
        print("  --verificar        : Verificar modelos disponibles")
        sys.exit(1)
    
    # Descargar modelo(s)
    if args.modelo == "ambos":
        exito = descargar_ambos(args.directorio)
    else:
        exito = descargar_modelo(args.modelo, args.directorio)
    
    if exito:
        print("\n✓ Proceso completado exitosamente")
        print("\nAhora puedes usar los modelos para generar videos:")
        if args.modelo in ["1.3B", "ambos"]:
            print("\n  # T2V con modelo 1.3B")
            print("  python codigo/generar_video.py --modo t2v \\")
            print("      --prompt 'Tu prompt aquí' \\")
            print("      --salida resultados/video.mp4 \\")
            print("      --ckpt_dir /app/models/Wan2.1-T2V-1.3B")
        if args.modelo in ["14B", "ambos"]:
            print("\n  # T2V con modelo 14B")
            print("  python codigo/generar_video.py --modo t2v \\")
            print("      --prompt 'Tu prompt aquí' \\")
            print("      --salida resultados/video.mp4 \\")
            print("      --ckpt_dir /app/models/Wan2.1-T2V-14B")
        if args.modelo == "i2v-480p":
            print("\n  # I2V con modelo I2V-480P")
            print("  python codigo/generar_video.py --modo i2v \\")
            print("      --imagen_referencia recursos/imagen.png \\")
            print("      --prompt 'Tu prompt aquí' \\")
            print("      --salida resultados/video.mp4 \\")
            print("      --resolucion 832x480 \\")
            print("      --ckpt_dir /app/models/Wan2.1-I2V-14B-480P")
        if args.modelo == "i2v-720p":
            print("\n  # I2V con modelo I2V-720P")
            print("  python codigo/generar_video.py --modo i2v \\")
            print("      --imagen_referencia recursos/imagen.png \\")
            print("      --prompt 'Tu prompt aquí' \\")
            print("      --salida resultados/video.mp4 \\")
            print("      --resolucion 1280x720 \\")
            print("      --ckpt_dir /app/models/Wan2.1-I2V-14B-720P")
    else:
        print("\n✗ Error en el proceso de descarga")
        sys.exit(1)


if __name__ == "__main__":
    main()

