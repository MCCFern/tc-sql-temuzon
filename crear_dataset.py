from google.cloud import bigquery
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("BQ_DATASET_ID")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Cliente autenticado
credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_PATH
)
client = bigquery.Client(
    project=PROJECT_ID,
    credentials=credentials
)

# Crear dataset
dataset_ref = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
dataset_ref.location = "EU"  # Datos en Europa
dataset = client.create_dataset(dataset_ref, exists_ok=True)
print(f"Dataset {DATASET_ID} creado")