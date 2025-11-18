# Wan 2.1 Video Generation - Docker Setup

Este repositorio contiene el entorno Docker para generar videos usando el modelo Wan 2.1.

## Requisitos Previos

- Docker y Docker Compose instalados
- NVIDIA Docker runtime configurado (para soporte GPU)
- GPU NVIDIA con mínimo 8 GB VRAM (recomendado)
- Espacio en disco: ~50 GB libres

**Nota:** El contenedor selecciona automáticamente la GPU con más memoria disponible. Si tienes múltiples GPUs, se usará la que tenga más memoria libre.

## Configuración Rápida

### 1. Verificar que NVIDIA Docker funciona

```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### 2. Crear directorios para modelos y resultados

```bash
mkdir -p /home/202111068/workdata/models
mkdir -p /home/202111068/workdata/results
```

### 3. Construir y ejecutar el contenedor

```bash
cd /home/202111068/workspace/practicas/video_generation
docker-compose build
docker-compose up -d
```

### 4. Acceder al contenedor

```bash
docker-compose exec wan2.1-generator bash
```

## Descargar Modelos

Dentro del contenedor, puedes descargar los modelos usando:

### Opción 1: Usando el script de descarga (RECOMENDADO)

```bash
# Descargar modelo 1.3B (~5 GB, para T2V)
python codigo/descargar_modelo.py --modelo 1.3B

# Descargar modelo 14B (~28 GB, necesario para I2V)
python codigo/descargar_modelo.py --modelo 14B

# Después de descargar el modelo 14B, descargar el tokenizer para I2V
python codigo/descargar_tokenizer.py

# Descargar ambos modelos
python codigo/descargar_modelo.py --modelo ambos

# Verificar qué modelos están disponibles
python codigo/descargar_modelo.py --verificar
```

### Opción 2: Usando el script bash

```bash
./codigo/descargar_modelo.sh 1.3B    # Modelo pequeño
./codigo/descargar_modelo.sh 14B     # Modelo grande
./codigo/descargar_modelo.sh ambos   # Ambos modelos
./codigo/descargar_modelo.sh verificar  # Verificar disponibles
```

### Opción 3: Usando huggingface-cli directamente

```bash
huggingface-cli download Wan-AI/Wan2.1-T2V-1.3B --local-dir /app/models/Wan2.1-T2V-1.3B
huggingface-cli download Wan-AI/Wan2.1-T2V-14B --local-dir /app/models/Wan2.1-T2V-14B
```

### Opción 4: Usando Python directamente

```python
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='Wan-AI/Wan2.1-T2V-1.3B',
    local_dir='/app/models/Wan2.1-T2V-1.3B'
)
```

**Nota:** 
- Los modelos se guardan en `/app/models` dentro del contenedor, que está mapeado a `/home/202111068/workdata/models` en el host.
- Para I2V (Image-to-Video) necesitas un checkpoint específico de I2V:
  - `Wan2.1-I2V-14B-480P` para resolución 832x480
  - `Wan2.1-I2V-14B-720P` para resolución 1280x720
  - **Nota importante:** El checkpoint de T2V-14B NO funciona para I2V. Necesitas descargar el checkpoint específico de I2V usando:
    ```bash
    python codigo/descargar_modelo.py --modelo i2v-480p  # Para 480P
    python codigo/descargar_modelo.py --modelo i2v-720p  # Para 720P
    ```
- Para T2V (Text-to-Video) puedes usar el modelo 1.3B o 14B.

## Generar Videos

### Text-to-Video (T2V)

```bash
python codigo/generar_video.py --modo t2v \
    --prompt "Una lata de refresco azul sobre una mesa de madera, iluminación suave" \
    --salida resultados/video_t2v.mp4 \
    --ckpt_dir /app/models/Wan2.1-T2V-1.3B
```

### Image-to-Video (I2V)

```bash
python codigo/generar_video.py --modo i2v \
    --imagen_referencia recursos/ejemplo_producto.png \
    --prompt "La lata de refresco rotando lentamente sobre la mesa" \
    --salida resultados/video_i2v.mp4 \
    --ckpt_dir /app/models/Wan2.1-I2V-14B-480P
