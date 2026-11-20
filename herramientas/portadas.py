"""Genera una imagen liviana de la portada de cada guía.

Para cada archivo en guias/<curso>/<asignatura>/ crea
portadas/<curso>/<asignatura>/<nombre>.jpg con la primera página.
Solo crea las que faltan (o las rehace si la guía es más nueva).
Uso:  python herramientas/portadas.py
"""
import os, sys, io
import pymupdf
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCHO = 600          # px de ancho de la portada
CALIDAD = 82         # calidad JPEG
IMAGENES = (".jpg", ".jpeg", ".png")


def primera_pagina(ruta):
    ext = os.path.splitext(ruta)[1].lower()
    if ext == ".pdf":
        doc = pymupdf.open(ruta)
        pag = doc[0]
        pix = pag.get_pixmap(matrix=pymupdf.Matrix(ANCHO / pag.rect.width, ANCHO / pag.rect.width))
        return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    if ext in IMAGENES:
        img = Image.open(ruta).convert("RGB")
        img.thumbnail((ANCHO, ANCHO * 3))
        return img
    return None


def main():
    hechas = 0
    base = os.path.join(RAIZ, "guias")
    for carpeta, _, archivos in os.walk(base):
        for nombre in archivos:
            origen = os.path.join(carpeta, nombre)
            rel = os.path.relpath(origen, base)
            destino = os.path.join(RAIZ, "portadas", os.path.splitext(rel)[0] + ".jpg")
            if os.path.exists(destino) and os.path.getmtime(destino) >= os.path.getmtime(origen):
                continue
            img = primera_pagina(origen)
            if img is None:
                continue
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            img.save(destino, "JPEG", quality=CALIDAD, optimize=True, progressive=True)
            hechas += 1
            print(f"portada: {rel}  ({os.path.getsize(destino) // 1024} KB)")
    # borrar portadas de guías que ya no existen
    for carpeta, _, archivos in os.walk(os.path.join(RAIZ, "portadas")):
        for nombre in archivos:
            rel = os.path.relpath(os.path.join(carpeta, nombre), os.path.join(RAIZ, "portadas"))
            sin_ext = os.path.splitext(rel)[0]
            existe = any(os.path.exists(os.path.join(base, sin_ext + e)) for e in (".pdf",) + IMAGENES + tuple(e.upper() for e in (".pdf",) + IMAGENES))
            if not existe:
                os.remove(os.path.join(carpeta, nombre))
                print(f"borrada portada huérfana: {rel}")
    print(f"listo, {hechas} portada(s) nueva(s)")


if __name__ == "__main__":
    sys.exit(main())
