import os
import pandas as pd
from prefect import flow, task
from distilabel.models import TogetherLLM
from distilabel.steps.tasks import TextGeneration

import os
os.environ["TOGETHER_API_KEY"] = "your_api_key_here"

@task
def load_dataset(file_path):
    data = {
        "question": [
            "Quanti atleti hanno partecipato alle Olimpiadi del 2008?",
            "Quale città ha ospitato le Olimpiadi nel 2012?",
            "Elenca gli atleti che hanno vinto una medaglia d'oro nel nuoto."
        ],
        "schema": [
            "TABLE olympic_games (id INT PRIMARY KEY, year INT, city TEXT);\nTABLE athletes (id INT PRIMARY KEY, name TEXT, sport TEXT, game_id INT REFERENCES olympic_games.id);",
            "TABLE olympic_games (id INT PRIMARY KEY, year INT, city TEXT);",
            "TABLE olympic_games (id INT PRIMARY KEY, year INT, city TEXT);\nTABLE athletes (id INT PRIMARY KEY, name TEXT, sport TEXT, medal TEXT, game_id INT REFERENCES olympic_games.id);"
        ]
    }
    df = pd.DataFrame(data)
    #df.to_csv("dataset.csv", index=False)
    #df = pd.read_csv(file_path)
    return df

@task
def convert_schema_to_text(schema_dict):
    result = []
    for table_name, table_obj in schema_dict.items():
        cols = []
        primary_keys = {col.column_name for col in table_obj.primary_key}
        foreign_keys = {fk[0]: fk[1] for fk in table_obj.foreign_keys}
        
        for col_name, col_obj in table_obj.tbl_col2metadata.items():
            col_type = "INT" if col_obj.column_type == "numerical" else "TEXT"
            col_def = f"{col_name} {col_type}"
            if col_name in primary_keys:
                col_def += " PRIMARY KEY"
            if col_name in foreign_keys:
                col_def += f" REFERENCES {foreign_keys[col_name]}"
            cols.append(col_def)
        
        table_schema = f"TABLE {table_name} (\n    " + ",\n    ".join(cols) + "\n);"
        result.append(table_schema)
    return "\n".join(result)

@task
def generate_sql(df):
    llm = TogetherLLM(model="deepseek-ai/DeepSeek-R1", api_key=os.getenv("TOGETHER_API_KEY"))
    text_generation = TextGeneration(llm=llm, system_prompt=None, template="""
    Answer the following question with the SQL code. Use the database schema. Return only the SQL script enclosed in <answer> tags.
    Question: {{ question }}
    Database Schema: {{ schema }}
    """.strip(), columns=["question", "schema"])
    text_generation.load()
    df["generated_sql"] = df.apply(lambda row: next(text_generation.process([{"question": row["question"], "schema": row["schema"]}])), axis=1)
    return df

@task
def save_dataset(df, output_path):
    print(df)
    df.to_csv(output_path, index=False)

@flow
def OrchestratorPredictor(input_file, output_file):
    df = load_dataset(input_file)
    #df["schema"] = df["schema"].apply(convert_schema_to_text)
    df = generate_sql(df)
    save_dataset(df, output_file)

if __name__ == "__main__":
    OrchestratorPredictor("dataset.csv", "dataset_with_sql.csv")
