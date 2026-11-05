# Preguntas abiertas y riesgos del hardware

Lo que **no** está verificado. Cada línea es un candidato a experimento.
Extraído de la revisión crítica de 2026-08-21.

## Riesgo 1 — Margen de corriente de la batería (el más serio)

Picos de batería observados de **~40 A** contra una asunción de diseño de 25 A
(5 celdas × 5 A). Sobrepaso de ~1,6x, unos 8 A/celda de pico.

- Las celdas SINC ISR18650-26A **no tienen datasheet verificado**. Es habitual que
  celdas genéricas o remarcadas tengan capacidades de corriente infladas.
- El BMS (JK-BD4A17S4P) tiene límite continuo de 40 A → en los picos se está rozando
  también el límite del BMS, no solo el de las celdas.
- El BMS es hoy un backstop pasivo, solo visible por Bluetooth. Un evento de
  sobrecorriente se descubriría por el corte brusco, no por un aviso previo.

**Mitigación mientras no haya medida:** el limitador primario es el límite de corriente
configurado en el propio VESC, con margen por debajo de la capacidad real del pack y
del rating del BMS. ~~Instrumentar temperatura del pack directamente~~ — **descartado por
Pol el 2026-11-01** ([DEC-005](../08_decisions/DEC-005-arquitectura-vcu.md)): se acepta la
protección del BMS. Riesgo aceptado: en un grupo 5P las celdas exteriores se calientan más
de lo que ven las sondas del BMS. Queda la comprobación a mano al terminar cada ensayo.

**Experimento pendiente:** caída de tensión bajo carga para estimar la capacidad real
de corriente del pack.

## Riesgo 2 — Bucle de tierra PC / VESC  — **MATERIALIZADO 2026-09-07**

> [!danger] Ya no es un riesgo teórico
> El 2026-09-07 este mecanismo destruyó un ESP32-WROOM-32 al montar el primer
> sniffer de CAN. El aviso de abajo estaba escrito **antes** del incidente y no se
> leyó antes de montar. Cuantificación pendiente en
> [`EXP-001`](../07_experiments/EXP-001-bucle-tierra-vesc-pc.md).

### El síntoma original: corte de USB del VESC bajo carga

Catalogado como "posible EMI" pero nunca comprobado. Es un **fallo conocido y
documentado en la comunidad VESC**, sin causa única. Tres mecanismos candidatos,
no excluyentes:

1. Resistencias de terminación USB — el datasheet del STM32F405 no especifica bien
   los pull-ups; algunas revisiones de placas VESC 6 los cambiaron.
2. Acoplamiento EMI de la conmutación de fase hacia las líneas de datos USB.
   Difícil de arreglar cuando USB y potencia están en placas separadas (este caso).
3. Bucles de tierra entre la tierra del PC y la del VESC (referenciada a batería)
   en cuanto circula corriente. Puede llegar a matar un regulador.

Como el síntoma es "bajo carga, y el motor sigue funcionando", EMI o bucle de tierra
son más probables que un defecto de soldadura.

**Experimento barato pendiente (~30 min):** osciloscopio en D+/D- y en el raíl de 5 V
durante una rampa de carga. Probar hub USB aislado o ferrita como bisección.

### Lo que añade el incidente del 07-09

El mecanismo 3 (bucle de tierra) es también el candidato principal para la muerte del
ESP32. Montaje: módulo CAN alimentado desde el pin 3V3 del ESP32, lado CAN conectado
a un VESC encendido con la batería 13S. Eso pone el raíl de 3,3 V del micro en
contacto eléctrico con un sistema de 54 V que conmuta, sin nada en medio.

**Consecuencia de diseño:** cualquier conexión entre el VESC y un equipo referenciado
a red exige aislamiento galvánico. ISO1050 para el CAN, ADUM3160 para el USB.
Ver `shopping-list.md`.

> [!note] 2026-10-31: el registrador lo evita sin aislar
> El registrador CAN se alimenta de su propia batería de 12 V: no hay equipo de red en el
> lazo, así que no hace falta el ISO1050 ([DEC-004](../08_decisions/DEC-004-can-sin-aislar-logger-flotante.md)).
> Portátil por USB solo sin cargador. Y el registrador graba con carga sin depender del
> USB del VESC, así que el corte de USB deja de bloquear los datos.

## Riesgo 3 — El motor no está identificado con certeza

La referencia MY1020/BM1109 no está confirmada. Caracterizarlo (R de fase, back-EMF,
pares de polos) es barato y no requiere software. → Es el objetivo de **C01**.

**When the motor is opened (rotor photos for the id–iq work): inspect the Hall sensors (2026-11-05).** Their placement error (~±10°, 19°
spread, repeatable) causes the current ripple below the Hall→observer handover
([EXP-003](../07_experiments/EXP-003-low-speed-control.md)). Look for a moved, bent, loose or
dirty sensor; photograph their position against the slots; clean. Replace one only if it is
visibly damaged, then re-detect the table and repeat `hall_analyze 20`. Steps in
`01_plan/tareas-quad.md`.

## Implementaciones de referencia a revisar antes de programar nada

- **VESC Express** — firmware oficial de los desarrolladores de VESC para ESP32.
  Hace prácticamente lo mismo que el logger V1 planteado. Revisar antes de escribir código.
