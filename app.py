from flask import Flask, render_template
from dbhelper import create_schema
from clientes import clientes_bp
from proyectos import proyectos_bp
from hojas_trabajo import hojas_trabajo_bp

app = Flask(__name__)
app.secret_key = "supersecreto"
create_schema()

# Registro de blueprints
app.register_blueprint(clientes_bp)
app.register_blueprint(proyectos_bp)
app.register_blueprint(hojas_trabajo_bp)

@app.route("/")
def index():
    return render_template("inicio.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
