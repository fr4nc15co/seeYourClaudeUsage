# -*- coding: utf-8 -*-
"""Plantilla HTML del panel de costes. La cadena PLANTILLA se rellena con __DATOS__."""

PLANTILLA = r"""<!DOCTYPE html>
<!-- generado: __GEN__ -->
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Panel de costes · Claude Code</title>
<style>
  :root{
    --bg:#0b0f17; --bg2:#111726; --card:#141b2d; --card2:#1a2236; --line:#243049;
    --txt:#e7ecf5; --mut:#8a97b1; --mut2:#5d6b88; --acc:#6ea8fe;
    --in:#3b82f6; --out:#f59e0b; --cr:#10b981; --cw:#a855f7; --danger:#ef4444; --ok:#22c55e;
  }
  *{box-sizing:border-box}
  body{margin:0;background:radial-gradient(1200px 700px at 80% -10%,#16203a 0,var(--bg) 55%);
       color:var(--txt);font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
  a{color:var(--acc)}
  .wrap{max-width:1280px;margin:0 auto;padding:22px 20px 80px}
  header.top{display:flex;flex-wrap:wrap;align-items:flex-end;gap:14px;justify-content:space-between;margin-bottom:6px}
  h1{font-size:23px;margin:0;letter-spacing:.2px}
  h1 small{display:block;font-size:12px;color:var(--mut);font-weight:400;margin-top:4px}
  .badges{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
  .badge{font-size:11px;padding:4px 9px;border-radius:999px;border:1px solid var(--line);color:var(--mut);background:var(--card)}
  .badge.ro{color:#7ee2a8;border-color:#1f5137;background:#0f2419}
  h2{font-size:15px;margin:28px 0 12px;color:#cdd6e8;display:flex;align-items:center;gap:8px}
  h2:first-child{margin-top:0}
  h2 .hint{font-size:11px;color:var(--mut2);font-weight:400}
  .grid{display:grid;gap:14px}
  .kpis{grid-template-columns:repeat(auto-fit,minmax(168px,1fr))}
  .card{background:linear-gradient(180deg,var(--card),var(--bg2));border:1px solid var(--line);
        border-radius:14px;padding:15px 16px}
  .kpi .lab{font-size:11px;color:var(--mut);text-transform:uppercase;letter-spacing:.6px}
  .kpi .val{font-size:25px;font-weight:700;margin-top:6px;letter-spacing:.3px}
  .kpi .sub{font-size:11.5px;color:var(--mut);margin-top:3px}
  .kpi .val.danger{color:#ff8a8a}.kpi .val.ok{color:#86efac}
  /* Nivel de uso (banner reactivo al rango) */
  .nivel{display:flex;align-items:center;gap:18px;flex-wrap:wrap;padding:16px 18px;border-width:1px;border-style:solid}
  .nivel .ico{font-size:40px;line-height:1;filter:drop-shadow(0 2px 6px rgba(0,0,0,.4))}
  .nivel .body{flex:1 1 260px;min-width:0}
  .nivel .lab{font-size:11px;color:var(--mut);text-transform:uppercase;letter-spacing:.6px}
  .nivel .name{font-size:23px;font-weight:800;margin:2px 0 4px;letter-spacing:.2px}
  .nivel .sub{font-size:12px;color:var(--mut)}
  .nivel .quip{font-size:12px;font-style:italic;color:var(--mut2);margin-top:4px}
  .nivel .gauge{height:8px;border-radius:999px;background:#0d1322;border:1px solid var(--line);overflow:hidden;margin-top:10px}
  .nivel .gauge>i{display:block;height:100%;border-radius:999px;transition:width .45s ease}
  .nivel .ctrl{display:flex;flex-direction:column;align-items:flex-end;gap:8px}
  .nivel .score{font-size:30px;font-weight:800;line-height:1}
  .nivel .score small{font-size:13px;font-weight:600;color:var(--mut)}
  .cols{display:grid;gap:14px}
  .c2{grid-template-columns:1.55fr 1fr}.c2b{grid-template-columns:1fr 1fr}
  @media(max-width:900px){.c2,.c2b{grid-template-columns:1fr}}
  .chartbox{overflow-x:auto}
  svg{display:block}
  .legend{display:flex;flex-wrap:wrap;gap:10px 16px;margin-top:10px}
  .legend .it{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--mut)}
  .legend .sw{width:11px;height:11px;border-radius:3px;display:inline-block}
  table{width:100%;border-collapse:collapse;font-size:12.5px}
  th,td{text-align:right;padding:7px 9px;border-bottom:1px solid var(--line);white-space:nowrap}
  th:first-child,td:first-child{text-align:left}
  th{color:var(--mut);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.4px;position:sticky;top:0;background:var(--card)}
  tbody tr:hover{background:#0f1626}
  .tag{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;border:1px solid var(--line)}
  .tag.ok{color:#86efac;border-color:#1f5137;background:#0f2419}
  .tag.warn{color:#fde68a;border-color:#5b4a14;background:#241d07}
  .tag.bad{color:#fca5a5;border-color:#5b1f1f;background:#240b0b}
  .mut{color:var(--mut)} .small{font-size:11.5px}
  .barwrap{height:9px;background:#0e1626;border-radius:6px;overflow:hidden}
  .barwrap>i{display:block;height:100%}
  .verdict{font-size:13px}
  .verdict b{font-size:16px}
  .tablebox{max-height:520px;overflow:auto;border:1px solid var(--line);border-radius:12px}
  .controls{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}
  select,input[type=search],input[type=number],input[type=text]{
        background:var(--card2);color:var(--txt);border:1px solid var(--line);
        border-radius:8px;padding:6px 10px;font-size:12.5px}
  input[type=number]:focus,input[type=text]:focus{outline:none;border-color:var(--acc)}
  .precio-tbl input[type=number]{width:82px;padding:4px 8px}
  .btn-action{cursor:pointer;font:inherit;font-size:12px;padding:6px 14px;border-radius:8px;
              border:1px solid #1f5137;color:#7ee2a8;background:#0f2419;transition:opacity .15s}
  .btn-action:hover{opacity:.85}
  .btn-action:disabled{opacity:.45;cursor:default}
  .precios-note{font-size:11px;color:var(--mut2);margin:4px 0 0}
  .heat{display:grid;grid-template-columns:34px repeat(24,1fr);gap:2px;min-width:560px}
  .heat .h{font-size:9px;color:var(--mut2);text-align:center}
  .heat .d{font-size:10px;color:var(--mut);display:flex;align-items:center}
  .heat .cell{height:16px;border-radius:3px;background:#0e1626}
  .reclist{margin:0;padding-left:18px} .reclist li{margin:7px 0;color:#d7deec}
  .kv{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;font-size:12.5px}
  .kv .k{color:var(--mut)}
  .delta.up{color:#fca5a5}.delta.down{color:#86efac}.delta.flat{color:var(--mut)}
  .foot{margin-top:34px;color:var(--mut2);font-size:11.5px;border-top:1px solid var(--line);padding-top:14px}
  .pill{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px;vertical-align:-1px}
  .section-note{font-size:11.5px;color:var(--mut2);margin:8px 0 6px}
  .gran-sel{margin-left:auto;font-size:11px;padding:4px 9px;font-weight:400}

  /* ====================== TABS ====================== */
  .tabs-wrap{
    position:sticky;top:0;z-index:100;
    background:rgba(11,15,23,.92);
    backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
    border-bottom:1px solid var(--line);
    margin:18px -20px 0;padding:0 20px;
  }
  .tabs{display:flex;gap:0;overflow-x:auto;scrollbar-width:none}
  .tabs::-webkit-scrollbar{display:none}
  .tab-btn{
    background:none;border:none;border-bottom:2.5px solid transparent;
    color:var(--mut);font:inherit;font-size:12.5px;padding:11px 16px 10px;
    cursor:pointer;white-space:nowrap;
    transition:color .14s,border-color .14s;
    display:flex;align-items:center;gap:7px;
  }
  .tab-btn:hover{color:var(--txt)}
  .tab-btn.active{color:var(--acc);border-bottom-color:var(--acc);font-weight:600}
  .tab-icon{font-size:14px;line-height:1}
  .tbadge{
    background:#1a2638;border-radius:99px;font-size:10px;padding:1px 7px;
    color:var(--mut2);font-weight:400;transition:background .14s,color .14s;
  }
  .tab-btn.active .tbadge{background:#162236;color:#7fb8fe}
  .tbadge.warn{color:#fca5a5;background:#2a1515}
  .tbadge.ok{color:#86efac;background:#0f2419}

  /* panel fade-in */
  .panel{display:none}
  .panel.active{display:block;animation:panelIn .18s ease}
  @keyframes panelIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
  .panel-body{padding-top:20px}

  /* OVERLAY CONFIGURACIÓN */
  .cfg-btn{background:var(--card);border:1px solid var(--line);border-radius:8px;color:var(--mut);
    font:inherit;font-size:11px;padding:5px 12px;cursor:pointer;white-space:nowrap;
    transition:color .14s,border-color .14s,background .14s}
  .cfg-btn:hover{color:var(--txt);border-color:var(--mut2);background:var(--card2)}
  .ov-bg{position:fixed;inset:0;background:rgba(0,0,0,.72);z-index:900;
    display:none;align-items:flex-start;justify-content:center;padding-top:54px;
    animation:ovIn .18s ease}
  .ov-bg.open{display:flex}
  @keyframes ovIn{from{opacity:0}to{opacity:1}}
  .ov-box{background:var(--card);border:1px solid var(--line);border-radius:16px;
    width:min(880px,96vw);max-height:82vh;overflow:auto;padding:26px;
    animation:panelIn .2s ease}
  .ov-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
  .ov-hdr h2{margin:0;font-size:17px;color:#cdd6e8}
  .ov-close{background:none;border:none;color:var(--mut);font-size:28px;cursor:pointer;
    padding:0 4px;line-height:1;transition:color .14s}
  .ov-close:hover{color:var(--txt)}

  /* TOOLTIP */
  #tip{position:fixed;pointer-events:none;z-index:9100;display:none;
    background:var(--card2);border:1px solid var(--line);border-radius:8px;
    padding:7px 12px;font-size:12px;color:var(--txt);white-space:nowrap;
    box-shadow:0 4px 20px rgba(0,0,0,.5);line-height:1.6}
  svg [data-tip]:hover{opacity:.78;transition:opacity .1s;cursor:default}
</style>
</head>
<body>
<div class="wrap">

  <header class="top">
    <h1>Panel de costes · Claude Code
        <small id="hdrsub"></small></h1>
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
      <div class="badges" id="badges"></div>
      <button class="cfg-btn" id="btn_cfg" title="Configuración de tarifas y planes">⚙ Configuración</button>
    </div>
  </header>

  <!-- KPIs siempre visibles -->
  <section class="grid kpis" id="kpis" style="margin-top:14px"></section>

  <!-- Nivel de uso · "¿estoy enganchado?" (reactivo al selector de rango) -->
  <section class="card nivel" id="nivel_box" style="margin-top:14px"></section>

  <!-- Barra de tabs (sticky) -->
  <div class="tabs-wrap">
    <nav class="tabs" role="tablist" aria-label="Secciones del panel">
      <button class="tab-btn active" data-tab="costes" role="tab">
        <span class="tab-icon">💰</span>Costes<span class="tbadge" id="tb-costes"></span>
      </button>
      <button class="tab-btn" data-tab="productividad" role="tab">
        <span class="tab-icon">🎯</span>Productividad<span class="tbadge" id="tb-productividad"></span>
      </button>
      <button class="tab-btn" data-tab="actividad" role="tab">
        <span class="tab-icon">📊</span>Actividad<span class="tbadge" id="tb-actividad"></span>
      </button>
      <button class="tab-btn" data-tab="sesiones" role="tab">
        <span class="tab-icon">📋</span>Sesiones<span class="tbadge" id="tb-sesiones"></span>
      </button>
      <button class="tab-btn" data-tab="recomendaciones" role="tab">
        <span class="tab-icon">💡</span>Recomendaciones<span class="tbadge" id="tb-recomendaciones"></span>
      </button>
    </nav>
  </div>

  <!-- ============================================================
       TAB 1 · COSTES
       Gasto por día · semana/hora · modelo · suscripción vs API
       ============================================================ -->
  <div class="panel active" id="panel-costes" role="tabpanel">
    <div class="panel-body">
      <h2>Gasto en el tiempo <span class="hint">(apilado por modelo · tarifas API)</span>
        <select class="gran-sel rango-sel" title="Rango temporal (afecta a este gráfico, al donut y al de tokens)">
          <option value="todo">Todo</option>
          <option value="7">Últ. 7 días</option>
          <option value="30">Últ. 30 días</option>
          <option value="90">Últ. 90 días</option>
          <option value="mes">Este mes</option>
        </select>
        <select id="gran_costes" class="gran-sel">
          <option value="dia">Por día</option>
          <option value="semana">Por semana</option>
          <option value="mes">Por mes</option>
        </select></h2>
      <div class="section-note" id="periodo_costes" style="margin:2px 0 10px"></div>
      <div class="cols c2">
        <div class="card chartbox" id="chart_day"></div>
        <div class="card">
          <div id="donut_model"></div>
          <div class="legend" id="legend_model"></div>
        </div>
      </div>

      <h2>Coste por hora del día <span class="hint">(suma de todos los días · hora local)</span></h2>
      <div class="card chartbox" id="chart_hour"></div>

      <h2>Mapa de calor <span class="hint">(día × hora · intensidad = gasto acumulado)</span></h2>
      <div class="card chartbox" id="heat"></div>

      <h2>ROI y eficiencia</h2>
      <div class="grid kpis" id="roi_kpis"></div>

      <h2>Mes en curso <span class="hint">(mes natural · proyección a fin de mes)</span></h2>
      <div class="card" id="budget_box"></div>

      <h2>Desglose por modelo <span class="hint">(histórico completo)</span></h2>
      <div class="card"><div class="tablebox" style="max-height:none"><table id="tbl_model"></table></div></div>

      <h2>Suscripción vs pago por uso (API) <span class="hint">por mes</span></h2>
      <div class="cols c2">
        <div class="card chartbox" id="chart_subs"></div>
        <div class="card" id="subs_verdict"></div>
      </div>
    </div>
  </div>

  <!-- ============================================================
       TAB 2 · ACTIVIDAD
       Tokens por día · proyectos · heatmap
       ============================================================ -->
  <div class="panel" id="panel-actividad" role="tabpanel">
    <div class="panel-body">
      <h2>Tokens en el tiempo <span class="hint">(entrada / salida / cache lectura / cache escritura)</span>
        <select class="gran-sel rango-sel" title="Rango temporal (compartido con la pestaña Costes)">
          <option value="todo">Todo</option>
          <option value="7">Últ. 7 días</option>
          <option value="30">Últ. 30 días</option>
          <option value="90">Últ. 90 días</option>
          <option value="mes">Este mes</option>
        </select>
        <select id="gran_tokens" class="gran-sel">
          <option value="dia">Por día</option>
          <option value="semana">Por semana</option>
          <option value="mes">Por mes</option>
        </select></h2>
      <div class="section-note" id="periodo_tokens" style="margin:2px 0 10px"></div>
      <div class="card chartbox" id="chart_tokens"></div>
      <div class="legend" id="legend_tokens" style="padding-left:4px"></div>

      <h2 style="margin-top:22px">Tokens por modelo <span class="hint">(total y composición: entrada / salida / caché)</span></h2>
      <div class="cols c2">
        <div class="card chartbox" id="chart_tok_model"></div>
        <div class="card" style="padding:0"><div class="tablebox" style="max-height:none"><table id="tbl_tok_model"></table></div></div>
      </div>
      <div class="legend" id="legend_tok_model" style="padding-left:4px;margin-top:10px"></div>

      <h2 style="margin-top:22px">Tipos de actividad <span class="hint">(coste por tipo de tarea · clasificación automática, sin IA)</span></h2>
      <div id="cat_outcomes" style="margin:2px 0 12px"></div>
      <div class="cols c2">
        <div class="card">
          <div id="donut_cat"></div>
          <div class="legend" id="legend_cat"></div>
        </div>
        <div class="card">
          <b style="font-size:13px;color:#cdd6e8">Herramientas más usadas</b>
          <p class="section-note" style="margin-top:2px">Recuento de invocaciones de cada tool en todas las sesiones.</p>
          <div id="tools_box" style="margin-top:10px"></div>
        </div>
      </div>

      <h2 style="margin-top:14px">Gasto por proyecto</h2>
      <div class="card" id="chart_proj"></div>

      <h2 style="margin-top:18px">Archivos y patrones <span class="hint">(ficheros más tocados · repetición · comandos de shell)</span></h2>
      <div class="cols c2">
        <div class="card" style="padding:0"><div class="tablebox" style="max-height:380px"><table id="tbl_archivos"></table></div></div>
        <div class="card">
          <b style="font-size:13px;color:#cdd6e8">Comandos de shell más usados</b>
          <div id="bash_box" style="margin-top:10px"></div>
          <div id="relec_box" style="margin-top:16px"></div>
        </div>
      </div>

    </div>
  </div>

  <!-- ============================================================
       TAB 5 · RECOMENDACIONES
       Rightsizing · auto-mejora · skills · caché · límites
       ============================================================ -->
  <div class="panel" id="panel-recomendaciones" role="tabpanel">
    <div class="panel-body">
      <h2>Recomendaciones de modelo <span class="hint">(¿dónde usar un modelo más barato?)</span></h2>
      <div class="grid kpis" id="rs_kpis" style="margin-bottom:14px"></div>
      <div class="cols c2">
        <div class="card" id="rs_guide"></div>
        <div class="card" id="rs_recs"></div>
      </div>
      <div id="rs_tblwrap" class="card" style="padding:0;margin-top:14px">
        <div class="tablebox"><table id="rs_tbl"></table></div>
      </div>
      <p class="section-note" id="rs_note"></p>

      <h2 style="margin-top:34px">Ajuste por tipo de actividad <span class="hint">(¿qué categorías de tarea corren en un modelo más caro del necesario?)</span></h2>
      <div class="grid kpis" id="aj_kpis" style="margin-bottom:14px"></div>
      <div class="card" id="aj_recs"></div>
      <div id="aj_tblwrap" class="card" style="padding:0;margin-top:14px">
        <div class="tablebox"><table id="aj_tbl"></table></div>
      </div>
      <p class="section-note" id="aj_note"></p>

      <h2 style="margin-top:34px">Auto-mejora <span class="hint">(el panel aprende y se afina en cada ejecución)</span></h2>
      <div class="card" id="improve_box"></div>
    </div>
  </div>

  <!-- ============================================================
       TAB 4 · SESIONES
       Tabla detallada con filtros
       ============================================================ -->
  <div class="panel" id="panel-sesiones" role="tabpanel">
    <div class="panel-body">
      <h2>Sesiones <span class="hint">(coste, tokens, actividad y resultado)</span></h2>
      <div class="controls">
        <select id="f_proj"></select>
        <select id="f_cat"></select>
        <input type="search" id="f_text" placeholder="buscar prompt / objetivo…">
        <span class="mut small" id="sess_count"></span>
        <button class="btn-action" id="btn_csv" style="margin-left:auto" title="Descarga las sesiones filtradas en CSV">⬇ Exportar CSV</button>
      </div>
      <div class="card" style="padding:0"><div class="tablebox"><table id="tbl_sess"></table></div></div>

      <h2 style="margin-top:22px">Skills invocadas</h2>
      <div class="card" id="skills_box"></div>

      <h2 style="margin-top:22px">Caché y límites de uso</h2>
      <div class="cols c2b">
        <div class="card" id="cache_box"></div>
        <div class="card" id="limits_box"></div>
      </div>

      <h2 style="margin-top:22px">Memoria acumulada del panel</h2>
      <div class="card" id="memory_box"></div>
    </div>
  </div>

  <!-- ============================================================
       TAB 2 · PRODUCTIVIDAD
       Código generado · outcomes · lenguajes · duración · tasks
       ============================================================ -->
  <div class="panel" id="panel-productividad" role="tabpanel">
    <div class="panel-body">
      <h2>Código generado <span class="hint">(commits · líneas añadidas/eliminadas · datos de session-meta)</span></h2>
      <div class="card chartbox" id="chart_git_day"></div>

      <h2 style="margin-top:22px">Resultado de sesiones por semana <span class="hint">(outcomes de facets)</span></h2>
      <div class="card chartbox" id="chart_outcomes_week"></div>

      <h2 style="margin-top:22px">Lenguajes de programación y tipos de sesión</h2>
      <div class="cols c2b">
        <div class="card">
          <div id="donut_langs"></div>
          <div class="legend" id="legend_langs"></div>
        </div>
        <div class="card">
          <div id="donut_tipo_ses"></div>
          <div class="legend" id="legend_tipo_ses"></div>
        </div>
      </div>

      <h2 style="margin-top:22px">Distribución de duración de sesiones</h2>
      <div class="card chartbox" id="chart_dur_hist"></div>

      <h2 style="margin-top:22px">Tasks por proyecto <span class="hint">(estado de las tareas en ~/.claude/tasks/)</span></h2>
      <div class="card" id="tasks_box"></div>
    </div>
  </div>

  <div class="foot" id="foot"></div>
</div><!-- /wrap -->

<div id="tip"></div>

<!-- OVERLAY: CONFIGURACIÓN DE TARIFAS Y PLANES -->
<div class="ov-bg" id="ov_cfg" role="dialog" aria-modal="true" aria-label="Configuración">
  <div class="ov-box">
    <div class="ov-hdr">
      <h2>⚙ Configuración de tarifas y planes</h2>
      <button class="ov-close" id="btn_cfg_close" aria-label="Cerrar configuración">×</button>
    </div>
    <div class="card" id="precios_editor"></div>
    <div id="precios_actions" style="margin-top:12px;display:flex;gap:12px;align-items:center">
      <button class="btn-action" id="btn_save_precios">💾 Guardar y recalcular</button>
      <span class="small" id="precios_status"></span>
    </div>
  </div>
</div>

<script>
const PAYLOAD = __DATOS__;
const D = PAYLOAD.datos, M = PAYLOAD.mejora, MC = PAYLOAD.memoria_claude;
const COL = {}; D.by_model.forEach(m=>COL[m.modelo]=m.color);
const ELAB = {}; D.by_model.forEach(m=>ELAB[m.modelo]=m.etiqueta);
const CATCOL = {"Programación":"#3b82f6","Depuración":"#ef4444","Refactorización":"#a855f7",
  "Pruebas":"#f59e0b","Documentación":"#6ea8fe","Exploración":"#10b981","Investigación":"#14b8a6",
  "Orquestación":"#ec4899","Configuración/DevOps":"#8b5cf6","Scripting/Shell":"#64748b","Otro":"#5d6b88"};
function catTag(c){ if(!c) return ""; const k=CATCOL[c]||"#5d6b88";
  return `<span class="tag" style="border-color:${k};color:${k}">${esc(c)}</span>`; }

const TASA=(PAYLOAD.precios&&PAYLOAD.precios.eur_por_usd)||1;   // USD -> EUR (solo display)
function money(v){ v=(v||0)*TASA; if(!v) return "0 €"; const a=Math.abs(v);
  if(a<0.01) return v.toFixed(4)+" €";
  return v.toLocaleString("es-ES",{minimumFractionDigits:2,maximumFractionDigits:2})+" €"; }
function eur0(v){ return Math.round((v||0)*TASA)+" €"; }          // etiqueta compacta de barra
function eurize(s){ return (s==null?"":(""+s)).replace(/\$(\d+(?:\.\d+)?)/g,(m,n)=>money(parseFloat(n))); }
function toks(v){ v=v||0; if(v>=1e6) return (v/1e6).toFixed(2)+"M"; if(v>=1e3) return (v/1e3).toFixed(1)+"k"; return ""+v; }
function pct(v){ return (v||0).toFixed(1)+"%"; }
function esc(s){ return (s==null?"":(""+s)).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])); }
function el(id){ return document.getElementById(id); }
const DIAS=["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"];

/* ===================== RANGO TEMPORAL (global) =====================
   Un selector compartido (clase .rango-sel) filtra las series temporales de gasto y
   tokens + su donut de modelo. Las tablas detalladas y KPIs siguen siendo histórico. */
let RANGO="todo";
const RANGO_CBS=[];
function _hoy(){ return new Date(); }
function rangoCutoff(){
  if(RANGO==="todo") return null;
  if(RANGO==="mes") return {mes:_hoy().toISOString().slice(0,7)};
  const n=parseInt(RANGO,10); const d=_hoy(); d.setDate(d.getDate()-(n-1));
  return {desde:d.toISOString().slice(0,10)};
}
function enRangoDia(dia){ const c=rangoCutoff(); if(!c||!dia) return true;
  return c.mes ? dia.slice(0,7)===c.mes : dia>=c.desde; }
function filtraByDay(bd){ return (bd||[]).filter(d=>enRangoDia(d.dia)); }
const RANGO_LAB={todo:"todo el histórico","7":"últimos 7 días","30":"últimos 30 días","90":"últimos 90 días",mes:"este mes"};
function resumenPeriodo(bd){
  const coste=bd.reduce((a,d)=>a+d.coste,0);
  const tk=bd.reduce((a,d)=>a+d.input+d.output+d.cache_read+d.cache_write,0);
  const reqs=bd.reduce((a,d)=>a+d.requests,0);
  const ses=D.sesiones.filter(s=>s.inicio&&enRangoDia(s.inicio.slice(0,10))).length;
  const pctG=D.totales.coste?100*coste/D.totales.coste:0;
  const span=RANGO==="todo"?"":` <span class="mut">(${bd.length} días)</span>`;
  return `<b>Periodo:</b> ${esc(RANGO_LAB[RANGO]||RANGO)}${span} · <b>${money(coste)}</b> `+
    `<span class="mut">(${pctG.toFixed(0)}% del total)</span> · ${toks(tk)} tokens · `+
    `${reqs.toLocaleString()} llamadas · ${ses} sesiones`;
}
function setRango(v){ RANGO=v;
  document.querySelectorAll(".rango-sel").forEach(s=>{ if(s.value!==v) s.value=v; });
  RANGO_CBS.forEach(f=>{ try{ f(); }catch(e){} }); }
document.querySelectorAll(".rango-sel").forEach(s=>{ s.value=RANGO; s.onchange=()=>setRango(s.value); });

/* ===================== TAB SWITCHING ===================== */
(function(){
  const VALID=["costes","productividad","actividad","sesiones","recomendaciones"];
  function activate(tab){
    document.querySelectorAll(".tab-btn").forEach(b=>b.classList.toggle("active",b.dataset.tab===tab));
    document.querySelectorAll(".panel").forEach(p=>p.classList.toggle("active",p.id==="panel-"+tab));
    history.replaceState(null,"","#"+tab);
  }
  document.querySelectorAll(".tab-btn").forEach(btn=>{
    btn.addEventListener("click",()=>activate(btn.dataset.tab));
  });
  const hash=(location.hash||"").slice(1);
  if(VALID.includes(hash)) activate(hash);
})();

/* ===================== SVG CHARTS ===================== */

function stacked(rows,series,opt){
  opt=opt||{}; const bw=opt.bw||26, gap=opt.gap||8, padL=56, padR=14, padT=14, padB=opt.padB||64;
  const W=Math.max(620,padL+padR+rows.length*(bw+gap));
  const H=opt.h||300, ih=H-padT-padB;
  let max=1e-9; rows.forEach(r=>{let s=0;series.forEach(se=>s+=(r.vals[se.key]||0));if(s>max)max=s;});
  const nice=Math.pow(10,Math.floor(Math.log10(max))); max=Math.ceil(max/nice)*nice;
  const y=v=>padT+ih-(v/max)*ih;
  let g=`<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">`;
  for(let i=0;i<=4;i++){const v=max*i/4,yy=y(v);
    g+=`<line x1="${padL}" y1="${yy}" x2="${W-padR}" y2="${yy}" stroke="#1d2740"/>`;
    g+=`<text x="${padL-8}" y="${yy+3}" fill="#5d6b88" font-size="10" text-anchor="end">${opt.fmt?opt.fmt(v):money(v)}</text>`;}
  rows.forEach((r,i)=>{ let x=padL+i*(bw+gap), acc=0;
    series.forEach(se=>{ const v=r.vals[se.key]||0; if(v<=0) return;
      const hh=(v/max)*ih, yy=y(acc+v);
      g+=`<rect x="${x}" y="${yy}" width="${bw}" height="${Math.max(0.5,hh)}" fill="${se.color}" rx="1.5" data-tip="${esc(r.label+' · '+se.label+': '+(opt.fmt?opt.fmt(v):money(v)))}" data-color="${se.color}"></rect>`;
      acc+=v; });
    const tot=series.reduce((s,se)=>s+(r.vals[se.key]||0),0);
    if(tot>0) g+=`<text x="${x+bw/2}" y="${y(tot)-4}" fill="#9fb0d0" font-size="9" text-anchor="middle">${opt.lab?opt.lab(tot):""}</text>`;
    const lx=x+bw/2, ly=H-padB+12;
    g+=`<text x="${lx}" y="${ly}" fill="#7c8aa8" font-size="9.5" text-anchor="end" transform="rotate(-45 ${lx} ${ly})">${esc(r.label)}</text>`;
  });
  g+=`</svg>`; return g;
}

function grouped(rows,series,opt){
  opt=opt||{}; const gw=series.length*opt.bw+(series.length-1)*2; const grp=gw+22, padL=56,padR=14,padT=14,padB=52;
  const W=Math.max(620,padL+padR+rows.length*grp), H=opt.h||280, ih=H-padT-padB;
  let max=1e-9; rows.forEach(r=>series.forEach(se=>{if((r.vals[se.key]||0)>max)max=r.vals[se.key];}));
  const nice=Math.pow(10,Math.floor(Math.log10(max||1))); max=Math.ceil((max||1)/nice)*nice||1;
  const y=v=>padT+ih-(v/max)*ih;
  let g=`<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">`;
  for(let i=0;i<=4;i++){const v=max*i/4,yy=y(v);
    g+=`<line x1="${padL}" y1="${yy}" x2="${W-padR}" y2="${yy}" stroke="#1d2740"/>`;
    g+=`<text x="${padL-8}" y="${yy+3}" fill="#5d6b88" font-size="10" text-anchor="end">${money(v)}</text>`;}
  rows.forEach((r,i)=>{ let x0=padL+i*grp+11;
    series.forEach((se,j)=>{ const v=r.vals[se.key]||0, x=x0+j*(opt.bw+2), hh=(v/max)*ih;
      g+=`<rect x="${x}" y="${y(v)}" width="${opt.bw}" height="${Math.max(0.5,hh)}" fill="${se.color}" rx="1.5" data-tip="${esc(r.label+' · '+se.label+': '+money(v))}" data-color="${se.color}"></rect>`; });
    g+=`<text x="${x0+gw/2}" y="${H-padB+16}" fill="#7c8aa8" font-size="10" text-anchor="middle">${esc(r.label)}</text>`;
  });
  g+=`</svg>`; return g;
}

function donut(items,center){
  const R=78,r=50,cx=110,cy=100; let tot=items.reduce((s,i)=>s+i.value,0)||1, a=-Math.PI/2;
  let g=`<svg viewBox="0 0 220 200" width="220" height="200">`;
  items.forEach(it=>{ const frac=it.value/tot, a2=a+frac*2*Math.PI;
    const x1=cx+R*Math.cos(a),y1=cy+R*Math.sin(a),x2=cx+R*Math.cos(a2),y2=cy+R*Math.sin(a2);
    const xi2=cx+r*Math.cos(a2),yi2=cy+r*Math.sin(a2),xi1=cx+r*Math.cos(a),yi1=cy+r*Math.sin(a);
    const large=frac>0.5?1:0;
    g+=`<path d="M${x1} ${y1} A${R} ${R} 0 ${large} 1 ${x2} ${y2} L${xi2} ${yi2} A${r} ${r} 0 ${large} 0 ${xi1} ${yi1} Z" fill="${it.color}" data-tip="${esc(it.label+': '+money(it.value)+' ('+pct(100*it.value/tot)+')')}" data-color="${it.color}"></path>`;
    a=a2; });
  g+=`<text x="${cx}" y="${cy-4}" fill="#e7ecf5" font-size="20" font-weight="700" text-anchor="middle">${center.big}</text>`;
  g+=`<text x="${cx}" y="${cy+14}" fill="#8a97b1" font-size="11" text-anchor="middle">${center.small}</text></svg>`;
  return g;
}

function hbars(items,fmt){
  const max=Math.max(1e-9,...items.map(i=>i.value));
  let h="";
  items.forEach(it=>{ h+=`<div style="margin:9px 0">
    <div style="display:flex;justify-content:space-between;font-size:12.5px;margin-bottom:3px">
      <span>${esc(it.label)} ${it.sub?`<span class="mut small">${esc(it.sub)}</span>`:""}</span>
      <span class="mut">${fmt?fmt(it.value):money(it.value)}</span></div>
    <div class="barwrap"><i style="width:${(100*it.value/max).toFixed(1)}%;background:${it.color||"#6ea8fe"}" data-tip="${esc(it.label+': '+(fmt?fmt(it.value):money(it.value)))}" data-color="${it.color||'#6ea8fe'}"></i></div></div>`; });
  return h;
}

/* Reagrupa la serie diaria (D.by_day) por día / semana (lunes) / mes. En cliente. */
function agrupar(byday, gran){
  if(gran==="dia") return (byday||[]).map(d=>({label:d.dia.slice(5),modelos:d.modelos,
    input:d.input,output:d.output,cache_read:d.cache_read,cache_write:d.cache_write}));
  const map={};
  (byday||[]).forEach(d=>{
    let k,label;
    if(gran==="mes"){ k=d.dia.slice(0,7); label=k; }
    else { const dt=new Date(d.dia); const dow=(dt.getUTCDay()+6)%7;       // lunes=0
           dt.setUTCDate(dt.getUTCDate()-dow); k=dt.toISOString().slice(0,10); label=k.slice(5); }
    let g=map[k]; if(!g){ g=map[k]={k,label,modelos:{},input:0,output:0,cache_read:0,cache_write:0}; }
    g.input+=d.input; g.output+=d.output; g.cache_read+=d.cache_read; g.cache_write+=d.cache_write;
    Object.entries(d.modelos||{}).forEach(([m,v])=>g.modelos[m]=(g.modelos[m]||0)+v);
  });
  return Object.values(map).sort((a,b)=>a.k<b.k?-1:1);
}

/* ===================== KPIs + TAB BADGES ===================== */
(function(){
  el("hdrsub").textContent="Generado "+D.generado+" · "+D.totales.transcripts+" transcripts · "+D.claude_dir;
  const b=el("badges");
  b.innerHTML=`<span class="badge ro">● SOLO LECTURA sobre ~/.claude</span>`+
    `<span class="badge">Tarifas API ${esc(D.precios_meta.vigente_desde||"")}</span>`;
  const T=D.totales, sub=D.subscripcion;
  const kpis=[
    {lab:"Coste total (API)",val:money(T.coste),sub:`${T.requests.toLocaleString()} llamadas`},
    {lab:"Tokens totales",val:toks(T.tokens_total),sub:`in ${toks(T.input)} · out ${toks(T.output)}`},
    {lab:"Tokens de caché",val:toks(T.cache_read+T.cache_write),sub:`lectura ${toks(T.cache_read)} · escritura ${toks(T.cache_write)}`},
    {lab:"Sesiones",val:T.sesiones,sub:`${T.proyectos} proyectos · ${T.dias} días`},
    {lab:"Límites de uso",val:D.limites.limite_uso,cls:D.limites.limite_uso?"danger":"ok",
       sub:`${D.limites.alta_confianza} errores API en total`},
    {lab:"Ahorro por caché",val:money(D.cache.ahorro_estimado),cls:"ok",sub:`ratio lectura ${pct(D.cache.ratio_lectura)}`},
    {lab:"Mejor opción",val:sub.mejor_opcion.nombre.replace(" (pago por uso)",""),
       sub:`${money(sub.mejor_opcion.coste)} / ${sub.n_meses} mes(es)`},
  ];
  el("kpis").innerHTML=kpis.map(k=>`<div class="card kpi"><div class="lab">${k.lab}</div>
    <div class="val ${k.cls||""}">${k.val}</div><div class="sub">${k.sub||""}</div></div>`).join("");

  /* badges de las tabs */
  el("tb-costes").textContent=money(T.coste);
  el("tb-actividad").textContent=toks(T.tokens_total);
  const rs=D.rightsizing||{}, aj=D.ajuste_actividad||{};
  const ahorroMax=Math.max(rs.ahorro_total||0, aj.ahorro_total||0);
  const recBadge=el("tb-recomendaciones");
  if(ahorroMax>0){ recBadge.textContent=money(ahorroMax)+" ahorro"; recBadge.classList.add("ok"); }
  else if(D.limites.alta_confianza>0){ recBadge.textContent=D.limites.alta_confianza+" lím."; recBadge.classList.add("warn"); }
  else { recBadge.textContent="sin errores"; recBadge.classList.add("ok"); }
  el("tb-sesiones").textContent=T.sesiones+" ses";
  const totalCommits=D.sesiones.reduce((a,s)=>a+(s.git_commits||0),0);
  const prodBadge=el("tb-productividad");
  if(totalCommits>0){ prodBadge.textContent=totalCommits+"c"; }
})();

/* ===================== NIVEL DE USO ("¿estoy enganchado?") =====================
   Mide la intensidad sobre la ventana activa (selector de rango compartido).
   score = 100·(0,55·frecuencia + 0,45·intensidad), con
     frecuencia = días activos / días de la ventana (hábito)
     intensidad = min(1, llamadas-por-día / 250)        (volumen, saturado)
   Reutiliza by_day + filtraByDay; se recalcula con setRango (RANGO_CBS). */
(function(){
  const SAT_REQDIA=250;            // llamadas/día a las que la intensidad satura a 1
  const NIVELES=[                  // de más a menos; primero cuyo min<=score gana
    {min:80, emoji:"🚨", name:"Adicto perdido a Claude", color:"#ff6b6b", quip:"Esto ya no es uso, es una relación."},
    {min:55, emoji:"🔥", name:"Enganchado",              color:"#f59e0b", quip:"Lo abres más que el WhatsApp."},
    {min:30, emoji:"⚡", name:"Uso moderado",            color:"#6ea8fe", quip:"Uso con cabeza, sin pasarte."},
    {min:0,  emoji:"🌱", name:"Uso ocasional",           color:"#86efac", quip:"De vez en cuando, a ratos."},
  ];
  const DESENGANCHADO={emoji:"🛌", name:"Desenganchado", color:"#8b95a7", quip:"Claude te echa de menos."};
  function diasVentana(){
    if(RANGO==="mes")  return Math.max(1,_hoy().getDate());
    if(RANGO!=="todo") return parseInt(RANGO,10);
    const f=(D.by_day[0]||{}).dia; if(!f) return 1;     // by_day va de antiguo a reciente
    return Math.max(1, Math.round((_hoy()-new Date(f+"T00:00:00"))/86400000)+1);
  }
  function draw(){
    const bd=filtraByDay(D.by_day), dv=diasVentana(), da=bd.length;
    const req=bd.reduce((a,d)=>a+d.requests,0), cost=bd.reduce((a,d)=>a+d.coste,0);
    const reqDia=req/dv, freq=Math.min(1,da/dv), inten=Math.min(1,reqDia/SAT_REQDIA);
    const score=da===0?0:Math.round(100*(0.55*freq+0.45*inten));
    const lv=da===0?DESENGANCHADO:NIVELES.find(n=>score>=n.min);
    const box=el("nivel_box");
    box.style.borderColor=lv.color+"66";
    box.innerHTML=
      `<div class="ico">${lv.emoji}</div>`+
      `<div class="body">`+
        `<div class="lab">Nivel de uso · ${esc(RANGO_LAB[RANGO]||RANGO)}</div>`+
        `<div class="name" style="color:${lv.color}">${esc(lv.name)}</div>`+
        `<div class="sub">${da}/${dv} días activos · ${Math.round(reqDia).toLocaleString()} llamadas/día · `+
          `${req.toLocaleString()} llamadas · ${money(cost)}</div>`+
        `<div class="gauge"><i style="width:${Math.max(2,score)}%;background:${lv.color}"></i></div>`+
        `<div class="quip">${esc(lv.quip)}</div>`+
      `</div>`+
      `<div class="ctrl">`+
        `<select class="gran-sel rango-sel" aria-label="Rango del nivel de uso">`+
          `<option value="todo">Todo</option><option value="7">Últ. 7 días</option>`+
          `<option value="30">Últ. 30 días</option><option value="90">Últ. 90 días</option>`+
          `<option value="mes">Este mes</option></select>`+
        `<div class="score" style="color:${lv.color}">${score}<small>/100</small></div>`+
      `</div>`;
    const s=box.querySelector(".rango-sel");          // re-sincroniza y re-cablea el selector recién inyectado
    if(s){ s.value=RANGO; s.onchange=()=>setRango(s.value); }
  }
  RANGO_CBS.push(draw); draw();
})();

/* ===================== TAB: COSTES ===================== */

(function(){ /* gasto en el tiempo (día/semana/mes · rango temporal) */
  const series=D.by_model.map(m=>({key:m.modelo,color:m.color,label:m.etiqueta}));
  const sel=el("gran_costes");
  function draw(){
    const bd=filtraByDay(D.by_day), gran=sel.value;
    const rows=agrupar(bd,gran).map(g=>({label:g.label,vals:g.modelos}));
    const opt=gran==="dia"?{h:320}:{h:320,bw:gran==="mes"?54:40,gap:gran==="mes"?20:14};
    el("chart_day").innerHTML=stacked(rows,series,{...opt,fmt:money,lab:v=>v>=1?eur0(v):""});
    el("periodo_costes").innerHTML=resumenPeriodo(bd);
  }
  sel.onchange=draw; RANGO_CBS.push(draw); draw();
})();

(function(){ /* donut modelo (rango temporal) */
  function draw(){
    const bd=filtraByDay(D.by_day), agg={};
    bd.forEach(d=>Object.entries(d.modelos||{}).forEach(([m,v])=>agg[m]=(agg[m]||0)+v));
    const tot=Object.values(agg).reduce((a,b)=>a+b,0);
    const items=D.by_model.filter(m=>(agg[m.modelo]||0)>0).map(m=>({label:m.etiqueta,value:agg[m.modelo],color:m.color}));
    el("donut_model").innerHTML=donut(items,{big:money(tot),small:RANGO==="todo"?"coste total":"coste periodo"});
    el("legend_model").innerHTML=D.by_model.map(m=>{const c=agg[m.modelo]||0,sh=tot?100*c/tot:0;
      return `<span class="it"><span class="sw" style="background:${m.color}"></span>${m.etiqueta} · ${money(c)} (${sh.toFixed(1)}%)</span>`;}).join("");
  }
  RANGO_CBS.push(draw); draw();
})();

(function(){ /* hora del día */
  const rows=(D.by_hour||[]).map(h=>({label:String(h.hora).padStart(2,"0"),vals:{c:h.coste}}));
  el("chart_hour").innerHTML=`<div class="section-note" style="margin-top:0">Suma de todos los días · por hora (local)</div>`+
    stacked(rows,[{key:"c",color:"#6ea8fe",label:"Coste"}],{h:250,bw:17,gap:4,fmt:money,lab:v=>v>=10?eur0(v):""});
})();

(function(){ /* heatmap de coste (día × hora) — ahora en pestaña Costes */
  let max=1e-9; D.heat.forEach(r=>r.forEach(v=>{if(v>max)max=v;}));
  let h=`<div class="section-note" style="margin-top:0;margin-bottom:8px">Coste acumulado por día de semana y hora · color = intensidad</div><div class="heat"><div class="h"></div>`;
  for(let hr=0;hr<24;hr++) h+=`<div class="h">${hr%3===0?hr:""}</div>`;
  for(let d=0;d<7;d++){ h+=`<div class="d">${DIAS[d]}</div>`;
    for(let hr=0;hr<24;hr++){ const v=D.heat[d][hr], a=v>0?(0.12+0.88*v/max):0;
      const bg=v>0?`rgba(110,168,254,${a.toFixed(3)})`:"#0e1626";
      h+=`<div class="cell" style="background:${bg}" title="${DIAS[d]} ${hr}:00 — ${money(v)}"></div>`; } }
  h+=`</div>`; el("heat").innerHTML=h;
})();

(function(){ /* tabla modelo */
  let h=`<thead><tr><th>Modelo</th><th>Coste</th><th>%</th><th>Llamadas</th><th>Input</th><th>Output</th><th>Cache lect.</th><th>Cache escr.</th><th>Tokens</th></tr></thead><tbody>`;
  D.by_model.forEach(m=>{ const tk=m.input+m.output+m.cache_read+m.cache_write;
    h+=`<tr><td><span class="pill" style="background:${m.color}"></span>${m.etiqueta}</td>
    <td>${money(m.coste)}</td><td>${m.share}%</td><td>${m.requests.toLocaleString()}</td>
    <td>${toks(m.input)}</td><td>${toks(m.output)}</td><td>${toks(m.cache_read)}</td><td>${toks(m.cache_write)}</td><td><b>${toks(tk)}</b></td></tr>`; });
  const T=D.totales;
  h+=`<tr style="font-weight:700"><td>TOTAL</td><td>${money(T.coste)}</td><td>100%</td><td>${T.requests.toLocaleString()}</td>
    <td>${toks(T.input)}</td><td>${toks(T.output)}</td><td>${toks(T.cache_read)}</td><td>${toks(T.cache_write)}</td><td>${toks(T.tokens_total)}</td></tr></tbody>`;
  el("tbl_model").innerHTML=h;
})();

(function(){ /* ROI y eficiencia */
  const sub=D.subscripcion, ef=D.eficiencia||{};
  const roiMul=sub.roi_multiplicador, roiPct=sub.roi_pct;
  const roiVal=roiMul!=null?roiMul.toFixed(1)+"×":"—";
  const roiSub=roiMul!=null
    ?`+${roiPct!=null?roiPct.toFixed(0):0}% · ${esc(sub.mejor_opcion.nombre)} ${money(sub.mejor_opcion.coste)}`
    :`pago por uso (sin cuota fija)`;
  const kpis=[
    {lab:"ROI suscripción",val:roiVal,cls:roiMul&&roiMul>=2?"ok":"",
     sub:roiSub,
     tip:"Valor API generado ÷ coste de la suscripción. Cuántas veces recuperas la cuota."},
    {lab:"Coste por sesión",val:money(ef.coste_por_sesion||0),
     sub:`${D.totales.sesiones} sesiones · ${D.totales.dias} días totales`,
     tip:"Coste API medio por sesión de Claude Code."},
    {lab:"Coste / día activo",val:money(ef.coste_por_dia_activo||0),
     sub:`${ef.dias_activos||0} días con actividad`,
     tip:"Coste API en los días en que realmente usaste Claude."},
    {lab:"Output por €",val:toks(Math.round((ef.output_por_dolar||0)/TASA))+"/€",
     sub:`ahorro caché ${(ef.ahorro_cache_pct||0).toFixed(1)}% del coste bruto`,
     tip:"Tokens de salida generados por cada euro de coste API."},
  ];
  el("roi_kpis").innerHTML=kpis.map(k=>`<div class="card kpi" title="${esc(k.tip||'')}">
    <div class="lab">${k.lab}</div>
    <div class="val ${k.cls||""}">${k.val}</div>
    <div class="sub">${k.sub}</div></div>`).join("");
})();

(function(){ /* mes en curso + proyección (sin presupuesto) */
  const B=D.presupuesto||{};
  el("budget_box").innerHTML=`<div class="grid kpis" style="margin:0">
    <div class="kpi"><div class="lab">Gastado este mes</div><div class="val">${money(B.gasto_mes||0)}</div>
      <div class="sub">${esc(B.mes||"")} · día ${B.dia_mes||0} de ${B.dias_mes||0}</div></div>
    <div class="kpi"><div class="lab">Media diaria</div><div class="val">${money(B.media_diaria||0)}</div>
      <div class="sub">sobre los ${B.dia_mes||0} días corridos</div></div>
    <div class="kpi"><div class="lab">Proyección fin de mes</div><div class="val">${money(B.proyeccion||0)}</div>
      <div class="sub">si sigue este ritmo</div></div>
  </div>`;
})();

(function(){ /* suscripción vs API */
  const sub=D.subscripcion, planes=Object.keys(sub.planes_mes);
  const PLAN_ACTUAL=(PAYLOAD.precios&&PAYLOAD.precios.plan_actual)||"";
  const series=[{key:"api",color:"#6ea8fe",label:"API (uso real)"}]
    .concat(planes.map((p,i)=>({key:p,color:["#a855f7","#f59e0b","#ef4444"][i%3],label:p})));
  const rows=sub.by_month.map(m=>{const v={api:m.api};planes.forEach(p=>v[p]=sub.planes_mes[p]);return{label:m.mes,vals:v};});
  el("chart_subs").innerHTML=grouped(rows,series,{h:280,bw:14})+
    `<div class="legend">`+series.map(s=>`<span class="it"><span class="sw" style="background:${s.color}"></span>${s.label}${s.key===PLAN_ACTUAL?' <span class="tag ok" style="padding:1px 6px">tu plan</span>':''}</span>`).join("")+`</div>`;
  let rec=sub.mejor_opcion.nombre.startsWith("API")
    ?`A tarifas de API pagarías <b>${money(sub.api_total)}</b> en ${sub.n_meses} mes(es). Eso es menos que cualquier plan de suscripción en ese periodo, así que <b>el pago por uso sale a cuenta</b>.`
    :`La suscripción <b>${esc(sub.mejor_opcion.nombre)}</b> (${money(sub.mejor_opcion.coste)} en ${sub.n_meses} mes/es) es la opción más barata frente a pagar la API (<b>${money(sub.api_total)}</b>).`;
  if(PLAN_ACTUAL && sub.planes_totales[PLAN_ACTUAL]!=null){
    const pt=sub.planes_totales[PLAN_ACTUAL], dif=sub.api_total-pt;
    rec+=`<br><b>Tu plan actual (${esc(PLAN_ACTUAL)})</b>: ${money(sub.planes_mes[PLAN_ACTUAL])}/mes → ${money(pt)} en ${sub.n_meses} mes(es). `+
      (dif>=0?`A tarifas API habrías pagado ${money(sub.api_total)}: lo amortizas con creces (${money(dif)} de valor por encima de la cuota).`
             :`La API te habría salido ${money(sub.api_total)}, ${money(-dif)} más barata que tu plan.`);
  }
  let tabla=`<table style="margin-top:12px"><thead><tr><th>Opción</th><th>Coste ${sub.n_meses} mes(es)</th><th>vs API</th></tr></thead><tbody>`;
  tabla+=`<tr><td>API (uso real)</td><td>${money(sub.api_total)}</td><td>—</td></tr>`;
  planes.forEach(p=>{const t=sub.planes_totales[p],dif=sub.api_total-t,cur=p===PLAN_ACTUAL;
    tabla+=`<tr${cur?' style="background:#162236"':''}><td>${esc(p)} (${money(sub.planes_mes[p])}/mes)${cur?' <span class="tag ok">tu plan</span>':''}</td><td>${money(t)}</td>
      <td style="color:${dif>=0?"#86efac":"#fca5a5"}">${dif>=0?"plan ahorra ":"API ahorra "}${money(Math.abs(dif))}</td></tr>`;});
  tabla+=`</tbody></table>`;
  if(D.limites.limite_uso>0) rec+=` <span style="color:#fca5a5">Ojo: alcanzaste el límite de sesión <b>${D.limites.limite_uso}</b> veces — la opción más barata por precio puede no tener bastante margen de uso; un plan superior daría más holgura aunque cueste más.</span>`;
  el("subs_verdict").innerHTML=`<div class="verdict">${rec}</div>`+tabla+
    `<p class="section-note">Nota: el coste API es el contrafactual "si hubieras pagado por token". La suscripción es tarifa plana con límites de uso. Comparado sobre los ${sub.n_meses} mes(es) con actividad. Importes en € (tasa ${TASA.toFixed(2)} €/$).</p>`;
})();

/* ===================== TAB: ACTIVIDAD ===================== */

(function(){ /* tokens en el tiempo (día/semana/mes · rango temporal) */
  const series=[{key:"input",label:"Entrada"},{key:"output",label:"Salida"},
    {key:"cache_read",label:"Caché lectura"},{key:"cache_write",label:"Caché escritura"}];
  const cmap={input:"#3b82f6",output:"#f59e0b",cache_read:"#10b981",cache_write:"#a855f7"};
  const sel=el("gran_tokens");
  function draw(){
    const bd=filtraByDay(D.by_day), gran=sel.value;
    const rows=agrupar(bd,gran).map(g=>({label:g.label,
      vals:{input:g.input,output:g.output,cache_read:g.cache_read,cache_write:g.cache_write}}));
    const opt=gran==="dia"?{h:300}:{h:300,bw:gran==="mes"?54:40,gap:gran==="mes"?20:14};
    el("chart_tokens").innerHTML=stacked(rows,series.map(s=>({...s,color:cmap[s.key]})),{...opt,fmt:toks,lab:v=>v>=1000?toks(v):""});
    el("periodo_tokens").innerHTML=resumenPeriodo(bd);
  }
  el("legend_tokens").innerHTML=series.map(s=>`<span class="it"><span class="sw" style="background:${cmap[s.key]}"></span>${s.label}</span>`).join("");
  sel.onchange=draw; RANGO_CBS.push(draw); draw();
})();

(function(){ /* tokens por modelo */
  const series=[{key:"input",label:"Entrada",color:"#3b82f6"},{key:"output",label:"Salida",color:"#f59e0b"},
    {key:"cache_read",label:"Caché lectura",color:"#10b981"},{key:"cache_write",label:"Caché escritura",color:"#a855f7"}];
  const conTok=D.by_model.map(m=>({...m,tk:m.input+m.output+m.cache_read+m.cache_write})).filter(m=>m.tk>0);
  const rows=conTok.map(m=>({label:m.etiqueta,vals:{input:m.input,output:m.output,cache_read:m.cache_read,cache_write:m.cache_write}}));
  el("chart_tok_model").innerHTML=stacked(rows,series,{h:300,bw:46,gap:28,fmt:toks,lab:v=>v>0?toks(v):""});
  el("legend_tok_model").innerHTML=series.map(s=>`<span class="it"><span class="sw" style="background:${s.color}"></span>${s.label}</span>`).join("");
  const totTok=D.totales.tokens_total||1;
  let t=`<thead><tr><th>Modelo</th><th>Tokens</th><th>% del total</th></tr></thead><tbody>`;
  conTok.slice().sort((a,b)=>b.tk-a.tk).forEach(m=>{ t+=`<tr>
    <td><span class="pill" style="background:${m.color}"></span>${esc(m.etiqueta)}</td>
    <td>${toks(m.tk)}</td><td>${(100*m.tk/totTok).toFixed(1)}%</td></tr>`; });
  t+=`<tr style="font-weight:700"><td>TOTAL</td><td>${toks(D.totales.tokens_total)}</td><td>100%</td></tr></tbody>`;
  el("tbl_tok_model").innerHTML=t;
})();

(function(){ /* proyectos */
  const items=D.by_project.map(p=>({label:p.proyecto,value:p.coste,color:"#6ea8fe",sub:`${p.sesiones} ses · ${toks(p.tokens)} tok`}));
  el("chart_proj").innerHTML=hbars(items,money);
})();


(function(){ /* tipos de actividad (donut) + resultados */
  const cats=D.by_categoria||[];
  if(!cats.length){ el("donut_cat").innerHTML=`<p class="mut">Sin datos de actividad.</p>`; }
  else{
    const tot=cats.reduce((s,c)=>s+c.coste,0);
    const items=cats.map(c=>({label:c.categoria,value:c.coste,color:CATCOL[c.categoria]||"#5d6b88"}));
    el("donut_cat").innerHTML=donut(items,{big:money(tot),small:"coste por tipo"});
    el("legend_cat").innerHTML=cats.map(c=>`<span class="it"><span class="sw" style="background:${CATCOL[c.categoria]||"#5d6b88"}"></span>${esc(c.categoria)} · ${money(c.coste)} <span class="mut">(${c.sesiones} ses)</span></span>`).join("");
  }
  const O=D.outcomes||{}, cd=O.con_dato||0, cc=O.conteo||{};
  if(cd>0){
    const p=k=>(100*(cc[k]||0)/cd).toFixed(0);
    el("cat_outcomes").innerHTML=`<span class="mut small">Resultado de las sesiones (de ${cd} con datos de facets): </span>`+
      `<span class="tag ok">${p("logrado")}% logrado</span> `+
      (cc.parcial?`<span class="tag warn">${p("parcial")}% parcial</span> `:"")+
      (cc.fallido?`<span class="tag bad">${p("fallido")}% fallido</span>`:"");
  }
})();

(function(){ /* herramientas más usadas */
  const H=D.herramientas||[];
  if(!H.length){ el("tools_box").innerHTML=`<p class="mut">Sin uso de herramientas detectado.</p>`; return; }
  const items=H.slice(0,12).map(t=>({label:t.nombre,value:t.veces,color:"#6ea8fe",sub:`${t.sesiones} ses`}));
  el("tools_box").innerHTML=hbars(items,v=>v.toLocaleString()+"×");
})();

(function(){ /* archivos más tocados */
  const A=D.archivos||[];
  if(!A.length){ el("tbl_archivos").innerHTML=`<tbody><tr><td class="mut" style="padding:14px">Sin datos de ficheros.</td></tr></tbody>`; return; }
  let h=`<thead><tr><th>Archivo</th><th>Lect.</th><th>Edic.</th><th>Escr.</th><th>Ses.</th><th title="Máximo de lecturas del mismo archivo en una sola sesión">Máx relec.</th></tr></thead><tbody>`;
  A.forEach(f=>{ const hot=f.max_relec>=10; const nm=f.archivo.length>32?f.archivo.slice(0,31)+"…":f.archivo;
    h+=`<tr><td style="text-align:left" title="${esc(f.archivo)}">${esc(nm)}</td>
      <td>${f.read||""}</td><td>${f.edit||""}</td><td>${f.write||""}</td><td>${f.sesiones}</td>
      <td style="${hot?"color:#fca5a5;font-weight:700":"color:var(--mut)"}">${f.max_relec||"—"}</td></tr>`; });
  el("tbl_archivos").innerHTML=h+`</tbody>`;
})();

(function(){ /* comandos de shell + relecturas intensas */
  const B=D.bash_top||[];
  el("bash_box").innerHTML=B.length
    ?hbars(B.map(b=>({label:b.cmd,value:b.veces,color:"#64748b"})),v=>v.toLocaleString()+"×")
    :`<p class="mut">Sin comandos de shell detectados.</p>`;
  const R=D.relecturas||[];
  if(R.length){
    el("relec_box").innerHTML=`<b style="font-size:12.5px;color:#cdd6e8">Relecturas intensas</b>
      <p class="section-note" style="margin:4px 0 7px">Mismo archivo leído muchas veces dentro de una sola sesión. Con prompt caching el coste se mitiga, pero suele indicar que conviene mantenerlo en contexto o dividirlo en piezas más pequeñas.</p>
      <ul class="reclist" style="margin-top:4px">${R.slice(0,6).map(f=>`<li><b>${esc(f.archivo)}</b> — hasta <b style="color:#fca5a5">${f.max_relec}×</b> en una sesión <span class="mut">(${f.read} lecturas en total)</span></li>`).join("")}</ul>`;
  }
})();

/* ===================== TAB: RECOMENDACIONES ===================== */

(function(){ /* rightsizing */
  const R=D.rightsizing||{};
  const mb=s=>eurize(esc(s).replace(/\*\*(.+?)\*\*/g,"<b>$1</b>"));
  const pctG=D.totales.coste?(100*(R.ahorro_total||0)/D.totales.coste):0;
  el("rs_kpis").innerHTML=[
    {lab:"Ahorro potencial",val:money(R.ahorro_total||0),cls:R.ahorro_total>0?"ok":"",sub:pctG.toFixed(0)+"% del gasto total"},
    {lab:"Sesiones candidatas",val:R.n||0,sub:"ligeras corridas en premium"},
    {lab:"→ a Haiku 4.5",val:money(R.ahorro_haiku||0),sub:"tareas muy ligeras"},
    {lab:"→ a Sonnet 4.6",val:money(R.ahorro_sonnet||0),sub:"complejidad media"},
  ].map(k=>`<div class="card kpi"><div class="lab">${k.lab}</div><div class="val ${k.cls||""}">${k.val}</div><div class="sub">${k.sub}</div></div>`).join("");

  el("rs_guide").innerHTML=`<b style="font-size:14px">Guía rápida: qué modelo para qué <span class="mut" style="font-weight:400;font-size:11px">(tarifas USD/1M tok)</span></b>
    <div class="kv" style="margin-top:10px;grid-template-columns:auto 1fr;gap:9px 14px">
      <span class="k"><span class="pill" style="background:#10b981"></span>Haiku 4.5 <span class="mut">$1/$5</span></span><span>Lecturas, ediciones puntuales, clasificación, formato, extracción simple, subagentes de búsqueda.</span>
      <span class="k"><span class="pill" style="background:#3b82f6"></span>Sonnet 4.6 <span class="mut">$3/$15</span></span><span>Refactors, resúmenes, tareas de volumen, complejidad media.</span>
      <span class="k"><span class="pill" style="background:#f59e0b"></span>Opus 4.8 <span class="mut">$5/$25</span></span><span>Trabajo agéntico largo, depuración difícil, diseño/arquitectura.</span>
      <span class="k"><span class="pill" style="background:#a855f7"></span>Fable 5 <span class="mut">$10/$50</span></span><span>Máxima capacidad — solo cuando Opus se queda corto.</span>
    </div>`;

  el("rs_recs").innerHTML=`<b style="font-size:14px">Qué cambiar</b>
    <ul class="reclist">${(R.recs||[]).map(r=>`<li>${mb(r)}</li>`).join("")}</ul>`;

  if((R.candidatas||[]).length){
    let h=`<thead><tr><th>Inicio</th><th>Proyecto</th><th>Modelo actual</th><th>Coste</th><th>Sugerido</th><th>Coste est.</th><th>Ahorro</th><th>Tarea</th></tr></thead><tbody>`;
    R.candidatas.forEach(c=>{ h+=`<tr>
      <td>${esc((c.inicio||"").slice(0,16).replace("T"," "))}</td>
      <td>${esc(c.proyecto||"")}</td>
      <td><span class="pill" style="background:${COL[c.modelo_actual]||"#888"}"></span>${esc(ELAB[c.modelo_actual]||c.modelo_actual||"")}</td>
      <td>${money(c.coste)}</td>
      <td><span class="pill" style="background:${COL[c.sugerido]||"#888"}"></span>${esc(ELAB[c.sugerido]||c.sugerido)}</td>
      <td>${money(c.coste_sugerido)}</td>
      <td style="color:#86efac">${money(c.ahorro)}</td>
      <td style="text-align:left;max-width:300px;overflow:hidden;text-overflow:ellipsis" title="${esc(c.tarea||"")}">${esc((c.tarea||"").slice(0,80))}</td>
    </tr>`; });
    el("rs_tbl").innerHTML=h+`</tbody>`;
  } else { el("rs_tblwrap").style.display="none"; }
  el("rs_note").textContent="Estimación heurística. Criterio: "+(R.criterios||"");
})();

(function(){ /* ajuste por tipo de actividad */
  const A=D.ajuste_actividad||{}; const cats=A.categorias||[];
  const mb=s=>eurize(esc(s).replace(/\*\*(.+?)\*\*/g,"<b>$1</b>"));
  const pctG=D.totales.coste?(100*(A.ahorro_total||0)/D.totales.coste):0;
  el("aj_kpis").innerHTML=[
    {lab:"Ahorro por actividad",val:money(A.ahorro_total||0),cls:A.ahorro_total>0?"ok":"",sub:pctG.toFixed(0)+"% del gasto total"},
    {lab:"Categorías con margen",val:cats.length,sub:"tipos de tarea mal asignados"},
    {lab:"vs rightsizing por longitud",val:money((D.rightsizing||{}).ahorro_total||0),
       sub:"lo que ve el criterio antiguo",
       tip:"El método por longitud solo ve sesiones cortas; este ve también las largas pero mecánicas."},
  ].map(k=>`<div class="card kpi" title="${esc(k.tip||'')}"><div class="lab">${k.lab}</div>
    <div class="val ${k.cls||""}">${k.val}</div><div class="sub">${k.sub}</div></div>`).join("");

  el("aj_recs").innerHTML=`<b style="font-size:14px">Qué reasignar</b>
    <ul class="reclist">${(A.recs||[]).map(r=>`<li>${mb(r)}</li>`).join("")}</ul>`;

  if(cats.length){
    let h=`<thead><tr><th>Tipo de actividad</th><th>Sesiones</th><th>Modelo actual</th><th>Coste actual</th>
      <th>Modelo sugerido</th><th>Coste est.</th><th>Ahorro</th></tr></thead><tbody>`;
    cats.forEach(c=>{ h+=`<tr>
      <td style="text-align:left">${catTag(c.categoria)}</td>
      <td>${c.sesiones}</td>
      <td><span class="pill" style="background:#f59e0b"></span>Opus/Fable</td>
      <td>${money(c.coste_actual)}</td>
      <td><span class="pill" style="background:${COL[c.modelo_sugerido]||"#888"}"></span>${esc(c.etiqueta_sugerido||c.modelo_sugerido)}</td>
      <td>${money(c.coste_estimado)}</td>
      <td style="color:#86efac"><b>${money(c.ahorro)}</b></td>
    </tr>`; });
    el("aj_tbl").innerHTML=h+`</tbody>`;
  } else { el("aj_tblwrap").style.display="none"; }
  el("aj_note").textContent="Criterio: "+(A.criterios||"")+" El mapa categoría→modelo es editable en analizar.py (TECHO_ACTIVIDAD).";
})();

(function(){ /* auto-mejora */
  const I=M, d=I.deltas;
  function delta(v){ if(v===0||v==null) return `<span class="delta flat">±0</span>`;
    const cls=v>0?"up":"down"; return `<span class="delta ${cls}">${v>0?"+":""}${typeof v==="number"&&!Number.isInteger(v)?v.toFixed(4):v}</span>`; }
  let dh=d?`<div class="kv">
      <span class="k">Δ Coste</span><span>${delta(d.coste)}</span>
      <span class="k">Δ Sesiones</span><span>${delta(d.sesiones)}</span>
      <span class="k">Δ Requests</span><span>${delta(d.requests)}</span>
      <span class="k">Δ Límites</span><span>${delta(d.limites)}</span>
      <span class="k">Desde</span><span class="mut">${esc((d.desde||"").slice(0,16).replace("T"," "))}</span>
    </div>`:`<p class="mut">Primera ejecución: no hay con qué comparar todavía. La próxima vez verás los deltas.</p>`;
  const H=I.historial||[]; let spark="";
  if(H.length>1){ const w=260,h=46,max=Math.max(...H.map(x=>x.coste||0))||1;
    const pts=H.map((x,i)=>`${(i/(H.length-1)*w).toFixed(1)},${(h-(x.coste||0)/max*h).toFixed(1)}`).join(" ");
    spark=`<svg viewBox="0 0 ${w} ${h}" width="100%" height="${h}" style="margin-top:8px"><polyline points="${pts}" fill="none" stroke="#6ea8fe" stroke-width="2"/></svg>
      <div class="mut small">coste por ejecución (${H.length} registradas)</div>`; }
  let inc=I.incremental;
  el("improve_box").innerHTML=`
    <div style="display:flex;justify-content:space-between;align-items:baseline">
      <div><b style="font-size:17px">Auto-mejora</b></div>
      <div class="mut small">${inc.transcripts_total} transcripts · ${inc.nuevos} nuevos · ${inc.cambiados} cambiados</div>
    </div>
    ${dh}${spark}
    <h2 style="margin:16px 0 8px;font-size:13px">Recomendaciones</h2>
    <ul class="reclist">${I.recomendaciones.map(r=>`<li>${eurize(esc(r))}</li>`).join("")}</ul>`;
})();

(function(){ /* memoria */
  const mem=M.memoria||{}, mc=MC||{};
  const unk=Object.keys(M.modelos_desconocidos||{});
  el("memory_box").innerHTML=`
    <b style="font-size:14px">Memoria acumulada del panel</b>
    <p class="section-note">Se guarda en <code>panel_costes/estado/</code> y se refina cada ejecución (nunca se escribe en ~/.claude).</p>
    <div class="kv">
      <span class="k">Proyecto top</span><span>${esc(mem.proyecto_top||"—")}</span>
      <span class="k">Modelo dominante</span><span>${esc(mem.modelo_dominante||"—")}</span>
      <span class="k">Hora pico</span><span>${esc(mem.hora_pico||"—")}</span>
      <span class="k">Ratio caché</span><span>${pct(mem.ratio_cache||0)}</span>
      <span class="k">Proyectos vistos</span><span>${(mem.proyectos_vistos||[]).length}</span>
      <span class="k">Modelos vistos</span><span>${esc((mem.modelos_vistos||[]).join(", "))}</span>
    </div>
    <hr style="border:0;border-top:1px solid var(--line);margin:14px 0">
    <b style="font-size:13px">Memoria de Claude Code</b>
    <div class="kv" style="margin-top:6px">
      <span class="k">Directorios memory/</span><span>${mc.directorios||0}</span>
      <span class="k">Entradas</span><span>${mc.entradas||0} ${!mc.entradas?"<span class=\"tag warn\">vacía</span>":""}</span>
    </div>
    ${unk.length?`<p class="section-note" style="color:#fca5a5;margin-top:12px">Modelos sin tarifa (añádelos a precios.json): ${esc(unk.join(", "))}</p>`:""}`;
})();

(function(){ /* skills */
  if(!D.skills.length){ el("skills_box").innerHTML=`<p class="mut">No se detectaron invocaciones de skills.</p>`; return; }
  const items=D.skills.map(s=>({label:s.nombre,value:s.veces,color:"#a855f7",sub:`${s.sesiones} ses`}));
  el("skills_box").innerHTML=hbars(items,v=>v+"×");
})();

/* ===================== TAB: PRODUCTIVIDAD ===================== */

(function(){ /* código generado por día (git_commits, lineas_mas, lineas_menos) */
  const byDay={};
  D.sesiones.forEach(s=>{
    if(!s.inicio) return;
    const dia=s.inicio.slice(0,10);
    if(!byDay[dia]) byDay[dia]={commits:0,add:0,del:0};
    byDay[dia].commits+=(s.git_commits||0);
    byDay[dia].add+=(s.lineas_mas||0);
    byDay[dia].del+=(s.lineas_menos||0);
  });
  const dias=Object.keys(byDay).sort();
  if(!dias.length){
    el("chart_git_day").innerHTML=`<p class="mut" style="padding:16px">Sin datos de git en los transcripts. Se obtienen de <code>usage-data/session-meta/</code> cuando Claude Code los registra.</p>`;
    return;
  }
  const maxAll=Math.max(1,...dias.map(d=>Math.max(byDay[d].add,byDay[d].del)));
  const bw=16,gap=6,padL=52,padR=14,padT=14,padB=52;
  const W=Math.max(620,padL+padR+dias.length*(bw*2+gap+4));
  const H=220,ih=H-padT-padB;
  let g=`<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">`;
  for(let i=0;i<=4;i++){const v=maxAll*i/4,yy=padT+ih-(v/maxAll)*ih;
    g+=`<line x1="${padL}" y1="${yy}" x2="${W-padR}" y2="${yy}" stroke="#1d2740"/>`;
    g+=`<text x="${padL-5}" y="${yy+3}" fill="#5d6b88" font-size="10" text-anchor="end">${v>=1000?(v/1000).toFixed(1)+"k":Math.round(v)}</text>`;}
  dias.forEach((dia,i)=>{
    const d=byDay[dia], x=padL+i*(bw*2+gap+4);
    if(d.add>0){const hh=(d.add/maxAll)*ih;g+=`<rect x="${x}" y="${padT+ih-hh}" width="${bw}" height="${hh}" fill="#10b981" rx="1.5"><title>${dia}: +${d.add} líneas</title></rect>`;}
    if(d.del>0){const hh=(d.del/maxAll)*ih;g+=`<rect x="${x+bw+2}" y="${padT+ih-hh}" width="${bw}" height="${hh}" fill="#ef4444" rx="1.5"><title>${dia}: -${d.del} líneas</title></rect>`;}
    if(d.commits>0){const lx=x+bw;g+=`<text x="${lx}" y="${padT+ih-5}" fill="#f59e0b" font-size="8" text-anchor="middle" font-weight="700">${d.commits}c</text>`;}
    const lx=x+bw,ly=H-padB+14;
    g+=`<text x="${lx}" y="${ly}" fill="#7c8aa8" font-size="9" text-anchor="end" transform="rotate(-45 ${lx} ${ly})">${dia.slice(5)}</text>`;
  });
  g+=`</svg>`;
  const legend=`<div class="legend" style="margin-top:6px">
    <span class="it"><span class="sw" style="background:#10b981"></span>Líneas añadidas</span>
    <span class="it"><span class="sw" style="background:#ef4444"></span>Líneas eliminadas</span>
    <span class="it" style="color:#f59e0b">● Commits (etiqueta)</span></div>`;
  el("chart_git_day").innerHTML=g+legend;
})();

(function(){ /* outcomes por semana */
  const byWeek={};
  D.sesiones.forEach(s=>{
    if(!s.inicio) return;
    const dt=new Date(s.inicio); const dow=(dt.getUTCDay()+6)%7;
    dt.setUTCDate(dt.getUTCDate()-dow); const wk=dt.toISOString().slice(0,10);
    if(!byWeek[wk]) byWeek[wk]={logrado:0,parcial:0,fallido:0,otro:0};
    const r=s.resultado||"";
    if(/achiev|success|complet/i.test(r)) byWeek[wk].logrado++;
    else if(/partial|parcial/i.test(r)) byWeek[wk].parcial++;
    else if(/fail|abandon|not_/i.test(r)) byWeek[wk].fallido++;
    else byWeek[wk].otro++;
  });
  const semanas=Object.keys(byWeek).sort();
  if(!semanas.length){
    el("chart_outcomes_week").innerHTML=`<p class="mut" style="padding:16px">Sin datos de outcome. Se obtienen de <code>usage-data/facets/</code> cuando Claude Code los registra.</p>`;
    return;
  }
  const series=[{key:"logrado",color:"#22c55e",label:"Logrado"},{key:"parcial",color:"#f59e0b",label:"Parcial"},
    {key:"fallido",color:"#ef4444",label:"Fallido"},{key:"otro",color:"#5d6b88",label:"Sin dato"}];
  const rows=semanas.map(wk=>({label:wk.slice(5),vals:byWeek[wk]}));
  el("chart_outcomes_week").innerHTML=stacked(rows,series,{h:220,bw:32,gap:14,fmt:v=>v.toFixed(0),lab:v=>v>0?v:""})+
    `<div class="legend" style="margin-top:6px">`+series.map(s=>`<span class="it"><span class="sw" style="background:${s.color}"></span>${s.label}</span>`).join("")+`</div>`;
})();

(function(){ /* distribución de lenguajes de programación */
  const langs={};
  D.sesiones.forEach(s=>Object.entries(s.languages||{}).forEach(([l,c])=>langs[l]=(langs[l]||0)+c));
  const items=Object.entries(langs).sort((a,b)=>b[1]-a[1]).slice(0,10);
  if(!items.length){ el("donut_langs").innerHTML=`<p class="mut" style="padding:10px">Sin datos de lenguajes.</p>`; return; }
  const LCOL={"Python":"#3572A5","JavaScript":"#f1e05a","TypeScript":"#2b7489","HTML":"#e34c26",
    "CSS":"#563d7c","Shell":"#89e051","Go":"#00ADD8","Rust":"#dea584","Java":"#b07219",
    "C":"#555555","C++":"#f34b7d","Ruby":"#701516","PHP":"#4F5D95","Kotlin":"#A97BFF","Markdown":"#083fa1"};
  const tot=items.reduce((s,[,c])=>s+c,0);
  const donItems=items.map(([l,c])=>({label:l,value:c,color:LCOL[l]||"#6ea8fe"}));
  el("donut_langs").innerHTML=donut(donItems,{big:items.length+"",small:"lenguajes"});
  el("legend_langs").innerHTML=items.map(([l,c])=>`<span class="it"><span class="sw" style="background:${LCOL[l]||"#6ea8fe"}"></span>${esc(l)} <span class="mut">${(100*c/tot).toFixed(0)}%</span></span>`).join("");
})();

(function(){ /* tipos de sesión */
  const tipos={};
  D.sesiones.forEach(s=>{
    let t=s.tipo_sesion||"desconocido";
    if(s.subagente) t="subagente";
    tipos[t]=(tipos[t]||0)+1;
  });
  const TCOL={"interactive":"#3b82f6","orchestrated":"#8b5cf6","subagente":"#f59e0b",
    "multi_task":"#10b981","iterative_refinement":"#06b6d4","single_task":"#6366f1",
    "desconocido":"#475569"};
  const TLAB={"interactive":"Interactivo","orchestrated":"Orquestado","subagente":"Subagente",
    "multi_task":"Multi-tarea","iterative_refinement":"Refinamiento iterativo","single_task":"Tarea única",
    "desconocido":"Desconocido"};
  const items=Object.entries(tipos).sort((a,b)=>b[1]-a[1]);
  if(!items.length){ el("donut_tipo_ses").innerHTML=`<p class="mut" style="padding:10px">Sin datos de tipo de sesión.</p>`; return; }
  const tot=items.reduce((s,[,c])=>s+c,0);
  const donItems=items.map(([k,c])=>({label:TLAB[k]||k,value:c,color:TCOL[k]||"#6ea8fe"}));
  el("donut_tipo_ses").innerHTML=donut(donItems,{big:tot+"",small:"sesiones"});
  el("legend_tipo_ses").innerHTML=items.map(([k,c])=>`<span class="it"><span class="sw" style="background:${TCOL[k]||"#6ea8fe"}"></span>${esc(TLAB[k]||k)} <span class="mut">${(100*c/tot).toFixed(0)}%</span></span>`).join("");
})();

(function(){ /* histograma de duración */
  const buckets=[{max:5,label:"0–5 min"},{max:15,label:"5–15 min"},{max:30,label:"15–30 min"},
    {max:60,label:"30–60 min"},{max:Infinity,label:">60 min"}];
  const cnt=buckets.map(()=>0); let total=0;
  D.sesiones.forEach(s=>{ if(s.duracion_min==null) return; total++;
    const i=buckets.findIndex(b=>s.duracion_min<b.max); if(i>=0) cnt[i]++; });
  if(!total){ el("chart_dur_hist").innerHTML=`<p class="mut" style="padding:16px">Sin datos de duración disponibles.</p>`; return; }
  const items=buckets.map((b,i)=>({label:b.label,value:cnt[i],color:"#6ea8fe",sub:cnt[i]+" sesiones"}));
  el("chart_dur_hist").innerHTML=hbars(items,v=>v+" sesiones");
})();

(function(){ /* tasks por proyecto */
  const T=D.tasks||{};
  const projs=Object.keys(T);
  if(!projs.length){ el("tasks_box").innerHTML=`<p class="mut">Sin tasks en <code>~/.claude/tasks/</code>.</p>`; return; }
  const series=[{key:"completed",color:"#22c55e",label:"Completadas"},{key:"in_progress",color:"#f59e0b",label:"En curso"},{key:"archived",color:"#5d6b88",label:"Archivadas"}];
  const rows=projs.map(p=>({label:p.length>20?p.slice(0,19)+"…":p,vals:{completed:T[p].completed||0,in_progress:T[p].in_progress||0,archived:T[p].archived||0}}));
  el("tasks_box").innerHTML=stacked(rows,series,{h:220,bw:36,gap:20,fmt:v=>v.toFixed(0),lab:v=>v>0?v:""})+
    `<div class="legend" style="margin-top:6px">`+series.map(s=>`<span class="it"><span class="sw" style="background:${s.color}"></span>${s.label}</span>`).join("")+`</div>`;
})();

/* ===================== TAB: SESIONES ===================== */

(function(){
  const proj=el("f_proj"), txt=el("f_text"), fcat=el("f_cat");
  const projs=[...new Set(D.sesiones.map(s=>s.proyecto))].sort();
  proj.innerHTML=`<option value="">Todos los proyectos (${D.sesiones.length})</option>`+
    projs.map(p=>`<option value="${esc(p)}">${esc(p)}</option>`).join("");
  const cats=[...new Set(D.sesiones.map(s=>s.categoria).filter(Boolean))].sort();
  fcat.innerHTML=`<option value="">Todos los tipos</option>`+
    cats.map(c=>`<option value="${esc(c)}">${esc(c)}</option>`).join("");
  let current=D.sesiones;
  function badge(out){ if(!out) return ""; const ok=/achiev|success|complet/i.test(out), bad=/fail|abandon|not_/i.test(out);
    return `<span class="tag ${ok?"ok":bad?"bad":"warn"}">${esc(out.replace(/_/g," "))}</span>`; }
  function tools(t){ return Object.entries(t||{}).sort((a,b)=>b[1]-a[1]).slice(0,3).map(([k,v])=>`${k}:${v}`).join(" "); }
  function langs(l){ return Object.keys(l||{}).slice(0,3).join(", "); }
  function render(){
    const fp=proj.value, ft=(txt.value||"").toLowerCase(), fc=fcat.value;
    const rows=D.sesiones.filter(s=>(!fp||s.proyecto===fp)&&(!fc||s.categoria===fc)&&
      (!ft||((s.primer_prompt||"")+" "+(s.objetivo||"")).toLowerCase().includes(ft)));
    current=rows;
    el("sess_count").textContent=`${rows.length} sesiones · ${money(rows.reduce((a,s)=>a+s.coste,0))}`;
    let h=`<thead><tr><th>Inicio</th><th>Proyecto</th><th>Tipo</th><th>Coste</th><th>Llam.</th><th>Modelo</th><th>Dur(min)</th>
      <th>Tokens</th><th>Tools</th><th>Lang</th><th>Git</th><th>Resultado</th><th>Prompt / objetivo</th></tr></thead><tbody>`;
    rows.slice(0,400).forEach(s=>{ const tk=s.input+s.output+s.cache_read+s.cache_write;
      const git=(s.git_commits||0)+"c/"+(s.git_pushes||0)+"p";
      h+=`<tr>
        <td>${esc((s.inicio||"").slice(0,16).replace("T"," "))}${s.subagente?" <span class=\"tag\">sub</span>":""}</td>
        <td>${esc(s.proyecto||"")}</td>
        <td style="text-align:left">${catTag(s.categoria)}</td>
        <td><b>${money(s.coste)}</b></td>
        <td>${s.requests}</td>
        <td><span class="pill" style="background:${COL[s.modelo_top]||"#888"}"></span>${esc(ELAB[s.modelo_top]||s.modelo_top||"")}</td>
        <td>${s.duracion_min!=null?s.duracion_min:"—"}</td>
        <td>${toks(tk)}</td>
        <td class="mut small" style="text-align:left">${esc(tools(s.tools))}</td>
        <td class="mut small" style="text-align:left">${esc(langs(s.languages))}</td>
        <td class="mut small">${esc(git)}</td>
        <td style="text-align:left">${badge(s.resultado)}</td>
        <td style="text-align:left;max-width:340px;overflow:hidden;text-overflow:ellipsis" title="${esc(s.objetivo||s.primer_prompt||"")}">${esc((s.objetivo||s.primer_prompt||"").slice(0,90))}</td>
      </tr>`; });
    el("tbl_sess").innerHTML=h+`</tbody>`;
  }
  proj.onchange=render; fcat.onchange=render; txt.oninput=render; render();

  el("btn_csv").addEventListener("click",()=>{
    const cols=[["inicio","Inicio"],["fin","Fin"],["proyecto","Proyecto"],["categoria","Tipo"],
      ["modelo_top","Modelo"],["coste","Coste USD"],["requests","Llamadas"],
      ["input","Input"],["output","Output"],["cache_read","CacheRead"],["cache_write","CacheWrite"],
      ["duracion_min","Duracion_min"],["resultado","Resultado"],["__obj","Objetivo/Prompt"]];
    const val=(s,k)=> k==="__obj" ? (s.objetivo||s.primer_prompt||"") : (s[k]==null?"":s[k]);
    const q=v=>{ v=(""+v).replace(/\r?\n/g," "); return /[",;]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v; };
    let csv="﻿"+cols.map(c=>c[1]).join(",")+"\n";
    current.forEach(s=>{ csv+=cols.map(c=>q(val(s,c[0]))).join(",")+"\n"; });
    const blob=new Blob([csv],{type:"text/csv;charset=utf-8"});
    const a=document.createElement("a"); a.href=URL.createObjectURL(blob);
    a.download="sesiones_claude.csv"; document.body.appendChild(a); a.click();
    setTimeout(()=>{ URL.revokeObjectURL(a.href); a.remove(); },500);
  });
})();

/* ===================== CACHÉ Y LÍMITES (pestaña Recomendaciones) ===================== */

(function(){ /* caché */
  const c=D.cache, ratio=c.ratio_lectura;
  el("cache_box").innerHTML=`
    <div class="kv">
      <span class="k">Tokens leídos de caché</span><span>${toks(c.read_tokens)} <span class="mut">(coste ${money(c.coste_lectura)})</span></span>
      <span class="k">Tokens escritos en caché</span><span>${toks(c.write_tokens)} <span class="mut">(coste ${money(c.coste_escritura)})</span></span>
      <span class="k">Ratio de lectura</span><span>${pct(ratio)} de la entrada total</span>
      <span class="k">Ahorro estimado</span><span style="color:#86efac">${money(c.ahorro_estimado)}</span>
    </div>
    <div class="barwrap" style="margin-top:14px;height:14px"><i style="width:${Math.min(100,ratio)}%;background:linear-gradient(90deg,#10b981,#34d399)"></i></div>
    <p class="section-note">La lectura de caché cuesta 0,1× la tarifa de entrada; sin caché esos ${toks(c.read_tokens)} tokens se pagarían a precio pleno. De ahí el ahorro estimado.</p>`;
})();

(function(){ /* límites */
  const L=D.limites; const cats=L.categorias||{};
  const rows=Object.keys(L.por_dia).sort().map(d=>({label:d.slice(5),vals:{n:L.por_dia[d]}}));
  const chart=rows.length?stacked(rows,[{key:"n",color:"#ef4444",label:"eventos"}],{h:170,fmt:v=>v.toFixed(0),lab:v=>v}):
    `<p class="mut">Sin eventos de límite de alta confianza. 🎉</p>`;
  let evhtml="";
  (L.eventos||[]).slice(0,8).forEach(e=>{ evhtml+=`<tr><td>${esc((e.ts||"").slice(0,16).replace("T"," "))}</td>
    <td><span class="tag bad">${esc(e.categoria)}</span></td><td style="text-align:left">${esc(e.proyecto||"")}</td></tr>`; });
  el("limits_box").innerHTML=`
    <div class="kv" style="margin-bottom:8px">
      <span class="k">Límites de uso/sesión</span><span><b style="color:#ff8a8a">${L.limite_uso}</b> veces ("hit your session limit")</span>
      <span class="k">Errores de API (total)</span><span>${L.alta_confianza}</span>
      <span class="k">Por categoría</span><span>${Object.keys(cats).length?Object.entries(cats).map(([k,v])=>`${esc(k)}: ${v}`).join(" · "):"—"}</span>
      <span class="k">Menciones en contenido</span><span>${L.menciones_contenido} <span class="mut">(orientativo)</span></span>
    </div>${chart}
    ${evhtml?`<table style="margin-top:10px"><thead><tr><th>Cuándo</th><th>Tipo</th><th>Proyecto</th></tr></thead><tbody>${evhtml}</tbody></table>`:""}`;
})();

/* ===================== EDITOR DE PRECIOS ===================== */
(function(){
  const P = PAYLOAD.precios || {};
  const modelos = P.modelos || {};
  const subs = P.suscripciones_usd_mes || {};
  const viaHTTP = location.protocol.startsWith("http");

  /* ---- tabla de modelos ---- */
  let mRows="";
  Object.entries(modelos).filter(([k])=>k!=="synthetic").forEach(([key,m])=>{
    mRows+=`<tr>
      <td><span class="pill" style="background:${m.color||"#888"}"></span>${esc(m.etiqueta||key)}</td>
      <td><input type="number" step="0.01" min="0" class="model-in" data-model="${esc(key)}" value="${m.input||0}" ${viaHTTP?"":"readonly"}></td>
      <td><input type="number" step="0.01" min="0" class="model-out" data-model="${esc(key)}" value="${m.output||0}" ${viaHTTP?"":"readonly"}></td>
    </tr>`;
  });

  /* ---- tabla de planes ---- */
  let sRows="";
  Object.entries(subs).forEach(([name,price])=>{
    sRows+=`<tr>
      <td>${esc(name)}</td>
      <td><input type="number" step="1" min="0" class="sub-price" data-plan="${esc(name)}" value="${price}" ${viaHTTP?"":"readonly"}></td>
    </tr>`;
  });

  const wsearch = P.web_search_por_1000||10;
  const eurVal = P.eur_por_usd||1;
  const planActual = P.plan_actual||"";
  const planOpts = ['<option value="">— ninguno (API) —</option>'].concat(
    Object.keys(subs).map(n=>`<option value="${esc(n)}" ${n===planActual?"selected":""}>${esc(n)}</option>`)).join("");

  el("precios_editor").innerHTML=`
    <div style="display:grid;grid-template-columns:1.1fr 1fr;gap:24px;align-items:start">
      <div>
        <b style="font-size:13px;color:#cdd6e8">Modelos API (USD por 1M tokens)</b>
        <table class="precio-tbl" style="margin-top:8px">
          <thead><tr><th>Modelo</th><th>Input</th><th>Output</th></tr></thead>
          <tbody>${mRows}</tbody>
        </table>
        <div style="margin-top:12px;display:flex;align-items:center;gap:10px;font-size:12.5px">
          <span class="mut">Web search (USD / 1000 búsquedas)</span>
          <input type="number" step="0.01" min="0" id="wsearch_val" value="${wsearch}" ${viaHTTP?"":"readonly"} style="width:80px">
        </div>
        <p class="precios-note">Fuente original: ${esc((P._meta||{}).fuente||"—")} · ${esc((P._meta||{}).vigente_desde||"")}</p>
      </div>
      <div>
        <b style="font-size:13px;color:#cdd6e8">Planes de suscripción (USD/mes)</b>
        <table class="precio-tbl" style="margin-top:8px">
          <thead><tr><th>Plan</th><th>$/mes</th></tr></thead>
          <tbody>${sRows}</tbody>
        </table>
        <p class="precios-note">Precios a facturación anual (ajusta si pagas mensual).</p>
        <div style="margin-top:14px;display:flex;align-items:center;gap:10px;font-size:12.5px;flex-wrap:wrap">
          <span class="mut">Importes en € · tasa €/$</span>
          <input type="number" step="0.01" min="0" id="eur_val" value="${eurVal}" ${viaHTTP?"":"readonly"} style="width:80px">
        </div>
        <div style="margin-top:10px;display:flex;align-items:center;gap:10px;font-size:12.5px;flex-wrap:wrap">
          <span class="mut">Tu plan actual (se marca en la comparativa)</span>
          <select id="plan_val" ${viaHTTP?"":"disabled"}>${planOpts}</select>
        </div>
        ${!viaHTTP?`<p class="precios-note" style="color:#fde68a;margin-top:8px">⚠ Edición solo disponible desde el servidor local (<code>python3 servidor.py</code>).</p>`:""}
      </div>
    </div>`;

  if(!viaHTTP){
    el("btn_save_precios").disabled=true;
    el("btn_save_precios").title="Requiere el servidor local";
    return;
  }

  el("btn_save_precios").addEventListener("click", async ()=>{
    const btn=el("btn_save_precios"), status=el("precios_status");
    btn.disabled=true; btn.textContent="Guardando…"; status.textContent="";

    /* construir nuevo precios.json (deep copy + edits) */
    const nuevo=JSON.parse(JSON.stringify(P));

    document.querySelectorAll(".model-in").forEach(inp=>{
      const k=inp.dataset.model;
      if(nuevo.modelos[k]) nuevo.modelos[k].input=parseFloat(inp.value)||0;
    });
    document.querySelectorAll(".model-out").forEach(inp=>{
      const k=inp.dataset.model;
      if(nuevo.modelos[k]) nuevo.modelos[k].output=parseFloat(inp.value)||0;
    });
    document.querySelectorAll(".sub-price").forEach(inp=>{
      nuevo.suscripciones_usd_mes[inp.dataset.plan]=parseFloat(inp.value)||0;
    });
    nuevo.web_search_por_1000=parseFloat(el("wsearch_val").value)||10;
    nuevo.eur_por_usd=parseFloat(el("eur_val").value)||1;
    nuevo.plan_actual=el("plan_val").value||"";
    if(nuevo._meta) nuevo._meta.vigente_desde=new Date().toISOString().slice(0,10);

    try{
      const r=await fetch("/guardar-precios",{
        method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify(nuevo),cache:"no-store"
      });
      const j=await r.json();
      if(j.ok){
        status.style.color="#86efac";
        status.textContent="✓ Guardado y recalculado — "+esc(j.generado||"");
        setTimeout(()=>location.reload(),1400);
      } else {
        throw new Error(j.error||"error del servidor");
      }
    }catch(e){
      status.style.color="#fca5a5";
      status.textContent="✗ "+e.message;
      btn.disabled=false; btn.textContent="💾 Guardar y recalcular";
    }
  });
})();

/* ===================== FOOTER ===================== */
(function(){
  const pm=D.precios_meta||{};
  el("foot").innerHTML=`Tarifas usadas (USD por 1M tokens, ${esc(pm.vigente_desde||"")}): `+
    D.by_model.filter(m=>m.modelo!=="synthetic").map(m=>esc(m.etiqueta)).join(", ")+
    `. Caché: lectura 0,1× · escritura 5m 1,25× · escritura 1h 2,0× la tarifa de entrada. `+
    `Web search ${esc(String((pm.herramientas_servidor||{}).web_search||"$10/1000"))}. `+
    `Fechas/horas en zona local. Coste = contrafactual a tarifas API. `+
    `Importes mostrados en € a ${TASA.toFixed(2)} €/$ (las tarifas API son en USD). `+
    `<br>Fuente de tarifas: ${esc(pm.fuente||"Anthropic")}. `+
    `Datos crudos en <code>panel_costes/datos.json</code>; estado de auto-mejora en <code>panel_costes/estado/</code>. `+
    `<b style="color:#7ee2a8">Este panel solo LEE ~/.claude; nunca escribe ahí.</b>`;
})();

/* ===================== TOOLTIP ===================== */
(function(){
  const tip=el("tip");
  function pos(e){
    const tw=tip.offsetWidth,th=tip.offsetHeight,vw=window.innerWidth,vh=window.innerHeight;
    const x=e.clientX+16,y=e.clientY-10;
    tip.style.left=(x+tw>vw?x-tw-28:x)+"px";
    tip.style.top=(y+th>vh?e.clientY-th-4:y)+"px";
  }
  document.addEventListener("mousemove",e=>{
    const t=e.target.closest("[data-tip]");
    if(!t){tip.style.display="none";return;}
    const c=t.dataset.color||"";
    const dot=c?`<span style="display:inline-block;width:9px;height:9px;border-radius:2px;background:${c};margin-right:7px;vertical-align:-1px"></span>`:"";
    tip.innerHTML=dot+esc(t.dataset.tip);
    tip.style.display="block";
    pos(e);
  });
  document.addEventListener("mouseleave",()=>{tip.style.display="none";});
})();

/* ===================== OVERLAY CONFIGURACIÓN ===================== */
(function(){
  const bg=el("ov_cfg"), btnOpen=el("btn_cfg"), btnClose=el("btn_cfg_close");
  if(!btnOpen||!bg) return;
  btnOpen.addEventListener("click",()=>bg.classList.add("open"));
  btnClose.addEventListener("click",()=>bg.classList.remove("open"));
  bg.addEventListener("click",e=>{ if(e.target===bg) bg.classList.remove("open"); });
  document.addEventListener("keydown",e=>{ if(e.key==="Escape"&&bg.classList.contains("open")) bg.classList.remove("open"); });
})();

/* ===================== BOTÓN ACTUALIZAR ===================== */
(function(){
  if(!location.protocol.startsWith("http")) return;
  const b=document.createElement("button");
  b.textContent="🔄 Actualizar ahora";
  b.style.cssText="cursor:pointer;font:inherit;font-size:11px;padding:4px 11px;border-radius:999px;"+
    "border:1px solid #1f5137;color:#7ee2a8;background:#0f2419";
  b.title="Regenera los datos en el servidor y recarga";
  b.onclick=async()=>{
    const prev=b.textContent; b.disabled=true; b.textContent="Actualizando…";
    try{
      const r=await fetch("/regenerar",{cache:"no-store"});
      const j=await r.json();
      if(j&&j.ok){ location.reload(); return; }
      throw new Error("respuesta inesperada");
    }catch(e){
      b.textContent="Error — reintenta"; b.disabled=false;
      setTimeout(()=>{ b.textContent=prev; },2500);
    }
  };
  el("badges").appendChild(b);
})();

/* ============== POLL: badge "datos nuevos" (servidor en vivo) ============== */
(function(){
  if(!location.protocol.startsWith("http")) return;
  const mio=D.generado; let avisado=false;
  function mostrar(gen){
    const b=document.createElement("button");
    b.textContent="🟢 Datos nuevos — recargar";
    b.style.cssText="cursor:pointer;font:inherit;font-size:11px;padding:4px 11px;border-radius:999px;"+
      "border:1px solid #7c5cff;color:#cdbcff;background:#1c1733";
    b.title="El servidor regeneró los datos ("+esc(gen||"")+")";
    b.onclick=()=>location.reload();
    el("badges").appendChild(b);
  }
  async function chk(){
    try{ const r=await fetch("/version",{cache:"no-store"}); const j=await r.json();
      if(j&&j.generado&&j.generado!==mio&&!avisado){ avisado=true; mostrar(j.generado); }
    }catch(e){}
  }
  setInterval(chk,20000);
})();
</script>
</body>
</html>
"""
