import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
from src.llm.company_matcher import get_company_name_from_content
import os

DIRECTORY = '../../data/enriched'
DATA_ARRAY = []
OUTPUT_FILE = '../../data/test.csv'


for file in os.listdir(DIRECTORY):
    file_path = os.path.join(DIRECTORY, file)
    DATA_ARRAY.append(pd.read_csv(file_path))

compacted_data = pd.concat(DATA_ARRAY)
def populate_dataset():
    profiles_only_df = compacted_data[compacted_data["category"] == "profiles"].copy()
    for idx, row in profiles_only_df.iterrows():
        text = row.get("content")
        company_name_predicted = get_company_name_from_content(text)
        profiles_only_df.at[idx, "company_name_predicted"] = company_name_predicted
    profiles_only_df.to_csv(OUTPUT_FILE)

def check_data():
    counter = 0
    df = pd.read_csv(OUTPUT_FILE)
    for idx, row in df.iterrows():
        if row.get('company_name') != row.get('company_name_predicted'):
            counter += 1
    print(counter)

check_data()


