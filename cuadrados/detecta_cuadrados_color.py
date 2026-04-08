import argparse
import csv
from pathlib import Path

import cv2
import numpy as np


# ================================
# CONFIGURACIÓN DE COLORES
# ================================
# Definimos los rangos de colores en el espacio HSV.
# HSV es más robusto que RGB para segmentar colores.
# Cada color puede tener uno o varios rangos (ej: rojo tiene dos rangos).
CLASES_COLOR = {
    "rojo": [
        ((0, 100, 80), (10, 255, 255)),
        ((170, 100, 80), (180, 255, 255)),
    ],
    "verde": [
        ((35, 80, 80), (85, 255, 255)),
    ],
    "azul": [
        ((90, 80, 80), (130, 255, 255)),
    ],
    "amarillo": [
        ((20, 80, 80), (35, 255, 255)),
    ],
    "naranja": [
        ((11, 100, 80), (19, 255, 255)),
    ],
    "morado": [
        ((131, 70, 70), (165, 255, 255)),
    ],
}

# ================================
# COLORES PARA DIBUJAR CONTORNOS
# ================================
# Define el color (en BGR) con el que se dibujará cada clase detectada.
COLORES_CONTORNO = {
    "rojo": (0, 0, 255),
    "verde": (0, 180, 0),
    "azul": (255, 0, 0),
    "amarillo": (0, 255, 255),
    "naranja": (0, 140, 255),
    "morado": (180, 0, 180),
}

# ================================
# EXTENSIONES VÁLIDAS
# ================================
# Tipos de archivo de imagen que el programa aceptará.
EXTENSIONES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


# ================================
# FUNCIÓN: DETECTAR SI UN CONTORNO ES UN CUADRADO
# ================================
# Esta función analiza un contorno y decide si tiene forma de cuadrado:
# 1. Filtra por área mínima (evita ruido pequeño)
# 2. Aproxima la forma (debe tener 4 lados)
# 3. Comprueba que ancho y alto sean similares
def es_cuadrado(contorno, area_minima=800):
    area = cv2.contourArea(contorno)
    if area < area_minima:
        return False, None

    perimetro = cv2.arcLength(contorno, True)
    aproximado = cv2.approxPolyDP(contorno, 0.04 * perimetro, True)

    if len(aproximado) != 4:
        return False, None

    x, y, w, h = cv2.boundingRect(aproximado)
    if h == 0:
        return False, None

    relacion = w / float(h)
    if 0.80 <= relacion <= 1.20:
        return True, (x, y, w, h)

    return False, None


# ================================
# FUNCIÓN: GENERAR MÁSCARAS POR COLOR
# ================================
# Convierte la imagen HSV en varias máscaras binarias,
# una por cada color definido.
# También limpia ruido con operaciones morfológicas.
def mascaras_por_color(hsv):
    for clase, rangos in CLASES_COLOR.items():
        mascara_total = None

        for (h1, s1, v1), (h2, s2, v2) in rangos:
            mascara = cv2.inRange(
                hsv,
                np.array([h1, s1, v1], dtype=np.uint8),
                np.array([h2, s2, v2], dtype=np.uint8),
            )
            mascara_total = mascara if mascara_total is None else cv2.bitwise_or(mascara_total, mascara)

        # Limpieza de ruido
        kernel = np.ones((5, 5), np.uint8)
        mascara_total = cv2.morphologyEx(mascara_total, cv2.MORPH_OPEN, kernel)
        mascara_total = cv2.morphologyEx(mascara_total, cv2.MORPH_CLOSE, kernel)

        yield clase, mascara_total


