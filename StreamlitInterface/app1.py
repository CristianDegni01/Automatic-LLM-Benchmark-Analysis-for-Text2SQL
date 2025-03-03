import streamlit as st
import pandas as pd
from io import BytesIO
import sqlite3
import tempfile
import os
import plotly.express as px
from qatch.connectors.sqlite_connector import SqliteConnector
from qatch.generate_dataset.orchestrator_generator import OrchestratorGenerator
from qatch.evaluate_dataset.orchestrator_evaluator import OrchestratorEvaluator
#from qatch.prediction_dataset.orchestrator_predictor import OrchestratorPredictor

# Initialize the page variable in the session state
if "page" not in st.session_state:
    st.session_state.page = "upload"

# Function to change the page
def change_page(page_name):
    if (page_name == "upload") : 
        st.session_state.dfs = None
    st.session_state.page = page_name
    st.rerun()  # Reload the page with the new screen

# Function to load an SQLite file and generate DataFrames for each table
def load_sqlite(uploaded_file):
    # Save the uploaded file as a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    # Connect to the SQLite database
    conn = sqlite3.connect(tmp_file_path)
    cursor = conn.cursor()

    # Retrieve table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Create a dictionary to store DataFrames, excluding sqlite_sequence
    dfs = {}
    for table in tables:
        table_name = table[0]
        if table_name != "sqlite_sequence":  # Exclude the sqlite_sequence table
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            dfs[table_name] = df

    conn.close()

    # Delete the temporary file
    os.remove(tmp_file_path)

    return dfs

# **Upload Screen**
if st.session_state.page == "upload":
    with open("./StreamlitInterface/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    if "dfs" not in st.session_state:
        st.session_state.dfs = None

    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    st.title("Upload your data 📊")

    # File upload with Drag & Drop
    uploaded_file = st.file_uploader("Upload a CSV, Excel, or SQLite file", type=["csv", "xlsx", "sqlite"])
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        try:
            # Load the file into a DataFrame or a dictionary of DataFrames
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                st.session_state.dfs = {"Table": df}  # Use a dictionary with a generic key
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
                st.session_state.dfs = {"Table": df}  # Use a dictionary with a generic key
            elif uploaded_file.name.endswith(".sqlite"):
                st.session_state.dfs = load_sqlite(uploaded_file)

            st.success("✅ File successfully uploaded!")

            # Display data editor for each table
            for table_name, df in st.session_state.dfs.items():
                st.markdown(f'<div class="data-table">', unsafe_allow_html=True)
                st.subheader(f"Table: {table_name}")
                edited_data = st.data_editor(df, num_rows="dynamic", width=800, height=200)
                st.session_state.dfs[table_name] = edited_data  # Update modified data
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            #TODO : check the name of the file
            if 'dbname' not in st.session_state:
                st.session_state['dbname'] = uploaded_file.name.split()[0]

            # **Switch to the table selection page**
            change_page("select")

        except Exception as e:
            st.error(f"❌ Error loading the file: {e}")

    else:
        st.info("📂 Drag and drop a CSV, Excel, or SQLite file here to get started.")

    # Sample table section
    st.markdown('<div class="data-table">', unsafe_allow_html=True)
    st.title("Or customize this toy table 📊")

    data = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["Rome", "London", "Paris"]
    })

    edited_data = st.data_editor(data, num_rows="dynamic", width=800, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

    # Button to save and switch pages
    st.markdown('<div class="buttons">', unsafe_allow_html=True)
    if st.button("Save data"):
        
        if 'dbname' not in st.session_state:
            st.session_state['dbname'] = "custom_table"
        
        st.session_state.dfs = {"Table": edited_data}  # Use a dictionary with a generic key
        st.write("✅ Data successfully saved!")
        change_page("select")
    st.markdown('</div>', unsafe_allow_html=True)

# **Tables Selection Screen**
elif st.session_state.page == "select":

    st.title("Select and View Tables")

    # Check if there are saved data
    if st.session_state.dfs is not None:
        # Multi-select box for table selection with default values
        tables_selected = st.multiselect("Select tables to view:", list(st.session_state.dfs.keys()), default=list(st.session_state.dfs.keys()))

        # State tracking for explored table
        if 'explored_table' not in st.session_state:
            st.session_state['explored_table'] = None

        # Horizontal layout
        cols = st.columns(len(tables_selected))
        for i, table_name in enumerate(tables_selected):
            with cols[i]:
                st.subheader(table_name)
                df = st.session_state.dfs[table_name]
                preview_df = df.iloc[:5, :3]
                if df.shape[1] > 3:
                    preview_df["..."] = "..."
                st.dataframe(preview_df)
                
                if st.button(f"Explore {table_name}"):
                    st.session_state['explored_table'] = table_name

        # Show the explored table while closing others
        if st.session_state['explored_table']:
            st.write(f"All columns of {st.session_state['explored_table']}")
            st.dataframe(st.session_state.dfs[st.session_state['explored_table']])

            # Button to download the table as CSV
            csv = st.session_state.dfs[st.session_state['explored_table']].to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Download {st.session_state['explored_table']} as CSV",
                data=csv,
                file_name=f"{st.session_state['explored_table']}.csv",
                mime="text/csv",
                key=f"download_{st.session_state['explored_table']}"  # Unique key for each button
            )
        # Button to save and switch pages
        st.markdown('<div class="buttons">', unsafe_allow_html=True)
        if st.button("Send tables to Qatch"):
            st.session_state.dfs = {table: st.session_state.dfs[table] for table in tables_selected}
            change_page("qatch")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.warning("⚠️ No data uploaded yet. Please go back and upload a file.")

    # Button to go back
    if st.button("🔙 Go back"):
        change_page("upload")

