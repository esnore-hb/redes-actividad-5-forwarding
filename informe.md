# Informe — Actividad 5: Forwarding básico

## 1. Comparación entre la tabla de rutas de la actividad y una tabla real

Al comparar las tablas, identificamos que ambas resuelven la misma pregunta: a qué siguiente salto enviar un paquete según su destino. El router no necesita conocer el camino completo.

La diferencia principal que observamos es cómo se representan los destinos. En una tabla real se agrupan mediante prefijos IP y se indica el siguiente salto y/o la interfaz de salida. En el modelo de la actividad usamos la misma IP local y distinguimos los routers por sus puertos, por lo que las tablas incluyen rangos de puertos. Seguimos esta simplificación para simular la red en un solo computador; en una red real, los puertos identifican aplicaciones.

## 2. Script de envío (ítem 5)

Elegimos recibir los datos como argumentos de terminal para poder repetir los envíos sin modificar el código. Colocamos primero el destino final, luego el mensaje y al final el router de entrada:

```text
python enviar.py IP_final puerto_final "mensaje" IP_envio puerto_envio
```

Por ejemplo, `python enviar.py 127.0.0.1 8883 "hola" 127.0.0.1 8881` envía a R3 entrando por R1. Usamos UTF-8 para admitir tildes y otros caracteres, y reutilizamos `create_packet()` para mantener un único formato de paquete. Las comillas permiten enviar mensajes con espacios como un solo argumento.

Para comprobar que distinguimos el destino final del router de entrada, enviamos un paquete a R1 con R3 indicado en el header. Verificamos que R1 recibió el paquete, que el destino seguía siendo R3 y que el mensaje con espacios y la letra ñ se recuperó sin cambios. Esta prueba comprueba la recepción y el formato del paquete; el reenvío se implementará más adelante.

## 3. Alternancia de rutas (ítem 8)

Elegimos guardar los turnos en un diccionario propio de cada router y pasarlo a `check_routes()`. Agrupamos las rutas por red y rango de puertos: los destinos de una misma área comparten turno, mientras que las otras áreas conservan el suyo. Respetamos la primera área que coincide en el archivo y alternamos solo entre sus siguientes saltos, en el orden escrito. Usamos el resto de la división por la cantidad de opciones para volver al inicio, sin limitar el número de rutas a dos.

Con las tablas `v3` del enunciado enviamos ocho mensajes de R1 a R5. Todos llegaron y R2 alternó entre R3 y R4. Algunos paquetes volvieron a pasar por R2 antes de llegar: round-robin reparte los envíos, pero no asegura el camino más corto ni evita ciclos.

Para la red ampliada creamos las tablas `v4`. Asignamos el puerto 8880 a R0 y el 8886 a R6. En R2 agregamos una alternativa por R0 hacia el área de R1 y otra por R6 hacia el área de R5. Intercalamos seis envíos en cada sentido: los doce llegaron. R2 mantuvo las secuencias R3–R4–R6 hacia R5 y R1–R0 hacia R1, sin que una avanzara el turno de la otra.

## 4. Router default (ítem 9)

Creamos las tablas `v5` a partir de la red ampliada para conservar las configuraciones anteriores. Agregamos al final de cada tabla esta ruta:

```text
0.0.0.0/0 0 65535 127.0.0.1 7000
```

Elegimos la última posición porque `check_routes()` conserva la primera área coincidente. Así, las rutas internas tienen prioridad y solo los demás destinos van al default. El prefijo /0 cubre cualquier dirección IPv4 y el rango 0–65535 cubre todos los puertos.

Para conectar el default con los siete routers, su tabla contiene una ruta directa a cada uno. No le agregamos una ruta hacia sí mismo: como no simulamos el resto de Internet, descarta los destinos externos al no encontrar ruta. Así evitamos que el paquete vuelva a circular por nuestra red.

Probamos los ocho routers en ejecución y enviamos un paquete con destino final `192.0.2.1:9000` desde cada router R0–R6. Los siete llegaron al default, donde se descartaron por falta de ruta. La dirección externa solo figuraba en el header; los envíos UDP se mantuvieron en localhost. También verificamos la entrega de R1 a R5 y del default a R1. No fue necesario modificar el código.

Las tablas resultantes son las siguientes. Cada fila contiene red, puerto inicial, puerto final, IP del siguiente salto y puerto del siguiente salto.

**rutas_R0_v5.txt**

```text
127.0.0.1/24 8881 8881 127.0.0.1 8881
127.0.0.1/24 8882 8886 127.0.0.1 8882
0.0.0.0/0 0 65535 127.0.0.1 7000
```

**rutas_R1_v5.txt**

```text
127.0.0.1/24 8880 8880 127.0.0.1 8880
127.0.0.1/24 8882 8886 127.0.0.1 8882
0.0.0.0/0 0 65535 127.0.0.1 7000
```

**rutas_R2_v5.txt**

```text
127.0.0.1/24 8880 8881 127.0.0.1 8881
127.0.0.1/24 8880 8881 127.0.0.1 8880
127.0.0.1/24 8883 8886 127.0.0.1 8883
127.0.0.1/24 8883 8886 127.0.0.1 8884
127.0.0.1/24 8883 8886 127.0.0.1 8886
0.0.0.0/0 0 65535 127.0.0.1 7000
```

**rutas_R3_v5.txt**

```text
127.0.0.1/24 8880 8882 127.0.0.1 8882
127.0.0.1/24 8880 8882 127.0.0.1 8885
127.0.0.1/24 8884 8885 127.0.0.1 8882
127.0.0.1/24 8884 8885 127.0.0.1 8885
127.0.0.1/24 8886 8886 127.0.0.1 8886
0.0.0.0/0 0 65535 127.0.0.1 7000
```

**rutas_R4_v5.txt**

```text
127.0.0.1/24 8880 8883 127.0.0.1 8882
127.0.0.1/24 8880 8883 127.0.0.1 8885
127.0.0.1/24 8885 8885 127.0.0.1 8882
127.0.0.1/24 8885 8885 127.0.0.1 8885
127.0.0.1/24 8886 8886 127.0.0.1 8882
0.0.0.0/0 0 65535 127.0.0.1 7000
```

**rutas_R5_v5.txt**

```text
127.0.0.1/24 8880 8884 127.0.0.1 8884
127.0.0.1/24 8880 8884 127.0.0.1 8883
127.0.0.1/24 8886 8886 127.0.0.1 8883
0.0.0.0/0 0 65535 127.0.0.1 7000
```

**rutas_R6_v5.txt**

```text
127.0.0.1/24 8880 8882 127.0.0.1 8882
127.0.0.1/24 8883 8883 127.0.0.1 8883
127.0.0.1/24 8884 8885 127.0.0.1 8882
0.0.0.0/0 0 65535 127.0.0.1 7000
```

**rutas_default_v5.txt**

```text
127.0.0.1/24 8880 8880 127.0.0.1 8880
127.0.0.1/24 8881 8881 127.0.0.1 8881
127.0.0.1/24 8882 8882 127.0.0.1 8882
127.0.0.1/24 8883 8883 127.0.0.1 8883
127.0.0.1/24 8884 8884 127.0.0.1 8884
127.0.0.1/24 8885 8885 127.0.0.1 8885
127.0.0.1/24 8886 8886 127.0.0.1 8886
```
