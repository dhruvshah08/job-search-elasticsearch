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


app = Flask(__name__)

# Enable CORS for all routes
CORS(app)


# def upload_jobs():
   
#     with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)  # Read CSV as a dictionary
        
#         actions = []
#         for row in reader:
#             action = {
#                 "_op_type": "index", 
#                 "_index": index_name,  
#                 "_source": row  
#             }
#             actions.append(action)
        
        
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

    
    # Search Elasticsearch to find jobs that match the filters
    response = es.search(index="usa_jobs", body=query)

    # Extract skills from the response
    jobs = response['hits']['hits']
    # print(jobs)
    job_skills = [job['_source'].get('skills', '') for job in jobs]  # Handle missing skills field safely
    # print(job_skills)
    # # Vectorize the resume text and job skills
    vectorizer = TfidfVectorizer(stop_words='english')
    all_texts = job_skills + [resume]  # Add the resume to the list of job skills for comparison
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # # Calculate cosine similarity between the resume and each job skill set
    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])

    # Add similarity scores to the jobs and convert it to percentage
    for i, job in enumerate(jobs):
        match_score = cosine_similarities[0][i] * 100  # Convert to percentage
        job['_source']['similarity_score'] = round(match_score, 2)  # Add the match score to the job document

    # Sort jobs based on similarity score (descending order) and return top 10
    jobs_sorted = sorted(
    [job for job in jobs if job['_source']['similarity_score'] > 0.00],  # Filtering
    key=lambda x: x['_source']['similarity_score'],  # Sorting by similarity_score
    reverse=True  # Sorting in descending order
)[:10] 

    # Print jobs with match score
    for job in jobs_sorted:
        print(f"Job Title: {job['_source']['Job Title']}")
        print(f"Company: {job['_source']['Company']}")
        print(f"Salary Range: ${job['_source']['Min salary']} - ${job['_source']['Max Salary']}")
        print(f"Experience Range: {job['_source']['skills']}")
        print(f"Experience Range: {job['_source']['Min Experience']} to {job['_source']['Max Experience']} years")
        print(f"Match Score: {job['_source']['similarity_score']:.2f}%")
        print("-" * 50)

    return jobs_sorted


@app.route('/api/jobs', methods=['POST'])
def get_jobs():
    try:
        # Get user input from the request
        data = request.get_json()
        resume = data.get('resume', '')
        experience = int(data.get('experience', 0))
        salary = int(data.get('salary', 0))
        work_type = data.get('workType', '')

        if not resume or not work_type:
            return jsonify({"error": "Missing required parameters: resume or workType"}), 400

        # Call the function to get filtered and matched jobs
        jobs = get_jobs_from_resume(resume, work_type, salary, experience)

        # Return the jobs as a JSON response
        return jsonify({"jobs": jobs}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # index_name = 'usa_jobs'
    # csv_file_path ='./Dataset/usa_jobs.csv'
    es = Elasticsearch('https://localhost:9200', basic_auth=('elastic', '_OElCKR8dbqnA8KwZ5Jp'), verify_certs=False)
    app.run(debug=True)
    # upload_jobs()
    # resume = ''''''
    # work_type = "Full-Time"
    # salary = 70  
    # experience = 3  

    # jobs = get_jobs_from_resume(resume, work_type, salary, experience)
    