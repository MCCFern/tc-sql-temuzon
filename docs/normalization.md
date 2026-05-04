# Análisis de Normalización 3NF - Temuzon Database

![Temuzon Logo](./Temuzon.png)

## Índice
1. [Visión General](#visión-general)
2. [Modelo de Datos](#modelo-de-datos)
3. [Análisis de Normalización 3NF](#análisis-de-normalización-3nf)
4. [Decisiones de Diseño](#decisiones-de-diseño)
5. [Relaciones y Restricciones](#relaciones-y-restricciones)
6. [Diagrama Entidad-Relación](#diagrama-entidad-relación)

---

## Visión General

La base de datos **Temuzon** es un sistema de gestión de e-commerce diseñado para administrar:
- Catálogo de productos organizados por categorías
- Gestión de clientes e información de contacto
- Procesamiento de pedidos y líneas de pedido
- Sistema de pagos y seguimiento de transacciones
- Reseñas y evaluaciones de productos
- Información geográfica (países) con cálculo de IVA

El diseño sigue principios de **normalización relacional de tercera forma normal (3NF)** para garantizar:
- Integridad referencial
- Eliminación de redundancia de datos
- Facilidad de mantenimiento y actualización

---

## Modelo de Datos

### Tablas del Sistema

#### 1. **Paises** (Tabla Referencial)
```
Propósito: Almacenar información de países y su régimen fiscal
```
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `IdPais` | INT | Identificador único (PK) |
| `Nombre` | STRING | Nombre del país |
| `Continente` | STRING | Continente al que pertenece |
| `IVA` | INT | Porcentaje de IVA aplicable en ese país |

**Función en el sistema:**
- Tabla maestro/referencial que proporciona información geográfica y fiscal
- Utilizada por `Clientes` (país de residencia) y `Pedidos` (país de envío)
- Facilita el cálculo automático de impuestos según destino

---

#### 2. **Categoria_Productos** (Tabla Referencial)
```
Propósito: Clasificación jerárquica de productos
```
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `IdCategoria` | INT | Identificador único (PK) |
| `Nombre` | STRING | Nombre de la categoría |
| `Descripción` | TEXT | Descripción detallada de la categoría |

**Función en el sistema:**
- Tabla maestro que define categorías de productos
- Permite organizar el catálogo de forma jerárquica
- Facilita búsquedas y filtros en el e-commerce

---

#### 3. **Productos** (Tabla Principal)
```
Propósito: Catálogo de productos disponibles
```
| Campo | Tipo | Relación | Descripción |
|-------|------|----------|-------------|
| `IdProducto` | INT | PK | Identificador único del producto |
| `IdCategoria` | INT | FK → Categoria_Productos | Categoría a la que pertenece |
| `Nombre` | STRING | | Nombre del producto |
| `Precio de venta` | INT | | Precio de venta al público |
| `Coste` | INT | | Costo de adquisición |
| `Stock` | INT | | Cantidad disponible en inventario |
| `Estado` | STRING | | Estado del producto (activo, descontinuado, etc.) |

**Decisión de diseño:**
- Los precios se almacenan como `INT` en lugar de `DECIMAL` para evitar problemas de precisión flotante
- El `Stock` se actualiza en transacciones de pedidos
- El `Estado` permite gestionar ciclo de vida de productos

---

#### 4. **Clientes** (Tabla Principal)
```
Propósito: Información de clientes del e-commerce
```
| Campo | Tipo | Relación | Descripción |
|-------|------|----------|-------------|
| `IdCliente` | INT | PK | Identificador único |
| `Nombre` | STRING | | Nombre del cliente |
| `Apellidos` | STRING | | Apellidos del cliente |
| `Dirección` | STRING | | Dirección de residencia |
| `Codigo Postal` | INT | | Código postal |
| `Ciudad` | STRING | | Ciudad |
| `País` | INT | FK → Paises | País de residencia |
| `Nº Identificacion` | STRING | | Documento de identidad |
| `Email` | STRING | | Correo electrónico |
| `Telefono` | STRING | | Número de teléfono |
| `Canal de adquisición` | STRING | | Cómo conoció de Temuzon (SEO, publicidad, referencia, etc.) |

**Decisión de diseño:**
- Separación de `Nombre` y `Apellidos` para facilitar búsquedas y reportes
- `Nº Identificacion` como STRING para soportar diferentes formatos (DNI, pasaporte, etc.)
- Dirección completa en un solo campo para simplificar, aunque podría normalizarse más si fuera necesario
- `Canal de adquisición` como enumeración de marketing para análisis

---

#### 5. **Pedidos** (Tabla Principal - Transaccional)
```
Propósito: Registro de órdenes de compra
```
| Campo | Tipo | Relación | Descripción |
|-------|------|----------|-------------|
| `IdPedido` | INT | PK | Identificador único del pedido |
| `IdCliente` | STRING | FK → Clientes | Cliente que realiza la compra |
| `Estado pedido` | STRING | | Estado (pendiente, procesado, enviado, entregado, cancelado) |
| `Cantidad` | INT | | Cantidad total de artículos |
| `Dirección de envío` | STRING | | Dirección de entrega (puede diferir de residencia) |
| `Codigo Postal` | INT | | Código postal de envío |
| `Ciudad de envío` | STRING | | Ciudad de entrega |
| `País de envío` | INT | FK → Paises | País destino (para cálculo de IVA/aduanas) |
| `Método de envío` | STRING | | Tipo de envío (express, estándar, etc.) |
| `Fecha de envío` | DATETIME | | Cuándo se envió |
| `Fecha de reparto` | DATETIME | | Cuándo fue entregado |
| `Notas` | STRING | | Notas especiales del pedido |

**Decisión de diseño:**
- Dirección de envío duplicada (desnormalización controlada) para mantener historial de entregas
- `País de envío` separado del cliente para auditoría de envíos internacionales
- Timestamps para tracking de envíos
- `Cantidad` se usa para estadísticas rápidas sin recalcular desde `Linea_Pedidos`

---

#### 6. **Linea_Pedidos** (Tabla de Detalles - Normalización)
```
Propósito: Desglose de artículos en cada pedido
```
| Campo | Tipo | Relación | Descripción |
|-------|------|----------|-------------|
| `IdOrdenPedido` | INT | PK | Identificador único de la línea |
| `IdPedido` | INT | FK → Pedidos | Pedido al que pertenece |
| `IDProducto` | INT | FK → Productos | Producto vendido |
| `Cantidad` | INT | | Unidades vendidas |
| `Precio Unidad` | INT | | Precio unitario en el momento de la venta |
| `Porcentaje descuento` | INT | | Descuento aplicado (0-100%) |
| `Subtotal` | INT | | Cantidad × Precio × (1 - Descuento%) |

**Decisión de diseño:**
- Tabla de detalles separada para mantener normalización 1NF
- `Precio Unidad` es copia del precio en el momento de venta (desnormalización intencional) para auditoría
- `Subtotal` se precalcula y almacena para queries rápidas
- Composite Key podría ser (IdPedido, IDProducto) pero se usa un PK simple para flexibilidad

---

#### 7. **Pagos** (Tabla Transaccional)
```
Propósito: Registro de transacciones de pago
```
| Campo | Tipo | Relación | Descripción |
|-------|------|----------|-------------|
| `IdPago` | INT | PK | Identificador único del pago |
| `IdPedido` | INT | FK → Pedidos | Pedido asociado |
| `Cantidad` | INT | | Monto pagado |
| `Metodo de pago` | STRING | | Método (tarjeta, transferencia, PayPal, etc.) |
| `Estado` | STRING | | Estado (pendiente, completado, fallido, reembolsado) |
| `Fecha de cobro` | DATETIME | | Fecha de transacción exitosa |
| `Fecha de reembolso` | DATETIME | | Fecha del reembolso si aplica |

**Decisión de diseño:**
- Tabla separada de `Pedidos` para rastrear múltiples intentos de pago
- `Estado` y fechas permiten auditoría de transacciones
- Soporta reembolsos parciales mediante cantidad

---

#### 8. **Reseñas** (Tabla de Opiniones)
```
Propósito: Sistema de evaluaciones y comentarios de clientes
```
| Campo | Tipo | Relación | Descripción |
|-------|------|----------|-------------|
| `IdReseña` | INT | PK | Identificador único |
| `IdOrdenPedido` | INT | FK → Linea_Pedidos | Línea de pedido reseñada |
| `IdCliente` | INT | FK → Clientes | Cliente que hace la reseña |
| `Valoración` | INT | | Puntuación (1-5 estrellas) |
| `Comentario` | TEXT | | Texto de la reseña |

**Decisión de diseño:**
- Relación a `Linea_Pedidos` en lugar de `Productos` para garantizar que solo se reseñan compras reales
- Validación de integridad: cliente debe ser el que compró el producto
- Permite reseñas múltiples del mismo producto por diferentes clientes

---

## Análisis de Normalización 3NF

### Primera Forma Normal (1NF)
**Requisito:** Todos los atributos contienen solo valores atómicos (no multivaluados)

✅ **Cumplida en todas las tablas:**
- Cada atributo contiene un único valor
- No hay conjuntos o listas dentro de campos
- Ejemplo: `Clientes.Nombre` es un string único, no un array

### Segunda Forma Normal (2NF)
**Requisito:** Está en 1NF AND todo atributo no-clave depende funcionalmente de la **clave primaria completa**

✅ **Cumplida:**
- `Productos`: IDProducto → IdCategoria, Nombre, Precio (dependencia completa)
- `Clientes`: IdCliente → Nombre, Email, Teléfono (dependencia completa)
- `Linea_Pedidos`: (IdPedido, IdProducto) → Cantidad, Precio (dependencia de la clave completa)

**Aplicación:**
- No hay atributos que dependan solo de parte de la clave primaria
- Categoría está en tabla separada, no duplicada en cada producto

### Tercera Forma Normal (3NF)
**Requisito:** Está en 2NF AND ningún atributo no-clave depende de otro atributo no-clave (eliminación de dependencias transitivas)

✅ **Cumplida con análisis detallado:**

| Tabla | Verificación 3NF |
|-------|------------------|
| **Paises** | ✅ Solo atributos descriptivos que dependen de IdPais |
| **Categoria_Productos** | ✅ Nombre y Descripción dependen solo de IdCategoria |
| **Productos** | ✅ Todos los atributos dependen solo de IdProducto |
| **Clientes** | ✅ ⚠️ Dirección + Ciudad + CP + País podría normalizarse más (ver nota) |
| **Pedidos** | ✅ ⚠️ Cantidad y Dirección de envío se desnormalizan intencionalmente (ver decisión) |
| **Linea_Pedidos** | ✅ Todos dependen de IdOrdenPedido |
| **Pagos** | ✅ Todos dependen de IdPago |
| **Reseñas** | ✅ Todos dependen de IdReseña |

#### Análisis de Excepciones Justificadas

**1. Desnormalización en `Clientes.País`**
```
DECISIÓN: Se mantiene el País como FK en lugar de derivar de Dirección
RAZÓN: 
- País es información crítica para cumplimiento fiscal
- Evita queries complejas cada vez que se necesita el IVA
- Rendimiento: O(1) en lugar de parsear dirección
- Integridad: La FK garantiza que el país existe en la tabla Paises
```

**2. Desnormalización en `Pedidos`**
```
DECISIÓN: Se almacena Cantidad + Dirección de envío en Pedidos
RAZÓN:
- AUDITORÍA: Mantiene historial exacto de cómo se envió
- Si se cambian direcciones, seguimos teniendo el histórico
- Cantidad permite dashboards rápidos sin JOIN a Linea_Pedidos
- NORMALIZACIÓN TEÓRICA: Podría removerse, pero el costo supera beneficios
```

**3. Copia de `Precio Unidad` en `Linea_Pedidos`**
```
DECISIÓN: Se duplica el precio del producto en la línea de pedido
RAZÓN:
- AUDITORÍA HISTÓRICA: Si cambia el precio del producto, mantenemos qué pagó
- CÁLCULOS RÁPIDOS: Subtotal sin necesar traer histórico de precios
- NORMALIZACIÓN: Viola 3NF técnicamente, pero es necesario para auditoría
```

**4. Dirección completa en campo único en `Clientes` y `Pedidos`**
```
DECISIÓN: Dirección + Ciudad + CP en campos separados (sin tabla Direcciones)
RAZÓN:
- En versiones futuras podría haber tabla Direcciones normalizada
- Por ahora, el overhead de otra tabla no justifica el beneficio
- Las direcciones se modifican raramente
- 3NF: Se cumple porque no hay dependencia cíclica
```

---

## Decisiones de Diseño

### 1. **Tipos de Datos**

#### Precios como INT en lugar de DECIMAL
```sql
Precio_de_venta INT  -- representa centavos (100 = 1.00€)
NO: Precio_de_venta DECIMAL(10,2)
```
**Razones:**
- Evita problemas de precisión flotante en cálculos
- Más rápido en operaciones matemáticas
- Estándar en sistemas financieros (almacenar en centavos/céntimos)
- Facilita auditoría exacta

#### Identificadores como STRING donde es necesario
```sql
Nº Identificacion STRING  -- soporta DNI, Pasaporte, etc.
```
**Razones:**
- Flexibilidad internacional
- Algunos países usan letras en documentos

### 2. **Relaciones Clave**

#### Relación Múltiple: Pedido → País (Cliente ≠ Envío)
```
Clientes.País ─────┐
                    ├─→ Determina zona fiscal
Pedidos.País ───────┤
                    └─→ Cálculo de impuestos, aduanas
```
**Razones:**
- Soporte para envíos internacionales
- Cliente en España, envío a Portugal ≠ mismo IVA
- Auditoría de cumplimiento aduanal

#### Linea_Pedidos como tabla de asociación
```
Pedidos ──┬─→ Linea_Pedidos ─┬─→ Productos
          └─→ (N:N mapping) ─┘
```
**Razones:**
- Un pedido tiene N productos
- Un producto en N pedidos
- Permite historial de precios

### 3. **Estrategia de Auditoría**

| Elemento | Estrategia | Ubicación |
|----------|-----------|-----------|
| **Precios históricos** | Copiar en Linea_Pedidos | Inmodificable |
| **Dirección de envío** | Copiar en Pedidos | Auditada con FK a Paises |
| **Cambios de estado** | Campos timestamp | Fecha_envio, Fecha_reparto |
| **Reembolsos** | Campo separado | Pagos.Fecha_reembolso |

### 4. **Integridad Referencial**

**Restricciones FK implementadas:**
```
Productos.IdCategoria → Categoria_Productos(IdCategoria) [NO DELETE CASCADE]
Clientes.País → Paises(IdPais) [NO DELETE CASCADE]
Pedidos.IdCliente → Clientes(IdCliente) [NO DELETE CASCADE]
Pedidos.País de envío → Paises(IdPais) [NO DELETE CASCADE]
Linea_Pedidos.IdPedido → Pedidos(IdPedido) [DELETE CASCADE]
Linea_Pedidos.IdProducto → Productos(IdProducto) [NO DELETE CASCADE]
Pagos.IdPedido → Pedidos(IdPedido) [DELETE CASCADE]
Reseñas.IdCliente → Clientes(IdCliente) [NO DELETE CASCADE]
Reseñas.IdOrdenPedido → Linea_Pedidos(IdOrdenPedido) [NO DELETE CASCADE]
```

---

## Relaciones y Restricciones

### Diagrama de Relaciones

```
                    ┌─────────────────┐
                    │   Paises        │
                    │ ─────────────── │
                    │ ⬤ IdPais (PK)   │
                    │   Nombre        │
                    │   Continente    │
                    │   IVA           │
                    └─────────────────┘
                           ▲
                  ┌────────┴────────┐
                  │                 │
           (1:N)  │                 │ (1:N)
          ┌───────┴────────┐        └──────────────┐
          │  Clientes      │              ┌────────┴──────────┐
          │ ────────────── │              │ Pedidos           │
          │ ⬤ IdCliente    │              │ ──────────────────│
          │   Nombre       │              │ ⬤ IdPedido (PK)   │
          │   Email        │              │   IdCliente (FK)  │
          │   País (FK) ◄──┤──────────────┤   País envío (FK) │
          │   ...          │              │   Estado pedido   │
          └────────────────┘              │   Cantidad        │
                                          │   Dirección envío │
                                          │   ...             │
                                          └──────┬─────────────┘
                                                 │
                                    ┌────────────┼────────────┐
                                    │            │            │
                            (1:N)   │            │            │ (1:N)
                          ┌─────────┴─────┐      │      ┌──────┴───────┐
                          │ Linea_Pedidos │      │      │ Pagos        │
                          │ ──────────────│      │      │ ──────────── │
                          │ ⬤ IdOrden (PK)│      │      │ ⬤ IdPago     │
                          │   IdPedido (FK)      │      │   IdPedido(FK)
                          │   IdProducto (FK)    │      │   Cantidad   │
                          │   Cantidad      ◄────┘      │   Método pago│
                          │   Precio Unidad      │      │   Estado     │
                          │   % Descuento        │      │   Fecha_cobro
                          │   Subtotal           │      │   ...        │
                          └──────────────────────┤      └──────────────┘
                                                 │
                                  ┌──────────────┴──────────────┐
                                  │                             │
                      (1:N)        │                             │
                    ┌──────────────┴─────────┐                 │
                    │ Categoria_Productos    │                 │
                    │ ──────────────────────  │                 │
                    │ ⬇ ⬇ ⬇ ⬇ ⬇ ⬇         │                 │
                    │ ⬇ ⬇ ⬇ ⬇ ⬇ ⬇         │                 │
                    │ IdCategoria (PK)       │                 │
                    │ Nombre                 │                 │
                    │ Descripción            │                 │
                    └────────────────────────┘                 │
                           ▲                                    │
                 (1:N)      │                                   │
                    ┌───────┴────────┐                         │
                    │ Productos      │                         │
                    │ ──────────────  │                         │
                    │ ⬇ ⬇ ⬇ ⬇ ⬇ ⬇ │                         │
                    │ ⬇ ⬇ ⬇ ⬇ ⬇ ⬇ │                         │
                    │ IdProducto (FK)                          │
                    │ IdCategoria (FK) ◄───────┐               │
                    │ Nombre                    │               │
                    │ Precio de venta  ◄────────┼───────────────┼─→ Reseñas
                    │ Coste                     │               │  ──────────
                    │ Stock                     │               │  IdReseña
                    │ Estado                    │               │  IdOrden(FK)
                    └────────────────────────────┘               │  IdCliente(FK)
                                 ▲                               │  Valoración
                           (1:N) │                               │  Comentario
                                 │                               │
                                 └───────────────────────────────┘
```

### Reglas de Integridad Críticas

1. **No puede existir pedido sin cliente**
   ```sql
   Pedidos.IdCliente NOT NULL
   Pedidos.IdCliente FK → Clientes
   ```

2. **Línea de pedido requiere producto y pedido**
   ```sql
   Linea_Pedidos.IdPedido NOT NULL FK → Pedidos
   Linea_Pedidos.IdProducto NOT NULL FK → Productos
   ```

3. **Pago requiere pedido**
   ```sql
   Pagos.IdPedido NOT NULL FK → Pedidos
   ```

4. **Reseña requiere cliente y compra real**
   ```sql
   Reseñas.IdCliente NOT NULL FK → Clientes
   Reseñas.IdOrdenPedido NOT NULL FK → Linea_Pedidos
   ```

5. **Cascada de borrados**
   ```
   DELETE Pedidos → DELETE Linea_Pedidos (CASCADE)
   DELETE Pedidos → DELETE Pagos (CASCADE)
   DELETE Linea_Pedidos → DELETE Reseñas (CASCADE)
   
   PERO:
   DELETE Clientes → ❌ ERROR (hay pedidos referenciados)
   DELETE Productos → ❌ ERROR (hay referencias)
   DELETE Paises → ❌ ERROR (hay clientes/pedidos)
   ```

---

## Diagrama Entidad-Relación

```
Leyenda:
PK = Primary Key (Clave Primaria)
FK = Foreign Key (Clave Foránea)
⬇ = Múltiples registros
```

### Resumen de Tablas

| Tabla | Registros | Propósito | Normalización |
|-------|-----------|----------|---------------|
| **Paises** | 195 aprox | Catálogo maestro | ✅ 3NF |
| **Categoria_Productos** | 10-50 aprox | Catálogo maestro | ✅ 3NF |
| **Productos** | 1K-10K | Inventario | ✅ 3NF |
| **Clientes** | Creciente | Datos cliente | ✅ 3NF |
| **Pedidos** | Creciente | Transacciones | ✅ 3NF (con desnormalización justificada) |
| **Linea_Pedidos** | N × Pedidos | Detalles | ✅ 3NF |
| **Pagos** | ≥ Pedidos | Auditoría transacciones | ✅ 3NF |
| **Reseñas** | Creciente | Opinions/Feedback | ✅ 3NF |

### Complejidad de Relaciones

- **Tablas maestro (0 FK):** Paises, Categoria_Productos
- **Tablas referencial (1-2 FK):** Productos, Clientes, Reseñas
- **Tablas transaccionales (2-3 FK):** Pedidos, Linea_Pedidos, Pagos
- **Tabla de asociación (2 FK):** Linea_Pedidos

---

## Consideraciones Futuras

### Posibles Mejoras para Escala

1. **Desnormalización de direcciones:**
   ```
   CREATE TABLE Direcciones (
     IdDireccion INT PK,
     Calle STRING,
     Numero INT,
     Piso STRING,
     CodigoPostal INT,
     Ciudad STRING,
     IdPais INT FK
   )
   ```

2. **Historial de cambios:**
   ```
   CREATE TABLE Cambios_Productos (
     IdCambio INT PK,
     IdProducto INT FK,
     Precio_anterior INT,
     Precio_nuevo INT,
     Fecha DATETIME
   )
   ```

3. **Tablas de dimensiones para analytics:**
   ```
   Dim_Tiempo, Dim_Metodo_Envio, Dim_Metodo_Pago
   para facilitar análisis OLAP
   ```

---

## Conclusión

La base de datos **Temuzon** cumple con **normalización 3NF** manteniendo:
- ✅ Integridad referencial mediante foreign keys
- ✅ Eliminación de redundancia innecesaria
- ✅ Flexibilidad para consultas comunes
- ⚠️ Desnormalización controlada en puntos críticos de auditoría y rendimiento

Las decisiones de diseño priorizan:
1. **Auditoría y cumplimiento:** Historial de precios, direcciones, transacciones
2. **Rendimiento:** Subtotales precalculados, País en Pedidos para rápido cálculo de IVA
3. **Escalabilidad:** Tablas maestro separadas, sin dependencias cíclicas
4. **Integridad:** Foreign keys no nulas donde sea crítico, cascadas de borrado inteligentes
