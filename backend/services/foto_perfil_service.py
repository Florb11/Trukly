from io import BytesIO
from struct import error as StructError

from PIL import Image, UnidentifiedImageError

from src.Usuario import Usuario


def validar_contenido_foto(archivo):
    formatos = {"png": "PNG", "jpg": "JPEG", "jpeg": "JPEG", "webp": "WEBP"}
    extension = Usuario.obtener_extension_foto(archivo.filename)
    try:
        contenido = archivo.read(Usuario.TAMANIO_MAXIMO_FOTO_BYTES + 1)
        if len(contenido) > Usuario.TAMANIO_MAXIMO_FOTO_BYTES:
            return False, "La imagen no puede superar los 3 MB"
        with Image.open(BytesIO(contenido), formats=list(set(formatos.values()))) as imagen:
            if imagen.format != formatos.get(extension):
                return False, "El contenido de la imagen no coincide con su extensión"
            if imagen.width * imagen.height > 25_000_000:
                return False, "La imagen tiene dimensiones demasiado grandes. Elegí una foto de menor resolución."
            imagen.verify()
        # La identificación y las cabeceras no bastan: comprobar la decodificación.
        with Image.open(BytesIO(contenido), formats=list(set(formatos.values()))) as imagen:
            imagen.load()
        return True, None
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError, StructError, Image.DecompressionBombError):
        return False, "El archivo no es una imagen válida o está dañado"
    finally:
        archivo.seek(0)
