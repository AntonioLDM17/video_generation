#!/usr/bin/env python3
"""
Script para limpiar la memoria GPU antes de generar videos.

Útil cuando tienes problemas de memoria CUDA.
"""

import sys

def limpiar_memoria():
    """Limpia la memoria GPU."""
    try:
        import torch
        
        if not torch.cuda.is_available():
            print("⚠ CUDA no está disponible")
            return False
        
        print("Memoria GPU antes de limpiar:")
        print(f"  Reservada: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")
        print(f"  Asignada: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
        
        # Limpiar caché
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        
        print("\nMemoria GPU después de limpiar:")
        print(f"  Reservada: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")
        print(f"  Asignada: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
        
        print("\n✓ Memoria GPU limpiada")
        return True
        
    except ImportError:
        print("✗ PyTorch no está instalado")
        return False
    except Exception as e:
        print(f"✗ Error al limpiar memoria: {e}")
        return False


if __name__ == "__main__":
    limpiar_memoria()

