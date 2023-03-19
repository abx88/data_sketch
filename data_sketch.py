#!/usr/bin/env python
# coding: utf-8

# In[1]:

import streamlit as st
import pandas as pd
import numpy as np
#from io import StringIO
import plotly.graph_objects as go
import scipy.stats as stats


st.set_page_config(
    page_title="DataSketch",
    layout="wide")

np.random.seed(123)
dfprova = pd.DataFrame(np.random.randn(50, 5), columns=('col %d' % i for i in range(5)))

st.header("Data Sketch")

pagina = st.radio("selezionare operazione",('modifica ed esporta','visualizzazione'))
col1, col2 = st.columns([2, 2])
expander_modificheCol = col1.expander("filtra/modifica colonne")
expander_modificheRighe = col2.expander("filtra/modifica righe")
expander_colonne = st.expander("aggiunta guidata colonne")
expander_csvOriginale = col1.expander("dati csv originali")
expander_csvModifica = col2.expander("dati csv modificati")
expander_modificheCol.write("modifiche effettuate su colonne")    
expander_modificheRighe.write("modifiche effettuate su righe")
#expander_csvOriginale.write("file csv originale")
#expander_csvModifica.write("file csv modificato")
uploaded_file = st.file_uploader("Selezionare un file .csv/.txt")
st.sidebar.header("Tool Modifica")
# Definisci la lista di delimitatori supportati da Pandas
delimiter_options = [',', '\t', '|', ';', ':']
# Aggiungi l'elemento checkbox per selezionare il delimitatore
delimitatore= st.sidebar.radio("Seleziona il delimitatore", delimiter_options)
# Aggiungi nomi colonne dataset
expander_csvOriginale.subheader("dataset originale")
expander_csvModifica.subheader("dataset modificato")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, delimiter = delimitatore)
    dfedit = expander_csvOriginale.experimental_data_editor(df, num_rows="dynamic")
else:
    df = dfprova
    dfedit = expander_csvOriginale.experimental_data_editor(df, num_rows="dynamic")

newdf= dfedit

#verifica se è necessario inserire delle intestazioni
tabella_senza_intestazioni = st.sidebar.checkbox("tabella senza intestazioni")

if tabella_senza_intestazioni == True:
    # Rinomina le colonne con numeri in ordine crescente
    new_column_names = list(range(len(df.columns)))
    newdf.loc[-1] = newdf.columns
    newdf.columns = new_column_names
    newdf.index = newdf.index + 1
    newdf.sort_index(inplace=True)

#verifica se ci sono colonne da aggiungere    
aggiungi_colonne = st.sidebar.checkbox("aggiungi colonne")
if aggiungi_colonne == True:
    expander_colonne.write("seleziona modalità aggiunta colonne") 
    if expander_colonne.button("aggiungi colonna", on_click=True):
        colonna_max = expander_colonne.multiselect("Seleziona le colonne di cui trovare max", newdf.columns.tolist())
        nome_colonna = expander_colonne.text_input("Inserisci il nome della nuova colonna")
        if nome_colonna:
            newdf[nome_colonna] = newdf[colonna_max].max(axis=1)
            expander_colonne.write(f"La colonna {nome_colonna} è stata aggiunta al dataframe")
        else:
            expander_colonne.write("Inserisci un nome valido per la nuova colonna")
    
    
#verifica se ci sono colonne da elimianre
elimina_colonne = expander_modificheCol.checkbox("elimina colonne")

if elimina_colonne == True:
    # Aggiungi l'elemento multiselect per selezionare le colonne da eliminare
    colonne_da_eliminare = expander_modificheCol.multiselect("Seleziona le colonne da eliminare", newdf.columns.tolist())

    # Elimina le colonne selezionate
    newdf = newdf.drop(columns=colonne_da_eliminare)

