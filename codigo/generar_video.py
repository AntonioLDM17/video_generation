#!/usr/bin/env python3
"""
Script para generar videos usando Wan 2.1 en modo T2V (Text-to-Video) o I2V (Image-to-Video).

Este script proporciona una interfaz simple para generar videos a partir de:
- Texto (modo T2V)
- Imagen de referencia (modo I2V)

Uso:
    python generar_video.py --modo t2v --prompt "Descripción del video" --salida video.mp4
    python generar_video.py --modo i2v --imagen_referencia imagen.png --prompt "Descripción" --salida video.mp4

Autor: Práctica académica - Generación de Video con Wan 2.1
"""

import argparse
import os
import sys
from pathlib import Path
import torch


def verificar_entorno():
    """Verifica que el entorno esté correctamente configurado."""
    errores = []
    
    # Verificar PyTorch
    try:
        import torch
        if not torch.cuda.is_available():
            print("⚠ Advertencia: CUDA no disponible. La generación será muy lenta en CPU.")
    except ImportError:
        errores.append("PyTorch no está instalado. Ejecuta: pip install torch")
    
    # Verificar repositorio Wan2.1
    possible_paths = [
        Path("/app/Wan2.1"),  # Docker container path
        Path("Wan2.1"),  # Current directory
        Path("../Wan2.1"),  # Parent directory
        Path("../../Wan2.1"),  # Two levels up
    ]
    
    wan2_1_found = any(p.exists() and p.is_dir() for p in possible_paths)
    if not wan2_1_found:
        errores.append("Repositorio Wan2.1 no encontrado. Ejecuta setup_wan2_1.py primero.")
    
    if errores:
        print("✗ Errores encontrados:")
        for error in errores:
            print(f"  - {error}")
        return False
    
    return True


def encontrar_repositorio_wan():
    """Encuentra la ruta del repositorio Wan2.1."""
    possible_paths = [
        Path("/app/Wan2.1"),  # Docker container path
        Path("Wan2.1"),  # Current directory
        Path("../Wan2.1"),  # Parent directory
        Path("../../Wan2.1"),  # Two levels up
    ]
    
    for path in possible_paths:
        if path.exists() and path.is_dir():
            return path.resolve()
    
    return None


def generar_video_t2v(prompt, salida, ckpt_dir, resolucion="832x480", 
                      offload_model=False, t5_cpu=False, sample_guide_scale=7.5):
    """
    Genera un video a partir de texto usando el modelo T2V.
    
    Args:
        prompt: Texto descriptivo del video deseado
        salida: Ruta de salida para el video generado
        ckpt_dir: Directorio donde están los checkpoints del modelo
        resolucion: Resolución del video (formato: "ancho x alto")
        offload_model: Si True, usa offloading para reducir memoria GPU
        t5_cpu: Si True, ejecuta el encoder T5 en CPU
        sample_guide_scale: Escala de guía para el sampling
    """
    print(f"\nGenerando video T2V...")
    print(f"  Prompt: {prompt}")
    print(f"  Resolución: {resolucion}")
    print(f"  Salida: {salida}")
    
    # Encontrar repositorio Wan2.1
    repo_path = encontrar_repositorio_wan()
    
    if repo_path is None:
        print("✗ Error: Repositorio Wan2.1 no encontrado.")
        print("  Ejecuta setup_wan2_1.py primero o clona el repositorio manualmente.")
        return False
    
    print(f"✓ Repositorio Wan2.1 encontrado en: {repo_path}")
    
    # Agregar el repositorio al path
    sys.path.insert(0, str(repo_path))
    
    try:
        # Importar módulos de Wan2.1
        print("\nImportando módulos de Wan2.1...")
        
        # Construir comando para generate.py del repositorio
        generate_script = repo_path / "generate.py"
        
        if not generate_script.exists():
            print("✗ Error: generate.py no encontrado en el repositorio Wan2.1")
            print("  Verifica que el repositorio esté correctamente clonado.")
            return False
        
        # Determinar el modelo según el tamaño del checkpoint
        if "1.3B" in str(ckpt_dir) or "1_3B" in str(ckpt_dir):
            task = "t2v-1.3B"
            size_default = "832*480"
        else:
            task = "t2v-14B"
            size_default = "1280*720" if resolucion == "1280x720" else "832*480"
        
        # Construir comando
        comando = [
            sys.executable,
            str(generate_script),
            "--task", task,
            "--size", size_default,
            "--ckpt_dir", str(ckpt_dir),
            "--prompt", prompt
        ]
        
        if offload_model:
            comando.append("--offload_model")
            comando.append("True")
        
        if t5_cpu:
            comando.append("--t5_cpu")
        
        if task == "t2v-1.3B":
            comando.extend(["--sample_guide_scale", str(sample_guide_scale)])
            comando.extend(["--sample_shift", "8"])
        
        # Limpiar memoria GPU antes de ejecutar
        print("\nLimpiando memoria GPU...")
        try:
            import torch
            torch.cuda.empty_cache()
            print("✓ Memoria GPU limpiada")
        except:
            pass
        
        # Ejecutar generación
        print("\nEjecutando generación (esto puede tomar varios minutos)...")
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
            return True
        else:
            print("\n✗ Error durante la generación")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Verifica que el repositorio Wan2.1 esté correctamente clonado")
        print("2. Verifica que los checkpoints del modelo estén descargados")
        print("3. Verifica que tengas suficiente memoria GPU")
        print("4. Consulta la documentación oficial: https://github.com/Wan-Video/Wan2.1")
        return False


