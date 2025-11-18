# Solución: Error de flash-attn en I2V

Si encuentras el error:
```
AssertionError
File "/app/Wan2.1/wan/modules/attention.py", line 112, in flash_attention
    assert FLASH_ATTN_2_AVAILABLE
```

Esto significa que `flash-attn` no está instalado correctamente. **flash-attn es REQUERIDO para I2V**, no es opcional.

## Solución Rápida

Dentro del contenedor Docker, ejecuta:

```bash
# Opción 1: Usar el script de instalación
./codigo/instalar_flash_attn.sh

# Opción 2: Instalar manualmente
pip install flash-attn --no-build-isolation
```

## Si la instalación falla

### Problema: Falta nvcc (compilador CUDA)

```bash
# Instalar CUDA development tools
apt-get update
apt-get install -y cuda-cudart-dev-12-1 cuda-nvcc-12-1
pip install flash-attn --no-build-isolation
```

### Problema: Compilación muy lenta

```bash
# Limitar número de jobs para evitar problemas de memoria
MAX_JOBS=2 pip install flash-attn --no-build-isolation
```

### Problema: No se puede compilar

Si no puedes compilar flash-attn, puedes intentar:

1. **Usar una imagen Docker diferente** que ya tenga flash-attn preinstalado
2. **Usar wheels precompilados** (si están disponibles para tu versión de CUDA)
3. **Usar solo T2V** (que no requiere flash-attn para funcionar)

## Verificar instalación

Después de instalar, verifica que funciona:

```bash
python3 -c "import flash_attn; print('✓ flash_attn instalado correctamente')"
```

## Nota sobre T2V vs I2V

- **T2V (Text-to-Video)**: Puede funcionar sin flash-attn (más lento)
- **I2V (Image-to-Video)**: **REQUIERE** flash-attn para funcionar

Si solo necesitas T2V, puedes evitar instalar flash-attn, pero para I2V es obligatorio.

