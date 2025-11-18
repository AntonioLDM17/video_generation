#!/usr/bin/env python3
"""
Script de configuración para instalar y configurar el entorno de Wan 2.1.

Este script guía al usuario a través del proceso de:
1. Verificación del entorno
2. Clonado del repositorio oficial de Wan 2.1
3. Descarga de pesos del modelo (si es necesario)
4. Verificación de la instalación

Autor: Práctica académica - Generación de Video con Wan 2.1
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def ejecutar_comando(comando, descripcion, shell=False):
    """
    Ejecuta un comando del sistema y maneja errores.
    
    Args:
        comando: Comando a ejecutar (lista o string)
        descripcion: Descripción del comando para mensajes
        shell: Si es True, ejecuta en shell del sistema
    """
    print(f"\n{descripcion}...")
    try:
        if isinstance(comando, str):
            resultado = subprocess.run(comando, shell=True, check=True, 
                                     capture_output=True, text=True)
        else:
            resultado = subprocess.run(comando, check=True, 
                                     capture_output=True, text=True)
        print(f"✓ {descripcion} completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error al ejecutar: {descripcion}")
        print(f"  Error: {e.stderr}")
        return False


def verificar_python():
    """Verifica que la versión de Python sea adecuada."""
    version = sys.version_info
    print(f"Versión de Python detectada: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Error: Se requiere Python 3.8 o superior")
        return False
    
    print("✓ Versión de Python compatible")
    return True


def verificar_cuda():
    """Verifica la disponibilidad de CUDA."""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ CUDA disponible")
            print(f"  Versión de CUDA: {torch.version.cuda}")
            print(f"  GPU detectada: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("⚠ CUDA no disponible. Se puede ejecutar en CPU (muy lento)")
            return False
    except ImportError:
        print("⚠ PyTorch no instalado. Se instalará en el siguiente paso.")
        return None


def clonar_repositorio_wan():
    """Clona el repositorio oficial de Wan 2.1."""
    # Check multiple possible paths
    possible_paths = [
        Path("/app/Wan2.1"),  # Docker container path
        Path("Wan2.1"),  # Current directory
        Path("../Wan2.1"),  # Parent directory
    ]
    
    repo_path = None
    for path in possible_paths:
        if path.exists() and path.is_dir() and any(path.iterdir()):
            print(f"✓ Repositorio Wan2.1 ya existe en: {path}")
            return True
        elif path.exists() and path.is_dir():
            # Directory exists but is empty
            repo_path = path
            break
    
    if repo_path is None:
        # Try to find a good location
        if Path("/app").exists():
            repo_path = Path("/app/Wan2.1")
        else:
            repo_path = Path("Wan2.1")
    
    if repo_path.exists() and any(repo_path.iterdir()):
        respuesta = input(f"El repositorio Wan2.1 ya existe en {repo_path}. ¿Desea actualizarlo? (s/N): ")
        if respuesta.lower() == 's':
            print("Actualizando repositorio...")
            os.chdir(repo_path)
            ejecutar_comando(["git", "pull"], "Actualización del repositorio")
            os.chdir("..")
        return True
    
    print(f"\nClonando repositorio oficial de Wan 2.1 en {repo_path}...")
    print("Esto puede tomar varios minutos dependiendo de la conexión...")
    
    url_repo = "https://github.com/Wan-Video/Wan2.1.git"
    
    # If directory exists but is empty, clone to temp then copy
    if repo_path.exists():
        temp_path = repo_path.parent / "Wan2.1-tmp"
        comando = ["git", "clone", url_repo, str(temp_path)]
        if ejecutar_comando(comando, "Clonado del repositorio"):
            import shutil
            for item in temp_path.iterdir():
                shutil.move(str(item), str(repo_path / item.name))
            shutil.rmtree(temp_path)
            return True
    else:
        comando = ["git", "clone", url_repo, str(repo_path)]
        return ejecutar_comando(comando, "Clonado del repositorio")


def descargar_modelo():
    """Guía al usuario para descargar el modelo."""
    print("\n" + "="*60)
    print("DESCARGA DEL MODELO")
    print("="*60)
    print("\nDebes descargar uno de los modelos disponibles:")
    print("\n1. T2V-1.3B (Recomendado para GPUs con 8-12 GB VRAM)")
    print("   - Modelo: Wan-AI/Wan2.1-T2V-1.3B")
    print("   - Resolución: 480P")
    print("   - Tamaño aproximado: ~5 GB")
    
    print("\n2. T2V-14B (Requiere GPU con 16+ GB VRAM o multi-GPU)")
    print("   - Modelo: Wan-AI/Wan2.1-T2V-14B")
    print("   - Resolución: 480P y 720P")
    print("   - Tamaño aproximado: ~28 GB")
    
    print("\nOpciones para descargar:")
    print("\nOpción A: Usando huggingface-cli")
    print("  huggingface-cli download Wan-AI/Wan2.1-T2V-1.3B --local-dir /app/models/Wan2.1-T2V-1.3B")
    
    print("\nOpción B: Usando Python")
    print("  from huggingface_hub import snapshot_download")
    print("  snapshot_download(repo_id='Wan-AI/Wan2.1-T2V-1.3B', local_dir='/app/models/Wan2.1-T2V-1.3B')")
    
    print("\nOpción C: Descarga manual desde Hugging Face")
    print("  https://huggingface.co/Wan-AI/Wan2.1-T2V-1.3B")
    
    respuesta = input("\n¿Deseas descargar el modelo ahora? (s/N): ")
    if respuesta.lower() == 's':
        modelo = input("¿Qué modelo deseas descargar? (1.3B/14B): ").strip()
        if modelo == "1.3B":
            repo_id = "Wan-AI/Wan2.1-T2V-1.3B"
            local_dir = "/app/models/Wan2.1-T2V-1.3B"
        elif modelo == "14B":
            repo_id = "Wan-AI/Wan2.1-T2V-14B"
            local_dir = "/app/models/Wan2.1-T2V-14B"
        else:
            print("Opción no válida. Puedes descargar el modelo manualmente más tarde.")
            return
        
        try:
            from huggingface_hub import snapshot_download
            print(f"\nDescargando {repo_id}...")
            print("Esto puede tomar mucho tiempo dependiendo de tu conexión...")
            Path(local_dir).mkdir(parents=True, exist_ok=True)
            snapshot_download(repo_id=repo_id, local_dir=local_dir)
            print(f"✓ Modelo descargado en {local_dir}")
        except ImportError:
            print("✗ huggingface_hub no está instalado. Instalando...")
            subprocess.run([sys.executable, "-m", "pip", "install", "huggingface_hub"])
            from huggingface_hub import snapshot_download
            Path(local_dir).mkdir(parents=True, exist_ok=True)
            snapshot_download(repo_id=repo_id, local_dir=local_dir)
            print(f"✓ Modelo descargado en {local_dir}")
        except Exception as e:
            print(f"✗ Error al descargar modelo: {e}")
            print("Puedes descargarlo manualmente más tarde.")


def verificar_instalacion():
    """Verifica que la instalación sea correcta."""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE INSTALACIÓN")
    print("="*60)
    
    # Verificar PyTorch
    try:
        import torch
        print(f"✓ PyTorch instalado: versión {torch.__version__}")
        if torch.cuda.is_available():
            print(f"✓ CUDA disponible: {torch.version.cuda}")
        else:
            print("⚠ CUDA no disponible")
    except ImportError:
        print("✗ PyTorch no está instalado")
        return False
    
    # Verificar repositorio
    possible_paths = [
        Path("/app/Wan2.1"),
        Path("Wan2.1"),
        Path("../Wan2.1"),
    ]
    
    repo_found = False
    for path in possible_paths:
        if path.exists() and path.is_dir() and any(path.iterdir()):
            print(f"✓ Repositorio Wan2.1 encontrado en: {path}")
            repo_found = True
            break
    
    if not repo_found:
        print("⚠ Repositorio Wan2.1 no encontrado")
    
    # Verificar dependencias principales
    dependencias = ["transformers", "diffusers", "accelerate", "PIL", "cv2"]
    for dep in dependencias:
        try:
            if dep == "PIL":
                import PIL
                print(f"✓ Pillow instalado")
            elif dep == "cv2":
                import cv2
                print(f"✓ OpenCV instalado")
            else:
                __import__(dep)
                print(f"✓ {dep} instalado")
        except ImportError:
            print(f"⚠ {dep} no encontrado")
    
    print("\n" + "="*60)
    print("VERIFICACIÓN COMPLETA")
    print("="*60)
    print("\nPróximos pasos:")
    print("1. Descarga el modelo (si no lo has hecho)")
    print("2. Ejecuta un script de prueba:")
    print("   python codigo/generar_video.py --modo t2v --prompt 'Un gato caminando' --ckpt_dir /app/models/Wan2.1-T2V-1.3B")
    
    return True


def main():
    """Función principal del script de configuración."""
    print("="*60)
    print("CONFIGURACIÓN DE ENTORNO WAN 2.1")
    print("="*60)
    print("\nEste script te guiará a través de la instalación y configuración")
    print("del entorno necesario para trabajar con Wan 2.1.\n")
    
    # Verificar Python
    if not verificar_python():
        sys.exit(1)
    
    # Verificar CUDA (opcional, no crítico)
    verificar_cuda()
    
    # Clonar repositorio
    respuesta = input("\n¿Deseas clonar/actualizar el repositorio oficial de Wan 2.1? (S/n): ")
    if respuesta.lower() != 'n':
        clonar_repositorio_wan()
    
    # Descargar modelo
    descargar_modelo()
    
    # Verificar instalación
    verificar_instalacion()
    
    print("\n✓ Configuración completada")
    print("\nPara más información, consulta la guía del estudiante.")


if __name__ == "__main__":
    main()

