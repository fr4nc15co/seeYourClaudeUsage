# seeYourClaudeUsage

**English** · [Español](#español)

Cost analysis panel for Claude Code. Reads transcripts from `~/.claude`, calculates equivalent API costs, and serves an interactive HTML dashboard.

## Quick Start

```bash
python3 main.py
```

That's it. The script analyzes your sessions, starts the server at `http://localhost:8799`, and opens the dashboard in your browser automatically.

**Requirements:** Python 3.8+ (no external dependencies — no need for `pip install`).

### Options

```bash
python3 main.py --port 9000            # custom port
python3 main.py --interval 300         # auto-refresh every 5 min
python3 main.py --share                # accessible from other devices on the network
```

### Screenshots

<table>
<tr>
<td><b>Costs</b> — KPIs, daily spending and model breakdown</td>
<td><b>Productivity</b> — session metrics and performance</td>
</tr>
<tr>
<td><img src="docs/screenshots/tab_costes.png" width="480"></td>
<td><img src="docs/screenshots/tab_productividad.png" width="480"></td>
</tr>
<tr>
<td><b>Activity</b> — tokens by day, week and hour</td>
<td><b>Sessions</b> — list with cost, model and project</td>
</tr>
<tr>
<td><img src="docs/screenshots/tab_actividad.png" width="480"></td>
<td><img src="docs/screenshots/tab_sesiones.png" width="480"></td>
</tr>
<tr>
<td><b>Recommendations</b> — rightsizing, caching and estimated savings</td>
<td></td>
</tr>
<tr>
<td><img src="docs/screenshots/tab_recomendaciones.png" width="480"></td>
<td></td>
</tr>
</table>

### Dashboard Features

- **Total cost and per-model** — what each session would cost at API rates (amounts in €, editable exchange rate)
- **Current month** — monthly spending, daily average, and end-of-month projection
- **Temporal evolution** — day / week / month selector and range (7/30/90 days · month); hourly heatmap
- **Files and patterns** — most read/edited files, detection of intensive re-reads, most-used shell commands
- **Activity types** — automatic classification (no AI) into 11 categories (Programming, Debugging, Refactoring, Testing, Documentation, Exploration, Research, Orchestration, DevOps…)
- **Top tools** — global count of each tool (Bash, Edit, Read, Agent…)
- **Model recommendations** — rightsizing by session length and activity type; estimated savings
- **Projects** — breakdown by project with cost and sessions
- **Cache** — tokens read/written and estimated cache savings
- **Subscription vs API** — monthly comparison with available plans (your plan highlighted)
- **Rate limits reached** — rate-limit errors and session limits detected
- **Skills and Tasks** — skill usage and created tasks
- **Auto-improvement** — evolution between runs (cost delta, sessions, limits)
- **CSV export** — button in Sessions tab; also generates `panel_costes/sesiones.csv` each run

### Static HTML Alternative (No Server)

```bash
cd panel_costes
python3 analizar.py
# Open panel_costes/panel.html in your browser
```

Generates a self-contained HTML file (embedded data, no CDN, works offline).

### Security and Privacy

- Access to `~/.claude` **read-only mode only** — never writes or deletes anything there.
- All writes happen exclusively in `panel_costes/`.
- The generated panel contains your session prompts: share it only with appropriate people.
- `--share` has no password; use it only on trusted networks.

### Customize Rates

Edit [`panel_costes/precios.json`](panel_costes/precios.json) and re-run.
Key settings:
- `modelos` — USD per 1M tokens (input/output) per model
- `suscripciones_usd_mes` — monthly fee for each plan in the comparison
- `eur_por_usd` — exchange rate to display amounts in €
- `plan_actual` — name of your current plan; highlighted in Subscription vs API comparison

Also editable from the dashboard at **System → Rates** while the server is running.

### Generated Files (inside `panel_costes/`)

| File | Content |
|---|---|
| `panel.html` / `index.html` | The visual dashboard (self-contained, no CDN) |
| `datos.json` | Calculated dataset (inspectable) |
| `sesiones.csv` | Session details in CSV (UTF-8 with BOM, opens in Excel) |
| `estado/historial.jsonl` | One line per run |
| `estado/resumen.json` | Latest summary + file fingerprint |
| `estado/memoria.json` | Accumulated memory between runs |
| `estado/insights.md` | Recommendations from last run |
| `estado/eventos_cache.json` | Incremental cache by file (speeds up re-analysis) |

### Subscription Plans Compared

| Plan | USD/month |
|---|---|
| Pro | 20 |
| Teams Standard | 25 |
| Teams Premium 5x | 125 |
| Max 5x | 100 |
| Max 20x | 200 |

> Edit `precios.json` to adjust based on your actual invoice.

---

## Español

Panel de análisis de coste para Claude Code. Lee los transcripts de `~/.claude`,
calcula el equivalente a tarifas de API y sirve un dashboard HTML interactivo.

### Inicio rápido

```bash
python3 main.py
```

Eso es todo. El script analiza tus sesiones, arranca el servidor en
`http://localhost:8799` y abre el panel en el navegador automáticamente.

**Requisitos:** Python 3.8+ (sin dependencias externas — no necesitas `pip install`).

### Opciones

```bash
python3 main.py --puerto 9000          # puerto distinto
python3 main.py --intervalo 300        # refresco automático cada 5 min
python3 main.py --compartir            # accesible desde otros equipos de la red
```

### Capturas de pantalla

<table>
<tr>
<td><b>Costes</b> — KPIs, gasto por día y desglose por modelo</td>
<td><b>Productividad</b> — métricas de sesiones y rendimiento</td>
</tr>
<tr>
<td><img src="docs/screenshots/tab_costes.png" width="480"></td>
<td><img src="docs/screenshots/tab_productividad.png" width="480"></td>
</tr>
<tr>
<td><b>Actividad</b> — tokens por día, semana y hora</td>
<td><b>Sesiones</b> — listado con coste, modelo y proyecto</td>
</tr>
<tr>
<td><img src="docs/screenshots/tab_actividad.png" width="480"></td>
<td><img src="docs/screenshots/tab_sesiones.png" width="480"></td>
</tr>
<tr>
<td><b>Recomendaciones</b> — rightsizing, caché y ahorros estimados</td>
<td></td>
</tr>
<tr>
<td><img src="docs/screenshots/tab_recomendaciones.png" width="480"></td>
<td></td>
</tr>
</table>

### Qué incluye el panel

- **Coste total y por modelo** — cuánto costaría cada sesión a tarifas de API (importes en €, tasa editable)
- **Mes en curso** — gasto del mes, media diaria y proyección a fin de mes
- **Evolución temporal** — selector día / semana / mes y rango (7/30/90 días · mes); heatmap por hora
- **Archivos y patrones** — ficheros más leídos/editados, detección de relecturas intensas, comandos shell más usados
- **Tipos de actividad** — clasificación automática (sin IA) en 11 categorías (Programación, Depuración, Refactorización, Pruebas, Documentación, Exploración, Investigación, Orquestación, DevOps…)
- **Herramientas más usadas** — recuento global de cada tool (Bash, Edit, Read, Agent…)
- **Recomendaciones de modelo** — rightsizing por longitud de sesión y por tipo de actividad; ahorros estimados
- **Proyectos** — desglose por proyecto con coste y sesiones
- **Caché** — tokens leídos/escritos y ahorro estimado por caching
- **Suscripción vs API** — comparativa mensual frente a los planes disponibles con tu plan resaltado
- **Límites alcanzados** — errores de rate-limit y límites de sesión detectados
- **Skills y Tasks** — uso de skills y tareas creadas
- **Auto-mejora** — evolución entre ejecuciones (delta gasto, sesiones, límites)
- **Exportación CSV** — botón en la pestaña Sesiones; también genera `panel_costes/sesiones.csv` en cada ejecución

### Alternativa sin servidor (HTML estático)

```bash
cd panel_costes
python3 analizar.py
# Abre panel_costes/panel.html en el navegador
```

Genera un fichero HTML autocontenido (datos embebidos, sin CDN, funciona offline).

### Seguridad y privacidad

- Acceso a `~/.claude` **solo en modo lectura** — nunca escribe ni borra nada ahí.
- Toda escritura ocurre exclusivamente en `panel_costes/`.
- El panel generado contiene los prompts de tus sesiones: compártelo solo con quien corresponda.
- `--compartir` no lleva contraseña; úsalo solo en redes de confianza.

### Personalizar tarifas

Edita [`panel_costes/precios.json`](panel_costes/precios.json) y vuelve a ejecutar.
Las claves principales:
- `modelos` — USD por 1M tokens (input/output) por modelo
- `suscripciones_usd_mes` — cuota mensual de cada plan para la comparativa
- `eur_por_usd` — tasa para mostrar los importes en €
- `plan_actual` — nombre del plan contratado; se resalta en la comparativa Suscripción vs API

También editables desde el panel en **Sistema → Tarifas** con el servidor en marcha.

### Ficheros generados (dentro de `panel_costes/`)

| Fichero | Contenido |
|---|---|
| `panel.html` / `index.html` | El panel visual (autocontenido, sin CDN) |
| `datos.json` | Dataset calculado (inspeccionable) |
| `sesiones.csv` | Detalle de sesiones en CSV (UTF-8 con BOM, abre en Excel) |
| `estado/historial.jsonl` | Una línea por ejecución |
| `estado/resumen.json` | Último resumen + huella de ficheros |
| `estado/memoria.json` | Memoria acumulada entre ejecuciones |
| `estado/insights.md` | Recomendaciones de la última ejecución |
| `estado/eventos_cache.json` | Caché incremental por fichero (acelera el reanálisis) |

### Planes de suscripción comparados

| Plan | USD/mes |
|---|---|
| Pro | 20 |
| Teams Standard | 25 |
| Teams Premium 5x | 125 |
| Max 5x | 100 |
| Max 20x | 200 |

> Edita `precios.json` para ajustar según tu factura real.
