"""
PFO 3 - Sistema Distribuido (Cliente-Servidor)
Cliente que envía una lista de tareas al servidor y recibe el resultado
de cada una, indicando qué worker la procesó.
"""

import socket


# ─────────────────────────────────────────────
# MÓDULO DE CONFIGURACIÓN
# ─────────────────────────────────────────────

HOST = "localhost"
PUERTO = 5000
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tareas = [
    "hola mundo",
    "programacion sobre redes",
    "sistema distribuido",
    "cola de mensajes",
    "estudiar conceptos de arquitectura",
    "hacer diagramas del sistema",
    "leer documentación técnica",
    "organizar archivos del proyecto",
    "escribir resumen de objetivos",
    "revisar código del cliente",
]


# ─────────────────────────────────────────────
# MÓDULO PRINCIPAL
# ─────────────────────────────────────────────

def iniciar_cliente(host: str = HOST, puerto: int = PUERTO) -> None:
    try:
        cliente_socket.connect((host, puerto))
        print(f"[CLIENTE] Conectado al servidor en {host}:{puerto}")
        print("[CLIENTE] Se inicia el envío de tareas.\n")
    except ConnectionRefusedError:
        print(
            f"[CLIENTE] No se pudo conectar a {host}:{puerto}. "
            "¿El servidor está corriendo?"
        )
        return

    try:
        for t in tareas:
            cliente_socket.sendall((t + "\n").encode("utf-8"))
            print(f"[CLIENTE] envía tarea -> {t}")

        archivo = cliente_socket.makefile("r", encoding="utf-8")
        print()
        for _ in tareas:
            resultado = archivo.readline().strip()
            print(f"[CLIENTE] resultado <- {resultado}")

    except (socket.error, BrokenPipeError) as e:
        print(f"[CLIENTE] Error de conexión: {e}")
    finally:
        cliente_socket.close()
        print("\n--- Comunicación cerrada ---")


# ─────────────────────────────────────────────
# EJECUTAR EL CLIENTE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    iniciar_cliente()