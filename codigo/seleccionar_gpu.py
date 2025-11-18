#!/usr/bin/env python3
"""
Script para seleccionar automáticamente la GPU con más memoria disponible.

Este script detecta todas las GPUs disponibles y selecciona la que tiene
más memoria libre, configurando CUDA_VISIBLE_DEVICES apropiadamente.
"""

import os
import sys


def obtener_info_gpus():
    """
    Obtiene información de todas las GPUs disponibles.
    
    Returns:
        Lista de diccionarios con información de cada GPU
    """
    try:
        import torch
        
        if not torch.cuda.is_available():
            return []
        
        gpus = []
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            # Obtener memoria total y reservada
            torch.cuda.set_device(i)
            memoria_total = props.total_memory / (1024**3)  # GB
            memoria_reservada = torch.cuda.memory_reserved(i) / (1024**3)  # GB
            memoria_libre = memoria_total - memoria_reservada
            
            gpus.append({
                'id': i,
                'name': props.name,
                'total_memory_gb': memoria_total,
                'reserved_memory_gb': memoria_reservada,
                'free_memory_gb': memoria_libre,
                'total_memory_mb': props.total_memory / (1024**2),  # MB para nvidia-smi
            })
        
        return gpus
        
    except ImportError:
        # Si PyTorch no está disponible, usar nvidia-smi
        try:
            import subprocess
            import json
            
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,memory.total,memory.free', 
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return []
            
            gpus = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 4:
                    gpus.append({
                        'id': int(parts[0]),
                        'name': parts[1],
                        'total_memory_gb': float(parts[2]) / 1024,
                        'free_memory_gb': float(parts[3]) / 1024,
                        'reserved_memory_gb': (float(parts[2]) - float(parts[3])) / 1024,
                    })
            
            return gpus
            
        except Exception as e:
            print(f"⚠ Error al obtener información de GPUs: {e}")
            return []


def seleccionar_mejor_gpu():
    """
    Selecciona la GPU con más memoria libre.
    
    Returns:
        ID de la GPU seleccionada, o None si no hay GPUs disponibles
    """
    gpus = obtener_info_gpus()
    
    if not gpus:
        return None
    
    # Ordenar por memoria libre (descendente)
    gpus_ordenadas = sorted(gpus, key=lambda x: x['free_memory_gb'], reverse=True)
    
    mejor_gpu = gpus_ordenadas[0]
    
    return mejor_gpu['id']


def configurar_gpu():
    """
    Configura CUDA_VISIBLE_DEVICES con la GPU con más memoria libre.
    
    Returns:
        ID de la GPU seleccionada, o None si no hay GPUs disponibles
    """
    gpu_id = seleccionar_mejor_gpu()
    
    if gpu_id is None:
        print("⚠ No se encontraron GPUs disponibles")
        return None
    
    # Configurar CUDA_VISIBLE_DEVICES
    os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
    
    # Obtener info de la GPU seleccionada
    gpus = obtener_info_gpus()
    gpu_info = next((g for g in gpus if g['id'] == gpu_id), None)
    
    if gpu_info:
        print(f"✓ GPU seleccionada: {gpu_info['name']} (ID: {gpu_id})")
        print(f"  Memoria total: {gpu_info['total_memory_gb']:.2f} GB")
        print(f"  Memoria libre: {gpu_info['free_memory_gb']:.2f} GB")
    else:
        print(f"✓ GPU seleccionada: ID {gpu_id}")
    
    return gpu_id


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Selecciona automáticamente la GPU con más memoria disponible"
    )
    parser.add_argument(
        "--mostrar_todas",
        action="store_true",
        help="Mostrar información de todas las GPUs disponibles"
    )
    parser.add_argument(
        "--configurar",
        action="store_true",
        help="Configurar CUDA_VISIBLE_DEVICES con la mejor GPU"
    )
    parser.add_argument(
        "--solo_id",
        action="store_true",
        help="Solo imprimir el ID de la GPU seleccionada (útil para scripts)"
    )
    
    args = parser.parse_args()
    
    gpus = obtener_info_gpus()
    
    if not gpus:
        if args.solo_id:
            print("0", end="")
        else:
            print("✗ No se encontraron GPUs disponibles")
        sys.exit(1)
    
    if args.mostrar_todas:
        print("\n" + "="*60)
        print("GPUs DISPONIBLES")
        print("="*60)
        for gpu in gpus:
            print(f"\nGPU {gpu['id']}: {gpu['name']}")
            print(f"  Memoria total: {gpu['total_memory_gb']:.2f} GB")
            print(f"  Memoria libre: {gpu['free_memory_gb']:.2f} GB")
            print(f"  Memoria reservada: {gpu['reserved_memory_gb']:.2f} GB")
    
    mejor_gpu_id = seleccionar_mejor_gpu()
    
    if mejor_gpu_id is None:
        if args.solo_id:
            print("0", end="")
        else:
            print("✗ No se pudo seleccionar una GPU")
        sys.exit(1)
    
    mejor_gpu = next((g for g in gpus if g['id'] == mejor_gpu_id), None)
    
    # Si solo se pide el ID, imprimirlo y salir
    if args.solo_id:
        print(mejor_gpu_id, end="")
        return
    
    print("\n" + "="*60)
    print("GPU SELECCIONADA")
    print("="*60)
    if mejor_gpu:
        print(f"  GPU {mejor_gpu_id}: {mejor_gpu['name']}")
        print(f"  Memoria total: {mejor_gpu['total_memory_gb']:.2f} GB")
        print(f"  Memoria libre: {mejor_gpu['free_memory_gb']:.2f} GB")
    
    if args.configurar:
        configurar_gpu()
        print(f"\n✓ CUDA_VISIBLE_DEVICES configurado a: {mejor_gpu_id}")
    else:
        print(f"\nPara usar esta GPU, ejecuta:")
        print(f"  export CUDA_VISIBLE_DEVICES={mejor_gpu_id}")
        print(f"  O ejecuta: python codigo/seleccionar_gpu.py --configurar")


if __name__ == "__main__":
    main()

