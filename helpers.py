import re

def extract_chapters(form_dict, chapter_field):
    """
    Extrae los capítulos y las partidas a partir del diccionario del formulario.

    :param form_dict: Diccionario obtenido de request.form.to_dict(flat=False)
    :param chapter_field: Nombre del campo del capítulo (por ejemplo, "tipo" en presupuestos o "descripcion" en hojas de trabajo)
    :return: Diccionario con la estructura:
             {cap_idx: {chapter_field: valor, "partidas": [lista de partidas dict]}}
    """
    chapters = {}
    # Extraer capítulos
    chapter_pattern = re.compile(r'capitulos\[(\d+)\]\[' + chapter_field + r'\]')
    for key, value in form_dict.items():
        m = chapter_pattern.match(key)
        if m:
            cap_idx = m.group(1)
            chapters[cap_idx] = {chapter_field: value[0], "partidas": {}}
    # Extraer partidas (asociadas al capítulo)
    partida_pattern = re.compile(r'capitulos\[(\d+)\]\[partidas\]\[(\d+)\]\[([^\]]+)\]')
    for key, value in form_dict.items():
        m = partida_pattern.match(key)
        if m:
            cap_idx = m.group(1)
            part_idx = m.group(2)
            field = m.group(3)
            if cap_idx in chapters:
                if part_idx not in chapters[cap_idx]["partidas"]:
                    chapters[cap_idx]["partidas"][part_idx] = {}
                chapters[cap_idx]["partidas"][part_idx][field] = value[0]
    # Convertir el diccionario de partidas en una lista ordenada
    for cap_idx in chapters:
        parts = chapters[cap_idx]["partidas"]
        chapters[cap_idx]["partidas"] = [parts[k] for k in sorted(parts, key=lambda x: int(x))]
    return chapters
