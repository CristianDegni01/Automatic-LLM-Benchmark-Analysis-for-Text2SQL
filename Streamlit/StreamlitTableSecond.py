import streamlit as st
import pandas as pd

# Sample data for tables
data_tables = {
    "Table 1": pd.DataFrame({"A": [1, 2, 3, 4, 5], "B": [4, 5, 6, 7, 8], "C": [7, 8, 9, 10, 11], "D": [10, 11, 12, 13, 14]}),
    "Table 2": pd.DataFrame({"X": [10, 20, 30, 40, 50], "Y": [40, 50, 60, 70, 80], "Z": [70, 80, 90, 100, 110], "W": [100, 110, 120, 130, 140]}),
    "Table 3": pd.DataFrame({"Name": ["Anna", "Luca", "Marco", "Giulia", "Paolo"], "Age": [25, 30, 35, 40, 45], "City": ["Rome", "Milan", "Turin", "Naples", "Florence"], "Country": ["Italy", "Italy", "Italy", "Italy", "Italy"]})
}

# Application title
st.title("Select and View Tables")

# Multi-select box for table selection with default
tables_selected = st.multiselect("Select tables to view:", list(data_tables.keys()), default=["Table 1"])

# State tracking for explored table
if 'explored_table' not in st.session_state:
    st.session_state['explored_table'] = None

# Horizontal layout
cols = st.columns(len(tables_selected))
for i, table_name in enumerate(tables_selected):
    with cols[i]:
        st.subheader(table_name)
        df = data_tables[table_name]
        preview_df = df.iloc[:5, :3]
        if df.shape[1] > 3:
            preview_df["..."] = "..."
        st.dataframe(preview_df)
        
        if st.button(f"Explore {table_name}"):
            st.session_state['explored_table'] = table_name

# Show the explored table while closing others
if st.session_state['explored_table']:
    st.write(f"All columns of {st.session_state['explored_table']}")
    st.dataframe(data_tables[st.session_state['explored_table']])