import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

def process_data(df):
    try:
        pattern = r'\b(\d{2}-\w{3}-\d{4})\b'
        date_series = pd.Series(df.to_string()).str.extract(pattern)
        report_date_str = pd.to_datetime(date_series[0], format='%d-%b-%Y').dt.strftime('%Y-%m-%d').iloc[0]

        start_location = np.where(df == 'SNo')
        row_num, col_num = start_location[0][0], start_location[1][0]
        df = df.iloc[row_num:, col_num:]
        df.columns = df.iloc[0]
        df = df.drop(df.index[0])

        df = df.dropna(axis=1, how='any')
        df['report_date'] = report_date_str
        # print(df)
        db_credentials = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_DATABASE')
        }

        engine = create_engine(f"postgresql://{db_credentials['user']}:{db_credentials['password']}@{db_credentials['host']}:{db_credentials['port']}/{db_credentials['database']}")
        df.to_sql('public.office_hours', con=engine, index=False, if_exists='append')

        return f"Data pushed successfully!"
    except Exception as e:
        return f"Error processing and pushing data: {str(e)}"

def get_insights_from_db():
    pass