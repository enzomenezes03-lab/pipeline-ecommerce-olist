import pandas as pd
from logger import get_logger
from pathlib import Path
from sqlalchemy import create_engine
import numpy as np

logger = get_logger(__name__)

SILVER_DB_PATH = Path('data/silver/olist_silver.db')
GOLD_DB_PATH = Path('data/gold/olist_gold.db')

def connection_silver():
    return create_engine(f'sqlite:///{SILVER_DB_PATH}')

def connection_gold():
    return create_engine(f'sqlite:///{GOLD_DB_PATH}')

def transform_fact_orders(con_db_leitura, con_db_escrita):
    df = pd.read_sql('''WITH 
    unique_oi as (
        SELECT 
        oi.order_id as o_id,
        SUM(oi.freight_value) as sum_freight
        FROM order_items oi
        GROUP BY oi.order_id
    ),
    most_distant_seller as (
        SELECT 
        oi.order_id,
        MAX(oi.seller_id) max_sid
        FROM order_items oi
        LEFT JOIN (
        SELECT
        oi.order_id,
        MAX(oi.freight_value) as max_freight
        FROM order_items oi
        GROUP BY oi.order_id
        ) as sub
        ON oi.order_id = sub.order_id AND oi.freight_value = sub.max_freight
        GROUP BY oi.order_id
    )
    SELECT
    o.order_id as id,  
    ROUND(JULIANDAY(o.order_approved_at ) - JULIANDAY(o.order_purchase_timestamp), 0) as aprov_time_days,
    ROUND(JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp), 0) as deliver_time_days,
    CASE
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN TRUE 
        ELSE FALSE 
    END as late,
    uoi.sum_freight,
    AVG(ow.review_score) as avg_review_score, 
    c.customer_state,
    s.seller_state
    FROM orders o
    LEFT JOIN unique_oi uoi
    ON uoi.o_id = o.order_id
    LEFT JOIN order_reviews ow
    ON ow.order_id = o.order_id
    LEFT JOIN customers c 
    ON o.customer_id = c.customer_id 
    LEFT JOIN most_distant_seller mds
    ON o.order_id = mds.order_id
    LEFT JOIN sellers s
    ON s.seller_id = mds.max_sid
    GROUP BY 
    o.order_id, 
    uoi.sum_freight, 
    c.customer_state,
    s.seller_state''', con_db_leitura)
    df.to_sql('fact_orders', con_db_escrita, if_exists='replace', index=False)
    logger.info('Tabela fact_orders construída!')

def run_transformation():
    logger.info('Iniciando transformação Gold!')
    con_silver = connection_silver()
    con_gold = connection_gold()

    transform_fact_orders(con_silver, con_gold)
    logger.info('Transformação Gold concluída!')

if __name__ == '__main__':
    run_transformation()