```

### Masked Video-to-Video (VACE)

El modo VACE (Video-Aware Content Editing) permite editar videos usando máscaras, manteniendo consistencia de objetos específicos mientras se modifica el resto del contenido. Esto es especialmente útil para mantener la consistencia de un producto a través de diferentes escenarios.

**⚠️ Requisito previo:** Necesitas descargar el modelo VACE antes de usar este modo:

```bash
# Descargar modelo VACE 14B (recomendado)
huggingface-cli download Wan-AI/Wan2.1-VACE-14B --local-dir /app/models/Wan2.1-VACE-14B

# O modelo VACE 1.3B (menor calidad, menos memoria)
huggingface-cli download Wan-AI/Wan2.1-VACE-1.3B --local-dir /app/models/Wan2.1-VACE-1.3B
```

#### Paso 1: Crear una máscara

Primero, necesitas crear una máscara que identifique las regiones del video que quieres mantener sin cambios (el producto) y las que quieres editar (el fondo).

**Opción A: Crear máscara automática (básica):**

```bash
# Crear una máscara automática basada en la imagen del producto
# Esta máscara crea un círculo en el centro de la imagen
python codigo/generar_video_con_mascara.py \
    --crear_mascara \
    --imagen_producto recursos/drink.png \
    --salida recursos/mascara_drink.png
```

**Opción B: Crear máscara manualmente:**

Puedes crear tu propia máscara usando cualquier editor de imágenes (GIMP, Photoshop, etc.):
- **Blanco (255)**: Regiones que se mantienen sin cambios (el producto)
- **Negro (0)**: Regiones que se editan según el prompt (el fondo)
- Guarda como PNG en escala de grises

#### Paso 2: Generar un video base (opcional)

Si no tienes un video base, puedes generar uno usando I2V:

```bash
# Generar video base con I2V
python codigo/generar_video.py --modo i2v \
    --imagen_referencia recursos/drink.png \
    --prompt "A person drinking the energy drink at the beach" \
    --salida resultados/video_base.mp4 \
    --ckpt_dir /app/models/Wan2.1-I2V-14B-480P \
    --resolucion 832x480
```

#### Paso 3: Editar el video con máscara

Una vez que tienes el video base y la máscara, puedes editarlo:

```bash
# Editar video manteniendo el producto, cambiando el fondo
python codigo/generar_video_con_mascara.py \
    --video_base /app/resultados/i2v-14B_832*480_1_1_A_person_drinking_the_energy_drink_at_the_beach_20251110_185755.mp4 \
    --mascara recursos/mascara_drink.png \
    --prompt "Cambiar el fondo a un ambiente de montaña con nieve, manteniendo el producto exactamente igual" \
    --salida resultados/video_editado.mp4 \
    --ckpt_dir /app/models/Wan2.1-VACE-14B \
    --resolucion 832x480 \
    --offload_model \
    --t5_cpu
```

**Parámetros importantes:**
- `--video_base`: Ruta al video que quieres editar
- `--mascara`: Ruta a la máscara (imagen PNG o video MP4)
- `--prompt`: Descripción de cómo quieres editar el video
- `--ckpt_dir`: Debe apuntar a un modelo VACE (no I2V o T2V)
- `--offload_model` y `--t5_cpu`: Recomendados para ahorrar memoria GPU

#### Ejemplo completo paso a paso

```bash
# 1. Crear máscara automática para el producto
python codigo/generar_video_con_mascara.py \
    --crear_mascara \
    --imagen_producto recursos/drink.png \
    --salida recursos/mascara_drink.png

# 2. Generar video base con I2V (si no tienes uno)
python codigo/generar_video.py --modo i2v \
    --imagen_referencia recursos/drink.png \
    --prompt "A person drinking the energy drink at the beach, sunny day" \
    --salida resultados/video_base.mp4 \
    --ckpt_dir /app/models/Wan2.1-I2V-14B-480P \
    --resolucion 832x480

# 3. Editar el video cambiando el fondo
python codigo/generar_video_con_mascara.py \
    --video_base resultados/i2v-14B_832*480_1_1_A_person_drinking_the_energy_drink_at_the_beach_20251110_185755.mp4  \
    --mascara recursos/mascara_drink_mask_1762811250.mp4 \
    --prompt "Cambiar el fondo a un ambiente de montaña con nieve, manteniendo el producto exactamente igual" \
    --salida resultados/video_montana.mp4 \
    --ckpt_dir /app/models/Wan2.1-VACE-14B \
    --resolucion 832x480 \
    --offload_model \
    --t5_cpu

