import csv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import warnings

from urllib3.exceptions import InsecureRequestWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

warnings.simplefilter('ignore', InsecureRequestWarning)
import pandas as pd

csv_file_path = './Dataset/usa_jobs.csv'
new_index_name = "usa_jobs_index1"
def upload_jobs():
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)  
        actions = []
        i=0
        for row in reader:
            row["Min salary"] = int(row.get("Min salary", 0)) if row.get("Min salary") else None
            row["Max Salary"] = int(row.get("Max Salary", 0)) if row.get("Max Salary") else None
            row["Min Experience"] = int(row.get("Min Experience", 0)) if row.get("Min Experience") else None
            row["Max Experience"] = int(row.get("Max Experience", 0)) if row.get("Max Experience") else None
            print(i)
            action = {
                "_op_type": "index", 
                "_index": new_index_name,  
                "_source": row  
            }
            actions.append(action)
            i+=1
        
        
        success, failed = bulk(es, actions)
        print(f"Successfully indexed {success} documents.")
        print(f"Failed to index {failed} documents.")

if __name__ == '__main__':
    es = Elasticsearch('https://localhost:9200', basic_auth=('elastic', '_OElCKR8dbqnA8KwZ5Jp'), verify_certs=False)
    upload_jobs()