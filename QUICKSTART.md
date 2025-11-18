# Quick Start Guide - Wan 2.1 Video Generation

## Inicio Rápido

### 1. Construir la imagen Docker

```bash
cd /home/202111068/workspace/practicas/video_generation
docker-compose build
```

### 2. Iniciar el contenedor

```bash
docker-compose up -d
```

### 3. Acceder al contenedor

```bash
docker-compose exec wan2.1-generator bash
```

### 4. Verificar el setup (dentro del contenedor)

El script de entrada verifica automáticamente:
- GPU NVIDIA disponible
- **Selecciona automáticamente la GPU con más memoria disponible** (si hay múltiples GPUs)
- PyTorch y CUDA
- Repositorio Wan2.1 (lo clona si no existe)

**Nota:** Si tienes múltiples GPUs, el contenedor seleccionará automáticamente la que tenga más memoria libre. Puedes verificar qué GPU se seleccionó en los logs del contenedor.

### 5. Descargar un modelo

```bash
# Opción 1: Usando el script de descarga (RECOMENDADO)
python codigo/descargar_modelo.py --modelo 1.3B    # Modelo pequeño para T2V (~5 GB)
python codigo/descargar_modelo.py --modelo 14B     # Modelo grande para T2V (~28 GB)
python codigo/descargar_modelo.py --modelo i2v-480p  # Modelo I2V 480P (para I2V con resolución 832x480)
python codigo/descargar_modelo.py --modelo i2v-720p  # Modelo I2V 720P (para I2V con resolución 1280x720)
python codigo/descargar_tokenizer.py               # Tokenizer necesario para I2V
python codigo/descargar_modelo.py --modelo ambos   # Descargar ambos modelos T2V (1.3B y 14B)
python codigo/descargar_modelo.py --verificar      # Verificar qué modelos están disponibles

# Opción 2: Usando el script bash
./codigo/descargar_modelo.sh 1.3B
./codigo/descargar_modelo.sh 14B
./codigo/descargar_modelo.sh ambos
./codigo/descargar_modelo.sh verificar

# Opción 3: Usando huggingface-cli directamente
huggingface-cli download Wan-AI/Wan2.1-T2V-1.3B --local-dir /app/models/Wan2.1-T2V-1.3B
huggingface-cli download Wan-AI/Wan2.1-T2V-14B --local-dir /app/models/Wan2.1-T2V-14B
huggingface-cli download Wan-AI/Wan2.1-I2V-14B-480P --local-dir /app/models/Wan2.1-I2V-14B-480P
huggingface-cli download Wan-AI/Wan2.1-I2V-14B-720P --local-dir /app/models/Wan2.1-I2V-14B-720P

# Opción 4: Usando Python directamente
python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='Wan-AI/Wan2.1-T2V-1.3B', local_dir='/app/models/Wan2.1-T2V-1.3B')"
```

**Nota:** 
- El modelo se guardará en `/app/models` dentro del contenedor, que está mapeado a `/home/202111068/workdata/models` en el host.
- Para I2V (Image-to-Video) necesitas un checkpoint específico de I2V:
  - `Wan2.1-I2V-14B-480P` para resolución 832x480
  - `Wan2.1-I2V-14B-720P` para resolución 1280x720
  - **Nota importante:** El checkpoint de T2V-14B NO funciona para I2V. Necesitas descargar el checkpoint específico de I2V.
- Para T2V (Text-to-Video) puedes usar el modelo 1.3B o 14B.

### 6. Generar tu primer video

```bash
# Ejemplo simple (T2V con modelo 1.3B)
python codigo/generar_video.py --modo t2v \
    --prompt "A blue soda can on a wooden table, soft lighting" \
    --salida resultados/mi_primer_video.mp4 \
    --ckpt_dir /app/models/Wan2.1-T2V-1.3B

# Ejemplo I2V (con optimizaciones automáticas de memoria)
python codigo/generar_video.py --modo i2v \
    --imagen_referencia recursos/imagen.png \
    --prompt "The product rotating slowly" \
    --salida resultados/video_i2v.mp4
    # Las optimizaciones --offload_model y --t5_cpu se activan automáticamente

# O usar el script de ejemplo
python codigo/ejemplo_generacion.py
```

