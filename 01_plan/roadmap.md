# Roadmap por ciclos

Regla: **solo el ciclo activo está planificado en detalle.** Los siguientes existen
como dirección, no como plan. Se concretan al abrirlos. Si esta lista empieza a crecer
hacia abajo con detalle, es la señal de que estoy buscando el plan perfecto otra vez.

Presupuesto: ~14 h por ciclo (1 h/día, desde el 20-oct; antes 2 h/día).

## Calendario real

> [!warning] Vacaciones 10 → 27 de septiembre
> Sin ordenador. **No se planifica trabajo dentro de ese hueco.** Un proyecto que
> exige trabajar en vacaciones el primer mes no llega al mes doce.

| Ciclo   | Fechas          | Objetivo                                       | Review            |
| ------- | --------------- | ---------------------------------------------- | ----------------- |
| **C00** | 2 → 9 sep       | Kickoff con mentores + primeras medidas        | mar 8 o mié 9 sep |
| —       | 10 → 27 sep     | *Vacaciones*                                   | —                 |
| **C01** | 28 sep → 11 oct | Modelo longitudinal antes que datos (pivote 8-oct) — **hecho** | vie 9 oct |
| **C02** | 20 → 30 oct     | Motor + inversor: **modelar y saber explicarlo**. Nada de validar. Ver [C02](C02.md) | **vie 30 oct** |
| **C03** | 31 oct → 13 nov | Modelo dq (L3), primer control (lazo abierto/cerrado, PI) y el motor en Simulink (L4). Plan en Google Calendar (25-oct); artifacts aún sin construir | vie 13 nov        |
| **C04** | 14 → 27 nov     | Dirección (1-nov): validar el modelo de motor con los logs CAN | vie 27 nov        |
| **C05** | 28 nov → 11 dic | Dirección: validación del vehículo (coast-down, aceleración) con el registrador | vie 11 dic        |
| **C06** | 12 → 25 dic     | Dirección: cerrar el modelo validado; unidad de control v0 si cabe. Navidad: probablemente se mueve | vie 25 dic |

**Secuencia decidida el 20-oct:** modelo de motor + inversor → data logger → validación
(coast-down, correlación modelo ↔ vehículo). Sin logger no hay datos y sin datos no se valida.

**Actualizada el 1-nov:** el registrador CAN se adelantó y funciona (31-oct, EXP-002), así
que el eslabón de los datos ya está. Orden acordado con Pol:

1. **C03 sin cambios:** modelo dq y lazo PI en Simulink. Inversor y motor.
2. **Validar el motor con los logs:** corriente, erpm, ciclo de trabajo y tensión del VESC
   contra el modelo (p. ej. ciclo × tensión frente a erpm debe dar λm).
3. **Unidad de control v0** (dic–ene): acelerador → ESP32 → orden de corriente por CAN →
   VESC. Sin control, con las protecciones en el código. Revisar DEC-004 antes.
4. **IMU y velocidad de rueda** registradas en la SD.
5. **Control de tracción:** primero en Simulink, después en el ESP32.

**Fuera, por decisión de Pol:** el BMS por CAN (el VESC ya da tensión y corriente del pack;
el foco es motor e inversor). Recordatorio: la unidad de control enseña control de vehículo
y C embebido, no inversor; el inversor se aprende en el modelo.

**Fin de 2026: modelo validado contra el vehículo real.** Ese es el objetivo del año.

Después de C06 (no antes): control de tracción, launch control, y **entonces** MPC —
que requiere exactamente lo que C06 produce, un modelo validado.

### Horizonte largo — una línea por trimestre, y nada más

Deliberadamente vago. Concretarlo ahora sería buscar el plan perfecto.

| Trimestre | Dirección |
|---|---|
| **T4 2026** (C01–C06) | Del hardware medido a un modelo validado |
| **T1 2027** | Control implementado: del modelo al ESP32. Aquí entra el firmware en serio |
| **T2 2027** | Funciones de vehículo: tracción, launch. Y MPC si el modelo aguanta |
| **T3 2027+** | El quad es plataforma: percepción, autonomía, lo que aparezca |

## Cómo funciona un ciclo

El ciclo es el motor del proyecto. Sin ritual, es solo el nombre de una carpeta.

> [!todo] Apertura — 1 sesión, el día después de la review
> 1. Leer el cierre del ciclo anterior. Qué salió mal se arrastra, no se olvida.
> 2. Elegir **un** objetivo. Uno. Si necesita un "y", son dos ciclos.
> 3. Definir el entregable: qué se enseña el día de la review.
> 4. Escribir el plan diario. 14 bloques de 2 h.
> 5. Todo lo que no quepa → `backlog.md`.

> [!tip] Durante — cada sesión
> Cerrar escribiendo **una línea** en la bitácora: qué hice, qué aprendí, qué queda.
> Es la costumbre más barata y de más valor del sistema. Sin ella, cada sesión
> empieza a ciegas.

> [!success] Cierre — últimas sesiones antes de la review
> 1. Rellenar Resultado / Qué aprendí / Qué salió mal.
> 2. **Examen del ciclo** (`C0X-examen.md`): Claude pregunta, yo respondo de memoria,
>    veredicto por respuesta. **Mis respuestas corregidas son el guion del deck.**
> 3. Acordar la lista de slides **antes** de que se construya nada (lección de C01).
> 4. Deck con la skill `review-deck`: `_check.py` y `_audit.py` a cero antes de presentar.
> 5. Ensayar en voz alta con la pregunta probable de cada slide (notas del orador).
> 6. Si no lo sé explicar sin apuntes, **no está terminado**.

### La review, en 45 minutos

