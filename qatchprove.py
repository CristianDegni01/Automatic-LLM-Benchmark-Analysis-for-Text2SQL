import pandas as pd

from qatch.connectors.sqlite_connector import SqliteConnector
from qatch.generate_dataset.orchestrator_generator import OrchestratorGenerator
from qatch.evaluate_dataset.orchestrator_evaluator import OrchestratorEvaluator

# Create dummy table
data = {
    "id": [0, 1, 2, 3, 4, 5],
    "year": [1896, 1900, 1904, 2004, 2008, 2012],
    "city": ["athens", "paris", "st. louis", "athens", "beijing", "london"]
}
table = pd.DataFrame.from_dict(data)

table['path'] = 'test_db.sqlite'

# define the tables in the database (<table_name> : <table>)
db_tables = {'olympic_games': table}

# Assume the PKs have all different names. Two tables cannot have same PK name.
table2primary_key = {'olympic_games': 'id'}

# define where to store the sqlite database
db_save_path = 'test_db.sqlite'

# define the name of the database
db_id = 'olympic'

# create database connection
connector = SqliteConnector(
    relative_db_path=db_save_path,
    db_name=db_id,
    tables=db_tables,
    table2primary_key=table2primary_key
)

db_save_path = 'test_db.sqlite'
db_name = 'olympics'
connector = SqliteConnector(
    relative_db_path=db_save_path,
    db_name=db_name,
)

# init the orchestrator
orchestrator_generator = OrchestratorGenerator()
# test generation
target_df = orchestrator_generator.generate_dataset(connector)

#print(target_df)

#codice pipeline
#->df_prediction 

evaluator = OrchestratorEvaluator()
# Returns: The input dataframe enriched with the metrics computed for each test case.

#<QUESRION NL><PREDICTION><GROUND><PATH> = df

#target_col_name = nome della colonna del df che contiene i valori target/ground truth
#  

#prediction_col_name = nome della colonna del df che contiene i valori predetti

#db_path_name = nome della colonna del df che contiene il path del db -> (erve per indicare su che database eseguire le query => ESEMPIO: C:\Users\crist\Downloads\spider_data\spider_data\database)


#sistemare perchè qui papicchio ci ammazza
#per valori tipo having e group lui fa min -max ma questi sono ugauali per cui torna 0 e divide per 0
#corregre il nan nella colonna sort nel caso in cui ci sia un solo elemento
eval_input = target_df
eval_input["prediction"] = eval_input["query"]

metrics = evaluator.evaluate_df(
    df=eval_input,
    target_col_name="query",#'<target_column_name>',
    prediction_col_name="prediction",#'<prediction_column_name>',
    db_path_name= "db_path",#'<db_path_column_name>'
)

#metrics = evaluator.evaluate_df(
#    df=table,
#    target_col_name="city",#'<target_column_name>',
#    prediction_col_name="city",#'<prediction_column_name>',
#    db_path_name='path',#'<db_path_column_name>'
#)


print (metrics)
