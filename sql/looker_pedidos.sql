-- =====================================================================
-- Temuzon · Fuente de datos B para Looker Studio  (opcional)
-- Grano: PEDIDO (1 fila = 1 pedido) → 2.000 filas
--
-- Para qué existe si ya tenemos la fuente A:
--   los KPIs logísticos (días de entrega) y cualquier media "por pedido"
--   se calculan mal sobre la fuente A, porque un pedido con 3 líneas
--   pesaría el triple que uno con 1 línea. Este es exactamente el error de
--   "media de medias" que avisa la guía. A grano pedido, cada pedido pesa 1.
--
-- Uso: segunda fuente de datos del mismo informe (Recurso → Añadir datos →
--      BigQuery → Consulta personalizada). Alimenta solo el bloque de
--      logística; no hace falta blending.
-- =====================================================================

SELECT
  -- ── Eje temporal ────────────────────────────────────────────────────
  DATE(pa.fecha_de_cobro)                                     AS fecha,

  -- ── Dimensiones ─────────────────────────────────────────────────────
  pe.estado_pedido                                            AS estado_pedido,
  pe.metodo_de_envio                                          AS metodo_envio,
  pa.metodo_de_pago                                           AS metodo_pago,
  pa.estado                                                   AS estado_pago,
  cl.canal_de_adquisicion                                     AS canal_adquisicion,
  pais_cli.nombre                                             AS pais_cliente,
  pais_env.nombre                                             AS pais_envio,
  pe.ciudad_de_envio                                          AS ciudad_envio,

  -- ── IDs ─────────────────────────────────────────────────────────────
  CAST(pe.id_pedido AS STRING)                                AS id_pedido,
  IF(pe.estado_pedido = 'cancelado',
     CAST(pe.id_pedido AS STRING), NULL)                      AS id_pedido_cancelado,
  CAST(cl.id_cliente AS STRING)                               AS id_cliente,

  -- ── Métricas logísticas ─────────────────────────────────────────────
  DATE_DIFF(pe.fecha_de_reparto, pe.fecha_de_envio, DAY)      AS dias_entrega,
  IF(DATE_DIFF(pe.fecha_de_reparto, pe.fecha_de_envio, DAY) > 3, 1, 0) AS entrega_tardia,
  pe.cantidad                                                 AS unidades_pedido,

  -- ── Valor del pedido (desde las líneas, no desde `pagos`) ───────────
  IF(pe.estado_pedido = 'cancelado', 0, l.valor_pedido)       AS valor_pedido,
  IF(pe.estado_pedido = 'cancelado', l.valor_pedido, 0)       AS valor_cancelado

FROM      `ds-temuzon.Temuzon.pedidos`     pe
JOIN      `ds-temuzon.Temuzon.clientes`    cl ON pe.id_cliente    = cl.id_cliente
LEFT JOIN `ds-temuzon.Temuzon.paises` pais_cli ON cl.pais         = pais_cli.id_pais
LEFT JOIN `ds-temuzon.Temuzon.paises` pais_env ON pe.pais_de_envio = pais_env.id_pais
LEFT JOIN `ds-temuzon.Temuzon.pagos`       pa ON pe.id_pedido     = pa.id_pedido
LEFT JOIN (
  SELECT id_pedido, SUM(subtotal) AS valor_pedido
  FROM `ds-temuzon.Temuzon.linea_pedidos`
  GROUP BY id_pedido
) l ON pe.id_pedido = l.id_pedido
