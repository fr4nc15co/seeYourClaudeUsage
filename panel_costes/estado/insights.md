# Insights del panel de costes

Ejecucion #39 — 2026-06-17 23:47

## Cambios desde la ejecucion anterior
- Gasto: +0.0979 USD
- Sesiones: +0   Requests: +8   Limites: +0

## Recomendaciones
- Por TIPO de actividad hay ~$177.19 reasignables (frente a $5.15 del rightsizing por longitud): Documentación→Sonnet 4.6, Refactorización→Sonnet 4.6, Configuración/DevOps→Sonnet 4.6. Son tareas mecánicas que corrieron en Opus. Ver 'Ajuste por tipo de actividad'.
- Rightsizing: 5 sesiones ligeras en modelos premium podrían haber usado Haiku/Sonnet → ahorro potencial estimado $5.15 (0% del gasto). Ver sección 'Recomendaciones de modelo'.
- Opus acumula el 78% del gasto. Para refactors mecanicos, busquedas o resumenes, Sonnet 4.6 (3/15) o Haiku 4.5 (1/5) reducirian el coste bastante.
- El caching va muy bien: el 96% de los tokens de entrada se sirven de cache (ahorro estimado de $6144.75). Mantener prompts estables potencia esto.
- La suscripcion 'Pro' ($40 total) sale mas barata que pagar la API ($1341.15). Si ese es tu plan, lo estas amortizando con creces.
- Se detectaron 18 eventos de error/limite de API. Si topan a menudo, considera espaciar las rafagas o subir de plan.
