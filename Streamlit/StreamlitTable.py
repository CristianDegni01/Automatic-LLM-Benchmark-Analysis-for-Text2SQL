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
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
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

        .upload-box, .data-table, .buttons {
            animation: fadeIn 1s ease-out;
        }

        .download-buttons {
            animation: slideIn 1s ease-out;
        }
    </style>
    <div class="header-bar"> [DEMO] QATCH Analyzer 📊</div>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="upload-box">', unsafe_allow_html=True)
st.title("Upload your data 📊")

# File upload with Drag & Drop
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    try:
        # Check file type and read
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ File successfully uploaded!")

        # Apply animation to table
        st.markdown('<div class="data-table">', unsafe_allow_html=True)
        edited_data = st.data_editor(df, num_rows="dynamic", width=800, height=200)
        st.markdown('</div>', unsafe_allow_html=True)

        # Download modified data
        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode('utf-8')

        def convert_df_to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            return output.getvalue()

        # Animated download buttons
        st.markdown('<div class="download-buttons">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download CSV",
                data=convert_df_to_csv(edited_data),
                file_name="modified_data.csv",
                mime="text/csv"
            )
        with col2:
            st.download_button(
                label="📥 Download Excel",
                data=convert_df_to_excel(edited_data),
                file_name="modified_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error loading the file: {e}")

else:
    st.info("📂 Drag and drop a CSV or Excel file here to get started.")

# Toy Table Section with Animation
st.markdown('<div class="data-table">', unsafe_allow_html=True)
st.title("Or customize this toy table 📊")

data = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["Rome", "London", "Paris"]
})

edited_data = st.data_editor(data, num_rows="dynamic", width=800, height=200)
st.markdown('</div>', unsafe_allow_html=True)

# Animated save button
st.markdown('<div class="buttons">', unsafe_allow_html=True)
if st.button("Save data"):
    st.write("✅ Data successfully saved!")
    st.write(edited_data)
st.markdown('</div>', unsafe_allow_html=True)
