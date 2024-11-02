# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 22:49:53 2024

@author: volka
"""

import pandas as pd
from collections import Counter
import re
import streamlit as st

st.title("Keyword Analysis Dashboard")

# File uploader for Excel file input
uploaded_file = st.file_uploader("Upload your Excel file", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    st.write("### Original Data")
    st.dataframe(df.head())

    # Sort by Volume and Keyword
    df = df.sort_values(by=['Volume', 'Keyword'], ascending=[False, True])

    # Filter for 'ranked' status
    ranked_df = df[df['Rank Status'] == 'ranked']

    # Calculate occurrences of each keyword in 'Keyword' column
    keyword_counts = ranked_df['Keyword'].value_counts().reset_index()
    keyword_counts.columns = ['Keyword', 'Occurrence']
    df = df.merge(keyword_counts, on='Keyword', how='left')

    # Ensure 'App Name' and 'Subtitle' columns are strings
    df['App Name'] = df['App Name'].astype(str)
    df['Subtitle'] = df['Subtitle'].astype(str)

    # Define a function to find missing words in 'App Name' and 'Subtitle'
    def find_missing_words(row):
        keyword_words = row['Keyword'].lower().split()
        app_name_words = row['App Name'].lower().split()
        subtitle_words = row['Subtitle'].lower().split()
        missing_words = [word for word in keyword_words if word not in app_name_words + subtitle_words]
        return f"missing: {', '.join(missing_words)}" if missing_words else None

    df['Missing Words (Not Title or Subtitle)'] = df.apply(find_missing_words, axis=1)

    # Input fields for text analysis
    input_text = st.text_area("Enter text for keyword analysis", "Simple Invoice maker Invoicer Make receipt Invoices")
    Title = st.text_input("Title", "Simple Invoice maker Invoicer")
    Subtitle = st.text_input("Subtitle", "Make receipt Invoices")
    KeywordField = st.text_input("Keyword Field", "free,generator,home,app,estimate,square,business,receipts")
    KeywordField2 = st.text_input("Additional Keyword Field", "")
    input_text_full = f"{Title} {Subtitle} {KeywordField} {KeywordField2}"

    # Function to clean and find missing words
    def clean_and_find_missing_words(row, input_text):
        cleaned_keyword = re.sub(r'[^a-zA-Z\s,]', '', row['Keyword']).lower()
        keyword_words = re.split(r'[,\s]+', cleaned_keyword)
        input_words = re.split(r'[ ,]+', input_text.lower())
        missing_words = [word for word in keyword_words if word and word not in input_words]
        return "all missing" if len(missing_words) == len(keyword_words) else ', '.join(missing_words) if missing_words else None

    df['Missing Words from My Input'] = df.apply(lambda row: clean_and_find_missing_words(row, input_text_full), axis=1)

    # Function to check if a word is in the 'Keyword' column
    def check_text_in_keyword(df, text):
        df['Text in Keyword'] = df['Keyword'].apply(lambda keyword: 1 if text.lower() in str(keyword).lower() else 0)
        return df

    tekTekelime = st.text_input("Single Word to Check", "invoice")
    df = check_text_in_keyword(df, tekTekelime)

    # Function to find most common words in a column
    def most_common_words_in_column(df, column_name, n=5):
        all_text = ' '.join(df[column_name].astype(str).tolist())
        all_words = re.findall(r'\b\w+\b', all_text.lower())
        return Counter(all_words).most_common(n)

    # Display most common words
    st.write("### Most Common Words in 'Keyword' Column")
    most_common_keywords = most_common_words_in_column(ranked_df, 'Keyword', n=10)
    for word, count in most_common_keywords:
        st.write(f"{word}: {count}")

    # Function to find common words in unique column combinations
    def most_common_words_in_unique_combinations(df, columns, n=10):
        unique_df = df.drop_duplicates(subset=columns)
        all_text = ' '.join(unique_df[columns[0]].astype(str) + ' ' + unique_df[columns[1]].astype(str))
        all_words = re.findall(r'\b\w+\b', all_text.lower())
        return Counter(all_words).most_common(n)

    # Display most common words in unique combinations
    st.write("### Most Common Words in Unique 'App Name' and 'Subtitle' Combinations")
    most_common_app_name_subtitle = most_common_words_in_unique_combinations(ranked_df, ['App Name', 'Subtitle'], n=5)
    for word, count in most_common_app_name_subtitle:
        st.write(f"{word}: {count}")

    # Function to find and display top unranked keywords
    def find_top_10_unranked_keywords(df):
        unranked_keywords = df[df['Rank Status'] != 'ranked']['Keyword']
        unranked_keyword_counts = unranked_keywords.value_counts().reset_index()
        unranked_keyword_counts.columns = ['Keyword', 'Count']
        top_10_unranked = unranked_keyword_counts.sort_values(by='Count', ascending=False).head(10)
        return top_10_unranked

    st.write("### Top 10 Most Common Unranked Keywords")
    top_10_unranked_keywords = find_top_10_unranked_keywords(df)
    st.write(top_10_unranked_keywords)

    # Display final DataFrame
    st.write("### Final Processed Data")
    st.dataframe(df)

else:
    st.write("Please upload an Excel file to begin.")
