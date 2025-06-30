import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME')

# Load CSV
df = pd.read_csv('data/degustations_var0.csv', sep=';')

# Create connection string
conn_str = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(conn_str)


# Push to table
df.to_sql('raw_degustation_data', engine, schema='public', if_exists='replace', index=False)

print("CSV with raw data loaded into PostgreSQL successfully.")
