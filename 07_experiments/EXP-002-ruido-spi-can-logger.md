# EXP-002: Ruido al acelerar en el registrador CAN

**Estado:** cerrado el 2026-11-01. Confirmado y resuelto.

## Pregunta

Las grabaciones del registrador (`05_firmware/arduino/can_logger/`) se cortaban a los
3–10 s, antes con gas que sin él. ¿Por qué, y dónde entra el problema?

## Hipótesis

**H1 (Pol).** Interferencias: el problema aparece al acelerar, cuando el VESC conmuta
corriente.

**H2.** Si el ruido entra por el bus CAN, el MCP2515 contará errores de bus (REC/TEC).
Si entra por el enlace SPI entre el MCP2515 y el ESP32, el bus estará limpio y las
tramas llegarán corruptas igualmente.

## Método

1. Registrar en `boot.txt` el motivo de cada reinicio del ESP32.
2. Tres ensayos, de menos a más ruido: **A** el ESP32 solo, **B** el VESC encendido y el
   motor parado, **C** con gas (ruedas en el aire, límite de corriente puesto).
3. Clasificar cada trama: buena (ID de estado del VESC, DLC 8), fantasma (ID imposible)
   o con bits cambiados (ID correcto, valor físicamente imposible).

## Datos

Crudos en `06_data/2026-10-31_can_logger_bench/raw/`; decodificador
`04_model/scripts/can_log_decode.py`.

| Ensayo | Duración | Tramas buenas/s | Corruptas | Desbord. | Errores de bus |
|---|---|---|---|---|---|
| Antes del arreglo | 3–10 s | — | reinicios PANIC / watchdog | — | — |
| A (log_012) | 138 s | — (sin VESC) | 0 | 0 | 0 |
| B (log_013) | 144 s | 282 | 39 de 40 659 | 0 | 0 |
| C (log_014) | 70 s | 249 | ~3 150 (152 de 192 con bits cambiados, durante la corriente) | 14 | 0 |
| **Después (log_017)** | 137 s, 12 s con corriente | **288** | **1** (al encender el VESC) | **0** | **0** |

En C aparecieron 458 V, −3249 °C y 10⁹ erpm dentro de tramas con el ID correcto.

## Conclusión

- **H1 confirmada:** el ruido aparece con corriente.
- **H2: entra por el SPI, no por el CAN.** Los errores de bus son 0 en todos los ensayos.
- **Los reinicios eran un fallo de firmware destapado por el ruido.** Un bit cambiado
  daba una longitud (DLC) de 9–15; la librería `mcp_can` copiaba esa cantidad en un
  búfer de 8 bytes, pisaba memoria y el ESP32 caía (PANIC). Arreglo: lector propio que
  nunca copia más de 8 bytes, con el SPI bajado de 10 a 4 MHz.
- **El ruido lo quitó el hardware:** 5 V directos del DC-DC al raíl (antes 4,5 V en el
  pin 5V por el cable USB y el diodo de la placa, bajo el mínimo de 4,75 V del TJA1050),
  cables SPI más cortos y el montaje lejos del VESC. Los tres cambios se hicieron a la
  vez, así que **no se sabe cuál pesó más**.
- La doble lectura (cada trama se lee hasta que dos lecturas coinciden) contó 0
  discrepancias en log_017: no tuvo que corregir nada. Se queda como red de seguridad
  y como medidor (`spi_errors` en cada línea `#stat`).

## Dato de regalo

Caída de tensión en log_017: 50,9 V en reposo → 45,8 V a 29 A ⇒
**R ≈ 0,18 Ω, batería + cables + BMS** (antes ASSUMED 0,10 Ω). A 29 A son unos 150 W
de calor. Por celda (13S5P) salen ~70 mΩ, por encima de una 18650 sana (20–50 mΩ):
parte está en el cableado. Cálculo de Pol.

## Limitaciones

- Ensayo con las ruedas en el aire; con carga real la corriente y el ruido serán mayores.
- Sin separar los tres cambios de hardware.
- La terminación del lado del VESC no está clara: las medidas de resistencia entre
  CAN-H y CAN-L no cuadran entre sí. El bus funciona con 0 errores con el cable corto.
