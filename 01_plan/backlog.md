# Backlog — todo lo que NO se hace ahora

Destino único de las ideas. Si algo no cabe en el ciclo activo, viene aquí y se sale
de la cabeza. Nada de esto está descartado; está **aplazado con criterio de entrada**.

Regla: una entrada solo se activa cuando se cumple su condición, y entonces se
convierte en el objetivo de un ciclo.

---

## Proyectos separados (fuera de este repo, por decisión propia)

**Second brain personal + LLM sobre él.** Conocimiento de universidad, Formula Student,
calibración, trabajo, proyectos. Obsidian como candidato. Referencia mencionada:
el trabajo de Karpathy sobre wiki/LLM en GitHub.
*Por qué fuera:* es un proyecto de gestión del conocimiento, no de ingeniería de
powertrain. Mezclarlo aquí fue la causa de la saturación inicial.
*Nota:* `02_knowledge/` de este repo ya es Markdown plano y se puede abrir con cualquier visor
sin conversión. El second brain personal puede absorberlo más adelante.

**Agentes de información / actualidad.** Síntesis semanal sobre robótica, defensa,
drones, semiconductores, IA, ecosistema israelí, y referentes técnicos concretos.
*Argumento a favor (suyo, válido):* no quiere perder tiempo en redes; prefiere
señal filtrada de gente cuyas acciones tienen consecuencias reales.
*Riesgo a vigilar:* una síntesis que se acepta sin cuestionar es cognición delegada.
Si se construye, debe entregar **fuentes + preguntas**, no conclusiones.

---

## Dentro de este proyecto, más adelante

| Idea | Condición de entrada |
|---|---|
| **Agente examinador** (alimentado con libros de texto, me cuestiona antes de las reviews) | Que exista material de referencia elegido y ≥3 ciclos de rutina que codificar |
| ~~**Skills propias**~~ | **Activado 2026-10-25:** `review-deck`, `leccion` y `corregir` existen. Siguientes (analizar datos, documentar decisión): misma regla, 3 veces a mano |
| **CI: compilar el firmware en cada push** | Que haya firmware propio en el repo |
| **Logger de telemetría propio (ESP32 + CAN)** | Que el gemelo necesite datos que el VESC Tool no da. Revisar VESC Express antes de escribir nada |
| **Dashboard / análisis en Python de los logs** | Que existan los primeros CSV |
| **Hook de fin de sesión: avisar de trabajo sin commitear** | Haber cerrado 3 sesiones más olvidando el commit. Ver la nota de abajo |
| **Control de tracción, launch control** | Modelo validado + control de par funcionando |
| **MPC** | Modelo validado. MPC sin modelo es imposible por definición |
| **Percepción, cámaras, autonomía, robot acompañante** | Muy lejos. Mantener como horizonte, no planificar |
| **Diagnóstico del corte de USB del VESC bajo carga** | Fallo conocido en la comunidad VESC (EMI / bucle de tierra / pull-ups). 30 min de osciloscopio antes de construir nada para evitarlo |
| **Decidir `l_in_current_max` (hoy 40 A = límite continuo del BMS)** | Salió del modelo C01: por encima de 9 km/h cada aceleración a fondo va pegada a 40 A. Llevado a la review C01 como pregunta a los mentores |
| **Medir `R_int` del pack** | Caída de tensión ante un escalón de corriente en un log del VESC. Hoy ASSUMED 0,10 Ω sin datasheet |
| **`si_wheel_diameter` 0,30 m vs `2·r_roll` 0,31 m** | Decidir cuál vale cuando se haga el roll-out con neumáticos nuevos |
| **Altura del CG (`h_cg`)** | MISSING. La necesita el load transfer del L2 (examen C01, bloque I) |
| **EXP-001 (bucle de tierra) sin medir** | Sigue sin día. Antes de montar el ESP32 nuevo: M1 y M2 son 20 min de multímetro |

---

## Hacia robótica — apuntado el 30 de octubre de 2026, sin plan

Decidido: el quad tiene que acabar enseñando **software de robot**, no solo física. Las
startups de robótica piden C++, Linux, ROS 2 y comunicaciones, y hoy el repositorio no tiene
código que lo demuestre. La idea no es añadir un proyecto al lado, sino **construir lo que el
quad ya necesita con las herramientas de la robótica**. Nada de esto se planifica todavía: se
concreta al abrir el ciclo que toque, y se decide juntos.

