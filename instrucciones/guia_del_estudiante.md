# Guía del Estudiante: Generación de Producto Consistente en Múltiples Escenarios

## Descripción de la Tarea

En esta práctica, deberás diseñar un producto ficticio y generar videos consistentes del mismo producto en diferentes escenarios utilizando el modelo **Wan 2.1**. El objetivo principal es evaluar la capacidad del modelo para mantener la coherencia visual de un objeto a través de distintas condiciones de iluminación, fondos y contextos.

### Objetivos Específicos

1. Definir un producto ficticio con características visuales claras y distintivas
2. Generar videos del producto en al menos 5 escenarios diferentes
3. Evaluar la consistencia visual del producto entre escenarios
4. Documentar el proceso, resultados y análisis en un informe estructurado
5. Reflexionar sobre las capacidades y limitaciones del modelo generativo

## Requisitos Técnicos

### Hardware

- **GPU NVIDIA**: Mínimo 8 GB VRAM (RTX 3060 o superior)
- **RAM**: 16 GB mínimo, 32 GB recomendado
- **Espacio en disco**: 50 GB libres

### Software

- **Python**: Versión 3.8 o superior
- **CUDA**: Versión 11.8 o superior
- **PyTorch**: Versión 2.4.0 o superior
- **Sistema operativo**: Linux, macOS o Windows (recomendado Linux)

### Alternativas sin GPU Local (Si la DGX sigue sin funcionar)

Si no dispones de GPU local, puedes utilizar:

- **Google Colab Pro**: Con acceso a GPU T4 o V100 -
  - https://colab.research.google.com/github/Isi-dev/Google-Colab_Notebooks/blob/main/Wan2_1_14B_T2V_GGUF_Free.ipynb#scrollTo=XV-6JezhtN6l
  - https://colab.research.google.com/github/Isi-dev/Google-Colab_Notebooks/blob/main/Wan2_1_14B_I2V_GGUF_Free.ipynb#scrollTo=t089iwSddWDL
- **Kaggle Notebooks**: GPU P100 gratuita
- **Cloud Computing**: AWS, GCP o Azure con instancias GPU

## Pasos a Seguir

### Paso 1: Definir Producto Ficticio

Define un producto con las siguientes características:

- **Nombre**: Descriptivo y memorable
- **Características visuales**: Color, forma, tamaño, textura, marca/logo
- **Contexto de uso**: Tipo de producto (bebida, electrónico, herramienta, etc.)

**Ejemplo**:

- Producto: "Lata de refresco Sparkle"
- Características: Lata cilíndrica, color azul brillante, logo "Sparkle" en blanco en el centro, diseño minimalista
- Contexto: Bebida energética

### Paso 2: Crear o Seleccionar Imagen de Referencia

Crea una imagen de referencia del producto usando:

- Herramientas de diseño (Photoshop, GIMP, Canva)
- Generación con modelos de imagen (Stable Diffusion, DALL-E)
- Imágenes existentes modificadas (con permiso/licencia)

La imagen debe ser clara, con fondo neutro preferiblemente, y mostrar el producto desde un ángulo frontal o lateral estándar.

### Paso 3: Generar Múltiples Escenarios con Wan 2.1

Utiliza los scripts proporcionados para generar videos en diferentes escenarios:

#### Escenarios Sugeridos

1. **Escenario deportivo**: Producto en contexto de actividad física
2. **Escenario doméstico**: Producto en ambiente hogareño
3. **Escenario profesional**: Producto en oficina o entorno laboral
4. **Variación de iluminación**: Mismo contexto con diferente iluminación (día/noche)
5. **Variación de fondo**: Producto en diferentes fondos manteniendo otras condiciones

#### Uso de los Scripts

**Generación básica (I2V)**:

```bash
python generar_video.py --modo i2v \
    --imagen_referencia recursos/ejemplo_producto.png \
    --prompt "El producto Sparkle en una mesa de oficina, iluminación natural" \
    --salida resultados/escenario_oficina.mp4
```

**Generación avanzada (MV2V)**:

```bash
python generar_video_con_mascara.py \
    --video_base video_base.mp4 \
    --mascara mascara_producto.png \
    --prompt "Mantener el producto Sparkle consistente mientras el fondo cambia" \
    --salida resultados/escenario_editado.mp4
```

### Paso 4: Analizar Consistencia del Producto

Para cada video generado, evalúa:

- **Consistencia de color**: ¿El color del producto se mantiene constante?
- **Consistencia de forma**: ¿La forma y proporciones se preservan?
- **Consistencia de marca/logo**: ¿Los elementos distintivos (logos, texto) se mantienen?
- **Coherencia temporal**: ¿El producto se anima de manera natural?
- **Artefactos visuales**: ¿Aparecen distorsiones, duplicaciones o errores?

Crea una tabla comparativa con estas métricas para cada escenario.

### Paso 5: Redactar Informe y Entregar Resultados

Utiliza la plantilla proporcionada (`recursos/plantilla_reporte.docx`) para estructurar tu informe. Incluye:

