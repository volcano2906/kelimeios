import streamlit as st
import pandas as pd
import re

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
        
        # Function to find missing words
        def find_missing_words(row):
            keyword_words = row['Keyword'].lower().split()
            app_name_words = row['App Name'].lower().split()
            subtitle_words = row['Subtitle'].lower().split()
            missing_words = [word for word in keyword_words if word not in app_name_words + subtitle_words]
            return f"missing: {', '.join(missing_words)}" if missing_words else None
        
        # Apply the function and store results in a new column
        df['Missing Words (Not Title or Subtitle)'] = df.apply(find_missing_words, axis=1)
        
        # Input text for custom missing words analysis
        input_text = st.text_area("Enter custom keywords for analysis", 
                                  "Simple Invoice maker Invoicer Make receipt Invoices free,generator,home,app,estimate,square,business,receipts,contractor,foreman,instant,invoicing,tracker,easy,facturas,creator,manager,digital,factura,simple,")
        
        # Function to clean and find missing words from 'Keyword' based on input_text
        def clean_and_find_missing_words(row, input_text):
            cleaned_keyword = re.sub(r'[^a-zA-Z\s,]', '', row['Keyword']).lower()
            keyword_words = re.split(r'[,\s]+', cleaned_keyword)
            input_words = re.split(r'[ ,]+', input_text.lower())
            missing_words = [word for word in keyword_words if word and word not in input_words]
            if len(missing_words) == len(keyword_words):
                return "all missing"
            return ', '.join(missing_words) if missing_words else None
        
        # Apply the function and store results in a new column
        df['Missing Words from My Input'] = df.apply(lambda row: clean_and_find_missing_words(row, input_text), axis=1)
        
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
        @st.cache_data
        def convert_df_to_excel(df):
            return df.to_excel(index=False, engine='xlsxwriter')
        
        excel_data = convert_df_to_excel(df)
        st.download_button("Download Processed Data as Excel", data=excel_data, file_name="invoicer_with_occurrences.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        st.success("Analysis Complete!")
