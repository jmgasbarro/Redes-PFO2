"""
cliente.py - Cliente de consola para interactuar con la API REST.

Permite al usuario:
  1. Registrarse
  2. Iniciar sesión
  3. Ver la página de tareas (requiere credenciales)
  4. Salir
"""

import requests
import getpass

# URL base del servidor Flask
URL_BASE = "http://127.0.0.1:5000"


def registrar_usuario():
    """Solicita datos al usuario y envía una petición POST /registro."""
    print("\n--- Registro de Usuario ---")
    nombre = input("Nombre de usuario: ").strip()
    contrasena = getpass.getpass("Contraseña: ")

    if not nombre or not contrasena:
        print("[!] Ambos campos son obligatorios.")
        return

    try:
        respuesta = requests.post(
            f"{URL_BASE}/registro",
            json={"usuario": nombre, "contraseña": contrasena}
        )
        datos = respuesta.json()

        if respuesta.status_code == 201:
            print(f"[✓] {datos['mensaje']}")
        else:
            print(f"[✗] Error: {datos.get('error', 'Error desconocido')}")
    except requests.ConnectionError:
        print("[✗] No se pudo conectar con el servidor. ¿Está corriendo?")


def iniciar_sesion():
    """Solicita datos al usuario y envía una petición POST /login."""
    print("\n--- Inicio de Sesión ---")
    nombre = input("Nombre de usuario: ").strip()
    contrasena = getpass.getpass("Contraseña: ")

    if not nombre or not contrasena:
        print("[!] Ambos campos son obligatorios.")
        return

    try:
        respuesta = requests.post(
            f"{URL_BASE}/login",
            json={"usuario": nombre, "contraseña": contrasena}
        )
        datos = respuesta.json()

        if respuesta.status_code == 200:
            print(f"[✓] {datos['mensaje']}")
        else:
            print(f"[✗] Error: {datos.get('error', 'Error desconocido')}")
    except requests.ConnectionError:
        print("[✗] No se pudo conectar con el servidor. ¿Está corriendo?")


def ver_tareas():
    """
    Solicita credenciales y envía una petición GET /tareas con HTTP Basic Auth.
    Muestra el HTML devuelto por el servidor.
    """
    print("\n--- Ver Tareas (requiere autenticación) ---")
    nombre = input("Nombre de usuario: ").strip()
    contrasena = getpass.getpass("Contraseña: ")

    if not nombre or not contrasena:
        print("[!] Ambos campos son obligatorios.")
        return

    try:
        respuesta = requests.get(
            f"{URL_BASE}/tareas",
            auth=(nombre, contrasena)  # HTTP Basic Auth
        )

        if respuesta.status_code == 200:
            print("[✓] Acceso concedido. Contenido HTML recibido:\n")
            print(respuesta.text)
        else:
            datos = respuesta.json()
            print(f"[✗] Error: {datos.get('error', 'Error desconocido')}")
    except requests.ConnectionError:
        print("[✗] No se pudo conectar con el servidor. ¿Está corriendo?")


def menu():
    """Muestra el menú principal del cliente y gestiona la selección."""
    while True:
        print("\n" + "=" * 40)
        print("  Cliente API - Gestión de Tareas")
        print("=" * 40)
        print("  1. Registrar usuario")
        print("  2. Iniciar sesión")
        print("  3. Ver tareas")
        print("  4. Salir")
        print("-" * 40)

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            iniciar_sesion()
        elif opcion == "3":
            ver_tareas()
        elif opcion == "4":
            print("\n¡Hasta luego!")
            break
        else:
            print("[!] Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    menu()
