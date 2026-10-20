from time import perf_counter
import threading
import requests
import time

TIMEOUT = 6

SERVICIOS = {
    "Python": {
        "url": "https://www.python.org/",
        "nombre_hilo": "web-python",
        "estado": "SIN INICIAR"
    },
    "Docs Python": {
        "url": "https://docs.python.org/3/",
        "nombre_hilo": "web-docs-python",
        "estado": "SIN INICIAR"
    },
    "PyPI": {
        "url": "https://pypi.org/",
        "nombre_hilo": "web-pypi",
        "estado": "SIN INICIAR"
    },
    "GitHub": {
        "url": "https://github.com/",
        "nombre_hilo": "web-github",
        "estado": "SIN INICIAR"
    },
    "httpbin-retraso": {
        "url": "https://httpbin.org/delay/5",
        "nombre_hilo": "web-httpbin-retraso",
        "estado": "SIN INICIAR"
    },
    "httpbin-503": {
        "url": "https://httpbin.org/status/503",
        "nombre_hilo": "web-httpbin-503",
        "estado": "SIN INICIAR"
    }
}

def reiniciar_estados():
    for clave, datos in SERVICIOS.items():
        datos["estado"] = "SIN INICIAR"


####################
##### Fases 1 y 3 ##
####################

def comprobar_servicio(clave:str, url:str):
    nombre_hilo = threading.current_thread().name

    print(f"[{nombre_hilo}] Iniciando {url}")
    SERVICIOS[clave]["estado"] = "EN CURSO"

    inicio = perf_counter()

    respuesta = requests.get(url, timeout=TIMEOUT)
    codigo = respuesta.status_code
    if respuesta.ok:
        estado = "ONLINE"
    else:
        estado = "ERROR HTTP"

    duracion = round(perf_counter() - inicio, 2)
    SERVICIOS[clave]["estado"] = estado

    print(f"[{nombre_hilo}] {estado} (código: {codigo}) - {duracion} s")

####################
###### Fase 1 ######
####################

def comprobar_secuencial():
    reiniciar_estados()
    inicio = perf_counter()

    for clave, datos in SERVICIOS.items():
        comprobar_servicio(clave, datos["url"])

    return round(perf_counter() - inicio, 2)

####################
###### Fase 2 ######
####################

def comprobar_concurrente():
    reiniciar_estados()
    inicio = perf_counter()

    lista_hilos = []
    for clave, datos in SERVICIOS.items():
        hilo = threading.Thread(
            target=comprobar_servicio,
            args=(clave, datos["url"]),
            name=datos["nombre_hilo"]
        )
        lista_hilos.append(hilo)
        hilo.start()

    while True:
        activos = []
        for hilo in lista_hilos:
            if hilo.is_alive():
                activos.append(hilo.name)

        if not activos:
            break

        print(f"   ... siguen activos ({len(activos)}): {', '.join(activos)}")
        time.sleep(1)

    print(f"[PRINCIPAL] Hilos activos tras lanzarlos: {len(activos)} -> {', '.join(activos)}")

    for hilo in lista_hilos:
        hilo.join()

    return round(perf_counter() - inicio, 2)


####################
##### Ejecución ####
####################

print("===== VERSIÓN SECUENCIAL =====")
tiempo_secuencial = comprobar_secuencial()
print(f"Tiempo total secuencial: {tiempo_secuencial} s")

print("\n===== VERSIÓN CONCURRENTE =====")
tiempo_concurrente = comprobar_concurrente()
print(f"Tiempo total concurrente: {tiempo_concurrente} s")