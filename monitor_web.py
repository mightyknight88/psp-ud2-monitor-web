import threading
import requests
from time import perf_counter, sleep

UMBRAL_LENTO = 2
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
###### Fase 5 ######
####################

def avisar_lento(url:str):
    print(f"[AVISO] {url} está tardando demasiado.")


####################
## Fases 1, 3 y 6 ##
####################

def comprobar_servicio(clave:str, url:str):
    nombre_hilo = threading.current_thread().name  # Fase 3

    print(f"[{nombre_hilo}] Iniciando {url}")
    SERVICIOS[clave]["estado"] = "EN CURSO"

    aviso = threading.Timer(UMBRAL_LENTO, avisar_lento, args=(url,))
    aviso.start()

    inicio = perf_counter()
    codigo = None

    try:
        respuesta = requests.get(url, timeout=TIMEOUT)
        codigo = respuesta.status_code
        if respuesta.ok:
            estado = "ONLINE"
        else:
            estado = "ERROR HTTP"
    except requests.exceptions.Timeout:
        estado = "TIMEOUT"
    except requests.exceptions.RequestException:
        estado = "ERROR DE CONEXIÓN"
    finally:
        aviso.cancel()

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

    hilo_monitor = threading.Thread(
        target=monitor,
        args=(lista_hilos,),
        name="monitor",
        daemon=True
    )
    hilo_monitor.start()

    for hilo in lista_hilos:
        hilo.join()

    return round(perf_counter() - inicio, 2)

####################
###### Fase 4 ######
####################

def monitor(lista_hilos:list):
    while True:
        activos = []
        for hilo in lista_hilos:
            if hilo.is_alive():
                activos.append(hilo.name)

        if activos:
            print(f"[MONITOR] Comprobaciones activas: {len(activos)} -> {', '.join(activos)}")

        sleep(1)



####################
###### Fase 7 ######
####################

def mostrar_resumen(tiempo_secuencial:float, tiempo_concurrente:float):
    resultados = {"disponibles": [], "con_error": []}

    for clave, datos in SERVICIOS.items():
        match datos["estado"]:
            case "ONLINE":
                resultados["disponibles"].append(clave)
            case _:
                resultados["con_error"].append(clave)

    print("\n===============================")
    print("        RESUMEN DEL MONITOR")
    print("===============================")
    print(f"Servicios comprobados: {len(SERVICIOS)}")
    print(f"Disponibles: {len(resultados['disponibles'])}")
    print(f"Con error: {len(resultados['con_error'])}")

    for clave in resultados["con_error"]:
        print(f"\t- {clave}: {SERVICIOS[clave]['estado']}")

    print(f"Tiempo secuencial:   {tiempo_secuencial} s")
    print(f"Tiempo concurrente:  {tiempo_concurrente} s")


####################
##### Ejecución ####
####################

print("===== VERSIÓN SECUENCIAL =====")
tiempo_secuencial = comprobar_secuencial()
print(f"Tiempo total secuencial: {tiempo_secuencial} s")

print("\n===== VERSIÓN CONCURRENTE =====")
tiempo_concurrente = comprobar_concurrente()
print(f"Tiempo total concurrente: {tiempo_concurrente} s")

mostrar_resumen(tiempo_secuencial, tiempo_concurrente)