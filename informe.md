# Informe — Actividad 5: Forwarding básico

## 1. Funcionamiento

| Archivo | Función |
|---|---|
| `router.py` | Recibe paquetes UDP, consulta rutas y entrega o reenvía mensajes. Incluye las funciones para construir y leer paquetes. |
| `enviar.py` | Envía un mensaje indicando destino final, router de entrada y TTL. |
| `prueba_router.py` | Envía un archivo, con un paquete independiente por línea. |
| `rutas_*.txt` | Definen los siguientes saltos de cada configuración. |
| `mensajes.txt` / `mensajes_grande.txt` | Archivos de entrada para las pruebas. |
| `orden_recibido_ttl.txt` | Registro del orden de llegada observado en la prueba de 200 líneas. |

Cada router abre un socket UDP en la IP y el puerto recibidos y espera de forma bloqueante. Al llegar un paquete:

1. Lee el header con `parse_packet()`.
2. Si el TTL es cero, descarta el paquete y muestra el aviso, incluso si era para él.
3. Si el destino coincide con su dirección, imprime solo el mensaje.
4. Si el destino es otro, consulta `check_routes()`. Sin ruta, descarta el paquete con un aviso.
5. Si encuentra ruta, resta uno al TTL, reconstruye el paquete con `create_packet()` y lo reenvía. El log indica destino final, router actual y siguiente salto.

Después vuelve a esperar. El destino final del header se conserva durante el recorrido y puede ser distinto del router al que el emisor entrega inicialmente el paquete.

## 2. Ejecución

Usamos Python 3.10 o superior y solo bibliotecas estándar: `socket`, `sys`, `ipaddress` y `pathlib`. No se necesita instalar dependencias. Los siguientes comandos se ejecutan desde la carpeta del repositorio; en sistemas que lo requieran se puede usar `python3` en lugar de `python`.

### Red de tres routers

Abrir una terminal distinta para cada comando y mantenerlas ejecutándose:

```text
python router.py 127.0.0.1 8881 rutas_R1_v2.txt
python router.py 127.0.0.1 8882 rutas_R2_v2.txt
python router.py 127.0.0.1 8883 rutas_R3_v2.txt
```

Desde otra terminal, enviar a R3 entrando por R1:

```text
python enviar.py 127.0.0.1 8883 "hola R3" 127.0.0.1 8881 10
```

Los argumentos son `IP_final puerto_final "mensaje" IP_envio puerto_envio TTL`. R3 imprime `hola R3`; R1 y R2 registran los reenvíos. Para probar entrega local, usar 8881 como puerto final; para probar un destino sin ruta, usar 8884. Detener cada router con Ctrl+C al finalizar.

### Envío de archivos

```text
python prueba_router.py "127.0.0.1;8883;10" 127.0.0.1 8881
python prueba_router.py "127.0.0.1;8883;10" 127.0.0.1 8881 otro_archivo.txt
```

El primer argumento contiene `IP_final;puerto_final;TTL`; luego se indica el router inicial. Sin archivo explícito se usa `mensajes.txt`, ubicado junto al script. Las comillas evitan que PowerShell interprete los puntos y coma como comandos separados. El TTL inicial debe estar entre 1 y 255.

### Otras configuraciones

| Tablas | Routers que se deben iniciar | Uso |
|---|---|---|
| `v2` | R1–R3, puertos 8881–8883 | Red lineal de tres routers. |
| `v3` | R1–R5, puertos 8881–8885 | Red original de cinco routers. |
| `v4` | R0–R6, puertos 8880–8886 | Red ampliada, sin default. |
| `v5` | R0–R6 y default en 7000 | Red ampliada con salida default. |

Para cada router se usa el mismo comando, cambiando puerto y archivo. Por ejemplo, R5 en la red de cinco routers se inicia con `python router.py 127.0.0.1 8885 rutas_R5_v3.txt`. El default se inicia con `python router.py 127.0.0.1 7000 rutas_default_v5.txt`.

