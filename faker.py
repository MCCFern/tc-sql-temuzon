import os
import pandas as pd
import random
from faker import Faker
from datetime import timedelta
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "ds-temuzon")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID", "temuzon")

client = bigquery.Client(project=GCP_PROJECT_ID)
fake = Faker('es_ES')
Faker.seed(42)
random.seed(42)

#1.PAISES
paises_lista = []
nombres_vistos = set()
while len(paises_lista) < 10:
    nombre_p = fake.country()
    if nombre_p not in nombres_vistos:
        paises_lista.append({
            'id_pais': len(paises_lista) + 1,
            'nombre': nombre_p,
            'iva': random.choice([16, 18, 19, 21, 23, 25])
        })
        nombres_vistos.add(nombre_p)
df_paises = pd.DataFrame(paises_lista)

#2.CATEGORIAS_PRODUCTOS
categorias_list = ['smartphones', 'laptops', 'perifericos', 'wearables', 'audio']
df_categoria_productos = pd.DataFrame([
    {'id_categoria': i, 'nombre': cat, 'descripción': fake.sentence()} 
    for i, cat in enumerate(categorias_list, 1)
])

#3.CLIENTES
clientes = []
canales = ['organico', 'publicidad_de_pago', 'redes_sociales', 'directo', 'referido']
for i in range(1, 501):
    clientes.append({
        'id_cliente': i,
        'nombre': fake.first_name(),
        'apellidos': fake.last_name(),
        'direccion': fake.street_address(),
        'codigo_postal': fake.postcode(),
        'ciudad': fake.city(),
        'pais': random.choice(df_paises['id_pais']),
        'n_identificacion': fake.dni(),
        'email': fake.email(),
        'telefono': fake.phone_number(),
        'canal_de_adquisicion': random.choice(canales)
    })
df_clientes = pd.DataFrame(clientes)

#4.PRODUCTOS
productos = []
for i in range(1, 71):
    coste = round(random.uniform(40.0, 600.0), 2)
    productos.append({
        'id_producto': i,
        'id_categoria': random.choice(df_categoria_productos['id_categoria']),
        'nombre': f"Tech {fake.word().capitalize()}",
        'precio_de_venta': round(coste * random.uniform(1.2, 1.7), 2),
        'coste': coste,
        'stock': random.randint(5, 150),
        'estado': random.choice(['activo', 'activo', 'inactivo'])
    })
df_productos = pd.DataFrame(productos)
mapa_precios = df_productos.set_index('id_producto')['precio_de_venta'].to_dict()
#5.PEDIDOS
pedidos = []
estados_ped = ['pendiente', 'enviado', 'entregado', 'cancelado']
for i in range(1, 2001):
    f_pedido = fake.date_between(start_date='-1y', end_date='today')
    pedidos.append({
        'id_pedido': i,
        'id_cliente': random.choice(df_clientes['id_cliente']),
        'estado_pedido': random.choices(estados_ped, weights=[10, 20, 60, 10])[0],
        'cantidad': 0, # Se actualizará con la suma de lineas
        'direccion_de_envio': fake.street_address(),
        'codigo_postal': fake.postcode(),
        'ciudad_de_envio': fake.city(),
        'pais_de_envio': random.choice(df_paises['id_pais']),
        'metodo_de_envio': random.choice(['Estándar', 'Express']),
        'fecha_de_envio': f_pedido + timedelta(days=random.randint(1, 2)),
        'fecha_de_reparto': f_pedido + timedelta(days=random.randint(3, 5)),
        'notas': fake.sentence() if random.random() > 0.8 else ""
    })
df_pedidos = pd.DataFrame(pedidos)

#6.LINEA_PEDIDOS
lineas = []
id_linea_acc = 1
for p_id in df_pedidos['id_pedido']:
    items_en_pedido = 0
    for _ in range(random.randint(1, 3)):
        prod_id = random.choice(df_productos['id_producto'])
        cant = random.randint(1, 2)
        precio_u = mapa_precios[prod_id]
        desc_pct = random.choice([0, 0, 5, 10])
        
        subtotal = (precio_u * cant) * (1 - desc_pct/100)
        
        lineas.append({
            'id_orden_pedido': id_linea_acc,
            'id_pedido': p_id,
            'id_producto': prod_id,
            'cantidad': cant,
            'precio_unidad': precio_u,
            'porcentaje_descuento': desc_pct,
            'subtotal': round(subtotal, 2)
        })
        items_en_pedido += cant
        id_linea_acc += 1
    # Actualizar cantidad total en la tabla de pedidos
    df_pedidos.loc[df_pedidos['id_pedido'] == p_id, 'cantidad'] = items_en_pedido

df_lineas = pd.DataFrame(lineas)

#7.PAGOS
pagos = []
for i, row in df_pedidos.iterrows():
    monto_total = df_lineas[df_lineas['id_pedido'] == row['id_pedido']]['subtotal'].sum()
    pagos.append({
        'id_pago': i + 1,
        'id_pedido': row['id_pedido'],
        'cantidad': round(monto_total, 2),
        'metodo_de_pago': random.choice(['Tarjeta', 'PayPal', 'Transferencia']),
        'estado': 'completado' if row['estado_pedido'] != 'cancelado' else 'reembolsado',
        'fecha_de_cobro': row['fecha_de_envio'],
        'fecha_de_reembolso': row['fecha_de_reparto'] if row['estado_pedido'] == 'cancelado' else None
    })
df_pagos = pd.DataFrame(pagos)

#8.RESEÑAS
resenas_sample = df_lineas.sample(frac=0.3)
resenas = []
for i, (idx, row) in enumerate(resenas_sample.iterrows(), 1):
    resenas.append({
        'id_reseña': i,
        'id_orden_pedido': row['id_orden_pedido'],
        'id_cliente': df_pedidos.loc[df_pedidos['id_pedido'] == row['id_pedido'], 'id_cliente'].values[0],
        'valoracion': random.randint(1, 5),
        'comentario': fake.text(max_nb_chars=120)
    })
df_resenas = pd.DataFrame(resenas)


# CARGA A BIGQUERY
def subir_a_bq(df, nombre_tabla):
    # Convertir todas las fechas a formato DATE para BigQuery
    for col in df.columns:
        if 'fecha' in col:
            df[col] = pd.to_datetime(df[col]).dt.date
            
    id_tabla_full = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{nombre_tabla}"
    config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    
    print(f"Cargando {nombre_tabla}...")
    tarea = client.load_table_from_dataframe(df, id_tabla_full, job_config=config)
    tarea.result()
    print(f"✅ {len(df)} filas cargadas en {nombre_tabla}")

# Diccionario de tablas
tablas_finales = {
    "paises": df_paises,
    "categoria_productos": df_categoria_productos,
    "productos": df_productos,
    "clientes": df_clientes,
    "pedidos": df_pedidos,
    "linea_pedidos": df_lineas,
    "pagos": df_pagos,
    "resenas": df_resenas
}

for nombre, df_obj in tablas_finales.items():
    subir_a_bq(df_obj, nombre)