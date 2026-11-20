from pathlib import Path
import pandas as pd
import boto3
from urllib.parse import urlparse
from io import BytesIO
import logging
import os

logging.basicConfig(
    level= logging.INFO,
    format= "%(asctime)s - %(levelname)s - %(message)s"
)
logger= logging.getLogger()

def load_data(source, source_type= "s3", query= None):
    try:
        s3_path= urlparse(source)
        bucket= s3_path.netloc
        key= s3_path.path.lstrip("/")

        s3= boto3.client("s3")
        response= s3.get_object(Bucket= bucket, Key= key)
        file_data= BytesIO(response["Body"].read())
        file_type= Path(key).suffix.lower()
        if file_type == ".csv":
            df= pd.read_csv(file_data)
        elif file_type in ['.xlsx', 'xls']:
            df= pd.read_excel(file_data)
        elif file_type == ".json":
            df= pd.read_json(file_data)        
        else:
            raise ValueError('Unsupported file type')
        if df.empty:
            raise ValueError('the dataset is empty')
        return df
    except Exception:
        logger.exception('Data ingestion failed')
        raise


if __name__== '__main__':
    df= load_data("s3://insurence-bucket-ssd023/insurance.csv")
    os.makedirs("data/ingested", exist_ok= True)
    os.makedirs("data/raw", exist_ok= True)

    df.to_csv("data/ingested/ssd.csv")
    df.to_csv("data/raw/ssd.csv")

    logger.info('Dataset loaded successfully')
