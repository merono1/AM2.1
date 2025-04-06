from flask import Blueprint, render_template, request, redirect, url_for, flash
from dbhelper import DBHelper
from datetime import datetime

proveedores_bp = Blueprint("proveedores_bp", __name__)
db = DBHelper()

def generar_referencia_proveedor():
    """
    Genera la referencia del proveedor de forma sencilla:
    Cuenta el número de proveedores y devuelve un código del tipo "PROV001", "PROV002", etc.
    """
    result = db.execute_query("SELECT COUNT(*) as total FROM proveedores", fetchone=True)
    count = result["total"] if result else 0
    return f"PROV{int(count)+1:03d}"

# Ruta para listar proveedores
@proveedores_bp.route("/proveedores")
def listar_proveedores():
    proveedores = db.execute_query("SELECT * FROM proveedores ORDER BY id DESC", fetch=True)
    return render_template("proveedores_list.html", proveedores=proveedores)

# Ruta para crear un nuevo proveedor
@proveedores_bp.route("/proveedores/nuevo", methods=["GET", "POST"])
def nuevo_proveedor():
    # Opciones para el campo Tipo: se selecciona entre 'Servicio' y 'Suministro'
    tipos = ["Servicio", "Suministro"]
    # Opciones para Especialidad (usando las mismas que en "Nuevo Proyecto" para tener relación)
    especialidades = [
        "Reforma (varios oficios)",
        "Albañilería",
        "Fontanería",
        "Electricidad",
        "Carpintería (madera)",
        "Carpintería metálica / cerrajería",
        "Climatización / aire acondicionado",
        "Calefacción",
        "Energía solar (fotovoltaica / térmica)",
        "Gas",
        "Ascensores",
        "Pintura",
        "Vidrios y acristalamientos",
        "Jardinería / paisajismo",
        "Antenas y telecomunicaciones",
        "Protección contra incendios",
        "Domótica y automatización"
    ]
    if request.method == "POST":
        referencia = generar_referencia_proveedor()
        tipo = request.form.get("tipo")
        nombre = request.form.get("nombre")
        razon_social = request.form.get("razon_social")
        direccion = request.form.get("direccion")
        codigo_postal = request.form.get("codigo_postal")
        localidad = request.form.get("localidad")
        provincia = request.form.get("provincia")
        pais = request.form.get("pais")
        telefono1 = request.form.get("telefono1")
        telefono2 = request.form.get("telefono2")
        telefono3 = request.form.get("telefono3")
        telefono4 = request.form.get("telefono4")
        email1 = request.form.get("email1")
        email2 = request.form.get("email2")
        contacto = request.form.get("contacto")
        contacto_telefono1 = request.form.get("contacto_telefono1")
        contacto_telefono2 = request.form.get("contacto_telefono2")
        contacto_email = request.form.get("contacto_email")
        fecha_alta = datetime.now().strftime("%Y-%m-%d")
        fecha_modificacion = fecha_alta
        facturas = 0  # Por defecto se inicia en 0
        especialidad = request.form.get("especialidad") or "Ninguna"

        db.execute_query("""
            INSERT INTO proveedores (
                referencia, tipo, nombre, razon_social, direccion, codigo_postal, localidad, provincia, pais,
                telefono1, telefono2, telefono3, telefono4, email1, email2,
                contacto, contacto_telefono1, contacto_telefono2, contacto_email,
                fecha_alta, fecha_modificacion, facturas, especialidad
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            referencia, tipo, nombre, razon_social, direccion, codigo_postal, localidad, provincia, pais,
            telefono1, telefono2, telefono3, telefono4, email1, email2,
            contacto, contacto_telefono1, contacto_telefono2, contacto_email,
            fecha_alta, fecha_modificacion, facturas, especialidad
        ))
        flash(f"Proveedor creado correctamente. Referencia: {referencia}", "success")
        return redirect(url_for("proveedores_bp.listar_proveedores"))
    return render_template("proveedores_nuevo.html", tipos=tipos, especialidades=especialidades)

# Ruta para editar proveedor
@proveedores_bp.route("/proveedores/editar/<int:id>", methods=["GET", "POST"])
def editar_proveedor(id):
    proveedor = db.execute_query("SELECT * FROM proveedores WHERE id = ?", (id,), fetchone=True)
    if not proveedor:
        flash("Proveedor no encontrado.", "danger")
        return redirect(url_for("proveedores_bp.listar_proveedores"))
    tipos = ["Servicio", "Suministro"]
    especialidades = [
        "Reforma (varios oficios)",
        "Albañilería",
        "Fontanería",
        "Electricidad",
        "Carpintería (madera)",
        "Carpintería metálica / cerrajería",
        "Climatización / aire acondicionado",
        "Calefacción",
        "Energía solar (fotovoltaica / térmica)",
        "Gas",
        "Ascensores",
        "Pintura",
        "Vidrios y acristalamientos",
        "Jardinería / paisajismo",
        "Antenas y telecomunicaciones",
        "Protección contra incendios",
        "Domótica y automatización"
    ]
    if request.method == "POST":
        tipo = request.form.get("tipo")
        nombre = request.form.get("nombre")
        razon_social = request.form.get("razon_social")
        direccion = request.form.get("direccion")
        codigo_postal = request.form.get("codigo_postal")
        localidad = request.form.get("localidad")
        provincia = request.form.get("provincia")
        pais = request.form.get("pais")
        telefono1 = request.form.get("telefono1")
        telefono2 = request.form.get("telefono2")
        telefono3 = request.form.get("telefono3")
        telefono4 = request.form.get("telefono4")
        email1 = request.form.get("email1")
        email2 = request.form.get("email2")
        contacto = request.form.get("contacto")
        contacto_telefono1 = request.form.get("contacto_telefono1")
        contacto_telefono2 = request.form.get("contacto_telefono2")
        contacto_email = request.form.get("contacto_email")
        especialidad = request.form.get("especialidad") or "Ninguna"
        fecha_modificacion = datetime.now().strftime("%Y-%m-%d")
        db.execute_query("""
            UPDATE proveedores SET
                tipo = ?, nombre = ?, razon_social = ?, direccion = ?, codigo_postal = ?, localidad = ?,
                provincia = ?, pais = ?, telefono1 = ?, telefono2 = ?, telefono3 = ?, telefono4 = ?,
                email1 = ?, email2 = ?, contacto = ?, contacto_telefono1 = ?, contacto_telefono2 = ?, contacto_email = ?,
                fecha_modificacion = ?, especialidad = ?
            WHERE id = ?
        """, (
            tipo, nombre, razon_social, direccion, codigo_postal, localidad,
            provincia, pais, telefono1, telefono2, telefono3, telefono4,
            email1, email2, contacto, contacto_telefono1, contacto_telefono2, contacto_email,
            fecha_modificacion, especialidad, id
        ))
        flash("Proveedor actualizado correctamente.", "success")
        return redirect(url_for("proveedores_bp.listar_proveedores"))
    return render_template("proveedores_editar.html", proveedor=proveedor, tipos=tipos, especialidades=especialidades)

# Ruta para borrar proveedor
@proveedores_bp.route("/proveedores/borrar/<int:id>", methods=["POST"])
def borrar_proveedor(id):
    db.execute_query("DELETE FROM proveedores WHERE id = ?", (id,))
    flash("Proveedor borrado correctamente.", "success")
    return redirect(url_for("proveedores_bp.listar_proveedores"))
