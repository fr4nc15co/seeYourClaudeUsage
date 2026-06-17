# motor_agentico_basico — Guía para Claude

Panel de costes y análisis para Claude Code. Lee los transcripts JSONL de `~/.claude`,
calcula costes a tarifas API, clasifica actividad y sirve un dashboard HTML interactivo.

---

## Estructura del proyecto

```
motor_agentico_basico/
├── panel_costes/
│   ├── analizar.py          # Motor principal de análisis (≈1 336 líneas)
│   ├── servidor.py          # Servidor HTTP local en :8799 (193 líneas)
│   ├── plantilla_html.py    # Template HTML+JS+CSS autocontenido (~71 k líneas)
│   ├── precios.json         # Tarifas editables (input/output por modelo, presupuesto)
│   ├── datos.json           # Salida generada: dataset completo
│   ├── panel.html / index.html  # Dashboard generado (listo para abrir)
│   ├── sesiones.csv         # Export CSV con BOM (compatible Excel)
│   └── estado/
│       ├── historial.jsonl  # Una línea JSON por ejecución (timestamp, coste, sesiones…)
│       ├── resumen.json     # Resumen de la última ejecución + stat de archivos
│       ├── memoria.json     # Acumulado: proyecto top, modelo dominante, hora pico…
│       ├── insights.md      # Recomendaciones legibles generadas automáticamente
│       └── eventos_cache.json  # Caché incremental (clave: path → {size, mtime, rec})
├── .claude/
│   └── launch.json          # Config de Claude Code para arrancar el servidor
├── docs/screenshots/        # Capturas de las 4 pestañas del dashboard
└── README.md
```

**Invariante crítica:** `analizar.py` es **solo lectura sobre `~/.claude`**. Nunca escribe
ahí. Toda salida va a `panel_costes/`. Hay guardas explícitas en `leer_claude()` y
`escribir()` que abortan si el destino está dentro de `~/.claude`.

---

## Módulos clave

### `analizar.py` — Motor de análisis

**Punto de entrada:** ejecutar directamente (`python3 analizar.py`).

**Flujo completo:**

```
glob ~/.claude/projects/**/*.jsonl
  └─> _extraer_archivo(path)          # parsea un JSONL: eventos, tools, errores
        └─ cache hit? → usa eventos_cache.json (clave: size+mtime)
        └─ cache miss? → relee y guarda
  └─> _agregar(recs)                  # desduplicación + acumulación global
        └─ dedup por message.id (set `vistos`)
        └─ coste_evento() por cada evento
        └─ construye: by_day, by_hour, by_model, por_sesion, herramientas…
  └─> cargar_facets()                 # outcome/satisfacción desde usage-data/facets/
  └─> cargar_meta()                   # duración, tools, git desde usage-data/session-meta/
  └─> construir(A, facets, meta, …)   # dataset final (40+ claves de top-level)
  └─> auto_mejora(datos, …)           # deltas vs ejecución anterior, actualiza estado/
  └─> render(datos, mejora, …)        # embebe JSON en plantilla → panel.html, datos.json
  └─> escribir_csv(datos)             # → sesiones.csv
```

**Funciones principales:**

| Función | Qué hace |
|---------|----------|
| `_es_seguro_escribir(path)` | Retorna `True` si el path está **dentro** de `~/.claude` (usado para bloquear escrituras) |
| `leer_claude(path)` | Lectura segura desde `~/.claude`; verifica que el path sea subpath válido |
| `escribir(path, content)` | Escritura atómica (`.tmp` + rename) solo en `panel_costes/`; aborta si destino es `~/.claude` |
| `cargar_precios()` | Carga `precios.json`; devuelve dict con modelos, tarifas, suscripciones, presupuesto |
| `normaliza_modelo(m)` | Elimina sufijos de fecha y prefijos de proveedor; mapea aliases → clave canónica |
| `coste_evento(uso, modelo, precios)` | `input*P.in + output*P.out + cache_read*P.in*0.10 + cache_w5*P.in*1.25 + cache_w1h*P.in*2.00 + web*0.01` |
| `clasificar_actividad(texto, tools)` | Clasifica en 11 categorías sin LLM: primero keywords en texto, luego mezcla de tools |
| `_extraer_archivo(path)` | Lee un `.jsonl`; devuelve `{events, tools, limites}` (tokens crudos, sin coste) |
| `_agregar(recs)` | Agrega todos los registros; desduplicación global; calcula costes con tarifas actuales |
| `analizar_transcripts()` | Orquesta extracción + caché incremental para todos los archivos |
| `cargar_facets()` | Lee `~/.claude/usage-data/facets/*.json` → outcome, helpfulness, friction, satisfaction |
| `cargar_meta()` | Lee `~/.claude/usage-data/session-meta/*.json` → duración, herramientas, git stats |
| `contar_tasks()` | Cuenta tasks por estado en `~/.claude/tasks/` |
| `construir(…)` | Ensambla el dataset final (`datos.json`) con todas las vistas y métricas |
| `auto_mejora(datos, A, ahora)` | Compara con `resumen.json` anterior; actualiza `memoria.json`, `historial.jsonl`, `insights.md` |
| `escribir_csv(datos)` | Exporta sesiones a `sesiones.csv` con UTF-8 BOM |
| `render(datos, mejora, …)` | Inyecta JSON en `plantilla_html.py`; escribe `panel.html`, `index.html`, `datos.json` |

