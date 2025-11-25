Te relleno todo el punto 5 para que puedas copiar-pegar directamente:

---

## 5. Reflexión Final

### 5.1. Capacidades del Modelo

A lo largo de la práctica he comprobado que Wan 2.1 es muy potente generando **escenas cinematográficas** con buena composición, profundidad de campo y manejo de la luz. En los escenarios T2V (terraza y ciudad nocturna) el modelo produce fondos complejos, con bokeh, neones, tráfico en movimiento y reflejos dinámicos que resultan muy atractivos visualmente.
En modo I2V, su principal fortaleza es la **fidelidad al producto de referencia**: mantiene con mucha precisión la forma cilíndrica, el material metálico y, sobre todo, el logo, incluso cuando cambia la iluminación (cocina vs oficina). En general, el modelo se desempeña mejor cuando:

* Tiene una **imagen de referencia clara** (I2V).
* El producto es el foco principal y el movimiento de cámara es moderado.
* Hay que generar **publicidad estática o semidinámica** donde la prioridad es respetar el diseño del objeto.

---

### 5.2. Limitaciones Identificadas

La limitación más importante observada es la **inconsistencia en el texto y la marca** cuando se trabaja solo con T2V: el logo nunca se reproduce correctamente y las letras cambian entre frames. Además, con T2V la **geometría del objeto rígido** (la lata) tiende a deformarse: bases abombadas, cambios de ancho y variaciones de escala no explicadas por la cámara.
También se aprecian problemas de **estabilidad temporal** en detalles finos: los reflejos cambian de forma brusca y el tamaño relativo de la lata fluctúa, especialmente en la ciudad nocturna. Estas limitaciones se agravan cuando:

* El fondo es muy complejo o tiene muchas fuentes de luz en movimiento.
* El texto es pequeño y se coloca sobre una superficie curva.
* El prompt exige mucho dinamismo de cámara sin aportar una referencia visual.

---

### 5.3. Aprendizajes sobre Ingeniería de Prompts

De la práctica saco varias lecciones claras de prompt engineering:

1. **Detalle por encima de brevedad**: los prompts largos y específicos (color exacto, tipo de iluminación, textura, movimiento de cámara) producen resultados mucho más controlados que descripciones genéricas como “lata dorada en un gimnasio”.
2. **Estructurar el prompt en capas**: primero describir el producto (forma, material, logo), después el entorno y por último el tipo de movimiento. Esta estructura ayuda al modelo a “anclar” la identidad del objeto antes de añadir complejidad.
3. **La iluminación es clave**: especificar si la luz es cálida, fría, natural, de neón, etc., reduce variaciones indeseadas en el color del metal.
4. **I2V como herramienta de corrección**: cuando T2V no mantiene la forma o la marca, usar una imagen de referencia y pasar a I2V es una forma muy eficaz de recuperar la consistencia.
5. **Dinamismo vs fidelidad**: pedir demasiados movimientos de cámara y elementos móviles hace que el modelo sacrifi que precisión en el producto; conviene equilibrar ambos objetivos según la tarea.

A otros usuarios les recomendaría **reutilizar siempre una descripción base del producto**, iterar gradualmente (cambiar solo un elemento por vez) y combinar T2V e I2V según si priorizan creatividad del entorno o exactitud del objeto.

---

### 5.4. Aplicaciones Prácticas

Esta práctica muestra que Wan 2.1 ya es útil para varias aplicaciones reales:

* **Previsualización rápida de anuncios de producto**: generar propuestas visuales para campañas de marketing (distintos entornos, luces y moods) sin necesidad de rodar todavía un spot real.
* **Storyboards y moodboards en vídeo**: crear clips cortos que transmitan la atmósfera de un anuncio (gimnasio, ciudad nocturna, oficina, etc.) para presentaciones internas o a clientes.
* **Exploración de branding**: probar cómo se vería un mismo producto en diferentes contextos (doméstico, corporativo, urbano) antes de decidir una línea creativa.

Sin embargo, para un uso en **producción comercial real** serían necesarias mejoras importantes:

* Mayor **consistencia geométrica** de objetos rígidos a lo largo del tiempo.
* Capacidad de reproducir **logos y tipografías exactas** (por ejemplo, usando guías de texto o capas editables).
* Mejor control sobre la **escala relativa y el tracking** del producto dentro del plano.

En resumen, Wan 2.1 es una herramienta muy prometedora para la **fase creativa y de prototipado** en publicidad y contenido audiovisual, pero todavía requiere supervisión humana y retoque posterior para cumplir los estándares de un anuncio profesional completamente acabado.

---
