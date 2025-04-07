from flask import Blueprint, render_template, request, redirect, url_for, flash
from dbhelper import DBHelper
from datetime import datetime
import re

hojas_trabajo_bp = Blueprint("hojas_trabajo_bp", __name__)
db = DBHelper()

@hojas_trabajo_bp.route("/hojas_trabajo")
def listar_hojas():
    hojas = db.execute_query("""
        SELECT h.*, pr.nombre_proyecto, cl.nombre AS cliente,
            COALESCE(h.tecnico_encargado, 
                (SELECT tecnico_encargado FROM presupuestos WHERE id_proyecto = h.id_proyecto ORDER BY id DESC LIMIT 1)
            ) AS tecnico_encargado
        FROM hojas_trabajo h
        JOIN proyectos pr ON h.id_proyecto = pr.id
        JOIN clientes cl ON pr.id_cliente = cl.id
        ORDER BY h.id DESC
    """, fetch=True)
    return render_template("hojas_trabajo_list.html", hojas=hojas)


@hojas_trabajo_bp.route("/hojas_trabajo/nuevo", methods=["GET", "POST"])
def nuevo_hoja_trabajo():
    # Por el momento, se deja como stub; implementar según necesidades.
    flash("Funcionalidad de 'Nueva Hoja de Trabajo' aún no implementada.", "info")
    return redirect(url_for("hojas_trabajo_bp.listar_hojas"))

