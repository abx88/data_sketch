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
    delimitatore= st.radio("Seleziona il delimitatore", delimiter_options)

    st.write("delimiter is ", delimitatore)
    df = pd.read_csv(uploaded_file, delimiter = delimitatore)
    
    # Rinomina le colonne con numeri in ordine crescente
    new_column_names = list(range(len(df.columns)))
    df.columns = new_column_names
    st.write(df)
    
    # Aggiungi l'elemento multiselect per selezionare le colonne da rinominare
    colonne_da_rinominare = st.multiselect("Seleziona le colonne da rinominare", df.columns.tolist())

    # Crea un dizionario per mappare i vecchi nomi delle colonne ai nuovi nomi
    mapping_nomi_colonne = {}
    for colonna in colonne_da_rinominare:
        nuovo_nome_colonna = st.text_input(f"Inserisci il nuovo nome per la colonna '{colonna}'", colonna)
        mapping_nomi_colonne[colonna] = nuovo_nome_colonna

    # Rinomina le colonne selezionate con i nuovi nomi
    df = df.rename(columns=mapping_nomi_colonne)

    indice = st.checkbox("colonna indice")
    
    if indice == True:
        # Aggiungi l'elemento selectbox per selezionare la colonna da usare come indice
        colonna_indice = st.selectbox("Seleziona la colonna da usare come indice", df.columns.tolist())

        # Imposta la colonna selezionata come indice del DataFrame
        df = df.set_index(colonna_indice)
    
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