**Nota sobre memoria:** El script activa automáticamente optimizaciones de memoria para I2V con el modelo 14B. Si tienes problemas de memoria, consulta `codigo/SOLUCION_MEMORIA.md`.

### 7. Encontrar tus resultados

Los videos generados se guardan en:
- **Dentro del contenedor:** `/app/resultados/`
- **En el host:** `/home/202111068/workdata/results/`

## Comandos Útiles

### Ver logs del contenedor
```bash
docker-compose logs -f wan2.1-generator
```

### Detener el contenedor
```bash
docker-compose stop
```

### Reiniciar el contenedor
```bash
docker-compose restart
```

### Salir del contenedor (sin detenerlo)
```bash
exit
```

## Estructura de Comandos

### Text-to-Video (T2V)
```bash
python codigo/generar_video.py --modo t2v \
    --prompt "Tu descripción aquí" \
    --salida resultados/video.mp4 \
    --ckpt_dir /app/models/Wan2.1-T2V-1.3B
```

### Image-to-Video (I2V)
```bash
# I2V requiere el modelo 14B (se usa automáticamente)
# Las optimizaciones de memoria se activan automáticamente
python codigo/generar_video.py --modo i2v \
    --imagen_referencia recursos/drink.png \
    --prompt "A person drinking the energy drink at the beach" \
    --salida resultados/video.mp4
    # --offload_model y --t5_cpu se activan automáticamente para reducir VRAM
```

### Con optimizaciones de memoria explícitas (si tienes problemas)

```bash
# Para T2V con modelo 14B
python codigo/generar_video.py --modo t2v \
    --prompt "Tu prompt" \
    --salida resultados/video.mp4 \
    --ckpt_dir /app/models/Wan2.1-T2V-14B \
    --offload_model --t5_cpu

# Para I2V (ya se activan automáticamente, pero puedes forzarlas)
python codigo/generar_video.py --modo i2v \
    --imagen_referencia recursos/imagen.png \
    --prompt "Tu prompt" \
    --salida resultados/video.mp4 \
    --offload_model --t5_cpu
```

**Nota:** Si tu GPU tiene mucha memoria (32+ GB), puedes desactivar optimizaciones:
```bash
python codigo/generar_video.py --modo i2v ... --sin_optimizaciones
```

## Selección de GPU

### Ver qué GPU se seleccionó automáticamente

```bash
# Ver información de todas las GPUs
python codigo/seleccionar_gpu.py --mostrar_todas

# Ver solo la GPU seleccionada
python codigo/seleccionar_gpu.py
```

### Seleccionar manualmente una GPU específica

Si quieres usar una GPU específica en lugar de la selección automática:

```bash
# Dentro del contenedor
export CUDA_VISIBLE_DEVICES=1  # Usar GPU 1
# O
export CUDA_VISIBLE_DEVICES=0,1  # Usar GPUs 0 y 1
```

## Solución de Problemas Rápidos

### "CUDA not available"
- Verifica que NVIDIA Docker runtime esté instalado
- Ejecuta: `nvidia-smi` en el host para verificar GPU

### "Out of Memory"
- Usa `--offload_model --t5_cpu`
- Reduce resolución: `--resolucion 832x480`
- Usa el modelo 1.3B en lugar del 14B

### "Model not found"
- Descarga el modelo primero (ver paso 5)
- Verifica que esté en `/app/models/Wan2.1-T2V-1.3B`

### "Wan2.1 repository not found"
- El script de entrada debería clonarlo automáticamente
- Si falla, clónalo manualmente:
  ```bash
  cd /app
  git clone https://github.com/Wan-Video/Wan2.1.git
  ```

## Próximos Pasos

1. Lee `instrucciones/guia_del_estudiante.md` para la práctica completa
2. Revisa `codigo/ejemplo_prompts.txt` para ejemplos de prompts
3. Experimenta con diferentes prompts y escenarios
4. Genera al menos 5 videos en diferentes escenarios para la práctica

## Recursos

- **Guía del estudiante:** `instrucciones/guia_del_estudiante.md`
- **Ejemplos de prompts:** `codigo/ejemplo_prompts.txt`
- **Documentación completa:** `README.md`