#verifica se ci sono colonne da rinominare
rinomina_colonne = expander_modificheCol.checkbox("colonne da rinominare")
if rinomina_colonne == True:
    # Aggiungi l'elemento multiselect per selezionare le colonne da rinominare
    colonne_da_rinominare = expander_modificheCol.multiselect("Seleziona le colonne da rinominare", newdf.columns.tolist())

    # Crea un dizionario per mappare i vecchi nomi delle colonne ai nuovi nomi
    mapping_nomi_colonne = {}
    for colonna in colonne_da_rinominare:
        nuovo_nome_colonna = expander_modificheCol.text_input(f"Inserisci il nuovo nome per la colonna '{colonna}'", colonna)
        mapping_nomi_colonne[colonna] = nuovo_nome_colonna

    # Rinomina le colonne selezionate con i nuovi nomi
    newdf =  newdf.rename(columns=mapping_nomi_colonne)


#verifica la necessità di una colonna indice    
indice = st.sidebar.checkbox("colonna indice")

if indice == True:
    expander_indice = st.sidebar.expander("scegli colonna indice")
    # Aggiungi l'elemento selectbox per selezionare la colonna da usare come indice
    colonna_indice = expander_indice.selectbox("Seleziona la colonna da usare come indice", newdf.columns.tolist())
    # Imposta la colonna selezionata come indice del DataFrame
    newdf = newdf.set_index(colonna_indice)

    # imposta se indice è in formato date_time (time series) oppure no (scatter dati) 
    indice_datetime = expander_indice.checkbox("indice date_time")
    if indice_datetime ==True:
        newdf.index = pd.to_datetime(newdf.index)#occorre per convertire in datetime la data
        scomponi_data = expander_indice.checkbox("estrai giorno, mese, anno") 
        if scomponi_data ==True:
            newdf['giorno_W'] = newdf.index.dayofweek
            newdf['mese'] = newdf.index.month
            newdf['anno'] = newdf.index.year

righe_da_eliminare = expander_modificheRighe.checkbox("righe da eliminare")

if righe_da_eliminare:
    #lista colonne presenti in df
    scegli_colonna_valori = expander_modificheRighe.selectbox("Seleziona la colonna", newdf.columns.tolist())
    # crea una serie da una colonna del df, da questa crea una lista di valori univoci presenti nella serie
    if scegli_colonna_valori is not None:
        valori = newdf[scegli_colonna_valori].unique().tolist()

        # chiede all'utente di selezionare i valori da eliminare
        valori_da_elim = expander_modificheRighe.multiselect('Seleziona i valori da eliminare:', valori)

        # elimina le righe che contengono i valori selezionati
        newdf = newdf.loc[~newdf[scegli_colonna_valori].isin(valori_da_elim)]

righe_da_filtrare = expander_modificheRighe.checkbox("righe da selezionare")

if righe_da_filtrare:
    #lista colonne presenti in df
    scegli_colonna_valori_filtro = expander_modificheRighe.selectbox("Seleziona la colonna", newdf.columns.tolist())
    # crea una serie da una colonna del df, da questa crea una lista di valori univoci presenti nella serie
    if scegli_colonna_valori_filtro is not None:
        valori_filt = newdf[scegli_colonna_valori_filtro].unique().tolist()

        # chiede all'utente di selezionare i valori da eliminare
        valori_da_filtrare = expander_modificheRighe.multiselect('Seleziona i valori da filtrare:', valori_filt)

        # elimina le righe che contengono i valori selezionati
        newdf = newdf.loc[newdf[scegli_colonna_valori_filtro].isin(valori_da_filtrare)]


        
pivot_df = st.sidebar.checkbox("raggruppa dati")
if pivot_df == True:
    expander_pivot = st.sidebar.expander("inserire input raggruppamento")
    colonne = expander_pivot.checkbox("pivot con colonne")
    if colonne == False:
        valori = expander_pivot.selectbox("valori", newdf.columns.tolist())
        indice = expander_pivot.selectbox("indice", newdf.columns.tolist())
        funzione = expander_pivot.text_input('funzione', 'mean')
        if indice == valori:
            indice = newdf.columns[1]
        newdf = pd.pivot_table(newdf,
                               values=valori,
                               index=indice, 
                               aggfunc=funzione,
                               dropna = True)
    else:
        valori = expander_pivot.selectbox("valori", newdf.columns.tolist())
        indice = expander_pivot.selectbox("indice", newdf.columns.tolist())
        colonna = expander_pivot.selectbox("colonne", newdf.columns.tolist())
        funzione = expander_pivot.text_input('funzione', 'mean')
        if indice == valori or indice == colonna:
            indice = newdf.columns[0]
        if valori == colonna or valori == indice:
            valori = newdf.columns[-1]
        if colonna == indice or colonna == valori:
            colonna = newdf.columns[1]
       
        newdf = pd.pivot_table(newdf,
                               values=valori,
                               index=indice, 
                               columns=colonna,
                               aggfunc=funzione,
                               dropna = True)

