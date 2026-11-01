# Lista de compra — hardware pendiente

Actualizada 2026-11-01 (noche): velocidad de rueda montada, tarjeta e IMU rotas. Marcar `[x]` al recibir y
mover al inventario de `baseline.md`.

## Ahora — para usar el registrador montado en el quad (~35 €)

- [ ] **Tarjeta microSD 16–32 GB, de marca (SanDisk o Samsung)** · ~6 €
  Buscar: `microSD SanDisk 32GB`
  La Kodak de 16 GB murió el 2026-11-01: contesta, pero no guarda lo que se le escribe
  (ni un formateo). Sin tarjeta el registrador no graba nada. **La primera.** Más de 32 GB
  viene en exFAT y hay que pasarla a FAT32.

- [ ] **IMU GY-LSM6DS3 ×1 (o ×2, por si acaso)** · ~5 € cada una
  Buscar: `GY-LSM6DS3`
  La de inventario se rompió soldándola (se arrancó la resistencia de SDA). Al soldar la
  nueva: pines primero en la protoboard, punta fina y poco tiempo.

- [ ] **Condensadores cerámicos 100 nF ("104"), surtido** · ~3 €
  Buscar: `condensador ceramico 100nF 104 pack`
  Uno junto a cada sensor (Hall, IMU), entre VCC y GND. El de 220 µF que hay no filtra
  el ruido rápido.

- [ ] **Lector microSD USB ×1** · ~5 €
  Buscar: `lector tarjetas microSD USB`
  El PC no tiene ranura SD. Descargar por el USB del ESP32 funciona pero mete basura en
  ficheros grandes (hay que bajar cada uno tres veces). Con lector: segundos y sin errores.

- [ ] **Placa perforada + tiras de pines hembra** · ~5 €
  Buscar: `placa perforada PCB prototipo 7x9 cm` y `tira pines hembra 2.54`
  La protoboard con cables dupont no aguanta las vibraciones del quad, y los cables
  largos del SPI fueron la entrada del ruido (EXP-002). Soldado y corto. ESP32 y módulos
  en zócalos de pines hembra, para poder cambiarlos.

- [ ] **Caja de plástico pequeña** · ~5 € (opcional)
  Buscar: `caja estanca ABS 100x68x50`
  Polvo y barro. De plástico: una de aluminio habría que conectarla a masa con criterio.

## Ya en inventario — NO comprar

- ESP32 ×2 de repuesto (el nº 2 hace de registrador)
- MCP2515 + TJA1050, módulo microSD (la tarjeta, muerta), batería 12 V + DC-DC a 5 V
- Sensores Hall 3144 (uno montado en la rueda delantera, el resto de repuesto) + imanes;
  el acelerador Hall de 5 V
- Protoboard, cables dupont, resistencias, osciloscopio, multímetro, soldador

## Cuando toque la unidad de control del vehículo

Nada todavía. Lo que haga falta (corte de emergencia, adaptar el acelerador de 5 V a la
entrada de 3,3 V del ESP32) se decide al diseñarla, no antes.

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
