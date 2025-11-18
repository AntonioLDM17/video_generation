#!/usr/bin/env python3
"""
Script para generar videos usando Wan 2.1 en modo MV2V (Masked Video-to-Video).

Este script permite editar videos mediante máscaras, manteniendo consistencia
de objetos específicos mientras se modifica el resto del contenido.

El modo MV2V es especialmente útil para mantener la consistencia de un producto
a través de diferentes escenarios, ya que permite especificar qué regiones
del video deben permanecer inalteradas.

Uso:
    python generar_video_con_mascara.py \\
        --video_base video_inicial.mp4 \\
        --mascara mascara_producto.png \\
        --prompt "Editar fondo manteniendo producto" \\
        --salida video_editado.mp4

Autor: Práctica académica - Generación de Video con Wan 2.1
"""

import argparse
import os
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import cv2
import subprocess
import time


def verificar_entorno():
    """Verifica que el entorno esté correctamente configurado."""
    errores = []
    
    try:
        import torch
        if not torch.cuda.is_available():
            print("⚠ Advertencia: CUDA no disponible. La generación será muy lenta en CPU.")
    except ImportError:
        errores.append("PyTorch no está instalado")
    
    # Check multiple possible paths for Wan2.1
    possible_paths = [
        Path("/app/Wan2.1"),  # Docker container path
        Path("Wan2.1"),  # Current directory
        Path("../Wan2.1"),  # Parent directory
        Path("../../Wan2.1"),  # Two levels up
    ]
    wan2_1_found = any(p.exists() and p.is_dir() for p in possible_paths)
    if not wan2_1_found:
        errores.append("Repositorio Wan2.1 no encontrado")
    
    if errores:
        print("✗ Errores encontrados:")
        for error in errores:
            print(f"  - {error}")
        return False
    
    return True


def cargar_mascara(ruta_mascara):
    """
    Carga y procesa una máscara de imagen.
    
    La máscara debe ser una imagen en escala de grises donde:
    - Valores blancos (255) indican regiones que se mantienen
    - Valores negros (0) indican regiones que se editan
    
    Args:
        ruta_mascara: Ruta a la imagen de máscara
    
    Returns:
        Máscara procesada como array numpy
    """
    if not Path(ruta_mascara).exists():
        print(f"✗ Error: Máscara no encontrada: {ruta_mascara}")
        return None
    
    try:
        mascara = Image.open(ruta_mascara).convert("L")
        mascara_array = np.array(mascara)
        
        # Normalizar a rango 0-1
        mascara_normalizada = mascara_array / 255.0
        
        print(f"✓ Máscara cargada: {mascara_array.shape}")
        return mascara_normalizada
    except Exception as e:
        print(f"✗ Error al cargar máscara: {e}")
        return None


