# Sources — what to read for each topic

Library in `BOOKS/` at the repository root (`../BOOKS/` from `PROJECT_ePWT/`; outside Git,
copyright). Claude filters the 20 % needed and cites section and page. This table says
**where to look**, not that it has to be read in full.

| Topic | Main book | Chapters | Cycle |
|---|---|---|---|
| Motor fundamentals: force, back-EMF, equivalent circuit | Hughes & Drury, *Electric Motors and Drives*, 5th ed. | 1 | C02 |
| Inverter, PWM, three-phase bridge | Hughes & Drury | 2 | C02 |
| PMSM, synchronous machines, vector control | Hughes & Drury | 9 (and 8 for FOC on induction) | C02–C03 |
| Power electronics in depth (switching, losses, design) | MIT 6.622 (Perreault, 2023): lectures + problems with solutions | lec01–09 | C03+ |
| Dynamic models, response, first loop | Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems*, 8th ed. | 2, 3, 4 | C03 |
| PI/PID, frequency design | Franklin (ch. 6) · Åström & Murray, *Feedback Systems*, 2nd ed. (ch. 11, clearer) | — | C03 |
| Digital control (the current loop runs at 15–30 kHz) | Franklin | 8 | C04 |
| State space (the road to MPC) | Franklin ch. 7 · Åström & Murray ch. 7–8 | — | 2027 |
| Longitudinal dynamics, vehicle propulsion | Ehsani et al., *Modern Electric, Hybrid Electric and Fuel Cell Vehicles*, 3rd ed. | 2, 5, 7 | C01 (review) |
| Regenerative braking | Ehsani | 14 | later |
| Embedded firmware (logger, ESP32) | White, *Making Embedded Systems*, 2nd ed. | 4, 5, 7, 14 | logger cycle |
| Embedded systems, overview | Marwedel, *Embedded System Design* | — | reference |
| Robotics, nonlinear control | Tedrake, *Underactuated Robotics* | — | horizon |
| Franklin's MATLAB example material | `../BOOKS/BOOK_FeedbackControl/` | — | C03 |

**Unidentified:** `ELECTRONICS.pdf` (731 pp, scanned without text) and
`Training Inverters.pptx`. Pol: where do they come from? If they are no use, out.
