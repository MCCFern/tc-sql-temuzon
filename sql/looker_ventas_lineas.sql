-- =====================================================================
-- Temuzon · Fuente de datos A para Looker Studio
-- Grano: LÍNEA DE PEDIDO (1 fila = 1 producto dentro de 1 pedido) → 4.002 filas
-- Uso: Recurso → Añadir datos → BigQuery → CONSULTA PERSONALIZADA
--
-- Por qué consulta personalizada y no "tabla directa":
--   la agregación y los joins se resuelven en BigQuery (una sola pasada,
--   ~0,5 MB escaneados) en vez de mandar 8 tablas crudas a Looker Studio.
--
-- Convenciones aplicadas:
--   · Los IDs salen como STRING para que Looker Studio NO los trate como
--     métricas sumables (error clásico: "suma de id_pedido").
--   · Las métricas de negocio ya vienen a 0 en los pedidos cancelados, así
--     ningún gráfico necesita acordarse de filtrar. El importe cancelado
--     viaja aparte en `ingresos_cancelados`.
--   · Los importes NO llevan IVA (`subtotal` es base imponible). El IVA por
--     país está en `paises.iva` si se necesitara vista fiscal.
--
-- ⚠ La tabla `pedidos` NO tiene fecha de pedido. Se usa `pagos.fecha_de_cobro`
--   como eje temporal (en los datos generados coincide con `fecha_de_envio`,
--   es decir, pedido + 1-2 días). Documentado en docs/bi_looker_studio.md.
-- =====================================================================

SELECT
  -- ── Eje temporal ────────────────────────────────────────────────────
  DATE(pa.fecha_de_cobro)                                     AS fecha,

  -- ── Dimensiones de catálogo ─────────────────────────────────────────
  cp.nombre                                                   AS categoria,
  pr.nombre                                                   AS producto,
  pr.estado                                                   AS estado_producto,
  pr.stock                                                    AS stock_actual,

  -- ── Dimensiones de cliente y geografía ──────────────────────────────
  pais_cli.nombre                                             AS pais_cliente,
  pais_env.nombre                                             AS pais_envio,
  cl.canal_de_adquisicion                                     AS canal_adquisicion,

  -- ── Dimensiones de pedido ───────────────────────────────────────────
  pe.estado_pedido                                            AS estado_pedido,
  pe.metodo_de_envio                                          AS metodo_envio,
  pa.metodo_de_pago                                           AS metodo_pago,
  CONCAT(CAST(lp.porcentaje_descuento AS STRING), '%')        AS tramo_descuento,

  -- ── IDs (STRING → dimensiones, nunca métricas) ──────────────────────
  CAST(pe.id_pedido AS STRING)                                AS id_pedido,
  IF(pe.estado_pedido = 'cancelado', NULL,
     CAST(pe.id_pedido AS STRING))                            AS id_pedido_valido,
  IF(pe.estado_pedido = 'cancelado',
     CAST(pe.id_pedido AS STRING), NULL)                      AS id_pedido_cancelado,
  CAST(cl.id_cliente AS STRING)                               AS id_cliente,
  CAST(pr.id_producto AS STRING)                              AS id_producto,

  -- ── Métricas de negocio (cancelados neutralizados a 0) ──────────────
  IF(pe.estado_pedido = 'cancelado', 0,
     lp.subtotal)                                             AS ingresos_netos,
  IF(pe.estado_pedido = 'cancelado', 0,
     lp.precio_unidad * lp.cantidad)                          AS ingresos_brutos,
  IF(pe.estado_pedido = 'cancelado', 0,
     lp.precio_unidad * lp.cantidad - lp.subtotal)            AS descuento_eur,
  IF(pe.estado_pedido = 'cancelado', 0,
     pr.coste * lp.cantidad)                                  AS coste,
  IF(pe.estado_pedido = 'cancelado', 0,
     lp.subtotal - pr.coste * lp.cantidad)                    AS margen,
  IF(pe.estado_pedido = 'cancelado', 0,
     lp.cantidad)                                             AS unidades,

  -- ── Métricas de fuga ────────────────────────────────────────────────
  IF(pe.estado_pedido = 'cancelado', lp.subtotal, 0)          AS ingresos_cancelados,

  -- ── Contadores auxiliares ───────────────────────────────────────────
  -- Sumar un 1 por fila es más limpio que COUNT() sobre una dimensión
  -- cualquiera, y deja los denominadores explícitos en cada fórmula.
  1                                                           AS linea,
  IF(r.valoracion IS NULL, 0, 1)                              AS resena,
  IF(r.valoracion <= 2, 1, 0)                                 AS resena_detractora,
  IF(r.valoracion >= 4, 1, 0)                                 AS resena_promotora,

  -- ── Satisfacción (0 o 1 reseña por línea → no hay fan-out) ──────────
  r.valoracion                                                AS valoracion

FROM      `ds-temuzon.Temuzon.linea_pedidos`       lp
JOIN      `ds-temuzon.Temuzon.pedidos`             pe ON lp.id_pedido      = pe.id_pedido
JOIN      `ds-temuzon.Temuzon.productos`           pr ON lp.id_producto    = pr.id_producto
LEFT JOIN `ds-temuzon.Temuzon.categoria_productos` cp ON pr.id_categoria   = cp.id_categoria
JOIN      `ds-temuzon.Temuzon.clientes`            cl ON pe.id_cliente     = cl.id_cliente
LEFT JOIN `ds-temuzon.Temuzon.paises`        pais_cli ON cl.pais           = pais_cli.id_pais
LEFT JOIN `ds-temuzon.Temuzon.paises`        pais_env ON pe.pais_de_envio  = pais_env.id_pais
-- 1 pago por pedido → no multiplica filas. NO sumar `pagos.cantidad` aquí:
-- a grano línea se duplicaría. Los ingresos salen de `linea_pedidos.subtotal`.
LEFT JOIN `ds-temuzon.Temuzon.pagos`               pa ON pe.id_pedido      = pa.id_pedido
LEFT JOIN `ds-temuzon.Temuzon.resenas`              r ON lp.id_orden_pedido = r.id_orden_pedido
