from flask import Flask, render_template
from clientes import clientes_bp
from proyectos import proyectos_bp
from presupuestos import presupuestos_bp
from proveedores import proveedores_bp
from hojas_trabajo import hojas_trabajo_bp
from dbhelper import DBHelper, create_schema


app = Flask(__name__)
app.secret_key = "supersecreto"

# Crear la base de datos y las tablas si no existen
db = DBHelper()
create_schema()


# Registrar los blueprints
app.register_blueprint(clientes_bp)
app.register_blueprint(proyectos_bp)
app.register_blueprint(presupuestos_bp)
app.register_blueprint(proveedores_bp)
app.register_blueprint(hojas_trabajo_bp)

@app.route("/")
def index():
    return render_template("inicio.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
