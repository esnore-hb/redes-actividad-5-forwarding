# Informe — Actividad 5: Forwarding básico

## 1. Comparación entre la tabla de rutas de la actividad y una tabla real

Ambas tablas indican a qué siguiente salto enviar un paquete según su destino, sin necesidad de conocer el camino completo.

En la actividad, los routers usan la misma IP local y se distinguen por sus puertos. Por eso, las tablas incluyen rangos de puertos para agrupar destinos y un par (IP, puerto) como siguiente salto. En una tabla real, los destinos se agrupan mediante prefijos IP y se indica el siguiente salto y/o la interfaz de salida; los puertos identifican aplicaciones. Esta simplificación permite simular la red en un solo computador.