def convertir_mascara_imagen_a_video(ruta_mascara_imagen, ruta_video_base):
    """
    Convierte una máscara de imagen estática a un video de máscara
    con las mismas dimensiones y duración que el video base.
    
    Args:
        ruta_mascara_imagen: Ruta a la imagen de máscara
        ruta_video_base: Ruta al video base
    
    Returns:
        Ruta al video de máscara creado, o None si hay error
    """
    try:
        # Cargar video base para obtener dimensiones y duración
        cap = cv2.VideoCapture(str(ruta_video_base))
        if not cap.isOpened():
            print(f"✗ Error: No se pudo abrir el video base: {ruta_video_base}")
            return None
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Contar frames reales leyendo el video
        frame_count = 0
        while True:
            ret, _ = cap.read()
            if not ret:
                break
            frame_count += 1
        
        cap.release()
        
        if frame_count == 0:
            print(f"✗ Error: El video base no tiene frames: {ruta_video_base}")
            return None
        
        print(f"  Video base: {width}x{height}, {fps} fps, {frame_count} frames")
        
        # Cargar máscara de imagen
        mascara_img = cv2.imread(str(ruta_mascara_imagen), cv2.IMREAD_GRAYSCALE)
        if mascara_img is None:
            print(f"✗ Error: No se pudo cargar la máscara: {ruta_mascara_imagen}")
            return None
        
        print(f"  Máscara original: {mascara_img.shape[1]}x{mascara_img.shape[0]}")
        
        # Redimensionar máscara al tamaño del video
        mascara_resized = cv2.resize(mascara_img, (width, height), interpolation=cv2.INTER_LINEAR)
        
        # Crear nombre único para el video de máscara
        mascara_video_path = Path(ruta_mascara_imagen).with_suffix('.mp4')
        # Si ya existe, agregar timestamp
        if mascara_video_path.exists():
            timestamp = int(time.time())
            mascara_video_path = Path(ruta_mascara_imagen).parent / f"{Path(ruta_mascara_imagen).stem}_mask_{timestamp}.mp4"
        
        # Guardar máscara redimensionada temporalmente
        temp_mascara_path = Path(ruta_mascara_imagen).parent / f"temp_mask_{int(time.time())}.png"
        cv2.imwrite(str(temp_mascara_path), mascara_resized)
        
        # Calcular duración del video
        duration = frame_count / fps if fps > 0 else frame_count / 16.0
        
        # Usar ffmpeg para crear el video de máscara
        print(f"  Usando ffmpeg para crear video de máscara...")
        
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Sobrescribir si existe
            '-loop', '1',  # Loop la imagen
            '-i', str(temp_mascara_path),  # Imagen de entrada
            '-t', str(duration),  # Duración
            '-vf', f'scale={width}:{height},fps={fps}',  # Escalar y establecer fps
            '-pix_fmt', 'yuv420p',  # Formato de píxel compatible
            '-c:v', 'libx264',  # Codec H.264
            '-preset', 'fast',  # Preset rápido
            '-crf', '23',  # Calidad
            str(mascara_video_path)
        ]
        
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True
        )
        
        # Limpiar archivo temporal
        if temp_mascara_path.exists():
            temp_mascara_path.unlink()
        
        if result.returncode != 0:
            print(f"✗ Error al ejecutar ffmpeg: {result.stderr}")
            if mascara_video_path.exists():
                mascara_video_path.unlink()
            return None
        
        # Verificar que el archivo se creó correctamente
        if not mascara_video_path.exists():
            print(f"✗ Error: El archivo de video no se creó")
            return None
        
        file_size = mascara_video_path.stat().st_size
        if file_size == 0:
            print(f"✗ Error: El archivo de video está vacío (0 bytes)")
            mascara_video_path.unlink()
            return None
        
        # Verificar que el video se puede leer
        test_cap = cv2.VideoCapture(str(mascara_video_path))
        if not test_cap.isOpened():
            print(f"✗ Error: El archivo de video no se puede leer")
            test_cap.release()
            return None
        
        test_frame_count = int(test_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        test_cap.release()
        
        if test_frame_count == 0:
            print(f"✗ Error: El video no tiene frames")
            return None
        
        print(f"  ✓ Video de máscara creado exitosamente: {mascara_video_path}")
        print(f"    Tamaño: {file_size / 1024:.2f} KB, Frames: {test_frame_count}")
        
        return mascara_video_path
        
    except Exception as e:
        import traceback
        print(f"✗ Error al convertir máscara a video: {e}")
        print(f"  Detalles: {traceback.format_exc()}")
        # Limpiar archivos temporales si existen
        try:
            temp_files = list(Path(ruta_mascara_imagen).parent.glob("temp_mask_*.png"))
            for temp_file in temp_files:
                temp_file.unlink()
        except:
            pass
        return None


def procesar_video_base(ruta_video):
    """
    Procesa el video base para extraer frames y metadatos.
    
    Args:
        ruta_video: Ruta al video base
    
    Returns:
        Tupla con (frames, fps, dimensiones)
    """
    if not Path(ruta_video).exists():
        print(f"✗ Error: Video base no encontrado: {ruta_video}")
        return None, None, None
    
    try:
        cap = cv2.VideoCapture(str(ruta_video))
        
        if not cap.isOpened():
            print(f"✗ Error: No se pudo abrir el video: {ruta_video}")
            return None, None, None
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        
        cap.release()
        
        print(f"✓ Video cargado: {len(frames)} frames, {width}x{height}, {fps} fps")
        return frames, fps, (width, height)
        
    except Exception as e:
        print(f"✗ Error al procesar video: {e}")
        return None, None, None


def generar_video_mv2v(video_base, mascara, prompt, salida, ckpt_dir, 
                       resolucion="832x480", offload_model=False, t5_cpu=False):
    """
    Genera un video editado usando máscaras (VACE - Video-Aware Content Editing).
    
    Args:
        video_base: Ruta al video base
        mascara: Ruta a archivo de máscara de video
        prompt: Instrucciones de edición
        salida: Ruta de salida para el video editado
        ckpt_dir: Directorio donde están los checkpoints del modelo
        resolucion: Resolución del video
        offload_model: Si True, usa offloading para reducir memoria GPU
        t5_cpu: Si True, ejecuta T5 en CPU
    """
    print(f"\nGenerando video VACE (Video-Aware Content Editing)...")
    print(f"  Prompt de edición: {prompt}")
    print(f"  Video base: {video_base}")
    print(f"  Máscara: {mascara}")
    print(f"  Salida: {salida}")
    
    # Verificar repositorio Wan2.1
    possible_paths = [
        Path("/app/Wan2.1"),  # Docker container path
        Path("Wan2.1"),  # Current directory
        Path("../Wan2.1"),  # Parent directory
        Path("../../Wan2.1"),  # Two levels up
    ]
    
    repo_path = None
    for path in possible_paths:
        if path.exists() and path.is_dir():
            repo_path = path.resolve()
            break
    
    if repo_path is None or not repo_path.exists():
        print("✗ Error: Repositorio Wan2.1 no encontrado.")
        print(f"  Buscado en: {[str(p) for p in possible_paths]}")
        return False
    
    print(f"✓ Repositorio Wan2.1 encontrado en: {repo_path}")
    
    # Verificar que los archivos existen
    video_path = Path(video_base)
    mascara_path = Path(mascara)
    
    if not video_path.exists():
        print(f"✗ Error: Video base no encontrado: {video_base}")
        return False
    
    if not mascara_path.exists():
        print(f"✗ Error: Máscara no encontrada: {mascara}")
        return False
    
    # Si la máscara es una imagen, convertirla a video de máscara
    # VACE requiere un video de máscara, no una imagen estática
    if mascara_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
        print("ℹ Máscara es una imagen. Convirtiendo a video de máscara...")
        mascara_video_path = convertir_mascara_imagen_a_video(mascara_path, video_path)
        if mascara_video_path is None:
            print("✗ Error: No se pudo convertir la máscara a video")
            return False
        mascara_path = mascara_video_path
        print(f"✓ Máscara convertida a video: {mascara_path}")
    
    # Determinar el modelo según el checkpoint
    ckpt_str = str(ckpt_dir)
    if "1.3B" in ckpt_str or "1_3B" in ckpt_str:
        task = "vace-1.3B"
        size_default = "480*832" if resolucion == "832x480" else "832*480"
    else:
        task = "vace-14B"
        if resolucion == "1280x720":
            size_default = "1280*720"
        else:
            size_default = "832*480"
    
    # Verificar que el checkpoint es de VACE
    if "VACE" not in ckpt_str and "vace" not in ckpt_str.lower():
        print("⚠ Advertencia: El checkpoint especificado puede no ser de VACE.")
        print("  VACE requiere checkpoints específicos:")
        print("    - Wan2.1-VACE-1.3B para modelo 1.3B")
        print("    - Wan2.1-VACE-14B para modelo 14B")
    
    # Construir comando para generate.py
    generate_script = repo_path / "generate.py"
    if not generate_script.exists():
        print("✗ Error: generate.py no encontrado en el repositorio Wan2.1")
        return False
    
    comando = [
        sys.executable,
        str(generate_script),
        "--task", task,
        "--size", size_default,
        "--ckpt_dir", str(ckpt_dir),
        "--prompt", prompt,
        "--src_video", str(video_path.resolve()),
        "--src_mask", str(mascara_path.resolve()),
        "--frame_num", "81",  # VACE usa 81 frames por defecto
    ]
    
    if offload_model:
        comando.append("--offload_model")
        comando.append("True")
    
    if t5_cpu:
        comando.append("--t5_cpu")
    
    # Limpiar memoria GPU antes de ejecutar
    print("\nLimpiando memoria GPU...")
    try:
        import torch
        torch.cuda.empty_cache()
        print("✓ Memoria GPU limpiada")
    except:
        pass
    
    # Ejecutar generación
    print("\nEjecutando generación VACE (esto puede tomar varios minutos)...")
    print(f"Comando: {' '.join(comando)}")
    
    import subprocess
    import os
    env = os.environ.copy()
    env['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
    resultado = subprocess.run(comando, cwd=str(repo_path), env=env)
    
    if resultado.returncode == 0:
        print(f"\n✓ Video generado exitosamente")
        print(f"  Nota: El video se guarda en el directorio del repositorio Wan2.1")
        print(f"  Busca el archivo de salida y muévelo a: {salida}")
        
        # Intentar encontrar el archivo generado y copiarlo
        # Los archivos generados suelen tener un patrón específico con timestamp
        import glob
        import shutil
        import time
        
        # Buscar archivos mp4 generados recientemente (últimos 5 minutos)
        output_pattern = repo_path / "*.mp4"
        generated_files = glob.glob(str(output_pattern))
        
        if generated_files:
            # Filtrar archivos modificados en los últimos 5 minutos
            current_time = time.time()
            recent_files = [
                f for f in generated_files 
                if current_time - os.path.getmtime(f) < 300  # 5 minutos
            ]
            
            if recent_files:
                # Ordenar por tiempo de modificación (más reciente primero)
                recent_files.sort(key=os.path.getmtime, reverse=True)
                latest_file = recent_files[0]
                print(f"  Archivo generado encontrado: {latest_file}")
                print(f"  Copiando a: {salida}")
                
                # Asegurar que el directorio de salida existe
                Path(salida).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(latest_file, salida)
                print(f"✓ Video copiado a: {salida}")
            else:
                print("  ⚠ No se encontraron archivos generados recientemente")
                print(f"  Busca manualmente en: {repo_path}")
        else:
            print(f"  ⚠ No se encontraron archivos MP4 en: {repo_path}")
            print(f"  El video puede haberse guardado con otro nombre")
        
        return True
    else:
        print("\n✗ Error durante la generación")
        return False


def crear_mascara_ejemplo(imagen_producto, salida_mascara):
    """
    Crea una máscara de ejemplo para un producto.
    
    Esta función proporciona una forma simple de crear una máscara
    basada en detección de color o segmentación básica.
    
    Args:
        imagen_producto: Ruta a imagen del producto
        salida_mascara: Ruta donde guardar la máscara
    """
    print(f"\nCreando máscara de ejemplo para: {imagen_producto}")
    
    try:
        img = cv2.imread(str(imagen_producto))
        if img is None:
            print(f"✗ Error: No se pudo cargar imagen: {imagen_producto}")
            return False
        
        # Convertir a HSV para mejor segmentación de color
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Crear máscara simple (ejemplo: mantener región central)
        height, width = img.shape[:2]
        mascara = np.zeros((height, width), dtype=np.uint8)
        
        # Crear región central (producto típicamente en el centro)
        centro_x, centro_y = width // 2, height // 2
        radio = min(width, height) // 4
        
        cv2.circle(mascara, (centro_x, centro_y), radio, 255, -1)
        
        # Aplicar suavizado
        mascara = cv2.GaussianBlur(mascara, (21, 21), 0)
        
        # Guardar máscara
        cv2.imwrite(str(salida_mascara), mascara)
        
        print(f"✓ Máscara de ejemplo creada: {salida_mascara}")
        print("  Nota: Ajusta la máscara manualmente si es necesario")
        return True
        
    except Exception as e:
        print(f"✗ Error al crear máscara: {e}")
        return False


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Genera videos editados usando máscaras con Wan 2.1 (MV2V)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Editar video con máscara
  python generar_video_con_mascara.py \\
      --video_base video_inicial.mp4 \\
      --mascara mascara_producto.png \\
      --prompt "Cambiar el fondo a una playa manteniendo el producto idéntico" \\
      --salida video_editado.mp4

  # Crear máscara de ejemplo
  python generar_video_con_mascara.py \\
      --crear_mascara \\
      --imagen_producto producto.png \\
      --salida mascara_ejemplo.png

Nota: El modo MV2V puede requerir configuración específica según la versión
de Wan2.1. Consulta la documentación oficial para detalles.
        """
    )
    
    parser.add_argument("--video_base", type=str, default=None,
                       help="Ruta al video base que se va a editar")
    parser.add_argument("--mascara", type=str, default=None,
                       help="Ruta a la imagen de máscara (blanco=mantener, negro=editar)")
    parser.add_argument("--prompt", type=str, default=None,
                       help="Instrucciones de edición del video (requerido para generar video, no necesario para crear máscara)")
    parser.add_argument("--salida", type=str, default="resultados/video_editado.mp4",
                       help="Ruta de salida para el video editado")
    parser.add_argument("--ckpt_dir", type=str, default="/app/models/Wan2.1-VACE-14B",
                       help="Directorio donde están los checkpoints del modelo VACE (Wan2.1-VACE-1.3B o Wan2.1-VACE-14B)")
    parser.add_argument("--resolucion", type=str, default="832x480",
                       choices=["832x480", "1280x720"],
                       help="Resolución del video generado")
    parser.add_argument("--offload_model", action="store_true",
                       help="Usar offloading de modelo para reducir uso de memoria GPU")
    parser.add_argument("--t5_cpu", action="store_true",
                       help="Ejecutar encoder T5 en CPU en lugar de GPU (recomendado para modelo 14B)")
    
    # Opción para crear máscara
    parser.add_argument("--crear_mascara", action="store_true",
                       help="Crear una máscara de ejemplo en lugar de generar video")
    parser.add_argument("--imagen_producto", type=str, default=None,
                       help="Imagen del producto para crear máscara")
    
    args = parser.parse_args()
    
    # Verificar entorno
    if not verificar_entorno():
        sys.exit(1)
    
    # Crear directorio de salida si no existe
    salida_path = Path(args.salida)
    salida_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Modo: crear máscara
    if args.crear_mascara:
        if not args.imagen_producto:
            print("✗ Error: --imagen_producto es requerido cuando se usa --crear_mascara")
            sys.exit(1)
        exito = crear_mascara_ejemplo(args.imagen_producto, args.salida)
        sys.exit(0 if exito else 1)
    
    # Modo: generar video
    if not args.video_base or not args.mascara:
        print("✗ Error: --video_base y --mascara son requeridos para generar video")
        sys.exit(1)
    
    if not args.prompt:
        print("✗ Error: --prompt es requerido para generar video")
        sys.exit(1)
    
    exito = generar_video_mv2v(
        args.video_base,
        args.mascara,
        args.prompt,
        args.salida,
        args.ckpt_dir,
        args.resolucion,
        args.offload_model
    )
    
    if exito:
        print("\n✓ Proceso completado")
        print(f"  Video guardado en: {args.salida}")
    else:
        print("\n✗ Error en la generación del video")
        sys.exit(1)


if __name__ == "__main__":
    main()

