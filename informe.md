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