Sus mentores son ingenieros de motores térmicos: no pueden validar el FOC, pero sí
el razonamiento de ingeniería. El formato aprovecha lo que sí saben:

| Tiempo | Qué |
|---|---|
| 5 min | Qué dije que haría |
| 15 min | Qué he hecho, con datos |
| 10 min | **Lo que no entiendo** — la parte más valiosa |
| 10 min | Crítica: ¿el razonamiento se sostiene? |
| 5 min | Objetivo del siguiente ciclo |

Los 10 minutos de "lo que no entiendo" son el núcleo. Enseñar solo lo que funciona
convierte la review en un teatro y desperdicia a dos doctores.

## Cómo mido si esto funciona

El objetivo es "ser mejor ingeniero", que no se mide. Estos cuatro indicadores sí,
y se revisan **cada 3 ciclos**, no cada semana:

1. **¿Puedo explicar algo hoy que hace 6 semanas no?** Sin apuntes, a alguien que no
   sabe del tema. Es el único indicador que importa de verdad.
2. **¿El modelo predice mejor?** A partir de C06, el error de correlación es un número
   que baja o no baja. No admite autoengaño.
3. **¿Cuántos ciclos he cerrado en fecha?** Mide el sistema, no el conocimiento.
   Si van dos seguidos fallando, el problema es el plan, no yo.
4. **¿Cuántas decisiones tengo escritas con su porqué?** Mide si estoy haciendo
   ingeniería o solo tocando cosas.

> [!warning] Lo que NO se mide
> Horas invertidas, archivos escritos, líneas de código, commits. Todo eso se puede
> subir sin aprender nada. Optimizar un indicador falso es peor que no medir.

## Por qué este orden

Cada ciclo consume la salida del anterior. C02 no puede empezar sin los números de C01.
C04 no significa nada sin la máquina de C03. MPC no es implementable sin C06.

No es una secuencia arbitraria: es la cadena de dependencias real. Saltarse un eslabón
produce un sistema que parece funcionar y que no se puede depurar, porque no sabes qué
capa está mintiendo.

## El data logger: por qué NO va primero, y la excepción

> [!note] Historia
> Escrito antes de construirlo. El registrador existe desde el 31-oct-2026 y graba con
> carga sin depender del USB del VESC: lo de abajo queda como razonamiento de entonces.

**El problema real:** hoy solo puedo registrar con el motor en vacío. Con el vehículo
funcionando, el USB del VESC se corta bajo carga. Para logs con carga haría falta un
data logger propio con ESP32 — que no existe todavía.

**¿Habría que construirlo primero, entonces?** No, y por dos razones:

1. **C01 no lo necesita.** R de fase, pares de polos y back-EMF se miden con el motor
   parado o girando a mano. Multímetro y osciloscopio. Cero software.
2. **No sé aún qué medir.** Un logger se diseña a partir de las señales que el modelo
   pide. Construirlo antes del modelo es adivinar qué canales, a qué frecuencia y con
   qué resolución — y equivocarse sale caro en semanas de trabajo embebido.

**La excepción que sí merece adelantarse (30 minutos):** diagnosticar el corte de USB.
El síntoma es "bajo carga" → apunta a EMI de la conmutación de fase o a bucle de tierra.
Pero hay un detalle que cambia el cálculo: **un ensayo de coast-down es, por definición,
sin par** — acelerar, soltar, y dejar que el vehículo decelere solo. Con corriente de
fase casi nula, es plausible que el USB **no** se corte.

Y el coast-down es exactamente el ensayo de validación que necesita C02.

Por tanto, antes de dar por hecho que hace falta el logger: probar un coast-down
registrando por USB. Si funciona, **C02 se valida sin construir nada** y el logger se
queda donde está, en C05. Si no funciona, ya tengo el dato con certeza en vez de con
una suposición — y sé que el logger es un bloqueante real.

Media hora de osciloscopio en D+/D- y en el raíl de 5 V durante una rampa de carga
completa el diagnóstico. Ver `03_hardware/open-questions.md`.

## Lo que cambia ahora que sé qué toolboxes tengo

Verificado el 2026-09-01: la licencia de estudiante trae **las 40 toolboxes**,
incluidas Motor Control Blockset, Simscape Electrical, Vehicle Dynamics Blockset,
Powertrain Blockset, MPC Toolbox y Embedded Coder. Ver `08_decisions/DEC-002-entorno-tecnico.md`.

Esto no acelera el roadmap. Lo hace **más peligroso**, y conviene decirlo claro:

Motor Control Blockset trae FOC para PMSM ya hecho. Arrastrar ese bloque da un quad que
funciona y un ingeniero que no ha aprendido nada. El objetivo declarado del proyecto es
entender FOC, no usarlo.

**Regla para todo el roadmap:** primero lo construyo desde las ecuaciones, después lo
comparo contra la implementación de referencia. La diferencia entre mi versión y la suya
es el contenido de aprendizaje — ahí está lo que no sabía que no sabía.

Dos consecuencias concretas:
- **C03/C04:** construir Clarke, Park y los lazos de corriente a mano antes de abrir
  ningún ejemplo de MCB.
- **MPC (post-C06):** deja de ser inalcanzable. MPC Toolbox está. Sigue necesitando el
  modelo validado de C06, así que la secuencia no cambia — solo deja de ser un horizonte
  lejano y pasa a ser un objetivo real a ~6 meses.

## Qué NO está en este roadmap, a propósito

Rediseño mecánico, montaje de batería, soportes, chasis. El hardware es la planta y el
banco de validación, no el objeto de trabajo. Cambios de hardware, sí — cuando el modelo
o los datos los pidan, no por iniciativa propia.
