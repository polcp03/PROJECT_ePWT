# Sesión: firmware / embebido

Contexto adicional para trabajar en `05_firmware/`. Se suma al `CLAUDE.md` raíz.

## Regla nº1 — Aquí no se inventa control

La lógica de control se diseña y se valida en `04_model/`. Este directorio la
**implementa**. Si aparece una constante mágica que no viene del modelo, es un bug
de proceso, no una optimización.

## Regla nº2 — Los límites de seguridad son código, no configuración

Límites de corriente, temperatura y estado del BMS se comprueban en el firmware, no
solo en el VESC Tool. Ver las reglas de seguridad del `CLAUDE.md` raíz.

## Regla nº3 — Antes de escribir, buscar

Existen implementaciones de referencia (VESC Express para ESP32,
`syssi/esphome-jk-bms` para el protocolo del BMS). Revisarlas antes de hacer
ingeniería inversa desde cero. Primeros principios se reservan para el dominio
que quiero dominar, no para protocolos.

## Cómo enseñarme

Quiero aprender **arquitectura de software**, no solo que compile: separación de
responsabilidades, módulos, interfaces, dependencias. Cuando propongas código,
explica primero cómo se reparten las responsabilidades y por qué.

Nada de un `.ino` gigante. Módulos con una responsabilidad cada uno.

## Cómo se compila y se ve (el Arduino IDE no funciona)

Skill `esp32`: el código abierto en el panel de ficheros y el monitor serie en una
pestaña visible del Terminal, con `esp32.py` (compilar, flashear, monitor, enviar).
Nunca flashear a ciegas en segundo plano: Pol tiene que verlo.

## Estructura de la carpeta

```
arduino/    sketches y experimentos rápidos
```

`src/` (módulos) y `docs/` (protocolos, pinouts) se crean **cuando empiece la VCU**,
no antes. Una carpeta vacía es ruido: promete algo que no existe.

Aquí **solo va código mío**. Lo del VESC está repartido a propósito:
la configuración de mi equipo en `03_hardware/vesc/`, sus logs en `06_data/`,
y el firmware y la herramienta de terceros en `_tools/` (fuera de Git).
Ver `03_hardware/vesc/README.md`.
