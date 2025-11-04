from pathlib import Path
from typing import Union

def guardar_archivo(ruta_archivo: Union[str, Path], contenido: str, encoding: str = "utf-8") -> Path:
    ruta = Path(ruta_archivo)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido, encoding=encoding)
    return ruta