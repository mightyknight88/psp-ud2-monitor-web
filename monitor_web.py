from time import perf_counter
import threading
import requests

TIMEOUT = 6

SERVICIOS = {
    "Python": {
        "url": "https://www.python.org/",
        "estado": "SIN INICIAR"
    },
    "Docs Python": {
        "url": "https://docs.python.org/3/",
        "estado": "SIN INICIAR"
    },
    "PyPI": {
        "url": "https://pypi.org/",
        "estado": "SIN INICIAR"
    },
    "GitHub": {
        "url": "https://github.com/",
        "estado": "SIN INICIAR"
    },
    "httpbin-retraso": {
        "url": "https://httpbin.org/delay/5",
        "estado": "SIN INICIAR"
    },
    "httpbin-503": {
        "url": "https://httpbin.org/status/503",
        "estado": "SIN INICIAR"
    }
}


def reiniciar_estados():
    for clave, datos in SERVICIOS.items():
        datos["estado"] = "SIN INICIAR"


####################
###### Fase 1 ######
####################

def comprobar_servicio(clave:str, url:str):
    print(f"[{clave}] Iniciando {url}")
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

    print(f"[{clave}] {estado} (código: {codigo}) - {duracion} s")


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
            args=(clave, datos["url"])
        )
        lista_hilos.append(hilo)
        hilo.start()

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