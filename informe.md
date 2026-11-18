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
