def reemplazar_parametros(texto: str, parametros: dict) -> str:
    for clave, valor in parametros.items():
        texto = texto.replace(f"{{{{ {clave} }}}}", str(valor))
    return texto