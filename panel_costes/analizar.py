#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Panel de costes de Claude Code  —  motor analizador (SOLO LECTURA sobre ~/.claude)
==================================================================================

Lee los transcripts de Claude Code en ~/.claude, calcula el coste de cada sesion
a las tarifas publicadas de la API, y genera un panel HTML local autocontenido.

GARANTIA DE SOLO-LECTURA:
  - Todo acceso a ~/.claude se hace en modo lectura ('r') a traves de leer_claude().
  - Toda escritura ocurre EXCLUSIVAMENTE bajo este directorio (panel_costes/),
    nunca bajo ~/.claude. Se verifica en tiempo de ejecucion (guardia _es_seguro_escribir).

AUTO-MEJORA:
  - Cada ejecucion guarda un resumen en estado/historial.jsonl y refina estado/memoria.json.
  - Compara con la ejecucion anterior (deltas de gasto, sesiones nuevas, limites nuevos).
  - Registra modelos desconocidos para que amplies precios.json -> mejora la cobertura.

Uso:   python3 analizar.py
"""

import os, sys, json, re, glob, html, csv, io, calendar
from collections import defaultdict, Counter
from datetime import datetime, timezone, timedelta

# --------------------------------------------------------------------------------------
# Configuracion de rutas y guardia de seguridad
# --------------------------------------------------------------------------------------
HOME        = os.path.expanduser("~")
CLAUDE_DIR  = os.path.realpath(os.path.join(HOME, ".claude"))
PROJECTS    = os.path.join(CLAUDE_DIR, "projects")
USAGE_DIR   = os.path.join(CLAUDE_DIR, "usage-data")
TELE_DIR    = os.path.join(CLAUDE_DIR, "telemetry")
TASKS_DIR   = os.path.join(CLAUDE_DIR, "tasks")

OUT_DIR     = os.path.dirname(os.path.realpath(__file__))     # panel_costes/
STATE_DIR   = os.path.join(OUT_DIR, "estado")
PRECIOS     = os.path.join(OUT_DIR, "precios.json")
SALIDA_HTML = os.path.join(OUT_DIR, "panel.html")
SALIDA_JSON = os.path.join(OUT_DIR, "datos.json")

def _es_seguro_escribir(path):
    """True solo si 'path' NO esta dentro de ~/.claude (protege los datos de Claude)."""
    rp = os.path.realpath(path)
    return not (rp == CLAUDE_DIR or rp.startswith(CLAUDE_DIR + os.sep))

def leer_claude(path):
    """Abre un fichero de ~/.claude SIEMPRE en modo lectura, verificando la ruta."""
    rp = os.path.realpath(path)
    if not (rp == CLAUDE_DIR or rp.startswith(CLAUDE_DIR + os.sep)):
        raise PermissionError("leer_claude solo lee dentro de ~/.claude: " + path)
    return open(path, "r", encoding="utf-8", errors="replace")

def escribir(path, contenido):
    if not _es_seguro_escribir(path):
        raise PermissionError("BLOQUEADO: intento de escritura dentro de ~/.claude: " + path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"                       # escritura atomica (el servidor nunca sirve a medias)
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(contenido)
    os.replace(tmp, path)

# --------------------------------------------------------------------------------------
# Precios
# --------------------------------------------------------------------------------------
def cargar_precios():
    with open(PRECIOS, "r", encoding="utf-8") as fh:
        return json.load(fh)

CFG     = cargar_precios()
MODELOS = CFG["modelos"]
WEB_1K  = CFG.get("web_search_por_1000", 10.0)
SUBS    = CFG.get("suscripciones_usd_mes", {"Pro": 20, "Max 5x": 100, "Max 20x": 200})

def normaliza_modelo(m):
    if not m:
        return None
    m = m.lower().strip().replace("[1m]", "")
    if m == "<synthetic>":
        return "synthetic"
    m = re.sub(r"-20\d{6}$", "", m)        # quita sufijo fecha -YYYYMMDD
    m = re.sub(r"^claude-", "", m)         # quita prefijo de proveedor
    return m

def coste_evento(usage, modelo_norm):
    """Devuelve (coste_total, componentes_dict, conocido_bool)."""
    p = MODELOS.get(modelo_norm)
    conocido = p is not None
    if not conocido:
        p = {"input": 0.0, "output": 0.0}
    ri = p["input"] / 1e6
    ro = p["output"] / 1e6

    inp = usage.get("input_tokens", 0) or 0
    out = usage.get("output_tokens", 0) or 0
    cr  = usage.get("cache_read_input_tokens", 0) or 0
    cc  = usage.get("cache_creation", {}) or {}
    c5  = cc.get("ephemeral_5m_input_tokens", 0) or 0
    c1  = cc.get("ephemeral_1h_input_tokens", 0) or 0
    cw_total = usage.get("cache_creation_input_tokens", 0) or 0
    if (c5 + c1) == 0 and cw_total:        # fallback si no hay desglose 5m/1h
        c5 = cw_total

    st = usage.get("server_tool_use", {}) or {}
    ws = st.get("web_search_requests", 0) or 0

    comp = {
        "input":       inp * ri,
        "output":      out * ro,
        "cache_read":  cr * ri * 0.10,
        "cache_w5":    c5 * ri * 1.25,
        "cache_w1":    c1 * ri * 2.00,
        "web_search":  ws * (WEB_1K / 1000.0),
    }
    total = sum(comp.values())
    return total, comp, conocido

# --------------------------------------------------------------------------------------
# Utilidades de fecha / proyecto
# --------------------------------------------------------------------------------------
def parse_ts(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()  # a hora local
    except Exception:
        return None

def proyecto_de_ruta(path):
    """Devuelve (clave_proyecto_dir, sesion_padre, es_subagente)."""
    norm = path.replace("\\", "/")
    idx = norm.find("/projects/")
    if idx < 0:
        return ("desconocido", None, False)
    resto = norm[idx + len("/projects/"):].split("/")
    projdir = resto[0] if resto else "desconocido"
    sesion = None
    if len(resto) >= 2:
        sesion = resto[1]
        if sesion.endswith(".jsonl"):
            sesion = sesion[:-6]
    es_sub = "/subagents/" in norm
    return (projdir, sesion, es_sub)

def nombre_amistoso(projdir):
    n = projdir
    if "GIT-" in n:
        n = n.split("GIT-")[-1]
    elif "Documents-" in n:
        n = n.split("Documents-")[-1]
    return n

def texto_de_contenido(content):
    out = []
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for b in content:
            if isinstance(b, dict):
                if b.get("type") == "text" and b.get("text"):
                    out.append(b["text"])
                elif b.get("type") == "tool_result":
                    c = b.get("content")
                    if isinstance(c, str):
                        out.append(c)
                    elif isinstance(c, list):
                        for x in c:
                            if isinstance(x, dict) and x.get("text"):
                                out.append(x["text"])
    return " ".join(out)

LIMIT_RE = re.compile(r"rate.?limit|limit reached|overloaded|usage limit|too many requests|\b429\b|reset at", re.I)

# --------------------------------------------------------------------------------------
# Clasificacion de actividad por sesion (DETERMINISTA, sin IA)
# --------------------------------------------------------------------------------------
# Inspirado en CodeBurn: en lugar de llamar a un modelo, se infiere el tipo de tarea
# dominante de cada sesion a partir de (1) la mezcla de herramientas usadas y (2)
# palabras clave del primer prompt / objetivo. 100% reproducible y offline.
CATEGORIAS_ACTIVIDAD = [
    "Programación", "Depuración", "Refactorización", "Pruebas", "Documentación",
    "Exploración", "Investigación", "Orquestación", "Configuración/DevOps",
    "Scripting/Shell", "Otro",
]

def clasificar_actividad(tools, texto):
    """Devuelve la categoria de actividad dominante de una sesion (str)."""
    t = (texto or "").lower()
    tools = tools or {}
    def has(*names): return sum(tools.get(n, 0) for n in names)
    edits = has("Edit", "Write", "MultiEdit", "NotebookEdit")
    reads = has("Read", "Grep", "Glob")
    web   = has("WebSearch", "WebFetch")
    bash  = has("Bash")
    agent = has("Agent", "Task")
    def kw(*ws): return any(w in t for w in ws)

    # 1) Intencion explicita en el texto (señal fuerte; el orden marca la prioridad)
    if kw("refactor", "renombr", "reorganiz", "reescrib", "simplifica", "clean up", "limpia el código"):
        return "Refactorización"
    if kw("pytest", "unit test", "test unitario", "tests", "cobertura", "jest", "vitest"):
        return "Pruebas"
    if kw("bug", "debug", "depura", "traceback", "stack trace", "stacktrace",
          "crash", "no funciona", "falla", "arregla", "fix "):
        return "Depuración"
    if kw("readme", "docstring", "documenta", "documentación", "comenta el código"):
        return "Documentación"
    if kw("deploy", "despliega", "docker", "kubernetes", "ci/cd", "pipeline",
          "instala", "setup", "configura el entorno", "variables de entorno"):
        return "Configuración/DevOps"

    # 2) Señal por herramientas (cuando el texto no es concluyente)
    if agent >= 2:                              return "Orquestación"
    if web >= 2 and web >= edits:               return "Investigación"
    if edits >= 3:                              return "Programación"
    if reads >= 3 and edits == 0 and bash == 0: return "Exploración"
    if bash >= 3 and edits == 0:                return "Scripting/Shell"
    if edits >= 1:                              return "Programación"
    if reads >= 1:                              return "Exploración"
    if bash >= 1:                               return "Scripting/Shell"
    if web >= 1:                                return "Investigación"
    return "Otro"

# Modelo "techo" recomendado por tipo de actividad: el mas barato que TIPICAMENTE
# basta para esa clase de tarea. Las categorias NO listadas (Programación, Depuración,
# Orquestación, Otro) se consideran trabajo donde un modelo premium suele justificarse,
# asi que nunca se sugiere degradarlas. Edita este mapa para ajustar la agresividad.
TECHO_ACTIVIDAD = {
    "Exploración":          "haiku-4-5",
    "Investigación":        "haiku-4-5",
    "Scripting/Shell":      "haiku-4-5",
    "Documentación":        "sonnet-4-6",
    "Refactorización":      "sonnet-4-6",
    "Pruebas":              "sonnet-4-6",
    "Configuración/DevOps": "sonnet-4-6",
}
# Rango de "potencia/coste" para no sugerir nunca un modelo mas caro que el actual.
RANGO_MODELO = {"haiku-4-5": 1, "sonnet-4-6": 2,
                "opus-4-6": 3, "opus-4-7": 3, "opus-4-8": 3, "fable-5": 4}

# --------------------------------------------------------------------------------------
# Parseo INCREMENTAL de los transcripts
# --------------------------------------------------------------------------------------
# Para no releer TODO en cada ejecucion, se cachea por fichero lo extraido (eventos
# facturables, herramientas, ficheros tocados, comandos, limites...) junto a su
# (size, mtime). En el siguiente run los ficheros que no han cambiado se sirven del
# cache y solo se releen los nuevos/modificados.
#
# IMPORTANTE: el cache guarda TOKENS crudos, nunca el coste. El coste se recalcula
# SIEMPRE en _agregar() a partir de los tokens, asi que editar precios.json sigue
# recalculando bien aunque todo venga del cache. El cache vive en panel_costes/estado/
# (jamas en ~/.claude) y se versiona: si cambia el formato, se ignora y se relee todo.
CACHE_VER  = 3   # subir si cambia el formato del registro por fichero (p.ej. nuevos campos)
CACHE_PATH = os.path.join(STATE_DIR, "eventos_cache.json")

def _cargar_cache():
    try:
        with open(CACHE_PATH, encoding="utf-8") as fh:
            c = json.load(fh)
        if c.get("version") == CACHE_VER and isinstance(c.get("files"), dict):
            return c["files"]
    except Exception:
        pass
    return {}

def _guardar_cache(files):
    try:
        escribir(CACHE_PATH, json.dumps({"version": CACHE_VER, "files": files}, ensure_ascii=False))
    except Exception as e:
        print("  [!] No se pudo guardar el cache incremental:", e)

def _extraer_archivo(path):
    """Lee UN transcript y devuelve sus contribuciones crudas, SIN dedup/agregacion
    global y SIN coste (solo tokens). Es lo que se cachea por fichero. Devuelve None
    si el fichero no se puede leer."""
    events, tools, limites, menciones = [], [], [], 0
    projdir, sesion_padre, _es_sub = proyecto_de_ruta(path)
    try:
        fh = leer_claude(path)
    except Exception:
        return None
    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            tipo = r.get("type")
            uuid = r.get("uuid")
            msg = r.get("message") if isinstance(r.get("message"), dict) else None

            # ---- tool_use: herramientas, ficheros, comandos, skills ----
            if msg and isinstance(msg.get("content"), list):
                for b in msg["content"]:
                    if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                        continue
                    nm = b.get("name", "")
                    if not nm:
                        continue
                    inp = b.get("input", {}) or {}
                    t = {"n": nm}
                    if isinstance(inp, dict):
                        fp = inp.get("file_path")
                        if fp and nm in ("Read", "Edit", "Write", "NotebookEdit"):
                            t["fp"] = os.path.basename(str(fp)) or str(fp)
                            t["op"] = "read" if nm == "Read" else ("write" if nm == "Write" else "edit")
                        elif nm == "Bash":
                            cmd = str(inp.get("command", "")).strip()
                            if cmd:
                                t["bash"] = cmd.split()[0]
                    if nm in ("Skill", "SlashCommand"):
                        t["skill"] = "%s" % (inp.get("skill") or inp.get("command")
                                             or inp.get("name") or "?")
                    tools.append(t)

            # ---- eventos de error / limite (alta confianza) ----
            if r.get("isApiErrorMessage"):
                txt = texto_de_contenido(msg.get("content")) if msg else json.dumps(r)
                low = txt.lower()
                if re.search(r"session limit|usage limit|limit reached|reached your|resets?\b|rate.?limit|too many|\b429\b", low):
                    cat = "límite de uso"
                elif "too long" in low:
                    cat = "prompt demasiado largo"
                elif "selected model" in low or "may not exist" in low or "access to it" in low:
                    cat = "acceso a modelo"
                elif re.search(r"overload|internal server|server error|\b5[0-9][0-9]\b", low):
                    cat = "error de servidor"
                else:
                    cat = "otro"
                dt = parse_ts(r.get("timestamp"))
                limites.append({
                    "key": str(uuid or txt[:40]),
                    "ts": dt.isoformat() if dt else None,
                    "dia": dt.strftime("%Y-%m-%d") if dt else None,
                    "categoria": cat,
                    "proyecto": nombre_amistoso(projdir),
                    "sesion": sesion_padre,
                    "texto": txt[:160],
                })

            # ---- menciones de limite (orientativo, solo system/assistant) ----
            if tipo in ("system", "assistant") and not r.get("isApiErrorMessage") and msg:
                tt = texto_de_contenido(msg.get("content"))
                if tt and LIMIT_RE.search(tt):
                    menciones += 1

            # ---- evento facturable (solo assistant con usage real) ----
            if tipo != "assistant" or not msg:
                continue
            usage = msg.get("usage")
            if not isinstance(usage, dict):
                continue
            modelo_raw = msg.get("model")
            modelo = normaliza_modelo(modelo_raw)
            if modelo == "synthetic" or modelo is None:
                continue
            dt = parse_ts(r.get("timestamp"))
            cc = usage.get("cache_creation", {}) or {}
            st = usage.get("server_tool_use", {}) or {}
            events.append({
                "mid": msg.get("id") or uuid,
                "modelo": modelo, "modelo_raw": modelo_raw,
                "ep": r.get("entrypoint"),          # cliente: claude-desktop / claude-vscode / ...
                "ts": dt.isoformat() if dt else None,
                "inp": usage.get("input_tokens", 0) or 0,
                "out": usage.get("output_tokens", 0) or 0,
                "cr":  usage.get("cache_read_input_tokens", 0) or 0,
                "c5":  cc.get("ephemeral_5m_input_tokens", 0) or 0,
                "c1":  cc.get("ephemeral_1h_input_tokens", 0) or 0,
                "cwt": usage.get("cache_creation_input_tokens", 0) or 0,
                "ws":  st.get("web_search_requests", 0) or 0,
                "wf":  st.get("web_fetch_requests", 0) or 0,
            })
    return {"events": events, "tools": tools, "limites": limites, "menciones": menciones}

def _agregar(recs):
    """Agrega las contribuciones por fichero -> estructura global (dedup, coste, by_*).
    El coste se calcula aqui a partir de los tokens (precios actuales de precios.json)."""
    vistos = set()                 # dedup por message.id / uuid / clave de limite
    eventos = []                   # cada llamada facturable
    por_sesion = defaultdict(lambda: {
        "coste": 0.0, "requests": 0, "input": 0, "output": 0,
        "cache_read": 0, "cache_write": 0, "modelos": Counter(),
        "ts_min": None, "ts_max": None, "proyecto": None, "subagente": False,
    })
    limites = []                   # eventos de error/limite alta confianza
    menciones_limite = 0
    skills = Counter()
    skills_por_sesion = defaultdict(set)
    herramientas = Counter()                       # uso global de cada tool
    herramientas_sesiones = defaultdict(set)       # tool -> sesiones distintas
    herramientas_por_sesion = defaultdict(Counter) # sesion -> {tool: veces} (para clasificar)
    ficheros_tocados = defaultdict(lambda: {"read": 0, "edit": 0, "write": 0, "sesiones": set()})
    reads_sesion = defaultdict(Counter)            # sesion -> {archivo: lecturas} (relecturas)
    bash_cmds = Counter()                          # primer token de cada comando Bash
    modelos_desconocidos = Counter()

    tot = defaultdict(float)
    by_model = defaultdict(lambda: defaultdict(float))
    by_day = defaultdict(lambda: {"coste": 0.0, "requests": 0, "modelos": defaultdict(float),
                                  "input": 0, "output": 0, "cache_read": 0, "cache_write": 0})
    by_project = defaultdict(lambda: {"coste": 0.0, "requests": 0, "sesiones": set(),
                                      "input": 0, "output": 0, "cache_read": 0, "cache_write": 0})
    by_client = defaultdict(lambda: {"coste": 0.0, "requests": 0, "sesiones": set()})
    by_month = defaultdict(float)
    by_week = defaultdict(lambda: {"coste": 0.0, "requests": 0, "modelos": defaultdict(float), "inicio": None})
    heat = [[0.0] * 24 for _ in range(7)]
    heat_req = [[0] * 24 for _ in range(7)]

    for path in sorted(recs.keys()):                # orden estable (dedup determinista)
        rec = recs[path]
        projdir, sesion_padre, es_sub = proyecto_de_ruta(path)

        menciones_limite += rec.get("menciones", 0)

        # ---- herramientas / ficheros / comandos / skills ----
        for t in rec.get("tools", []):
            nm = t["n"]
            herramientas[nm] += 1
            if sesion_padre:
                herramientas_sesiones[nm].add(sesion_padre)
                herramientas_por_sesion[sesion_padre][nm] += 1
            if "fp" in t:
                a = ficheros_tocados[t["fp"]]
                a[t["op"]] += 1
                if sesion_padre:
                    a["sesiones"].add(sesion_padre)
                    if t["op"] == "read":
                        reads_sesion[sesion_padre][t["fp"]] += 1
            if "bash" in t:
                bash_cmds[t["bash"]] += 1
            if "skill" in t:
                skills[t["skill"]] += 1
                if sesion_padre:
                    skills_por_sesion[t["skill"]].add(sesion_padre)

        # ---- limites (dedup global por clave) ----
        for L in rec.get("limites", []):
            k = "LIM:" + str(L.get("key"))
            if k in vistos:
                continue
            vistos.add(k)
            limites.append({"ts": L.get("ts"), "dia": L.get("dia"), "categoria": L.get("categoria"),
                            "proyecto": L.get("proyecto"), "sesion": L.get("sesion"), "texto": L.get("texto")})

        # ---- eventos facturables (dedup global por message.id) ----
        for ev in rec.get("events", []):
            mid = ev["mid"]
            if mid in vistos:
                continue
            vistos.add(mid)
            modelo = ev["modelo"]
            inp, out, cr = ev["inp"], ev["out"], ev["cr"]
            c5, c1, cwt = ev["c5"], ev["c1"], ev["cwt"]
            cw = cwt or (c5 + c1)
            ws, wf = ev["ws"], ev["wf"]
            usage_like = {
                "input_tokens": inp, "output_tokens": out, "cache_read_input_tokens": cr,
                "cache_creation": {"ephemeral_5m_input_tokens": c5, "ephemeral_1h_input_tokens": c1},
                "cache_creation_input_tokens": cwt,
                "server_tool_use": {"web_search_requests": ws},
            }
            total, comp, conocido = coste_evento(usage_like, modelo)
            if not conocido:
                modelos_desconocidos[ev["modelo_raw"]] += 1
            dt = datetime.fromisoformat(ev["ts"]) if ev["ts"] else None

            # acumular totales
            tot["coste"] += total
            tot["input"] += inp
            tot["output"] += out
            tot["cache_read"] += cr
            tot["cache_write"] += cw
            tot["cache_w5"] += c5
            tot["cache_w1"] += c1
            tot["web_search"] += ws
            tot["web_fetch"] += wf
            tot["requests"] += 1
            tot["coste_cache_read"] += comp["cache_read"]
            tot["coste_cache_write"] += comp["cache_w5"] + comp["cache_w1"]
            tot["coste_input"] += comp["input"]
            tot["coste_output"] += comp["output"]
            tot["coste_web"] += comp["web_search"]

            bm = by_model[modelo]
            bm["coste"] += total; bm["requests"] += 1
            bm["input"] += inp; bm["output"] += out
            bm["cache_read"] += cr; bm["cache_write"] += cw

            if dt:
                dkey = dt.strftime("%Y-%m-%d")
                d = by_day[dkey]
                d["coste"] += total; d["requests"] += 1
                d["modelos"][modelo] += total
                d["input"] += inp; d["output"] += out
                d["cache_read"] += cr; d["cache_write"] += cw
                by_month[dt.strftime("%Y-%m")] += total
                wk = dt.strftime("%G-W%V")
                mon = (dt - timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
                w = by_week[wk]
                w["coste"] += total; w["requests"] += 1; w["modelos"][modelo] += total
                if not w["inicio"] or mon < w["inicio"]:
                    w["inicio"] = mon
                heat[dt.weekday()][dt.hour] += total
                heat_req[dt.weekday()][dt.hour] += 1

            pr = by_project[projdir]
            pr["coste"] += total; pr["requests"] += 1
            pr["input"] += inp; pr["output"] += out
            pr["cache_read"] += cr; pr["cache_write"] += cw
            if sesion_padre:
                pr["sesiones"].add(sesion_padre)

            bc = by_client[ev.get("ep") or "desconocido"]
            bc["coste"] += total; bc["requests"] += 1
            if sesion_padre:
                bc["sesiones"].add(sesion_padre)

            skey = sesion_padre or mid
            s = por_sesion[skey]
            s["coste"] += total; s["requests"] += 1
            s["input"] += inp; s["output"] += out
            s["cache_read"] += cr; s["cache_write"] += cw
            s["modelos"][modelo] += total
            s["proyecto"] = nombre_amistoso(projdir)
            if es_sub:
                s["subagente"] = True
            ts_iso = ev["ts"]
            if ts_iso:
                if not s["ts_min"] or ts_iso < s["ts_min"]:
                    s["ts_min"] = ts_iso
                if not s["ts_max"] or ts_iso > s["ts_max"]:
                    s["ts_max"] = ts_iso

            eventos.append({"dia": dt.strftime("%Y-%m-%d") if dt else None,
                            "modelo": modelo, "coste": total})

    return {
        "eventos": eventos, "por_sesion": por_sesion,
        "tot": tot, "by_model": by_model, "by_day": by_day, "by_project": by_project,
        "by_client": by_client,
        "by_month": by_month, "by_week": by_week, "heat": heat, "heat_req": heat_req,
        "limites": limites, "menciones_limite": menciones_limite,
        "skills": skills, "skills_por_sesion": skills_por_sesion,
        "herramientas": herramientas, "herramientas_sesiones": herramientas_sesiones,
        "herramientas_por_sesion": herramientas_por_sesion,
        "ficheros_tocados": ficheros_tocados, "reads_sesion": reads_sesion, "bash_cmds": bash_cmds,
        "modelos_desconocidos": modelos_desconocidos,
    }

def analizar_transcripts():
    """Glob de transcripts + lectura INCREMENTAL (cache por fichero) + agregacion."""
    archivos = glob.glob(os.path.join(PROJECTS, "**", "*.jsonl"), recursive=True)
    cache = _cargar_cache()
    nuevos_files = {}              # cache reconstruido solo con ficheros vivos
    archivos_stat = {}
    recs = {}
    cache_hits = 0
    for path in archivos:
        try:
            stt = os.stat(path)
            size, mtime = stt.st_size, stt.st_mtime
        except Exception:
            continue
        archivos_stat[path] = {"size": size, "mtime": mtime}
        ent = cache.get(path)
        if ent and ent.get("size") == size and ent.get("mtime") == mtime and "rec" in ent:
            rec = ent["rec"]
            cache_hits += 1
        else:
            rec = _extraer_archivo(path)
        if rec is None:
            continue
        recs[path] = rec
        nuevos_files[path] = {"size": size, "mtime": mtime, "rec": rec}
    _guardar_cache(nuevos_files)   # los ficheros borrados se purgan al no re-anadirse

    A = _agregar(recs)
    A["archivos"] = archivos
    A["archivos_stat"] = archivos_stat
    A["incremental_cacheados"] = cache_hits
    A["incremental_releidos"] = len(recs) - cache_hits
    return A

# --------------------------------------------------------------------------------------
# Carga de metadatos cualitativos (facets / session-meta / tasks / memoria)
# --------------------------------------------------------------------------------------
def cargar_json_seguro(path):
    try:
        with leer_claude(path) as fh:
            return json.load(fh)
    except Exception:
        return None

def cargar_facets():
    d = {}
    for f in glob.glob(os.path.join(USAGE_DIR, "facets", "*.json")):
        j = cargar_json_seguro(f)
        if j and j.get("session_id"):
            d[j["session_id"]] = j
    return d

def cargar_meta():
    d = {}
    for f in glob.glob(os.path.join(USAGE_DIR, "session-meta", "*.json")):
        j = cargar_json_seguro(f)
        if j and j.get("session_id"):
            d[j["session_id"]] = j
    return d

def contar_tasks():
    res = {}
    if not os.path.isdir(TASKS_DIR):
        return res
    for sd in os.listdir(TASKS_DIR):
        base = os.path.join(TASKS_DIR, sd)
        if not os.path.isdir(base):
            continue
        c = Counter()
        for jf in glob.glob(os.path.join(base, "*.json")):
            j = cargar_json_seguro(jf)
            if j and isinstance(j, dict) and j.get("status"):
                c[j["status"]] += 1
        if c:
            res[sd] = dict(c)
    return res

def estado_memoria_claude():
    """Cuenta entradas de la memoria de Claude Code (solo lectura, informativo)."""
    candidatos = glob.glob(os.path.join(PROJECTS, "*", "memory"))
    total, dirs = 0, 0
    for d in candidatos:
        if os.path.isdir(d):
            dirs += 1
            total += len([x for x in glob.glob(os.path.join(d, "*")) if os.path.isfile(x)])
    return {"directorios": dirs, "entradas": total}

# --------------------------------------------------------------------------------------
# Auto-mejora: estado persistente entre ejecuciones (en panel_costes/estado/)
# --------------------------------------------------------------------------------------
def cargar_estado_previo():
    p = os.path.join(STATE_DIR, "resumen.json")
    if os.path.isfile(p):
        try:
            with open(p, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return None
    return None

def cargar_historial():
    p = os.path.join(STATE_DIR, "historial.jsonl")
    hist = []
    if os.path.isfile(p):
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        hist.append(json.loads(line))
                    except Exception:
                        pass
    return hist

# --------------------------------------------------------------------------------------
# Construccion del dataset final
# --------------------------------------------------------------------------------------
def construir(A, facets, meta, tasks, ahora):
    tot = A["tot"]
    # by_model -> lista ordenada
    by_model = []
    coste_total = tot["coste"] or 1e-9
    for m, v in sorted(A["by_model"].items(), key=lambda kv: -kv[1]["coste"]):
        info = MODELOS.get(m, {"etiqueta": m, "color": "#ef4444"})
        by_model.append({
            "modelo": m, "etiqueta": info.get("etiqueta", m), "color": info.get("color", "#ef4444"),
            "coste": round(v["coste"], 4), "requests": v["requests"],
            "input": v["input"], "output": v["output"],
            "cache_read": v["cache_read"], "cache_write": v["cache_write"],
            "share": round(100 * v["coste"] / coste_total, 1),
        })
    modelos_orden = [m["modelo"] for m in by_model]

    # by_day ordenado
    by_day = []
    for dkey in sorted(A["by_day"].keys()):
        d = A["by_day"][dkey]
        by_day.append({
            "dia": dkey, "coste": round(d["coste"], 4), "requests": d["requests"],
            "modelos": {m: round(d["modelos"].get(m, 0.0), 4) for m in modelos_orden},
            "input": d["input"], "output": d["output"],
            "cache_read": d["cache_read"], "cache_write": d["cache_write"],
        })

    # coste por hora del dia (suma de todos los dias) y por semana
    by_hour = []
    for h in range(24):
        c = sum(A["heat"][d][h] for d in range(7))
        rq = sum(A["heat_req"][d][h] for d in range(7))
        by_hour.append({"hora": h, "coste": round(c, 4), "requests": rq})
    by_week = []
    for wk in sorted(A["by_week"].keys()):
        w = A["by_week"][wk]
        by_week.append({"semana": wk, "inicio": w["inicio"],
                        "coste": round(w["coste"], 4), "requests": w["requests"],
                        "modelos": {m: round(w["modelos"].get(m, 0.0), 4) for m in modelos_orden}})

    # by_project
    by_project = []
    for projdir, v in sorted(A["by_project"].items(), key=lambda kv: -kv[1]["coste"]):
        by_project.append({
            "proyecto": nombre_amistoso(projdir),
            "coste": round(v["coste"], 4), "requests": v["requests"],
            "sesiones": len(v["sesiones"]),
            "tokens": v["input"] + v["output"] + v["cache_read"] + v["cache_write"],
        })

    # by_cliente (entrypoint: desde dónde se usó Claude Code). Editable.
    CLIENTES = {"claude-desktop": "Escritorio / terminal", "claude-vscode": "VS Code",
                "claude-code": "CLI", "cli": "CLI", "sdk": "SDK", "desconocido": "Desconocido"}
    by_cliente = []
    for ep, v in sorted(A.get("by_client", {}).items(), key=lambda kv: -kv[1]["coste"]):
        by_cliente.append({
            "cliente": ep, "etiqueta": CLIENTES.get(ep, ep),
            "coste": round(v["coste"], 4), "requests": v["requests"],
            "sesiones": len(v["sesiones"]),
            "share": round(100 * v["coste"] / coste_total, 1),
        })

    # sesiones (join con meta + facets)
    sesiones = []
    for sid, s in A["por_sesion"].items():
        m = meta.get(sid, {})
        f = facets.get(sid, {})
        dur = m.get("duration_minutes")
        if dur is None and s["ts_min"] and s["ts_max"]:
            try:
                dur = round((datetime.fromisoformat(s["ts_max"]) -
                             datetime.fromisoformat(s["ts_min"])).total_seconds() / 60.0, 1)
            except Exception:
                dur = None
        modelo_top = s["modelos"].most_common(1)[0][0] if s["modelos"] else None
        # clasificacion de actividad: herramientas en vivo (universal) o, si no, las del meta
        tools_sesion = dict(A["herramientas_por_sesion"].get(sid, {})) or (m.get("tool_counts") or {})
        categoria = clasificar_actividad(
            tools_sesion, (f.get("underlying_goal") or "") + " " + (m.get("first_prompt") or ""))
        sesiones.append({
            "id": sid, "proyecto": s["proyecto"], "subagente": s["subagente"],
            "categoria": categoria,
            "inicio": s["ts_min"], "fin": s["ts_max"], "duracion_min": dur,
            "coste": round(s["coste"], 4), "requests": s["requests"],
            "input": s["input"], "output": s["output"],
            "cache_read": s["cache_read"], "cache_write": s["cache_write"],
            "modelo_top": modelo_top,
            "modelos": {k: round(v, 4) for k, v in s["modelos"].items()},
            "msgs_user": m.get("user_message_count"),
            "msgs_assist": m.get("assistant_message_count"),
            "tools": m.get("tool_counts") or {},
            "languages": m.get("languages") or {},
            "git_commits": m.get("git_commits"), "git_pushes": m.get("git_pushes"),
            "files_mod": m.get("files_modified"),
            "lineas_mas": m.get("lines_added"), "lineas_menos": m.get("lines_removed"),
            "tool_errors": m.get("tool_errors"),
            "primer_prompt": (m.get("first_prompt") or f.get("brief_summary") or "")[:140],
            "objetivo": f.get("underlying_goal"),
            "resultado": f.get("outcome"),
            "satisfaccion": (list(f.get("user_satisfaction_counts", {}).keys()) or [None])[0],
            "ayuda": f.get("claude_helpfulness"),
            "friccion": f.get("friction_detail"),
            "tipo_sesion": f.get("session_type"),
        })
    sesiones.sort(key=lambda x: (x["inicio"] or ""), reverse=True)

    # ---- actividad por tipo (clasificacion automatica determinista) ----
    cat_map = {}
    for s in sesiones:
        g = cat_map.setdefault(s["categoria"], {"coste": 0.0, "sesiones": 0, "requests": 0, "tokens": 0})
        g["coste"] += s["coste"]; g["sesiones"] += 1; g["requests"] += s["requests"]
        g["tokens"] += s["input"] + s["output"] + s["cache_read"] + s["cache_write"]
    by_categoria = [{"categoria": k, "coste": round(v["coste"], 4), "sesiones": v["sesiones"],
                     "requests": v["requests"], "tokens": int(v["tokens"])}
                    for k, v in sorted(cat_map.items(), key=lambda kv: -kv[1]["coste"])]

    # ---- herramientas mas usadas (global) ----
    herramientas = [{"nombre": k, "veces": v, "sesiones": len(A["herramientas_sesiones"].get(k, ()))}
                    for k, v in A["herramientas"].most_common(25)]

    # ---- ficheros mas tocados + patrones de repeticion ----
    max_reads = defaultdict(int)        # max relecturas del mismo archivo en UNA sesion
    for _sid, cnt in A["reads_sesion"].items():
        for base, c in cnt.items():
            if c > max_reads[base]:
                max_reads[base] = c
    archivos_top = []
    for base, a in A["ficheros_tocados"].items():
        total = a["read"] + a["edit"] + a["write"]
        archivos_top.append({"archivo": base, "read": a["read"], "edit": a["edit"], "write": a["write"],
                             "total": total, "sesiones": len(a["sesiones"]),
                             "max_relec": max_reads.get(base, 0)})
    archivos_top.sort(key=lambda x: -x["total"])
    relecturas = sorted([x for x in archivos_top if x["max_relec"] >= 4],
                        key=lambda x: -x["max_relec"])[:10]
    archivos_top = archivos_top[:20]
    bash_top = [{"cmd": c, "veces": n} for c, n in A["bash_cmds"].most_common(12)]

    # ---- resumen de resultados (desde facets; solo si hay datos) ----
    outcomes = Counter()
    for s in sesiones:
        o = (s.get("resultado") or "").lower()
        if not o:
            outcomes["desconocido"] += 1
        elif re.search(r"achiev|success|complet|resolv|logr", o):
            outcomes["logrado"] += 1
        elif re.search(r"partial|parcial", o):
            outcomes["parcial"] += 1
        elif re.search(r"fail|abandon|not_|fall", o):
            outcomes["fallido"] += 1
        else:
            outcomes["otro"] += 1
    outcomes_con_dato = sum(v for k, v in outcomes.items() if k != "desconocido")

    # ---- rightsizing: ¿que sesiones podrian haber usado un modelo mas barato? ----
    PREMIUM = {"opus-4-8", "opus-4-7", "opus-4-6", "fable-5"}

    def coste_en(modelo, inp, out, cr, cw):
        p = MODELOS.get(modelo)
        if not p:
            return None
        ri = p["input"] / 1e6; ro = p["output"] / 1e6
        return inp * ri + out * ro + cr * ri * 0.10 + cw * ri * 1.25

    candidatas = []
    ahorro_haiku = ahorro_sonnet = 0.0
    premium_total = 0.0
    for s in sesiones:
        prem = sum(v for m, v in s["modelos"].items() if m in PREMIUM)
        premium_total += prem
        if s["coste"] < 0.5:                      # ignora sesiones triviales
            continue
        share = prem / s["coste"] if s["coste"] else 0
        req = s["requests"] or 0
        ligera = s["output"] < 30000 and req <= 25
        muy_ligera = s["output"] < 8000 and req <= 8
        if share < 0.8 or not ligera:
            continue
        sugerido = "haiku-4-5" if muy_ligera else "sonnet-4-6"
        cf = coste_en(sugerido, s["input"], s["output"], s["cache_read"], s["cache_write"])
        if cf is None:
            continue
        ahorro = round(s["coste"] - cf, 4)
        if ahorro <= 0.05:
            continue
        candidatas.append({
            "id": s["id"], "proyecto": s["proyecto"], "inicio": s["inicio"],
            "modelo_actual": s["modelo_top"], "coste": s["coste"],
            "sugerido": sugerido, "coste_sugerido": round(cf, 4), "ahorro": ahorro,
            "tarea": (s.get("objetivo") or s.get("primer_prompt") or "")[:140],
            "tipo": s.get("tipo_sesion"),
        })
        if sugerido == "haiku-4-5":
            ahorro_haiku += ahorro
        else:
            ahorro_sonnet += ahorro
    candidatas.sort(key=lambda c: -c["ahorro"])
    ahorro_total = ahorro_haiku + ahorro_sonnet
    light_premium = sum(c["coste"] for c in candidatas)
    heavy_share = 100 * (1 - light_premium / premium_total) if premium_total else 100

    rs_recs = []
    if premium_total > 0:
        rs_recs.append("El **%.0f%%** de tu gasto en Opus/Fable está en sesiones pesadas (largas o "
                       "complejas), donde el modelo premium se justifica; solo ~%.0f%% está en tareas "
                       "ligeras movibles." % (heavy_share, 100 - heavy_share))
    if candidatas:
        n = len(candidatas)
        coste_cand = sum(c["coste"] for c in candidatas)
        rs_recs.append("Detecté %d sesiones ligeras (poca salida y pocas iteraciones) que corrieron en "
                       "modelos premium y costaron $%.2f. En el modelo más barato adecuado habrían costado "
                       "~$%.2f → ahorro potencial **$%.2f**." % (n, coste_cand, coste_cand - ahorro_total, ahorro_total))
        if ahorro_haiku > 0:
            nh = sum(1 for c in candidatas if c["sugerido"] == "haiku-4-5")
            rs_recs.append("Usa más **Haiku 4.5** para tareas muy ligeras (lecturas, ediciones puntuales, "
                           "clasificación, formato, extracción): %d de esas sesiones encajan y ahorrarían ≈$%.2f."
                           % (nh, ahorro_haiku))
        if ahorro_sonnet > 0:
            ns = sum(1 for c in candidatas if c["sugerido"] == "sonnet-4-6")
            rs_recs.append("Pasa a **Sonnet 4.6** las de complejidad media (refactors, resúmenes, volumen): "
                           "%d sesiones, ≈$%.2f de ahorro." % (ns, ahorro_sonnet))
        # pista por proyecto (donde se concentran las candidatas)
        por_proj = Counter()
        for c in candidatas:
            por_proj[c["proyecto"]] += c["ahorro"]
        top_p, top_a = por_proj.most_common(1)[0]
        rs_recs.append("Donde más margen hay es en **%s** (≈$%.2f de ahorro potencial en tareas ligeras)."
                       % (top_p, top_a))
    else:
        rs_recs.append("No hay candidatas claras: tu mezcla de modelos ya está bien ajustada al tipo de tarea.")

    rightsizing = {
        "candidatas": candidatas[:50], "n": len(candidatas),
        "ahorro_total": round(ahorro_total, 2),
        "ahorro_haiku": round(ahorro_haiku, 2), "ahorro_sonnet": round(ahorro_sonnet, 2),
        "recs": rs_recs,
        "criterios": ("sesión con ≥80% del gasto en Opus/Fable y ligera (salida <30k tokens y ≤25 iteraciones); "
                      "muy ligera (<8k y ≤8) → Haiku, resto → Sonnet. Coste estimado = mismos tokens a la tarifa "
                      "del modelo sugerido (lectura de caché 0,1×, escritura 1,25×)."),
    }

    # ---- ajuste por TIPO DE ACTIVIDAD (usa la clasificación, no la longitud) ----
    # Complementa al rightsizing: en vez de "¿la sesión fue corta?", pregunta "¿este
    # TIPO de tarea necesita un modelo premium?". Captura gasto que el proxy de
    # longitud no ve (p. ej. documentar/refactorizar mucho en Opus).
    act_map = {}     # categoria -> agregados de sesiones premium degradables
    for s in sesiones:
        techo = TECHO_ACTIVIDAD.get(s["categoria"])
        if not techo:
            continue                                   # categoría donde premium se justifica
        if RANGO_MODELO.get(s["modelo_top"], 3) <= RANGO_MODELO.get(techo, 2):
            continue                                   # ya usa un modelo <= al techo: nada que bajar
        prem = sum(v for m, v in s["modelos"].items() if m in PREMIUM)
        if prem <= 0.02:
            continue
        cf = coste_en(techo, s["input"], s["output"], s["cache_read"], s["cache_write"])
        if cf is None:
            continue
        g = act_map.setdefault(s["categoria"], {"techo": techo, "sesiones": 0,
                                                 "coste_actual": 0.0, "coste_estimado": 0.0})
        g["sesiones"] += 1
        g["coste_actual"] += s["coste"]
        g["coste_estimado"] += cf
    ajuste_cats = []
    for cat, g in act_map.items():
        ahorro = round(g["coste_actual"] - g["coste_estimado"], 2)
        if ahorro <= 0.10:
            continue
        ajuste_cats.append({
            "categoria": cat, "sesiones": g["sesiones"], "modelo_sugerido": g["techo"],
            "etiqueta_sugerido": MODELOS.get(g["techo"], {}).get("etiqueta", g["techo"]),
            "coste_actual": round(g["coste_actual"], 2),
            "coste_estimado": round(g["coste_estimado"], 2), "ahorro": ahorro,
        })
    ajuste_cats.sort(key=lambda x: -x["ahorro"])
    ajuste_total = round(sum(c["ahorro"] for c in ajuste_cats), 2)

    aj_recs = []
    if ajuste_cats:
        top = ajuste_cats[0]
        ses_txt = "%d sesión%s" % (top["sesiones"], "" if top["sesiones"] == 1 else "es")
        aj_recs.append("Tu mayor margen por **tipo de tarea**: %s de **%s** corrió en modelos premium "
                       "($%.2f). %s suele bastar para esa clase de trabajo → ahorro estimado **$%.2f**." %
                       (ses_txt, top["categoria"], top["coste_actual"],
                        top["etiqueta_sugerido"], top["ahorro"]))
        if len(ajuste_cats) > 1:
            resto = ", ".join("%s ($%.2f)" % (c["categoria"], c["ahorro"]) for c in ajuste_cats[1:4])
            aj_recs.append("Otras actividades con margen: %s." % resto)
        aj_recs.append("Total reasignable por actividad: **$%.2f** (%.0f%% del gasto). A diferencia del rightsizing "
                       "por longitud, esto SÍ incluye sesiones largas pero mecánicas (documentar, refactorizar)." %
                       (ajuste_total, 100 * ajuste_total / max(1e-9, tot["coste"])))
    else:
        aj_recs.append("No hay categorías mal asignadas: el gasto premium está en tareas que lo justifican "
                       "(programación compleja, depuración, orquestación).")

    ajuste_actividad = {
        "categorias": ajuste_cats, "ahorro_total": ajuste_total, "recs": aj_recs,
        "mapeo": TECHO_ACTIVIDAD,
        "criterios": ("para cada sesión cuya CATEGORÍA suele no necesitar premium (Exploración/Investigación/"
                      "Scripting→Haiku; Documentación/Refactorización/Pruebas/DevOps→Sonnet) y que corrió en un "
                      "modelo más caro que ese techo, se estima su coste a la tarifa del techo. Programación, "
                      "Depuración y Orquestación nunca se sugieren bajar."),
    }

    # heatmap
    heat = [[round(c, 4) for c in fila] for fila in A["heat"]]

    # subscripcion: por mes
    meses = sorted(A["by_month"].keys())
    by_month = []
    for mk in meses:
        api = A["by_month"][mk]
        by_month.append({
            "mes": mk, "api": round(api, 4),
            "planes": {k: v for k, v in SUBS.items()},
        })
    n_meses = len(meses)
    api_total = tot["coste"]
    planes_totales = {k: v * n_meses for k, v in SUBS.items()}
    # mejor opcion global
    opciones = {"API (pago por uso)": api_total}
    opciones.update(planes_totales)
    mejor = min(opciones.items(), key=lambda kv: kv[1])
    # ahorro frente a cada plan (positivo = la API sale mas barata que el plan)
    ahorro_vs = {k: round(v - api_total, 2) for k, v in planes_totales.items()}

    # cache: cache_read ya facturado a 0.1x; el ahorro = 0.9x de su coste-pleno
    coste_cache_read_pleno = tot["coste_cache_read"] / 0.10 if tot["coste_cache_read"] else 0.0
    ahorro_cache = round(coste_cache_read_pleno - tot["coste_cache_read"], 2)

    # presupuesto mensual + proyeccion de fin de mes (mes natural en curso)
    mes_actual = ahora.strftime("%Y-%m")
    gasto_mes = A["by_month"].get(mes_actual, 0.0)
    dia_mes = ahora.day
    dias_mes = calendar.monthrange(ahora.year, ahora.month)[1]
    media_diaria = gasto_mes / dia_mes if dia_mes else 0.0
    proyeccion = media_diaria * dias_mes
    presup = float(CFG.get("presupuesto_usd_mes", 0) or 0)
    presupuesto = {
        "mes": mes_actual, "gasto_mes": round(gasto_mes, 4),
        "dia_mes": dia_mes, "dias_mes": dias_mes,
        "media_diaria": round(media_diaria, 4), "proyeccion": round(proyeccion, 4),
        "presupuesto": round(presup, 2),
        "pct_usado": round(100 * gasto_mes / presup, 1) if presup > 0 else None,
        "pct_proyectado": round(100 * proyeccion / presup, 1) if presup > 0 else None,
        "restante": round(presup - gasto_mes, 2) if presup > 0 else None,
    }

    skills = [{"nombre": k, "veces": v, "sesiones": len(A["skills_por_sesion"].get(k, []))}
              for k, v in A["skills"].most_common()]

    # limites por dia
    lim_por_dia = Counter()
    cats = Counter()
    for L in A["limites"]:
        if L["dia"]:
            lim_por_dia[L["dia"]] += 1
        cats[L["categoria"]] += 1

    datos = {
        "generado": ahora.strftime("%Y-%m-%d %H:%M:%S %Z") or ahora.strftime("%Y-%m-%d %H:%M:%S"),
        "tz": str(ahora.tzinfo),
        "claude_dir": CLAUDE_DIR,
        "solo_lectura": True,
        "precios_meta": CFG.get("_meta", {}),
        "totales": {
            "coste": round(tot["coste"], 4),
            "coste_input": round(tot["coste_input"], 4),
            "coste_output": round(tot["coste_output"], 4),
            "coste_cache_read": round(tot["coste_cache_read"], 4),
            "coste_cache_write": round(tot["coste_cache_write"], 4),
            "coste_web": round(tot["coste_web"], 4),
            "input": int(tot["input"]), "output": int(tot["output"]),
            "cache_read": int(tot["cache_read"]), "cache_write": int(tot["cache_write"]),
            "cache_w5": int(tot["cache_w5"]), "cache_w1": int(tot["cache_w1"]),
            "tokens_total": int(tot["input"] + tot["output"] + tot["cache_read"] + tot["cache_write"]),
            "web_search": int(tot["web_search"]), "web_fetch": int(tot["web_fetch"]),
            "requests": int(tot["requests"]),
            "sesiones": len(A["por_sesion"]),
            "proyectos": len(A["by_project"]),
            "dias": len(A["by_day"]),
            "transcripts": len(A["archivos"]),
        },
        "by_model": by_model,
        "by_day": by_day,
        "by_hour": by_hour,
        "by_week": by_week,
        "by_project": by_project,
        "by_cliente": by_cliente,
        "sesiones": sesiones,
        "heat": heat,
        "subscripcion": {
            "meses": meses, "n_meses": n_meses, "by_month": by_month,
            "api_total": round(api_total, 2),
            "planes_mes": SUBS, "planes_totales": {k: round(v, 2) for k, v in planes_totales.items()},
            "mejor_opcion": {"nombre": mejor[0], "coste": round(mejor[1], 2)},
            "ahorro_vs": ahorro_vs,
            # ROI: cuántas veces más valor API se generó vs lo que cuesta la suscripción
            "roi_multiplicador": round(api_total / mejor[1], 1) if (not mejor[0].startswith("API") and mejor[1] > 0) else None,
            "roi_pct": round(100 * (api_total - mejor[1]) / mejor[1], 0) if (not mejor[0].startswith("API") and mejor[1] > 0) else None,
        },
        "eficiencia": {
            "coste_por_sesion": round(api_total / len(A["por_sesion"]), 4) if A["por_sesion"] else 0,
            "coste_por_dia_activo": round(api_total / len([d for d in by_day if d["coste"] > 0]), 2)
                                    if any(d["coste"] > 0 for d in by_day) else 0,
            "dias_activos": len([d for d in by_day if d["coste"] > 0]),
            "output_por_dolar": int(tot["output"] / api_total) if api_total else 0,
            "tokens_por_dolar": int((tot["input"] + tot["output"]) / api_total) if api_total else 0,
            "ahorro_cache_pct": round(100 * ahorro_cache / (api_total + ahorro_cache), 1)
                                if (api_total + ahorro_cache) > 0 else 0,
        },
        "presupuesto": presupuesto,
        "cache": {
            "read_tokens": int(tot["cache_read"]), "write_tokens": int(tot["cache_write"]),
            "coste_lectura": round(tot["coste_cache_read"], 4),
            "coste_escritura": round(tot["coste_cache_write"], 4),
            "ahorro_estimado": ahorro_cache,
            "ratio_lectura": round(100 * tot["cache_read"] /
                                   max(1, (tot["input"] + tot["cache_read"] + tot["cache_write"])), 1),
        },
        "limites": {
            "alta_confianza": len(A["limites"]),
            "limite_uso": cats.get("límite de uso", 0),
            "categorias": dict(cats),
            "por_dia": dict(lim_por_dia),
            "eventos": A["limites"][:200],
            "menciones_contenido": A["menciones_limite"],
        },
        "skills": skills,
        "tasks": tasks,
        "rightsizing": rightsizing,
        "ajuste_actividad": ajuste_actividad,
        "by_categoria": by_categoria,
        "herramientas": herramientas,
        "archivos": archivos_top,
        "relecturas": relecturas,
        "bash_top": bash_top,
        "outcomes": {"conteo": dict(outcomes), "con_dato": outcomes_con_dato, "total": len(sesiones)},
    }
    return datos

# --------------------------------------------------------------------------------------
# Auto-mejora: deltas, memoria, recomendaciones
# --------------------------------------------------------------------------------------
def auto_mejora(datos, A, ahora):
    prev = cargar_estado_previo()
    hist = cargar_historial()
    run_n = (prev.get("run", 0) + 1) if prev else 1

    deltas = None
    if prev:
        deltas = {
            "coste": round(datos["totales"]["coste"] - prev.get("coste", 0), 4),
            "sesiones": datos["totales"]["sesiones"] - prev.get("sesiones", 0),
            "requests": datos["totales"]["requests"] - prev.get("requests", 0),
            "limites": datos["limites"]["alta_confianza"] - prev.get("limites", 0),
            "desde": prev.get("ts"),
        }

    # ficheros nuevos / cambiados desde la ejecucion anterior
    prev_files = (prev or {}).get("archivos_stat", {})
    nuevos, cambiados = 0, 0
    for p, st in A["archivos_stat"].items():
        if p not in prev_files:
            nuevos += 1
        elif prev_files[p].get("mtime") != st.get("mtime") or prev_files[p].get("size") != st.get("size"):
            cambiados += 1

    # recomendaciones derivadas de los datos
    recs = []
    T = datos["totales"]
    bm = {m["modelo"]: m for m in datos["by_model"]}
    share_opus = sum(m["share"] for m in datos["by_model"] if m["modelo"].startswith("opus"))
    share_fable = bm.get("fable-5", {}).get("share", 0)
    share_haiku = bm.get("haiku-4-5", {}).get("share", 0)
    if share_fable >= 20:
        recs.append("Fable 5 concentra el %.0f%% del gasto (tier mas caro, $10/$50). "
                    "Reserva Fable solo para tareas que de verdad necesiten el maximo nivel; "
                    "Opus 4.8 cuesta la mitad por token." % share_fable)
    if share_opus >= 50:
        recs.append("Opus acumula el %.0f%% del gasto. Para refactors mecanicos, busquedas o "
                    "resumenes, Sonnet 4.6 (3/15) o Haiku 4.5 (1/5) reducirian el coste bastante." % share_opus)
    if datos["cache"]["ratio_lectura"] >= 50:
        recs.append("El caching va muy bien: el %.0f%% de los tokens de entrada se sirven de cache "
                    "(ahorro estimado de $%.2f). Mantener prompts estables potencia esto." %
                    (datos["cache"]["ratio_lectura"], datos["cache"]["ahorro_estimado"]))
    elif T["cache_read"] > 0:
        recs.append("Ratio de lectura de cache del %.0f%%: hay margen. Evita timestamps/IDs "
                    "variables al inicio del prompt para no invalidar la cache." % datos["cache"]["ratio_lectura"])
    sub = datos["subscripcion"]
    if sub["n_meses"] > 0:
        if sub["mejor_opcion"]["nombre"].startswith("API"):
            recs.append("A tarifas de API pagarias $%.2f en total (%d mes/es). Es menos que cualquier "
                        "plan de suscripcion en ese periodo: el pago por uso te saldria a cuenta." %
                        (sub["api_total"], sub["n_meses"]))
        else:
            recs.append("La suscripcion '%s' ($%.0f total) sale mas barata que pagar la API ($%.2f). "
                        "Si ese es tu plan, lo estas amortizando con creces." %
                        (sub["mejor_opcion"]["nombre"], sub["mejor_opcion"]["coste"], sub["api_total"]))
    if datos["limites"]["alta_confianza"] > 0:
        recs.append("Se detectaron %d eventos de error/limite de API. Si topan a menudo, considera "
                    "espaciar las rafagas o subir de plan." % datos["limites"]["alta_confianza"])
    if A["modelos_desconocidos"]:
        recs.append("Modelos sin tarifa en precios.json: %s. Anadelos para afinar el coste (auto-mejora)." %
                    ", ".join(sorted(A["modelos_desconocidos"].keys())))
    rs = datos.get("rightsizing", {})
    if rs.get("ahorro_total", 0) > 0:
        recs.insert(0, "Rightsizing: %d sesiones ligeras en modelos premium podrían haber usado "
                    "Haiku/Sonnet → ahorro potencial estimado $%.2f (%.0f%% del gasto). Ver sección "
                    "'Recomendaciones de modelo'." % (rs["n"], rs["ahorro_total"],
                    100 * rs["ahorro_total"] / max(1e-9, datos["totales"]["coste"])))
    aj = datos.get("ajuste_actividad", {})
    if aj.get("ahorro_total", 0) > 0 and aj["ahorro_total"] >= rs.get("ahorro_total", 0):
        recs.insert(0, "Por TIPO de actividad hay ~$%.2f reasignables (frente a $%.2f del rightsizing por longitud): "
                    "%s. Son tareas mecánicas que corrieron en Opus. Ver 'Ajuste por tipo de actividad'." % (
                    aj["ahorro_total"], rs.get("ahorro_total", 0),
                    ", ".join("%s→%s" % (c["categoria"], c["etiqueta_sugerido"]) for c in aj["categorias"][:3])))
    if not recs:
        recs.append("Todo equilibrado: mezcla de modelos y caching razonables, sin limites detectados.")

    # memoria acumulada (se refina cada ejecucion)
    mem_path = os.path.join(STATE_DIR, "memoria.json")
    memoria = {}
    if os.path.isfile(mem_path):
        try:
            with open(mem_path, encoding="utf-8") as fh:
                memoria = json.load(fh)
        except Exception:
            memoria = {}
    top_proj = datos["by_project"][0]["proyecto"] if datos["by_project"] else None
    # hora pico
    heat = A["heat"]
    pico_val, pico_dh = -1, (None, None)
    for dow in range(7):
        for h in range(24):
            if heat[dow][h] > pico_val:
                pico_val, pico_dh = heat[dow][h], (dow, h)
    dias_sem = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]
    memoria["ultima_actualizacion"] = ahora.isoformat()
    memoria["proyecto_top"] = top_proj
    memoria["modelo_dominante"] = datos["by_model"][0]["etiqueta"] if datos["by_model"] else None
    memoria["hora_pico"] = ("%s %02d:00" % (dias_sem[pico_dh[0]], pico_dh[1])) if pico_dh[0] is not None else None
    memoria["ratio_cache"] = datos["cache"]["ratio_lectura"]
    memoria["coste_acumulado_max"] = max(memoria.get("coste_acumulado_max", 0), datos["totales"]["coste"])
    memoria["proyectos_vistos"] = sorted(set(memoria.get("proyectos_vistos", []) +
                                             [p["proyecto"] for p in datos["by_project"]]))
    memoria["modelos_vistos"] = sorted(set(memoria.get("modelos_vistos", []) +
                                           [m["modelo"] for m in datos["by_model"]]))
    memoria["ejecuciones"] = run_n

    info = {
        "run": run_n,
        "deltas": deltas,
        "incremental": {"transcripts_total": len(A["archivos"]), "nuevos": nuevos, "cambiados": cambiados},
        "recomendaciones": recs,
        "memoria": memoria,
        "modelos_desconocidos": dict(A["modelos_desconocidos"]),
        "historial": [{"ts": h.get("ts"), "coste": h.get("coste"), "sesiones": h.get("sesiones"),
                       "requests": h.get("requests"), "limites": h.get("limites")} for h in hist][-30:],
    }

    # persistir estado (SOLO en panel_costes/estado/)
    resumen = {
        "run": run_n, "ts": ahora.isoformat(),
        "coste": datos["totales"]["coste"], "sesiones": datos["totales"]["sesiones"],
        "requests": datos["totales"]["requests"], "limites": datos["limites"]["alta_confianza"],
        "archivos_stat": A["archivos_stat"],
    }
    escribir(os.path.join(STATE_DIR, "resumen.json"), json.dumps(resumen, ensure_ascii=False, indent=1))
    with open(os.path.join(STATE_DIR, "historial.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": ahora.isoformat(), "coste": datos["totales"]["coste"],
                             "sesiones": datos["totales"]["sesiones"],
                             "requests": datos["totales"]["requests"],
                             "limites": datos["limites"]["alta_confianza"]}, ensure_ascii=False) + "\n")
    escribir(mem_path, json.dumps(memoria, ensure_ascii=False, indent=1))

    # insights legible
    md = ["# Insights del panel de costes", "",
          "Ejecucion #%d — %s" % (run_n, ahora.strftime("%Y-%m-%d %H:%M")), ""]
    if deltas:
        md.append("## Cambios desde la ejecucion anterior")
        md.append("- Gasto: %+.4f USD" % deltas["coste"])
        md.append("- Sesiones: %+d   Requests: %+d   Limites: %+d" %
                  (deltas["sesiones"], deltas["requests"], deltas["limites"]))
        md.append("")
    md.append("## Recomendaciones")
    for r in recs:
        md.append("- " + r)
    escribir(os.path.join(STATE_DIR, "insights.md"), "\n".join(md) + "\n")

    # actualizar historial dentro de info tras anadir la ejecucion actual
    info["historial"] = (info["historial"] + [{"ts": ahora.isoformat(),
                          "coste": datos["totales"]["coste"], "sesiones": datos["totales"]["sesiones"],
                          "requests": datos["totales"]["requests"],
                          "limites": datos["limites"]["alta_confianza"]}])[-30:]
    return info

# --------------------------------------------------------------------------------------
# Render HTML
# --------------------------------------------------------------------------------------
def escribir_csv(datos):
    """Exporta el detalle de sesiones a sesiones.csv (UTF-8 con BOM para Excel)."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["inicio", "fin", "proyecto", "tipo", "modelo", "coste_usd", "llamadas",
                "input", "output", "cache_read", "cache_write", "duracion_min",
                "resultado", "objetivo_o_prompt"])
    for s in datos["sesiones"]:
        objetivo = (s.get("objetivo") or s.get("primer_prompt") or "").replace("\n", " ")
        w.writerow([s.get("inicio") or "", s.get("fin") or "", s.get("proyecto") or "",
                    s.get("categoria") or "", s.get("modelo_top") or "", s.get("coste"),
                    s.get("requests"), s.get("input"), s.get("output"),
                    s.get("cache_read"), s.get("cache_write"),
                    s.get("duracion_min") if s.get("duracion_min") is not None else "",
                    s.get("resultado") or "", objetivo])
    escribir(os.path.join(OUT_DIR, "sesiones.csv"), "﻿" + buf.getvalue())

