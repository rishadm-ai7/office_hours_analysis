import streamlit as st
import pandas as pd
import numpy as np

uploaded_files = st.file_uploader("Choose a Excel file", accept_multiple_files=True)

for uploaded_file in uploaded_files:
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
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
        
