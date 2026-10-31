# DEC-004: CAN sin aislar, con el registrador flotante

**Fecha:** 2026-10-31. Decide Pol. Sustituye a lo que pedía `shopping-list.md` (ISO1050).

## Decisión

El registrador usa el **MCP2515 + TJA1050** que ya había, sin aislamiento galvánico.
La seguridad la da la arquitectura: el registrador se alimenta de **su propia batería de
12 V** con un DC-DC a 5 V, y solo se une al VESC por CAN-H, CAN-L y la masa del CAN.
Ningún equipo conectado a la red eléctrica toca ese sistema: el portátil, si se conecta
por USB, va **siempre sin cargador**.

La salida SO del MCP2515 (5 V) pasa por un divisor 1 kΩ / 2 kΩ hasta el ESP32 (3,3 V).

## Alternativas

- **ISO1050 (aislado).** Lo correcto si hubiera un equipo referenciado a red en el lazo.
  Descartado: Pol no quiere comprarlo, y con el registrador flotante no hay lazo que cortar.
- **SN65HVD230.** 3,3 V nativo, sin divisor. Sin aislar igual, y había que comprarlo.
- **MCP2515 a 3,3 V.** El TJA1050 necesita 5 V: no funciona.

## Razonamiento

El ESP32 de septiembre murió por un **bucle de tierra**: masa del PC (red) unida a la
masa de un VESC que conmuta 54 V ([EXP-001](../07_experiments/EXP-001-bucle-tierra-vesc-pc.md)).
Aislar es una forma de romper ese lazo; no tener la red en el lazo es otra, y no cuesta nada.

## Asunciones

- Nadie conecta un cargador al portátil mientras está unido al vehículo.
- El ruido de modo común del VESC en carga cabe en el rango de modo común del TJA1050. Con
  0 errores de bus en log_017 (49 A de pico) se sostiene; con carga real, por ver.

## Consecuencias

- Funciona hoy, sin gastar nada ([EXP-002](../07_experiments/EXP-002-ruido-spi-can-logger.md)).
- El divisor y la protoboard hacen el enlace SPI sensible al ruido: cables cortos y lejos
  del VESC. Montarlo en el vehículo pide **placa perforada soldada**, no protoboard.
- Si algún día el ESP32 manda par al VESC (unidad de control del vehículo), un fallo
  aquí deja de ser un dato perdido: se revisa esta decisión antes.