- El asistente de detección FOC de VESC Tool ya estima R, L y flujo magnético
  (rangos típicos ~15–35 mΩ y 4–20 µH para este tipo de motor). Sirve como contraste
  independiente de la medida manual.
- `syssi/esphome-jk-bms` — protocolo JK-BMS por UART/BLE ya deconstruido y mantenido.

## Riesgo 4 — Sin sensor de temperatura en el motor

`m_motor_temp_sens_type = 8` = `TEMP_SENSOR_DISABLED`. Es correcto: **no hay sensor
instalado**. Pero la consecuencia sí es un riesgo abierto: los límites configurados
de 85/100 °C de motor son código muerto, y hay 120 A de corriente de motor disponibles
sobre un bobinado que ya se sabe que calienta.

Hoy la protección térmica de la máquina es **el procedimiento, no el sistema**: límite
de corriente en el VESC y comprobación manual al terminar el ensayo.

- Sin sensor no se puede validar el modelo térmico ni la compensación `R(T)`
  (`foc_temp_comp = 0`, coherente).
- La `R` estimada por el VESC corresponde a la temperatura de la tirada de detección.
  Sin medida de temperatura no se sabe a qué temperatura.

**Barato:** el VESC ya soporta NTC 10 k / KTY / PT1000 en el puerto de temperatura.
Un NTC pegado a la carcasa no da temperatura de bobinado, pero da tendencia y
reactiva el fold-back. Es el único hueco de sensores para validar el modelo
([DEC-005](../08_decisions/DEC-005-arquitectura-vcu.md)): **se compra** (Pol, 2026-11-01).

## Auditoría de configuración del VESC — 2026-09-06

Revisión completa de `MOTOR_1.9.xml` + `MOTOR_1.9_app.xml` contra el firmware.

**Consistencia interna: correcta.** `kp = L·bw` y `ki = R·bw` dan el mismo
`bw = 2000 rad/s` con los dos números, y `observer_gain = 1e3/λ²` = 3,898e6 ≈ 3,9e6
configurado. La detección se aplicó bien.

**Desviaciones encontradas:**

| Campo | Valor | Debería ser | Impacto |
|---|---|---|---|
| `si_gear_ratio` | ~~6,5~~ → **8,363** | 8,36 (92/11) | ✅ Resuelto. El export del 09-09 ya decía 8,363: la nota del 6,5 era vieja |
| `si_motor_poles` | ~~14~~ → **6** | 6 (p = 3 MEDIDO) | ✅ Corregido en el VESC y re-exportado el 01-10. **Sí** entra en la velocidad reportada |
| `si_wheel_diameter` | 0,30 m | 2·r_roll ≈ 0,31 m | ⚠️ ~3 %. Decidir cuál vale cuando se mida el roll-out |
| `si_battery_ah` | 13 | sin verificar | Solo estimación de autonomía |
| `foc_encoder_ratio` | 7 | — | Irrelevante, no hay encoder |

> [!success] Actualizado 2026-10-09
> Lo de abajo describía el estado antes de corregir. Hoy el canal de velocidad
> solo arrastra el ~3 % del diámetro de rueda.

`si_gear_ratio` no afecta al control, pero **sí corrompe el canal de velocidad de
todos los logs**. Como la regla nº3 de `04_model/CLAUDE.md` dice que el modelo no
vale nada hasta correlacionar contra `06_data/`, es un bloqueante barato: un campo.

**Cadena de mando confirmada** (para modelar la entrada del conductor):
`app_to_use = 2` (ADC), `ctrl_type = 3` (corriente con marcha atrás por botón),
mapa lineal 0,81 → 3,30 V, y **rampa de 0,3 s de subida / 0,1 s de bajada**.
Esa rampa (400 A/s) domina la dinámica percibida frente al lazo de corriente
(~1,5 ms). Detalle en [`04_model/params/throttle_params.m`](../04_model/params/throttle_params.m).

## Answered on the bench — the VESC controlled badly below ~2500 erpm (2026-11-05)

Full record: [EXP-003](../07_experiments/EXP-003-low-speed-control.md). Two causes, found the
same evening with the wheels in the air:
1. **Hard start = over-tensioned chain.** Chain off: breakaway ~7 A → ~2.5 A, turns at 2 % duty.
2. **Current ripple below ~4000 erpm = Hall angle** (sensor placement, ~±10°). Moving the
   Hall→observer handover from 2500/4000 to **1000/2000 erpm** cut the id ripple at
   2000–3400 erpm from ~2 A to ~0.15 A.

**Still open:** the observer at 1000–2000 erpm **under load** (chain back on, at a tension
spec), and the observer's flux linkage (detections scatter 16.2–17 mWb against 16.86 mWb
measured), which matters most at low speed.

**Export of 23:41 checked:** handover 1000/2000 ✓, `si_motor_poles` 6 ✓, battery current
39 / −25 A ✓. Motor current ±120 A is Pol's choice (full power), not a discrepancy.

## Gotcha de hardware confirmado

El TJA1050 es lógica de 5 V. Muchos módulos MCP2515/TJA1050 baratos alimentan todo el
módulo a 5 V, fuera de spec para los GPIO de 3,3 V del ESP32. **Verificar con multímetro
el nivel lógico real del módulo antes de cablear directo.**
