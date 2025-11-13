from pathlib import Path
from typing import Union, Optional

def guardar_archivo(ruta_archivo: Union[str, Path], contenido: str, encoding: str = "utf-8") -> Path:
    ruta = Path(ruta_archivo)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido, encoding=encoding)
    return ruta

def leer_archivo(ruta_archivo: Union[str, Path], encoding: str = "utf-8", default_on_missing: Optional[str] = None) -> str:
    ruta = Path(ruta_archivo)
    if not ruta.exists():
        if default_on_missing is not None:
            return default_on_missing
        return "" #FileNotFoundError(f"Archivo no encontrado: {ruta}")
    result = ruta.read_text(encoding=encoding)
    return result