def generar_video_i2v(imagen_referencia, prompt, salida, ckpt_dir, resolucion="832x480",
                      offload_model=False, t5_cpu=False, frame_num=None):
    """
    Genera un video a partir de una imagen de referencia usando el modelo I2V.
    
    Args:
        imagen_referencia: Ruta a la imagen de referencia
        prompt: Descripción de la animación deseada
        salida: Ruta de salida para el video generado
        ckpt_dir: Directorio donde están los checkpoints del modelo
        resolucion: Resolución del video
        offload_model: Si True, usa offloading para reducir memoria GPU
        t5_cpu: Si True, ejecuta el encoder T5 en CPU
    """
    print(f"\nGenerando video I2V...")
    print(f"  Imagen de referencia: {imagen_referencia}")
    print(f"  Prompt: {prompt}")
    print(f"  Resolución: {resolucion}")
    print(f"  Salida: {salida}")
    
    # Verificar que existe la imagen
    if not Path(imagen_referencia).exists():
        print(f"✗ Error: Imagen de referencia no encontrada: {imagen_referencia}")
        return False
    
    # Encontrar repositorio Wan2.1
    repo_path = encontrar_repositorio_wan()
    
    if repo_path is None:
        print("✗ Error: Repositorio Wan2.1 no encontrado.")
        return False
    
    print(f"✓ Repositorio Wan2.1 encontrado en: {repo_path}")
    
    # Agregar el repositorio al path
    sys.path.insert(0, str(repo_path))
    
    try:
        # Construir comando para generate.py del repositorio
        generate_script = repo_path / "generate.py"
        
        if not generate_script.exists():
            print("✗ Error: generate.py no encontrado en el repositorio Wan2.1")
            return False
        
        # Determinar el modelo según el tamaño del checkpoint
        # Nota: I2V requiere un checkpoint específico de I2V, no de T2V
        # Los checkpoints de I2V son: Wan2.1-I2V-14B-480P o Wan2.1-I2V-14B-720P
        
        # Verificar si el checkpoint es de I2V
        ckpt_str = str(ckpt_dir)
        es_checkpoint_i2v = "I2V" in ckpt_str or "i2v" in ckpt_str
        
        if not es_checkpoint_i2v:
            # Intentar encontrar el checkpoint de I2V correspondiente
            print("⚠ Advertencia: I2V requiere un checkpoint específico de I2V.")
            print("  El checkpoint de T2V no es compatible con I2V.")
            
            # Determinar qué checkpoint de I2V usar según la resolución
            if resolucion == "1280x720":
                ckpt_i2v = str(ckpt_dir).replace("T2V-14B", "I2V-14B-720P").replace("T2V_14B", "I2V-14B-720P")
                if "1.3B" in ckpt_str or "1_3B" in ckpt_str:
                    ckpt_i2v = "/app/models/Wan2.1-I2V-14B-720P"
            else:
                ckpt_i2v = str(ckpt_dir).replace("T2V-14B", "I2V-14B-480P").replace("T2V_14B", "I2V-14B-480P")
                if "1.3B" in ckpt_str or "1_3B" in ckpt_str:
                    ckpt_i2v = "/app/models/Wan2.1-I2V-14B-480P"
            
            print(f"  Buscando checkpoint de I2V en: {ckpt_i2v}")
            
            if Path(ckpt_i2v).exists():
                ckpt_dir = ckpt_i2v
                print(f"✓ Usando checkpoint de I2V: {ckpt_dir}")
            else:
                print(f"✗ Error: No se encontró el checkpoint de I2V en: {ckpt_i2v}")
                print("\n  Por favor, descarga el checkpoint correcto de I2V:")
                if resolucion == "1280x720":
                    print("    huggingface-cli download Wan-AI/Wan2.1-I2V-14B-720P --local-dir /app/models/Wan2.1-I2V-14B-720P")
                else:
                    print("    huggingface-cli download Wan-AI/Wan2.1-I2V-14B-480P --local-dir /app/models/Wan2.1-I2V-14B-480P")
                print("\n  O usa el script de descarga:")
                print("    python codigo/descargar_modelo.py --modelo i2v-480p  # Para 480P")
                print("    python codigo/descargar_modelo.py --modelo i2v-720p  # Para 720P")
                return False
        
        task = "i2v-14B"
        # Determinar tamaño según resolución
        if resolucion == "1280x720":
            size_default = "1280*720"
        else:
            size_default = "832*480"
        
        # Construir comando para I2V
        comando = [
            sys.executable,
            str(generate_script),
            "--task", task,
            "--size", size_default,
            "--ckpt_dir", str(ckpt_dir),
            "--prompt", prompt,
            "--image", str(Path(imagen_referencia).resolve())
        ]
        
        if offload_model:
            comando.append("--offload_model")
            comando.append("True")
        
        if t5_cpu:
            comando.append("--t5_cpu")
        
        # Configurar número de frames
        # NOTA: I2V requiere 81 frames por defecto. El código de Wan2.1 tiene la máscara
        # hardcodeada a 81 frames, por lo que usar un número diferente causará errores.
        if frame_num is not None:
            if frame_num != 81:
                print("⚠ Advertencia: I2V está optimizado para 81 frames.")
                print("  Usar un número diferente puede causar errores de dimensiones.")
            comando.extend(["--frame_num", str(frame_num)])
        else:
            # Usar 81 frames por defecto (requerido por I2V)
            comando.extend(["--frame_num", "81"])
            if offload_model or t5_cpu:
                print("ℹ Usando 81 frames (requerido por I2V) con optimizaciones de memoria activas")
        
        # Limpiar memoria GPU antes de ejecutar
        print("\nLimpiando memoria GPU...")
        try:
            import torch
            torch.cuda.empty_cache()
            print("✓ Memoria GPU limpiada")
        except:
            pass
        
        # Ejecutar generación
        print("\nEjecutando generación I2V (esto puede tomar varios minutos)...")
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
            return True
        else:
            print("\n✗ Error durante la generación")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Verifica que el repositorio Wan2.1 esté correctamente clonado")
        print("2. Verifica que los checkpoints del modelo estén descargados")
        print("3. Verifica que tengas suficiente memoria GPU")
        print("4. Consulta la documentación oficial: https://github.com/Wan-Video/Wan2.1")
        return False


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Genera videos usando Wan 2.1 (T2V o I2V)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Generar video desde texto
  python generar_video.py --modo t2v --prompt "Un gato caminando por un jardín" --salida video.mp4

  # Generar video desde imagen
  python generar_video.py --modo i2v --imagen_referencia producto.png --prompt "Producto rotando" --salida video.mp4

  # Con opciones de optimización de memoria
  python generar_video.py --modo t2v --prompt "Video" --salida video.mp4 --offload_model --t5_cpu
        """
    )
    
    parser.add_argument("--modo", type=str, choices=["t2v", "i2v"], required=True,
                       help="Modo de generación: 't2v' (texto a video) o 'i2v' (imagen a video)")
    parser.add_argument("--prompt", type=str, required=True,
                       help="Descripción textual del video deseado")
    parser.add_argument("--imagen_referencia", type=str, default=None,
                       help="Ruta a imagen de referencia (requerido para modo I2V)")
    parser.add_argument("--salida", type=str, default="resultados/video_generado.mp4",
                       help="Ruta de salida para el video generado")
    parser.add_argument("--ckpt_dir", type=str, default=None,
                       help="Directorio donde están los checkpoints del modelo. Para I2V se requiere el modelo 14B.")
    parser.add_argument("--resolucion", type=str, default="832x480",
                       choices=["832x480", "1280x720"],
                       help="Resolución del video generado")
    parser.add_argument("--offload_model", action="store_true",
                       help="Usar offloading de modelo para reducir uso de memoria GPU (recomendado para modelo 14B)")
    parser.add_argument("--t5_cpu", action="store_true",
                       help="Ejecutar encoder T5 en CPU en lugar de GPU (recomendado para modelo 14B)")
    parser.add_argument("--sin_optimizaciones", action="store_true",
                       help="Desactivar optimizaciones automáticas de memoria (solo para GPUs muy grandes)")
    parser.add_argument("--sample_guide_scale", type=float, default=7.5,
                       help="Escala de guía para el sampling (solo para modelo 1.3B)")
    parser.add_argument("--frame_num", type=int, default=None,
                       help="Número de frames a generar (default: 81. NOTA: I2V requiere 81 frames, usar otro número puede causar errores)")
    
    args = parser.parse_args()
    
    # Verificar entorno
    if not verificar_entorno():
        sys.exit(1)
    
    # Crear directorio de salida si no existe
    salida_path = Path(args.salida)
    salida_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Validaciones según el modo
    if args.modo == "i2v" and not args.imagen_referencia:
        print("✗ Error: --imagen_referencia es requerido para el modo I2V")
        sys.exit(1)
    
    # Establecer checkpoint por defecto según el modo
    if args.ckpt_dir is None:
        if args.modo == "i2v":
            # I2V requiere un checkpoint específico de I2V (no T2V)
            # Seleccionar según la resolución
            if args.resolucion == "1280x720":
                args.ckpt_dir = "/app/models/Wan2.1-I2V-14B-720P"
            else:
                args.ckpt_dir = "/app/models/Wan2.1-I2V-14B-480P"
            print(f"ℹ Usando checkpoint de I2V por defecto: {args.ckpt_dir}")
            print("  (I2V requiere un checkpoint específico, diferente de T2V)")
            # El modelo 14B es muy grande, usar optimizaciones de memoria por defecto
            if not args.sin_optimizaciones and not args.offload_model and not args.t5_cpu:
                print("ℹ Activando optimizaciones de memoria automáticamente para el modelo 14B")
                print("  (usa --sin_optimizaciones si tu GPU tiene suficiente memoria)")
                args.offload_model = True
                args.t5_cpu = True
        else:
            # T2V puede usar 1.3B o 14B
            args.ckpt_dir = "/app/models/Wan2.1-T2V-1.3B"
            print("ℹ Usando modelo 1.3B por defecto para T2V")
    
    # Generar video según el modo
    if args.modo == "t2v":
        exito = generar_video_t2v(
            args.prompt,
            args.salida,
            args.ckpt_dir,
            args.resolucion,
            args.offload_model,
            args.t5_cpu,
            args.sample_guide_scale
        )
    else:  # i2v
        exito = generar_video_i2v(
            args.imagen_referencia,
            args.prompt,
            args.salida,
            args.ckpt_dir,
            args.resolucion,
            args.offload_model,
            args.t5_cpu,
            args.frame_num
        )
    
    if exito:
        print("\n✓ Proceso completado")
        print(f"  Video guardado en: {args.salida}")
    else:
        print("\n✗ Error en la generación del video")
        sys.exit(1)


if __name__ == "__main__":
    main()

