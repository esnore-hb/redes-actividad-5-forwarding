# Informe — Actividad 5: Forwarding básico

## 1. Comparación entre la tabla de rutas de la actividad y una tabla real

Al comparar las tablas, identificamos que ambas resuelven la misma pregunta: a qué siguiente salto enviar un paquete según su destino. El router no necesita conocer el camino completo.

La diferencia principal que observamos es cómo se representan los destinos. En una tabla real se agrupan mediante prefijos IP y se indica el siguiente salto y/o la interfaz de salida. En el modelo de la actividad usamos la misma IP local y distinguimos los routers por sus puertos, por lo que las tablas incluyen rangos de puertos. Seguimos esta simplificación para simular la red en un solo computador; en una red real, los puertos identifican aplicaciones.

## 2. Script de envío (ítem 5)

Elegimos recibir los datos como argumentos de terminal para poder repetir los envíos sin modificar el código. En la versión sin TTL colocamos primero el destino final, luego el mensaje y al final el router de entrada:

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

## 5. Prueba de una tabla incorrecta sin TTL

Guardamos el error en `rutas_R2_v2_incorrecta.txt` para conservar la tabla correcta. Mantuvimos las tablas `v2` de R1 y R3 y cambiamos en R2 el siguiente salto hacia el puerto 8883 por el puerto 8881:

```text
127.0.0.1/24 8881 8881 127.0.0.1 8881
127.0.0.1/24 8883 8883 127.0.0.1 8881
```

Enviamos un solo mensaje a R3 entrando por R1. Capturamos doce reenvíos consecutivos alternando R1 → R2 y R2 → R1, sin cambios en los bytes ni en el destino final del paquete. R3 no recibió el mensaje durante la prueba y detuvimos los tres procesos al confirmar el ciclo.

El error hace que R2 devuelva a R1 lo que debería enviar a R3. Como R1 vuelve a elegir R2 y todavía no hay TTL, el código no tiene una condición que limite esos reenvíos.

## 6. Saltos en la red de cinco routers sin TTL

Iniciamos los cinco routers con las tablas `v3` y los turnos en cero. Enviamos ocho mensajes distintos de R1 a R5, uno por uno, esperando cada entrega para identificar sus reenvíos. Contamos solo los saltos entre routers; el envío inicial del script a R1 no se incluye.

| Paquete | Recorrido observado | Saltos |
|---|---|---:|
| 1 | R1 → R2 → R3 → R2 → R4 → R2 → R3 → R5 | 7 |
| 2 | R1 → R2 → R4 → R5 | 3 |
| 3 | R1 → R2 → R3 → R2 → R4 → R2 → R3 → R5 | 7 |
| 4 | R1 → R2 → R4 → R5 | 3 |
| 5 | R1 → R2 → R3 → R2 → R4 → R2 → R3 → R5 | 7 |
| 6 | R1 → R2 → R4 → R5 | 3 |
| 7 | R1 → R2 → R3 → R2 → R4 → R2 → R3 → R5 | 7 |
| 8 | R1 → R2 → R4 → R5 | 3 |

Los ocho mensajes llegaron, pero sus recorridos variaron entre 3 y 7 saltos. El mínimo de la topología es tres: R1 → R2 → R3 → R5, o por R4 en lugar de R3. Los recorridos más largos volvieron a pasar por routers anteriores antes de llegar.

Comprobamos que R2 alternó entre R3 y R4 en sus 16 reenvíos, incluyendo las visitas repetidas de un mismo paquete. Esto explica que no haya necesariamente una única elección de R2 por mensaje. Observamos que round-robin reparte los siguientes saltos, pero no selecciona el camino mínimo. Estos resultados corresponden a esta secuencia de envíos; no garantizan la entrega de cualquier paquete sin TTL.

## 7. Saltos en la red ampliada sin TTL

Reiniciamos los siete routers con las tablas `v4` y los turnos en cero. Intercalamos seis mensajes R1 → R5 y seis R5 → R1, esperando cada entrega antes del siguiente envío. Contamos únicamente los reenvíos entre routers.

| Paquete | Sentido | Recorrido observado | Saltos |
|---|---|---|---:|
| 1 | R1 → R5 | R1 → R2 → R3 → R2 → R4 → R2 → R6 → R2 → R3 → R5 | 9 |
| 2 | R5 → R1 | R5 → R4 → R2 → R1 | 3 |
| 3 | R1 → R5 | R1 → R2 → R4 → R5 | 3 |
| 4 | R5 → R1 | R5 → R3 → R2 → R0 → R1 | 4 |
| 5 | R1 → R5 | R1 → R2 → R6 → R2 → R3 → R2 → R4 → R2 → R6 → R2 → R3 → R5 | 11 |
| 6 | R5 → R1 | R5 → R4 → R5 → R3 → R5 → R4 → R2 → R1 | 7 |
| 7 | R1 → R5 | R1 → R2 → R4 → R5 | 3 |
| 8 | R5 → R1 | R5 → R3 → R2 → R0 → R1 | 4 |
| 9 | R1 → R5 | R1 → R2 → R6 → R2 → R3 → R2 → R4 → R2 → R6 → R2 → R3 → R5 | 11 |
| 10 | R5 → R1 | R5 → R4 → R5 → R3 → R5 → R4 → R2 → R1 | 7 |
| 11 | R1 → R5 | R1 → R2 → R4 → R5 | 3 |
| 12 | R5 → R1 | R5 → R3 → R2 → R0 → R1 | 4 |

