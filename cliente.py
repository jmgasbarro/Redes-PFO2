"""
cliente.py - Cliente de consola para interactuar con la API REST.

Permite al usuario:
  1. Registrarse
  2. Iniciar sesión
  3. Ver la página de tareas (requiere credenciales)
  4. Salir
"""

import requests
import webbrowser
import tempfile
import os

# URL base del servidor Flask
URL_BASE = "http://127.0.0.1:5000"

# Variable global para guardar la sesión activa
sesion_activa = None  # Guardará {"usuario": ..., "contraseña": ...} tras un login exitoso


def registrar_usuario():
    """Solicita datos al usuario y envía una petición POST /registro."""
    print("\n--- Registro de Usuario ---")
    nombre = input("Nombre de usuario: ").strip()
    contrasena = input("Contraseña: ").strip()

    if not nombre or not contrasena:
        print("[!] Ambos campos son obligatorios.")
        return

    try:
        respuesta = requests.post(
            f"{URL_BASE}/registro",
            json={"usuario": nombre, "contraseña": contrasena}
        )

        try:
            datos = respuesta.json()
        except Exception:
            print(f"[!] Respuesta inesperada del servidor (codigo {respuesta.status_code})")
            return

        if respuesta.status_code == 201:
            print(f"[OK] {datos['mensaje']}")
        else:
            print(f"[X] Error: {datos.get('error', 'Error desconocido')}")
    except requests.ConnectionError:
        print("[X] No se pudo conectar con el servidor. Esta corriendo?")


def iniciar_sesion():
    """Solicita datos al usuario y envía una petición POST /login."""
    global sesion_activa

    print("\n--- Inicio de Sesion ---")
    nombre = input("Nombre de usuario: ").strip()
    contrasena = input("Contraseña: ").strip()

    if not nombre or not contrasena:
        print("[!] Ambos campos son obligatorios.")
        return

    try:
        respuesta = requests.post(
            f"{URL_BASE}/login",
            json={"usuario": nombre, "contraseña": contrasena}
        )

        try:
            datos = respuesta.json()
        except Exception:
            print(f"[!] Respuesta inesperada del servidor (codigo {respuesta.status_code})")
            return

        if respuesta.status_code == 200:
            # Guardar las credenciales para usarlas en /tareas
            sesion_activa = {"usuario": nombre, "contraseña": contrasena}
            print(f"[OK] {datos['mensaje']}")
        else:
            print(f"[X] Error: {datos.get('error', 'Error desconocido')}")
    except requests.ConnectionError:
        print("[X] No se pudo conectar con el servidor. Esta corriendo?")


def ver_tareas():
    """
    Envía una petición GET /tareas con HTTP Basic Auth.
    Si ya se inició sesión, usa esas credenciales.
    Si no, las pide manualmente.
    """
    global sesion_activa

    if sesion_activa:
        # Ya hay una sesión activa, usar esas credenciales
        nombre = sesion_activa["usuario"]
        contrasena = sesion_activa["contraseña"]
        print(f"\n--- Accediendo a tareas como '{nombre}' ---")
    else:
        # No hay sesión, pedir credenciales
        print("\n--- Ver Tareas (requiere autenticacion) ---")
        print("[!] No hay sesion activa. Ingresa tus credenciales:")
        nombre = input("Nombre de usuario: ").strip()
        contrasena = input("Contraseña: ").strip()

        if not nombre or not contrasena:
            print("[!] Ambos campos son obligatorios.")
            return

    try:
        respuesta = requests.get(
            f"{URL_BASE}/tareas",
            auth=(nombre, contrasena)  # HTTP Basic Auth
        )

        if respuesta.status_code == 200:
            # Guardar el HTML en un archivo temporal y abrirlo en el navegador
            archivo = os.path.join(tempfile.gettempdir(), "tareas_bienvenida.html")
            with open(archivo, "w", encoding="utf-8") as f:
                f.write(respuesta.text)
            webbrowser.open(f"file:///{archivo}")
            print("[OK] Pagina de bienvenida abierta en el navegador.")
        else:
            try:
                datos = respuesta.json()
                print(f"[X] Error: {datos.get('error', 'Error desconocido')}")
            except Exception:
                print(f"[X] Error del servidor (codigo {respuesta.status_code})")
    except requests.ConnectionError:
        print("[X] No se pudo conectar con el servidor. Esta corriendo?")


def menu():
    """Muestra el menú principal del cliente y gestiona la selección."""
    while True:
        print("\n" + "=" * 40)
        print("  Cliente API - Gestion de Tareas")
        print("=" * 40)
        print("  1. Registrar usuario")
        print("  2. Iniciar sesion")
        print(f"  3. Ver tareas", end="")
        if sesion_activa:
            print(f"  (sesion: {sesion_activa['usuario']})")
        else:
            print()
        print("  4. Salir")
        print("-" * 40)

        opcion = input("Selecciona una opcion: ").strip()

        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            iniciar_sesion()
        elif opcion == "3":
            ver_tareas()
        elif opcion == "4":
            print("\nHasta luego!")
            break
        else:
            print("[!] Opcion no valida. Intenta de nuevo.")


if __name__ == "__main__":
    menu()
