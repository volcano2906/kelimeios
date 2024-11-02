# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 22:49:53 2024

@author: volka
"""

import pandas as pd
from collections import Counter
import re
import streamlit as st
# Set the page to wide layout
st.set_page_config(page_title="Keyword Analysis Dashboard", layout="wide")
st.title("Keyword Analysis Dashboard")

# File uploader for Excel file input
uploaded_file = st.file_uploader("Upload your Excel file", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Check for required columns
    required_columns = {"App Name", "Subtitle", "Keyword"}
    if not required_columns.issubset(df.columns):
        st.error("Error")
    else:
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

        # Define function to get most common words in a column
        def most_common_words_in_column(df, column_name, n=5):
            all_text = ' '.join(df[column_name].astype(str).tolist())
            all_words = re.findall(r'\b\w+\b', all_text.lower())
            return [word for word, _ in Counter(all_words).most_common(n)]

        # Most common words in 'Keyword' column
        most_common_keywords = most_common_words_in_column(ranked_df, 'Keyword', n=10)

        # Define function to get most common words in unique combinations of columns
        def most_common_words_in_unique_combinations(df, columns, n=5):
            unique_df = df.drop_duplicates(subset=columns)
            all_text = ' '.join(unique_df[columns[0]].astype(str) + ' ' + unique_df[columns[1]].astype(str))
            all_words = re.findall(r'\b\w+\b', all_text.lower())
            return [word for word, _ in Counter(all_words).most_common(n)]

        # Most common words in 'App Name' and 'Subtitle' combinations
        most_common_app_name_subtitle = most_common_words_in_unique_combinations(ranked_df, ['App Name', 'Subtitle'], n=5)

        # Function to find and display top unranked keywords
        def find_top_10_unranked_keywords(df):
            unranked_keywords = df[df['Rank Status'] != 'ranked']['Keyword']
            unranked_keyword_counts = unranked_keywords.value_counts().reset_index()
            unranked_keyword_counts.columns = ['Keyword', 'Count']
            top_10_unranked = unranked_keyword_counts.sort_values(by='Count', ascending=False).head(10)
            return [keyword for keyword in top_10_unranked['Keyword']]

        # Get the top 10 unranked keywords
        top_10_unranked_keywords = find_top_10_unranked_keywords(df)

        # First container: Summary of most common words
        with st.container():
            st.write("### Summary of Most Common Words")
            st.write(f"**Most Common Words in 'Keyword' Column**: {', '.join(most_common_keywords)}")
            st.write(f"**Most Common Words in Unique 'App Name' and 'Subtitle' Combinations**: {', '.join(most_common_app_name_subtitle)}")
            st.write(f"**Top 10 Most Common Unranked Keywords**: {', '.join(top_10_unranked_keywords)}")

        # Second container: Two columns with input fields on the left and processed data on the right
        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                st.write("### Input Fields")
                Title = st.text_input("Title", "Simple Invoice maker Invoicer")
                st.write(f"Character count: {len(Title)}")

                Subtitle = st.text_input("Subtitle", "Make receipt Invoices")
                st.write(f"Character count: {len(Subtitle)}")

                KeywordField = st.text_input("Keyword Field", "free,generator,home,app,estimate,square,business,receipts")
                st.write(f"Character count: {len(KeywordField)}")

                KeywordField2 = st.text_input("Additional Keyword Field", "")
                st.write(f"Character count: {len(KeywordField2)}")

                tekTekelime = st.text_input("Single Word to Check", "invoice")
                st.write(f"Character count: {len(tekTekelime)}")

                # Update input_text_full from Title, Subtitle, and KeywordFields
                input_text_full = f"{Title} {Subtitle} {KeywordField} {KeywordField2}"

                # Function to clean and find missing words from input text
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

                # Apply the function to create the new column for single word check
                df = check_text_in_keyword(df, tekTekelime)

            with col2:
                st.write("### Final Processed Data")
                st.dataframe(df)
else:
    st.write("Please upload an Excel file to begin.")