def render(datos, mejora, memoria_claude):
    payload = {"datos": datos, "mejora": mejora, "memoria_claude": memoria_claude, "precios": CFG}
    js = json.dumps(payload, ensure_ascii=False)
    htmlout = PLANTILLA.replace("__DATOS__", js).replace("__GEN__", html.escape(datos["generado"]))
    escribir(SALIDA_HTML, htmlout)
    escribir(os.path.join(OUT_DIR, "index.html"), htmlout)   # entrada amigable (mismo contenido)
    escribir(SALIDA_JSON, json.dumps(datos, ensure_ascii=False, indent=1))
    escribir_csv(datos)

# La plantilla HTML vive en plantilla_html.py (mismo directorio).
sys.path.insert(0, OUT_DIR)
from plantilla_html import PLANTILLA

def main():
    if not _es_seguro_escribir(OUT_DIR):
        print("ERROR: el directorio de salida esta dentro de ~/.claude. Abortando.")
        sys.exit(1)
    if not os.path.isdir(PROJECTS):
        print("No encuentro %s. Abortando." % PROJECTS)
        sys.exit(1)

    ahora = datetime.now().astimezone()
    print("Leyendo transcripts (SOLO LECTURA) en %s ..." % PROJECTS)
    A = analizar_transcripts()
    facets = cargar_facets()
    meta = cargar_meta()
    tasks = contar_tasks()
    memoria_claude = estado_memoria_claude()

    datos = construir(A, facets, meta, tasks, ahora)
    mejora = auto_mejora(datos, A, ahora)
    render(datos, mejora, memoria_claude)

    T = datos["totales"]
    print("\n================ RESUMEN ================")
    print("Transcripts analizados : %d" % T["transcripts"])
    print("Sesiones / Proyectos   : %d / %d" % (T["sesiones"], T["proyectos"]))
    print("Requests (API calls)   : %d" % T["requests"])
    print("Coste total (API)      : $%.2f" % T["coste"])
    print("  input/output/cacheR/cacheW : $%.2f / $%.2f / $%.2f / $%.2f" %
          (T["coste_input"], T["coste_output"], T["coste_cache_read"], T["coste_cache_write"]))
    print("Tokens (in/out/cR/cW)  : %s / %s / %s / %s" %
          (f"{T['input']:,}", f"{T['output']:,}", f"{T['cache_read']:,}", f"{T['cache_write']:,}"))
    print("Limites (alta conf.)   : %d   (menciones: %d)" %
          (datos["limites"]["alta_confianza"], datos["limites"]["menciones_contenido"]))
    sub = datos["subscripcion"]
    print("Suscripcion vs API     : mejor opcion = %s ($%.2f) sobre %d mes/es" %
          (sub["mejor_opcion"]["nombre"], sub["mejor_opcion"]["coste"], sub["n_meses"]))
    print("Auto-mejora            : ejecucion #%d, %d transcripts nuevos, %d cambiados" %
          (mejora["run"], mejora["incremental"]["nuevos"], mejora["incremental"]["cambiados"]))
    print("Cache incremental      : %d servidos de cache, %d releidos" %
          (A.get("incremental_cacheados", 0), A.get("incremental_releidos", 0)))
    bp = datos.get("presupuesto", {})
    print("Mes en curso (%s)    : $%.2f gastado, proyeccion fin de mes $%.2f" %
          (bp.get("mes", ""), bp.get("gasto_mes", 0), bp.get("proyeccion", 0)))
    print("=========================================")
    if datos.get("by_categoria"):
        top = datos["by_categoria"][0]
        print("Actividad dominante    : %s ($%.2f en %d sesiones)" %
              (top["categoria"], top["coste"], top["sesiones"]))
    print("Panel    -> %s" % SALIDA_HTML)
    print("Datos    -> %s" % SALIDA_JSON)
    print("CSV      -> %s" % os.path.join(OUT_DIR, "sesiones.csv"))
    print("Estado   -> %s" % STATE_DIR)
    print("\nGarantia: no se ha escrito NADA dentro de ~/.claude (solo lectura).")

if __name__ == "__main__":
    main()
