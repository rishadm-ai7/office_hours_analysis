import streamlit as st
import pandas as pd
from functions import process_data, get_insights

def main():
    st.title('Admin Dashboard')

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button('Login'):
        if username == 'admin' and password == 'admin':
            st.success('Logged in successfully')
            file = st.file_uploader("Upload excel", type=['xlsx'])
            if file is not None:
                data = pd.read_excel(file)
                if st.button('Push Data'):
                    process_data(data)s
                    st.success('Data pushed successfully')
                if st.button('Get Insights'):
                    insights = get_insights()
                    st.write(insights)
        else:
            st.error('The username or password you entered is incorrect.')

if __name__ == "__main__":
    main()
