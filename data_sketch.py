#!/usr/bin/env python
# coding: utf-8

# In[1]:

import streamlit as st
import pandas as pd
from io import StringIO

st.header("Data Sketch")

pagina = st.radio("Pagina",('tool modifica','tool visualizzazione'))

    
uploaded_file = st.file_uploader("Selezionare un file .csv/.txt")
if uploaded_file is not None:
    st.sidebar.header("Tool Modifica")
    # Definisci la lista di delimitatori supportati da Pandas
    delimiter_options = [',', '\t', '|', ';', ':']

    # Aggiungi l'elemento checkbox per selezionare il delimitatore
    delimitatore= st.sidebar.radio("Seleziona il delimitatore", delimiter_options)

    st.subheader("dataset originale")
    df = pd.read_csv(uploaded_file, delimiter = delimitatore)
    newdf= df
    

    st.write(df)

    tabella_senza_intestazioni = st.sidebar.checkbox("tabella senza intestazioni")
    if tabella_senza_intestazioni == True:
        # Rinomina le colonne con numeri in ordine crescente
        new_column_names = list(range(len(df.columns)))
        newdf.loc[-1] = newdf.columns
        newdf.columns = new_column_names
        newdf.index = newdf.index + 1
        newdf.sort_index(inplace=True)
        #st.write(df)
    #else:
     #   st.write(df)

    elimina_colonne = st.sidebar.checkbox("elimina colonne")
    if elimina_colonne == True:
        # Aggiungi l'elemento multiselect per selezionare le colonne da eliminare
        colonne_da_eliminare = st.sidebar.multiselect("Seleziona le colonne da eliminare", newdf.columns.tolist())

        # Elimina le colonne selezionate
        newdf = newdf.drop(columns=colonne_da_eliminare)

    rinomina_colonne = st.sidebar.checkbox("colonne da rinominare")
    if rinomina_colonne == True:
        # Aggiungi l'elemento multiselect per selezionare le colonne da rinominare
        colonne_da_rinominare = st.sidebar.multiselect("Seleziona le colonne da rinominare", newdf.columns.tolist())

        # Crea un dizionario per mappare i vecchi nomi delle colonne ai nuovi nomi
        mapping_nomi_colonne = {}
        for colonna in colonne_da_rinominare:
            nuovo_nome_colonna = st.sidebar.text_input(f"Inserisci il nuovo nome per la colonna '{colonna}'", colonna)
            mapping_nomi_colonne[colonna] = nuovo_nome_colonna

        # Rinomina le colonne selezionate con i nuovi nomi
        newdf =  newdf.rename(columns=mapping_nomi_colonne)

    indice = st.sidebar.checkbox("colonna indice")

    if indice == True:
        # Aggiungi l'elemento selectbox per selezionare la colonna da usare come indice
        colonna_indice = st.selectbox("Seleziona la colonna da usare come indice", newdf.columns.tolist())
        # Imposta la colonna selezionata come indice del DataFrame
        newdf = newdf.set_index(colonna_indice)
        indice_datetime = st.checkbox("indice date_time")
        if indice_datetime ==True:
            newdf.index = pd.to_datetime(newdf.index)#occorre per convertire in datetime la data

    if pagina == 'tool modifica':
        st.subheader("dataset rielaborato")
        st.write(newdf)

        nome_file=st.text_input("inserisci il nome con cui vuoi salvare il file scaricato", "nuovo_dataset")

        @st.cache
        def convert_df(newdf):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return newdf.to_csv().encode('utf-8')

        csv = convert_df(newdf)

        st.download_button(
        label="Download dataset modificato",
        data=csv,
        file_name=f"{nome_file}.csv",  # utilizzo della f-string per inserire il valore di nome_file come stringa
        mime='text/csv')
   
    else:
        col1, col2 = st.columns([2, 2])
        col1.subheader("dataset rielaborato")
        col1.write(newdf)
        #visualizzazione variabile    
        col2.subheader("visualizza variabile")
        if tabella_senza_intestazioni == True:
            colonna_da_visualizzare = col2.selectbox("Seleziona le colonne da visualizzare", newdf.columns.tolist(), index = 2)
        else:
            colonna_da_visualizzare = col2.selectbox("Seleziona le colonne da visualizzare", newdf.columns.tolist())
        serie = newdf[colonna_da_visualizzare]
        st.write(serie)
        col2.line_chart(serie)
    
else:
    st.text("inserire file csv")