Para reproducir el error de rutas con TTL, detener los routers anteriores y reiniciar R1/R3 con sus tablas `v2`, y R2 con `rutas_R2_v2_incorrecta.txt`. Después ejecutar:

```text
python enviar.py 127.0.0.1 8883 "prueba de ciclo" 127.0.0.1 8881 10
```

Para el destino externo, iniciar todos los routers con las tablas `v5` y enviar:

```text
python enviar.py 192.0.2.1 9000 "destino externo" 127.0.0.1 8881 10
```

El paquete llega al default y allí se descarta por falta de ruta externa. El envío UDP permanece en localhost.

## 3. Decisiones de diseño

### Tabla simulada y tabla real

Ambas permiten elegir un siguiente salto sin conocer el camino completo. La diferencia que identificamos es cómo agrupan destinos: una tabla real usa prefijos IP e indica el siguiente salto y/o interfaz de salida. En la simulación seguimos el uso de una IP local común y rangos de puertos para distinguir routers. Esto permite representar la red en un solo computador; en una red real, los puertos identifican aplicaciones.

### Formato del paquete y emisores

Seguimos el header sugerido de tamaño fijo: IP de cuatro bytes, puerto de dos y TTL de uno, seguido del mensaje. Usamos big-endian para el puerto y un diccionario con los campos `ip`, `puerto`, `ttl` y `mensaje` para facilitar su lectura y modificación. El mensaje se conserva como bytes hasta su entrega, cuando se decodifica en UTF-8.

Elegimos argumentos de terminal para repetir envíos sin modificar el código. Reutilizamos `create_packet()` en ambos emisores para mantener un solo formato. UTF-8 permite enviar tildes y ñ. Al leer archivos quitamos solo el salto de línea, conservamos espacios y líneas vacías, y asignamos a cada paquete el mismo TTL inicial porque cada línea es un mensaje independiente.

### Round-robin

Guardamos los turnos en un diccionario propio de cada router y lo pasamos a `check_routes()`. Agrupamos las rutas por red y rango de puertos: los destinos de una misma área comparten turno y las otras áreas conservan el suyo. Elegimos la primera área coincidente del archivo y alternamos entre sus siguientes saltos en el orden escrito. El módulo de la cantidad de opciones permite volver al inicio y manejar más de dos rutas.

Usamos `ipaddress` para comprobar pertenencia a la red. Aceptamos la escritura `127.0.0.1/24` del material mediante `strict=False`, que la interpreta como la red `127.0.0.0/24`.

### Router default y tablas resultantes

Creamos las tablas `v5` a partir de `v4` para conservar las configuraciones de las pruebas. Agregamos al final de cada tabla `0.0.0.0/0 0 65535 127.0.0.1 7000`. Como conservamos la primera área coincidente, esa posición da prioridad a las rutas internas. El prefijo /0 y el rango completo de puertos cubren los demás destinos.

La tabla del default tiene una ruta directa a cada router y no incluye una ruta hacia sí mismo. Como no simulamos el resto de Internet, descarta los destinos externos y evita devolverlos a la red. No fue necesario agregar código para este comportamiento.

Cada fila contiene red, puerto inicial, puerto final, IP del siguiente salto y puerto del siguiente salto.

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

## 4. Pruebas y resultados

Las pruebas sin TTL se realizaron antes de incorporarlo. El código entregado es la versión final con TTL; los comandos actuales usan ese formato. Reiniciamos los routers al comenzar cada configuración para partir con los turnos en cero. Los saltos contados corresponden a reenvíos entre routers, sin incluir el envío inicial del script.

### Comprobaciones de implementación