**Caché incremental (`eventos_cache.json`):**
- Versión `CACHE_VER = 2` (si cambia el formato, se descarta todo el caché automáticamente)
- Clave por archivo: `{size, mtime}` → si ambos coinciden, se usan los tokens ya extraídos
- **Coste siempre se recalcula** en vivo con `precios.json` → editar tarifas funciona sin borrar caché

**Desduplicación:**
- Set global `vistos` keyed por `message.id` (o `uuid` para eventos de límite)
- Evita doble conteo cuando el mismo mensaje aparece en varios `.jsonl` (subagentes, workflows)

**Clasificación de actividad (11 categorías):**
1. Keywords en el texto del prompt (Refactorización, Depuración, Documentación…)
2. Mezcla de tools usadas (Agent≥2 → Orquestación, WebSearch≥2 → Investigación, Edit≥3 → Programación…)
3. Fallback: Exploración o "Otro"

---

### `servidor.py` — Servidor HTTP

**Puerto:** `127.0.0.1:8799` (o `0.0.0.0` con `--compartir`).

**Arranque:** `python3 servidor.py [--puerto N] [--intervalo N] [--compartir]`

**Endpoints:**

| Ruta | Método | Acción |
|------|--------|--------|
| `/` `/analisisClaude` | GET | Redirige a `/panel.html` |
| `/panel.html` | GET | Sirve el dashboard generado |
| `/datos.json` | GET | Dataset completo (para inspección) |
| `/version` | GET | `{generado, coste}` — el cliente hace polling cada 5 s para mostrar badge "Datos nuevos" |
| `/regenerar` | GET | Ejecuta `analizar.py` en subproceso (lock thread-safe); devuelve datos actualizados |
| `/guardar-precios` | POST | Valida y guarda nuevo `precios.json`; regenera dashboard |

Al arrancar lanza `analizar.py` automáticamente. Con `--intervalo N` lo relanza en background
cada N segundos.

---

### `plantilla_html.py` — Template del dashboard

Contiene el HTML/CSS/JS completo del dashboard embebido como string de Python.
El JSON de `datos.json` se inyecta inline al hacer `render()`.
**No depende de CDN** — funciona offline tras generarse.

**5 pestañas:**

| Pestaña | Contenido |
|---------|-----------|
| Costes | Gráficas diarias/semanales/mensuales, donut por modelo, heatmap horario, comparativa suscripción |
| Actividad | Uso de tools, patrones de acceso a archivos, relecturas >3, comandos bash top |
| Optimización | Rightsizing (sesiones cortas en modelos premium), ajuste por tipo de actividad, ahorros estimados |
| Sesiones | Tabla sortable/filtrable con 40+ columnas: coste, proyecto, categoría, outcome, satisfacción, git stats |
| Sistema | Editor de tarifas, resumen de límites, uso de skills/tasks, deltas auto-mejora, historial de ejecuciones |

---

## Dataset `datos.json` — claves top-level