| Idea | Cuándo, y por qué ahí |
|---|---|
| **Registrador de datos con ROS 2.** Ordenador Linux pequeño (tipo Raspberry Pi) que lee el VESC por CAN, publica la telemetría como topics de ROS 2, la graba en rosbag y se ve con Foxglove | Sustituye al logger con ESP32 de arriba, que ya hacía falta para validar (C05). Una sola pieza enseña Linux, C++ o Python, ROS 2, CAN y git, y deja código público |
| **Fusión de sensores.** Unidad inercial + velocidad de rueda en un filtro de Kalman extendido, para tener la velocidad y la posición reales del quad | Primer trimestre de 2027, con el registrador funcionando. Sirve para validar el modelo y es la pregunta de Kalman de cualquier entrevista |
| **Control en el hardware, en C/C++.** El lazo de control del modelo, escrito y corriendo en el microcontrolador | Primer trimestre de 2027, ya en el roadmap. Es lo que convierte "sé Simulink" en "sé hacer firmware" |
| **Lidar, cámara, gemelo digital con sensores, autonomía** | **No antes de 2027, y solo si es útil de verdad**: cuando haya una pregunta que el quad no pueda contestar sin ellos. Sin cadena de percepción detrás es una demo, no ingeniería. La autonomía exige además un actuador de dirección, que es hardware nuevo |

---

## Higiene de Git: qué automatizar y qué no

> **Actualizado el 2026-10-30: ya se automatiza, con revisión.** Pol decidió que no quiere
> hacer el trabajo de git a mano: lo hace un agente y él es el revisor. La tarea
> «Sincronizar con GitHub» (cada noche, 22:00, en el PC) agrupa los cambios por tema en
> commits con su porqué, abre un Pull Request y Pol lo fusiona. Eso responde a la objeción
> de abajo: el criterio lo pone el agente y Pol lo valida en el PR, en vez de un commit
> automático a ciegas. Procedimiento en `../prompts/sincronizar.md`. Lo de abajo queda
> como historia.

Abierto el 2026-09-09, tras una operación de rescate: 46 archivos nuevos y 24
modificados llevaban hasta dos semanas sin commitear. Todo el trabajo técnico de C00
—caracterización del motor, inercia, EXP-001, decks— vivía solo en el disco.

**Fontanería, hecho o inmediato.** No requiere criterio, así que se automatiza sin
debate: `push.autoSetupRemote` (mata el `-u` de la primera subida), `fetch.prune`
(limpia referencias a ramas remotas muertas), y en GitHub desactivar el squash merge
y activar el borrado de rama al mergear.

Lo del squash no es cosmético: el PR #4 aplastó 7 commits temáticos en uno solo
titulado como el primero de ellos, así que ahora `a3e6f9b` dice "versiona la config
del VESC" y contiene además el motor, la inercia, EXP-001 y las presentaciones.
El contenido está intacto; la trazabilidad no. Desactivar la opción en el repo hace
el error irrepetible, que es mejor que recordar no cometerlo.

**Criterio, NO se automatiza.** Agrupar los cambios por tema y escribir por qué el
VESC se queda un 5,5 % corto en λm son decisiones de ingeniería. Un commit automático
produciría exactamente la historia inútil que este proyecto intenta evitar.

**El punto intermedio, aplazado.** El fallo real fue olvidarse, no no saber. Un hook
de fin de sesión que *avise* (nunca que commitee) es la herramienta correcta. Pero
aplica la regla de entrada de las skills propias: tres repeticiones a mano antes de
codificar nada. Va una.

Mientras tanto, la disciplina es manual: al cerrar sesión, `add` por tema → `commit`
→ `push`, aunque el trabajo esté a medias. Un WIP con mensaje honesto vale más que
46 archivos en el limbo.

---

## Marca personal, contenido y empresa

Reconocido como objetivo real a largo plazo. **Cero acción de investigación ahora.**

- **LinkedIn:** activo, pero como *subproducto*. Cada review con mentores produce
  material; publicar es copiar y traducir, no un proyecto aparte. Sin agente.
- **Portfolio para entrevistas — decidido el 2026-10-30.** Tres piezas, en este orden de
  importancia: (1) **este repositorio público** (`polcp03/epwt`), que se actualiza solo;
  (2) **una presentación** que cuente el proyecto y lo hecho, sacada de los decks de las
  reviews; (3) **un vídeo de 30 segundos** para enseñar a la gente: el quad, el gemelo
  digital y un número medido, sin explicar teoría. Para el vídeo, **graba desde ya** clips
  cortos de cada hito (el banco, una medida en el osciloscopio, el modelo corriendo): el
  material que no se graba cuando pasa ya no se puede grabar después. Se monta cuando haya
  una entrevista cerca o cuando el quad se mueva con control propio.
- **YouTube / newsletter / formación:** más adelante. Doble función reconocida —
  construir marca y forzar comprensión real. La excusa del vídeo es aprender a
  explicar y perder vergüenza; ese objetivo ya lo cubren las presentaciones por ahora.
- **Empresa tecnológica (robótica u otra):** horizonte a años. Primero: conocimiento,
  experiencia, entender sectores y detectar problemas reales. No forzar una idea.
- **Organización AI-first como laboratorio:** aprender a trabajar con IA como capa
  común de conocimiento antes de tener equipo. Este repo ya es la versión mínima.