# **Qatch Screen**
elif st.session_state.page == "qatch":
    st.title("Qatch")
    st.write("🚧 Under construction... 🚧")
 
    table2primary_key = {}
    for table_name, df in st.session_state.dfs.items():
        # Assign primary keys for each table
        table2primary_key[table_name] = 'id'

    db_save_path = "./data/data_interface/"+st.session_state['dbname']+".sqlite"
    db_id = st.session_state['dbname']

    #check for overwrite
    if os.path.exists(db_save_path):
        os.remove(db_save_path)

    connector = SqliteConnector(
        relative_db_path=db_save_path,
        db_name=db_id,
        tables= st.session_state.dfs,
        table2primary_key=table2primary_key
    )

    # init the orchestrator for generation of tests
    orchestrator_generator = OrchestratorGenerator()
    # test generation
    target_df = orchestrator_generator.generate_dataset(connector)

    schema_dict = connector.load_tables_from_database()
    
    #TODO : check the library. Doesn't work
    #init the orchestrator for generation of prediction by API
    #orchestrator_predictor = OrchestratorPredictor()
    #predicted_df = orchestrator_predictor.predict_df(target_df['question'], schema_dict)

    evaluator = OrchestratorEvaluator()

    #For now we are using the same data for evaluation
    eval_input = target_df
    eval_input["prediction"] = eval_input["query"]
    eval_input["model"] = "model1"

    metrics = evaluator.evaluate_df(
        df=eval_input,
        target_col_name="query",#'<target_column_name>',
        prediction_col_name="prediction",#'<prediction_column_name>',
        db_path_name= "db_path",#'<db_path_column_name>'
    )
    #TODO: loading bar
    #TODO: print some test results and examples
    st.write(metrics)

    #TODO: allow to download the results
    st.download_button(
        label=f"📥 Download Test, Prediction and Metrics as CSV",
        data = metrics.to_csv(index=False).encode('utf-8'),
        file_name=f"results.csv",
        mime="text/csv",
        key="results"  # Unique key for each button
    )

    st.markdown('<div class="buttons">', unsafe_allow_html=True)
    if st.button("Show metrics"):
        st.session_state["metrics"] = metrics
        change_page("metrics")
    st.markdown('</div>', unsafe_allow_html=True)

    #TODO: why sometimes execute evaluation 2 times?

    if st.button("🔙 Go back"):
        change_page("upload")

# **Results Screen**
elif st.session_state.page == "metrics":
    st.title("Metrics Results")
    st.write("🚧 Under construction... 🚧")

    metrics_df = st.session_state["metrics"]
    #TODO: multi models

    metric = st.session_state["metrics"].columns[8:].to_list()
    st.write(metric)
    metric_categories = {
        'Models': metric,
        'SQL Category': metric,
        'Tables': metric
    }

    if 'selected_metrics' not in st.session_state:
        st.session_state.selected_metrics = metric_categories['Models']

    # Sidebar for model and metric selection
    st.sidebar.header("Filters")
    
    selected_models = st.sidebar.multiselect("Select models",  metrics_df['model'].unique(), default= metrics_df['model'].unique())
    available_metrics =  metrics_df.columns[8:]
    selected_metrics = st.sidebar.multiselect("Select metrics", available_metrics, default=st.session_state.selected_metrics)

    # Buttons to select metric categories
    st.header("Select a category")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Models"):
            st.session_state.selected_metrics = metric_categories['Models']
    with col2:
        if st.button("SQL Category"):
            st.session_state.selected_metrics = metric_categories['SQL Category']
    with col3:
        if st.button("Tables"):
            st.session_state.selected_metrics = metric_categories['Tables']

    #TODO: add horizontal bar chart
    # Filter metrics based on selected models and metrics
# Filter the dataframe based on selections
    filtered_df = metrics_df[8:]
    filtered_df = metrics_df[metrics_df['model'].isin(selected_models)][selected_metrics]
    st.write(filtered_df)
    # Create an interactive horizontal bar chart
    if not filtered_df.empty:
        melted_df = filtered_df.melt(id_vars=['model'], var_name='Metric', value_name='Value')
        fig = px.histogram(melted_df, y='Metric', x='Value', color='model', orientation='h', barmode='group', title='Model Performance')
        st.plotly_chart(fig)
    else:
        st.write("No data to display with the selected filters.")

    #TODO: val massimo fino a 1, group per categoria (da aggiungere come colonna al dataframe [test_category, model, tbl_name])
    #TODO: add a ranking system

    st.write(st.session_state["metrics"])
    if st.button("🔙 Go back"):
        change_page("upload")