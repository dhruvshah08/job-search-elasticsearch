import csv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import warnings
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS

from urllib3.exceptions import InsecureRequestWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

warnings.simplefilter('ignore', InsecureRequestWarning)
import pandas as pd

app = Flask(__name__)

CORS(app)
csv_file_path = './Dataset/usa_jobs.csv'
new_index_name = "usa_jobs_index1"
# def upload_jobs():
#     with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)  
#         actions = []
#         i=0
#         for row in reader:
#             row["Min salary"] = int(row.get("Min salary", 0)) if row.get("Min salary") else None
#             row["Max Salary"] = int(row.get("Max Salary", 0)) if row.get("Max Salary") else None
#             row["Min Experience"] = int(row.get("Min Experience", 0)) if row.get("Min Experience") else None
#             row["Max Experience"] = int(row.get("Max Experience", 0)) if row.get("Max Experience") else None
#             print(i)
#             action = {
#                 "_op_type": "index", 
#                 "_index": new_index_name,  
#                 "_source": row  
#             }
#             actions.append(action)
#             i+=1
        
        
#         success, failed = bulk(es, actions)
#         print(f"Successfully indexed {success} documents.")
#         print(f"Failed to index {failed} documents.")


def get_jobs_from_resume(resume, work_type, salary, experience):
   
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"Work Type": work_type}},  
                    {"range": {"Min salary": {"lte": salary}}},  
                    {"range": {"Max Salary": {"gte": salary}}}, 
                    {"range": {"Min Experience": {"lte": experience}}},  
                    {"range": {"Max Experience": {"gte": experience}}}  
                ]
            }
        }
    }

    response = es.search(index=new_index_name, body=query)
    jobs = response['hits']['hits']

    if not jobs:
        print("No jobs found matching the criteria.")
        return []

    job_skills = [job['_source'].get('skills', '') for job in jobs]
    vectorizer = TfidfVectorizer(stop_words='english')
    all_texts = job_skills + [resume]
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])

    for i, job in enumerate(jobs):
        match_score = cosine_similarities[0][i] * 100  

        min_exp = int(job['_source'].get('Min Experience', 0))
        max_exp = int(job['_source'].get('Max Experience', 1))  
        min_salary = int(job['_source'].get('Min salary', 0))
        max_salary = int(job['_source'].get('Max Salary', 1)) 

        if min_exp <= experience <= max_exp:
            experience_score = 1 - abs(experience - max_exp) / (max_exp - min_exp + 1e-5)  
        else:
            experience_score = 0.2  

        salary_score = 1 - abs(salary - min_salary) / (max_salary - min_salary + 1e-5)  # Add a small constant

        match_score += salary_score * 20
        match_score += experience_score * 20
        job['_source']['similarity_score'] = round(match_score, 2)

    jobs_sorted = sorted(jobs, key=lambda x: x['_source']['similarity_score'], reverse=True)[:10]

    for job in jobs_sorted:
        print(f"Job Title: {job['_source']['Job Title']}")
        print(f"Company: {job['_source']['Company']}")
        print(f"Salary Range: ${job['_source']['Min salary']} - ${job['_source']['Max Salary']}")
        print(f"Skills: {job['_source']['skills']}")
        print(f"Work Type: {job['_source']['Work Type']}")
        print(f"Experience Range: {job['_source']['Min Experience']} to {job['_source']['Max Experience']} years")
        print(f"Match Score: {job['_source']['similarity_score']:.2f}%")
        print("-" * 50)

    return jobs_sorted



@app.route('/api/jobs', methods=['POST'])
def get_jobs():
    try:
        data = request.get_json()
        resume = data.get('resume', '')
        experience = int(data.get('experience', 0))
        salary = int(data.get('salary', 0))
        work_type = data.get('workType', '')
        if not resume or not work_type:
            return jsonify({"error": "Missing required parameters: resume or workType"}), 400
        jobs = get_jobs_from_resume(resume, work_type, salary, experience)

        return jsonify({"jobs": jobs}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    es = Elasticsearch('https://localhost:9200', basic_auth=('elastic', '_OElCKR8dbqnA8KwZ5Jp'), verify_certs=False)
    app.run(debug=True)
    # upload_jobs()