```
generado, tz, claude_dir, solo_lectura
totales          → coste total + desglose (input/output/cache_read/cache_write/web), tokens, requests, sesiones, proyectos
by_model[]       → por modelo: coste, requests, tokens, share%
by_day[]         → por día: coste, requests, modelos{}
by_week[]        → por semana ISO
by_project[]     → por proyecto: coste, requests, sesiones
by_categoria[]   → por categoría de actividad
sesiones[]       → cada sesión: id, proyecto, categoria, inicio, fin, duracion_min, coste, requests,
                   tokens, modelo_top, modelos{}, msgs_user, msgs_assist, tools{}, languages{},
                   git_commits, git_pushes, files_mod, lineas_mas/menos, tool_errors,
                   primer_prompt, objetivo, resultado, satisfaccion, ayuda, friccion, tipo_sesion, subagente
herramientas[]   → tool: nombre, veces, sesiones
archivos[]       → archivo: read, edit, write, total, sesiones, max_relec
relecturas[]     → archivos con >3 lecturas en una sesión
bash_top[]       → comandos bash más frecuentes
by_hour[]        → coste + requests por hora del día
heat[][]         → matriz [weekday][hour] de coste (para heatmap)
cache{}          → read_tokens, write_tokens, ahorro_estimado, ratio_lectura
subscripcion{}   → comparativa mensual API vs planes; mejor_opcion, roi_multiplicador
eficiencia{}     → coste_por_sesion, output_por_dolar, ahorro_cache_pct…
limites{}        → alta_confianza, por_dia{}, categorias{}, eventos[]
presupuesto{}    → gasto_mes, proyeccion, presupuesto, pct_usado, restante
rightsizing{}    → candidatas[], ahorro_total, recs[]
ajuste_actividad{} → categorias[], ahorro_total, recs[]
skills[]         → nombre, veces, sesiones
tasks{}          → por proyecto: completed, in_progress, archived
outcomes{}       → conteo por resultado
```

---

## `precios.json` — Configuración de tarifas

```json
{
  "modelos": {
    "fable-5":    { "input": 10.00, "output": 50.00, "etiqueta": "Fable 5",    "color": "#a855f7" },
    "opus-4-8":   { "input":  5.00, "output": 25.00, "etiqueta": "Opus 4.8",   "color": "#f59e0b" },
    "sonnet-4-6": { "input":  3.00, "output": 15.00, "etiqueta": "Sonnet 4.6", "color": "#3b82f6" },
    "haiku-4-5":  { "input":  1.00, "output":  5.00, "etiqueta": "Haiku 4.5",  "color": "#10b981" }
  },
  "web_search_por_1000": 10.00,
  "presupuesto_usd_mes": 0,
  "eur_por_usd": 0.86,
  "plan_actual": "...",
  "suscripciones_usd_mes": { "Pro": 20, "Max 5x": 100, ... }
}
```

Tarifa en USD por millón de tokens. Cache read = 10% del precio input.
Cache write 5 min = 125%; cache write 1 h = 200%.

---

## Comandos frecuentes

```bash
# Análisis único (genera panel.html + datos.json + sesiones.csv)
cd panel_costes && python3 analizar.py

# Servidor interactivo en localhost:8799
python3 servidor.py

# Auto-refresh cada 5 minutos
python3 servidor.py --intervalo 300

# Accesible en red local
python3 servidor.py --compartir
```

---

## Dónde tocar cada cosa

| Necesidad | Archivo |
|-----------|---------|
| Cambiar tarifas de modelos | `panel_costes/precios.json` (o UI del tab Sistema) |
| Añadir/cambiar categorías de actividad | `analizar.py` → `clasificar_actividad()` |
| Cambiar fórmula de coste | `analizar.py` → `coste_evento()` |
| Cambiar la lógica de rightsizing | `analizar.py` → sección `rightsizing` en `construir()` |
| Modificar el dashboard visual | `panel_costes/plantilla_html.py` |
| Cambiar endpoints del servidor | `panel_costes/servidor.py` |
| Añadir modelo nuevo | `precios.json` + `normaliza_modelo()` en `analizar.py` |

---

## Notas para ediciones seguras

- Nunca tocar nada en `~/.claude` — es solo lectura por diseño.
- `datos.json`, `panel.html`, `sesiones.csv` son archivos **generados** — no editar a mano.
- `eventos_cache.json` puede borrarse sin riesgo (se regenera en el siguiente análisis).
- `estado/` puede borrarse sin riesgo (se pierde el historial de ejecuciones pero no los datos fuente).
- Para forzar reanálisis completo: borrar `estado/eventos_cache.json`.
