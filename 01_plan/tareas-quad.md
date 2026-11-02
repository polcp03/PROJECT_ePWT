# El quad: qué comprar y qué hacer

> Hoy, 1-nov-2026. Lo que bloquea todo es **una tarjeta microSD**: sin ella el registrador no
> graba y no sale ni un dato. Pídela hoy con el lector. Todo lo de aquí sale del roadmap y de
> DEC-005, ya acordados contigo: no hay rumbo nuevo, solo ordenado.

## Comprar

### Ya, porque bloquea (≈ 25 €)

1. **Tarjeta microSD 16–32 GB de marca** (SanDisk o Samsung) · ~6 €. La Kodak murió. Más de
   32 GB viene en exFAT y hay que pasarla a FAT32.
2. **Lector microSD USB** · ~5 €. Bajar los ficheros por el USB del ESP32 mete basura; con
   lector son segundos.
3. **IMU GY-LSM6DS3 ×2** · ~5 € cada una. La tuya se rompió al soldar; la segunda es de repuesto.
4. **Termistor NTC 10 kΩ con cable ×2** (`NTC 10K 3950`) · ~2 €. Temperatura del motor, al
   puerto de temperatura del VESC. Decidido por ti hoy.
5. **Condensadores cerámicos 100 nF, surtido** · ~3 €. Uno junto a cada sensor, entre VCC y GND.

### Para montar el registrador en el quad (≈ 35 €)

