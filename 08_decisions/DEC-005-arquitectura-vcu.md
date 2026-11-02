# DEC-005: Arquitectura de la unidad de control (VCU) y sensores

**Fecha:** 2026-11-01. Decide Pol, tras discutirlo con Claude. Concreta la arquitectura
objetivo del kickoff (C00, slide 5) y el paso 3 de [roadmap](../01_plan/roadmap.md).

## Decisión

| Señal | Va a | Por qué |
|---|---|---|
| **Acelerador** | **VCU** (hoy, al ADC del VESC) | Es la base del control de tracción: la VCU decide el par y lo pide por CAN |
| **Interruptores de freno** | **VCU** (hoy, desconectados) | Seguridad (freno + gas = par cero), saber cuándo la referencia de velocidad no vale, y etiquetar los datos |
| **Velocidad de rueda delantera** | VCU | Ya montada (2026-11-01). Rueda sin tracción = referencia de velocidad del vehículo |
| **IMU** | VCU | Cuando llegue la nueva. Aceleración longitudinal, pendiente y giro |
| **Hall del rotor** | **VESC, sin cambios** | La conmutación necesita microsegundos; la VCU ya recibe las rpm por CAN |
| **BMS** | **Nada.** Respaldo pasivo | Protocolo cerrado; tensión y corriente del pack ya llegan del VESC |
| **Temperatura del pack** | **Sin sensor** | El BMS tiene dos sondas propias y corta si se pasa |

El foco es **VCU + VESC**. El BMS no se toca.

## Alternativas descartadas

- **Hall del rotor también a la VCU.** Duplica lo que el VESC ya manda (erpm).
- **BMS por CAN o UART** (`syssi/esphome-jk-bms`). Daría tensión por grupo, temperatura y
  aviso antes del corte. Descartado por coste/beneficio: protocolo cerrado y el foco es
  motor e inversor. Sigue en el backlog.
- **Sonda de temperatura en las celdas exteriores** (lo que pedía `open-questions.md`).
  Descartada por Pol: se acepta la protección del BMS.

## Comprobación: ¿bastan los sensores para validar el modelo?

Objetivo del año: modelo validado contra el vehículo real (C04 motor, C05 vehículo).

| Qué hay que validar | Señal | De dónde | Estado |
|---|---|---|---|
| Motor (C04): λm, R, lazo de corriente | corriente, erpm, ciclo de trabajo, tensión | VESC por CAN | ✅ ya se graba |
| Resistencia con la temperatura, `R(T)` | temperatura del motor | — | ⚠️ **hueco**. Ver abajo |
| Coast-down (C05): rodadura, aerodinámica, eficiencia | velocidad del vehículo frente al tiempo | Hall de rueda delantera | ✅ sensor; falta **`r_roll`** (roll-out) y **tarjeta SD** |
| Aceleración (C05): fuerza en la rueda | corriente + velocidad + aceleración | VESC + rueda + IMU | ✅ cuando llegue la IMU |
| Pendiente del terreno | cabeceo | IMU, o terreno llano medido | ✅ con IMU |
| Deslizamiento (control de tracción) | rueda trasera vs delantera | erpm ÷ 3 ÷ 8,364 frente al Hall | ✅ |
| Curvas | velocidad de giro | IMU | ✅ con IMU. Eje trasero rígido y un solo sensor delantero: en curva la referencia necesita el giro |
| Transferencia de carga | `h_cg`, peso por eje | báscula, no sensor | ❌ medida pendiente |
| Entrada del conductor | acelerador, freno | VCU | ✅ con esta decisión |

**Conclusión:** con lo que hay, más la IMU y el freno, se valida todo lo de 2026. **No
hace falta comprar ningún sensor más.** Lo que bloquea no son sensores: es la tarjeta SD,
la IMU, el roll-out de 10 m y las básculas por eje.

**Único hueco: la temperatura del motor.** La resistencia del cobre sube ~0,4 %/K: con
40 K de calentamiento, `Rs` sube ~16 %. A 120 A eso es medio voltio más de caída, que
importa justo donde el ciclo de trabajo ya va al límite. Además, sin sensor, los límites
de 85/100 °C del VESC son código muerto (Riesgo 4 de `open-questions.md`). Un NTC de 10 k
pegado a la carcasa, al puerto de temperatura del **VESC** (no de la VCU): ~1 €.
**Decidido por Pol el mismo día: se compra** (`shopping-list.md`).

## Consecuencias

Lo que hay que hacer **antes** de que el acelerador pase por la ESP32 (gas por cable):

1. **VESC:** quitar la app ADC y configurar el **timeout de CAN**. Si la VCU se cuelga o
   se calla, el VESC tiene que cortar el par solo. Probarlo con la rueda en el aire.
2. **Acelerador:** alimentado desde los 5 V de la VCU. Su salida pasa de 3,3 V y el ADC del
   ESP32 no: **divisor**. Usar un pin de ADC1 (GPIO 32–39), porque ADC2 no funciona con
   Wi-Fi activo. Ventana de fallo como la del VESC: fuera de rango → par cero.
3. **Freno:** cada interruptor, un pin a masa con pull-up interno. GPIO 32 y 33 sí tienen;
   **34–39 no**. Antes, medir con el multímetro que es un contacto seco (que no lleva
   tensión del sistema original) y si es normalmente abierto o cerrado. Antirrebote en
   código.
4. **Freno + gas → par cero**, en el código desde la v0.
5. **Bucle de tierra:** la VCU sigue flotando en su batería de 12 V ([DEC-004](DEC-004-can-sin-aislar-logger-flotante.md)).
   Con la VCU mandando par, EXP-001 vuelve a importar.

Pinout completo, con las condiciones de cada pin: [`05_firmware/docs/vcu-pinout.md`](../05_firmware/docs/vcu-pinout.md).
Acelerador GPIO 35, frenos GPIO 32 y 33, IMU GPIO 21/22.

## Asunciones

- La VCU es la evolución del registrador: la misma ESP32 graba y manda.
- El BMS corta antes de que el pack sea peligroso. **Riesgo aceptado:** un corte del BMS
  es una pérdida brusca de potencia sin aviso, y en un grupo 5P las celdas exteriores se
  calientan más de lo que ven sus sondas. La regla de seguridad de `CLAUDE.md` se mantiene:
  comprobar la temperatura del pack a mano al terminar cada ensayo de corriente alta.
- Los interruptores de freno originales sirven tal cual.

## Por saber

- ~~¿Qué ruedas frena cada maneta?~~ Medido el 2-nov: freno delantero y trasero, interruptores
  normalmente abiertos. El trasero falla: solo se cablea el delantero (GPIO 32).
- Pregunta abierta para Pol: si frenas fuerte y la rueda delantera se bloquea, ¿qué le
  pasa a la referencia de velocidad y qué haría el control de tracción con ella?