# ================================
# FUNCIÓN: PROCESAR UNA IMAGEN
# ================================
# 1. Lee la imagen
# 2. Convierte a HSV
# 3. Detecta colores y contornos
# 4. Filtra cuadrados
# 5. Dibuja resultados y guarda imagen anotada
def procesar_imagen(imagen_path: Path, carpeta_anotadas: Path):
    imagen = cv2.imread(str(imagen_path))
    if imagen is None:
        raise ValueError(f"No se pudo leer la imagen: {imagen_path}")

    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    imagen_anotada = imagen.copy()
    detecciones = []

    for clase, mascara in mascaras_por_color(hsv):
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contorno in contornos:
            valido, caja = es_cuadrado(contorno)
            if not valido:
                continue

            x, y, w, h = caja
            color_bgr = COLORES_CONTORNO[clase]

            # Dibujar rectángulo
            cv2.rectangle(imagen_anotada, (x, y), (x + w, y + h), color_bgr, 3)

            # Escribir etiqueta
            cv2.putText(
                imagen_anotada,
                clase,
                (x, max(y - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color_bgr,
                2,
                cv2.LINE_AA,
            )

            # Guardar detección
            detecciones.append({
                "imagen": imagen_path.name,
                "clase": clase,
                "x": x,
                "y": y,
                "ancho": w,
                "alto": h,
            })

    salida_imagen = carpeta_anotadas / f"anotada_{imagen_path.name}"
    cv2.imwrite(str(salida_imagen), imagen_anotada)

    return detecciones, salida_imagen


# ================================
# FUNCIÓN: PROCESAR TODAS LAS IMÁGENES
# ================================
# Recorre una carpeta:
# - Procesa cada imagen
# - Cuenta detecciones
# - Guarda resultados en CSV
def procesar_imagenes(carpeta_entrada: Path, carpeta_salida: Path):
    imagenes = sorted([p for p in carpeta_entrada.iterdir() if p.suffix.lower() in EXTENSIONES])

    if not imagenes:
        raise FileNotFoundError(
            f"No se encontraron imágenes en {carpeta_entrada}. "
            "Añade imágenes .jpg, .jpeg, .png, .bmp o .webp"
        )

    carpeta_salida.mkdir(parents=True, exist_ok=True)
    carpeta_anotadas = carpeta_salida / "imagenes_anotadas"
    carpeta_anotadas.mkdir(exist_ok=True)

    filas_csv = []

    print("Procesando imágenes...")
    for imagen_path in imagenes:
        detecciones, salida_imagen = procesar_imagen(imagen_path, carpeta_anotadas)

        print(f"\n{imagen_path.name}")

        if detecciones:
            conteo = {}
            for det in detecciones:
                conteo[det["clase"]] = conteo.get(det["clase"], 0) + 1
                filas_csv.append(det)

            for clase, cantidad in sorted(conteo.items()):
                print(f"  - {clase}: {cantidad}")
        else:
            print("  - No se encontraron cuadrados de color")
            filas_csv.append({
                "imagen": imagen_path.name,
                "clase": "sin_detecciones",
                "x": "",
                "y": "",
                "ancho": "",
                "alto": "",
            })

        print(f"  - Imagen anotada: {salida_imagen}")

    # Guardar CSV
    csv_path = carpeta_salida / "resumen_cuadrados.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["imagen", "clase", "x", "y", "ancho", "alto"])
        writer.writeheader()
        writer.writerows(filas_csv)

    print(f"\nCSV guardado en: {csv_path}")
    print(f"Imágenes anotadas guardadas en: {carpeta_anotadas}")


# ================================
# FUNCIÓN PRINCIPAL (ENTRY POINT)
# ================================
# Maneja argumentos desde la terminal y lanza el procesamiento.
def main():
    parser = argparse.ArgumentParser(
        description="Detecta cuadrados de colores y los clasifica según su color."
    )
    parser.add_argument("--input", default="imagenes_cuadrados", help="Carpeta con imágenes de entrada")
    parser.add_argument("--output", default="salida_cuadrados", help="Carpeta de salida")
    args = parser.parse_args()

    procesar_imagenes(Path(args.input), Path(args.output))


# ================================
# EJECUCIÓN DEL SCRIPT
# ================================
# Este bloque hace que el script se ejecute solo si lo llamas directamente.
if __name__ == "__main__":
    main()