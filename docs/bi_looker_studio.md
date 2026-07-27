![Temuzon Logo](./Temuzon.png)

# Ejercicio BI — Dashboard de Temuzon en Looker Studio

> Resolución del ejercicio por equipos de la masterclass *BI con Looker Studio*,
> usando la base de datos real de Temuzon en BigQuery (`ds-temuzon.Temuzon`).
>
> **Ventana de análisis:** 2025-06-01 → 2026-04-30 (11 meses completos).
> Todas las cifras de este documento están calculadas sobre ese rango y
> verificadas contra BigQuery.

## Índice
1. [Pregunta de negocio](#1-pregunta-de-negocio)
2. [Canvas de KPIs](#2-canvas-de-kpis)
3. [La historia: insight y recomendación](#3-la-historia-insight-y-recomendación)
4. [Preparación: preguntas de stakeholder](#4-preparación-preguntas-de-stakeholder)
5. [Cómo montar el dashboard](#5-cómo-montar-el-dashboard)
6. [Decisiones técnicas y trampas evitadas](#6-decisiones-técnicas-y-trampas-evitadas)
7. [Límites del dato](#7-límites-del-dato)
8. [Autoevaluación](#8-autoevaluación)

---

## 1. Pregunta de negocio

> **¿Dónde ganamos dinero de verdad en Temuzon, y qué nos lo está quitando por el camino?**

El planteamiento deliberado es no preguntar "¿cuánto vendemos?". Temuzon vende
**2,12 M€** en once meses y esa cifra lleva un año sin moverse: la banda mensual
va de 174 k€ a 221 k€ sin tendencia. Preguntar por ingresos no cambiaría ninguna
decisión, porque la respuesta ya se sabe y es "igual que el mes pasado".

La pregunta que sí cambia decisiones es la del margen: con ingresos planos, lo
único que mueve el resultado es dejar de perder dinero en el trayecto entre lo
que se factura y lo que se ingresa de verdad.

---

## 2. Canvas de KPIs

Cinco KPIs, en la fila superior del informe, cada uno como *scorecard* con
comparación al periodo anterior. Ordenados de izquierda a derecha: primero lo
que sube, después lo que resta.

### KPI 1 — Ingresos netos · **2.116.408 €**

| | |
|---|---|
| **Pregunta que responde** | ¿El negocio crece, se estanca o cae? |
| **Gráfico** | Scorecard con comparación al periodo anterior + línea temporal mensual debajo |
| **Fórmula** | `SUM(ingresos_netos)` |

**Justificación.** Es el contexto obligatorio: ningún otro número significa nada
sin él. Va primero por convención de lectura (esquina superior izquierda), no
porque sea el más accionable. Se llama *netos* porque excluye los pedidos
cancelados y no incluye IVA — es lo que realmente entra en caja.

### KPI 2 — Margen bruto % · **28,6 %**

| | |
|---|---|
| **Pregunta que responde** | ¿Vender más nos está haciendo ganar más? |
| **Gráfico** | Scorecard + barras horizontales ordenadas por categoría |
| **Fórmula** | `SUM(margen) / SUM(ingresos_netos)` |

**Justificación.** Es el KPI que separa facturar de ganar. Con los ingresos
planos, el margen es la única palanca que queda: un punto porcentual de margen
son ~21 k€ al año sin vender ni una unidad más. Se muestra en % y no en euros
porque en euros se confunde con crecimiento de volumen.

### KPI 3 — Ticket medio (AOV) · **1.295 €**

| | |
|---|---|
| **Pregunta que responde** | Si los ingresos se mueven, ¿es por más pedidos o por pedidos más caros? |
| **Gráfico** | Scorecard con comparación al periodo anterior |
| **Fórmula** | `SUM(ingresos_netos) / COUNT_DISTINCT(id_pedido_valido)` |

**Justificación.** Descompone el KPI 1 en sus dos motores. Sin él, una caída de
ingresos es un misterio; con él, se sabe si el problema es de captación
(menos pedidos) o de cesta (pedidos más pequeños). Ojo: **se calcula sobre los
totales agregados, nunca promediando un AOV por fila** — ese es el error de
"media de medias" que avisa la guía.

### KPI 4 — Euros regalados en descuento · **79.216 € (13,1 % del margen)**

| | |
|---|---|
| **Pregunta que responde** | ¿Cuánto margen estamos entregando en descuentos y qué compramos con él? |
| **Gráfico** | Scorecard + barras agrupadas por tramo de descuento (0 % / 5 % / 10 %) mostrando unidades por línea y margen % |
| **Fórmula** | `SUM(descuento_eur)`, y `SUM(descuento_eur) / SUM(margen)` para el % |

**Justificación.** Es el KPI incómodo, y el único de los cinco con una palanca
directa: se decide mañana en una reunión de pricing. El descuento no aparece en
ningún estado financiero como gasto, así que nadie lo mira — pero 79 k€ es más
que dos tercios del margen anual de toda la categoría *laptops* (117 k€).

### KPI 5 — Tasa de cancelación · **9,7 % (245.509 € perdidos)**

| | |
|---|---|
| **Pregunta que responde** | ¿Cuánto de lo que vendemos se cae antes de cobrarse? |
| **Gráfico** | Scorecard + línea temporal mensual para detectar picos |
| **Fórmula** | `COUNT_DISTINCT(id_pedido_cancelado) / COUNT_DISTINCT(id_pedido)` |

**Justificación.** Uno de cada diez pedidos se cancela. En euros son 245 k€
—más que el margen anual completo de *laptops*— y a diferencia del descuento,
esto ya ha consumido coste de captación, picking y atención al cliente. Se mide
como tasa y no en euros absolutos para que sea comparable entre meses de
distinto tamaño.

> **Lo que se quedó fuera y por qué.** Nº de clientes activos, valoración media
> y tiempo medio de entrega no pasan la prueba del KPI: ninguna decisión
> comercial cambiaría si se movieran, y en el caso del tiempo de entrega los
> datos muestran que ni siquiera afecta a la satisfacción (ver sección 3).
> Están en el informe, pero como gráficos de apoyo, no como KPIs.

---

## 3. La historia: insight y recomendación

### Insight

**Temuzon lleva un año facturando lo mismo cada mes, pero pierde 325.000 € al
año en dos fugas que nadie está mirando — y no sabe qué está vendiendo
realmente.**

Los tres hallazgos, en orden de importancia:

**1. El descuento cuesta 79.216 € y no compra volumen.**
La mitad de las líneas de pedido (49,3 %) llevan descuento del 5 % o del 10 %.
El margen cae en línea recta con el tramo: 31,2 % → 27,3 % → 23,5 %. Y las
unidades vendidas por línea son idénticas en los tres tramos:

| Tramo | Líneas | % líneas | Unidades/línea | € regalados | Margen % |
|---|---:|---:|---:|---:|---:|
| 0 % | 1.639 | 50,7 % | **1,495** | — | 31,2 % |
| 5 % | 800 | 24,7 % | **1,484** | 26.933 € | 27,3 % |
| 10 % | 795 | 24,6 % | **1,501** | 52.283 € | 23,5 % |

Estamos pagando 79 k€ por un incremento de volumen de exactamente cero.

**2. El 33 % de la facturación viene de productos marcados como "inactivo".**
26 de los 70 productos del catálogo tienen `estado = 'inactivo'` y aun así
facturaron 698.584 € — con **mejor** margen que los activos (30,5 % vs 27,6 %).
O el campo `estado` está podrido, o estamos vendiendo cosas que la empresa cree
haber descatalogado. Mientras eso no se resuelva, ninguna decisión de surtido o
de compras es fiable.

**3. Se cancela 1 de cada 10 pedidos: 245.509 €.**
Y el margen está muy concentrado: **14 productos (el 20 % del catálogo) generan
el 41,8 % del margen total**. Uno de ellos, *Tech Común* (14.723 € de margen),
tiene stock para **1,1 meses**.

**Lo que NO es el problema.** La logística está sana y no explica la
satisfacción: la entrega tarda 2,5 días de media, y las valoraciones no mejoran
al entregar antes (3,07 con 2 días; 3,21 con 4 días) ni al pagar Express (3,12
frente a 3,09 en Estándar, sobre ~550 reseñas cada uno). El 3,10/5 con 37 % de
detractores es un problema de producto o de expectativa, no de reparto — y por
eso invertir en logística no lo arreglaría.

### Recomendación

**Primero, y esta semana: auditar el campo `estado` del catálogo.** No es una
recomendación de negocio, es de gobernanza — pero va primero porque un tercio
de la facturación está clasificada de forma incoherente y eso invalida
cualquier análisis de surtido que hagamos encima. Coste: una tarde de trabajo.

**Segundo: pasar el descuento de automático a condicionado.** Hoy la mitad de
las líneas lo llevan sin criterio visible. Propuesta: reservarlo para liquidar
las referencias con más de 12 meses de cobertura de stock, o para superar un
umbral de ticket. Impacto máximo teórico de eliminar el descuento no
justificado: **+79 k€ de margen anual, un +13 %**, sin caída esperada de
volumen según los datos. Validación antes de generalizar: test A/B de 6 semanas
en una categoría, midiendo unidades por línea y margen %.

**Tercero: reponer las tres referencias en riesgo** (*Tech Común*, *Tech Tal*,
*Tech Menos*: menos de 3 meses de cobertura), y desplazar el mix hacia
*laptops*. *Laptops* rinde al 33,4 % de margen frente al 26,3 % de *audio*;
cada euro de venta que se mueve de una a otra vale **7 puntos** de margen.

---

## 4. Preparación: preguntas de stakeholder

**«¿Cómo sé que esta tendencia no es simplemente estacionalidad?»**
No lo es, y precisamente porque no hay tendencia. Con una media de 192.401 €
al mes, los ingresos se mueven entre −9 % y +15 % sin dirección, y el único
pico esperable es diciembre (220.920 €). El margen % es todavía más plano: entre
27,8 % y 29,3 % los once meses. Nuestro insight no depende de una tendencia
temporal — el 13 % de margen que se va en descuentos está ahí todos los meses.

**«Me habéis enseñado el qué. ¿Cuál es el porqué?»**
El *qué* es que el margen cae 7,7 puntos entre las líneas sin descuento y las
del 10 %. El *porqué* es que el descuento se está aplicando sin criterio: si
fuera una palanca de venta, las líneas con descuento moverían más unidades, y
mueven exactamente las mismas (1,49 vs 1,50). Es un descuento defensivo o
inercial, no comercial.

**«¿Este dato es fiable? ¿Cómo sé que no hay un error de agregación detrás?»**
Es la pregunta correcta, y aquí tenemos una respuesta concreta. Si se mira el
descuento **a nivel de pedido**, parece que funciona: los pedidos con algún
descuento tienen un AOV de 1.405 € frente a 1.054 € sin descuento. Es falso.
Un pedido con tres líneas tiene el triple de probabilidad de contener al menos
una línea con descuento que uno de una sola línea, así que el grupo "con
descuento" está lleno de pedidos grandes **por construcción**. El descuento se
aplica a la línea, así que hay que medirlo en la línea — y ahí el efecto
desaparece. También hemos cuadrado los ingresos de la fuente contra
`SUM(pagos.cantidad)` de los pagos completados: 2.348.908,42 € por ambos
caminos, cero fan-out en los joins.

**«Si solo pudiera mirar un número antes de una reunión de 5 minutos, ¿cuál?»**
Margen bruto %. Los ingresos ya sabemos que no se mueven; el margen es lo único
que reacciona a las decisiones que tomamos.

**«¿Qué decisión cambiaría si el número de descuentos bajase un 20 % el mes que viene?»**
Sabríamos que la política nueva está aplicándose, y pasaríamos a vigilar
unidades por línea: si se mantienen en ~1,49, se generaliza a todas las
categorías; si caen, el descuento sí estaba sosteniendo volumen y revertimos.
Ese es exactamente el diseño del test A/B que proponemos.

**«¿Por qué barras y no una tarta para el margen por categoría?»**
Porque con cinco categorías que van del 17,0 % al 22,7 % del margen total, los
ángulos de una tarta son indistinguibles a simple vista. Las barras ordenadas
permiten leer el ranking y la magnitud de un vistazo, que es justo la pregunta
que se hace ahí.

**«¿Qué falta en este dashboard que yo preguntaría en la reunión?»**
Tres cosas, y sabemos que faltan: (1) el coste de adquisición por canal, que no
está en la base de datos, y sin él "canal directo factura más" no significa que
sea el más rentable; (2) la fecha real del pedido — sólo tenemos la de cobro
(ver sección 7); (3) clientes recurrentes frente a nuevos, que requiere una
definición de negocio que aún no existe.

---

## 5. Cómo montar el dashboard

### 5.1 Conexión

`Recurso → Añadir datos → BigQuery → Consulta personalizada → proyecto ds-temuzon`,
y pegar el contenido de:

| Fuente | Archivo | Grano | Filas | Alimenta |
|---|---|---|---:|---|
| **A** (principal) | [`sql/looker_ventas_lineas.sql`](../sql/looker_ventas_lineas.sql) | Línea de pedido | 4.002 | Los 5 KPIs y todos los gráficos comerciales |
| **B** (opcional) | [`sql/looker_pedidos.sql`](../sql/looker_pedidos.sql) | Pedido | 2.000 | Sólo el bloque de logística |

Consulta personalizada y no tabla directa: los joins y el cálculo de margen se
resuelven en BigQuery en una sola pasada. Cada refresco escanea **395 KB**
(fuente A) — a efectos prácticos, gratis. Traer las 8 tablas crudas y hacer los
joins en Looker Studio costaría más y sería más frágil.

### 5.2 Campos calculados a crear en Looker Studio

```
Margen %              =  SUM(margen) / SUM(ingresos_netos)
Ticket medio (AOV)    =  SUM(ingresos_netos) / COUNT_DISTINCT(id_pedido_valido)
Tasa de cancelación   =  COUNT_DISTINCT(id_pedido_cancelado) / COUNT_DISTINCT(id_pedido)
Descuento s/ margen   =  SUM(descuento_eur) / SUM(margen)
Unidades por línea    =  SUM(unidades) / SUM(linea)
% detractores         =  SUM(resena_detractora) / SUM(resena)
Meses de cobertura    =  MAX(stock_actual) / (SUM(unidades) / 11)
```

Los cuatro primeros deben formatearse como porcentaje o moneda **en el campo, no
en el gráfico**, para que sean consistentes en todo el informe.

### 5.3 Estructura del informe

**Controles (barra superior, aplican a todo el informe)**
- Control de fecha sobre `fecha`, por defecto **2025-06-01 → 2026-04-30**
- Lista desplegable: `categoria`, `pais_cliente`, `canal_adquisicion`

**Fila 1 — los 5 KPIs** (scorecards con comparación al periodo anterior)
`Ingresos netos` · `Margen %` · `AOV` · `€ en descuento` · `Tasa de cancelación`

**Fila 2 — la tendencia**
Gráfico de líneas mensual: ingresos netos (barras) + margen % (línea, eje
secundario). Responde "¿vamos mejor o peor?" y muestra de un golpe que ninguna
de las dos se mueve.

**Fila 3 — dónde está el negocio y dónde se escapa** (dos gráficos lado a lado)
- Barras horizontales ordenadas: **margen € por categoría**, con el margen % como
  etiqueta. Barras y no tarta: cinco categorías entre el 17 % y el 23 % son
  indistinguibles en ángulos.
- Barras agrupadas por **tramo de descuento**: unidades por línea y margen %.
  Es el gráfico que sostiene toda la recomendación — dos series, tres barras,
  y la conclusión se lee sin explicación.

**Fila 4 — el detalle accionable**
Tabla de productos con barras en la celda: producto · categoría · estado ·
unidades · margen € · margen % · meses de cobertura. Ordenada por margen
descendente, con formato condicional en rojo para cobertura < 3 meses. Es la
lista que se lleva alguien a la reunión de compras.

**Colorimetría.** Verde corporativo en tres intensidades para todo lo que suma
(ingresos, margen, unidades); gris para contexto; **rojo reservado en exclusiva
para lo que resta** (descuento, cancelaciones, riesgo de stock). Ningún color
decorativo, y ningún dato codificado sólo por color: los estados de riesgo
llevan además el valor numérico visible.

---

## 6. Decisiones técnicas y trampas evitadas

**Grano y fan-out.** La fuente A está a nivel de línea de pedido. Un pedido con
tres líneas ocupa tres filas, así que `pagos.cantidad` (que es de nivel pedido)
se triplicaría si se sumara ahí. Por eso los ingresos se calculan siempre desde
`linea_pedidos.subtotal`. Comprobación: `SUM(ingresos_netos)` de la fuente A =
2.348.908,42 €, idéntico a `SUM(cantidad)` de los pagos en estado `completado`.

**Cancelados neutralizados en origen.** Las métricas de la fuente A ya vienen a
0 en los pedidos cancelados, y el importe cancelado viaja aparte en
`ingresos_cancelados`. Así ningún gráfico depende de que alguien se acuerde de
poner el filtro — el error más común y más silencioso en un informe compartido.

**IDs como STRING.** `id_pedido`, `id_cliente` e `id_producto` salen casteados a
texto para que Looker Studio los clasifique como dimensiones. Si salen como
enteros, la herramienta los ofrece como métricas y aparecen "sumas de
id_pedido" en los gráficos.

**Por qué existe la fuente B.** El tiempo medio de entrega es un atributo del
pedido, no de la línea. Calculado sobre la fuente A, un pedido de tres líneas
pesaría el triple que uno de una. En estos datos concretos el sesgo resulta ser
cero (2,5055 días por ambos caminos, porque los días de reparto se generaron
independientes del número de líneas), pero el método seguiría siendo incorrecto
y con datos reales daría un número distinto. Las medias por pedido se calculan
en la fuente B.

**Bug detectado en el repo.** La query 6 de
[`notebooks/queries_verification.ipynb`](../notebooks/queries_verification.ipynb)
une `clientes` con `linea_pedidos` mediante `ON c.id_cliente = lp.id_pedido`
—identificador de cliente contra identificador de pedido—, así que su resultado
("el canal principal de laptops es directo") no es válido. La ruta correcta es
`clientes → pedidos → linea_pedidos`. No afecta a este dashboard, que no reutiliza
esa query, pero conviene corregirlo.

---

## 7. Límites del dato

Cinco cosas que hay que decir antes de que las pregunte alguien:

1. **No existe fecha de pedido.** La tabla `pedidos` sólo tiene `fecha_de_envio`
   y `fecha_de_reparto`. El eje temporal usa `pagos.fecha_de_cobro`, que en
   estos datos coincide con la fecha de envío (pedido + 1-2 días). Para
   análisis de estacionalidad fina el desfase importaría; para la lectura
   mensual, no.
2. **Meses parciales.** El histórico va del 2025-05-06 al 2026-05-07, así que
   mayo de 2025 y mayo de 2026 están incompletos. Por eso el rango por defecto
   son los 11 meses completos: incluirlos produciría una "caída" del 77 % en el
   último mes que no existe (44.509 € frente a una media de 192.401 €).
3. **Los importes no llevan IVA.** `subtotal` es base imponible. El IVA por país
   está en `paises.iva` (16-25 %) si se necesitara una vista fiscal.
4. **No hay coste de adquisición ni de envío.** El margen calculado es margen
   bruto de producto (`subtotal − coste × cantidad`), no margen de contribución.
   Por eso el análisis por canal se queda en descriptivo: sin CAC, "el canal
   directo factura más" no permite concluir que sea el más rentable.
5. **Los datos son sintéticos (Faker con distribuciones uniformes).** Esto tiene
   una consecuencia que conviene no esconder: las diferencias pequeñas entre
   segmentos —canal, país, método de pago— son ruido estadístico y no deberían
   defenderse como hallazgos. Y en el caso concreto del descuento, el generador
   lo asigna al azar con independencia de la cantidad, así que la ausencia de
   efecto sobre el volumen está garantizada por construcción.

   Lo que hace válido el ejercicio no es la conclusión, sino el método: medir la
   palanca en el grano donde se aplica, y desmontar el artefacto de composición
   que aparece al agregarla un nivel más arriba. Sobre datos reales, ese mismo
   análisis es el que decide si una política de descuentos se mantiene o se
   retira.

---

## 8. Autoevaluación

| Criterio | Cómo lo cumplimos |
|---|---|
| **KPIs relevantes** | Los 5 pasan la prueba "si este número cambia, ¿qué decisión cambia?". Los que no la pasaban (valoración media, tiempo de entrega, nº de clientes) quedaron como gráficos de apoyo, no como KPIs. |
| **Claridad visual** | 5 KPIs arriba, una tendencia en el centro, dos gráficos de desglose y una tabla de detalle. Paleta de un solo color en intensidades + rojo reservado para lo que resta. |
| **Gráfico correcto** | Barras ordenadas en vez de tarta para las 5 categorías; línea para la evolución temporal; barras agrupadas para el efecto del descuento; tabla sólo donde hace falta el dato exacto (reposición). |
| **Storytelling** | Dato (79 k€ en descuentos, 13 % del margen) → interpretación (no compra volumen: 1,49 vs 1,50 unidades por línea) → recomendación (descuento condicionado + test A/B de 6 semanas). |
| **Justificación** | Cada KPI tiene su pregunta de negocio explícita, y las trampas conocidas (media de medias, fan-out, artefacto de composición pedido/línea) están documentadas con la cifra que las desmonta. |
| **Corrección técnica** | Ambas consultas validadas contra BigQuery; ingresos cuadrados contra los pagos completados (2.348.908,42 € por dos caminos); 395 KB por refresco; IDs casteados para no ser tratados como métricas. |