- Construimos paquetes manualmente y comprobamos que `create_packet(parse_packet(paquete))` recupera exactamente sus bytes. Incluimos TTL 0, 1 y 255, mensajes vacíos, binarios y UTF-8.
- Verificamos entrega local, reenvío R1 → R2 → R3 y descarte de un destino sin ruta. Los routers siguieron recibiendo después de los descartes.
- Con destino R3, TTL inicial 1 se descartó en R2, TTL 2 en R3 y TTL 3 permitió la entrega con TTL 1. También comprobamos el descarte de TTL cero para destino local.
- En las redes de cinco y siete routers verificamos la alternancia y los turnos independientes por área, incluyendo tres rutas posibles en R2.
- Con las tablas `v5`, siete paquetes externos, uno desde cada router R0–R6, llegaron al default y se descartaron allí. También comprobamos entrega R1 → R5 y default → R1.
- El archivo predeterminado entregó sus tres líneas por R1 → R2 → R3 con TTL 10. Un archivo alternativo conservó tildes, espacios, líneas vacías y una última línea sin salto final.

### Tabla incorrecta sin TTL
Guardamos el error en `rutas_R2_v2_incorrecta.txt` para conservar la tabla correcta. Mantuvimos las tablas `v2` de R1 y R3 y cambiamos en R2 el siguiente salto hacia el puerto 8883 por el puerto 8881:

```text
127.0.0.1/24 8881 8881 127.0.0.1 8881
127.0.0.1/24 8883 8883 127.0.0.1 8881
```

Enviamos un solo mensaje a R3 entrando por R1. Capturamos doce reenvíos consecutivos alternando R1 → R2 y R2 → R1, sin cambios en los bytes ni en el destino final del paquete. R3 no recibió el mensaje durante la prueba y detuvimos los tres procesos al confirmar el ciclo.

El error hace que R2 devuelva a R1 lo que debería enviar a R3. En esa versión, sin TTL, R1 volvía a elegir R2 y no había una condición que limitara los reenvíos.

### Saltos en cinco routers sin TTL

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

### Saltos en la red ampliada sin TTL

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

### Tabla incorrecta con TTL 10

Repetimos la prueba de tres routers con `rutas_R2_v2_incorrecta.txt`: R2 devuelve a R1 los paquetes destinados a R3. Enviamos un único mensaje a R3 entrando por R1, esta vez con TTL 10.

Observamos diez reenvíos, cinco por router. R1 envió con TTL 9, 7, 5, 3 y 1; R2 con TTL 8, 6, 4, 2 y 0. Al volver a R1 con TTL cero, el paquete se descartó y apareció el aviso correspondiente. R3 no recibió el mensaje.

Sin TTL habíamos detenido la prueba después de capturar doce reenvíos porque el paquete seguía circulando. Con TTL el ciclo terminó por el descarte, sin detener los procesos para frenarlo. El TTL no corrige la tabla ni permite llegar a R3, pero limita cuántos saltos puede consumir un paquete mal encaminado. Detuvimos los tres routers al finalizar la comprobación.

### Orden del archivo grande con TTL

Creamos `mensajes_grande.txt` con 200 líneas numeradas y reiniciamos los cinco routers con las tablas `v3`. Usamos TTL inicial 10 y enviamos el archivo completo sin esperar la llegada de cada línea:

```text
python prueba_router.py "127.0.0.1;8885;10" 127.0.0.1 8881 mensajes_grande.txt
```

En esta ejecución recibimos 187 de las 200 líneas en R5, registramos 13 descartes por TTL cero y 0 entregas duplicadas. Guardamos las líneas entregadas, en orden de recepción, en `orden_recibido_ttl.txt`.

Las primeras veinte llegadas fueron: 3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 4, 8, 46, 12, 16, 5, 20, 24, 28. La línea 43 llegó antes que la 4, aunque se envió después. Detectamos 54 descensos de numeración entre llegadas consecutivas.

Los paquetes pueden tomar caminos distintos por round-robin y algunos vuelven a routers anteriores. Por eso, el orden de envío no garantiza el orden de llegada: una línea posterior puede completar antes su recorrido. El TTL limita los saltos, pero no ordena ni retransmite mensajes. Los resultados corresponden a esta ejecución y pueden variar según cómo se intercalen los procesos. Detuvimos los cinco routers al finalizar.
