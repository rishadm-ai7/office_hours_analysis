import streamlit as st
import pandas as pd
from functions import process_data

def main():
    st.title('Admin Dashboard')

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button('Login'):
        if username == 'admin' and password == 'admin':
            st.success('Logged in successfully')
            st.balloons()

            files = st.file_uploader("Upload excel", type=['xlsx', 'xls'], accept_multiple_files=True)

            if files:
                for file in files:
                    data = pd.read_excel(file)
                    process_data(data)
                    st.success(f'Data pushed successfully for {file.name}')

        else:
            st.error('The username or password you entered is incorrect.')

if __name__ == "__main__":
    main()
