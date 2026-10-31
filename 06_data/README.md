# Datos de ensayo

Una carpeta por campaña: `AAAA-MM-DD_<ensayo>`. Dentro, `raw/` son los archivos tal
y como los escupe el instrumento — **no se editan nunca**.

> [!warning] `raw/` no está en Git
> Los crudos de osciloscopio pesan cientos de MB y no admiten diff. Viven en disco
> local y están ignorados. **Este README es el índice: si un crudo no está listado
> aquí, no existe.** Lo que sí entra al repo: CSV pequeños, y las figuras de
> análisis, que van a `04_model/results/`.

---

## `2026-09-07_back-emf` — back-EMF en circuito abierto

Motor desconectado del VESC, sonda entre fase A y fase B, motor girado con un
taladro. Ventana de 500 ms, rango ±20 V. Es la medida que da `λm = 16,86 mWb`
(ver `03_hardware/motor-parameters.md`).

| Ruta | Qué es | Tamaño |
|---|---|---|
| `raw/low_speed/*.BMP` | 12 pantallazos del MaxiScope | 67 MB |
| `raw/mid_speed/*.BMP` | 13 pantallazos | 73 MB |
| `raw/high_speed/*.BMP` | 32 pantallazos | 179 MB |
| `raw/scope_txt/*.txt` | 2 exportaciones numéricas del osciloscopio, a 1310 y 2510 rpm mecánicos | 56 MB |

**Análisis:** `04_model/scripts/backemf_extract.py` (lee los BMP) →
`backemf_fit.py` (ajusta λm y genera la figura) y `backemf_from_csv.py` (misma
medida desde los TXT, inmune al jitter del taladro).

---

## `2026-09-07_inercia` — inercia y fricción del rotor

Log del VESC Tool durante una deceleración libre. CSV con `;` como separador.

| Ruta | Qué es |
|---|---|
| `2026-09-07_test_inercia.csv` | Log del VESC Tool (195 KB, sí versionado) |

**Análisis:** `04_model/scripts/inertia_from_vesc_log.py`.

---

## `2026-10-31_can_logger_bench` — registrador CAN en banco

Tráfico CAN crudo del VESC grabado por el registrador propio
(`05_firmware/arduino/can_logger/`), ruedas en el aire. Formato en el README del
registrador. Historia completa en `07_experiments/EXP-002-ruido-spi-can-logger.md`.

| Ruta | Qué es |
|---|---|
| `raw/log_003…010.csv` | Primeras grabaciones, cortadas por reinicios del ESP32 |
| `raw/log_012.csv` | Ensayo A: ESP32 solo, sin VESC (138 s) |
| `raw/log_013.csv` | Ensayo B: VESC encendido, motor parado (144 s) |
| `raw/log_014.csv` | Ensayo C: con gas, antes del arreglo de hardware (70 s, tramas corruptas) |
| `raw/log_017.csv` | **Con gas, después del arreglo** (137 s, 0 corruptas). Fusión por mayoría de `log_017_dl1…3.csv` |
| `raw/log_017_dl1…3.csv` | Las tres descargas por USB tal cual, con la basura del puerto serie |

013, 014 y 017 se descargaron por USB tres veces y se fusionaron por mayoría: la
descarga por puerto serie mete alguna línea basura. Con lector de tarjetas no hace falta.

**Análisis:** `04_model/scripts/can_log_decode.py` → figura
`04_model/results/can_logger_log017.png`.

---

## Cómo añadir una campaña

1. `mkdir 06_data/AAAA-MM-DD_<ensayo>/raw`.
2. Volcar los archivos del instrumento en `raw/`, sin renombrar ni recortar.
3. Añadir una sección aquí: qué se midió, con qué montaje y qué script lo lee.
4. La figura de salida va a `04_model/results/`, nunca junto a los datos.