# 4. Crear otra variante con diferente fondo
python codigo/generar_video_con_mascara.py \
    --video_base resultados/video_base.mp4 \
    --mascara recursos/mascara_drink.png \
    --prompt "Cambiar el fondo a una ciudad moderna de noche, manteniendo el producto exactamente igual" \
    --salida resultados/video_ciudad.mp4 \
    --ckpt_dir /app/models/Wan2.1-VACE-14B \
    --resolucion 832x480 \
    --offload_model \
    --t5_cpu
```

**Notas importantes:**
- El script convierte automáticamente máscaras de imagen (PNG) a video de máscara si es necesario
- La máscara debe tener las mismas dimensiones que el video base (el script lo ajusta automáticamente)
- VACE requiere el modelo específico VACE, no funciona con modelos I2V o T2V
- Para mejores resultados, ajusta la máscara manualmente para que cubra exactamente el producto

### Con optimizaciones de memoria

```bash
python codigo/generar_video.py --modo t2v \
    --prompt "Tu prompt aquí" \
    --salida resultados/video.mp4 \
    --ckpt_dir /app/models/Wan2.1-T2V-1.3B \
    --offload_model --t5_cpu
```

## Estructura de Directorios

```
video_generation/
├── codigo/                    # Scripts de generación
│   ├── generar_video.py      # Script principal T2V/I2V
│   ├── generar_video_con_mascara.py  # Script MV2V
│   ├── setup_wan2_1.py       # Script de configuración
│   ├── ejemplo_prompts.txt   # Ejemplos de prompts
│   └── requirements.txt       # Dependencias Python
├── recursos/                  # Recursos (imágenes de ejemplo)
├── instrucciones/             # Guías y documentación
│   └── guia_del_estudiante.md
├── Wan2.1/                   # Repositorio clonado (se crea automáticamente)
├── Dockerfile                # Imagen Docker
├── docker-compose.yml        # Configuración Docker Compose
├── docker-entrypoint.sh      # Script de inicio del contenedor
└── README.md                 # Este archivo
```

## Volúmenes Montados

- `/app/codigo` → `./codigo` (código editable)
- `/app/resultados` → `/home/202111068/workdata/results` (videos generados)
- `/app/models` → `/home/202111068/workdata/models` (modelos descargados)
- `/app/Wan2.1` → `./Wan2.1` (repositorio clonado)
- `/app/.cache` → `./cache` (caché de Hugging Face)
- `/app/recursos` → `./recursos` (recursos)
- `/app/instrucciones` → `./instrucciones` (documentación)

## Solución de Problemas

### Error: "CUDA not available"

Verifica que el runtime de NVIDIA Docker esté configurado:

```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### Error: "Out of Memory"

- Usa el modelo 1.3B en lugar del 14B
- Reduce la resolución: `--resolucion 832x480`
- Activa optimizaciones: `--offload_model --t5_cpu`

### El repositorio Wan2.1 no se clona

El script de entrada intenta clonar automáticamente. Si falla, puedes clonarlo manualmente:

```bash
cd /home/202111068/workspace/practicas/video_generation
git clone https://github.com/Wan-Video/Wan2.1.git
```

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

### Eliminar el contenedor (mantiene volúmenes)

```bash
docker-compose down
```

### Reconstruir la imagen

```bash
docker-compose build --no-cache
```

## Recursos Adicionales

- [Documentación oficial de Wan 2.1](https://github.com/Wan-Video/Wan2.1)
- [Modelos en Hugging Face](https://huggingface.co/Wan-AI/Wan2.1-T2V-14B)
- Ver `instrucciones/guia_del_estudiante.md` para más detalles sobre la práctica

## Notas

- Los modelos son grandes (5-28 GB), asegúrate de tener suficiente espacio
- La generación de videos puede tomar 15-30 minutos dependiendo de la GPU
- Los resultados se guardan automáticamente en `/home/202111068/workdata/results`