trasponi_df = st.sidebar.checkbox("trasponi dataframe in modifica")
if trasponi_df == True:
    newdf = newdf.transpose()
        

expander_csvModifica.write(newdf)       
newdfvisual=newdf


if pagina == 'modifica ed esporta':

    st.subheader("esporta dataframe in csv")
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
    st.subheader("visualizza dati")
    tipologia_dati = st.radio("tipologia dati in esame",('Time Series','Cross Section (analisi correlazione)'))
    col3, col4 = st.columns([2, 2])

    if tipologia_dati == 'Time Series':
        with col3:
            #visualizzazione variabile    
            colonna_da_visualizzare = st.selectbox("Seleziona la colonna da visualizzare", newdfvisual.columns.tolist())
            variabile = go.Figure()

            variabile.add_trace(go.Scatter(
                mode = "lines",
                y = newdfvisual[colonna_da_visualizzare],
                x = newdfvisual.index,
                name="variabile",
                connectgaps=False))

            variabile.update_layout(
                xaxis_title_text="data",
                title={
                    'text': colonna_da_visualizzare,
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'})
            st.plotly_chart(variabile,use_container_width=False )

        with col4:
            colonna_da_visualizzare2 = st.selectbox("Seleziona la colonna da visualizzare ", newdfvisual.columns.tolist())
            variabile2 = go.Figure()

            variabile2.add_trace(go.Scatter(
                mode = "markers",
                y = newdfvisual[colonna_da_visualizzare2],
                x = newdfvisual.index,
                name="variabile2",
                connectgaps=False))

            variabile2.update_layout(
                xaxis_title_text="data",
                title={
                    'text': colonna_da_visualizzare2,
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'})
            st.plotly_chart(variabile2,use_container_width=False )

    else:
        with col3:
            col5,col6,col9= st.columns([2,2,2])
            colonna_confrontoY = col5.selectbox("Seleziona asse Y", newdfvisual.columns.tolist())
            colonna_confrontoX = col6.selectbox("Seleziona asse X", newdfvisual.columns.tolist())

            somma_valori = col9.checkbox("raggruppa valori Y per x")
            #newdfvisual[colonna_confrontoY] = pd.to_numeric(newdfvisual[colonna_confrontoY], errors='coerce')
            #newdfvisual[colonna_confrontoX] = pd.to_numeric(newdfvisual[colonna_confrontoX], errors='coerce')
            #st.write(newdfvisual)

            if somma_valori == False:
                scatter = go.Figure()

                scatter.add_trace(go.Scatter(
                    mode = "markers",
                    y = newdfvisual[colonna_confrontoY],
                    x = newdfvisual[colonna_confrontoX],
                    name="scatter",
                    connectgaps=False))


                scatter.update_layout(
                    xaxis_title_text=colonna_confrontoX,
                    yaxis_title_text=colonna_confrontoY,
                    title={
                        'text': "confronto variabili",
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'})


                st.plotly_chart(scatter,use_container_width=False )

            else:

                #creo tabella pivot + grafico che raggruppa valori di y per valori x (solo se x è categorica)
                pivotVariabile = pd.pivot_table(newdfvisual, 
                                                values=colonna_confrontoY, 
                                                index=colonna_confrontoX, 
                                                aggfunc=np.sum)

                filtroAggiuntivo = st.checkbox("Aggiungi filtro indice")
                if filtroAggiuntivo ==True:
                    #colonna_filtro = newdfvisual[colonna_confrontoX]
                    valori = newdfvisual[colonna_confrontoX].unique().tolist()
                    valori_filt = col6.multiselect('Seleziona valori:', valori)
                    pivotVariabile = pivotVariabile.loc[valori_filt]
                else:
                    pivotVariabile = pivotVariabile

                graficoBarre = go.Figure()

                graficoBarre.add_trace(go.Bar(
                    y = pivotVariabile[colonna_confrontoY],
                    x = pivotVariabile.index,
                    name="grafico a barre"))

                graficoBarre.update_layout(
                    xaxis_title_text=colonna_confrontoX,
                    yaxis_title_text=colonna_confrontoY,
                    title={
                        'text': "raggruppamento Y per X",
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'})
                st.plotly_chart(graficoBarre,use_container_width=False )



        with col4:
            col7,col8 = st.columns([2, 2])
            #dal df scelgo una variabile per confrontare la sua distribuzione 
            colonna_distribuzione = col7.selectbox("Seleziona colonna per vedere la sua distribuzione", newdfvisual.columns.tolist())
            # calcola la media e la deviazione standard della variabile di interesse
            colonna_distribuzione_perc = col7.checkbox("distribuzione della variazione percentuale")
            if colonna_distribuzione_perc == False:
                newdfvisual[colonna_distribuzione] = pd.to_numeric(newdfvisual[colonna_distribuzione], errors='coerce')
                media = newdfvisual[colonna_distribuzione].mean()
                dev_std = newdfvisual[colonna_distribuzione].std()    
                # crea una figura con due tracce: la distribuzione dei dati e la distribuzione normale
                distribuzione = go.Figure()

                # traccia 1: distribuzione dei dati
                distribuzione.add_trace(go.Histogram(
                    x=newdfvisual[colonna_distribuzione],
                    histnorm='probability',
                    name="distribuzione variabile"))

                # traccia 2: distribuzione normale
                x = np.linspace(newdfvisual[colonna_distribuzione].min(), newdfvisual[colonna_distribuzione].max(), 100)
                pdf = stats.norm.pdf(x, media, dev_std)
                distribuzione.add_trace(go.Scatter(
                    x=x, 
                    y=pdf, 
                    mode='lines', 
                    name='distribuzione normale',
                    yaxis='y2'))

                # aggiungi i titoli degli assi e il titolo della figura
                distribuzione.update_layout(
                    xaxis_title_text=colonna_distribuzione,
                    yaxis_title_text='densità di probabilità',
                    yaxis2=dict(overlaying='y',side='right'),
                    title={
                        'text': "Distribuzione dei dati e distribuzione normale",
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'})

                # visualizza la figura
                st.plotly_chart(distribuzione, use_container_width=False)


            else:
                #creazione del df delle variazioni percentuali
                newdfvisual[colonna_distribuzione] = pd.to_numeric(newdfvisual[colonna_distribuzione], errors='coerce')
                serie_perc = newdfvisual[colonna_distribuzione].pct_change()
                media_perc = serie_perc.mean()
                dev_std_perc = serie_perc.std()    

                # crea una figura con due tracce: la distribuzione dei dati e la distribuzione normale
                distribuzione_perc = go.Figure()

                # traccia 1: distribuzione dei dati
                distribuzione_perc.add_trace(go.Histogram(
                    x=serie_perc,
                    histnorm='probability',
                    name="distribuzione variabile"))

                # traccia 2: distribuzione normale
                x = np.linspace(serie_perc.min(), serie_perc.max(), 100)
                pdf = stats.norm.pdf(x, media_perc, dev_std_perc)
                distribuzione_perc.add_trace(go.Scatter(
                    x=x, 
                    y=pdf, 
                    mode='lines', 
                    name='distribuzione normale',
                    yaxis='y2'))

                # aggiungi i titoli degli assi e il titolo della figura
                distribuzione_perc.update_layout(
                    xaxis_title_text=colonna_distribuzione,
                    yaxis_title_text='densità di probabilità',
                    yaxis2=dict(overlaying='y',side='right'),
                    title={
                        'text': "Distribuzione dei dati e distribuzione normale",
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'})
                st.plotly_chart(distribuzione_perc, use_container_width=False)
    
                    
          
    
#else:
 #   st.text("inserire file csv")

