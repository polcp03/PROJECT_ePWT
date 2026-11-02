# Lista de compra — hardware pendiente

Actualizada 2026-11-01 (noche): velocidad de rueda montada, tarjeta e IMU rotas. Marcar `[x]` al recibir y
mover al inventario de `baseline.md`.

## Ahora — para usar el registrador montado en el quad (~55 €)

- [ ] **Tarjeta microSD 16–32 GB, de marca (SanDisk o Samsung)** · ~6 €
  Buscar: `microSD SanDisk 32GB`
  La Kodak de 16 GB murió el 2026-11-01: contesta, pero no guarda lo que se le escribe
  (ni un formateo). Sin tarjeta el registrador no graba nada. **La primera.** Más de 32 GB
  viene en exFAT y hay que pasarla a FAT32.
  Al llegar el lector, mirar la vieja en el PC: no la ve = chip muerto; la ve pero no
  formatea = se bloqueó en solo lectura; formatea bien = revisar el módulo SD.
  Se calentó estando en reposo: fallo interno. Causas probables: cortes de corriente
  grabando (muchos reinicios ese día), meterla o sacarla en caliente, estática.

- [ ] **IMU GY-LSM6DS3 ×1 (o ×2, por si acaso)** · ~5 € cada una
  Buscar: `GY-LSM6DS3`
  La de inventario se rompió soldándola (se arrancó la resistencia de SDA). Al soldar la
  nueva: pines primero en la protoboard, punta fina y poco tiempo.

- [ ] **Condensadores cerámicos 100 nF ("104"), surtido** · ~3 €
  Buscar: `condensador ceramico 100nF 104 pack`
  Uno junto a cada sensor (Hall, IMU), entre VCC y GND. El de 220 µF que hay no filtra
  el ruido rápido.

- [ ] **Termistor NTC 10 kΩ con cable ×2** (uno de repuesto) · ~2 €
  Buscar: `NTC 10K 3950 termistor cable`
  Temperatura del motor, al pin `TEMP` del conector de los Hall del **VESC** (no a la VCU;
  comprobar el pin en la placa). Pegado a la carcasa con cinta kapton o epoxi térmico.
  En VESC Tool: tipo NTC y la beta de la pieza comprada (3950 o 3380). Reactiva los límites
  de 85/100 °C y da `R(T)` para validar el modelo ([DEC-005](../08_decisions/DEC-005-arquitectura-vcu.md)).
  Decidido por Pol el 2026-11-01.

- [ ] **Lector microSD USB ×1** · ~5 €
  Buscar: `lector tarjetas microSD USB`
  El PC no tiene ranura SD. Descargar por el USB del ESP32 funciona pero mete basura en
  ficheros grandes (hay que bajar cada uno tres veces). Con lector: segundos y sin errores.

### La placa del registrador (~20 €)

Plano: [`05_firmware/docs/perfboard-layout.html`](../05_firmware/docs/perfboard-layout.html)
(artifact https://claude.ai/artifact/1iWNCiLEPZMBHst7gngBAS). La protoboard con cables dupont
no aguanta las vibraciones del quad, y los cables largos del SPI fueron la entrada del ruido
(EXP-002): soldado y corto, con la ESP32 y los módulos enchufables.

- [ ] **Placa perforada 9×15 cm, de doble cara (agujeros metalizados)** ×2 · ~4 €
  Buscar: `placa perforada 9x15 doble cara`
  La de 7×9 no llega: la distribución ocupa 44×34 agujeros (112×86 mm). La segunda, de
  repuesto, y de su sobrante sale la placa pequeña de la IMU.
- [ ] **Tiras de pines hembra 2,54 mm, 1×40** ×3 · ~2 €
  Buscar: `tira pines hembra 2.54 40`
  Zócalo de la ESP32 (2×19) y de la SD (1×6, la SD va de pie en él), y el de la IMU.
- [ ] **Tira de pines macho 2,54 mm, 1×40** ×1 · ~1 €
  Para la placa del cable del CAN (1×7) y la IMU.
- [ ] **Bornas de tornillo paso 5,08 mm, 2 y 3 polos** · ~3 €
  Buscar: `borne tornillo 5.08 2P 3P`. Hacen falta 2 de 2 polos (J1 y la IMU, que va en 2+2)
  y 4 de 3 polos (rueda, acelerador, frenos y CAN al VESC). Comprar un paquete.
- [ ] **Hilo de cobre estañado desnudo 0,6 mm** · ~2 €
  Buscar: `hilo cobre estañado 0.6mm`. Solo para los buses de GND, +5 V y +3,3 V.
- [ ] **Cable rígido aislado 22 AWG, caja de colores** · ~6 €
  Buscar: `cable rigido 22AWG kit colores`. Todo lo demás: puede cruzar por encima de otro.
- [ ] **Cable dupont hembra-hembra de 10 cm (tira de 40)** · ~2 €
  Del módulo CAN a la placa: sus pines salen hacia arriba, así que no se enchufa. Se separa una
  tira de 7 cables que van juntos, con una gota de cola caliente en cada extremo.
- [ ] **Separadores de nylon M3 de 10 mm con tornillos (kit)** · ~4 €
  Buscar: `separadores nylon M3 kit`. El módulo CAN sobre la placa, la placa dentro de la caja y
  la IMU en el chasis.
- [ ] **Cable de 4 hilos apantallado, 1 m** · ~2 €
  Buscar: `cable apantallado 4 hilos`. De la placa a la IMU, que va fuera, atornillada al chasis.

- [ ] **Caja estanca ABS ~150×110×70 mm** · ~8 €
  Buscar: `caja estanca ABS 150x110x70`
  Polvo y barro. Por dentro, 60 mm de alto como mínimo: la SD va de pie (42 mm) y el CAN sobre
  separadores. De plástico: una de aluminio habría que conectarla a masa con criterio.

## Ya en inventario — NO comprar

- ESP32 ×2 de repuesto (el nº 2 hace de registrador)
- MCP2515 + TJA1050, módulo microSD (la tarjeta, muerta), batería 12 V + DC-DC a 5 V
- Sensores Hall 3144 (uno montado en la rueda delantera, el resto de repuesto) + imanes;
  el acelerador Hall de 5 V
- Protoboard, cables dupont, resistencias, osciloscopio, multímetro, soldador

## Cuando toque la unidad de control del vehículo

Pinout decidido: [`05_firmware/docs/vcu-pinout.md`](../05_firmware/docs/vcu-pinout.md). Las
resistencias (10 k, 12 k) salen del inventario y los condensadores, del surtido de 100 nF
de arriba. Lo único por decidir es el corte de emergencia.

## Descartado o aplazado

- **Módulo CAN aislado ISO1050:** descartado el 2026-10-31. El registrador flota con su
  propia batería; ver [DEC-004](../08_decisions/DEC-004-can-sin-aislar-logger-flotante.md).
  Se revisa si el ESP32 llega a mandar par al VESC.
- **Aislador USB ADUM3160 y ferritas de pinza:** aplazados. Eran para diagnosticar el corte
  del USB del VESC bajo carga; el registrador ya graba con carga sin USB.
- **Resistencias de 120 Ω:** aplazadas. El MCP2515 trae la suya (jumper J1) y el bus
  funciona con 0 errores.
- **ESP32-WROOM-32 nº 1:** destruido el 2026-09-07. Cortocircuito interno. Marcada y
  guardada aparte para no confundirla con una buena.