1. **Descripción del producto y escenarios**: Detalle del producto y justificación de escenarios seleccionados
2. **Prompts utilizados**: Todos los prompts empleados con explicación de decisiones
3. **Resultados**: Frames clave de cada video o enlaces a videos completos
4. **Análisis de consistencia**: Tabla comparativa y discusión de resultados
5. **Reflexión final**: Conclusiones sobre capacidades y limitaciones del modelo

## Instrucciones Detalladas de Uso de Scripts

### Script: `generar_video.py`

Este script permite generar videos usando los modos T2V (texto a video) o I2V (imagen a video).

**Argumentos**:

- `--modo`: Modo de generación (`t2v` o `i2v`)
- `--prompt`: Descripción textual del video deseado
- `--imagen_referencia`: Ruta a imagen de referencia (requerido para I2V)
- `--salida`: Ruta de salida para el video generado
- `--resolucion`: Resolución del video (por defecto: `832x480`)

**Ejemplo T2V**:

```bash
python generar_video.py --modo t2v \
    --prompt "Una lata de refresco azul sobre una mesa de madera, iluminación suave" \
    --salida resultados/video_t2v.mp4
```

**Ejemplo I2V**:

```bash
python generar_video.py --modo i2v \
    --imagen_referencia mi_producto.png \
    --prompt "La lata de refresco rotando lentamente sobre la mesa" \
    --salida resultados/video_i2v.mp4
```

### Script: `generar_video_con_mascara.py`

Este script permite editar videos usando máscaras para mantener consistencia del producto.

**Argumentos**:

- `--video_base`: Video inicial que se va a editar
- `--mascara`: Imagen de máscara (regiones blancas se mantienen, negras se editan)
- `--prompt`: Instrucciones de edición
- `--salida`: Ruta de salida para el video editado

**Ejemplo**:

```bash
python generar_video_con_mascara.py \
    --video_base video_original.mp4 \
    --mascara mascara_producto.png \
    --prompt "Cambiar el fondo a una playa mientras se mantiene el producto idéntico" \
    --salida resultados/video_editado.mp4
```

## Consejos sobre Ingeniería de Prompts

### Estructura de Prompts Efectivos

1. **Descripción base del producto**: Siempre incluye características visuales clave

   - Ejemplo: "Lata de refresco Sparkle, azul brillante con logo blanco en el centro"
2. **Contexto del escenario**: Describe el entorno donde aparece el producto

   - Ejemplo: "sobre una mesa de oficina moderna"
3. **Condiciones de iluminación**: Especifica iluminación si es relevante

   - Ejemplo: "iluminación natural de ventana, sombras suaves"
4. **Acción o animación**: Describe el movimiento deseado

   - Ejemplo: "rotando lentamente", "permaneciendo estático"

### Mantenimiento de Consistencia

- **Usa la misma descripción base del producto** en todos los prompts
- **Mantén características distintivas** (color, logo, forma) consistentes en la descripción
- **Varía el contexto y escenario**, no las características del producto
- **Revisa el archivo `ejemplo_prompts.txt`** para más ejemplos estructurados

### Ejemplos de Prompts por Escenario

Ver archivo `codigo/ejemplo_prompts.txt` para ejemplos detallados y estructurados.

### Limitaciones y Sesgos

- Los modelos pueden generar contenido con sesgos presentes en los datos de entrenamiento
- Pueden reproducir estereotipos o representaciones problemáticas
- La calidad puede variar significativamente según el prompt y contexto

### Reflexión en el Informe

Incluye una sección en tu informe reflexionando sobre:

- Implicaciones del uso de estos modelos en la industria
- Limitaciones éticas identificadas
- Recomendaciones para uso responsable

## Solución de Problemas Comunes

### Error de Memoria (OOM)

Si encuentras errores de memoria insuficiente:

1. Usa el modelo T2V-1.3B en lugar del 14B
2. Reduce la resolución de salida
3. Activa optimizaciones: `--offload_model True --t5_cpu`

### Generación Lenta

- Es normal en GPUs de menor capacidad (15-30 minutos por video)
- Considera usar servicios cloud con GPU más potente
- Reduce el número de frames generados si es posible

### Resultados Inconsistentes

- Experimenta con diferentes prompts
- Ajusta parámetros de guidance scale y steps
- Considera usar MV2V para mayor control sobre la consistencia

## Recursos Adicionales

- **Documentación oficial de Wan 2.1**: [https://github.com/Wan-Video/Wan2.1](https://github.com/Wan-Video/Wan2.1)
- **Repositorio en Hugging Face**: [https://huggingface.co/Wan-AI/Wan2.1-T2V-14B](https://huggingface.co/Wan-AI/Wan2.1-T2V-14B)
- **Ejemplos de la comunidad**: Explora los Spaces de Hugging Face para inspiración

## Entrega

La entrega debe incluir:

1. **Carpeta `resultados/`**: Contiene todos los videos generados
2. **Informe final**: Documento Word usando la plantilla proporcionada
3. **Código modificado**
4. **Imagen de referencia**: Archivo de la imagen del producto utilizada

**Formato de entrega**: ZIP o carpeta compartida con nombre `Apellido_Nombre_TareaWan2.1.zip`

## Fecha de Entrega

Consultar con el instructor la fecha límite de entrega.
