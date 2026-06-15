import html

# Req. 7 - Protección XSS: usa html.escape() de stdlib para escapar caracteres peligrosos.
# Previene que el usuario inyecte <script>, <img onerror>, etc. en los datos almacenados.
def sanitize(text):
    if not isinstance(text, str):
        return text
    return html.escape(text, quote=True)
