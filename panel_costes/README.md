# Panel de costes de Claude Code

Analiza tus transcripts de Claude Code (`~/.claude`), calcula el coste de cada
sesión a las **tarifas públicas de la API** y genera un panel HTML local con el
gasto por modelo y por día, comparativa con/sin suscripción, tokens, límites
alcanzados, actividad, skills, memoria y auto-mejora. Importes en **euros** (tasa
editable). Incluye **rango temporal** (7/30/90 días · mes), **proyección de gasto**
de fin de mes, marca de **tu plan** en la comparativa, **escaneo incremental** (solo
relee los transcripts que cambiaron) y, con el servidor, **aviso de datos nuevos en vivo**.

<table>
<tr>
<td><img src="../docs/screenshots/tab_costes.png" width="480"></td>
<td><img src="../docs/screenshots/tab_optimizacion.png" width="480"></td>
</tr>
<tr>
<td><img src="../docs/screenshots/tab_actividad.png" width="480"></td>
<td><img src="../docs/screenshots/tab_sesiones.png" width="480"></td>
</tr>
</table>

## 🔒 Garantía de solo lectura
- Todo acceso a `~/.claude` se hace **en modo lectura** (`open(..., "r")`) a través de
  `leer_claude()`, que además verifica que la ruta está dentro de `~/.claude`.
- **Toda escritura** ocurre exclusivamente bajo `panel_costes/`. La función
  `escribir()` aborta si la ruta destino cae dentro de `~/.claude`.
- El motor **nunca crea, modifica ni borra nada** en `~/.claude`.

## Uso
```bash
cd panel_costes
python3 analizar.py        # no necesita dependencias externas
```
Abre **`panel_costes/panel.html`** (o `index.html`) en el navegador. Es un fichero
autocontenido (datos embebidos, gráficos SVG propios, sin CDN → funciona offline).

## Servidor local (URL local · refresco con botón)
Arranca el servidor: **regenera los datos al arrancar** y sirve el panel en una **URL local**.
El refresco es **manual con un botón** — no hay temporizador por defecto.
```bash
cd panel_costes
python3 servidor.py                 # http://localhost:8799/  (solo tu ordenador)
python3 servidor.py --puerto 9000
python3 servidor.py --intervalo 300 # opcional: además, refresco automático cada 5 min
```
Abre `http://localhost:8799/`. Arriba a la derecha tienes **“🔄 Actualizar ahora”**: al
pulsarlo el servidor regenera los datos (solo lectura sobre `~/.claude`, vía el endpoint
`/regenerar`) y la página se recarga con lo último. Además, la página comprueba en segundo
plano (endpoint `/version`) si el servidor regeneró los datos y muestra un aviso
**🟢 Datos nuevos — recargar**. La caché del navegador está desactivada
(`Cache-Control: no-store`). `Ctrl+C` para parar.

## Compartir (que cada uno pueda verlo)
Tres formas, de más simple a más “en red”:
1. **Enviar el fichero** `panel.html` (o `index.html`). Es **autocontenido** (datos
   embebidos, sin CDN): quien lo reciba lo abre en su navegador y lo ve, sin instalar nada.
   Es una foto fija del momento en que lo generaste.
2. **Servir en tu red local** para que otros equipos entren a tu panel en vivo:
   ```bash
   python3 servidor.py --compartir      # escucha en 0.0.0.0
   ```
   El servidor imprime las URLs de red (p. ej. `http://192.168.1.20:8799/`) que los demás
   abren desde el mismo Wi-Fi/LAN. ⚠ **No lleva contraseña** y el panel contiene los
   *prompts* de tus sesiones: compártelo solo en una **red de confianza**.
3. **Que cada uno mida lo suyo**: copia la carpeta `panel_costes/` a otro equipo y que
   ejecute `python3 analizar.py` allí — analizará *su* propio `~/.claude`.

## Qué genera (todo dentro de `panel_costes/`)
| Fichero | Contenido |
|---|---|
| `panel.html` / `index.html` | El panel visual (mismo contenido). |
| `datos.json` | El dataset crudo calculado (inspeccionable). |
| `precios.json` | **Tarifas editables** (entrada/salida por 1M tokens, suscripciones). |
| `estado/historial.jsonl` | Una línea por ejecución (auto-mejora). |
| `estado/resumen.json` | Último resumen + huella de ficheros (para detectar nuevos/cambiados). |
| `estado/memoria.json` | Memoria acumulada del panel (proyecto top, hora pico, etc.). |
| `estado/insights.md` | Recomendaciones legibles de la última ejecución. |
| `estado/eventos_cache.json` | Caché incremental por fichero (acelera el reanálisis; se regenera solo, se versiona). |

## Cómo se calcula el coste
A partir del bloque `usage` de cada mensaje *assistant*:
- **input** × tarifa_input · **output** × tarifa_output
- **cache_read** × 0,10 × tarifa_input
- **cache_write 5m** × 1,25 × tarifa_input · **cache_write 1h** × 2,0 × tarifa_input
- **web_search** × ($10 / 1000)

Las llamadas se **deduplican** por `message.id` (no se cuentan dos veces aunque el
registro aparezca en varios ficheros). Se incluyen los transcripts de **subagentes**
y workflows, atribuidos a su sesión padre. Fechas/horas en **zona local**.

> El "coste" es el **contrafactual**: lo que pagarías *si* hubieras usado la API por
> token. Si usas suscripción (tarifa plana), tu pago real es la cuota mensual; por eso
> el panel compara ambas cosas.

## Suscripción vs API
Compara, sobre los meses con actividad, el coste API calculado frente a los planes de
`precios.json` (Pro / Teams / Max 5x / Max 20x / Enterprise). Si alcanzaste el
**límite de sesión** varias veces, el panel lo avisa: la opción más barata por precio
puede no tener bastante margen de uso.

> Teams y Enterprise tienen precio **por usuario**. El valor en `precios.json` asume
> 1 usuario; ajusta la cifra de Enterprise si tienes un contrato con tarifa distinta.

## Límites
- **Alta confianza**: errores de API registrados (`isApiErrorMessage`), clasificados en
  *límite de uso* (incluye "hit your session limit"), *error de servidor*,
  *prompt demasiado largo*, *acceso a modelo*, *otro*.
- **Menciones en contenido**: heurística orientativa (texto que menciona límites).

## Auto-mejora (mejora en cada ejecución)
Cada ejecución: registra un resumen, **compara con la anterior** (Δ gasto, Δ sesiones,
Δ requests, Δ límites), detecta **transcripts nuevos/cambiados**, refina la **memoria
acumulada**, regenera **recomendaciones** y dibuja la evolución del coste por ejecución.
Los **modelos sin tarifa** que aparezcan se registran para que amplíes `precios.json`
(mejora la cobertura del cálculo).

## Actualizar tarifas
Edita `precios.json` (USD por 1M tokens) y vuelve a ejecutar. Claves útiles: `eur_por_usd`
(tasa para mostrar los importes en €; las tarifas se siguen editando en USD) y `plan_actual`
(nombre del plan contratado, que se resalta en la comparativa). También editables desde
el panel en **Sistema → Tarifas** con el servidor en marcha. Fuente por defecto:
referencia de la API de Anthropic (cacheada 2026-05-26). Si en el futuro cambian los
precios o aparecen modelos nuevos, solo tienes que tocar ese fichero.
