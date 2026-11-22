import logging
import os
import joblib
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, root_mean_squared_error, r2_score

logging.basicConfig(level= logging.INFO,
                    format= "%(asctime)s - %(levelname)s - %(message)s")

logger= logging.getLogger()

df= pd.read_csv('data/raw/ssd.csv')
X= df.drop('expenses', axis= 1)

y= df['expenses']
X_train, X_test, y_train, y_test= train_test_split(X,y, test_size=0.2, random_state= 42)
logger.info('train test split has been executed')
num_cols= X.select_dtypes(include= ['int64', 'float64']).columns
cat_cols= X.select_dtypes(include= ['object']).columns
num_pipelines= Pipeline([
    ('impute', SimpleImputer(strategy= 'median')),
    ('scaler', StandardScaler())
])
cat_pipelines= Pipeline([
    ('impute', SimpleImputer(strategy= 'most_frequent')),
    ('encoder', OneHotEncoder())
])
preprocessing= ColumnTransformer([
    ('num', num_pipelines, num_cols),
    ('cat', cat_pipelines, cat_cols)
])
models= {
    'Decision Tree': DecisionTreeRegressor(),
    'Random Forest': RandomForestRegressor(),
    'Gradient Boosting': GradientBoostingRegressor(),
    'XG Boost': XGBRegressor()
}
best_mdoel= None
best_model_name= None
best_rmse= float('inf')

mlflow.set_tracking_uri('http://127.0.0.1:5000')
mlflow.set_experiment('Insurence App')

for model_name, model in models.items():
    pipeline= Pipeline([
        ('preprocessing', preprocessing),
        ('model', model)
    ])
    pipeline.fit(X_train, y_train)
    y_pred= pipeline.predict(X_test)

    with mlflow.start_run(run_name= model_name):
        logger.info('mlflow run has started')
        mae= mean_absolute_error(y_test, y_pred)
        mse= mean_squared_error(y_test, y_pred)
        rmse= root_mean_squared_error(y_test, y_pred)
        r2= r2_score(y_test, y_pred)
        print('mean absolute error', mae)
        print('mean squared error', mse)
        print('root mean squared error', rmse)

        mlflow.log_param('model name', model_name)
        mlflow.log_metric('mae', mae)
        mlflow.log_metric('mse', mse)
        mlflow.log_metric('rmse', rmse)
        mlflow.log_metric('r2_score', r2)

        mlflow.sklearn.log_model(serialization_format= 'cloudpickle', artifact_path= 'model', sk_model= pipeline)
        if rmse< best_rmse:
            best_rmse= rmse
            best_mdoel= pipeline
            best_model_name= model_name

os.makedirs('models', exist_ok= True)
joblib.dump(best_mdoel, 'models/best_models.pkl')