import streamlit as st
import pandas as pd
from io import BytesIO

# CSS Animations
st.markdown(
    """
    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes cubeRotate {
            from {
                transform: rotateY(90deg);
                opacity: 0;
            }
            to {
                transform: rotateY(0deg);
                opacity: 1;
            }
        }

        .header-bar {
            background-color: #0073e6;
            padding: 15px;
            text-align: center;
            font-size: 24px;
            color: white;
            border-radius: 10px;
            font-weight: bold;
            animation: fadeIn 1s ease-out;
        }

        .data-table {
            display: flex;
            align-items: center;
            justify-content: center;
            animation: cubeRotate 0.6s ease-out;
        }

        .nav-buttons {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 10px;
        }

        .arrow-button {
            font-size: 24px;
            background: none;
            border: none;
            cursor: pointer;
            transition: transform 0.2s;
        }

        .arrow-button:hover {
            transform: scale(1.2);
        }
    </style>
    <div class="header-bar"> [DEMO] QATCH Analyzer 📊</div>
    """,
    unsafe_allow_html=True
)

# Controllo per la selezione delle tabelle
if "table_index" not in st.session_state:
    st.session_state.table_index = 0  # Inizialmente la prima tabella

# Liste di dati di esempio per le tabelle
tables = [
    pd.DataFrame({"Name": ["Alice", "Bob", "Charlie"], "Age": [25, 30, 35], "City": ["Rome", "London", "Paris"]}),
    pd.DataFrame({"Product": ["Laptop", "Mouse", "Keyboard"], "Price": [1000, 25, 50], "Stock": [5, 50, 30]}),
    pd.DataFrame({"Country": ["Italy", "UK", "France"], "Population (M)": [60, 67, 65], "Capital": ["Rome", "London", "Paris"]})
]

# Navigazione con frecce a sinistra e destra della tabella
st.markdown('<div class="nav-buttons">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 8, 1])

with col1:
    if st.button("⬅️", key="left_arrow"):
        st.session_state.table_index = (st.session_state.table_index - 1) % len(tables)

with col3:
    if st.button("➡️", key="right_arrow"):
        st.session_state.table_index = (st.session_state.table_index + 1) % len(tables)

st.markdown('</div>', unsafe_allow_html=True)

# Visualizza la tabella corrente con animazione cube
st.markdown('<div class="data-table">', unsafe_allow_html=True)
st.title(f"Table {st.session_state.table_index + 1} 📊")
edited_data = st.data_editor(tables[st.session_state.table_index], num_rows="dynamic", width=800, height=200)
st.markdown('</div>', unsafe_allow_html=True)

# Pulsante per salvare i dati modificati
st.markdown('<div class="buttons">', unsafe_allow_html=True)
if st.button("Save data"):
    st.write("✅ Data successfully saved!")
    st.write(edited_data)
st.markdown('</div>', unsafe_allow_html=True)
