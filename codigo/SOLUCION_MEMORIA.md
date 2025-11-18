# Solución: Error de Memoria CUDA (Out of Memory)

Si encuentras el error:
```
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate X MiB. GPU 0 has a total capacity of Y GiB...
```

Esto significa que el modelo está usando más memoria GPU de la disponible.

## Soluciones Rápidas

### Opción 1: Usar Optimizaciones de Memoria (Recomendado)

El script ahora activa automáticamente optimizaciones para I2V con modelo 14B, pero puedes forzarlas:

```bash
# Para I2V con modelo 14B
python codigo/generar_video.py --modo i2v \
    --imagen_referencia recursos/imagen.png \
    --prompt "Tu prompt" \
    --salida resultados/video.mp4 \
    --offload_model --t5_cpu

# Para T2V con modelo 14B
python codigo/generar_video.py --modo t2v \
    --prompt "Tu prompt" \
    --salida resultados/video.mp4 \
    --ckpt_dir /app/models/Wan2.1-T2V-14B \
    --offload_model --t5_cpu
```

**Qué hacen estas opciones:**
- `--offload_model`: Mueve partes del modelo a CPU cuando no se usan
- `--t5_cpu`: Ejecuta el encoder T5 en CPU en lugar de GPU

### Opción 2: Reducir Resolución

```bash
# Usar resolución más baja (480P en lugar de 720P)
python codigo/generar_video.py --modo i2v \
    --imagen_referencia recursos/imagen.png \
    --prompt "Tu prompt" \
    --salida resultados/video.mp4 \
    --resolucion 832x480 \
    --offload_model --t5_cpu
```

### Opción 3: Usar Modelo Más Pequeño (Solo T2V)

```bash
# El modelo 1.3B usa mucha menos memoria
python codigo/generar_video.py --modo t2v \
    --prompt "Tu prompt" \
    --salida resultados/video.mp4 \
    --ckpt_dir /app/models/Wan2.1-T2V-1.3B
```

**Nota:** I2V solo está disponible con el modelo 14B.

### Opción 4: Limpiar Memoria GPU

Antes de ejecutar, limpia la memoria:

```bash
# Usando el script
python codigo/limpiar_memoria.py

# O manualmente
python3 -c "import torch; torch.cuda.empty_cache(); print('Memoria GPU limpiada')"
```

### Opción 5: Reducir Número de Frames (Solo T2V)

**⚠️ IMPORTANTE:** I2V requiere 81 frames. El código de Wan2.1 tiene la máscara hardcodeada a 81 frames, por lo que usar un número diferente causará errores de dimensiones (`RuntimeError: Sizes of tensors must match`).

Para T2V, puedes reducir el número de frames:

```bash
# Generar video T2V con menos frames (49 en lugar de 81)
python codigo/generar_video.py --modo t2v \
    --prompt "Tu prompt" \
    --salida resultados/video.mp4 \
    --frame_num 49 \
    --offload_model --t5_cpu
```

**Nota sobre I2V:** Si tienes problemas de memoria con I2V, usa las optimizaciones (`--offload_model --t5_cpu`) pero mantén 81 frames. Reducir el número de frames causará errores.

### Opción 5: Configurar PyTorch para Mejor Gestión de Memoria

```bash
# Antes de ejecutar el script
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Luego ejecuta tu comando
python codigo/generar_video.py ...
```

## Requisitos de Memoria Aproximados

| Modelo | Resolución | VRAM Mínima | VRAM Recomendada |
|--------|-----------|-------------|------------------|
| 1.3B   | 480P      | 8 GB        | 12 GB            |
| 14B    | 480P      | 16 GB       | 24 GB            |
| 14B    | 720P      | 20 GB       | 32 GB            |
| 14B    | 480P (con optimizaciones) | 12 GB | 16 GB |
| 14B    | 720P (con optimizaciones) | 16 GB | 24 GB |

## Verificar Uso de Memoria

```bash
# Ver uso actual de GPU
nvidia-smi

# Ver uso desde Python
python3 -c "import torch; print(f'Memoria GPU usada: {torch.cuda.memory_allocated()/1024**3:.2f} GB'); print(f'Memoria GPU reservada: {torch.cuda.memory_reserved()/1024**3:.2f} GB')"
```

## Soluciones Avanzadas

### Usar CPU para Más Componentes

Si tienes mucha RAM pero poca VRAM, puedes modificar el código para mover más componentes a CPU, pero esto será mucho más lento.

### Usar Multi-GPU (si tienes múltiples GPUs)

El código de Wan2.1 soporta multi-GPU, pero requiere configuración adicional. Consulta la documentación oficial.

### Usar Cuantización (Experimental)

Algunas versiones de Wan2.1 soportan cuantización para reducir el uso de memoria, pero puede afectar la calidad.

## Recomendaciones

1. **Para GPUs con 8-12 GB VRAM**: Usa el modelo 1.3B con T2V
2. **Para GPUs con 16-24 GB VRAM**: Usa el modelo 14B con optimizaciones (`--offload_model --t5_cpu`)
3. **Para GPUs con 32+ GB VRAM**: Puedes usar el modelo 14B sin optimizaciones

## Nota sobre I2V

I2V requiere el modelo 14B, que es muy grande. Si tu GPU no tiene suficiente memoria incluso con optimizaciones, considera:
- Usar solo T2V con el modelo 1.3B
- Reducir la resolución a 480P
- Usar servicios cloud con GPUs más grandes

