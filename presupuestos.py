from flask import Blueprint, render_template, request, redirect, url_for, flash
from dbhelper import DBHelper
from datetime import datetime
import re

presupuestos_bp = Blueprint("presupuestos_bp", __name__)
db = DBHelper()

def generar_referencia_presupuesto(proyecto_id):
    fecha = datetime.now().strftime("%d%m%y")
    tipo = db.execute_query("SELECT tipo_proyecto FROM proyectos WHERE id = ?", (proyecto_id,), fetchone=True)
    if tipo:
        tipo_proyecto = tipo[0]
        letras = (tipo_proyecto[0] + tipo_proyecto[2] + tipo_proyecto[4]).upper() if len(tipo_proyecto) >= 5 else tipo_proyecto[:3].upper()
    else:
        letras = "XXX"
    base_ref = f"PR{int(proyecto_id):03d}{letras}-{fecha}-"
    similares = db.execute_query("SELECT referencia FROM presupuestos WHERE referencia LIKE ?", (f"{base_ref}%",), fetch=True)
    sufijo = f"{len(similares) + 1:02d}"
    return base_ref + sufijo

@presupuestos_bp.route("/presupuestos")
def listar_presupuestos():
    presupuestos = db.execute_query("""
        SELECT p.id, p.referencia, p.fecha, cl.nombre, pr.tipo_proyecto, pr.nombre_proyecto,
               p.tecnico_encargado, p.aprobacion, p.fecha_aprobacion, p.estado
        FROM presupuestos p
        JOIN proyectos pr ON p.id_proyecto = pr.id
        JOIN clientes cl ON pr.id_cliente = cl.id
        ORDER BY p.id DESC
    """, fetch=True)
    return render_template("presupuestos_list.html", presupuestos=presupuestos)

@presupuestos_bp.route("/presupuestos/nuevo", methods=["GET", "POST"])
def nuevo_presupuesto():
    proyectos = db.execute_query("SELECT id, nombre_proyecto FROM proyectos", fetch=True)
    datos_proyecto = {}
    proyecto_id_param = request.args.get("proyecto_id")
    if proyecto_id_param:
        proyecto_info = db.execute_query("""
            SELECT pr.nombre_proyecto, pr.calle, pr.nombre_via, pr.numero, pr.puerta,
                   pr.codigo_postal, pr.poblacion, cl.nombre
            FROM proyectos pr
            JOIN clientes cl ON pr.id_cliente = cl.id
            WHERE pr.id = ?
        """, (proyecto_id_param,), fetchone=True)
        if proyecto_info:
            datos_proyecto = {
                "titulo": proyecto_info[0],
                "tipo_via": proyecto_info[1],
                "nombre_via": proyecto_info[2],
                "numero_via": proyecto_info[3],
                "puerta": proyecto_info[4],
                "codigo_postal": proyecto_info[5],
                "poblacion": proyecto_info[6],
                "cliente_nombre": proyecto_info[7],
                "referencia": generar_referencia_presupuesto(proyecto_id_param),
                "proyecto_id": proyecto_id_param,
                "proyecto_nombre": proyecto_info[0]
            }
    if request.method == "POST":
        proyecto_id = request.form.get("proyecto_id")
        titulo = request.form.get("titulo")
        tipo_via = request.form.get("tipo_via")
        nombre_via = request.form.get("nombre_via")
        numero_via = request.form.get("numero_via")
        puerta = request.form.get("puerta")
        codigo_postal = request.form.get("codigo_postal")
        poblacion = request.form.get("poblacion")
        notas = request.form.get("notas")
        fecha = datetime.now().strftime("%Y-%m-%d")
        referencia = generar_referencia_presupuesto(proyecto_id)

        presupuesto_id = db.execute_query("""
            INSERT INTO presupuestos (
                id_proyecto, referencia, fecha, tipo_via, nombre_via, numero_via, puerta,
                codigo_postal, poblacion, titulo, notas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (proyecto_id, referencia, fecha, tipo_via, nombre_via, numero_via, puerta, codigo_postal, poblacion, titulo, notas))

        # Extraer capítulos y partidas del formulario usando el índice de partida
        form_dict = request.form.to_dict(flat=False)
        chapters = {}
        chapter_pattern = re.compile(r'capitulos\[(\d+)\]\[tipo\]')
        for key, values in form_dict.items():
            m = chapter_pattern.match(key)
            if m:
                cap_idx = m.group(1)
                chapters[cap_idx] = {'tipo': values[0], 'partidas': []}
        partida_pattern = re.compile(r'capitulos\[(\d+)\]\[partidas\]\[(\d+)\]\[([^\]]+)\]')
        partidas_group = {}
        for key, values in form_dict.items():
            m = partida_pattern.match(key)
            if m:
                cap_idx = m.group(1)
                part_idx = m.group(2)
                field = m.group(3)
                if cap_idx not in partidas_group:
                    partidas_group[cap_idx] = {}
                if part_idx not in partidas_group[cap_idx]:
                    partidas_group[cap_idx][part_idx] = {}
                partidas_group[cap_idx][part_idx][field] = values[0]
        # Asignar las partidas a cada capítulo ordenándolas por su índice
        for cap_idx, parts in partidas_group.items():
            if cap_idx in chapters:
                for part_idx in sorted(parts.keys(), key=int):
                    chapters[cap_idx]['partidas'].append(parts[part_idx])
        
        for cap_idx, chapter in chapters.items():
            chapter_number = str(int(cap_idx) + 1)
            db.execute_query("""
                INSERT INTO capitulos (id_presupuesto, numero, descripcion)
                VALUES (?, ?, ?)
            """, (presupuesto_id, chapter_number, chapter['tipo']))
            for i, partida in enumerate(chapter['partidas']):
                cap_num = f"{chapter_number}.{i+1}"
                cantidad = float(partida.get('cantidad') or 0)
                precio = float(partida.get('precio') or 0)
                total = float(partida.get('total') or 0)
                margen = float(partida.get('margen') or 40)
                final = total * (1 + margen / 100)
                db.execute_query("""
                    INSERT INTO partidas (id_presupuesto, capitulo_numero, descripcion, unitario, cantidad, precio, total, margen, final)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    presupuesto_id, cap_num, partida.get('descripcion'),
                    partida.get('unitario'),
                    cantidad,
                    precio,
                    total,
                    margen,
                    final
                ))
                
        flash(f"Presupuesto creado correctamente. Referencia: {referencia}", "success")
        return redirect(url_for("presupuestos_bp.listar_presupuestos"))
    
    return render_template("presupuesto_nuevo.html", proyectos=proyectos, **datos_proyecto)

