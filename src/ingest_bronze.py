import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
from src.logger import get_logger

logger = get_logger(__name__)

RAW_DIR = Path("data/raw")
DB_PATH = Path("data/raw/olist_bronze.db")

tabelas = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "product_category_translation": "product_category_name_translation.csv",
}

def get_engine():
    return create_engine(f"sqlite:///{DB_PATH}")

def load_csv(csv_path):
    df = pd.read_csv(csv_path)
    logger.info(f"Arquivo {csv_path} lido com sucesso! {len(df)} linhas.")
    return df

def save_to_bronze(data_frame, engine, table_name):
    data_frame.to_sql(table_name, con=engine, if_exists="replace", index=False)
    logger.info(f"Data Frame: {table_name} salvo com sucesso!")

def run_ingestion():
    logger.info("Iniciando ingestão bronze!")
    conexao = get_engine()
    for k, v in tabelas.items():
        caminho_csv = RAW_DIR / v
        data_frame  = load_csv(caminho_csv)
        save_to_bronze(data_frame, conexao, k)
    logger.info("Ingestão concluída!")

if __name__ == "__main__":
    run_ingestion()
