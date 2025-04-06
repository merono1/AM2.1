from flask import Blueprint, render_template, request, redirect, url_for, flash
from dbhelper import DBHelper
from datetime import datetime

proyectos_bp = Blueprint("proyectos_bp", __name__)
db = DBHelper()

def generar_referencia(id_cliente, tipo_proyecto):
    fecha = datetime.now().strftime("%d%m%y")
    cli = f"{int(id_cliente):03d}"
    letras = (tipo_proyecto[0] + tipo_proyecto[2] + tipo_proyecto[4]).upper() if len(tipo_proyecto) >= 5 else tipo_proyecto[:3].upper()
    base_ref = f"{cli}{letras}{fecha}"

    similares = db.execute_query("""
        SELECT referencia FROM proyectos WHERE referencia LIKE ?
    """, (f"{base_ref}%",), fetch=True)

    sufijo = f"{len(similares) + 1:02d}"
    return base_ref + sufijo

@proyectos_bp.route("/proyectos", endpoint="listar_proyectos")
def listar_proyectos():
    proyectos = db.execute_query("""
        SELECT pr.id, cl.nombre, pr.tipo_proyecto, pr.nombre_proyecto, pr.calle,
               pr.nombre_via, pr.numero, pr.puerta, pr.poblacion,
               pr.fecha_creacion, pr.referencia
        FROM proyectos pr
        JOIN clientes cl ON pr.id_cliente = cl.id
        ORDER BY pr.id DESC
    """, fetch=True)
    return render_template("proyectos_list.html", proyectos=proyectos)

@proyectos_bp.route("/proyectos/nuevo", methods=["GET", "POST"])
def nuevo_proyecto():
    clientes = db.execute_query("SELECT id, nombre FROM clientes", fetch=True)
    if request.method == "POST":
        id_cliente = request.form.get("id_cliente")
        tipo_proyecto = request.form.get("tipo_proyecto")
        nombre_proyecto = request.form.get("nombre_proyecto")
        calle = request.form.get("calle")
        nombre_via = request.form.get("nombre_via")
        numero = request.form.get("numero")
        puerta = request.form.get("puerta")
        codigo_postal = request.form.get("codigo_postal")
        poblacion = request.form.get("poblacion")
        fecha_creacion = datetime.now().strftime("%Y-%m-%d")

        if not id_cliente or not nombre_proyecto or not tipo_proyecto:
            flash("Cliente, tipo y nombre del proyecto son obligatorios.", "danger")
            return render_template("proyectos_nuevo.html", clientes=clientes)

        referencia = generar_referencia(id_cliente, tipo_proyecto)

        db.execute_query("""
            INSERT INTO proyectos (
                id_cliente, tipo_proyecto, nombre_proyecto, calle, nombre_via, numero,
                puerta, codigo_postal, poblacion, referencia, fecha_creacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_cliente, tipo_proyecto, nombre_proyecto, calle, nombre_via, numero,
              puerta, codigo_postal, poblacion, referencia, fecha_creacion))

        flash(f"Proyecto creado correctamente. Referencia: {referencia}", "success")
        return redirect(url_for("proyectos_bp.listar_proyectos"))

    return render_template("proyectos_nuevo.html", clientes=clientes)

@proyectos_bp.route("/proyectos/nuevo/<int:cliente_id>", methods=["GET", "POST"])
def nuevo_proyecto_cliente(cliente_id):
    clientes = db.execute_query("SELECT id, nombre FROM clientes", fetch=True)
    cliente = db.execute_query("SELECT nombre FROM clientes WHERE id = ?", (cliente_id,), fetchone=True)
    cliente_nombre = cliente[0] if cliente else ""

    if request.method == "POST":
        tipo_proyecto = request.form.get("tipo_proyecto")
        nombre_proyecto = request.form.get("nombre_proyecto")
        calle = request.form.get("calle")
        nombre_via = request.form.get("nombre_via")
        numero = request.form.get("numero")
        puerta = request.form.get("puerta")
        codigo_postal = request.form.get("codigo_postal")
        poblacion = request.form.get("poblacion")
        fecha_creacion = datetime.now().strftime("%Y-%m-%d")

        if not tipo_proyecto or not nombre_proyecto:
            flash("Nombre y tipo del proyecto son obligatorios.", "danger")
            return render_template("proyectos_nuevo.html", cliente_id=cliente_id, cliente_nombre=cliente_nombre, clientes=clientes)

        referencia = generar_referencia(cliente_id, tipo_proyecto)

        db.execute_query("""
            INSERT INTO proyectos (
                id_cliente, tipo_proyecto, nombre_proyecto, calle, nombre_via, numero,
                puerta, codigo_postal, poblacion, referencia, fecha_creacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cliente_id, tipo_proyecto, nombre_proyecto, calle, nombre_via, numero,
              puerta, codigo_postal, poblacion, referencia, fecha_creacion))

        flash(f"Proyecto creado correctamente. Referencia: {referencia}", "success")
        return redirect(url_for("proyectos_bp.listar_proyectos"))

    return render_template("proyectos_nuevo.html", cliente_id=cliente_id, cliente_nombre=cliente_nombre, clientes=clientes)
# Añadir al final de proyectos.py

@proyectos_bp.route("/proyectos/editar/<int:id>", methods=["GET", "POST"])
def editar_proyecto(id):
    proyecto = db.execute_query("""
        SELECT id, id_cliente, tipo_proyecto, nombre_proyecto, calle, nombre_via,
               numero, puerta, codigo_postal, poblacion
        FROM proyectos WHERE id = ?
    """, (id,), fetchone=True)

    if request.method == "POST":
        tipo_proyecto = request.form.get("tipo_proyecto")
        nombre_proyecto = request.form.get("nombre_proyecto")
        calle = request.form.get("calle")
        nombre_via = request.form.get("nombre_via")
        numero = request.form.get("numero")
        puerta = request.form.get("puerta")
        codigo_postal = request.form.get("codigo_postal")
        poblacion = request.form.get("poblacion")

        db.execute_query("""
            UPDATE proyectos SET tipo_proyecto = ?, nombre_proyecto = ?, calle = ?,
            nombre_via = ?, numero = ?, puerta = ?, codigo_postal = ?, poblacion = ?
            WHERE id = ?
        """, (tipo_proyecto, nombre_proyecto, calle, nombre_via, numero, puerta, codigo_postal, poblacion, id))

        flash("Proyecto actualizado correctamente.", "success")
        return redirect(url_for("proyectos_bp.listar_proyectos"))

    return render_template("proyectos_editar.html", proyecto=proyecto)

@proyectos_bp.route("/proyectos/borrar/<int:id>", methods=["POST"])
def borrar_proyecto(id):
    db.execute_query("DELETE FROM proyectos WHERE id = ?", (id,))
    flash("Proyecto borrado correctamente.", "success")
    return redirect(url_for("proyectos_bp.listar_proyectos"))
