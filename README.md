# 🟥 Detector de Cuadrados por Color (Python + OpenCV)

Este proyecto permite detectar múltiples cuadrados de colores en imágenes, clasificarlos según su color y generar imágenes anotadas junto con un archivo resumen.

---

## 🚀 Características

* Detección de objetos geométricos (cuadrados)
* Clasificación automática por color:

  * rojo
  * verde
  * azul
  * amarillo
  * naranja
  * morado
* Generación de imágenes con contornos coloreados según la clase
* Exportación de resultados a CSV
* Procesamiento de múltiples imágenes

---

## 🧠 Cómo funciona

El sistema utiliza:

* **OpenCV** para procesamiento de imágenes
* Espacio de color **HSV** para detectar colores
* Detección de contornos para encontrar formas
* Filtrado geométrico para identificar cuadrados

Pasos:

1. Convertir imagen a HSV
2. Crear máscaras por color
3. Detectar contornos
4. Filtrar contornos con forma cuadrada
5. Clasificar según color
6. Dibujar resultados

---

## 📦 Instalación

Se recomienda usar **uv** (rápido y moderno):

```bash
uv pip install -r requirements_cuadrados.txt
```

O con pip clásico:

```bash
pip install -r requirements_cuadrados.txt
```

---

## ▶️ Uso

```bash
uv run detecta_cuadrados_color.py --input imagenes_cuadrados --output salida_cuadrados
```

Parámetros:

| Parámetro  | Descripción          |
| ---------- | -------------------- |
| `--input`  | Carpeta con imágenes |
| `--output` | Carpeta de salida    |

---

## 📁 Estructura del proyecto

```
proyecto/
├── detecta_cuadrados_color.py
├── requirements_cuadrados.txt
├── imagenes_cuadrados/
│   ├── cuadrados_1.png
│   ├── cuadrados_2.png
│   └── ...
```

---

## 📊 Resultados

Después de ejecutar:

```
salida_cuadrados/
├── imagenes_anotadas/
│   ├── anotada_cuadrados_1.png
│   └── ...
└── resumen_cuadrados.csv
```

### 📄 CSV generado

Ejemplo:

```
imagen,clase,x,y,ancho,alto
cuadrados_1.png,rojo,80,90,120,120
cuadrados_1.png,azul,470,90,140,140
```

---

## 🎨 Visualización

* Cada cuadrado detectado se dibuja con un contorno
* El color del contorno representa su clase
* Cuadrados de la misma clase → mismo color

---

## ⚠️ Limitaciones

* Solo detecta cuadrados (no rectángulos ni otras formas)
* Funciona mejor con:

  * colores bien definidos
  * fondo claro
  * poco ruido visual
* No es un modelo de IA, sino visión por computador clásica

---

## 🔧 Posibles mejoras

* Detectar otras formas (círculos, triángulos)
* Añadir interfaz gráfica
* Procesamiento en tiempo real (webcam)
* Entrenar modelo de deep learning

---

## 📚 Tecnologías usadas

* Python 3
* OpenCV
* NumPy

---

## 👨‍💻 Autor

Sofia Foguet Garcia

---

## ⭐ Contribuciones

Las contribuciones son bienvenidas. Puedes:

* abrir issues
* proponer mejoras
* hacer forks

---

## 📄 Licencia

Uso libre para fines educativos.