Los doce mensajes llegaron. El mínimo sigue siendo tres saltos en ambos sentidos. De R1 a R5 observamos entre 3 y 11 saltos. De R5 a R1 observamos entre 3 y 7 saltos. Los recorridos con vueltas superaron ese mínimo; agregar alternativas no hizo que round-robin eligiera siempre el camino más corto.

En R2 comprobamos turnos independientes: R3–R4–R6 hacia el área de R5 y R1–R0 hacia el área de R1. Las vueltas de un paquete también avanzaron el turno de su área. Al terminar detuvimos los siete procesos.

Usamos los puertos 8880 y 8886 para R0 y R6. En sus tablas agregamos rutas hacia sus vecinos y, para los demás destinos, un siguiente salto que permite continuar el recorrido. Estas son las siete tablas utilizadas, sin ruta default:

**rutas_R0_v4.txt**

```text
127.0.0.1/24 8881 8881 127.0.0.1 8881
127.0.0.1/24 8882 8886 127.0.0.1 8882
```

**rutas_R1_v4.txt**

```text
127.0.0.1/24 8880 8880 127.0.0.1 8880
127.0.0.1/24 8882 8886 127.0.0.1 8882
```

**rutas_R2_v4.txt**

```text
127.0.0.1/24 8880 8881 127.0.0.1 8881
127.0.0.1/24 8880 8881 127.0.0.1 8880
127.0.0.1/24 8883 8886 127.0.0.1 8883
127.0.0.1/24 8883 8886 127.0.0.1 8884
127.0.0.1/24 8883 8886 127.0.0.1 8886
```

**rutas_R3_v4.txt**

```text
127.0.0.1/24 8880 8882 127.0.0.1 8882
127.0.0.1/24 8880 8882 127.0.0.1 8885
127.0.0.1/24 8884 8885 127.0.0.1 8882
127.0.0.1/24 8884 8885 127.0.0.1 8885
127.0.0.1/24 8886 8886 127.0.0.1 8886
```

**rutas_R4_v4.txt**

```text
127.0.0.1/24 8880 8883 127.0.0.1 8882
127.0.0.1/24 8880 8883 127.0.0.1 8885
127.0.0.1/24 8885 8885 127.0.0.1 8882
127.0.0.1/24 8885 8885 127.0.0.1 8885
127.0.0.1/24 8886 8886 127.0.0.1 8882
```

**rutas_R5_v4.txt**

```text
127.0.0.1/24 8880 8884 127.0.0.1 8884
127.0.0.1/24 8880 8884 127.0.0.1 8883
127.0.0.1/24 8886 8886 127.0.0.1 8883
```

**rutas_R6_v4.txt**

```text
127.0.0.1/24 8880 8882 127.0.0.1 8882
127.0.0.1/24 8883 8883 127.0.0.1 8883
127.0.0.1/24 8884 8885 127.0.0.1 8882
```

## 8. Incorporación del campo TTL

Seguimos la distribución sugerida: cuatro bytes de IP, dos de puerto y uno de TTL, antes del mensaje. Mantener posiciones fijas nos permite separar el header sin delimitadores. `parse_packet()` devuelve el TTL como entero y `create_packet()` lo escribe en un byte; el mensaje sigue siendo bytes.

Agregamos el TTL al final de los argumentos del emisor para conservar el orden anterior. Su interfaz actual es:

```text
python enviar.py IP_final puerto_final "mensaje" IP_envio puerto_envio TTL
python enviar.py 127.0.0.1 8883 "hola" 127.0.0.1 8881 10
```

El emisor exige un TTL inicial entre 1 y 255. Las funciones de paquetes también admiten cero, porque un paquete puede alcanzar ese valor durante el recorrido. Construimos manualmente un paquete con TTL 10 y comprobamos que parsearlo y reconstruirlo recupera exactamente sus bytes. También probamos TTL 0, 1 y 255, mensajes vacíos, binarios y UTF-8, y la recepción UDP del paquete generado por el emisor. En esta etapa todavía no disminuimos el TTL ni descartamos paquetes por su valor.