Todo sale del [plano de la placa](https://claude.ai/artifact/1iWNCiLEPZMBHst7gngBAS).

1. **Placa perforada 9×15 cm de doble cara ×2** (`placa perforada 9x15 doble cara`) · ~4 €.
   La de 7×9 no llega: la placa ocupa 112×86 mm.
2. **Tiras de pines 2,54 mm:** hembra 1×40 ×3 y macho 1×40 ×1 · ~3 €. Zócalos de la ESP32,
   la SD (va de pie) y la IMU.
3. **Bornas de tornillo 5,08 mm** (`borne tornillo 5.08 2P 3P`) · ~3 €: 2 de 2 polos y 4 de 3.
   Son los conectores del borde: el cable se atornilla y no se suelta con la vibración.
4. **Hilo de cobre estañado desnudo 0,6 mm** · ~2 €, para los buses.
5. **Cable rígido aislado 22 AWG, kit de colores** · ~6 €, para todo lo demás.
6. **Cable dupont hembra-hembra de 10 cm, tira de 40** · ~2 €: del módulo CAN a la placa.
7. **Separadores de nylon M3, kit** · ~4 €: CAN sobre la placa, placa en la caja, IMU en el chasis.
8. **Cable apantallado de 4 hilos, 1 m** · ~2 €: de la placa a la IMU.
9. **Caja estanca ABS ~150×110×70 mm** · ~8 €. 60 mm de alto por dentro como mínimo.

### Para medir el vehículo (préstamo mejor que compra)

1. **Dos básculas de baño** iguales. Peso por eje y altura del centro de gravedad.
2. **Cinta métrica larga** (10 m) para el roll-out.

### No comprar

Ya lo tienes: ESP32 ×2 de repuesto, módulo CAN, módulo SD, batería de 12 V con DC-DC, Hall
3144 e imanes, acelerador Hall, osciloscopio, multímetro, soldador. Aplazados: CAN aislado
ISO1050, aislador USB, resistencias de 120 Ω.

## Antes de nada: la deuda

### Papeles del quad sin cerrar

1. **C02 sin cierre escrito**: no hay `cerrados/C02.md` (resultado, qué aprendí, qué salió mal).
2. **C03 empezó el 31-oct** y sus lecciones (L3 modelo dq, L4 Simulink) existen, pero no hay
   `C03.md` con el plan del ciclo.
3. **Error nº 4 abierto** en `errores.md` (por qué PWM y no una resistencia).
4. **`R_int` = 0,18 Ω** medida el 31-oct y todavía no está en `04_model/params/`.

### Git

Al día desde el 2-nov: todas las ramas fusionadas y la lista de compra completa (tarjeta,
lector, IMU, condensadores y NTC) en `03_hardware/shopping-list.md`.

## Paso 1 · Que el registrador grabe otra vez

### Cuando llegue la tarjeta

1. Formatear en FAT32 y grabar con la rueda delantera girando a mano.
2. Comprobar en el fichero las líneas `#wheel` y `#wstat`. La velocidad de rueda está
   cargada en el ESP32 pero **nunca se ha visto en una tarjeta**.
3. Mirar la Kodak vieja en el lector: no la ve = muerta; la ve sin formatear = solo
   lectura; formatea = revisar el módulo.

### Pasarlo a placa perforada

ESP32 y módulos en zócalos, cables cortos, lejos del VESC y de las fases. Lo que quitó el
ruido fue eso, no el firmware. Después, grabar con gas y confirmar 0 tramas corruptas.

### IMU nueva

Soldar con los pines pinchados en la protoboard, punta fina y poco tiempo. I2C en GPIO 21/22.

### NTC en el motor

Pegado a la carcasa (kapton o epoxi térmico), al pin `TEMP` del conector de los Hall del
VESC. En VESC Tool: tipo NTC y la beta de la pieza. Reactiva los límites de 85/100 °C.

## Paso 2 · Medidas sin software

Son números que el modelo marca como supuestos o que faltan. Ninguno necesita código.

### Roll-out de 10 m → radio de rodadura real

Contigo encima, contar imanes (o vueltas) en 10 m medidos. Sustituye el `r_roll` supuesto
y decide si `si_wheel_diameter` del VESC es 0,30 o 0,31 m. Todos los canales de velocidad
dependen de este número.

### Peso por eje y altura del centro de gravedad

Báscula bajo cada eje en llano, con y sin ti. Para la altura, levantar un eje una altura
conocida y ver cuánto peso pasa al otro. **La fórmula la deduces tú** antes de medir: es
un equilibrio de momentos.

### Frenos — hecho el 2-nov

Normalmente abiertos: hay continuidad solo al frenar. El interruptor del freno trasero
falla, así que solo se cablea el **delantero** (GPIO 32); el GPIO 33 queda reservado. Un
bloqueo de la trasera se verá igual, porque su velocidad es la del motor. Falta comprobar
que en los cables no queda tensión del sistema original de 36 V.

## Paso 3 · Ensayos que dan información

Cada ensayo responde a una pregunta del modelo. Señales del VESC por CAN: corriente de
motor y de batería, erpm, ciclo de trabajo, tensión. Más rueda, IMU y NTC cuando estén.

### A · Constante del motor, con la rueda en el aire (C04)

Subir el gas en escalones y aguantar cada uno. Si el modelo es bueno, ciclo × tensión
frente a velocidad eléctrica es una recta y su pendiente da la constante de flujo λm.
Compárala con la del back-EMF de C00. Antes de mirar el resultado: **predice** si la
recta pasa por cero y por qué no del todo.

### B · Resistencia con la temperatura (C04, con NTC)

Tandas cortas con carga, apuntando temperatura del motor. La resistencia del cobre sube
~0,4 % por grado. Sirve para saber a qué temperatura vale la R que estimó el VESC.

### C · Coast-down: rodadura y aerodinámica (C05)

Llegar a la máxima velocidad segura, soltar el gas y dejar que frene solo. Registrar
velocidad de la rueda delantera frente al tiempo. Es el método estándar (SAE J2263):
la fuerza que frena se ajusta a `a + b·v + c·v²`, donde lo constante y lo lineal son
rodadura y transmisión y lo cuadrático, aire. Hace falta la masa y la inercia que ya
mediste en septiembre.

1. Terreno llano, sin viento, y **en los dos sentidos** para cancelar pendiente y viento.
2. Al menos tres pasadas por sentido. Neumáticos siempre a la misma presión, apuntada.
3. MathWorks tiene un ejemplo que hace este ajuste con Simulink Design Optimization.

### D · Aceleración a fondo (C05)

Desde parado, gas a fondo. Corriente y velocidad dan la fuerza en la rueda; la IMU da la
aceleración. El modelo de C01 tiene que predecir la curva. Por encima de 9 km/h va pegado
a 40 A de batería: es el límite del BMS. **Seguridad abajo.**

### E · Deslizamiento

Rueda trasera (erpm ÷ 3 ÷ 8,364) frente a la delantera (Hall). En recta y sin patinar,
la diferencia es el error del radio. Es la base del control de tracción.

## Paso 4 · Unidad de control v0 (dic–ene)

La ESP32 lee el acelerador y manda la corriente al VESC por CAN. Sin control: solo pasar
la orden con protecciones. Antes de que el gas pase por la ESP32:

1. **Timeout de CAN en el VESC.** Si la ESP32 se cuelga, el VESC corta solo. La
   documentación del VESC insiste en no desactivarlo nunca. La orden de corriente se
   reenvía continuamente, no una vez. Probarlo con la rueda en el aire.
2. **Acelerador**: divisor (su salida pasa de 3,3 V) y un pin de ADC1 (GPIO 32–39). Fuera
   de rango → par cero.
3. **Freno**: el delantero en el GPIO 32 (el trasero no se cablea); freno + gas → par cero,
   desde la v0. Como es normalmente abierto, un cable cortado se lee como «sin frenar».
4. **Bucle de tierra**: con la ESP32 mandando par, EXP-001 vuelve a importar.

## Después

1. **IMU y rueda en la tarjeta**, con el filtro elegido en el PC a partir de datos reales.
2. **Control de tracción**: primero en Simulink, después en la ESP32.
3. **Fin de 2026**: modelo validado contra el vehículo. Es el objetivo del año.

## Decisiones que son tuyas

1. **El corte de emergencia** de la unidad de control: qué es y dónde va.
2. Si frenas fuerte y la delantera se bloquea, ¿qué pasa con la referencia de velocidad y
   qué haría el control de tracción con ella? Contestado a medias el 1-nov: error nº 11 de
   `errores.md`, se vuelve a preguntar el sábado 7-nov.
3. `l_in_current_max`: seguir en 40 A (el límite del BMS) o bajar.

## Seguridad, en cada ensayo con corriente

1. Límite de corriente configurado en el VESC antes de empezar.
2. Temperatura del pack a mano al terminar.
3. Nunca cargar sin supervisión.
4. Primero con la rueda en el aire; en el suelo, solo cuando eso funciona.
