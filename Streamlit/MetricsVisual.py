import streamlit as st
import pandas as pd
import plotly.express as px

# Sample data
data = {
    'Model': ['Model A', 'Model B', 'Model C'],
    'Metric1': [0.8, 0.7, 0.9],
    'Metric2': [0.6, 0.5, 0.7],
    'Metric3': [0.9, 0.8, 0.85],
    'Metric4': [0.75, 0.65, 0.8],
    'Metric5': [0.85, 0.75, 0.9]
}

df = pd.DataFrame(data)

# Metric categories
metric_categories = {
    'Category1': ['Metric1', 'Metric2'],
    'Category2': ['Metric3', 'Metric4'],
    'Category3': ['Metric5']
}

# Set the first category as the default selection
if 'selected_metrics' not in st.session_state:
    st.session_state.selected_metrics = metric_categories['Category1']

# Sidebar for model and metric selection
st.sidebar.header("Filters")
selected_models = st.sidebar.multiselect("Select models", df['Model'].unique(), default=df['Model'].unique())
available_metrics = df.columns[1:]
selected_metrics = st.sidebar.multiselect("Select metrics", available_metrics, default=st.session_state.selected_metrics)

# Buttons to select metric categories
st.header("Select a metric category")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Category1"):
        st.session_state.selected_metrics = metric_categories['Category1']
with col2:
    if st.button("Category2"):
        st.session_state.selected_metrics = metric_categories['Category2']
with col3:
    if st.button("Category3"):
        st.session_state.selected_metrics = metric_categories['Category3']

# Filter the dataframe based on selections
filtered_df = df[df['Model'].isin(selected_models)][['Model'] + st.session_state.selected_metrics]

# Create an interactive horizontal bar chart
if not filtered_df.empty:
    melted_df = filtered_df.melt(id_vars=['Model'], var_name='Metric', value_name='Value')
    fig = px.bar(melted_df, y='Metric', x='Value', color='Model', orientation='h', barmode='group', title='Model Performance')
    st.plotly_chart(fig)
else:
    st.write("No data to display with the selected filters.")

# Function to calculate rankings
def calculate_rank(df, category_metrics):
    # Create a copy of the DataFrame to avoid modifying the original
    category_df = df[['Model'] + category_metrics].copy()
    # Calculate the mean of metrics for each model
    category_df['Average'] = category_df[category_metrics].mean(axis=1)
    # Sort models by average (descending order)
    category_df = category_df.sort_values(by='Average', ascending=False)
    return category_df[['Model', 'Average']]

# Display rankings for the selected category
st.header("Model Rankings for Selected Category")

# Determine which category is currently selected
current_category = None
for category, metrics in metric_categories.items():
    if st.session_state.selected_metrics == metrics:
        current_category = category
        break

if current_category:
    st.subheader(f"Rankings for {current_category}")
    rank = calculate_rank(df, st.session_state.selected_metrics)
    
    # Display rankings as a numbered list
    for i, (model, average) in enumerate(rank.values, start=1):
        st.write(f"{i}. **{model}**: Average = {average:.2f}")
else:
    st.write("No category selected.")