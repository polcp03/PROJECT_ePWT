# ePWT — empieza aquí

Banco de aprendizaje de powertrain eléctrico. **El quad es la planta física, Simulink es
el gemelo digital, y el ciclo de dos semanas con mentores es el motor de progreso.**
Objetivo 0: convertirme en mejor ingeniero, desde primeros principios, con un portfolio
que lo demuestre.

## Hoy

**C02 + C03 — Motor, inversor y primer lazo de corriente · review vie 13 nov.** Detalle en [C03](01_plan/C03.md).

Dos tareas al día hasta el 13, a las **07:00** y a las **14:00**.

| Día | 07:00 | 14:00 |
|---|---|---|
| mar 3 | L1 · [Batería → par](https://claude.ai/artifact/F5pNX14PcUEVxtYv8zrwpN) | L2 · [El campo que gira](https://claude.ai/artifact/Fxcfde7icEog8iBLodXWTp) |
| mié 4 | [Examen L1+L2](https://claude.ai/artifact/2o9NrZ6BgGsVTbg18AX3rZ) | L3a · [Park y dq](https://claude.ai/artifact/LcqqugrE6jFi8U22KqKPCM) |
| jue 5 | L3b · [Par y límites](https://claude.ai/artifact/2metZHTgmmyaxgZu6usJpL) | Control 1 · [Lazo abierto y cerrado](https://claude.ai/artifact/GKUX9KpwnF92yySFnHHfpL) |
| vie 6 | Control 2 · [El PI](https://claude.ai/artifact/Vu428jai3Yqk2PmyCk3epu) | — |
| sáb 7 | [Kp y Ki a mano](https://claude.ai/artifact/U5QxEKTCLnBLrPNoyWQQvz) (10:00) | Repaso de fallos |
| mar 10 | Simulink A · Tu motor en dq | λm con tus logs |
| mié 11 | Simulink B · Cierra el lazo | Hueco libre |
| jue 12 | Examen C03 | Acordar slides |
| vie 13 | **Review con mentores** | |

Haz solo la fila de hoy. Los enlaces que faltan llegan al calendario el día antes.

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
