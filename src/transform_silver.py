import pandas as pd
from logger import get_logger
from pathlib import Path
from sqlalchemy import create_engine
import unicodedata
import numpy as np

logger = get_logger(__name__)

BRONZE_DB_PATH = Path("data/raw/olist_bronze.db")
SILVER_DB_PATH = Path("data/silver/olist_silver.db")

def con_bronze_db():
    return create_engine(f'sqlite:///{BRONZE_DB_PATH}')

def con_silver_db():
    return create_engine(f'sqlite:///{SILVER_DB_PATH}')

def remove_acentos(texto):
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')

def transform_customers(con_db_leitura, con_db_escrita):
    df = pd.read_sql("SELECT * FROM customers", con_db_leitura)
    df['customer_city'] = df['customer_city'].str.title().str.strip()
    df['customer_state'] = df['customer_state'].str.upper().str.strip()
    df['customer_zip_code_prefix'] = df['customer_zip_code_prefix'].astype(str).str.zfill(5)
    df.to_sql('customers', con_db_escrita, if_exists='replace', index=False)
    logger.info(f"Limpeza de customers realizada!")

def transform_geolocation(con_db_leitura, con_db_escrita):
    df = pd.read_sql("SELECT * FROM geolocation", con_db_leitura)
    df = df.drop_duplicates()
    df['geolocation_city'] = df['geolocation_city'].apply(remove_acentos).str.title().str.strip()
    df['geolocation_city'] = np.where(df['geolocation_city'].str.len() < 3, None, df['geolocation_city'])
    df['geolocation_zip_code_prefix'] = df['geolocation_zip_code_prefix'].astype(str).str.zfill(5)
    df.to_sql('geolocation', con_db_escrita, if_exists='replace', index=False)
    logger.info(f"Limpeza de geolocation realizada!")

def transform_order_items(con_db_leitura, con_db_escrita):
    df = pd.read_sql("SELECT * FROM order_items", con_db_leitura)
    df['shipping_limit_date'] = pd.to_datetime(df['shipping_limit_date'])
    df.to_sql('order_items', con_db_escrita, if_exists='replace', index=False)
    logger.info(f"Limpeza de order_items realizada!")

def transform_order_payments(con_db_leitura, con_db_escrita):
    df = pd.read_sql("SELECT * FROM order_payments", con_db_leitura)
    df['payment_suspicious'] = np.where(
        (df['payment_value'] == 0) | (df['payment_type'] == 'not_defined'),
        True, False)
    df.to_sql('order_payments', con_db_escrita, if_exists='replace', index=False)
    logger.info(f"Limpeza de order_payments realizada!")

def transform_order_reviews(con_db_leitura, con_db_escrita):
    df = pd.read_sql("SELECT * FROM order_reviews", con_db_leitura)
    df['review_comment_title'] = df['review_comment_title'].str.strip().str.capitalize()
    df['review_comment_message'] = df['review_comment_message'].str.strip().str.capitalize()
    df["review_creation_date"] = pd.to_datetime(df['review_creation_date'])
    df['review_answer_timestamp'] = pd.to_datetime(df['review_answer_timestamp'])
    df['review_comment_title'] = df['review_comment_title'].fillna("Não Preenchido")
    df['review_comment_message'] = df['review_comment_message'].fillna("Não Preenchido")
    df.to_sql('order_reviews', con_db_escrita, if_exists='replace', index=False)
    logger.info(f"Limpeza de order_reviews realizada!")

def transform_orders(con_db_leitura, con_db_escrita):
    df = pd.read_sql("SELECT * FROM orders", con_db_leitura)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'])
    df['order_delivered_carrier_date'] = pd.to_datetime(df['order_delivered_carrier_date'])
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
    df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'])
    df.to_sql('orders', con_db_escrita, if_exists='replace', index=False)
    logger.info(f"Limpeza de orders realizada!")

def transform_product_category_translations(con_db_leitura, con_db_escrita):
    df = pd.read_sql("SELECT * FROM product_category_translation", con_db_leitura)
    df.to_sql('product_category_translation',con_db_escrita, if_exists='replace', index=False)
    logger.info(f"Limpeza de product_category_translation realizada!")

def transform_products(con_db_leitura, con_db_escrita):
    df = pd.read_sql('SELECT * FROM products', con_db_leitura)
    df['product_category_name'] = df['product_category_name'].fillna("Não Preenchido")
    df.to_sql('products', con_db_escrita, if_exists='replace', index=False)
    logger.info(f"Limpeza de products realizada!")

def transform_sellers(con_db_leitura, con_db_escrita):
    df = pd.read_sql("SELECT * FROM sellers", con_db_leitura)
    df['seller_zip_code_prefix'] = df['seller_zip_code_prefix'].astype(str).str.zfill(5)
    df['seller_city'] = df['seller_city'].apply(remove_acentos).str.title().str.strip()
    df['seller_city'] = np.where(
        (df['seller_city'].str.len() < 3) |
        (df['seller_city'].str.contains('-')) |
        (df['seller_city'].str.contains(r'\\')) |
        (df['seller_city'].str.contains('/')) |
        (df['seller_city'].str.contains('@')),
        None, df['seller_city'])
    df.to_sql('sellers', con_db_escrita, if_exists='replace', index=False)
    logger.info(f"Limpeza de sellers realizada!")

def run_transformation():
    logger.info("Iniciando limpeza!")

    bronze_db = con_bronze_db()
    silver_db = con_silver_db()

    transform_orders(bronze_db, silver_db)
    transform_products(bronze_db, silver_db)
    transform_sellers(bronze_db, silver_db)
    transform_order_payments(bronze_db, silver_db)
    transform_product_category_translations(bronze_db, silver_db)
    transform_order_reviews(bronze_db, silver_db)
    transform_geolocation(bronze_db, silver_db)
    transform_order_items(bronze_db, silver_db)
    transform_customers(bronze_db, silver_db)

    logger.info('Limpeza concluída!')

if __name__ == "__main__":
    run_transformation()