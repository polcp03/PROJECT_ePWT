# Software — lo que sé explicar

Cómo se trabaja: skill `software-con-ia`. Yo pongo el contrato y la prueba; la IA escribe el código.
Aquí van mis respuestas ya corregidas.

## ¿Cómo sé que un programa embebido está bien sin leer el código? (2-nov-2026)

**Lo que dije:** leo dos nodos de CAN, hago una prueba (acelero, el motor se mueve), veo que lo que
hago se correlaciona con lo que leo y no hay errores de CAN. Si el resultado es bueno, no hace falta
leer cómo está hecho.

**Corrección.** El instinto es el bueno, y es el de un calibrador: comprobar contra la realidad física.
Pero se queda en el escalón 3 de 6 (escalera en la skill `software-con-ia`):

- "Plausible" no es un criterio. Hace falta un número: **0 tramas perdidas** y la frecuencia de
  tramas igual a la que tiene configurada el VESC.
- "No hay errores" solo vale si hay algo que los cuenta. Mi `can_logger` sí los cuenta:
  `queue drops`, `hw overflows`, `SPI err` y los contadores de error del controlador de CAN
  (`RX err`, `TX err`). La prueba es que sigan a 0. **El contrato tiene que exigir esos contadores**: sin ellos,
  un fallo es invisible.
- Una prueba de dos minutos no ve los fallos lentos: un contador de tiempo de 32 bits en
  microsegundos vuelve a 0 a los **71,6 minutos**. Hay que aguantar 30 minutos o más a carga máxima.
- Y hay que provocar los fallos: desconectar el cable, apagar un nodo, llenar la SD. ¿Qué hace?

**Bien dicho, en una frase:** sin leer el código me fío de él si cumple un criterio con número, lo
mantiene en una prueba larga y tiene contadores que demuestran que no ha fallado nada.
