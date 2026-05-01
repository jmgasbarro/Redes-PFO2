"""
servidor.py - API REST con Flask para gestión de usuarios y tareas.

Endpoints:
  POST /registro  -> Registra un nuevo usuario (contraseña hasheada con Werkzeug).
  POST /login     -> Verifica credenciales y devuelve un mensaje de éxito.
  GET  /tareas    -> Muestra una página HTML de bienvenida (requiere autenticación básica).

Persistencia: SQLite (archivo usuarios.db).
"""

import sqlite3
import os
from flask import Flask, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# ---------------------------------------------------------------------------
# Configuración de la aplicación
# ---------------------------------------------------------------------------
app = Flask(__name__)

# Ruta de la base de datos SQLite (mismo directorio que el script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "usuarios.db")


# ---------------------------------------------------------------------------
# Funciones auxiliares para la base de datos
# ---------------------------------------------------------------------------

def obtener_conexion():
    """Abre y devuelve una conexión a la base de datos SQLite."""
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
    return conexion


def inicializar_db():
    """Crea la tabla de usuarios si no existe."""
    conexion = obtener_conexion()
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario  TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL
        )
    """)
    conexion.commit()
    conexion.close()


# ---------------------------------------------------------------------------
# Decorador de autenticación básica (HTTP Basic Auth)
# ---------------------------------------------------------------------------

def requiere_autenticacion(f):
    """
    Decorador que protege un endpoint con HTTP Basic Auth.
    Verifica que el usuario exista en la DB y que la contraseña coincida.
    """
    @wraps(f)
    def decorador(*args, **kwargs):
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return jsonify({"error": "Se requieren credenciales de autenticación."}), 401

        conexion = obtener_conexion()
        fila = conexion.execute(
            "SELECT * FROM usuarios WHERE usuario = ?", (auth.username,)
        ).fetchone()
        conexion.close()

        if fila is None:
            return jsonify({"error": "Usuario no encontrado."}), 401

        if not check_password_hash(fila["password"], auth.password):
            return jsonify({"error": "Contraseña incorrecta."}), 401

        # Pasar el nombre de usuario al endpoint
        return f(usuario_autenticado=auth.username, *args, **kwargs)

    return decorador


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.route("/registro", methods=["POST"])
def registro():
    """
    POST /registro
    Body JSON: {"usuario": "nombre", "contraseña": "1234"}
    Registra un nuevo usuario con contraseña hasheada.
    """
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "El cuerpo de la solicitud debe ser JSON."}), 400

    nombre = datos.get("usuario")
    contrasena = datos.get("contraseña")

    if not nombre or not contrasena:
        return jsonify({"error": "Los campos 'usuario' y 'contraseña' son obligatorios."}), 400

    # Hashear la contraseña antes de almacenarla
    hash_contrasena = generate_password_hash(contrasena)

    try:
        conexion = obtener_conexion()
        conexion.execute(
            "INSERT INTO usuarios (usuario, password) VALUES (?, ?)",
            (nombre, hash_contrasena)
        )
        conexion.commit()
        conexion.close()
    except sqlite3.IntegrityError:
        return jsonify({"error": f"El usuario '{nombre}' ya existe."}), 409

    return jsonify({"mensaje": f"Usuario '{nombre}' registrado exitosamente."}), 201


@app.route("/login", methods=["POST"])
def login():
    """
    POST /login
    Body JSON: {"usuario": "nombre", "contraseña": "1234"}
    Verifica las credenciales del usuario.
    """
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "El cuerpo de la solicitud debe ser JSON."}), 400

    nombre = datos.get("usuario")
    contrasena = datos.get("contraseña")

    if not nombre or not contrasena:
        return jsonify({"error": "Los campos 'usuario' y 'contraseña' son obligatorios."}), 400

    conexion = obtener_conexion()
    fila = conexion.execute(
        "SELECT * FROM usuarios WHERE usuario = ?", (nombre,)
    ).fetchone()
    conexion.close()

    if fila is None:
        return jsonify({"error": "Usuario no encontrado."}), 404

    if not check_password_hash(fila["password"], contrasena):
        return jsonify({"error": "Contraseña incorrecta."}), 401

    return jsonify({"mensaje": f"Inicio de sesión exitoso. ¡Bienvenido, {nombre}!"}), 200


@app.route("/tareas", methods=["GET"])
@requiere_autenticacion
def tareas(usuario_autenticado):
    """
    GET /tareas
    Requiere autenticación básica (HTTP Basic Auth).
    Muestra una página HTML de bienvenida con el nombre del usuario.
    """
    return render_template("tareas.html", usuario=usuario_autenticado)


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    inicializar_db()
    print("=" * 50)
    print("  Servidor Flask iniciado")
    print("  http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)
