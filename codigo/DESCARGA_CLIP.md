# Descarga del Modelo CLIP para I2V

Si encuentras el error:
```
FileNotFoundError: models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth
```

Esto significa que el modelo CLIP necesario para I2V (Image-to-Video) no está presente.

## Solución Automática (Recomendada)

Usa el script de descarga que ahora incluye verificación y descarga automática del CLIP:

```bash
# Descargar solo el modelo CLIP
python codigo/descargar_modelo.py --descargar_clip

# O descargar el modelo 14B completo (incluye verificación de CLIP)
python codigo/descargar_modelo.py --modelo 14B
```

## Solución Manual

### Opción 1: Usando huggingface-cli (desde repositorio I2V)

```bash
# El modelo CLIP está en el repositorio I2V, no en T2V
# Opción A: Descargar solo el archivo CLIP
huggingface-cli download Wan-AI/Wan2.1-I2V-14B-480P \
    models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth \
    --local-dir /app/models/Wan2.1-T2V-14B

# Opción B: Descargar todo el repositorio I2V y copiar el archivo
huggingface-cli download Wan-AI/Wan2.1-I2V-14B-480P --local-dir /tmp/i2v
cp /tmp/i2v/models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth \
   /app/models/Wan2.1-T2V-14B/
```

### Opción 2: Usando Python (desde repositorio I2V)

```python
from huggingface_hub import hf_hub_download

# El modelo CLIP está en el repositorio I2V
hf_hub_download(
    repo_id="Wan-AI/Wan2.1-I2V-14B-480P",  # o I2V-14B-720P
    filename="models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth",
    local_dir="/app/models/Wan2.1-T2V-14B",
    local_dir_use_symlinks=False
)
```

### Opción 3: Descarga desde Hugging Face Web

**IMPORTANTE:** El modelo CLIP está en el repositorio **I2V**, no en T2V.

1. Ve a uno de estos repositorios:
   - https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-480P/tree/main (para 480P)
   - https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-720P/tree/main (para 720P)
2. Busca el archivo: `models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth`
3. Descárgalo manualmente
4. Colócalo en: `/app/models/Wan2.1-T2V-14B/` (dentro del contenedor)
   o en: `/home/202111068/workdata/models/Wan2.1-T2V-14B/` (en el host)

## Verificación

Después de descargar, verifica que el archivo esté presente:

```bash
ls -lh /app/models/Wan2.1-T2V-14B/models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth
```

O usa el script de verificación:

```bash
python codigo/descargar_modelo.py --verificar
```

## Descargar el Tokenizer

Además del modelo CLIP, también necesitas el tokenizer `xlm-roberta-large`:

```bash
# Usando el script
python codigo/descargar_tokenizer.py

# O manualmente
python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('xlm-roberta-large').save_pretrained('/app/models/Wan2.1-T2V-14B/xlm-roberta-large')"
```

El tokenizer se descargará automáticamente en: `/app/models/Wan2.1-T2V-14B/xlm-roberta-large/`

## Nota

El modelo CLIP y el tokenizer son necesarios **solo para I2V (Image-to-Video)**. Si solo usas T2V (Text-to-Video), no necesitas estos archivos.

