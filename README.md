# psp-ud2-monitor-web

**Práctica UD2 · Monitor Web Concurrente** — Programación de Servicios y Procesos 2º DAM
**Miguel Andrés Sánchez Tovar


### 1. ¿Qué diferencia de tiempo observaste entre la versión secuencial y la concurrente?

En mi ejecución, la versión secuencial tardó 8 segundos apróx y la concurrente 6 segundos apróx. En la secuencial cada comprobación espera a que termine la anterior, así que el tiempo total es aproximadamente la suma de todas. En la concurrente se lanzan todas a la vez y el tiempo total se acerca al de la comprobación más lenta, que aquí es httpbin-retraso (unos 5 s).

### 2. ¿Por qué este problema puede considerarse I/O-bound?

Porque casi todo el tiempo se va en esperar la respuesta de la red, no en calcular. La CPU está libre mientras llega la respuesta del servidor, así que el cuello de botella es la latencia de entrada/salida.

### 3. ¿Por qué los hilos son adecuados para este caso?

Mientras un hilo espera una respuesta de red, Python libera el GIL y otros hilos pueden ejecutarse. Así se solapan las esperas y se ahorra tiempo. Además, los hilos comparten memoria (el diccionario SERVICIOS) y son más ligeros que los procesos.

### 4. ¿Qué ocurriría si realizaras join() inmediatamente después de cada start()?

El hilo principal esperaría a que terminase cada hilo antes de lanzar el siguiente, y el programa volvería a ser secuencial. No habría ganancia de tiempo y se añadiría el coste de crear los hilos.

### 5. ¿Los servicios terminan siempre en el mismo orden? Explica por qué.

No. El orden de finalización depende del tiempo de respuesta de cada servidor, de la red y de la planificación de los hilos por el sistema operativo, no del orden en que se lanzaron. Por ejemplo, "httpbin-503" suele terminar pronto y "httpbin-retraso" el último, pero el resto puede variar entre ejecuciones.

### 6. ¿Qué utilidad tiene asignar un nombre a cada hilo?

Permite identificar qué hilo escribe cada mensaje (por ejemplo [web-github]), depurar errores y mostrar en el monitor qué comprobaciones siguen activas. Sin nombres solo aparecería Thread-1, Thread-2, etc., que no dicen nada del servicio.

### 7. ¿Qué información aporta is_alive() y qué diferencia tiene respecto a join()?

is_alive() indica, sin bloquear, si un hilo sigue ejecutándose en ese momento. join() bloquea al hilo que lo llama hasta que el otro termina. Uso is_alive() en el monitor para consultar el estado y join() para esperar a que acaben todas las comprobaciones.

### 8. ¿Por qué el monitor se ha configurado como daemon?

Porque su bucle (while True) no termina nunca y es solo un apoyo. Al ser daemon, no impide que el programa finalice: cuando terminan el hilo principal y los hilos de comprobación, el intérprete se cierra y el monitor muere con él. Si no fuera daemon, el programa quedaría colgado para siempre.

### 9. ¿Qué diferencia existe entre el Timer de aviso y el timeout de requests?

El Timer solo avisa: a los 2 s (UMBRAL_LENTO) imprime que el servicio es lento, pero la petición sigue su curso. El timeout=6 de requests sí la corta: si no hay respuesta a tiempo lanza Timeout y el estado pasa a TIMEOUT. Con httpbin/delay/5 se ve el aviso a los 2 s y, como responde antes de 6 s, termina ONLINE. Si la petición acaba antes del umbral, el Timer se cancela.

### 10. ¿Qué problema podría aparecer si varios hilos modificaran simultáneamente una misma estructura de resultados?

Una condición de carrera: dos hilos podrían leer y escribir a la vez, y una actualización pisaría a otra, o un hilo (como el monitor) leería datos a medio actualizar. Los resultados serían inconsistentes y variarían de una ejecución a otra. En mi código cada hilo escribe solo en su propia clave de SERVICIOS, pero con una estructura compartida (una lista común, un contador) el riesgo sería real.
