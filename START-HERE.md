# ePWT — empieza aquí

Banco de aprendizaje de powertrain eléctrico. **El quad es la planta física, Simulink es
el gemelo digital, y el ciclo de dos semanas con mentores es el motor de progreso.**
Objetivo 0: convertirme en mejor ingeniero, desde primeros principios, con un portfolio
que lo demuestre.

## Hoy

**C02 — Motor + inversor, solo modelo · review vie 30 oct.** Detalle en [C02](01_plan/C02.md).

| Día | Tarea (45–60 min) | Abrir |
|---|---|---|
| mar 27 | L1 · De la batería al par | [lección](https://claude.ai/artifact/F5pNX14PcUEVxtYv8zrwpN) |
| mié 28 | L2 · El campo que gira | [lección](https://claude.ai/artifact/Fxcfde7icEog8iBLodXWTp) |
| jue 29 | Examen L1+L2 y acordar slides | [examen](https://claude.ai/artifact/2o9NrZ6BgGsVTbg18AX3rZ) |
| vie 30 | Review con mentores | deck en `01_plan/presentations/` |

Haz solo la fila de hoy. El día exacto también está en Google Calendar (07:00).

## Dónde está cada cosa

| Carpeta | Qué hay | ¿La abro? |
|---|---|---|
| `01_plan/` | Ciclo activo, roadmap, backlog, decks. `cerrados/` = ciclos terminados | **A diario** |
| `02_knowledge/` | Lo que he aprendido, en mis palabras, y mis errores | Antes de cada examen |
| `03_hardware/` | El quad: lo medido. Fuente de verdad | Cuando necesito un número |
| `04_model/` | Simulink: gemelo digital | En las tareas de modelo |
| `05_firmware/` | ESP32 / Arduino. **Registrador CAN funcionando** (`arduino/can_logger/`) | Al grabar |
| `06_data/` | Ensayos por campaña | Cuando haya datos |
| `07_experiments/` · `08_decisions/` | Hipótesis → medida; decisiones con su porqué | Al cerrar algo |
| `../BOOKS/` | Biblioteca, en la raíz del repositorio (fuera de Git). Índice en [fuentes](02_knowledge/fuentes.md) | Lo filtra Claude |

## Mis tres reglas

1. **Solo existe el ciclo activo.** Toda idea nueva va a [backlog](01_plan/backlog.md).
2. **Si un día se cae, se cae.** No se recupera acumulando.
3. **Si importa, se escribe y se commitea.** Cerrar cada sesión con una línea en la
   bitácora del ciclo y un commit.

## Seguridad — no negociable

Batería 13S5P Li-ion. Picos de **~40 A** contra una asunción de diseño de 25 A, y el
BMS corta a 40 A continuos. Ningún ensayo de corriente alta sin: límite configurado en
el VESC · comprobar temperatura del pack al terminar · **nunca cargar sin supervisión**.

## Si eres una sesión nueva

1. `CLAUDE.md` — cómo trabajar con Pol (modo ingeniero senior, cerebro primero).
2. Este archivo — qué toca hoy.
3. El ciclo activo en `01_plan/`.
4. Si el trabajo cae en `04_model/` o `05_firmware/`, lee su `CLAUDE.md` antes de responder.
5. Lecciones → skill `leccion`. Corregir respuestas → skill `corregir`. Deck → skill `review-deck`.