@hojas_trabajo_bp.route("/hojas_trabajo/editar/<int:id>", methods=["GET", "POST"])
def editar_hoja_trabajo(id):
    # Obtenemos la hoja de trabajo junto con datos del proyecto y cliente.
    hoja = db.execute_query("""
        SELECT h.*, pr.nombre_proyecto, cl.nombre AS cliente,
            COALESCE(h.tecnico_encargado, 
                (SELECT tecnico_encargado FROM presupuestos WHERE id_proyecto = h.id_proyecto ORDER BY id DESC LIMIT 1)
            ) AS tecnico_encargado
        FROM hojas_trabajo h
        JOIN proyectos pr ON h.id_proyecto = pr.id
        JOIN clientes cl ON pr.id_cliente = cl.id
        WHERE h.id = ?
    """, (id,), fetchone=True)

    if not hoja:
        flash("Hoja de trabajo no encontrada.", "danger")
        return redirect(url_for("hojas_trabajo_bp.listar_hojas"))
    
    if request.method == "POST":
        # Actualizamos el técnico encargado de la hoja
        tecnico_encargado = request.form.get("tecnico_encargado")
        db.execute_query("""
            UPDATE hojas_trabajo SET
                tecnico_encargado = ?
            WHERE id = ?
        """, (tecnico_encargado, id))
        
        # Actualización de capítulos y partidas:
        # Eliminamos capítulos y partidas actuales
        db.execute_query("DELETE FROM capitulos_hojas WHERE id_hoja = ?", (id,))
        db.execute_query("DELETE FROM partidas_hojas WHERE id_hoja = ?", (id,))
        
        # Obtenemos el diccionario completo del formulario
        form_dict = request.form.to_dict(flat=False)
        
        # Procesamos los capítulos. Se esperan claves del tipo:
        # capitulos[<índice>][descripcion]
        chapters = {}
        chapter_pattern = re.compile(r'^capitulos\[(\d+)\]\[descripcion\]$')
        for key, value in form_dict.items():
            m = chapter_pattern.match(key)
            if m:
                idx = m.group(1)
                chapters[idx] = {"descripcion": value[0], "partidas": {}}
        
        # Procesamos las partidas. Se esperan claves del tipo:
        # capitulos[<índice>][partidas][<índice>][campo]
        partida_pattern = re.compile(r'^capitulos\[(\d+)\]\[partidas\]\[(\d+)\]\[([^\]]+)\]$')
        for key, value in form_dict.items():
            m = partida_pattern.match(key)
            if m:
                chap_idx = m.group(1)
                part_idx = m.group(2)
                field = m.group(3)
                if chap_idx in chapters:
                    if part_idx not in chapters[chap_idx]["partidas"]:
                        chapters[chap_idx]["partidas"][part_idx] = {}
                    chapters[chap_idx]["partidas"][part_idx][field] = value[0]
        
        # Insertamos capítulos y partidas en las tablas correspondientes
        for chap_idx, chap_data in chapters.items():
            descripcion = chap_data["descripcion"]
            # Usamos el índice +1 como número de capítulo
            chapter_number = str(int(chap_idx) + 1)
            db.execute_query(
                "INSERT INTO capitulos_hojas (id_hoja, numero, descripcion) VALUES (?, ?, ?)",
                (id, chapter_number, descripcion)
            )
            for part_idx, part_data in chap_data["partidas"].items():
                # Definimos el número de partida como "capítulo.partida"
                partida_number = f"{chapter_number}.{int(part_idx)+1}"
                # Convertimos valores numéricos; si falla, se asigna 0
                cantidad = float(part_data.get("cantidad", 0) or 0)
                precio = float(part_data.get("precio", 0) or 0)
                total = float(part_data.get("total", 0) or 0)
                margen = float(part_data.get("margen", 0) or 0)
                final = float(part_data.get("final", 0) or 0)
                db.execute_query("""
                    INSERT INTO partidas_hojas 
                    (id_hoja, capitulo_numero, descripcion, unitario, cantidad, precio, total, margen, final)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id,
                    partida_number,
                    part_data.get("descripcion", ""),
                    part_data.get("unitario", ""),
                    cantidad,
                    precio,
                    total,
                    margen,
                    final
                ))
        
        flash("Hoja de trabajo actualizada correctamente.", "success")
        return redirect(url_for("hojas_trabajo_bp.listar_hojas"))
    
    # Para GET, recuperamos los capítulos y partidas ya existentes
    capitulos_rows = db.execute_query("SELECT * FROM capitulos_hojas WHERE id_hoja = ? ORDER BY id", (id,), fetch=True)
    capitulos = []
    for cap in capitulos_rows:
        cap_dict = dict(cap)
        cap_number = cap_dict.get("numero", "")
        partidas_rows = db.execute_query(
            "SELECT * FROM partidas_hojas WHERE id_hoja = ? AND capitulo_numero LIKE ? ORDER BY id",
            (id, f"{cap_number}.%"), fetch=True)
        cap_dict["partidas"] = [dict(p) for p in partidas_rows]
        capitulos.append(cap_dict)
    
    return render_template("hojas_trabajo_editar.html", hoja=hoja, capitulos=capitulos)

@hojas_trabajo_bp.route("/hojas_trabajo/borrar/<int:id>", methods=["POST"])
def borrar_hoja_trabajo(id):
    db.execute_query("DELETE FROM hojas_trabajo WHERE id = ?", (id,))
    flash("Hoja de trabajo borrada correctamente.", "success")
    return redirect(url_for("hojas_trabajo_bp.listar_hojas"))

@hojas_trabajo_bp.route("/hojas_trabajo/clonar/<int:id>", methods=["POST"])
def clonar_hoja_trabajo(id):
    # Clonar un presupuesto a hoja de trabajo.
    original = db.execute_query("SELECT * FROM presupuestos WHERE id = ?", (id,), fetchone=True)
    if not original:
        flash("Presupuesto no encontrado.", "danger")
        return redirect(url_for("presupuestos_bp.listar_presupuestos"))
    
    # Extraer la referencia base quitando cualquier sufijo " TRn"
    base_ref = re.sub(r" TR\d+$", "", original["referencia"])
    
    # Buscar hojas de trabajo con la misma base y extensión TR
    clones = db.execute_query("SELECT referencia FROM hojas_trabajo WHERE referencia LIKE ?", (f"{base_ref} TR%",), fetch=True)
    if clones:
        versions = []
        for clone in clones:
            ref = clone["referencia"]
            m = re.search(r" TR(\d+)$", ref)
            if m:
                try:
                    versions.append(int(m.group(1)))
                except ValueError:
                    pass
        new_version = max(versions) + 1 if versions else 1
    else:
        new_version = 1
        
    new_ref = f"{base_ref} TR{new_version}"
    fecha = datetime.now().strftime("%Y-%m-%d")
    
    new_hoja_id = db.execute_query("""
        INSERT INTO hojas_trabajo (
            id_proyecto, referencia, fecha, tipo_via, nombre_via, numero_via, puerta,
            codigo_postal, poblacion, titulo, notas, tecnico_encargado, aprobacion, fecha_aprobacion, estado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        original["id_proyecto"],
        new_ref,
        fecha,
        original["tipo_via"],
        original["nombre_via"],
        original["numero_via"],
        original["puerta"],
        original["codigo_postal"],
        original["poblacion"],
        original["titulo"],
        original["notas"],
        original["tecnico_encargado"],
        original["aprobacion"],
        original["fecha_aprobacion"],
        original["estado"]
    ))
    
    # Clonar capítulos y partidas a las nuevas tablas para hojas de trabajo.
    capitulos = db.execute_query("SELECT * FROM capitulos WHERE id_presupuesto = ? ORDER BY id", (id,), fetch=True)
    for cap in capitulos:
        db.execute_query("""
            INSERT INTO capitulos_hojas (id_hoja, numero, descripcion)
            VALUES (?, ?, ?)
        """, (new_hoja_id, cap["numero"], cap["descripcion"]))
        partidas = db.execute_query("SELECT * FROM partidas WHERE id_presupuesto = ? AND capitulo_numero LIKE ? ORDER BY id",
                                     (id, f"{cap['numero']}.%"), fetch=True)
        for part in partidas:
            db.execute_query("""
                INSERT INTO partidas_hojas (id_hoja, capitulo_numero, descripcion, unitario, cantidad, precio, total, margen, final)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_hoja_id,
                part["capitulo_numero"],
                part["descripcion"],
                part["unitario"],
                part["cantidad"],
                part["precio"],
                part["total"],
                part["margen"],
                part["final"]
            ))
    
    flash(f"Hoja de trabajo creada correctamente. Nueva referencia: {new_ref}", "success")
    return redirect(url_for("hojas_trabajo_bp.listar_hojas"))
