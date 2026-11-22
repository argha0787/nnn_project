import joblib
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
import os
from prometheus_client import Counter, Histogram, make_asgi_app
import time

app= FastAPI(title ='Insurence App')
model= joblib.load(Path(__file__).resolve().parents[1]/'models'/'best_models.pkl')

class Info(BaseModel):
    age: int
    sex: str
    bmi: float
    children: int
    smoker: str
    region: str
    

REQUEST_COUNT= Counter(
    'api_request_total',
    'Total number of '
)
PREDICTION_COUNT= Counter(
    'predictions_total',
    'total number of predictions'
)
ERROR_COUNT= Counter(
    'prediction_error_total',
    'total number of errors in predictions'
)
PREDICTION_TIME= Histogram(
    'prediction_duration_second',
    'total time taken to generate predictions'
)

@app.get('/')
def home():
    return{
        'message': 'the app is running'
    }

@app.post('/predict')
def predictions(info: Info):
    try:
        REQUEST_COUNT.inc()
        data= pd.DataFrame([info.model_dump()])
        predict= model.predict(data)
        start_time= time.time()
        PREDICTION_TIME.observe(time.time() - start_time)
        PREDICTION_COUNT.inc()
        return{
            'message': float(predict[0])
        }

    except Exception:
        ERROR_COUNT.inc()
        raise    

metric_app= make_asgi_app()
app.mount('/metrics', metric_app)
