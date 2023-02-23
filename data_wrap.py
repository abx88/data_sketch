#!/usr/bin/env python
# coding: utf-8

# In[1]:

import streamlit as st
import pandas as pd
from io import StringIO

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    delimitatore = st.text_input("delimitatore", "s")
    st.write("delimiter is ", delimitatore)
    # Can be used wherever a "file-like" object is accepted:
    
    
    a = st.text_input("colonna1","a" )
    b = st.text_input("colonna2","b" )
    c = st.text_input("colonna3","c" )
        
    new_column_names = [c,b,a]
    
    df = pd.read_csv(uploaded_file, delimiter = (delimitatore), names=new_column_names)
    

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