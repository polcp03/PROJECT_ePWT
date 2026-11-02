# Git, explicado desde cero

Nota de aprendizaje. Escrita porque me perdía con Git y necesitaba entender **qué es**
antes de memorizar comandos.

## 1. Qué problema resuelve Git

Sin Git, guardar versiones se hace así: `modelo_v1.slx`, `modelo_v2.slx`,
`modelo_v2_bueno.slx`, `modelo_final_DEFINITIVO.slx`. Todo el mundo ha hecho esto.
Falla por tres razones:

1. No sabes **qué cambió** entre v1 y v2. Solo tienes dos archivos.
2. No sabes **por qué** cambió. El motivo estaba en tu cabeza y se te ha olvidado.
3. Si v3 rompe algo, no puedes volver a v2 sin perder lo bueno de v3.

Git guarda **la secuencia de cambios**, no copias del archivo. Y cada cambio lleva
adjunto un mensaje que explica el porqué. Eso es todo el invento.

Para este proyecto es directamente una herramienta de ingeniería: dentro de seis meses
querré saber *por qué* cambié un parámetro del modelo, y la respuesta estará escrita.

## 2. Los cuatro sitios donde vive tu trabajo

Este es el concepto que más cuesta, y sin él nada tiene sentido.

```
  Working directory  ->  Staging area  ->  Repositorio local  ->  Remoto (GitHub)
   (tus archivos)        (git add)         (git commit)           (git push)
```

- **Working directory** — los archivos tal y como están en tu disco ahora mismo.
- **Staging area** — la "bandeja de salida". Aquí eliges *qué parte* de tu trabajo
  entra en la siguiente foto. Existe porque a veces tocas 5 archivos y solo 3
  pertenecen al mismo cambio lógico.
- **Repositorio local** — el historial, en tu PC, en la carpeta `.git`. Aquí es
  donde vive de verdad tu proyecto.
- **Remoto (GitHub)** — una copia del historial en un servidor. Es backup y es
  escaparate, pero **no es Git**: Git funciona entero sin internet.

## 3. Los cinco comandos que cubren el 95%

```bash
git status
```
"¿Dónde estoy y qué he tocado?" Ejecútalo constantemente. No cambia nada, solo informa.

```bash
git add 04_model/params/vehicle.m
```
Mueve ese archivo a la bandeja de salida. `git add .` mete todo lo modificado.

```bash
git commit -m "Add measured phase resistance from C01"
```
Hace la foto y le pega el mensaje. **El mensaje es la parte valiosa**, no el comando.
Un commit debe ser *un cambio lógico*: si el mensaje necesita un "y", probablemente
son dos commits.

```bash
git push
```
Sube tus commits a GitHub.

```bash
git log --oneline
```
Ver el historial. Aquí es donde se cobra todo el esfuerzo.

## 4. Ramas: qué son de verdad

Una rama **no es una copia de la carpeta**. Es solo una etiqueta que apunta a un commit.
Por eso crear una rama es instantáneo aunque el proyecto pese 2 GB.

Sirve para esto: quiero probar un modelo de neumático distinto sin romper el que
funciona. Creo una rama, experimento, y si sale mal la borro y no ha pasado nada.
Si sale bien, la fusiono.

```bash
git switch -c model/tyre-slip     # crear rama y saltar a ella
git switch master                  # volver
```

Convención de nombres que voy a usar: `area/descripcion-corta`, por ejemplo
`model/longitudinal-v1`, `firmware/can-logger`, `docs/cycle-01`.

## 5. Pull Request: qué es y por qué lo hago trabajando solo

Un PR es una **propuesta de fusión**: "quiero meter esta rama en `master`, ¿lo revisamos?".
En un equipo sirve para que otro revise el código.

Trabajando solo parece absurdo. No lo es, por dos razones:

1. **Te obliga a mirar tu propio diff antes de que sea permanente.** Ver todos tus
   cambios juntos, en rojo y verde, encuentra errores que no ves mientras escribes.
2. **El PR es documentación.** Su descripción explica *por qué* existe este bloque de
   trabajo. Dentro de un año, el historial de PRs cuenta la historia del proyecto
   mucho mejor que los commits sueltos.

Y para este proyecto en concreto: aprender el flujo de PR **es un objetivo declarado**.
Practicarlo solo, sin la presión de un equipo, es la mejor forma de llegar preparado.

## 6. El flujo completo, un ciclo de trabajo real

```bash
git fetch origin                           # 1-2. traerse lo ultimo de GitHub
git switch -c model/longitudinal-v1 origin/master   # 3. rama nueva desde el master de GitHub
# ... trabajar ...
git add .                                  # 4. seleccionar
git commit -m "Add longitudinal vehicle model"   # 5. foto + porque
git push -u origin model/longitudinal-v1   # 6. subir la rama
gh pr create --fill                        # 7. abrir el PR (GitHub CLI)
gh pr merge --merge                        # 8. fusionar cuando este revisado (merge commit, nunca squash)
```

## 7. Errores típicos y cómo salir

| Situación | Qué hacer |
|---|---|
| He hecho `add` de algo que no quería | `git restore --staged archivo` |
| Quiero descartar cambios de un archivo | `git restore archivo` (**destruye** el trabajo) |
| El último commit tiene un mensaje malo | `git commit --amend -m "mensaje bueno"` (solo si no has hecho push) |
| Estoy perdido | `git status`. Siempre. Te dice dónde estás y qué opciones tienes |

## 8. Qué NO meter en Git

- Ejecutables y programas descargados (VESC Tool) → `_tools/`, ignorado.
- Entornos virtuales de Python (`.venv/`) → se reconstruyen con un comando.
- Salidas de compilación (`slprj/`, `build/`, `.pio/`).
- Archivos enormes. Git nunca olvida: si metes 1 GB, el repo pesa 1 GB para siempre,
  aunque luego lo borres.

**Regla:** el repositorio contiene lo que yo creo, no lo que descargo ni lo que se
puede regenerar.