@presupuestos_bp.route("/presupuestos/editar/<int:id>", methods=["GET", "POST"])
def editar_presupuesto(id):
    presupuesto = db.execute_query("SELECT * FROM presupuestos WHERE id = ?", (id,), fetchone=True)
    if request.method == "POST":
        titulo = request.form.get("titulo")
        tipo_via = request.form.get("tipo_via")
        nombre_via = request.form.get("nombre_via")
        numero_via = request.form.get("numero_via")
        puerta = request.form.get("puerta")
        codigo_postal = request.form.get("codigo_postal")
        poblacion = request.form.get("poblacion")
        notas = request.form.get("notas")
        
        db.execute_query("""
            UPDATE presupuestos SET
                titulo = ?, tipo_via = ?, nombre_via = ?, numero_via = ?, puerta = ?,
                codigo_postal = ?, poblacion = ?, notas = ?
            WHERE id = ?
        """, (titulo, tipo_via, nombre_via, numero_via, puerta, codigo_postal, poblacion, notas, id))
        
        # Eliminar capítulos y partidas existentes para este presupuesto
        db.execute_query("DELETE FROM capitulos WHERE id_presupuesto = ?", (id,))
        db.execute_query("DELETE FROM partidas WHERE id_presupuesto = ?", (id,))
        
        # Extraer los nuevos capítulos y partidas del formulario
        form_dict = request.form.to_dict(flat=False)
        chapters = {}
        chapter_pattern = re.compile(r'capitulos\[(\d+)\]\[tipo\]')
        for key, values in form_dict.items():
            m = chapter_pattern.match(key)
            if m:
                cap_idx = m.group(1)
                chapters[cap_idx] = {'tipo': values[0], 'partidas': []}
        partida_pattern = re.compile(r'capitulos\[(\d+)\]\[partidas\]\[(\d+)\]\[([^\]]+)\]')
        partidas_group = {}
        for key, values in form_dict.items():
            m = partida_pattern.match(key)
            if m:
                cap_idx = m.group(1)
                part_idx = m.group(2)
                field = m.group(3)
                if cap_idx not in partidas_group:
                    partidas_group[cap_idx] = {}
                if part_idx not in partidas_group[cap_idx]:
                    partidas_group[cap_idx][part_idx] = {}
                partidas_group[cap_idx][part_idx][field] = values[0]
        for cap_idx, parts in partidas_group.items():
            if cap_idx in chapters:
                for part_idx in sorted(parts.keys(), key=int):
                    chapters[cap_idx]['partidas'].append(parts[part_idx])
        
        for cap_idx, chapter in chapters.items():
            chapter_number = str(int(cap_idx) + 1)
            db.execute_query("""
                INSERT INTO capitulos (id_presupuesto, numero, descripcion)
                VALUES (?, ?, ?)
            """, (id, chapter_number, chapter['tipo']))
            for i, partida in enumerate(chapter['partidas']):
                cap_num = f"{chapter_number}.{i+1}"
                cantidad = float(partida.get('cantidad') or 0)
                precio = float(partida.get('precio') or 0)
                total = float(partida.get('total') or 0)
                margen = float(partida.get('margen') or 40)
                final = total * (1 + margen / 100)
                db.execute_query("""
                    INSERT INTO partidas (id_presupuesto, capitulo_numero, descripcion, unitario, cantidad, precio, total, margen, final)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id, cap_num, partida.get('descripcion'),
                    partida.get('unitario'),
                    cantidad,
                    precio,
                    total,
                    margen,
                    final
                ))
                
        flash("Presupuesto actualizado correctamente.", "success")
        return redirect(url_for("presupuestos_bp.listar_presupuestos"))
    
    capitulos_rows = db.execute_query("SELECT * FROM capitulos WHERE id_presupuesto = ? ORDER BY id", (id,), fetch=True) or []
    capitulos = []
    for row in capitulos_rows:
         cap = dict(row)
         cap["tipo"] = cap["descripcion"]
         partidas_rows = db.execute_query(
             "SELECT * FROM partidas WHERE id_presupuesto = ? AND capitulo_numero LIKE ? ORDER BY id",
             (id, f"{cap['numero']}.%"), fetch=True
         ) or []
         cap["partidas"] = [dict(p) for p in partidas_rows]
         capitulos.append(cap)
    
    proyecto = db.execute_query("SELECT nombre_proyecto FROM proyectos WHERE id = ?", (presupuesto["id_proyecto"],), fetchone=True)
    proyecto_nombre = proyecto[0] if proyecto else ""
    
    return render_template("presupuesto_nuevo.html", presupuesto=presupuesto, capitulos=capitulos, proyecto_id=presupuesto["id_proyecto"], proyecto_nombre=proyecto_nombre)

@presupuestos_bp.route("/presupuestos/actualizar/<int:id>", methods=["POST"])
def actualizar_presupuesto_estado(id):
    tecnico = request.form.get("tecnico")
    aprobacion = request.form.get("aprobacion")
    fecha_aprobacion = request.form.get("fecha_aprobacion")
    estado = request.form.get("estado")
    db.execute_query("""
        UPDATE presupuestos SET 
            tecnico_encargado = ?, 
            aprobacion = ?, 
            fecha_aprobacion = ?, 
            estado = ?
        WHERE id = ?
    """, (tecnico, aprobacion, fecha_aprobacion, estado, id))
    return "OK"

@presupuestos_bp.route("/presupuestos/borrar/<int:id>", methods=["POST"])
def borrar_presupuesto(id):
    db.execute_query("DELETE FROM presupuestos WHERE id = ?", (id,))
    flash("Presupuesto borrado correctamente.", "success")
    return redirect(url_for("presupuestos_bp.listar_presupuestos"))

@presupuestos_bp.route("/presupuestos/clonar/<int:id>", methods=["POST"])
def clonar_presupuesto(id):
    original = db.execute_query("SELECT * FROM presupuestos WHERE id = ?", (id,), fetchone=True)
    if not original:
        flash("Presupuesto no encontrado.", "danger")
        return redirect(url_for("presupuestos_bp.listar_presupuestos"))
    
    # Extraer la referencia base quitando cualquier sufijo " Vn" previo
    base_ref = re.sub(r" V\d+$", "", original["referencia"])
    
    # Buscar clones que ya tengan esa base con versión
    clones = db.execute_query("SELECT referencia FROM presupuestos WHERE referencia LIKE ?", (f"{base_ref} V%",), fetch=True)
    if clones:
        versions = []
        for clone in clones:
            ref = clone["referencia"]
            m = re.search(r" V(\d+)$", ref)
            if m:
                try:
                    ver = int(m.group(1))
                    versions.append(ver)
                except ValueError:
                    pass
        new_version = max(versions) + 1 if versions else 2
    else:
        new_version = 2
        
    new_ref = f"{base_ref} V{new_version}"
    fecha = datetime.now().strftime("%Y-%m-%d")
    
    new_presupuesto_id = db.execute_query("""
        INSERT INTO presupuestos (
            id_proyecto, referencia, fecha, tipo_via, nombre_via, numero_via, puerta,
            codigo_postal, poblacion, titulo, notas
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        original["notas"]
    ))
    
    capitulos = db.execute_query("SELECT * FROM capitulos WHERE id_presupuesto = ? ORDER BY id", (id,), fetch=True)
    for cap in capitulos:
        db.execute_query("""
            INSERT INTO capitulos (id_presupuesto, numero, descripcion)
            VALUES (?, ?, ?)
        """, (new_presupuesto_id, cap["numero"], cap["descripcion"]))
        partidas = db.execute_query("SELECT * FROM partidas WHERE id_presupuesto = ? AND capitulo_numero LIKE ? ORDER BY id", (id, f"{cap['numero']}.%"), fetch=True)
        for part in partidas:
            db.execute_query("""
                INSERT INTO partidas (id_presupuesto, capitulo_numero, descripcion, unitario, cantidad, precio, total, margen, final)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_presupuesto_id,
                part["capitulo_numero"],
                part["descripcion"],
                part["unitario"],
                part["cantidad"],
                part["precio"],
                part["total"],
                part["margen"],
                part["final"]
            ))
    
    flash(f"Presupuesto clonado correctamente. Nueva referencia: {new_ref}", "success")
    return redirect(url_for("presupuestos_bp.listar_presupuestos"))
