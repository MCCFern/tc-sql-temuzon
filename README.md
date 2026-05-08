# tc-sql-temuzon
Projecto grupal de SLQ para The Bridge DS
![Logo_Temuzon](./notebooks/temuzon_logo.jpg)


# 📊 E-commerce Data Pipeline con BigQuery

Este proyecto implementa un flujo completo de generación, carga y análisis de datos de un sistema e-commerce utilizando Google BigQuery como almacén de datos.

---

## Objetivo

Construir una base de datos analítica en la nube con datos generados por faker y realizar consultas SQL para extraer información sore el negocio como:

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
Documentación del modelo de datos y diagrama de normalización. El diagrama se creó con [dbdiagram](https://dbdiagram.io/). También se encuentra el archivo marckdown con la información de la normalización de los datos.

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

### 1. Se debe crear el entrono virtual donde instalar las dependencias descritas en requirements.txt

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