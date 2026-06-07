"""
PFO 3 - Sistema Distribuido (Cliente-Servidor)
Servidor que recibe tareas por socket, las encola y las distribuye a un
pool de hilos worker. Cada worker procesa una tarea y devuelve el
resultado al cliente que la envió, indicando qué worker la atendió.
"""

import socket
import threading
import queue
import time


# ─────────────────────────────────────────────
# MÓDULO DE CONFIGURACIÓN
# ─────────────────────────────────────────────

HOST = "localhost"
PUERTO = 5000
CANTIDAD_WORKERS = 3

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cola_de_tareas = queue.Queue()


# ─────────────────────────────────────────────
# MÓDULO DE PROCESAMIENTO
# ─────────────────────────────────────────────

def procesar_tarea(contenido: str) -> str:
    time.sleep(1)
    return contenido.upper()


# ─────────────────────────────────────────────
# MÓDULO DE WORKERS (POOL DE HILOS)
# ─────────────────────────────────────────────

def worker(nombre: str) -> None:
    while True:
        item = cola_de_tareas.get()
        if item is None:
            break
        cliente_socket, direccion, contenido, lock = item
        print(f"[{nombre}] Procesando '{contenido}' de {direccion}")
        resultado = procesar_tarea(contenido)


        respuesta = f"[{nombre}] {contenido} => {resultado}\n"
        try:
            with lock:
                cliente_socket.sendall(respuesta.encode("utf-8"))
        except socket.error:
            pass 
        cola_de_tareas.task_done()


def iniciar_pool(cantidad: int = CANTIDAD_WORKERS) -> None:
    for i in range(cantidad):
        hilo_worker = threading.Thread(target=worker, args=(f"Worker-{i+1}",))
        hilo_worker.daemon = True
        hilo_worker.start()
    print(f"[SERVIDOR] Pool de {cantidad} workers iniciado")


# ─────────────────────────────────────────────
# MÓDULO DE SERVIDOR
# ─────────────────────────────────────────────

def inicializar_socket(host: str = HOST, puerto: int = PUERTO) -> socket.socket:
    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, puerto))
        server.listen()
        print(f"[SERVIDOR] Servidor escuchando en {host}:{puerto}")
        return server
    except socket.error as e:
        raise RuntimeError(f"[SERVIDOR] No se pudo inicializar el socket: {e}")


# ─────────────────────────────────────────────
# MÓDULO DE MANEJO DE CLIENTES
# ─────────────────────────────────────────────

def manejar_cliente(cliente_socket: socket.socket, direccion: tuple) -> None:

    print(f"[SERVIDOR] Cliente conectado desde {direccion}")
    lock = threading.Lock()  # candado propio de esta conexión
    try:
        archivo = cliente_socket.makefile("r", encoding="utf-8")
        for linea in archivo:
            tarea = linea.strip()
            if not tarea:
                continue
            print(f"[SERVIDOR] Tarea recibida de {direccion}: '{tarea}'")
            cola_de_tareas.put((cliente_socket, direccion, tarea, lock))
        print(f"[SERVIDOR] Cliente {direccion} se ha desconectado")
    except socket.error as e:
        print(f"[SERVIDOR] Error en la conexión con {direccion}: {e}")
    finally:
        cliente_socket.close()
        print(f"[SERVIDOR] Conexión con {direccion} cerrada")


# ─────────────────────────────────────────────
# INICIAR LA COMUNICACIÓN
# ─────────────────────────────────────────────

def iniciar_comunicacion() -> None:
    iniciar_pool()

    try:
        servidor_socket = inicializar_socket()
        servidor_socket.settimeout(1.0)
    except RuntimeError as e:
        print(e)
        return

    print("[SERVIDOR] Esperando conexiones...")

    try:
        while True:
            try:
                cliente_socket, direccion = servidor_socket.accept()
                hilo_cliente = threading.Thread(target=manejar_cliente, args=(cliente_socket, direccion))
                hilo_cliente.daemon = True
                hilo_cliente.start()
            except socket.timeout:
                    continue
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Apagando...")
    finally:        
        for _ in range(CANTIDAD_WORKERS):
            cola_de_tareas.put(None)
        servidor_socket.close()
        print("[SERVIDOR] Servidor cerrado")
            

# ─────────────────────────────────────────────
# EJECUTAR EL SERVIDOR
# ─────────────────────────────────────────────

if __name__ == "__main__":
    iniciar_comunicacion()