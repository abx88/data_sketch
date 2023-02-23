#!/usr/bin/env python
# coding: utf-8

# In[1]:

import streamlit as st
import pandas as pd
from io import StringIO

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    
    # Definisci la lista di delimitatori supportati da Pandas
    delimiter_options = [',', '\t', '|', ';', ':']

    # Aggiungi l'elemento checkbox per selezionare il delimitatore
    delimitatore= st.checkbox("Seleziona il delimitatore", delimiter_options)

    st.write("delimiter is ", delimitatore)
    df = pd.read_csv(uploaded_file, delimiter = delimitatore)
    
    # Rinomina le colonne con numeri in ordine crescente
    new_column_names = list(range(len(df.columns)))
    df.columns = new_column_names
    st.write(df)

    @st.cache
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    csv = convert_df(df)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='large_df.csv',
        mime='text/csv')
else:
    st.text("inserire file csv")