# tc-sql-temuzon

![Logo_Temuzon](./notebooks/temuzon_logo.jpg)


# 📊 E-commerce Data Pipeline con BigQuery

Proyecto formativo de generación, carga y análisis de **datos sintéticos de comercio electrónico generados con Faker**, utilizando Google BigQuery como almacén de datos. Los importes y clientes del ejercicio no corresponden a la actividad real de una empresa.

---

## Objetivo

Construir una base de datos analítica en la nube con datos generados por faker y realizar consultas SQL para extraer información sobre el negocio como:

- Clientes por país
- Productos más vendidos
- Ingresos mensuales
- Tiempo medio de envío
- Valoración media de clientes
- Análisis de canales de adquisición

---

## 🏗️ Arquitectura del proyecto

El proyecto sigue la siguiente estructura:

```
tc-sql-Temuzon/
```

### 📂 data/
Vacío. Los datos se encuentran en BigQuery.

### 📂 docs/
Documentación del modelo de datos y diagrama de normalización. El diagrama se creó con [dbdiagram](https://dbdiagram.io/). También se encuentra el archivo Markdown con la información de la normalización de los datos.
- `normalization.md` → modelo relacional y análisis de 3NF
- `bi_looker_studio.md` → ejercicio de Business Intelligence: pregunta de negocio, canvas de KPIs, insights y guion del dashboard de Looker Studio

### 📂 sql/
Consultas listas para pegar en Looker Studio como *consulta personalizada* sobre BigQuery:
- `looker_ventas_lineas.sql` → fuente principal, grano línea de pedido (KPIs comerciales)
- `looker_pedidos.sql` → fuente secundaria, grano pedido (métricas logísticas sin sesgo de grano)

### 📂 notebooks/
Notebooks de análisis:
- `queries_verification.ipynb` → Archivo con las queries utilizadas para verificar el correcto funcionamiento de la conexión con BigQuery
- SQL Murder Mystery (primera parte del Team Challenge)
- `creacion_dataset_tablas.ipynb` → Configuración inicial de las tablas en BigQuery
- `datos_faker.ipynb` → Generación de datos con faker

### 🔐 credentials/
⚠️ No incluido en el repositorio por seguridad.

### 📄 Archivos base
- `.env.example` → variables de entorno de ejemplo  
- `.gitignore` → archivos ignorados por Git  
- `README.md` → documentación principal  
- `requirements.txt` → dependencias del proyecto  


## 🛠️ Tecnologías utilizadas

- Google BigQuery
- Python
- pandas
- faker
- python-dotenv
- pyarrow
- db-dtypes
- google-cloud-bigquery

---

## 🖥️ ¿Cómo realizar una consulta a una base de datos almacenada en BigQuery?

Usaremos de ejemplo las tablas presentes en nuestra base de datos de Temuzon.

### 1. Se debe crear el entorno virtual donde instalar las dependencias descritas en requirements.txt

```python
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar las variables de entorno

Será necesario completar los datos con los específicos del proyecto al que se pueda acceder y de la localización del archivo de credenciales .json. Si se quiere revisar la estructura concreta y la estrategia de generación y estructura de los datos, consultar la carpeta del repositorio scripts/.

Una vez solventado, estas serán las variables de entorno (.env) que se crearán para asegurar la conexión con la base de datos:

GCP_PROJECT_ID=your_project_id

BQ_DATASET_ID=your_dataset_id

GOOGLE_APPLICATION_CREDENTIALS=ruta_a_credentials.json

### 3. Realizar las queries para analizar los datos

Para ver ejemplos de ejecución, revisar notebooks/queries_verification.ipynb

## Dashboard y revisión sin acceso a BigQuery

El diseño del dashboard, sus KPIs, decisiones de agregación y límites del dato
están documentados en [el ejercicio de BI](docs/bi_looker_studio.md).
Las fuentes SQL están en [ventas por línea](sql/looker_ventas_lineas.sql) y
[pedidos](sql/looker_pedidos.sql). La guía está en
[Guía de referencia de Looker Studio](docs/Guia_Referencia_Looker_Studio.html).

Estos archivos permiten revisar el diseño, pero no acreditan un dashboard
publicado y terminado. Este repositorio todavía no incluye un enlace verificado
ni capturas de ese dashboard. Los logotipos y las imágenes de soluciones SQL no
deben interpretarse como capturas del informe de BI.
