from flask import Blueprint, render_template, request, redirect, url_for, flash
from dbhelper import DBHelper

clientes_bp = Blueprint("clientes_bp", __name__)
db = DBHelper()

@clientes_bp.route("/clientes")
def listar_clientes():
    query = """
        SELECT id, nombre, tipo_via, nombre_via, numero_via, puerta, codigo_postal,
               cif_nif, telefono1, telefono2, telefono3, telefono4,
               mail1, mail2, poblacion, tipo_cliente, categoria_cliente, notas
        FROM clientes
        ORDER BY id DESC
    """
    clientes = db.execute_query(query, fetch=True) or []
    return render_template("clientes_list.html", clientes=clientes)

@clientes_bp.route("/clientes/nuevo", methods=["GET", "POST"], endpoint="nuevo_cliente")
def nuevo_cliente():
    if request.method == "POST":
        try:
            nombre = request.form.get("nombre")
            tipo_via = request.form.get("tipo_via")
            nombre_via = request.form.get("nombre_via")
            numero_via = request.form.get("numero_via")
            puerta = request.form.get("puerta")
            codigo_postal = request.form.get("codigo_postal")
            cif_nif = request.form.get("cif_nif")
            telefono1 = request.form.get("telefono1")
            telefono2 = request.form.get("telefono2")
            telefono3 = request.form.get("telefono3")
            telefono4 = request.form.get("telefono4")
            mail1 = request.form.get("mail1")
            mail2 = request.form.get("mail2")
            poblacion = request.form.get("poblacion")
            notas = request.form.get("notas")
            tipo_cliente = request.form.get("tipo_cliente")
            categoria_cliente = request.form.get("categoria_cliente")

            db.execute_query("""
                INSERT INTO clientes (
                    nombre, tipo_via, nombre_via, numero_via, puerta, codigo_postal,
                    cif_nif, telefono1, telefono2, telefono3, telefono4,
                    mail1, mail2, poblacion, notas, tipo_cliente, categoria_cliente
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nombre, tipo_via, nombre_via, numero_via, puerta, codigo_postal, cif_nif,
                  telefono1, telefono2, telefono3, telefono4, mail1, mail2, poblacion,
                  notas, tipo_cliente, categoria_cliente))

            flash("Cliente creado correctamente.", "success")
            return redirect(url_for("clientes_bp.listar_clientes"))
        except Exception as e:
            flash(f"Error al crear cliente: {str(e)}", "danger")

    # Este return es necesario para mostrar el formulario si es GET o si falló algo
    return render_template("clientes_nuevo.html")

@clientes_bp.route("/clientes/nota/<int:cliente_id>", methods=["POST"])
def actualizar_nota(cliente_id):
    nueva_nota = request.form.get("nueva_nota")
    db.execute_query("UPDATE clientes SET notas = ? WHERE id = ?", (nueva_nota, cliente_id))
    flash("Nota actualizada correctamente.", "success")
    return redirect(url_for("clientes_bp.listar_clientes"))

        

@clientes_bp.route("/clientes/editar/<int:cliente_id>", methods=["GET", "POST"])
def editar_cliente(cliente_id):
    if request.method == "POST":
        nombre = request.form.get("nombre")
        tipo_via = request.form.get("tipo_via")
        nombre_via = request.form.get("nombre_via")
        numero_via = request.form.get("numero_via")
        puerta = request.form.get("puerta")
        codigo_postal = request.form.get("codigo_postal")
        cif_nif = request.form.get("cif_nif")
        telefono1 = request.form.get("telefono1")
        telefono2 = request.form.get("telefono2")
        telefono3 = request.form.get("telefono3")
        telefono4 = request.form.get("telefono4")
        mail1 = request.form.get("mail1")
        mail2 = request.form.get("mail2")
        poblacion = request.form.get("poblacion")
        notas = request.form.get("notas")
        tipo_cliente = request.form.get("tipo_cliente")
        categoria_cliente = request.form.get("categoria_cliente")

        db.execute_query("""
            UPDATE clientes SET nombre = ?, tipo_via = ?, nombre_via = ?, numero_via = ?, puerta = ?, 
                            codigo_postal = ?, cif_nif = ?, telefono1 = ?, telefono2 = ?, telefono3 = ?, 
                            telefono4 = ?, mail1 = ?, mail2 = ?, poblacion = ?, notas = ?, tipo_cliente = ?, categoria_cliente = ?
            WHERE id = ?
        """, (nombre, tipo_via, nombre_via, numero_via, puerta, codigo_postal, cif_nif,
            telefono1, telefono2, telefono3, telefono4, mail1, mail2, poblacion,
            notas, tipo_cliente, categoria_cliente, cliente_id))

        flash("Cliente actualizado correctamente.", "success")
        return redirect(url_for("clientes_bp.listar_clientes"))
     # <-- ESTE BLOQUE ES CLAVE PARA MOSTRAR EL FORMULARIO CUANDO NO SE HACE POST
    cliente = db.execute_query("SELECT * FROM clientes WHERE id = ?", (cliente_id,), fetchone=True)
    return render_template("clientes_editar.html", cliente=cliente)
    

@clientes_bp.route("/clientes/borrar/<int:cliente_id>", methods=["POST"], endpoint="borrar_cliente")
def borrar_cliente(cliente_id):
    try:
        db.execute_query("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        flash("Cliente eliminado correctamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar el cliente: {str(e)}", "danger")
    return redirect(url_for("clientes_bp.listar_clientes"))
