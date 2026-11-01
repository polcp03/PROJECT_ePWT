# Errores — lo que he contestado mal y cuándo me lo vuelven a preguntar

Un error se cierra cuando lo contesto bien **dos veces, en días distintos**. Claude
pregunta los abiertos al empezar cada examen y en el ejercicio del sábado.

Estado: 🔴 abierto · 🟡 bien una vez · 🟢 cerrado

| # | Fecha | Tema | Lo que dije | Lo correcto | Volver a preguntar | Estado |
|---|---|---|---|---|---|---|
| 1 | 2026-10-25 | Faraday | "Un imán moviéndose dentro de un campo magnético genera tensión" | Si cambia el flujo que atraviesa una bobina, se induce tensión en ella: e = −dλ/dt. El imán no está "dentro de un campo": él *es* el campo | Examen 29-oct | 🔴 |
| 2 | 2026-10-25 | Quién fija la corriente | "La decide la demanda de par" | Con alimentación a tensión fija, sí: la carga. Con el VESC en control de corriente, la pide el puño, y solo circula si hay tensión de sobra para empujarla contra la back-EMF | Examen 29-oct | 🔴 |
| 3 | 2026-10-25 | Corriente de batería vs de fase | "La total es la de fase por tres" | No hay un factor 3. Las une la potencia: Vbat·Ibat ≈ P en el motor. A baja velocidad y par alto, I de fase ≫ I de batería | Examen 29-oct | 🔴 |
| 4 | 2026-10-25 | PWM vs resistencia | Explicó cómo se genera alterna; no dio la razón | Razón: **eficiencia**. Una resistencia quema (Vbat − Vmotor)·I. Un interruptor cerrado tiene V ≈ 0 y abierto I ≈ 0: casi no disipa. La bobina del motor suaviza la corriente | Examen 29-oct | 🔴 |
| 5 | 2026-10-25 | PWM | "Se varía la frecuencia" | Se varía el **ciclo de trabajo** (duty). La frecuencia es fija: 30 kHz en tu VESC | Examen 29-oct | 🔴 |
| 6 | 2026-10-25 | Medio puente | "Abriendo y cerrando pasas de positivo a negativo" | Un brazo pone su fase a +Vbus o a 0, nunca a negativo. La alterna aparece en la **diferencia** entre fases | Examen 29-oct | 🔴 |
| 7 | 2026-10-25 | Pares de polos | "Más pares → más suave" | La suavidad viene de la forma de onda senoidal y de las ranuras, no del número de polos. Más polos = más par por amperio (Te = 3/2·p·λ·iq) y frecuencia eléctrica más alta a la misma velocidad | Examen 29-oct | 🔴 |
| 8 | 2026-10-25 | Rotor IPM | "Agujeros de aire para que llegue más campo al bobinado, evitando el entrehierro" | Al revés: el aire tiene una permeabilidad bajísima. Las barreras de flujo **bloquean** el flujo que se cerraría dentro del rotor y lo obligan a cruzar el entrehierro. El entrehierro no se puede evitar. Y Lq/Ld = 1,136 dice "no es SPM puro", no "es IPM" (en un IPM típico, Lq/Ld ≈ 2–3) | Examen 29-oct | 🔴 |
| 9 | 2026-10-25 | Hábito | Mezcló 4 preguntas en un monólogo de voz y respondió de más | Una pregunta, una respuesta, 5 líneas. Contestar justo lo que se pregunta es una habilidad de entrevista | Siempre | 🔴 |
| 10 | 2026-11-02 | Verificar software | "Si lo que leo del CAN cuadra con lo que hago y no hay errores, está bien" | Plausible no basta: criterio con número (0 tramas perdidas, frecuencia de tramas igual a la del VESC), contadores de error que lo demuestren, prueba de 30 min o más y fallos provocados. Nota en `software.md` | Próximo cambio de firmware | 🔴 |
