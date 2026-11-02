# Fuentes — qué leer para cada tema

Biblioteca en `BOOKS/` de la raíz del repositorio (`../BOOKS/` desde `PROJECT_ePWT/`; fuera de Git, copyright). Claude filtra el 20 % que hace falta
y cita sección y página. Esta tabla dice **dónde mirar**, no que haya que leerlo entero.

| Tema | Libro principal | Capítulos | Ciclo |
|---|---|---|---|
| Fundamentos del motor: fuerza, back-EMF, circuito equivalente | Hughes & Drury, *Electric Motors and Drives*, 5.ª ed. | 1 | C02 |
| Inversor, PWM, puente trifásico | Hughes & Drury | 2 | C02 |
| PMSM, síncronas, control vectorial | Hughes & Drury | 9 (y 8 para FOC en inducción) | C02–C03 |
| Electrónica de potencia en profundidad (conmutación, pérdidas, diseño) | MIT 6.622 (Perreault, 2023): lecciones + problemas con solución | lec01–09 | C03+ |
| Modelos dinámicos, respuesta, primer lazo | Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems*, 8.ª ed. | 2, 3, 4 | C03 |
| PI/PID, diseño en frecuencia | Franklin (cap. 6) · Åström & Murray, *Feedback Systems*, 2.ª ed. (cap. 11, más claro) | — | C03 |
| Control digital (el lazo de corriente corre a 15–30 kHz) | Franklin | 8 | C04 |
| Espacio de estados (camino a MPC) | Franklin cap. 7 · Åström & Murray cap. 7–8 | — | 2027 |
| Dinámica longitudinal, propulsión del vehículo | Ehsani et al., *Modern Electric, Hybrid Electric and Fuel Cell Vehicles*, 3.ª ed. | 2, 5, 7 | C01 (repaso) |
| Frenada regenerativa | Ehsani | 14 | más adelante |
| Firmware embebido (logger, ESP32) | White, *Making Embedded Systems*, 2.ª ed. | 4, 5, 7, 14 | ciclo del logger |
| Sistemas embebidos, visión general | Marwedel, *Embedded System Design* | — | consulta |
| Robótica, control no lineal | Tedrake, *Underactuated Robotics* | — | horizonte |
| Material de ejemplo en MATLAB de Franklin | `../BOOKS/BOOK_FeedbackControl/` | — | C03 |

## Vía B: electrónica, CAN y la placa (revisado el 2-nov)

| Tema | Qué hay | Hueco |
|---|---|---|
| Leer datasheets y esquemas, E/S, temporizadores, interrupciones, máquinas de estados, watchdog | White, *Making Embedded Systems*: cap. 3, 4, 5 y 6 | — |
| Periféricos, ADC, sensores | White, cap. 7 y 8 · Marwedel cap. 3.2 y 3.5 | — |
| Kirchhoff y amplificadores operacionales | Marwedel, apéndice B (corto) | Para circuitos de verdad hace falta un libro de electrónica (abajo) |
| **CAN: capa física, trama, arbitraje, errores** | **Nada en la biblioteca** (White no lo trata) | Documentos gratuitos: TI SLOA101 *Introduction to the Controller Area Network*, especificación Bosch CAN 2.0 y las hojas de datos del MCP2515 y del transceptor. No hace falta comprar libro |
| Circuitos básicos, alimentación, protección, diseño de placa | `ELECTRONICS.pdf`, si es un libro de electrónica (está escaneado y no se puede leer el título) | Si no lo es: Scherz y Monk, *Practical Electronics for Inventors*, 4.ª ed. Es el único libro que habría que conseguir |

**Sin identificar:** `ELECTRONICS.pdf` (731 pp, escaneado sin texto) y
`Training Inverters.pptx`. Pol: ¿de dónde salen? Si no sirven, fuera.
