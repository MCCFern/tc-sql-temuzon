from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "ds-temuzon")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID", "temuzon")

client = bigquery.Client(project=GCP_PROJECT_ID)

def crear_tabla(nombre, schema):
    table_ref = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{nombre}"
    table = bigquery.Table(table_ref, schema=schema)
    table = client.create_table(table, exists_ok=True)
    print(f"Tabla {nombre} creada")


# ─── Tablas catálogo (sin dependencias) ────────────────────────────

schema_paises = [
    bigquery.SchemaField("id_pais", "INT64", mode="REQUIRED"),
    bigquery.SchemaField("nombre",  "STRING", mode="REQUIRED"),
    bigquery.SchemaField("iva",     "FLOAT64", mode="REQUIRED"),
]

schema_categoria_productos = [
    bigquery.SchemaField("id_categoria", "INT64",  mode="REQUIRED"),
    bigquery.SchemaField("nombre",       "STRING", mode="REQUIRED"),
    bigquery.SchemaField("descripcion",  "STRING", mode="NULLABLE"),
]

# ─── Tablas con FK a catálogos ─────────────────────────────────────

schema_clientes = [
    bigquery.SchemaField("id_cliente",         "INT64",  mode="REQUIRED"),
    bigquery.SchemaField("nombre",             "STRING", mode="REQUIRED"),
    bigquery.SchemaField("apellidos",          "STRING", mode="REQUIRED"),
    bigquery.SchemaField("direccion",          "STRING", mode="NULLABLE"),
    bigquery.SchemaField("codigo_postal",      "STRING", mode="NULLABLE"),
    bigquery.SchemaField("ciudad",             "STRING", mode="NULLABLE"),
    bigquery.SchemaField("pais",               "INT64",  mode="NULLABLE"),  # FK paises
    bigquery.SchemaField("num_identificacion", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("email",              "STRING", mode="REQUIRED"),
    bigquery.SchemaField("telefono",           "STRING", mode="NULLABLE"),
    bigquery.SchemaField("canal_adquisicion",  "STRING", mode="NULLABLE"),
]

schema_productos = [
    bigquery.SchemaField("id_producto",   "INT64",   mode="REQUIRED"),
    bigquery.SchemaField("id_categoria",  "INT64",   mode="NULLABLE"),  # FK categoria_productos
    bigquery.SchemaField("nombre",        "STRING",  mode="REQUIRED"),
    bigquery.SchemaField("precio_venta",  "FLOAT64", mode="REQUIRED"),
    bigquery.SchemaField("coste",         "FLOAT64", mode="NULLABLE"),
    bigquery.SchemaField("stock",         "INT64",   mode="REQUIRED"),
    bigquery.SchemaField("estado",        "STRING",  mode="REQUIRED"),
]

# ─── Pedidos y dependientes ────────────────────────────────────────

schema_pedidos = [
    bigquery.SchemaField("id_pedido",       "INT64",    mode="REQUIRED"),
    bigquery.SchemaField("id_cliente",      "INT64",    mode="REQUIRED"),  # FK clientes
    bigquery.SchemaField("estado_pedido",   "STRING",   mode="REQUIRED"),
    bigquery.SchemaField("cantidad",        "FLOAT64",    mode="REQUIRED"),
    bigquery.SchemaField("direccion_envio", "STRING",   mode="NULLABLE"),
    bigquery.SchemaField("codigo_postal",   "STRING",   mode="NULLABLE"),
    bigquery.SchemaField("ciudad_envio",    "STRING",   mode="NULLABLE"),
    bigquery.SchemaField("pais_envio",      "INT64",    mode="NULLABLE"),  # FK paises
    bigquery.SchemaField("metodo_envio",    "STRING",   mode="NULLABLE"),
    bigquery.SchemaField("fecha_envio",     "DATETIME", mode="NULLABLE"),
    bigquery.SchemaField("fecha_reparto",   "DATETIME", mode="NULLABLE"),
    bigquery.SchemaField("notas",           "STRING",   mode="NULLABLE"),
]

schema_linea_pedidos = [
    bigquery.SchemaField("id_orden_pedido",      "INT64",   mode="REQUIRED"),
    bigquery.SchemaField("id_pedido",            "INT64",   mode="REQUIRED"),  # FK pedidos
    bigquery.SchemaField("id_producto",          "INT64",   mode="REQUIRED"),  # FK productos
    bigquery.SchemaField("cantidad",             "INT64",   mode="REQUIRED"),
    bigquery.SchemaField("precio_unidad",        "FLOAT64", mode="REQUIRED"),
    bigquery.SchemaField("porcentaje_descuento", "FLOAT64", mode="NULLABLE"),
    bigquery.SchemaField("subtotal",             "FLOAT64",   mode="REQUIRED"),
]

schema_pagos = [
    bigquery.SchemaField("id_pago",         "INT64",    mode="REQUIRED"),
    bigquery.SchemaField("id_pedido",       "INT64",    mode="REQUIRED"),  # FK pedidos
    bigquery.SchemaField("cantidad",        "FLOAT64",    mode="REQUIRED"),
    bigquery.SchemaField("metodo_pago",     "STRING",   mode="REQUIRED"),
    bigquery.SchemaField("estado",          "STRING",   mode="REQUIRED"),
    bigquery.SchemaField("fecha_cobro",     "DATETIME", mode="NULLABLE"),
    bigquery.SchemaField("fecha_reembolso", "DATETIME", mode="NULLABLE"),
]

schema_resenas = [
    bigquery.SchemaField("id_resena",       "INT64",  mode="REQUIRED"),
    bigquery.SchemaField("id_orden_pedido", "INT64",  mode="REQUIRED"),  # FK linea_pedidos
    bigquery.SchemaField("id_cliente",      "INT64",  mode="REQUIRED"),  # FK clientes
    bigquery.SchemaField("valoracion",      "INT64",  mode="REQUIRED"),
    bigquery.SchemaField("comentario",      "STRING", mode="NULLABLE"),
]




# ─── Creación en orden de dependencias ─────────────────────────────

tablas = [
    ("paises",              schema_paises),
    ("categoria_productos", schema_categoria_productos),
    ("clientes",            schema_clientes),
    ("productos",           schema_productos),
    ("pedidos",             schema_pedidos),
    ("linea_pedidos",       schema_linea_pedidos),
    ("pagos",               schema_pagos),
    ("resenas",             schema_resenas),
]

for nombre, schema in tablas:
    crear_tabla(nombre, schema)



ddl_constraints = """
ALTER TABLE `ds-temuzon.Temuzon.paises`              ADD PRIMARY KEY (id_pais)         NOT ENFORCED;
ALTER TABLE `ds-temuzon.Temuzon.categoria_productos` ADD PRIMARY KEY (id_categoria)    NOT ENFORCED;
ALTER TABLE `ds-temuzon.Temuzon.clientes`            ADD PRIMARY KEY (id_cliente)      NOT ENFORCED;
ALTER TABLE `ds-temuzon.Temuzon.productos`           ADD PRIMARY KEY (id_producto)     NOT ENFORCED;
ALTER TABLE `ds-temuzon.Temuzon.pedidos`             ADD PRIMARY KEY (id_pedido)       NOT ENFORCED;
ALTER TABLE `ds-temuzon.Temuzon.linea_pedidos`       ADD PRIMARY KEY (id_orden_pedido) NOT ENFORCED;
ALTER TABLE `ds-temuzon.Temuzon.pagos`               ADD PRIMARY KEY (id_pago)         NOT ENFORCED;
ALTER TABLE `ds-temuzon.Temuzon.resenas`             ADD PRIMARY KEY (id_resena)       NOT ENFORCED;

ALTER TABLE `ds-temuzon.Temuzon.clientes`      ADD CONSTRAINT fk_clientes_pais       FOREIGN KEY (pais)            REFERENCES `ds-temuzon.Temuzon.paises`(id_pais)                       NOT ENFORCED;
ALTER TABLE `ds-temuzon.Temuzon.productos`     ADD CONSTRAINT fk_productos_categoria FOREIGN KEY (id_categoria)    REFERENCES `ds-temuzon.Temuzon.categoria_productos`(id_categoria)     NOT ENFORCED;
ALTER TABLE `ds-temuzon.Temuzon.pedidos`       ADD CONSTRAINT fk_pedidos_cliente     FOREIGN KEY (id_cliente)      REFERENCES `ds-temuzon.Temuzon.clientes`(id_cliente)                  NOT ENFORCED;
ALTER TABLE `ds-temuzon.Temuzon.pedidos`       ADD CONSTRAINT fk_pedidos_pais_envio  FOREIGN KEY (pais_envio)      REFERENCES `ds-temuzon.Temuzon.paises`(id_pais)                       NOT ENFORCED;
ALTER TABLE `ds-temuzon.Temuzon.linea_pedidos` ADD CONSTRAINT fk_linea_pedido        FOREIGN KEY (id_pedido)       REFERENCES `ds-temuzon.Temuzon.pedidos`(id_pedido)                    NOT ENFORCED;
ALTER TABLE `ds-temuzon.Temuzon.linea_pedidos` ADD CONSTRAINT fk_linea_producto      FOREIGN KEY (id_producto)     REFERENCES `ds-temuzon.Temuzon.productos`(id_producto)                NOT ENFORCED;
ALTER TABLE `ds-temuzon.Temuzon.pagos`         ADD CONSTRAINT fk_pagos_pedido        FOREIGN KEY (id_pedido)       REFERENCES `ds-temuzon.Temuzon.pedidos`(id_pedido)                    NOT ENFORCED;
ALTER TABLE `ds-temuzon.Temuzon.resenas`       ADD CONSTRAINT fk_resenas_linea       FOREIGN KEY (id_orden_pedido) REFERENCES `ds-temuzon.Temuzon.linea_pedidos`(id_orden_pedido)        NOT ENFORCED;
ALTER TABLE `ds-temuzon.Temuzon.resenas`       ADD CONSTRAINT fk_resenas_cliente     FOREIGN KEY (id_cliente)      REFERENCES `ds-temuzon.Temuzon.clientes`(id_cliente)                  NOT ENFORCED;
"""

dataset = client.get_dataset(f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}")
print(f"client.project = {client.project}")
print(f"dataset.full_dataset_id = {dataset.full_dataset_id}")
print(f"dataset.location = {dataset.location}")



print(f"Dataset en: {dataset.location}")  # ara confirmar
job = client.query(ddl_constraints, location=dataset.location)
job.result()
print("Restricciones añadidas")