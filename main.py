# -*- coding: utf-8 -*-
"""
Streamlit app for data analysis with keyword occurrence tracking.
Created on Fri Oct 11 22:49:53 2024
@author: volka
"""

import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Streamlit app title
st.title("Keyword Occurrence and Missing Words Analysis")

# Upload Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type="xlsx")
if uploaded_file:
    # Load data
    df = pd.read_excel(uploaded_file)
    
    # Check if required columns are present
    required_columns = {'Keyword', 'App Name', 'Subtitle'}
    if not required_columns.issubset(df.columns):
        st.error("The uploaded file must contain the columns: 'Keyword', 'App Name', and 'Subtitle'. Please check your file.")
    else:
        # Sort values
        df = df.sort_values(by=['Volume', 'Keyword'], ascending=[False, True])
        
        # Filter rows where 'Rank Status' is 'ranked'
        ranked_df = df[df['Rank Status'] == 'ranked']
        
        # Calculate the occurrence of each keyword
        keyword_counts = ranked_df['Keyword'].value_counts().reset_index()
        keyword_counts.columns = ['Keyword', 'Occurrence']
        
        # Merge occurrence data back into the original DataFrame
        df = df.merge(keyword_counts, on='Keyword', how='left')
        
        # Ensure 'App Name' and 'Subtitle' columns are strings
        df['App Name'] = df['App Name'].astype(str)
        df['Subtitle'] = df['Subtitle'].astype(str)
        
        # Title and Subtitle input fields with character limits
        title = st.text_input("Enter Title (max 30 characters)", max_chars=30)
        subtitle = st.text_input("Enter Subtitle (max 30 characters)", max_chars=30)
        
        # Two Keyword fields with max 100 characters each, separated by spaces or commas
        keyword_input1 = st.text_input("Enter Keywords Set 1 (max 100 characters, separated by space or comma)", max_chars=100)
        keyword_input2 = st.text_input("Enter Keywords Set 2 (max 100 characters, separated by space or comma)", max_chars=100)
        
        # Combine the two keyword inputs, split by spaces or commas, and make a single list
        input_keywords = re.split(r'[ ,]+', f"{keyword_input1} {keyword_input2}".strip().lower())

        # Function to find missing words from 'Keyword' based on combined keywords from Title, Subtitle, and Keywords input
        def clean_and_find_missing_words(row, input_keywords):
            cleaned_keyword = re.sub(r'[^a-zA-Z\s,]', '', row['Keyword']).lower()
            keyword_words = re.split(r'[,\s]+', cleaned_keyword)
            missing_words = [word for word in keyword_words if word and word not in input_keywords]
            if len(missing_words) == len(keyword_words):
                return "all missing"
            return ', '.join(missing_words) if missing_words else None
        
        # Apply the function and store results in a new column
        df['Missing Words from My Input'] = df.apply(lambda row: clean_and_find_missing_words(row, input_keywords), axis=1)
        
        # Text to check if present in keywords
        tekTekelime = st.text_input("Enter a word to check in Keyword column", "invoice")
        
        # Function to check if text is in 'Keyword' column
        def check_text_in_keyword(df, text):
            df['Text in Keyword'] = df['Keyword'].apply(lambda keyword: 1 if text.lower() in str(keyword).lower() else 0)
            return df
        
        # Apply the function to create the new column
        df = check_text_in_keyword(df, tekTekelime)
        
        # Display processed data
        st.write("Processed Data:")
        st.dataframe(df)
        
        # Option to download processed data as Excel
        def convert_df_to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            processed_data = output.getvalue()
            return processed_data
        
        excel_data = convert_df_to_excel(df)
        st.download_button("Download Processed Data as Excel", data=excel_data, file_name="invoicer_with_occurrences.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        st.success("Analysis Complete!")
