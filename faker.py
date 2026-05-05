#1.PAISES
paises_random = []
nombres_usados = set()

while len(paises_random) < 10:
    nombre_pais = fake.country()
    if nombre_pais not in nombres_usados:
        paises_random.append({
            'IdPais': len(paises_random) + 1,
            'Nombre': nombre_pais,
            'IVA': random.choice([16, 18, 19, 21, 23, 25]) # Asignamos IVA aleatorio
        })
        nombres_usados.add(nombre_pais)

df_paises = pd.DataFrame(paises_random)

#2.CATEGORIAS_PRODUCTOS
categorias_list = ['Smartphones', 'Laptops', 'Periféricos', 'Wearables', 'Audio']
df_categoria_productos = pd.DataFrame([
    {'IdCategoria': i, 'Nombre': cat, 'Descripción': fake.sentence()} 
    for i, cat in enumerate(categorias_list, 1)
])

#3.CLIENTES
clientes = []
for i in range(1, 501):
    clientes.append({
        'IdCliente': i,
        'Nombre': fake.first_name(),
        'Apellidos': fake.last_name(),
        'Dirección': fake.street_address(),
        'Codigo Postal': fake.postcode(), # Faker genera CP realista
        'Ciudad': fake.city(),
        'País': random.choice(df_paises['IdPais']),
        'Nº Identificacion': fake.dni(),
        'Email': fake.email(),
        'Telefono': fake.phone_number(),
        'Canal de adquisición': random.choice(['organic', 'paid ads', 'social media', 'direct'])
    })
df_clientes = pd.DataFrame(clientes)

#4.PRODUCTOS
productos = []
for i in range(1, 71):
    coste = round(random.uniform(50, 500), 2)
    productos.append({
        'IdProducto': i,
        'IdCategoria': random.choice(df_categoria_productos['IdCategoria']),
        'Nombre': f"Tech {fake.word().capitalize()}",
        'Precio de venta': round(coste * random.uniform(1.2, 1.7), 2),
        'Coste': coste,
        'Stock': random.randint(10, 200),
        'Estado': random.choice(['Activo', 'Inactivo'])
    })
df_productos = pd.DataFrame(productos)
precios_dict = df_productos.set_index('IdProducto')['Precio de venta'].to_dict()

#5.PEDIDOS
pedidos = []
for i in range(1, 2001):
    f_pedido = fake.date_between(start_date='-1y', end_date='today')
    pedidos.append({
        'IdPedido': i,
        'IdCliente': random.choice(df_clientes['IdCliente']),
        'Estado pedido': random.choice(['pending', 'shipped', 'delivered', 'cancelled']),
        'Cantidad': 0, # Se suma después
        'Dirección de envío': fake.street_address(),
        'Codigo Postal': fake.postcode(), # CP específico del envío
        'Ciudad de envío': fake.city(),
        'País de envío': random.choice(df_paises['IdPais']),
        'Método de envío': random.choice(['Standard', 'Express']),
        'Fecha de envío': f_pedido + timedelta(days=2),
        'Fecha de reparto': f_pedido + timedelta(days=5),
        'Notas': fake.sentence() if random.random() > 0.8 else ""
    })
df_pedidos = pd.DataFrame(pedidos)

#6.LINEA_PEDIDOS
lineas = []
acc_id = 1
for p_id in df_pedidos['IdPedido']:
    num_prods = random.randint(1, 3)
    total_items_pedido = 0
    for _ in range(num_prods):
        prod_id = random.choice(df_productos['IdProducto'])
        cantidad = random.randint(1, 2)
        precio_uni = precios_dict[prod_id]
        desc = random.choice([0, 5, 10]) #Porcentaje de descuento
        
        #Cálculo del subtotal: (Precio * Cantidad) - Descuento
        subtotal = (precio_uni * cantidad) * (1 - desc/100)
        
        lineas.append({
            'IdOrdenPedido': acc_id,
            'IdPedido': p_id,
            'IdProducto': prod_id,
            'Cantidad': cantidad,
            'Precio Unidad': precio_uni,
            'Porcentaje descuento': desc,
            'Subtotal': round(subtotal, 2)
        })
        total_items_pedido += cantidad
        acc_id += 1
    # Actualizar la cantidad total en el pedido
    df_pedidos.loc[df_pedidos['IdPedido'] == p_id, 'Cantidad'] = total_items_pedido

df_lineas = pd.DataFrame(lineas)

#7.PAGOS
pagos = []
for i, row in df_pedidos.iterrows():
    total_pago = df_lineas[df_lineas['IdPedido'] == row['IdPedido']]['Subtotal'].sum()
    pagos.append({
        'IdPago': i + 1,
        'IdPedido': row['IdPedido'],
        'Cantidad': round(total_pago, 2),
        'Metodo de pago': random.choice(['Tarjeta', 'PayPal']),
        'Estado': 'Completado' if row['Estado pedido'] != 'cancelled' else 'Reembolsado',
        'Fecha de cobro': row['Fecha de envío'],
        'Fecha de reembolso': row['Fecha de reparto'] if row['Estado pedido'] == 'cancelled' else None
    })
df_pagos = pd.DataFrame(pagos)

#8.RESEÑAS
reseñas_sample = df_lineas.sample(frac=0.3)
reseñas = []
for i, (idx, row) in enumerate(reseñas_sample.iterrows(), 1):
    reseñas.append({
        'IdReseña': i,
        'IdOrdenPedido': row['IdOrdenPedido'],
        'IdCliente': df_pedidos.loc[df_pedidos['IdPedido'] == row['IdPedido'], 'IdCliente'].values[0],
        'Valoración': random.randint(1, 5),
        'Comentario': fake.text(max_nb_chars=100)
    })
df_reseñas = pd.DataFrame(reseñas)


# CARGA A BIGQUERY


def cargar_bq(df, table_name):
    for col in df.columns:
        if 'Fecha' in col:
            df[col] = pd.to_datetime(df[col])
            
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"Cargada tabla: {table_name}")

tablas_dict = {
    "Paises": df_paises,
    "Categoria_Productos": df_categoria_productos,
    "Clientes": df_clientes,
    "Productos": df_productos,
    "Pedidos": df_pedidos,
    "Linea_Pedidos": df_lineas,
    "Pagos": df_pagos,
    "Reseñas": df_reseñas
}

for nombre, dataframe in tablas_dict.items():
    cargar_bq(dataframe, nombre)